# Copyright 2021-2025 Avaiga Private Limited
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

import os
import pathlib
import threading
import time
import typing as t
import webbrowser
from asyncio import Queue
from contextlib import asynccontextmanager, contextmanager

import socketio
import uvicorn
from fastapi import APIRouter, Depends, FastAPI, HTTPException, Request
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.testclient import TestClient
from flask.ctx import _AppCtxGlobals
from starlette.middleware.base import BaseHTTPMiddleware

import __main__
from taipy.common.logger._taipy_logger import _TaipyLogger

from ..._renderers.json import _TaipyJsonEncoder
from ...config import ServerConfig
from ...utils import _is_in_notebook, _is_port_open, _RuntimeManager
from ..server import _Server
from .request import RequestAccessorFastAPI, request_meta
from .request import request as request_context
from .request import sid as sid_context
from .utils import run_async, send_file, send_from_directory

if t.TYPE_CHECKING:
    from ...gui import Gui


# this is for fastapi routes
async def request_meta_dependency(_: Request):
    new_request_meta = _AppCtxGlobals()
    request_meta.set(new_request_meta)
    return new_request_meta


async def request_dependency(request: Request):
    request_context.set(request)
    return request  # Still return it if needed in the route


# this is for ws calls as contextmanager
@contextmanager
def get_request_meta_ctx():
    prev_meta = request_meta.get()
    new_request_meta = _AppCtxGlobals()
    request_meta.set(new_request_meta)
    yield new_request_meta
    request_meta.set(prev_meta)


@contextmanager
def set_sid_ctx(sid: str):
    prev_sid = sid_context.get()
    sid_context.set(sid)
    yield
    sid_context.set(prev_sid)


@contextmanager
def set_request_ctx(request: Request):
    prev_request = request_context.get()
    request_context.set(request)
    yield
    request_context.set(prev_request)


class CleanupMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        request_context.set(None)
        request_meta.set(None)
        return response


class FastAPIServer(_Server):
    def __init__(
        self,
        gui: "Gui",
        server: t.Optional[FastAPI] = None,
        path_mapping: t.Optional[dict] = None,
        # async mode is not used in FastAPI but it is here to comply with the api for now
        async_mode: t.Optional[str] = None,
        allow_upgrades: bool = True,
        server_config: t.Optional[ServerConfig] = None,
    ):
        self.request = RequestAccessorFastAPI()
        self._gui = gui
        server_config = server_config or {}
        self._path_mapping = path_mapping or {}
        self._allow_upgrades = allow_upgrades
        self._is_running = False
        self._port: t.Optional[int] = None

        # server setup
        self._emit_queue: t.Optional[Queue[t.Tuple[t.Tuple[t.Any, ...], t.Dict[str, t.Any]]]] = None
        self._server = server or FastAPI(json_encoder=_TaipyJsonEncoder)
        self._ws = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")
        self._server.mount("/socket.io", socketio.ASGIApp(self._ws, other_asgi_app=self._server, socketio_path="/"))

        # registering middleware
        self._server.add_middleware(CleanupMiddleware)

        self._server.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        # Define your event handlers and routes
        @self._ws.event
        async def connect(sid, *args):
            with get_request_meta_ctx(), set_sid_ctx(sid):
                gui._handle_connect()

        @self._ws.event
        async def message(sid, *args):
            message = args[0]
            with get_request_meta_ctx(), set_sid_ctx(sid):
                if "status" in message:
                    _TaipyLogger._get_logger().info(message["status"])
                elif "type" in message:
                    gui._manage_ws_message(message["type"], message)

        @self._ws.event
        async def disconnect(sid):
            with get_request_meta_ctx(), set_sid_ctx(sid):
                gui._handle_disconnect()

    def _get_default_handler(
        self,
        static_folder: str,
        template_folder: str,
        title: str,
        favicon: str,
        root_margin: str,
        scripts: t.List[str],
        styles: t.List[str],
        version: str,
        client_config: t.Dict[str, t.Any],
        watermark: t.Optional[str],
        css_vars: str,
        base_url: str,
    ) -> APIRouter:
        templates = Jinja2Templates(directory=template_folder)

        taipy_router = APIRouter()

        async def emit_dispatcher():
            while True:
                emit_args, emit_kwargs = await self._emit_queue.get()
                try:
                    await self._ws.emit(*emit_args, **emit_kwargs)
                except Exception as e:
                    _TaipyLogger._get_logger().info("Error sending ws message: ", e)

        @asynccontextmanager
        async def lifespan(app: FastAPI):
            self._emit_queue = Queue()
            self._ws.start_background_task(emit_dispatcher)
            yield

        taipy_router.lifespan_context = lifespan

        @taipy_router.get("/", response_class=HTMLResponse)
        @taipy_router.get("/{path:path}", response_class=HTMLResponse)
        def my_index(request: Request, path: str = "", request_meta: _AppCtxGlobals = Depends(request_meta_dependency)):  # noqa: B008
            with set_request_ctx(request), get_request_meta_ctx():
                from ..._hook import _Hooks

                custom_page_resource = _Hooks()._resolve_custom_page_resource_handler(
                    path, base_url, static_folder, client_config, css_vars, scripts, styles
                )
                if custom_page_resource is not None:
                    return custom_page_resource
                if not path or path == "index.html" or "." not in path:
                    try:
                        return templates.TemplateResponse(
                            request,
                            "index.html",
                            {
                                "title": title,
                                "favicon": f"{favicon}?version={version}",
                                "root_margin": root_margin,
                                "watermark": watermark,
                                "config": client_config,
                                "scripts": scripts,
                                "styles": styles,
                                "version": version,
                                "css_vars": css_vars,
                                "base_url": base_url,
                            },
                        )
                    except Exception:
                        raise HTTPException(  # noqa: B904
                            status_code=500,
                            detail="Something is wrong with the taipy-gui front-end installation. Check that the js bundle has been properly built.",  # noqa: E501
                        )

                if path == "taipy.status.json":
                    return JSONResponse(content=self._gui._serve_status(pathlib.Path(template_folder) / path))
                if (file_path := str(os.path.normpath((base_path := static_folder + os.path.sep) + path))).startswith(
                    base_path
                ) and os.path.isfile(file_path):
                    return self.send_from_directory(base_path, path)
                # use the path mapping to detect and find resources
                for k, v in self._path_mapping.items():
                    if (
                        path.startswith(f"{k}/")
                        and (
                            file_path := str(os.path.normpath((base_path := v + os.path.sep) + path[len(k) + 1 :]))
                        ).startswith(base_path)
                        and os.path.isfile(file_path)
                    ):
                        return self.send_from_directory(base_path, path[len(k) + 1 :])
                if (
                    hasattr(__main__, "__file__")
                    and (
                        file_path := str(
                            os.path.normpath((base_path := os.path.dirname(__main__.__file__) + os.path.sep) + path)
                        )
                    ).startswith(base_path)
                    and os.path.isfile(file_path)
                    and not self._is_ignored(file_path)
                ):
                    return self.send_from_directory(base_path, path)
                if (
                    (
                        file_path := str(os.path.normpath((base_path := self._gui._root_dir + os.path.sep) + path))  # type: ignore[attr-defined]
                    ).startswith(base_path)
                    and os.path.isfile(file_path)
                    and not self._is_ignored(file_path)
                ):
                    return self.send_from_directory(base_path, path)

                # Default error return for unmatched paths
                raise HTTPException(status_code=404, detail="")

        return taipy_router

    def direct_render_json(self, data):
        return jsonable_encoder(data)
        # return _TaipyJsonAdapter().parse(data)

    def get_server_instance(self):
        return self._server

    def get_port(self) -> int:
        return self._port or -1

    def test_client(self):
        return TestClient(self._server)

    def test_request_context(self, path, data):
        return get_request_meta_ctx()

    def send_ws_message(self, *args, **kwargs):
        if kwargs.get("to") is None:
            kwargs["to"] = [sid_context.get()]
        if isinstance(kwargs["to"], str) or kwargs["to"] is None:
            kwargs["to"] = [kwargs["to"]]
        if "include_self" in kwargs and kwargs["include_self"]:
            del kwargs["include_self"]
            sid = sid_context.get()
            if sid is not None and None not in kwargs["to"] and sid not in kwargs["to"]:
                kwargs["to"].append(sid)
        for sid in kwargs["to"]:
            temp_kwargs = kwargs.copy()
            temp_kwargs["to"] = sid
            self._emit_queue.put_nowait((("message", *args), temp_kwargs))

    def save_uploaded_file(self, file, path):
        if not file or not path:
            raise ValueError("File and path must be provided.")
        with open(path, "wb") as f_buffer:
            f_buffer.write(run_async(file.read))

    def send_file(self, *args, **kwargs):
        return send_file(*args, **kwargs)

    def send_from_directory(self, *args, **kwargs):
        return send_from_directory(*args, **kwargs)

    def has_server_context(self):
        return request_context.get() is not None

    def is_running_from_reloader(self):
        return os.getpid() == os.getppid()

    def run(
        self,
        host,
        port,
        client_url,
        debug,
        use_reloader,
        server_log,
        run_in_thread,
        allow_unsafe_werkzeug,
        notebook_proxy,
        port_auto_ranges,
    ):
        host_value = host if host != "0.0.0.0" else "localhost"
        self._host = host
        if port == "auto":
            port = self._get_random_port(port_auto_ranges)
        server_url = f"http://{host_value}:{port}"
        self._port = port
        if _is_in_notebook() or run_in_thread:
            runtime_manager = _RuntimeManager()
            runtime_manager.add_gui(self._gui, port)
        if debug and not self.is_running_from_reloader() and _is_port_open(host_value, port):
            raise ConnectionError(
                f"Port {port} is already opened on {host} because another application is running on the same port.\nPlease pick another port number and rerun with the 'port=<new_port>' setting.\nYou can also let Taipy choose a port number for you by running with the 'port=\"auto\"' setting."  # noqa: E501
            )
        if not self.is_running_from_reloader() and self._gui._get_config("run_browser", False):  # type: ignore[attr-defined]
            webbrowser.open(client_url or server_url, new=2)
        if _is_in_notebook() or run_in_thread:
            return self._run_notebook()
        self._is_running = True
        run_config = {
            "app": self._server,
            "host": host,
            "port": port,
            "reload": use_reloader,
        }
        uvicorn.run(**run_config)

    def _run_notebook(self):
        if not self._port or not self._host:
            raise RuntimeError("Port and host must be set before running the server in notebook mode.")
        self._is_running = True
        config = uvicorn.Config(app=self._server, host=self._host, port=self._port, reload=False, log_level="info")
        self._thread_server = uvicorn.Server(config)
        self._thread = threading.Thread(target=self._thread_server.run, daemon=True)
        self._thread.start()
        return

    def is_running(self):
        return self._is_running

    def stop_thread(self):
        if hasattr(self, "_thread") and self._thread.is_alive() and self._is_running:
            self._thread_server.should_exit = True
            self._thread.join()
            while _is_port_open(self._host, self._port):
                time.sleep(0.1)
            self._is_running = False
