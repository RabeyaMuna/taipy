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
import typing as t

from flask import has_request_context
from flask import request as flask_request
from starlette.datastructures import QueryParams
from werkzeug.datastructures import ImmutableMultiDict

from .fastapi.request import request as fastapi_request
from .fastapi.request import sid as fastapi_sid
from .server import server_type


class RequestAccessor:
    @staticmethod
    def args(to_dict=False) -> t.Union[ImmutableMultiDict[t.Any, t.Any], QueryParams, t.Dict[str, str]]:
        if server_type.get() == "flask":
            return flask_request.args if to_dict is False else flask_request.args.to_dict(flat=True)
        elif server_type.get() == "fastapi":
            fastapi_r = fastapi_request.get()
            return (
                {}
                if fastapi_r is None
                else fastapi_r.query_params
                if to_dict is False
                else dict(fastapi_r.query_params)
            )
        return {}

    @staticmethod
    def arg(key, default=None):
        if server_type.get() == "flask":
            return flask_request.args.get(key, default)
        elif server_type.get() == "fastapi":
            fastapi_r = fastapi_request.get()
            return default if fastapi_r is None else fastapi_r.query_params.get(key, default)
        return default

    @staticmethod
    def form():
        if server_type.get() == "flask":
            return flask_request.form
        elif server_type.get() == "fastapi":
            fastapi_r = fastapi_request.get()
            return {} if fastapi_r is None else dict(asyncio.run(fastapi_r._get_form()))
        return {}

    @staticmethod
    def files():
        if server_type.get() == "flask":
            return flask_request.files
        elif server_type.get() == "fastapi":
            raise NotImplementedError("FastAPI does not support files handling yet")
        return {}

    @staticmethod
    def cookies():
        if server_type.get() == "flask":
            return flask_request.cookies
        elif server_type.get() == "fastapi":
            fastapi_r = fastapi_request.get()
            return {} if fastapi_r is None else fastapi_r.cookies
        return {}

    @staticmethod
    def sid():
        if server_type.get() == "flask" and has_request_context() and flask_request:
            return getattr(flask_request, "sid", None)
        elif server_type.get() == "fastapi":
            return fastapi_sid.get()
        return None

    @staticmethod
    def set_sid(sid: t.Optional[str]):
        if server_type.get() == "flask":
            flask_request.sid = sid  # type: ignore[attr-defined]
        elif server_type.get() == "fastapi":
            fastapi_sid.set(sid)
