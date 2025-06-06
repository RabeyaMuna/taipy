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
from contextvars import ContextVar

from fastapi import Request
from flask.ctx import _AppCtxGlobals

from ..request import BaseRequestAccessor
from .utils import run_async

request: ContextVar[t.Optional[Request]] = ContextVar("request", default=None)
request_meta: ContextVar[t.Optional[_AppCtxGlobals]] = ContextVar("request_meta", default=None)
sid: ContextVar[t.Optional[str]] = ContextVar("sid", default=None)


class RequestAccessorFastAPI(BaseRequestAccessor):
    def args(self, to_dict=False):
        fastapi_r = request.get()
        return {} if fastapi_r is None else fastapi_r.query_params if to_dict is False else dict(fastapi_r.query_params)

    def arg(self, key, default=None):
        fastapi_r = request.get()
        return default if fastapi_r is None else fastapi_r.query_params.get(key, default)

    def form(self):
        fastapi_r = request.get()
        return {} if fastapi_r is None else dict(run_async(fastapi_r._get_form))

    def files(self):
        fastapi_r = request.get()
        if fastapi_r is None:
            return {}
        form_data = dict(run_async(fastapi_r._get_form))
        return {k: v for k, v in form_data.items() if hasattr(v, "filename")}

    def cookies(self):
        fastapi_r = request.get()
        return {} if fastapi_r is None else fastapi_r.cookies

    def sid(self):
        return sid.get()

    def set_sid(self, incoming_sid: t.Optional[str]):
        sid.set(incoming_sid)

    def get_request(self):
        return request.get()

    def get_request_meta(self):
        return request_meta.get()

    def has_request_context(self):
        return request.get() is not None
