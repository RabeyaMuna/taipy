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
# Returns the latest released versions for every Taipy package that is compatible with the target
# version (major and minor numbers match).
# The target package's version is set to the target version.
#
# Invoked from the workflow in build-and-release-single-package.yml.
#
# Outputs a line for each package (including  'taipy"):
#   <package_short_name>_VERSION=<package_version>
# If a dev release is requested, a similar line is issued indicating the next dev version number:
#   NEXT_<package_short_name>_VERSION=<package_version>
# An additional line is added containing the latest release for 'taipy', no matter what the target
# version is. This version is extracted so that it has no extension:
#   LATEST_TAIPY_VERSION=<package_version>
# --------------------------------------------------------------------------------------------------

import sys
import typing as t

import requests
from common import PACKAGES, Package, Version, fetch_github_releases, fetch_latest_github_taipy_releases


def usage() -> None:
    print(f"Usage: {sys.argv[0]} <package> <version> <dev_version> <deps> [<gh_path>]")  # noqa: T201
    print("   <package> must be a Taipy package name.")  # noqa: T201
    print("   <version> is the target version for *package*. It must of the form: <Maj>.<Min>.<Tech>[.dev*].")  # noqa: T201
    print("   <release_type> must be one of 'dev' or 'production'.")  # noqa: T201
    print("   <deps> must be 'Pypi' or 'GitHub', indicating where to find Taipy package dependencies.")  # noqa: T201
    print("   <gh_path>: The path of GitHub repository (owner/repo), used if <deps> is 'GitHub'.")  # noqa: T201


def fetch_latest_github_releases(
    package: Package, version: Version, dev: bool, all_releases: dict[Package, list[Version]]
) -> dict[Package, Version]:
    """Find the latest release version for each package, in the GitHub releases.

    All release versions are retrieved from GitHub, and we keep the ones that have a version that
    is compatible with *version*.
    "dev" releases are kept only if *dev* is True.

    Arguments:
        package: The package that we want to force *version* for.
        version: The incoming version of package *package*.
        dev: True if we're targeting a dev release, False for a production release.
        gh_path: The "OWNER/REPO" string at the beginning of the working repository.
          If not provided, it is computed at runtime from the current Git branch remote URL.

    Return:
        A dictionary make of [package, version] pairs where the *package* package's version is set
        to *version*.
    """
    # For each package, pick the latest that *version* is compatible with
    all_package_names = PACKAGES + ["taipy"]
    releases = {}
    for pkg_name in all_package_names:
        a_package = Package(pkg_name)
        if versions := all_releases.get(a_package):
            for a_version in versions:
                if a_version.ext and (not dev or not a_version.validate_extension("dev")):
                    continue
                if version.is_compatible(a_version):
                    releases[pkg_name] = a_version
                    break

    # Fill in missing versions
    releases[package.short_name] = version
    for p in all_package_names:
        if p not in releases:
            releases[p] = Version.UNKNOWN

    return {Package(p): v for p, v in releases.items()}


def fetch_latest_pypi_releases(package: Package, version: Version, dev: bool) -> dict[Package, Version]:
    """Find the latest release version for each package, in the Pypi releases.

    All release versions are retrieved from Pypi, and we keep the ones that have a version that
    is compatible with *version*.
    "dev" releases are kept only if *dev* is True.

    Return:
        A dictionary make of [package, version] pairs where the *package* package's version is set
        to *version*.
    """

    def retrieve_package_version(sub_pkg: Package, dev: bool) -> Version:
        """Returns the latest release version for *sub_pkg* on Pypi that is compatible with *version*."""
        url = f"https://pypi.org/pypi/{sub_pkg.name}/json"
        response = requests.get(url)
        resp_json = response.json()
        # All release versions for the <sub_pkg> package
        versions = list(resp_json["releases"].keys())
        if versions:
            versions.reverse()  # More recent release is last
            # Find first that <version> would be compatible with
            for v in versions:
                check_version = Version.from_string(v)
                # Drop all version with extension if not dev
                # Keep 'dev' extensions if dev
                if check_version.ext and (not dev or not check_version.validate_extension("dev")):
                    continue
                if version.is_compatible(check_version):
                    return check_version
        return Version.UNKNOWN

    releases = {pkg: retrieve_package_version(pkg, dev) for pkg in [Package(p) for p in PACKAGES]}
    releases[package] = version
    return releases


if __name__ == "__main__":
    if len(sys.argv) < 5:
        usage()
        raise ValueError("Missing arguments.")
    package = Package(sys.argv[1])
    version = Version.from_string(sys.argv[2])

    is_dev_version = sys.argv[3] == "dev"
    if is_dev_version and (version.ext is None or not version.validate_extension("dev")):
        raise ValueError("Version extension does not contain 'dev'.")

    pypi_deps = sys.argv[4] == "Pypi" or sys.argv[4] == "true"  # true to keep pre-4.0.3 compatibility
    gh_path = sys.argv[5] if len(sys.argv) > 5 else None

    # Retrieve all available Github releases for all packages
    all_releases = fetch_github_releases(gh_path)
    # Compute the latest versions compatible with *version*
    versions = (
        fetch_latest_pypi_releases(package, version, is_dev_version)
        if pypi_deps
        else fetch_latest_github_releases(package, version, is_dev_version, all_releases)
    )
    # Print them out
    for p, v in versions.items():
        print(f"{p.short_name}_VERSION={v}")  # noqa: T201

    # Print out the latest 'taipy' version that has no extension
    print(f"LATEST_TAIPY_VERSION={fetch_latest_github_taipy_releases(all_releases)}")  # noqa: T201
