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
from time import sleep

from taipy import Submission


def assert_true_after_time(assertion, time=120, msg=None, **msg_params):
    loops = 0
    start = datetime.now()
    while (datetime.now() - start).seconds < time:
        sleep(1)  # Limit CPU usage
        try:
            if assertion():
                return
        except BaseException as e:
            print("Raise : ", e)  # noqa: T201
            loops += 1
            continue
    if msg:
        print(msg(**msg_params))  # noqa: T201
    assert assertion()


def assert_submission_status(submission: Submission, expected_status, timeout=120):
    assert_true_after_time(
        lambda: submission.submission_status == expected_status,
        time=timeout,
        msg=submission_status_message,
        submission=submission,
        timeout=timeout)


def submission_status_message(submission: Submission, expected_status, timeout=120):
    ms = "\n--------------------------------------------------------------------------------\n"
    ms += f"Submission status is {submission.submission_status} after {timeout} seconds.\n"
    ms += f"                Expected status was {expected_status}.\n"
    ms += "--------------------------------------------------------------------------------\n"
    ms += "                              --------------                                    \n"
    ms += "                               Job statuses                                     \n"
    for job in submission.jobs:
        ms += f"{job.id}: {job.status}\n"
    ms += "--------------------------------------------------------------------------------\n"
    return ms


def _assert_available_workers(dispatcher, expected_workers, timeout=120):
    """Assert that the dispatcher has the expected number of available workers."""
    assert_true_after_time(
        lambda: dispatcher._nb_available_workers == expected_workers,
        time=timeout,
        msg=lambda: f"Expected {expected_workers} available workers, got {dispatcher._nb_available_workers}"
    )


def _assert_blocked_jobs_count(expected_count, timeout=120):
    """Assert that the expected number of jobs are blocked."""
    from taipy.core._orchestrator._orchestrator import _Orchestrator
    assert_true_after_time(
        lambda: len(_Orchestrator.blocked_jobs) == expected_count,
        time=timeout,
        msg=lambda: f"Expected {expected_count} blocked jobs, got {len(_Orchestrator.blocked_jobs)}"
    )
