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

import asyncio
import os
import typing as t

from fastapi import Response
from fastapi.responses import FileResponse


def send_file(
    path_or_file: t.Union[os.PathLike[str], str],
    **kwargs: t.Any,
) -> Response:
    return FileResponse(path_or_file, **kwargs)


def send_from_directory(
    directory: t.Union[os.PathLike[str], str],
    path: t.Union[os.PathLike[str], str],
    **kwargs: t.Any,
) -> Response:
    path = os.path.normpath(path)
    directory = os.path.normpath(directory)
    joined_path = os.path.join(directory, path)
    if not joined_path.startswith(directory):
        return Response("File not found", status_code=404)
    if not os.path.exists(joined_path) or not os.path.isfile(joined_path):
        return Response("File not found", status_code=404)
    if "as_attachment" in kwargs:
        if kwargs["as_attachment"]:
            kwargs["filename"] = os.path.basename(path)
            kwargs["media_type"] = "application/octet-stream"
            kwargs["headers"] = {"Content-Disposition": f"attachment; filename={os.path.basename(path)}"}
        del kwargs["as_attachment"]
    return FileResponse(joined_path, **kwargs)


def exec_async(async_func: t.Callable, *args, **kwargs) -> None:
    try:
        # future = asyncio.run_coroutine_threadsafe(async_func(*args, **kwargs), asyncio.get_event_loop())
        # return future.result()
        asyncio.get_event_loop().create_task(async_func(*args, **kwargs))
    except RuntimeError as ex:
        if "There is no current event loop in thread" in str(ex):
            asyncio.run(async_func(*args, **kwargs))
            return
        raise ex


def run_async(async_func: t.Callable, *args, **kwargs):
    try:
        return asyncio.get_event_loop().run_until_complete(async_func(*args, **kwargs))
    except RuntimeError as ex:
        if "There is no current event loop in thread" in str(ex):
            return asyncio.run(async_func(*args, **kwargs))
        raise ex
