#!/usr/bin/env python3
"""
Generate text-based flow structure for Dynamo (.dyn) graphs.
Minimal, DRY, and reusable across analyzers.
"""

import sys
from collections import deque
from typing import List, Dict, Any, Set

from dynamo_utils import load_dyn, build_indexes, indegree_zero, outdegree_zero, format_file_title


def _pick_starts(nodes: Dict[str, Any], rev: Dict[str, List[str]], view_inputs: Set[str]) -> List[str]:
    # Combine topology and view flags; no hard prioritization
    starts = set(indegree_zero(nodes, rev)) | set(view_inputs)
    return list(starts)


def _pick_ends(nodes: Dict[str, Any], adj: Dict[str, List[str]], view_outputs: Set[str]) -> List[str]:
    ends = set(outdegree_zero(nodes, adj)) | set(view_outputs)
    return list(ends)


def _simple_paths(adj: Dict[str, List[str]], start: str, end: str, cap_paths=50, cap_len=200) -> List[List[str]]:
    # DFS with caps for simplicity and safety
    results: List[List[str]] = []
    stack = [(start, [start])]
    visited_guard = 10_000
    steps = 0
    while stack and len(results) < cap_paths and steps < visited_guard:
        steps += 1
        node, path = stack.pop()
        if node == end:
            results.append(path)
            continue
        if len(path) >= cap_len:
            continue
        for nxt in adj.get(node, []):
            if nxt in path:
                continue  # avoid cycles in simple path
            stack.append((nxt, path + [nxt]))
    return results


def _score_path(path: List[str], nodes: Dict[str, Any]) -> int:
    # Prefer longer paths and paths with script/function nodes
    weight = 0
    for nid in path:
        n = nodes.get(nid, {})
        ctype = (n.get("ConcreteType") or "").lower()
        if "python" in ctype or "codeblock" in ctype or "dsfunction" in ctype:
            weight += 2
        else:
            weight += 1
    return weight


def analyze_flow(dyn_path: str) -> Dict[str, Any]:
    data = load_dyn(dyn_path)
    idx = build_indexes(data)

    nodes = idx["nodes"]
    adj = idx["adj"]
    rev = idx["rev"]
    starts = _pick_starts(nodes, rev, idx["view_inputs"])
    ends = _pick_ends(nodes, adj, idx["view_outputs"])

    # Enumerate candidate main paths
    all_paths: List[List[str]] = []
    for s in starts or list(nodes.keys())[:1]:
        for e in ends or list(nodes.keys())[-1:]:
            if s == e:
                continue
            paths = _simple_paths(adj, s, e)
            all_paths.extend(paths)

    # Pick top N by simple score
    scored = sorted(all_paths, key=lambda p: _score_path(p, nodes), reverse=True)[:10]

    # Branching/merge points
    branching = [nid for nid in nodes if len(adj.get(nid, [])) > 1]
    merges = [nid for nid in nodes if len(rev.get(nid, [])) > 1]

    return {
        "idx": idx,
        "paths": scored,
        "branching": branching,
        "merges": merges,
    }


def _name(nid: str, nodes: Dict[str, Any]) -> str:
    return nodes.get(nid, {}).get("display_name", nid)


def render_flow_report(flow: Dict[str, Any], dyn_path: str) -> str:
    idx = flow["idx"]
    nodes = idx["nodes"]
    adj = idx["adj"]
    rev = idx["rev"]

    lines: List[str] = []
    lines.append("# Dynamo Workflow Structure")
    lines.append("")
    lines.append(f"**{format_file_title(dyn_path)}**")
    lines.append("")

    # Component Summary
    lines.append("## Component Summary")
    lines.append(f"- Nodes: {len(nodes)}")
    lines.append(f"- Connections: {sum(len(v) for v in adj.values())}")
    lines.append(f"- Starts: {len([n for n in nodes if len(rev.get(n, [])) == 0])}")
    lines.append(f"- Ends: {len([n for n in nodes if len(adj.get(n, [])) == 0])}")
    lines.append("")

    # Main Workflow Paths
    lines.append("## Main Workflow Paths")
    if flow["paths"]:
        for path in flow["paths"]:
            parts = [f"{_name(nid, nodes)}" for nid in path]
            lines.append(" → ".join(parts))
    else:
        lines.append("(No clear start/end paths detected; graph may be cyclic or purely interactive.)")
    lines.append("")

    # Branching / Merges
    if flow["branching"]:
        lines.append("## Branching Points")
        for nid in flow["branching"]:
            lines.append(f"- {_name(nid, nodes)}")
        lines.append("")
    if flow["merges"]:
        lines.append("## Merge Points")
        for nid in flow["merges"]:
            lines.append(f"- {_name(nid, nodes)}")
        lines.append("")

    return "\n".join(lines)


def main(argv: List[str]) -> int:
    if len(argv) < 2:
        print("Usage: python dynamo_flow_diagram_generator.py <path>.dyn")
        return 2
    path = argv[1]
    try:
        flow = analyze_flow(path)
        print(render_flow_report(flow, path))
        return 0
    except Exception as e:
        print(f"Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))

