#!/usr/bin/env python3
"""
Unified Grasshopper (.ghx/.xml) analyzer producing a single structured report:
- Executive Summary
- Workflow Summary (concise; no full diagram)
- Libraries & Dependencies
- Custom Script Analysis
- Algorithmic Analysis for C# (A–E)
- Definition Summary

Saves to: <input>-grasshopper-report.md
"""

import os
import sys
import re
import importlib.util
from typing import List, Dict

here = os.path.dirname(__file__)


def _load_module_from(py_path: str, module_name: str):
    spec = importlib.util.spec_from_file_location(module_name, py_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load module from {py_path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore[attr-defined]
    return mod


# Load Grasshopper sub-agents (hyphenated filenames)
_fd_mod = _load_module_from(os.path.join(here, 'flow-diagram-generator.py'), 'gh_flow_diagram_generator')
_se_mod = _load_module_from(os.path.join(here, 'script-extractor.py'), 'gh_script_extractor')

FlowDiagramGenerator = getattr(_fd_mod, 'FlowDiagramGenerator')
ScriptExtractor = getattr(_se_mod, 'ScriptExtractor')


def _exec_summary(flow: FlowDiagramGenerator, extractor: ScriptExtractor) -> str:
    doc_panels = flow._find_documentation_panels()
    scripts = extractor.scripts

    purpose_indicators = []
    if any("discover" in (t or "").lower() for t in doc_panels.values()):
        purpose_indicators.append("component discovery and analysis")
    if any("generate" in (t or "").lower() for t in doc_panels.values()):
        purpose_indicators.append("automated code generation")
    if any("file" in (t or "").lower() for t in doc_panels.values()):
        purpose_indicators.append("file operations")

    lines: List[str] = []
    lines.append("## Executive Summary")
    lines.append("")

    if purpose_indicators:
        lines.append(f"This Grasshopper definition focuses on {', '.join(purpose_indicators)}.")
    else:
        lines.append("This Grasshopper definition implements a custom computational workflow.")

    total_components = len(flow.components)
    script_count = len(scripts)
    if script_count > 0:
        lines.append(
            f"It contains {total_components} components, including {script_count} custom script components."
        )
    else:
        lines.append(f"It contains {total_components} components implementing the workflow.")

    return "\n".join(lines) + "\n\n"


def _workflow_summary(flow: FlowDiagramGenerator) -> str:
    starts = flow._find_start_nodes()
    ends = flow._find_end_nodes()
    branching = flow._identify_branching_points()
    merges = flow._identify_merge_points()
    paths = flow._identify_main_workflow_paths()

    lines: List[str] = ["## Workflow Summary"]
    lines.append(f"- Start Nodes: {len(starts)}")
    lines.append(f"- End Nodes: {len(ends)}")
    lines.append(f"- Branching Points: {len(branching)}")
    lines.append(f"- Merge Points: {len(merges)}")
    if paths:
        best = paths[0]
        try:
            names = [flow.components[gid]['display_name'] for gid in best]
        except Exception:
            names = best
        if len(names) > 12:
            names = names[:6] + ["..."] + names[-5:]
        lines.append(f"- Primary Flow: {' -> '.join(names)}")
    lines.append("")
    return "\n".join(lines) + "\n"


def _render_libraries(extractor: ScriptExtractor) -> str:
    if not extractor.libraries:
        return ""
    unique = set()
    for lib in extractor.libraries:
        if lib.get('name') and lib['name'].strip():
            unique.add(lib['name'].strip())
        elif lib.get('assembly_full_name'):
            unique.add(lib['assembly_full_name'].split(',')[0].strip())
    if not unique:
        return ""
    lines = ["## Libraries and Dependencies", ""]
    for name in sorted(unique):
        lines.append(f"- {name}")
    lines.append("")
    return "\n".join(lines)


def _render_key_components(flow: FlowDiagramGenerator) -> str:
    # Recognize common GH components and describe them
    known = {
        'sqgrid': 'Generate a square point grid',
        'crv cp': 'Closest point from geometry to curve',
        'closest point': 'Compute nearest point/curve relationship',
        'remap': 'Remap numbers from source to target domain',
        'bnd': 'Clamp values within a numeric domain',
        'bounds': 'Compute numeric bounds/domain',
        'range': 'Generate a sequence of numbers',
        'a-b': 'Subtract numbers element-wise',
        'a+b': 'Add numbers element-wise',
        'abs': 'Absolute value (magnitude)',
        'larger': 'Compare values and pick larger',
        'rectangle': 'Create rectangles from size parameters',
        'move': 'Translate geometry by a vector',
        'x': 'Axis input/parameter for transform',
        'tweencrv': 'Tween curves between inputs',
        'pull': 'Pull geometry to curve/surface (project)',
        'dom': 'Construct or analyze numeric domain',
        'filter': 'Filter list elements by mask or condition',
        'partition': 'Partition lists into sublists',
        'path mapper': 'Re-map data tree paths',
        'boundary': 'Construct boundary from curves',
        'preview': 'Preview display control',
        'group': 'Group elements for organization',
        'area': 'Compute area of geometry',
        'bbox': 'Compute bounding box of geometry'
    }

    present = {}
    for comp in flow.components.values():
        name = (comp.get('display_name') or '').strip()
        lower = name.lower()
        for key, desc in known.items():
            if key in lower:
                present[name] = desc
                break

    if not present:
        return ""

    lines: List[str] = ["## Key Grasshopper Components", ""]
    for name in sorted(present.keys(), key=lambda s: s.lower()):
        lines.append(f"- {name}: {present[name]}")
    lines.append("")
    return "\n".join(lines)


def _name_counts(names: List[str]) -> List[str]:
    counts: Dict[str, int] = {}
    for n in names:
        key = n or ''
        counts[key] = counts.get(key, 0) + 1
    # present common controls compactly
    out = []
    for name, cnt in sorted(counts.items(), key=lambda kv: (-kv[1], kv[0])):
        if cnt > 1:
            out.append(f"{name} (x{cnt})")
        else:
            out.append(name)
    return out


def _fmt_param(param: Dict) -> str:
    name = param.get('nickname') or param.get('name') or ''
    desc = param.get('description') or ''
    access = param.get('access') or 'item'
    access_str = f" ({access})" if access and access != 'item' else ""
    optional_str = " [Optional]" if param.get('optional') else ""
    return f"- `{name}`: {desc}{access_str}{optional_str}"


def _render_custom_script_analysis(extractor: ScriptExtractor) -> str:
    scripts = extractor.scripts
    if not scripts:
        return ""
    lines: List[str] = ["## Custom Script Analysis", ""]
    # Group by language
    grouped: Dict[str, List[Dict]] = {}
    for s in scripts.values():
        grouped.setdefault(s.get('language') or 'Unknown', []).append(s)

    for lang in sorted(grouped.keys()):
        lines.append(f"### {lang} Scripts ({len(grouped[lang])})")
        lines.append("")
        for s in grouped[lang]:
            title = s.get('display_name') or (s.get('component_type') or 'Script')
            lines.append(f"#### {title}")
            lines.append(f"**GUID:** `{s.get('instance_guid','')}`")
            lines.append(f"**Language:** {s.get('language','Unknown')}")
            if s.get('description'):
                lines.append(f"**Description:** {s['description']}")

            ins = s.get('input_parameters') or []
            outs = s.get('output_parameters') or []
            if ins:
                lines.append("**Inputs:**")
                for p in ins:
                    lines.append(_fmt_param(p))
            else:
                lines.append("**Inputs:** None")
            if outs:
                lines.append("**Outputs:**")
                for p in outs:
                    name = p.get('nickname') or p.get('name') or ''
                    desc = p.get('description') or ''
                    lines.append(f"- `{name}`: {desc}")
            else:
                lines.append("**Outputs:** None")

            code = s.get('script_code') or ''
            lines.append("**Code:**")
            if code.strip():
                lang_tag = (s.get('language') or 'text').lower()
                lines.append("```" + lang_tag)
                lines.append(code)
                lines.append("```")
            else:
                lines.append("[Empty or not found]")
            lines.append("")
        lines.append("")

    return "\n".join(lines)


# Algorithmic A–E helpers (adapted from algorithmic analyzer)
def _alg_analyze_purpose(flow: FlowDiagramGenerator, extractor: ScriptExtractor) -> str:
    doc_panels = flow._find_documentation_panels()
    scripts = extractor.scripts

    indicators = []
    for text in doc_panels.values():
        t = (text or '').lower()
        if any(k in t for k in ['minimum', 'optimization', 'algorithm']):
            indicators.append("optimization algorithm")
        if any(k in t for k in ['generate', 'code', 'compile']):
            indicators.append("code generation system")
        if any(k in t for k in ['analyze', 'process', 'calculate']):
            indicators.append("computational analysis tool")

    for s in scripts.values():
        code = (s.get('script_code') or '').lower()
        if 'bbox' in code or 'bounding' in code:
            indicators.append("geometric bounding box calculation")
        if 'compile' in code or 'generate' in code:
            indicators.append("automated code generation")
        if 'optimization' in code or 'refine' in code:
            indicators.append("iterative optimization")

    if indicators:
        uniq = list(dict.fromkeys(indicators))
        if len(uniq) == 1:
            return f"This algorithm implements a {uniq[0]} with staged computational processing."
        return f"This algorithm combines multiple approaches including {', '.join(uniq[:-1])} and {uniq[-1]}."
    return "This algorithm processes inputs through multiple computational stages to produce outputs."


def _alg_core_breakdown(flow: FlowDiagramGenerator, extractor: ScriptExtractor) -> str:
    lines: List[str] = ["## B. Core Algorithm Breakdown", ""]
    inputs = flow._find_start_nodes()
    outputs = flow._find_end_nodes()
    if inputs:
        lines.append("1. Data Input & Validation:")
        for gid in inputs:
            name = flow.components.get(gid, {}).get('display_name', gid)
            lines.append(f"   - {name}")
        lines.append("")
    paths = flow._identify_main_workflow_paths()
    if paths:
        p = paths[0]
        pretty = " -> ".join(flow.components.get(g, {}).get('display_name', g) for g in p)
        lines.append("2. Processing Steps:")
        lines.append(f"   1. {pretty}")
        lines.append("")
    # Decision points from script code
    decisions = []
    for s in extractor.scripts.values():
        code = s.get('script_code') or ''
        for cond in re.findall(r'\bif\s+([^:]+):', code):
            c = cond.strip()
            if c and len(c) < 100:
                decisions.append(f"Conditional check: {c}")
        for loop in re.findall(r'\bfor\s+([^:]+):', code):
            l = loop.strip()
            if l and len(l) < 100:
                decisions.append(f"Iteration control: {l}")
    if decisions:
        lines.append("3. Decision Points:")
        for d in decisions:
            lines.append(f"   - {d}")
        lines.append("")
    if outputs:
        lines.append("4. Output Generation:")
        for gid in outputs:
            name = flow.components.get(gid, {}).get('display_name', gid)
            lines.append(f"   - {name}")
        lines.append("")
    return "\n".join(lines)


def _alg_key_components(extractor: ScriptExtractor) -> str:
    lines: List[str] = ["## C. Key Computational Components", ""]
    for s in extractor.scripts.values():
        name = s.get('display_name') or 'Script'
        code = s.get('script_code') or ''
        lname = s.get('language') or 'Unknown'
        lines.append(f"### {name} Component")
        # Purpose
        lname_lower = (name or '').lower()
        code_lower = code.lower()
        if 'axes' in lname_lower:
            purpose = "Generates coordinate system visualization"
        elif 'id' in lname_lower or 'guid' in lname_lower:
            purpose = "Extracts component identifiers"
        elif 'generation' in lname_lower or 'generate' in lname_lower:
            purpose = "Implements code generation algorithms"
        elif 'bbox' in lname_lower or 'bounding' in lname_lower:
            purpose = "Calculates bounding boxes/orientations"
        elif 'file' in lname_lower:
            purpose = "Handles file I/O"
        elif 'optimization' in code_lower or 'minimize' in code_lower:
            purpose = "Optimization to find best solutions"
        else:
            purpose = "Performs specialized computation"
        lines.append(f"**Purpose:** {purpose}")
        # Algorithm
        if 'for' in code and 'range' in code:
            algo = "Iterative processing with controlled loops"
        elif 'while' in code:
            algo = "Conditional iteration with dynamic termination"
        elif re.search(r'\bdef\s+\w+', code):
            func_count = len(re.findall(r'\bdef\s+\w+', code))
            algo = f"Modular implementation with {func_count} functions"
        elif 'class' in code:
            algo = "Object-oriented implementation"
        elif len(code.splitlines()) > 50:
            algo = "Complex multi-stage computation"
        else:
            algo = "Straightforward procedure"
        lines.append(f"**Algorithm:** {algo}")
        # Dependencies
        deps = []
        for imp in re.findall(r'\bimport\s+(\w+)', code):
            if imp not in ['sys', 'os', 'math', 'time']:
                deps.append(imp)
        if 'rhinoscriptsyntax' in code_lower:
            deps.append('Rhino geometry API')
        if 'Grasshopper' in code:
            deps.append('Grasshopper framework')
        if 'GhPython' in code:
            deps.append('GhPython environment')
        if deps:
            lines.append(f"**Dependencies:** {', '.join(sorted(set(deps)))}")
        # Output contribution
        outs = s.get('output_parameters') or []
        if not outs:
            contrib = "Intermediate processing"
        elif len(outs) == 1:
            nm = outs[0].get('nickname') or outs[0].get('name') or 'Output'
            contrib = f"Produces {nm}"
        else:
            names = [p.get('nickname') or p.get('name') or 'Output' for p in outs]
            contrib = f"Generates: {', '.join(names)}"
        lines.append(f"**Output:** {contrib}")
        lines.append("")
    return "\n".join(lines)


def _alg_data_flow(flow: FlowDiagramGenerator) -> str:
    lines: List[str] = ["## D. Data Flow Architecture", ""]
    ins = flow._find_start_nodes()
    outs = flow._find_end_nodes()
    if ins:
        in_names = [flow.components.get(gid, {}).get('display_name', gid) for gid in ins]
        lines.append("**Input Parameters:**")
        for n in _name_counts(in_names):
            lines.append(f"- `{n}`")
        lines.append("")
    if outs:
        out_names = [flow.components.get(gid, {}).get('display_name', gid) for gid in outs]
        lines.append("**Final Outputs:**")
        for n in _name_counts(out_names):
            lines.append(f"- `{n}`")
        lines.append("")
    paths = flow._identify_main_workflow_paths()
    if paths:
        p = paths[0]
        pretty = " -> ".join(flow.components.get(g, {}).get('display_name', g) for g in p)
        lines.append("**Processing Order:**")
        lines.append(f"1. {pretty}")
        lines.append("")
    return "\n".join(lines)


def _alg_impl_notes(extractor: ScriptExtractor) -> str:
    lines: List[str] = ["## E. Implementation Notes for C# Developer", ""]
    critical = []
    # Libraries
    for lib in extractor.libraries:
        name = lib.get('name')
        if name and name not in ['Grasshopper']:
            critical.append(f"{name} library for specialized functionality")
    # Rhino specifics
    for s in extractor.scripts.values():
        code = (s.get('script_code') or '')
        if 'rhinoscriptsyntax' in code:
            critical.append("RhinoCommon SDK for geometric operations")
        if 'Rhino.Geometry' in code:
            critical.append("Rhino.Geometry for geometric types")
    if critical:
        lines.append("**Critical Dependencies:**")
        for c in sorted(set(critical)):
            lines.append(f"- {c}")
        lines.append("")

    # Performance / Edge cases / Refactoring
    perf = set()
    edges = set()
    refac = set()
    for s in extractor.scripts.values():
        code = s.get('script_code') or ''
        if len(code.splitlines()) > 100:
            perf.add("Large scripts benefit from modular decomposition")
        if 'for' in code and 'range' in code:
            perf.add("Consider parallelization for heavy loops")
        cl = code.lower()
        if 'bbox' in cl or 'optimization' in cl:
            perf.add("Geometric optimization is computationally intensive")
        if 'if not' in code or re.search(r'\bif\s+P\s*:', code):
            edges.add("Null or empty input validation")
        if 'try:' in code or 'except' in code:
            edges.add("Exception handling for robustness")
        if 'tolerance' in cl or 'precision' in cl:
            edges.add("Numeric precision/tolerance management")
        fn_count = len(re.findall(r'\bdef\s+\w+', code))
        if fn_count > 5:
            refac.add("Consider organizing functions into service classes")
        if 'global ' in code:
            refac.add("Avoid globals; use dependency injection patterns")

    if perf:
        lines.append("**Performance Considerations:**")
        for p in sorted(perf):
            lines.append(f"- {p}")
        lines.append("")
    if edges:
        lines.append("**Edge Cases:**")
        for e in sorted(edges):
            lines.append(f"- {e}")
        lines.append("")
    if refac:
        lines.append("**Refactoring Opportunities:**")
        for r in sorted(refac):
            lines.append(f"- {r}")
        lines.append("")
    return "\n".join(lines)


def analyze(xml_path: str) -> str:
    flow = FlowDiagramGenerator(xml_path)
    flow.analyze_xml()  # proceed even if no components
    extractor = ScriptExtractor(xml_path)
    extractor.analyze_xml()  # proceed even if no scripts

    lines: List[str] = []
    lines.append("# Grasshopper Unified Analysis")
    lines.append("")
    lines.append(f"**File:** {os.path.basename(xml_path)}")
    lines.append("")
    lines.append(_exec_summary(flow, extractor))
    lines.append(_workflow_summary(flow))
    lib_section = _render_libraries(extractor)
    if lib_section:
        lines.append(lib_section)
    key_comp = _render_key_components(flow)
    if key_comp:
        lines.append(key_comp)
    cs_section = _render_custom_script_analysis(extractor)
    if cs_section:
        lines.append(cs_section)

    # Algorithmic A–E
    lines.append("# Algorithmic Analysis for C#")
    lines.append("")
    lines.append("## A. High-Level Algorithmic Summary\n")
    lines.append(_alg_analyze_purpose(flow, extractor) + "\n")
    # Optional narrative based on detected components
    narrative = _alg_narrative(flow)
    if narrative:
        lines.append("### Algorithmic Narrative")
        lines.append("")
        lines.append(narrative)
        lines.append("")
    lines.append(_alg_core_breakdown(flow, extractor))
    lines.append("")
    lines.append(_alg_key_components(extractor))
    lines.append("")
    lines.append(_alg_data_flow(flow))
    lines.append("")
    lines.append(_alg_impl_notes(extractor))
    lines.append("")

    # Definition Summary
    paths = flow._identify_main_workflow_paths()
    doc_panels = flow._find_documentation_panels()
    lines.append("## Definition Summary")
    lines.append("")
    lines.append(f"- **Total Components:** {len(flow.components)}")
    lines.append(f"- **Script Components:** {len(extractor.scripts)}")
    lines.append(f"- **Libraries Used:** {len(extractor.libraries)}")
    lines.append(f"- **Workflow Paths:** {len(paths)}")
    lines.append(f"- **Documentation Panels:** {len(doc_panels)}")
    lines.append("")

    return "\n".join(lines)


def _alg_narrative(flow: FlowDiagramGenerator) -> str:
    # Heuristic narrative based on component display names
    names = [c.get('display_name', '') for c in flow.components.values()]
    lower = [n.lower() for n in names]

    steps: List[str] = []
    if any('sqgrid' in n for n in lower):
        steps.append("Generate a square grid of points (SqGrid) controlled by sliders.")
    if any('crv cp' in n or 'closest' in n for n in lower) or any('pull' in n for n in lower):
        steps.append("Compute distances or closest points from grid to attractor curves (Crv CP/Pull).")
    if any('remap' in n for n in lower) or any('bnd' in n or 'bound' in n for n in lower):
        steps.append("Remap distances to a target domain and clamp values (ReMap/Bounds).")
    if any(n in lower for n in ['a-b', 'a+b']) or any('abs' in n for n in lower):
        steps.append("Derive per-point scalar values via arithmetic and absolute operations.")
    if any('rectangle' in n for n in lower):
        steps.append("Create rectangles sized by the mapped scalar values.")
    if any('move' in n for n in lower):
        steps.append("Transform geometry by translating along axes (Move).")
    if any('tweencrv' in n for n in lower):
        steps.append("Generate tween curves between inputs to produce smooth transitions (TweenCrv).")
    if any('filter' in n for n in lower) or any('larger' in n for n in lower):
        steps.append("Filter elements using thresholds or comparisons (Larger/Filter).")
    if any('group' in n for n in lower):
        steps.append("Group outputs for organization and downstream use (Group/Preview).")

    if not steps:
        return ""
    return "\n".join(f"- {s}" for s in steps)


def save_report(xml_path: str, text: str) -> str:
    base = os.path.splitext(xml_path)[0]
    out_path = f"{base}-grasshopper-report.md"
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(text)
    return out_path


def main(argv: List[str]) -> int:
    if len(argv) != 2:
        print("Usage: python gh-unified-analyzer.py <grasshopper_file.ghx>")
        return 2

    xml_file_path = argv[1]
    if not os.path.exists(xml_file_path):
        print(f"Error: File not found: {xml_file_path}")
        return 1

    lower = xml_file_path.lower()
    if lower.endswith('.gh'):
        print("Error: Binary .gh files are not supported. Save as .ghx and retry.")
        return 1
    if not (lower.endswith('.xml') or lower.endswith('.ghx')):
        print(f"Warning: Unexpected extension for {xml_file_path}. Proceeding anyway...")

    try:
        text = analyze(xml_file_path)
        out_path = save_report(xml_file_path, text)
        print(f"Saved: {out_path}")
        return 0
    except Exception as e:
        print(f"Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
