#!/usr/bin/env python3
"""Validate a BluPlai native whiteboard scene before sending it to the BluPlai MCP (copied from our bluplai-native-whiteboards skill)."""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any

COLORS = {
    "black", "grey", "light-violet", "violet", "blue", "light-blue",
    "yellow", "orange", "green", "light-green", "light-red", "red", "white",
}
FILLS = {"none", "semi", "solid", "pattern"}
SIZES = {"s", "m", "l", "xl"}
SIZE_PIXELS = {"s": 14, "m": 18, "l": 24, "xl": 32}
MCP_NODE_KEYS = {"id", "label", "x", "y", "width", "height", "size", "color", "fill"}
MCP_EDGE_KEYS = {"from_id", "to_id", "label", "bend"}


def number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def rect(node: dict[str, Any]) -> tuple[float, float, float, float] | None:
    fields = [node.get(key) for key in ("x", "y", "width", "height")]
    if not all(number(value) for value in fields):
        return None
    x, y, width, height = (float(value) for value in fields)
    return x, y, x + width, y + height


def intersection_ratio(first: tuple[float, float, float, float], second: tuple[float, float, float, float]) -> float:
    left = max(first[0], second[0])
    top = max(first[1], second[1])
    right = min(first[2], second[2])
    bottom = min(first[3], second[3])
    if right <= left or bottom <= top:
        return 0.0
    intersection = (right - left) * (bottom - top)
    first_area = (first[2] - first[0]) * (first[3] - first[1])
    second_area = (second[2] - second[0]) * (second[3] - second[1])
    return intersection / min(first_area, second_area)


def validate(scene: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    nodes = scene.get("nodes")
    edges = scene.get("edges", [])
    if not isinstance(nodes, list):
        return {"ready": False, "errors": ["nodes must be a list"], "warnings": [], "stats": {}}
    if not isinstance(edges, list):
        return {"ready": False, "errors": ["edges must be a list"], "warnings": [], "stats": {}}
    if not 1 <= len(nodes) <= 50:
        errors.append("nodes must contain between 1 and 50 items")
    if len(edges) > 100:
        errors.append("edges cannot exceed 100 items")

    ids: set[str] = set()
    positioned: list[dict[str, Any]] = []
    for index, node in enumerate(nodes):
        prefix = f"node[{index}]"
        if not isinstance(node, dict):
            errors.append(f"{prefix} must be an object")
            continue
        node_id = str(node.get("id") or "").strip()
        label = str(node.get("label") or "").strip()
        if not node_id:
            errors.append(f"{prefix} id is required")
        elif node_id in ids:
            errors.append(f"duplicate node id: {node_id}")
        else:
            ids.add(node_id)
        if not 1 <= len(label) <= 300:
            errors.append(f"{prefix} label must contain 1 to 300 characters")

        bounds = {"width": (120, 2000), "height": (60, 2000), "x": (-20000, 20000), "y": (-20000, 20000)}
        for field, (minimum, maximum) in bounds.items():
            value = node.get(field)
            if value is None:
                warnings.append(f"{node_id or prefix} omits {field}; deterministic layout is safer")
            elif not number(value) or not minimum <= float(value) <= maximum:
                errors.append(f"{node_id or prefix} {field} must be between {minimum} and {maximum}")
        size = str(node.get("size") or "m").lower()
        color = str(node.get("color") or "black").lower()
        fill = str(node.get("fill") or "none").lower()
        if size not in SIZES:
            errors.append(f"{node_id or prefix} size must be one of {sorted(SIZES)}")
        if color not in COLORS:
            errors.append(f"{node_id or prefix} color is unsupported: {color}")
        if fill not in FILLS:
            errors.append(f"{node_id or prefix} fill must be one of {sorted(FILLS)}")

        node_rect = rect(node)
        if node_rect:
            positioned.append(node)
            max_line = max((len(line) for line in label.splitlines()), default=0)
            estimated_width = max_line * SIZE_PIXELS.get(size, 18) * 0.56 + 28
            line_count = max(1, len(label.splitlines()))
            estimated_height = line_count * SIZE_PIXELS.get(size, 18) * 1.35 + 24
            if float(node["width"]) < estimated_width:
                warnings.append(f"{node_id} label may wrap or clip; estimated width {estimated_width:.0f}")
            if float(node["height"]) < estimated_height:
                warnings.append(f"{node_id} label may clip; estimated height {estimated_height:.0f}")

    for index, edge in enumerate(edges):
        prefix = f"edge[{index}]"
        if not isinstance(edge, dict):
            errors.append(f"{prefix} must be an object")
            continue
        source = str(edge.get("from_id") or "").strip()
        target = str(edge.get("to_id") or "").strip()
        if source not in ids or target not in ids:
            errors.append(f"{prefix} references an unknown node: {source} -> {target}")
        if len(str(edge.get("label") or "")) > 160:
            errors.append(f"{prefix} label exceeds 160 characters")
        bend = edge.get("bend", 0)
        if not number(bend) or not -1000 <= float(bend) <= 1000:
            errors.append(f"{prefix} bend must be between -1000 and 1000")

    for first_index, first in enumerate(positioned):
        if first.get("role") == "container":
            continue
        first_rect = rect(first)
        if not first_rect:
            continue
        for second in positioned[first_index + 1:]:
            if second.get("role") == "container":
                continue
            second_rect = rect(second)
            if not second_rect:
                continue
            ratio = intersection_ratio(first_rect, second_rect)
            if ratio >= 0.08:
                warnings.append(f"{first.get('id')} overlaps {second.get('id')} by {ratio:.0%} of the smaller card")

    all_rects = [rect(node) for node in positioned]
    all_rects = [value for value in all_rects if value]
    canvas = None
    if all_rects:
        canvas = {
            "x": min(value[0] for value in all_rects),
            "y": min(value[1] for value in all_rects),
            "width": max(value[2] for value in all_rects) - min(value[0] for value in all_rects),
            "height": max(value[3] for value in all_rects) - min(value[1] for value in all_rects),
        }
        aspect = canvas["width"] / max(canvas["height"], 1)
        if aspect < 1.25 or aspect > 2.25:
            warnings.append(f"scene aspect ratio {aspect:.2f} may not present cleanly on screen")

    return {
        "ready": not errors,
        "errors": errors,
        "warnings": warnings,
        "stats": {"nodes": len(nodes), "edges": len(edges), "canvas": canvas},
    }


def mcp_payload(scene: dict[str, Any]) -> dict[str, Any]:
    return {
        "nodes": [{key: value for key, value in node.items() if key in MCP_NODE_KEYS} for node in scene["nodes"]],
        "edges": [{key: value for key, value in edge.items() if key in MCP_EDGE_KEYS} for edge in scene.get("edges", [])],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("scene", type=Path)
    parser.add_argument("--emit-mcp-payload", type=Path)
    parser.add_argument("--strict", action="store_true", help="Treat warnings as a failing result")
    args = parser.parse_args(argv)

    try:
        scene = json.loads(args.scene.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(json.dumps({"ready": False, "errors": [str(exc)], "warnings": [], "stats": {}}, indent=2))
        return 1
    if not isinstance(scene, dict):
        print(json.dumps({"ready": False, "errors": ["scene root must be an object"], "warnings": [], "stats": {}}, indent=2))
        return 1

    report = validate(scene)
    print(json.dumps(report, indent=2))
    if report["ready"] and args.emit_mcp_payload:
        args.emit_mcp_payload.parent.mkdir(parents=True, exist_ok=True)
        args.emit_mcp_payload.write_text(json.dumps(mcp_payload(scene), indent=2) + "\n", encoding="utf-8")
    if report["errors"] or (args.strict and report["warnings"]):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
