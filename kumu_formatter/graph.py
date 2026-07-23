"""Graph accumulator for Kumu elements and connections.

Deduplicates nodes by label and edges by (from, to, type), and drops any
entry with an empty or missing endpoint.
"""

from __future__ import annotations

import math
from typing import Any


def _is_missing(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, float) and math.isnan(value):
        return True
    return str(value).strip() == ""


class KumuGraph:
    def __init__(self) -> None:
        self.elements: list[dict] = []
        self.connections: list[dict] = []
        self._element_labels: set[str] = set()
        self._connection_keys: set[tuple] = set()

    def add_element(self, label: Any, node_type: str, description: Any = "") -> None:
        if _is_missing(label):
            return
        label = str(label)
        if label in self._element_labels:
            return
        desc = "" if _is_missing(description) else str(description)
        self.elements.append({"label": label, "type": node_type, "description": desc})
        self._element_labels.add(label)

    def add_connection(
        self, source: Any, target: Any, conn_type: str, direction: str = "directed"
    ) -> None:
        if _is_missing(source) or _is_missing(target):
            return
        source, target = str(source), str(target)
        key = (source, target, conn_type)
        if key in self._connection_keys:
            return
        self.connections.append(
            {"from": source, "to": target, "direction": direction, "type": conn_type}
        )
        self._connection_keys.add(key)

    def to_dict(self) -> dict:
        return {"elements": self.elements, "connections": self.connections}
