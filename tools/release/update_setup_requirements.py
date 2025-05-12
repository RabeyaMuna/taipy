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
import re
import sys
import typing as t

from common import PACKAGES, Version, retrieve_github_path

BASE_PATH = "./tools/packages"


def usage() -> None:
    packages = "> <".join(f"{p}_ver" for p in PACKAGES)
    print(  # noqa: T201
        f"Usage: {sys.argv[0]} <package> <{packages}> <deps> [<gh_path>]"
    )
    packages = ", ".join(f"'{p}'" for p in PACKAGES[:-1])
    packages = f"{packages}, or '{PACKAGES[-1]}'"
    print(f"   <package> must be one of {packages}.")  # noqa: T201
    for p in PACKAGES:
        print(f"   <{p}_ver>: minimal version of the taipy-{p} dependency.")  # noqa: T201
    print("   <deps> must be 'Pypi' or 'GitHub', indicating where to find Taipy package dependencies.")  # noqa: T201
    print("   <gh_path>: The path of GitHub repository (owner/repo), used if <deps> is 'GitHub'.")  # noqa: T201


def __build_taipy_package_line(line: str, version: Version, use_pypi: bool, gh_path: t.Optional[str]) -> str:
    line = line.strip()
    if use_pypi:
        # Target dependency version should the latest compatible with 'version'
        return f"{line} >={version.major}.{version.minor},<{version.major}.{version.minor + 1}\n"
    tag = f"{version}-{line.split('-')[1]}"
    tar_name = f"{line}-{version}"
    return f"{line} @ https://github.com/{gh_path}/releases/download/{tag}/{tar_name}.tar.gz#egg={line}\n"


def update_setup_requirements(
    package: str, versions: dict[str, Version], publish_on_py_pi: bool, gh_path: t.Optional[str]
) -> None:
    path = os.path.join(BASE_PATH, "taipy" if package == "taipy" else f"taipy-{package}", "setup.requirements.txt")
    lines = []
    with open(path, mode="r") as req:
        for line in req:
            if match := re.match(r"^taipy(:?\-\w+)?\s*", line, re.MULTILINE):
                # Add subpackage version if not forced
                if not line[match.end() :] and (v := versions.get(line.strip())):
                    if v == Version.UNKNOWN:
                        raise ValueError(f"Missing version for dependency '{line.strip()}'.")
                    line = __build_taipy_package_line(line, v, publish_on_py_pi, gh_path)
            lines.append(line)

    with open(path, "w") as file:
        file.writelines(lines)
    # Issue the generated files for logging information
    print(f"Generated setup.requirements.txt for package '{package}'")  # noqa: T201
    for line in lines:
        print(line.strip())  # noqa: T201
    print("-" * 32)  # noqa: T201


if __name__ == "__main__":
    if len(sys.argv) < len(PACKAGES) + 3:
        usage()
        raise ValueError("Missing arguments.")
    package = sys.argv[1]
    # Store the provided version for each package listed in PACKAGES
    versions = {f"taipy-{p}": Version.from_string(sys.argv[i]) for i, p in enumerate(PACKAGES, 2)}
    # Keep compatibility with legacy actions ('true' is equivalent to 'Pypi')
    pypi_deps = sys.argv[len(PACKAGES) + 2].lower() in ["true", "pypi"]
    gh_path = None
    if not pypi_deps:
        if len(sys.argv) < len(PACKAGES) + 4:
            gh_path = retrieve_github_path()
            if gh_path is None:
                usage()
                raise ValueError("Couldn't figure out GitHub branch path.")
        else:
            gh_path = sys.argv[len(PACKAGES) + 3]

    update_setup_requirements(package, versions, pypi_deps, gh_path)
