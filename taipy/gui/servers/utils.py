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

from flask import g as flask_meta
from flask import has_app_context
from flask import has_request_context as flask_has_request_context
from flask import request as flask_request
from flask import send_file as flask_send_file
from flask import send_from_directory as flask_send_from_directory
from werkzeug.serving import is_running_from_reloader as flask_is_running_from_reloader

from .fastapi import FastAPIServer
from .fastapi.request import request as fastapi_request
from .fastapi.request import request_meta as fastapi_meta
from .fastapi.utils import send_file as fastapi_send_file
from .fastapi.utils import send_from_directory as fastapi_send_from_directory
from .flask import FlaskServer
from .server import ServerFrameworks, _Server, server, server_type


def set_server_type(framework: ServerFrameworks) -> None:
    server_type.set(framework)


def get_server_type() -> ServerFrameworks:
    return server_type.get()


def create_server(*args, **kwargs) -> _Server:
    new_server: t.Union[FlaskServer, FastAPIServer, None] = None
    if server_type.get() == "flask":
        new_server = FlaskServer(*args, **kwargs)
    elif server_type.get() == "fastapi":
        new_server = FastAPIServer(*args, **kwargs)
    if new_server is None:
        raise ValueError(f"Invalid server type: {type}")
    server.set(new_server)
    return new_server


def send_file(*args, **kwargs):
    if server_type.get() == "flask":
        return flask_send_file(*args, **kwargs)
    elif server_type.get() == "fastapi":
        return fastapi_send_file(*args, **kwargs)


def send_from_directory(*args, **kwargs):
    if server_type.get() == "flask":
        return flask_send_from_directory(*args, **kwargs)
    elif server_type.get() == "fastapi":
        return fastapi_send_from_directory(*args, **kwargs)


def get_request():
    if server_type.get() == "flask":
        return flask_request
    elif server_type.get() == "fastapi":
        return fastapi_request.get()
    return None


def get_request_meta():
    if server_type.get() == "flask":
        return flask_meta
    elif server_type.get() == "fastapi":
        return fastapi_meta.get()
    return {}


def has_server_context():
    if server_type.get() == "flask":
        return has_app_context()
    elif server_type.get() == "fastapi":
        return fastapi_request.get() is not None
    return False


def has_request_context():
    if server_type.get() == "flask":
        return flask_has_request_context()
    elif server_type.get() == "fastapi":
        return fastapi_request.get() is not None
    return False


def is_running_from_reloader():
    if server_type.get() == "flask":
        flask_is_running_from_reloader()
    elif server_type.get() == "fastapi":
        return server.get().get_server_instance().state.is_reloader
    return False
