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

try:
    from .rest import Rest
except ImportError as e:
    # Gracefully handle missing dependencies (e.g., pkg_resources)
    # This allows the module to be imported even if dependencies are missing
    # The actual error will be raised when Rest is used
    Rest = None
    import warnings

    warnings.warn(f"Failed to import Rest from .rest: {e}", ImportWarning)
