#!/usr/bin/env python3
"""
Lightweight utilities for parsing Dynamo (.dyn) JSON and building simple
graph indexes used by the Dynamo analyzers. Kept small and DRY so other
modules can import and reuse.
"""

from __future__ import annotations

import json
import os
from collections import defaultdict
from typing import Dict, List, Tuple, Any, Set


# -------------------------------
# JSON loading
# -------------------------------

def load_dyn(path: str) -> Dict[str, Any]:
    """Load a Dynamo .dyn file as JSON dict with basic validation."""
    if not os.path.isfile(path):
        raise FileNotFoundError(f"File not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict) or "Nodes" not in data or "Connectors" not in data:
        raise ValueError("Invalid .dyn file: missing Nodes/Connectors")
    return data


# -------------------------------
# Extraction helpers
# -------------------------------

def short_type(concrete_type: str) -> str:
    """Return a concise type name from a fully-qualified ConcreteType."""
    if not concrete_type:
        return ""
    # e.g., "PythonNodeModels.PythonNode, PythonNodeModels" → "PythonNode"
    left = concrete_type.split(",", 1)[0]
    return left.split(".")[-1]


def view_name_index(view: Dict[str, Any]) -> Dict[str, str]:
    """Map node Id → NodeViews.Name when available."""
    names = {}
    if not isinstance(view, dict):
        return names
    node_views = view.get("NodeViews") or []
    for nv in node_views:
        node_id = nv.get("Id")
        name = nv.get("Name")
        if node_id and name:
            names[node_id] = str(name)
    return names


def view_io_flags(view: Dict[str, Any]) -> Tuple[Set[str], Set[str]]:
    """Return sets of node ids marked as input/output in the view."""
    ins, outs = set(), set()
    if not isinstance(view, dict):
        return ins, outs
    for nv in view.get("NodeViews") or []:
        nid = nv.get("Id")
        if not nid:
            continue
        if nv.get("IsSetAsInput"):
            ins.add(nid)
        if nv.get("IsSetAsOutput"):
            outs.add(nid)
    return ins, outs


def build_indexes(data: Dict[str, Any]) -> Dict[str, Any]:
    """Build minimum indexes needed for analysis.

    Returns a dict with:
    - nodes: id → node dict (augmented with display_name)
    - port_to_node: portId → nodeId
    - adj: nodeId → [downstream nodeIds]
    - rev: nodeId → [upstream nodeIds]
    - view_names: nodeId → name
    - view_inputs, view_outputs: sets of nodeIds
    - dependencies: {packages: [(name, version)], deps: raw list}
    """
    nodes = {}
    for n in data.get("Nodes", []):
        nid = n.get("Id")
        if not nid:
            continue
        nodes[nid] = n

    vnames = view_name_index(data.get("View") or {})
    vin, vout = view_io_flags(data.get("View") or {})

    # Attach display_name once to keep DRY
    for nid, n in nodes.items():
        ntype = n.get("NodeType") or ""
        ctype = n.get("ConcreteType") or ""
        disp = (
            vnames.get(nid)
            or n.get("Description")
            or n.get("FunctionSignature")
            or short_type(ctype)
            or ntype
            or nid
        )
        n["display_name"] = str(disp)

    # Map ports to nodes; collect in/out port ids per node for quick lookup
    port_to_node: Dict[str, str] = {}
    in_ports: Dict[str, List[str]] = defaultdict(list)
    out_ports: Dict[str, List[str]] = defaultdict(list)
    for nid, n in nodes.items():
        for p in n.get("Inputs", []) or []:
            pid = p.get("Id")
            if pid:
                port_to_node[pid] = nid
                in_ports[nid].append(pid)
        for p in n.get("Outputs", []) or []:
            pid = p.get("Id")
            if pid:
                port_to_node[pid] = nid
                out_ports[nid].append(pid)

    # Build adjacency
    adj: Dict[str, List[str]] = defaultdict(list)
    rev: Dict[str, List[str]] = defaultdict(list)
    for c in data.get("Connectors", []) or []:
        s = c.get("Start")
        e = c.get("End")
        if not s or not e:
            continue
        s_node = port_to_node.get(s)
        e_node = port_to_node.get(e)
        if not s_node or not e_node or s_node == e_node:
            continue
        adj[s_node].append(e_node)
        rev[e_node].append(s_node)

    # Dependencies and packages
    packages = []
    for p in data.get("NodeLibraryDependencies", []) or []:
        name = p.get("Name") or p.get("ReferenceName") or ""
        ver = p.get("Version") or ""
        if name:
            packages.append((name, ver))
    deps = data.get("Dependencies", []) or []

    return {
        "nodes": nodes,
        "port_to_node": port_to_node,
        "adj": adj,
        "rev": rev,
        "view_names": vnames,
        "view_inputs": vin,
        "view_outputs": vout,
        "packages": packages,
        "dependencies": deps,
    }


def indegree_zero(nodes: Dict[str, Any], rev: Dict[str, List[str]]) -> List[str]:
    return [nid for nid in nodes if len(rev.get(nid, [])) == 0]


def outdegree_zero(nodes: Dict[str, Any], adj: Dict[str, List[str]]) -> List[str]:
    return [nid for nid in nodes if len(adj.get(nid, [])) == 0]


def format_file_title(path: str) -> str:
    base = os.path.basename(path)
    return f"Source File: {base}"

