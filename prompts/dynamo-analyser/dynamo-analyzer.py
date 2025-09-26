#!/usr/bin/env python3
"""
Unified Dynamo (.dyn) analyzer that produces a single structured report:
- Executive Summary
- Workflow Summary (concise; no full diagram)
- Libraries & Dependencies
- Custom Script Analysis
- Algorithmic Analysis (A–E)
- Definition Summary

Saves to: <input>-dynamo-report.md
"""

import os
import sys
from typing import List

from dynamo_utils import load_dyn, build_indexes, format_file_title
from dynamo_flow_diagram_generator import analyze_flow
from dynamo_script_extractor import extract_scripts, render_script_report


def _exec_summary(idx, scripts) -> str:
    nodes = idx["nodes"]
    has_py = any("python" in (n.get("ConcreteType") or "").lower() for n in nodes.values())
    uses_revit = any(
        sig.lower().startswith("revit.") for sig in scripts.get("ds_functions", [])
    ) or any("revitapi" in h.lower() for h in scripts.get("py_hints", []))
    has_geom = any(sig.lower().startswith("autodesk.designscript.geometry") for sig in scripts.get("ds_functions", []))

    lines = []
    lines.append("## Executive Summary")
    parts = ["Analyzes a Dynamo graph to understand its workflow and custom code."]
    if uses_revit:
        parts.append("Interacts with Revit API (collects/filters/updates model data).")
    if has_py:
        parts.append("Contains Python scripts for custom logic.")
    if has_geom:
        parts.append("Uses DesignScript geometry operations.")
    lines.append(" ".join(parts))
    lines.append("")
    return "\n".join(lines)


def _workflow_summary(idx, flow) -> str:
    lines = ["## Workflow Summary"]
    starts = [n for n in idx["nodes"] if len(idx["rev"].get(n, [])) == 0]
    ends = [n for n in idx["nodes"] if len(idx["adj"].get(n, [])) == 0]
    lines.append(f"- Start Nodes: {len(starts)}")
    lines.append(f"- End Nodes: {len(ends)}")
    lines.append(f"- Branching Points: {len(flow.get('branching', []))}")
    lines.append(f"- Merge Points: {len(flow.get('merges', []))}")
    if flow.get("paths"):
        best = flow["paths"][0]
        names = [idx["nodes"][nid]["display_name"] for nid in best]
        if len(names) > 12:
            names = names[:6] + ["…"] + names[-5:]
        lines.append(f"- Primary Flow: {' → '.join(names)}")
    lines.append("")
    return "\n".join(lines)


def _alg_summary(idx, scripts) -> str:
    has_py = bool(scripts.get("py_nodes"))
    uses_revit = any(sig.lower().startswith("revit.") for sig in scripts.get("ds_functions", [])) or any(
        "revitapi" in h.lower() for h in scripts.get("py_hints", [])
    )
    lines = ["## A. High-Level Algorithmic Summary", ""]
    msg = ["Identifies the core computational flow from inputs to outputs."]
    if uses_revit:
        msg.append("Includes Revit API operations (collection, filtering, transactions).")
    if has_py:
        msg.append("Custom Python logic augments built-in Dynamo nodes.")
    lines.append(" ".join(msg))
    lines.append("")
    return "\n".join(lines)


def _core_breakdown(idx, flow) -> str:
    lines = ["## B. Core Algorithm Breakdown", ""]
    inputs = [nid for nid in idx["nodes"] if len(idx["rev"].get(nid, [])) == 0]
    outputs = [nid for nid in idx["nodes"] if len(idx["adj"].get(nid, [])) == 0]
    if inputs:
        lines.append("1. Data Input & Validation:")
        for nid in inputs:
            lines.append(f"   - {idx['nodes'][nid]['display_name']}")
        lines.append("")
    if flow.get("paths"):
        p = flow["paths"][0]
        pretty = " → ".join(idx["nodes"][nid]["display_name"] for nid in p)
        lines.append("2. Processing Steps:")
        lines.append(f"   1. {pretty}")
        lines.append("")
    if flow.get("branching"):
        lines.append("3. Decision Points:")
        for nid in flow["branching"]:
            lines.append(f"   - {idx['nodes'][nid]['display_name']}")
        lines.append("")
    if outputs:
        lines.append("4. Output Generation:")
        for nid in outputs:
            lines.append(f"   - {idx['nodes'][nid]['display_name']}")
        lines.append("")
    return "\n".join(lines)


def _data_flow_arch(idx, flow) -> str:
    lines = ["## D. Data Flow Architecture", ""]
    ins = [nid for nid in idx["nodes"] if len(idx["rev"].get(nid, [])) == 0]
    outs = [nid for nid in idx["nodes"] if len(idx["adj"].get(nid, [])) == 0]
    if ins:
        lines.append("**Input Parameters:**")
        for nid in ins:
            lines.append(f"- `{idx['nodes'][nid]['display_name']}`")
        lines.append("")
    if outs:
        lines.append("**Final Outputs:**")
        for nid in outs:
            lines.append(f"- `{idx['nodes'][nid]['display_name']}`")
        lines.append("")
    if flow.get("paths"):
        lines.append("**Processing Order:**")
        p = flow["paths"][0]
        pretty = " → ".join(idx["nodes"][nid]["display_name"] for nid in p)
        lines.append(f"1. {pretty}")
        lines.append("")
    return "\n".join(lines)


def _impl_notes(scripts) -> str:
    lines = ["## E. Implementation Notes for C# Developer", ""]
    if scripts.get("py_hints"):
        lines.append("- Use Autodesk.Revit.DB with proper transactions for write ops.")
        lines.append("- Prefer FilteredElementCollector with category/class filters for performance.")
        lines.append("- Validate element/document context when accessing ActiveView/Document.")
    else:
        lines.append("- Implement pure data transforms with LINQ/immutable collections where possible.")
    lines.append("- Guard against null elements and empty lists; check view/document scope.")
    lines.append("- Handle unit conversions and list nesting typical in Dynamo graphs.")
    if any("Set" in h or "Create" in h for h in scripts.get("py_hints", [])):
        lines.append("- This graph likely modifies the model (transactions required).")
    lines.append("")
    return "\n".join(lines)


def _definition_summary(idx, scripts) -> str:
    nodes = idx["nodes"]
    adj = idx["adj"]
    py_count = len(scripts.get("py_nodes", []))
    cb_count = len(scripts.get("cb_nodes", []))
    funcs = len(scripts.get("ds_functions", []))
    lines = ["## Definition Summary"]
    lines.append(f"- Nodes: {len(nodes)}")
    lines.append(f"- Connections: {sum(len(v) for v in adj.values())}")
    lines.append(f"- Python Scripts: {py_count}")
    lines.append(f"- Code Blocks: {cb_count}")
    lines.append(f"- DSFunctions: {funcs}")
    lines.append("")
    return "\n".join(lines)


def analyze(dyn_path: str) -> str:
    data = load_dyn(dyn_path)
    idx = build_indexes(data)
    scripts = extract_scripts(data)
    flow = analyze_flow(dyn_path)

    out: List[str] = []
    out.append("# Dynamo Unified Analysis")
    out.append("")
    out.append(f"**{format_file_title(dyn_path)}**")
    out.append("")
    out.append(_exec_summary(idx, scripts))
    out.append(_workflow_summary(idx, flow))

    # Libraries & Dependencies
    if scripts.get("packages") or scripts.get("dependencies"):
        out.append("## Libraries and Dependencies")
        for name, ver in scripts.get("packages", []):
            suffix = f" {ver}" if ver else ""
            out.append(f"- {name}{suffix}")
        for d in scripts.get("dependencies", []):
            out.append(f"- {d}")
        out.append("")

    # Custom Script Analysis (reuse extractor rendering for brevity)
    out.append(render_script_report(scripts, dyn_path))
    out.append("")

    # Algorithmic A–E
    out.append("# Dynamo Algorithmic Analysis for C#")
    out.append("")
    out.append(_alg_summary(idx, scripts))
    out.append(_core_breakdown(idx, flow))
    out.append("## C. Key Computational Components\n")
    # leverage counts/names; detailed code already present above
    for s in scripts.get("py_nodes", []):
        out.append(f"- Python: {s['name']}")
    for s in scripts.get("cb_nodes", []):
        out.append(f"- DesignScript: {s['name']}")
    out.append("")
    out.append(_data_flow_arch(idx, flow))
    out.append(_impl_notes(scripts))

    # Summary
    out.append(_definition_summary(idx, scripts))
    return "\n".join(out)


def save_report(dyn_path: str, text: str) -> str:
    base = os.path.splitext(dyn_path)[0]
    out_path = f"{base}-dynamo-report.md"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(text)
    return out_path


def main(argv: List[str]) -> int:
    if len(argv) < 2:
        print("Usage: python dynamo-analyzer.py <path>.dyn")
        return 2
    path = argv[1]
    try:
        text = analyze(path)
        out_path = save_report(path, text)
        print(f"Saved: {out_path}")
        return 0
    except Exception as e:
        print(f"Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
