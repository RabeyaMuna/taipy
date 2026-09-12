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

from datetime import datetime

try:
    import taipy.gui.builder as tgb
    from taipy.gui import Gui
except Exception as e:
    # Provide a clearer error when runtime dependencies (like pkg_resources from setuptools)
    # are missing in the test/CI environment.
    if isinstance(e, ModuleNotFoundError) and "pkg_resources" in str(e):
        raise ModuleNotFoundError(
            "Required package 'pkg_resources' is missing. Install 'setuptools' in the test environment (e.g., `pip install setuptools`) or ensure it is available in CI to import taipy.gui."
        ) from e
    raise


def test_date_builder_1(gui: Gui, test_client, helpers):
    gui._bind_var_val("date", datetime.strptime("15 Dec 2020", "%d %b %Y"))
    with tgb.Page(frame=None) as page:
        tgb.date(id="date", date="{date}")  # type: ignore[attr-defined]
    expected_list = [
        "<DateSelector",
        'defaultDate="2020-12-',
        'updateVarName="',
        'date="',
    ]
    helpers.test_control_builder(gui, page, expected_list)


def test_date_builder_2(gui: Gui, test_client, helpers):
    gui._bind_var_val("date", datetime.strptime("15 Dec 2020", "%d %b %Y"))
    with tgb.Page(frame=None) as page:
        tgb.date(id="date", date="{date}", with_time=True)  # type: ignore[attr-defined]
    expected_list = [
        "<DateSelector",
        'defaultDate="2020-12-',
        'updateVarName="',
        'date="',
        "withTime",
    ]
    helpers.test_control_builder(gui, page, expected_list)
