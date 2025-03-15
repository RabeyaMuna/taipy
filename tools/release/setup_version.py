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
# Checks that build version matches package version.
# Updates version number for future 'dev' builds.
#
# Invoked from the workflow in build-and-release.yml.
# --------------------------------------------------------------------------------------------------

import json
import os
import sys
import typing as t

from common import PACKAGES, Version


def usage() -> None:
    print(f"Usage: {sys.argv[0]} <path> <release_type> [<version> <branch>]")  # noqa: T201
    print("   Checks that all <package>-<version> archives exist in <root_path>.")  # noqa: T201
    print("   if <path> is 'ALL' then ")  # noqa: T201
    print("   <release_type> must be 'dev' or 'production'")  # noqa: T201


def __write_version_to_path(base_path: str, version: Version) -> None:
    with open(os.path.join(base_path, "version.json"), "w") as version_file:
        json.dump(version.to_dict(), version_file)


def extract_version(base_path: str) -> Version:
    """
    Load version.json file from base path and return the version string.
    """
    with open(os.path.join(base_path, "version.json")) as version_file:
        data = json.load(version_file)
        return Version(**data)


def __setup_dev_version(version: Version, _base_path: str, name: t.Optional[str] = None) -> None:
    if not version.validate_extension("dev"):
        raise ValueError(f"{version=} is not a 'dev' version.")

    name = f"{name}_VERSION" if name else "VERSION"
    print(f"{name}={version.full_name}")  # noqa: T201

    version = version.bump_ext_version()

    __write_version_to_path(_base_path, version)
    print(f"NEW_{name}={version.full_name}")  # noqa: T201


def __setup_prod_version(version: Version, target_version: str, branch_name: str, name: t.Optional[str] = None) -> None:
    if str(version) != target_version:
        raise ValueError(f"Current {version=} does not match {target_version=}")

    if target_branch_name := f"release/{version.major}.{version.minor}" != branch_name:
        raise ValueError(
            f"Branch name mismatch branch={branch_name} does not match target branch name={target_branch_name}"
        )

    name = f"{name}_VERSION" if name else "VERSION"
    print(f"{name}={version.name}")  # noqa: T201


if __name__ == "__main__":
    if len(sys.argv) < 3:
        usage()
        raise ValueError("Missing arguments.")

    paths = (
        [sys.argv[1]]
        if sys.argv[1].lower() != "all"
        else [ f"taipy{os.sep}{p}" for p in PACKAGES ] + [ "taipy" ]
    )
    _environment = sys.argv[2]

    for _path in paths:
        _version = extract_version(_path)
        _name = None if _path == "taipy" else _path.split(os.sep)[-1]

        if _environment == "dev":
            __setup_dev_version(_version, _path, _name)
        elif _environment == "production":
            if len(sys.argv) < 5:
                usage()
                raise ValueError("Missing arguments.")
            __setup_prod_version(_version, sys.argv[3], sys.argv[4], _name)
        else:
            usage()
            raise ValueError(f"Invalid <release_type> argument ({_environment}).")
