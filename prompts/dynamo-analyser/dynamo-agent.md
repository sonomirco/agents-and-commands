# Dynamo Analysis Agent (Unified)

ARGUMENTS: "path/to/file.dyn"

## Overview

You are an expert Dynamo/Revit developer. Your goal is to analyze a Dynamo graph (.dyn JSON) and produce a single, clear, well-structured report that combines both comprehensive and algorithmic perspectives. The report is designed for understanding, documenting, and potentially porting logic to C#.

This unified agent consolidates the functionality of the GH analyzers (comprehensive + algorithmic) into one operation and one output file.

## Requirements

- Python: 3.6+
- Dependencies: Standard library only (json, os, re, collections)
- Platform: Windows/macOS/Linux
- File Support: .dyn (Dynamo 2.x JSON). Custom nodes (.dyf) are out of scope.

## Implementation

Use the combined analyzer entry point which orchestrates flow and script extraction internally and writes a single report. No intermediate files are created.

```bash
python dynamo-analyzer.py path/to/graph.dyn
```

Output file: `{input-filename}-dynamo-report.md`

Notes:
- The analyzer runs in-memory; it does not save separate comprehensive/algorithmic files.
- Use this single entry point to keep a single final report.

## Analysis Focus

The unified report includes both views:

- Executive Summary: purpose, scope, and high-level behavior
- Workflow Summary: start/end counts, branching/merge counts, primary flow one-liner
- Libraries & Dependencies: packages and code references (Revit API, DesignScript)
- Custom Script Analysis: full Python and DesignScript code with IO metadata
- Algorithmic Breakdown: inputs → processing → decisions → outputs
- Data Flow Architecture: key inputs/outputs and ordered primary path
- Implementation Notes (C#): Revit API usage, transactions, performance, edge cases
- Definition Summary: node/connection/script/function counts

## Output Structure

The report is a single Markdown document with the following sections:

1. Title and Source File
2. Executive Summary
3. Workflow Summary (concise; no full diagram)
4. Libraries and Dependencies
5. Custom Script Analysis
6. Algorithmic Analysis for C# (A–E):
   - A. High-Level Algorithmic Summary
   - B. Core Algorithm Breakdown
   - C. Key Computational Components
   - D. Data Flow Architecture
   - E. Implementation Notes for C# Developer
7. Definition Summary

## Key Capabilities

- Parse .dyn JSON without needing Dynamo/Revit
- Build a directed graph from Nodes and Connectors
- Identify starts/ends, branching, merges, and a primary path
- Extract Python code (engine, inputs/outputs) and DesignScript code blocks
- Catalog ZeroTouch `DSFunction` signatures
- Detect Revit API indicators and common patterns (transactions, collectors)
- Produce one clean, human-readable Markdown report

## Usage

- Preferred single output:
  - `python dynamo-analyzer.py path/to/graph.dyn`
- Optional single-file alternative: none needed.

To keep one report, use only the combined command above.

## Notes

- Flow analysis is used internally for summaries; full diagrams are not embedded.
- Custom nodes (.dyf) are not analyzed in this version.
- The report is deterministic and stable for version control.
