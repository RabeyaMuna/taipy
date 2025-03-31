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

import contextlib
import typing as t

from ..servers import _Server, get_request, has_request_context
from ._page import ResourceHandler, _ExternalResourceHandlerManager


def is_in_custom_page_context() -> bool:
    "NOT DOCUMENTED"
    resource_handler_id = None
    with contextlib.suppress(Exception):
        if has_request_context():
            resource_handler_id = get_request().cookies.get(_Server._RESOURCE_HANDLER_ARG, None)
    return resource_handler_id is not None


def get_current_resource_handler() -> t.Optional[ResourceHandler]:
    "NOT DOCUMENTED"
    resource_handler_id = None
    with contextlib.suppress(Exception):
        if has_request_context():
            resource_handler_id = get_request().cookies.get(_Server._RESOURCE_HANDLER_ARG, None)
    return _ExternalResourceHandlerManager().get(resource_handler_id) if resource_handler_id else None
