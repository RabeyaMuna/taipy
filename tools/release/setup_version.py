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
#
# Outputs a line for each package (all packages if 'all'):
#   <package_short_name>_VERSION=<package_version>
# If a dev release is requested, a similar line is issued indicating the next dev version number:
#   NEXT_<package_short_name>_VERSION=<package_version>
# --------------------------------------------------------------------------------------------------

import json
import sys
from pathlib import Path

from common import PACKAGES, Package, Version


def usage() -> None:
    print(f"Usage: {sys.argv[0]} <package> <release_type> [<version> <branch>]")  # noqa: T201
    print("   if <package> is 'ALL' then all packages including taipy are processed.")  # noqa: T201
    print("   <release_type> must be 'dev' or 'production'")  # noqa: T201
    print("     If <release_type> is 'production', <version> must be specified as the target")  # noqa: T201
    print("     version and <branch> must be set to the name of the current branch.")  # noqa: T201


def extract_version(package: Package) -> Version:
    """
    Returns a Version from a package's version.json content.
    """
    with open(Path(package.package_dir) / "version.json") as version_file:
        data = json.load(version_file)
        return Version(**data)


def __setup_dev_version(package: Package, version: Version) -> None:
    if not version.validate_extension("dev"):
        raise ValueError(f"{version=} is not a 'dev' version in package {package}.")

    var_name = f"{package.short_name}_VERSION"
    print(f"{var_name}={version.full_name}")  # noqa: T201

    # Increment dev version
    version = version.bump_ext_version()
    # Save in packages's version.json
    with open(Path(package.package_dir) / "version.json", "w") as version_file:
        json.dump(version.to_dict(), version_file)
    # Return it to the GitHub step
    print(f"NEXT_{var_name}={version.full_name}")  # noqa: T201


def __setup_prod_version(
    package: Package, version: Version, target_version: str, branch_name: str) -> None:
    if version.full_name != target_version:
        raise ValueError(f"Current {version=} does not match {target_version=} for package {package.name}")

    # Production releases can only be performed from a release branch
    if target_branch_name := f"release/{version.major}.{version.minor}" != branch_name:
        raise ValueError(
            f"Branch name mismatch branch={branch_name} does not match target branch name={target_branch_name}"
        )

    print(f"{package.short_name}_VERSION={version.name}")  # noqa: T201


if __name__ == "__main__":
    if len(sys.argv) < 3:
        usage()
        raise ValueError("Missing arguments.")

    packages = [sys.argv[1]] if sys.argv[1].lower() != "all" else PACKAGES + ["taipy"]
    release_type = sys.argv[2]

    for package_name in packages:
        package = Package(package_name)
        version = extract_version(package)

        if release_type == "dev":
            __setup_dev_version(package, version)
        elif release_type == "production":
            if len(sys.argv) < 5:
                usage()
                raise ValueError("Missing arguments.")
            __setup_prod_version(package, version, sys.argv[3], sys.argv[4])
        else:
            usage()
            raise ValueError(f"Invalid <release_type> argument ({release_type}).")
