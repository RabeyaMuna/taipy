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

import sys
from importlib.util import find_spec

# Ensure pkg_resources is available for apispec-webframeworks dependency
# In Python 3.12+, setuptools may not be bundled or newer versions removed pkg_resources
try:
    import pkg_resources  # noqa: F401
except ModuleNotFoundError:
    import importlib.metadata as _metadata
    import types as _types

    # Provide a substitute for pkg_resources to satisfy apispec-webframeworks==0.5.2
    _pkg_resources = _types.ModuleType("pkg_resources")

    def _get_distribution(name):
        class _Dist:
            def __init__(self, name):
                self._name = name
                self.parsed_version = _metadata.version(name)
        return _Dist(name)

    _pkg_resources.get_distribution = _get_distribution
    sys.modules["pkg_resources"] = _pkg_resources

if find_spec("taipy"):
    if find_spec("taipy.common") and find_spec("taipy.common.config"):
        from taipy.common.config._init import *

    if find_spec("taipy.gui"):
        from taipy.gui._init import *

    if find_spec("taipy.core"):
        from taipy.core._init import *

    if find_spec("taipy.rest"):
        from taipy.rest._init import *

    if find_spec("taipy.gui_core"):
        from taipy.gui_core._init import *

    if find_spec("taipy.enterprise"):
        from taipy.enterprise._init import *

    if find_spec("taipy.designer"):
        from taipy.designer._init import *

    if find_spec("taipy._run"):
        from taipy._run import _run as run
