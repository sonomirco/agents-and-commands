# CLAUDE.md

## Repository Overview

This is a Claude Code plugin marketplace repository focused on AEC (Architecture, Engineering, Construction) domain expertise. It contains 17 specialized agents, 2 workflow commands, 4 prompt templates, and 3 skills, all organized into **10 focused plugins** for granular installation. Covers backend architecture, Python development, testing, documentation, and AEC-specific tooling including Dynamo and Grasshopper analysis utilities.

**Installation**: Add via `/plugin marketplace add sonomirco/agents-and-commands` and install specific plugins as needed for minimal token usage.

## Repository Structure

```
.claude-plugin/
└── marketplace.json         # Plugin marketplace definition (10 plugins)

plugins/                     # Plugin-based organization (10 plugins)
├── aec-analysis-toolkit/
│   ├── agents/
│   │   ├── grasshopper-analyzer.md
│   │   └── aec-research-consultant.md
│   └── skills/
│       ├── grasshopper-analyzer/
│       └── dynamo-analyzer/
├── backend-architecture/
│   └── agents/
│       ├── backend-architect.md
│       ├── backend-security-coder.md
│       └── api-documenter.md
├── python-development/
│   └── agents/
│       ├── python-pro.md
│       └── python-developer.md
├── dotnet-development/
│   └── agents/
│       └── csharp-pro.md
├── quality-and-testing/
│   └── agents/
│       ├── tdd-orchestrator.md
│       ├── plan-validator.md
│       └── code-simplicity-reviewer.md
├── documentation-and-visualization/
│   └── agents/
│       ├── mermaid-expert.md
│       └── prompt-engineer.md
├── research-and-analysis/
│   └── agents/
│       ├── codebase-researcher.md
│       ├── document-parser-searcher.md
│       ├── pattern-recognition-specialist.md
│       └── best-practices-researcher.md
├── workflow-orchestration/
│   └── commands/
│       ├── generate-code-base-context.md
│       └── experiment-development.md
├── prompt-templates/
│   └── commands/
│       ├── clear-and-accurate.md
│       ├── humanise-response.md
│       └── reduce-hallucination.md
└── markdown-utilities/
    └── skills/
        └── markdown-to-xml/

skills-registry.json        # Manifest of skill names and plugin-relative paths
prompts/                     # Python analysis utilities (source)
├── dynamo-analyser/
│   ├── dynamo-analyzer.py
│   ├── dynamo-flow-diagram-generator.py
│   ├── dynamo-script-extractor.py
│   └── dynamo-utils.py
└── grasshopper-analyser/
    ├── gh-unified-analyzer.py
    ├── flow-diagram-generator.py
    └── script-extractor.py

install-skills.sh            # Installation script (Unix/macOS/Linux)
install-skills.bat           # Installation script (Windows)
```

## Maintenance Guidelines

- **CLAUDE.md**: Always update when structural changes occur (new directories, skills, agents, commands)
- **README.md**: Always update when adding/removing agents, commands, prompts, or skills. Use sentence case, not Title Case
- **Installation scripts**: Update `install-skills.sh` and `install-skills.bat` when adding new skills
- Keep all files in sync with repository structure
