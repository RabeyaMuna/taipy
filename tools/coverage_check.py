#!/usr/bin/env python
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

import argparse
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, Iterable, Set


def _parse_coverage_file(coverage_file: Path) -> ET.Element:
    if not coverage_file.exists():
        raise FileNotFoundError(f"Coverage file does not exist: {coverage_file}")
    return ET.parse(coverage_file).getroot()


def _ratio_to_percent(value: str) -> float:
    ratio = float(value)
    return ratio * 100 if ratio <= 1 else ratio


def _write(message: str, *, error: bool = False) -> None:
    stream = sys.stderr if error else sys.stdout
    stream.write(f"{message}\n")


def _get_total_coverage(coverage_file: Path) -> float:
    root = _parse_coverage_file(coverage_file)
    return _ratio_to_percent(root.attrib["line-rate"])


def _coverage_by_file(coverage_file: Path) -> Dict[str, Dict[int, int]]:
    root = _parse_coverage_file(coverage_file)
    coverage_by_file = {}

    for class_element in root.findall(".//class"):
        filename = class_element.attrib.get("filename")
        if not filename:
            continue
        line_hits = {}
        for line_element in class_element.findall("./lines/line"):
            number = int(line_element.attrib["number"])
            hits = int(line_element.attrib.get("hits", 0))
            line_hits[number] = hits
        coverage_by_file[filename] = line_hits

    return coverage_by_file


def _run_git_diff(base_branch: str) -> str:
    completed = subprocess.run(
        ["git", "diff", "--unified=0", f"origin/{base_branch}...HEAD", "--", "*.py"],
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout


def _changed_python_lines(base_branch: str) -> Dict[str, Set[int]]:
    changed_lines: Dict[str, Set[int]] = {}
    current_file = None

    for line in _run_git_diff(base_branch).splitlines():
        if line.startswith("+++ b/"):
            current_file = line.removeprefix("+++ b/")
            changed_lines.setdefault(current_file, set())
            continue
        if not line.startswith("@@ ") or current_file is None:
            continue

        new_hunk = line.split(" +", 1)[1].split(" ", 1)[0]
        start_length = new_hunk.split(",", 1)
        start = int(start_length[0])
        length = int(start_length[1]) if len(start_length) == 2 else 1
        if length > 0:
            changed_lines[current_file].update(range(start, start + length))

    return {filename: lines for filename, lines in changed_lines.items() if lines}


def _matching_coverage_keys(filename: str, coverage_files: Iterable[str]) -> Iterable[str]:
    normalized_filename = filename.replace("\\", "/")
    for coverage_file in coverage_files:
        normalized_coverage_file = coverage_file.replace("\\", "/")
        if normalized_filename == normalized_coverage_file or normalized_filename.endswith(
            f"/{normalized_coverage_file}"
        ):
            yield coverage_file


def _get_changed_coverage(coverage_file: Path, base_branch: str) -> float:
    changed_lines = _changed_python_lines(base_branch)
    if not changed_lines:
        _write("No changed Python lines to check.")
        return 100.0

    coverage_by_file = _coverage_by_file(coverage_file)
    covered_lines = 0
    total_lines = 0
    missing = []

    for filename, lines in changed_lines.items():
        file_coverage = {}
        for coverage_key in _matching_coverage_keys(filename, coverage_by_file.keys()):
            file_coverage.update(coverage_by_file[coverage_key])

        for line_number in sorted(lines):
            if line_number not in file_coverage:
                continue
            total_lines += 1
            if file_coverage[line_number] > 0:
                covered_lines += 1
            else:
                missing.append(f"{filename}:{line_number}")

    if total_lines == 0:
        _write("No executable changed Python lines to check.")
        return 100.0

    percent = covered_lines / total_lines * 100
    if missing:
        _write("Missing coverage for changed lines:")
        for item in missing:
            _write(f"  {item}")
    return percent


def _check_threshold(name: str, coverage: float, threshold: float) -> int:
    _write(f"{name} coverage: {coverage:.2f}%")
    _write(f"Required coverage: {threshold:.2f}%")
    if coverage < threshold:
        _write(f"{name} coverage is below the required threshold.", error=True)
        return 1
    return 0


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Check coverage thresholds.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    total_parser = subparsers.add_parser("check-total", help="Check total project coverage.")
    total_parser.add_argument("--coverage-file", required=True, type=Path)
    total_parser.add_argument("--threshold", required=True, type=float)

    changed_parser = subparsers.add_parser("check-changed", help="Check changed Python lines coverage.")
    changed_parser.add_argument("--coverage-file", required=True, type=Path)
    changed_parser.add_argument("--threshold", required=True, type=float)
    changed_parser.add_argument("--base-branch", required=True)

    return parser


def main() -> int:
    args = _build_parser().parse_args()

    if args.command == "check-total":
        return _check_threshold("Total", _get_total_coverage(args.coverage_file), args.threshold)
    if args.command == "check-changed":
        return _check_threshold(
            "Changed lines",
            _get_changed_coverage(args.coverage_file, args.base_branch),
            args.threshold,
        )

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
