#!/usr/bin/env python3
"""
Extract script/code information from Dynamo (.dyn) graphs:
- PythonScriptNode code and IO
- CodeBlockNode DesignScript code and IO
- Catalog DSFunction signatures
- Collect package/library hints

Outputs a Markdown report segment; other analyzers can import functions.
"""

import sys
import os
import re
from typing import Dict, Any, List, Tuple, Set

from dynamo_utils import load_dyn, build_indexes, format_file_title


PY_REFS = (
    r"clr\.AddReference\(['\"]RevitAPI['\"]\)",
    r"from\s+Autodesk\.Revit\.DB\s+import\s+",
    r"TransactionManager",
    r"FilteredElementCollector",
    r"SetParameter|SetLineStyle|Create\w+",
)


def _detect_py_hints(code: str) -> List[str]:
    hints = []
    for pat in PY_REFS:
        if re.search(pat, code):
            hints.append(pat)
    return hints


def extract_scripts(data: Dict[str, Any]) -> Dict[str, Any]:
    idx = build_indexes(data)
    nodes = idx["nodes"]

    py_nodes = []
    cb_nodes = []
    ds_funcs = []
    code_hints: Set[str] = set()

    for nid, n in nodes.items():
        ctype = (n.get("ConcreteType") or "").lower()
        if "python" in ctype:
            code = n.get("Code") or ""
            engine = n.get("EngineName") or n.get("Engine") or ""
            hints = _detect_py_hints(code)
            code_hints.update(hints)
            py_nodes.append({
                "id": nid,
                "name": n.get("display_name", "Python"),
                "engine": engine,
                "inputs": n.get("Inputs") or [],
                "outputs": n.get("Outputs") or [],
                "code": code,
            })
        elif "codeblock" in ctype:
            cb_nodes.append({
                "id": nid,
                "name": n.get("display_name", "CodeBlock"),
                "inputs": n.get("Inputs") or [],
                "outputs": n.get("Outputs") or [],
                "code": n.get("Code") or "",
            })
        elif "dsfunction" in ctype:
            sig = n.get("FunctionSignature") or n.get("display_name")
            if sig:
                ds_funcs.append(sig)

    packages = idx.get("packages") or []
    deps = idx.get("dependencies") or []

    return {
        "py_nodes": py_nodes,
        "cb_nodes": cb_nodes,
        "ds_functions": sorted(set(ds_funcs)),
        "packages": packages,
        "dependencies": deps,
        "py_hints": sorted(code_hints),
        "idx": idx,
    }


def render_script_report(extracted: Dict[str, Any], dyn_path: str) -> str:
    lines: List[str] = []
    lines.append("# Script and Code Analysis")
    lines.append("")
    lines.append(f"**{format_file_title(dyn_path)}**")
    lines.append("")

    # Packages & Dependencies
    if extracted["packages"] or extracted["dependencies"]:
        lines.append("## Libraries and Dependencies")
        if extracted["packages"]:
            lines.append("- Packages:")
            for name, ver in extracted["packages"]:
                suffix = f" {ver}" if ver else ""
                lines.append(f"  - {name}{suffix}")
        if extracted["dependencies"]:
            lines.append("- Dependencies:")
            for d in extracted["dependencies"]:
                lines.append(f"  - {d}")
        lines.append("")

    # Python scripts
    if extracted["py_nodes"]:
        lines.append("## Python Script Nodes")
        for s in extracted["py_nodes"]:
            lines.append(f"### {s['name']} ({s['id']})")
            if s.get("engine"):
                lines.append(f"- Engine: {s['engine']}")
            if s.get("inputs"):
                lines.append("- Inputs:")
                for p in s["inputs"]:
                    lines.append(f"  - {p.get('Name','')} — {p.get('Description','')}")
            if s.get("outputs"):
                lines.append("- Outputs:")
                for p in s["outputs"]:
                    lines.append(f"  - {p.get('Name','')} — {p.get('Description','')}")
            lines.append("")
            lines.append("```python")
            lines.append(s["code"])
            lines.append("```")
            lines.append("")

    # Code blocks
    if extracted["cb_nodes"]:
        lines.append("## DesignScript Code Blocks")
        for s in extracted["cb_nodes"]:
            lines.append(f"### {s['name']} ({s['id']})")
            if s.get("inputs"):
                lines.append("- Inputs:")
                for p in s["inputs"]:
                    lines.append(f"  - {p.get('Name','')} — {p.get('Description','')}")
            if s.get("outputs"):
                lines.append("- Outputs:")
                for p in s["outputs"]:
                    lines.append(f"  - {p.get('Name','')} — {p.get('Description','')}")
            lines.append("")
            lines.append("```python")  # DesignScript; markdown highlighters vary
            lines.append(s["code"])
            lines.append("```")
            lines.append("")

    # DSFunction catalog
    if extracted["ds_functions"]:
        lines.append("## DSFunction Catalog")
        for sig in extracted["ds_functions"]:
            lines.append(f"- {sig}")
        lines.append("")

    # Python hints
    if extracted["py_hints"]:
        lines.append("## Python Revit API Indicators")
        for h in extracted["py_hints"]:
            lines.append(f"- Pattern: `{h}`")
        lines.append("")

    return "\n".join(lines)


def main(argv: List[str]) -> int:
    if len(argv) < 2:
        print("Usage: python dynamo_script_extractor.py <path>.dyn")
        return 2
    path = argv[1]
    try:
        data = load_dyn(path)
        ext = extract_scripts(data)
        print(render_script_report(ext, path))
        return 0
    except Exception as e:
        print(f"Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))

