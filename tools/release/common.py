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
# Common artifacts used by the other scripts located in this directory.
# --------------------------------------------------------------------------------------------------
import os
import re
import typing as t
from dataclasses import asdict, dataclass

# These are the base name of the sub packages taipy-*
# They also are the names of the directory where their code belongs, under the 'taipy' directory
# in the root of the Taipy repository.
PACKAGES = ["common", "core", "gui", "rest", "templates"]


@dataclass
class Version:
    """Helps manipulate version numbers."""

    major: int
    minor: int
    patch: int
    ext: t.Optional[str] = None

    # Unknown version constant
    UNKNOWN: t.ClassVar["Version"]

    @property
    def name(self) -> str:
        """Returns a string representation of this Version without the extension part."""
        return f"{self.major}.{self.minor}.{self.patch}"

    @property
    def full_name(self) -> str:
        """Returns a full string representation of this Version."""
        return f"{self.name}.{self.ext}" if self.ext else self.name

    def __str__(self) -> str:
        """Returns a full string representation of this version."""
        return self.full_name

    @classmethod
    def from_string(cls, version: str):
        """Creates a Version from a string.

        Parameters:
            version: a version name as a string.<br/>
              The format should be "<major>.<minor>.<patch>[.<extension>] where

              - <major> must be a number, indicating the major number of the version
              - <minor> must be a number, indicating the minor number of the version
              - <patch> must be a number, indicating the patch level of the version
              - <extension> must be a string. It is common practice that <extension> ends with a
                number, but it is not required.
        Returns:
            A new Version object with the appropriate values that were parsed.
        """
        match = re.fullmatch(r"(\d+)\.(\d+)\.(\d+)(?:\.([^\s]+))?", version)
        if match:
            major = int(match[1])
            minor = int(match[2])
            patch = int(match[3])
            ext = match[4]
            return cls(major=major, minor=minor, patch=patch, ext=ext)
        else:
            raise ValueError(f"String not in expected format: {version}")

    def to_dict(self) -> dict[str, str] :
        """Returns this Version as a dictionary.
        """
        return {k: v for k, v in asdict(self).items() if v is not None}

    def bump_ext_version(self) -> "Version":
        """Returns a new Version object where the extension part version was incremented.

        If this Version has no extension part, this method returns *self*.
        """
        if not self.ext or (m := re.search(r"([0-9]+)$", self.ext)) is None:
            return self

        ext_ver = int(m[1])+1
        return Version(self.major, self.minor, self.patch, f"{self.ext[: m.start(1)]}{ext_ver}")

    def validate_extension(self, ext="dev"):
        """Returns True if the extension part of this Version is the one queried."""
        return self._split_ext()[0] == ext

    def _split_ext(self) -> t.Tuple[str, int]:
        """Splits extension into the (identifier, index) tuple

        Returns:
            ("", -1) if there is no extension.
            (extension, -1) if there is no extension index.
            (extension, index) if there is an extension index (e.g. "dev3").
        """
        if not self.ext or (match := re.fullmatch(r"(.*?)(\d+)?", self.ext)) is None:
            return ("", -1)  # No extension
        # Potentially no index
        return (match[1], int(match[2]) if match[2] else -1)

    def is_compatible(self, version: "Version") -> bool:
        """Checks if this version is compatible with another.

        Version v1 is defined as being compatible with version v2 if a package built with version v1
        can safely depend on another package built with version v2.<br/>
        Here are the conditions set when checking whether v1 is compatible with v2:

        - If v1 and v2 have different major or minor numbers, they are not compatible.
        - If v1 has no extension, it is compatible only with v2 that have no extension.
        - If v1 has an extension, it is compatible with any v2 that has the same extension, no
          matter the extension index.

        I.e.:
            package-1.[m].[t] is NOT compatible with any sub-package-[M].* where M != 1
            package-1.2.[t] is NOT compatible with any sub-package-1.[m].* where m != 2
            package-1.2.[t] is compatible with all sub-package-1.2.*
            package-1.2.[t].ext[X] is compatible with all sub-package-1.2.*.ext*
            package-1.2.3 is NOT compatible with any sub-package-1.2.*.*
            package-1.2.3.extA is NOT compatible with any sub-package-1.2.*.extB if extA != extB,
               independently of a potential extension index.

        Parameters:
            version: the version to check compatibility against.

        Returns:
            True is this Version is compatible with *version* and False if it is not.
        """
        if self.major != version.major or self.minor != version.minor:
            return False
        if self.patch > version.patch:
            return True
        if self.patch == version.patch:
            # No extensions on either → Compatible
            if not self.ext and not version.ext:
                return True

            # self has extension, version doesn't → Compatible
            if self.ext and not version.ext:
                return True

            # Version has extension, self doesn't → Not compatible
            if not self.ext and version.ext:
                return False

            # Both have extensions → check identifiers. Dissimilar identifiers → Not compatible
            self_prefix, _ = self._split_ext()
            other_prefix, _ = version._split_ext()
            if self_prefix != other_prefix:
                return False

            # Same identifiers → Compatible
            return True

        # If self.patch < version.patch → Not compatible
        return False

Version.UNKNOWN = Version(0, 0, 0)

class Package:
    """Information on any Taipy package and sub-package.
    """
    def __init__(self, package: str) -> None:
        self._name = package
        if package == "taipy":
            self._short = package
        else:
            if package.startswith("taipy-"):
                self._short = package[6:]
            else:
                self._name = f"taipy-{package}"
                self._short = package
            if self._short not in PACKAGES:
                raise ValueError(f"Invalid package name {package}.")

    @property
    def name(self) -> str:
        """The full package name."""
        return self._name

    @property
    def short_name(self) -> str:
        """The short package name."""
        return self._short

    @property
    def package_dir(self) -> str:
        return "taipy" if self._name == "taipy" else os.path.join("taipy", self._short)

    def __str__(self) -> str:
        """Returns a full string representation of this package."""
        return self.name


def retrieve_github_path() -> t.Optional[str]:
    # Retrieve current Git branch remote URL
    def run(*args) -> str:
        return subprocess.run(args, stdout=subprocess.PIPE, text=True, check=True).stdout.strip()
    branch_name = run("git", "branch", "--show-current")
    remote_name = run("git", "config", f"branch.{branch_name}.remote")
    url = run("git", "remote", "get-url", remote_name)
    if match := re.fullmatch(r"git@github.com:(.*)\.git", url):
        return match[1]
    print("ERROR - Could not retrieve GibHub branch path")  # noqa: T201
    return None
