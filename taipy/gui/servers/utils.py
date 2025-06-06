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

import typing as t

from .fastapi import FastAPIServer
from .flask import FlaskServer
from .request import BaseRequestAccessor
from .server import ServerFrameworks, ServerManager, _Server

if t.TYPE_CHECKING:
    from ..gui import Gui  # pragma: no cover


def set_server_type(framework: ServerFrameworks) -> None:
    ServerManager().set_server_type(framework)


def get_server_type() -> ServerFrameworks:
    return ServerManager().get_server_type()


def create_server(*args, **kwargs) -> _Server:
    new_server: t.Union[FlaskServer, FastAPIServer, None] = None
    if get_server_type() == "flask":
        new_server = FlaskServer(*args, **kwargs)
    elif get_server_type() == "fastapi":
        new_server = FastAPIServer(*args, **kwargs)
    if new_server is None:
        raise ValueError(f"Invalid server type: {type}")
    ServerManager().set_server(new_server)
    return new_server


def get_server_request_accessor(gui: "Gui") -> BaseRequestAccessor:
    return BaseRequestAccessor() if not hasattr(gui, "_server") or gui._server is None else gui._server.request
