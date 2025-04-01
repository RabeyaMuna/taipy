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
import re
import typing as t
from abc import ABC, abstractmethod
from contextvars import ContextVar
from random import choices, randint

from gitignore_parser import parse_gitignore

import __main__

from ..utils import _is_port_open, _RuntimeManager
from ..utils._css import get_style


class _Server(ABC):
    _RE_OPENING_CURLY = re.compile(r"([^\"])(\{)")
    _RE_CLOSING_CURLY = re.compile(r"(\})([^\"])")
    _OPENING_CURLY = r"\1&#x7B;"
    _CLOSING_CURLY = r"&#x7D;\2"
    _RESOURCE_HANDLER_ARG = "tprh"

    def _is_ignored(self, file_path: str) -> bool:
        if not hasattr(self, "_ignore_matches"):
            __IGNORE_FILE = ".taipyignore"
            ignore_file = (
                (pathlib.Path(__main__.__file__).parent / __IGNORE_FILE) if hasattr(__main__, "__file__") else None
            )
            if not ignore_file or not ignore_file.is_file():
                ignore_file = pathlib.Path(self._gui._root_dir) / __IGNORE_FILE  # type: ignore[attr-defined]
            self._ignore_matches = (
                parse_gitignore(ignore_file) if ignore_file.is_file() and os.access(ignore_file, os.R_OK) else None
            )

        if callable(self._ignore_matches):
            return self._ignore_matches(file_path)
        return False

    def _get_random_port(
        self, port_auto_ranges: t.Optional[t.List[t.Union[int, t.Tuple[int, int]]]] = None
    ):  # pragma: no cover
        if not hasattr(self, "_host"):
            raise RuntimeError("Server host is not set")
        port_auto_ranges = port_auto_ranges or [(49152, 65535)]
        random_weights = [1 if isinstance(r, int) else abs(r[1] - r[0]) + 1 for r in port_auto_ranges]
        while True:
            random_choices = [
                r if isinstance(r, int) else randint(min(r[0], r[1]), max(r[0], r[1])) for r in port_auto_ranges
            ]
            port = choices(random_choices, weights=random_weights)[0]
            if port not in _RuntimeManager().get_used_port() and not _is_port_open(self._host, port):  # type: ignore
                return port

    @abstractmethod
    def get_server_instance(self):
        raise NotImplementedError

    @abstractmethod
    def get_port(self) -> int:
        raise NotImplementedError

    @abstractmethod
    def send_ws_message(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def direct_render_json(self, data):
        raise NotImplementedError

    def render(self, html_fragment, script_paths, style, head, context):
        template_str = _Server._RE_OPENING_CURLY.sub(_Server._OPENING_CURLY, html_fragment)
        template_str = _Server._RE_CLOSING_CURLY.sub(_Server._CLOSING_CURLY, template_str)
        template_str = template_str.replace('"{!', "{")
        template_str = template_str.replace('!}"', "}")
        style = get_style(style)
        return self.direct_render_json(
            {
                "jsx": template_str,
                "style": (style + os.linesep) if style else "",
                "head": head or [],
                "context": context or self._gui._get_default_module_name(),  # type: ignore[attr-defined]
                "scriptPaths": script_paths,
            }
        )

    @abstractmethod
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
        raise NotImplementedError

    @abstractmethod
    def is_running(self):
        raise NotImplementedError

    @abstractmethod
    def stop_thread(self):
        raise NotImplementedError


ServerFrameworks = t.Literal["flask", "fastapi"]
server_type: ContextVar[ServerFrameworks] = ContextVar("server_type", default="flask")
server: ContextVar[_Server] = ContextVar("server")
