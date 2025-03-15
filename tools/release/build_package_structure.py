# Copyright 2021-2024 Avaiga Private Limited
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.
# --------------------------------------------------------------------------------------------------
# Builds the structure to hold the package files.
#
# Invoked by the workflow files build-and-release-single-package.yml and build-and-release.yml.
# Working directory must be '[root]/taipy/<package>'.
# --------------------------------------------------------------------------------------------------

import os
import shutil
import sys
from pathlib import Path

from common import PACKAGES

__SKIP = ["LICENSE", "MANIFEST.in", "taipy", "setup.py", "tools", "pyproject.toml"]


def usage() -> None:
    print(f"Usage: {sys.argv[0]} <package>")  # noqa: T201
    packages = "','".join(PACKAGES)
    print(f"   <package> must be one of '{packages}', or 'taipy'.")  # noqa: T201


if __name__ == "__main__":
    if len(sys.argv) < 2:
        usage()
        raise ValueError("Missing arguments.")

    _package = sys.argv[1]
    _package_path = "taipy" if _package == "taipy" else f"taipy/{_package}"

    Path(_package_path).mkdir(parents=True, exist_ok=True)

    for file_name in os.listdir("."):
        if (
            file_name.lower().endswith(".md")
            or file_name in __SKIP
            or (_package == "taipy" and file_name in PACKAGES)
        ):
            continue
        shutil.move(file_name, _package_path)

    if _package != "taipy":
        shutil.copy("../__init__.py", "./taipy/__init__.py")
