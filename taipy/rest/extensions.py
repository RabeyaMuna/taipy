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

"""Extensions registry

All extensions here are used as singletons and
initialized in application factory
"""

try:
    from .commons.apispec import APISpecExt
except ModuleNotFoundError as e:
    if "pkg_resources" in str(e):
        raise ModuleNotFoundError(
            "Missing dependency 'setuptools'. Please install it, e.g., via 'pip install setuptools'."
        ) from e
    raise

apispec = APISpecExt()
