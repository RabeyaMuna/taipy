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
# --------------------------------------------------------------------------------------------------

import sys

import requests
from common import PACKAGES, Package, Version, retrieve_github_path


def usage() -> None:
    print(f"Usage: {sys.argv[0]} <package> <version> <dev_version> <deps> [<gh_path>]")  # noqa: T201
    print("   <package> must be a Taipy package name.")  # noqa: T201
    print("   <version> is the target version for *package*. It must of the form: <Maj>.<Min>.<Tech>[.dev*].")  # noqa: T201
    print("   <release_type> must be one of 'dev' or 'production'.")  # noqa: T201
    print("   <deps> must be 'Pypi' or 'GitHub', indicating where to find Taipy package dependencies.")  # noqa: T201
    print("   <gh_path>: The path of GitHub repository (owner/repo), used if <deps> is 'GitHub'.")  # noqa: T201


def fetch_latest_github_releases(package: Package, version: Version, dev: bool, gh_path: str) -> dict[Package, Version]:
    """Find the latest release version for each package, in the GitHub releases.

    All release versions are retrieved from GitHub, and we keep the ones that have a version that
    is compatible with *version*.
    "dev" releases are kept only if *dev* is True.

    Return:
        A dictionary make of [package, version] pairs where the *package* package's version is set
        to *version*.
    """
    # Retrieve all available releases (potentially paginating results) for all packages
    available_releases = {}
    url = f"https://api.github.com/repos/{gh_path}/releases"
    page = 1
    while url:
        response = requests.get(url, params={"per_page": 50, "page": page})
        response.raise_for_status()  # Raise error for bad responses
        for release in response.json():
            tag_name = release["tag_name"]
            pkg_ver, pkg = tag_name.split("-") if "-" in tag_name else (tag_name, "taipy")
            versions: list[str] = available_releases.get(pkg, [])
            versions.append(pkg_ver)
            available_releases[pkg] = versions

        # Check for pagination in the `Link` header
        link_header = response.headers.get("Link", "")
        if 'rel="next"' in link_header:
            url = link_header.split(";")[0].strip("<>")  # Extract next page URL
            page += 1
        else:
            url = None  # No more pages

    # For each package, pick the latest that *version* is compatible with
    releases = {}
    for pkg_name in PACKAGES:
        available = available_releases.get(pkg_name, None)
        if available:
            for pkg_ver in available:
                pkg_version = Version.from_string(pkg_ver)
                if pkg_version.ext and (not dev or not pkg_version.validate_extension("dev")):
                    continue
                if version.is_compatible(pkg_version):
                    releases[pkg_name] = pkg_version
                    break

    # Fill in missing versions
    releases[package.short_name] = version
    for p in PACKAGES:
        if p not in releases:
            releases[p] = Version.UNKNOWN
    return releases


def fetch_latest_pypi_releases(package: Package, version: Version, dev: bool, _gh_path: str) -> dict[Package, Version]:
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
    gh_path = ""
    if not pypi_deps:
        if len(sys.argv) < 6:
            gh_path = retrieve_github_path()
            if gh_path is None:
                usage()
                raise ValueError("Couldn't figure out GitHub branch path.")
        else:
            gh_path = sys.argv[5]

    fetch_latest_releases = fetch_latest_pypi_releases if pypi_deps else fetch_latest_github_releases
    versions = fetch_latest_releases(package, version, is_dev_version, gh_path)

    for p, v in versions.items():
        print(f"{p}_VERSION={v}")  # noqa: T201
