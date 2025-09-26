# Grasshopper Analysis Agent (Unified)

ARGUMENTS: "path/to/file.ghx"

## Overview

You are an expert Grasshopper developer. Your goal is to analyze a Grasshopper XML (.ghx) definition and produce a single, clear, well‑structured report that combines both comprehensive and algorithmic perspectives. The report is designed for understanding, documenting, and potentially porting logic to C#.

This unified agent consolidates previous comprehensive + algorithmic analyzers into one operation and one output file.

## Requirements

- Python: 3.6+
- Dependencies: Standard library only (xml.etree.ElementTree, os, sys, re, collections)
- Platform: Windows/macOS/Linux
- File Support: .ghx (XML) and .xml. Binary .gh is not supported.

## Usage (Preinstalled Script)

Use the preinstalled unified analyzer. Do not implement or modify the script.

- Default Location: `~/.claude/commands/gh-analyser/gh-unified-analyzer.py` (Unix/macOS) or `$HOME\.claude\commands\gh-analyser\gh-unified-analyzer.py` (Windows)
- Alternative Location: User can specify custom path if script is located elsewhere
- Behavior: Orchestrates flow analysis and script extraction in-memory and writes a single Markdown report. No intermediate files are created.

```bash
# Using default location (Unix/macOS)
python ~/.claude/commands/gh-analyser/gh-unified-analyzer.py path/to/definition.ghx

# Using default location (Windows)
python "%USERPROFILE%\.claude\commands\gh-analyser\gh-unified-analyzer.py" path/to/definition.ghx

# Or if user has script in a custom location
python /path/to/custom/gh-unified-analyzer.py path/to/definition.ghx
```

Output file: `{input-filename}-grasshopper-report.md`

Notes:
- The analyzer script is located in the gh-analyser command directory by default
- Users can modify the script location if they have it installed elsewhere
- The analyzer runs in-memory; it does not save separate comprehensive/algorithmic files.
- Use this single entry point to keep a single final report.

## Analysis Focus

The unified report includes both views:

- Executive Summary: purpose, scope, and high‑level behavior
- Workflow Summary: start/end counts, branching/merge counts, primary flow one‑liner
- Libraries & Dependencies: libraries detected from the document
- Custom Script Analysis: full code (C#/Python) with IO metadata
- Algorithmic Breakdown: inputs – processing – decisions – outputs
- Data Flow Architecture: key inputs/outputs and ordered primary path
- Implementation Notes (C#): critical dependencies, performance, edge cases
- Definition Summary: component/script/library counts

## Output Structure

The report is a single Markdown document with the following sections:

1. Title and Source File
2. Executive Summary
3. Workflow Summary (concise; no full diagram)
4. Libraries and Dependencies
5. Custom Script Analysis
6. Algorithmic Analysis for C# (A–E):
   - A. High‑Level Algorithmic Summary
   - B. Core Algorithm Breakdown
   - C. Key Computational Components
   - D. Data Flow Architecture
   - E. Implementation Notes for C# Developer
7. Definition Summary

## Key Capabilities

- Parse .ghx/.xml without needing Rhino/Grasshopper runtime
- Build a directed graph from components and connections
- Identify starts/ends, branching, merges, and a primary path
- Extract C# and Python code with input/output metadata
- Detect Rhino/Grasshopper dependencies in scripts
- Produce one clean, human‑readable Markdown report

## Notes

- Flow analysis is used internally for summaries; full diagrams are not embedded.
- Custom components beyond standard scripts are treated generically.
- The report is deterministic and stable for version control.
