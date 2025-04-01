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

import asyncio
import os
import pathlib
import typing as t
import webbrowser
from contextlib import contextmanager

import socketio
import uvicorn
from fastapi import APIRouter, Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from flask.ctx import _AppCtxGlobals
from starlette.middleware.base import BaseHTTPMiddleware

import __main__
from taipy.common.logger._taipy_logger import _TaipyLogger

from ..._renderers.json import _TaipyJsonAdapter
from ...config import ServerConfig
from ...custom._page import _ExternalResourceHandlerManager
from ..server import _Server
from .request import request as request_context
from .request import request_meta
from .utils import send_from_directory

if t.TYPE_CHECKING:
    from ...gui import Gui


# this is for fastapi routes
def get_request_meta(_: Request):
    new_request_meta = _AppCtxGlobals()
    request_meta.set(new_request_meta)
    return new_request_meta


# this is for ws calls as contextmanager
@contextmanager
def get_request_meta_sync():
    new_request_meta = _AppCtxGlobals()
    request_meta.set(new_request_meta)
    yield new_request_meta
    request_meta.set(None)


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
        self._gui = gui
        server_config = server_config or {}
        self._path_mapping = path_mapping or {}
        self._allow_upgrades = allow_upgrades
        self._is_running = False
        self._port: t.Optional[int] = None

        # server setup
        self._server = server or FastAPI()
        self._ws = socketio.AsyncServer()
        self._server.mount("/", socketio.ASGIApp(self._ws, other_asgi_app=self._server))

        # registering middleware
        self._server.add_middleware(CleanupMiddleware)

        self._server.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # Change this to your frontend domain for security
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        # Define your event handlers and routes
        @self._ws.event
        def connect(sid, environ):
            with get_request_meta_sync():
                gui._handle_connect()

        @self._ws.on("message")  # type: ignore
        def handle_message(sid, message):
            with get_request_meta_sync():
                if "status" in message:
                    _TaipyLogger._get_logger().info(message["status"])
                elif "type" in message:
                    gui._manage_ws_message(message["type"], message)

        @self._ws.event
        def disconnect(sid):
            with get_request_meta_sync():
                gui._handle_disconnect()

    def _get_default_router(
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

        @taipy_router.get("/", response_class=HTMLResponse)
        @taipy_router.get("/{path:path}", response_class=HTMLResponse)
        def my_index(request: Request, path: str = "", request_meta: _AppCtxGlobals = Depends(get_request_meta)):  # noqa: B008
            resource_handler_id = request.cookies.get("_RESOURCE_HANDLER_ARG", None)
            if resource_handler_id is not None:
                resource_handler = _ExternalResourceHandlerManager().get(resource_handler_id)
                if resource_handler is None:
                    reload_html = """
                        <html>
                            <head><style>body {background-color: black; margin: 0;}</style></head>
                            <body><script>location.reload();</script></body>
                        </html>
                    """
                    response = HTMLResponse(content=reload_html, status_code=400)
                    response.set_cookie(
                        "_RESOURCE_HANDLER_ARG",
                        "",
                        secure=request.url.scheme == "https",
                        httponly=True,
                        expires=0,
                        path="/",
                    )
                    return response
                try:
                    return resource_handler.get_resources(path, static_folder, base_url)
                except Exception as e:
                    raise HTTPException(
                        status_code=500, detail="Can't get resources from custom resource handler"
                    ) from e

            if not path or path == "index.html" or "." not in path:
                try:
                    return templates.TemplateResponse(
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
                return send_from_directory(base_path, path)
            # use the path mapping to detect and find resources
            for k, v in self._path_mapping.items():
                if (
                    path.startswith(f"{k}/")
                    and (
                        file_path := str(os.path.normpath((base_path := v + os.path.sep) + path[len(k) + 1 :]))
                    ).startswith(base_path)
                    and os.path.isfile(file_path)
                ):
                    return send_from_directory(base_path, path[len(k) + 1 :])
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
                return send_from_directory(base_path, path)
            if (
                (
                    file_path := str(os.path.normpath((base_path := self._gui._root_dir + os.path.sep) + path))  # type: ignore[attr-defined]
                ).startswith(base_path)
                and os.path.isfile(file_path)
                and not self._is_ignored(file_path)
            ):
                return send_from_directory(base_path, path)

            # Default error return for unmatched paths
            raise HTTPException(status_code=404, detail="")

        return taipy_router

    def direct_render_json(self, data):
        return _TaipyJsonAdapter().parse(data)

    def get_server_instance(self):
        return self._server

    def get_port(self) -> int:
        return self._port or -1

    def send_ws_message(self, *args, **kwargs):
        asyncio.run(self._ws.emit("message", *args, **kwargs))

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
        from ..utils import is_running_from_reloader

        host_value = host if host != "0.0.0.0" else "localhost"
        self._host = host
        if port == "auto":
            port = self._get_random_port(port_auto_ranges)
        server_url = f"http://{host_value}:{port}"
        self._port = port
        if not is_running_from_reloader() and self._gui._get_config("run_browser", False):  # type: ignore[attr-defined]
            webbrowser.open(client_url or server_url, new=2)
        self._is_running = True
        run_config = {
            "app": self._server,
            "host": host,
            "port": port,
            "reload": use_reloader,
        }
        try:
            uvicorn.run(**run_config)
        except KeyboardInterrupt:
            pass

    def is_running(self):
        return self._is_running

    def stop_thread(self):
        raise NotImplementedError
