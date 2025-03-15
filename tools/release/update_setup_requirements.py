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
# Updates the setup.requirements.txt files for a given package.
#
# Invoked by workflows/build-and-release-single-package.yml and workflows/build-and-release.yml.
# Working directory must be [root_dir].
# --------------------------------------------------------------------------------------------------

import os
import sys

from common import PACKAGES

BASE_PATH = "./tools/packages"


def usage() -> None:
    print(  # noqa: T201
        f"Usage: {sys.argv[0]} <package> <{'> <'.join(f"{p}_ver" for p in PACKAGES)}> <pypi_deps>"
    )
    packages = f"{', '.join(f"'{p}'" for p in PACKAGES[:-1])}, or '{PACKAGES[-1]}'"
    print(f"   <package> must be one of {packages}.")  # noqa: T201
    for p in PACKAGES:
        print(f"   <{p}_ver>: minimal version of the taipy-{p} dependency.")  # noqa: T201
    print("   <pypi_deps>: 'true' if dependencies are retrieved from Pypi.")  # noqa: T201


def __build_taipy_package_line(line: str, version: str, use_pypi: bool) -> str:
    _line = line.strip()
    if use_pypi:
        # Target dependency version should the latest compatible with 'version'
        major, minor = version.split(".")[:2]
        return f"{_line} >={version},<{major}.{int(minor) + 1}\n"
    tag = f"{version}-{_line.split('-')[1]}"
    tar_name = f"{_line}-{version}"
    return f"{_line} @ https://github.com/Avaiga/taipy/releases/download/{tag}/{tar_name}.tar.gz\n"


def update_setup_requirements(package: str, versions: dict[str, str], publish_on_py_pi: bool) -> None:
    _path = os.path.join(BASE_PATH, "taipy" if package == "taipy" else f"taipy-{package}", "setup.requirements.txt")
    lines = []
    with open(_path, mode="r") as req:
        for line in req:
            if v := versions.get(line.strip()):
                if v.startswith("0.0"):
                    raise ValueError(f"Missing version for dependency '{line.strip()}'.")
                line = __build_taipy_package_line(line, v, publish_on_py_pi)
            lines.append(line)

    with open(_path, "w") as file:
        file.writelines(lines)
    if True:  # More logs
        print(f"Generated setup.requirements.txt for package '{package}'")  # noqa: T201
        for line in lines:
            print(line)  # noqa: T201
        print("-" * 25)  # noqa: T201


if __name__ == "__main__":
    if len(sys.argv) < len(PACKAGES)+3:
        usage()
        raise ValueError("Missing arguments.")
    package = sys.argv[1]
    versions = { f"taipy-{p}": sys.argv[i] for i, p in enumerate(PACKAGES, 2) }
    pypi_deps = sys.argv[len(PACKAGES)+2].lower() == "true"

    update_setup_requirements(package, versions, pypi_deps)
