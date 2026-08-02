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

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from .._repository._base_taipy_model import _BaseModel


@dataclass
class _SequenceModel(_BaseModel):
    id: str
    owner_id: Optional[str]
    parent_ids: List[str]
    properties: Dict[str, Any]
    tasks: List[str]
    subscribers: List[Dict]
    version: str

    @staticmethod
    def from_dict(data: Dict[str, Any]):
        return _SequenceModel(
            id=data["id"],
            owner_id=data.get("owner_id"),
            parent_ids=_BaseModel._deserialize_attribute(data.get("parent_ids", [])),
            properties=_BaseModel._deserialize_attribute(data.get("properties", {})),
            tasks=_BaseModel._deserialize_attribute(data.get("tasks", [])),
            subscribers=_BaseModel._deserialize_attribute(data.get("subscribers", [])),
            version=data["version"],
        )

    def to_list(self):
        return [
            self.id,
            self.owner_id,
            _BaseModel._serialize_attribute(self.parent_ids),
            _BaseModel._serialize_attribute(self.properties),
            _BaseModel._serialize_attribute(self.tasks),
            _BaseModel._serialize_attribute(self.subscribers),
            self.version,
        ]
