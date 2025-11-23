# Agents, commands & prompts

A curated repository of agent commands and prompt templates, specifically for the AEC (Architecture, Engineering, Construction). While it naturally includes general-purpose coding for day-to-day development, the primary goal is to provide construction-focused agents, commands, and prompts that address domain-specific tasks (e.g., BIM/parametric workflows, Dynamo/Grasshopper analysis, technical documentation, and AEC research).

## Overview

This repository provides ready-to-use building blocks for effective, agent-driven development:

- **17 specialized agents** across architecture, languages, testing, documentation, and AEC
- **2 workflow commands** for context generation and experimentation
- **4 prompt templates** for precision writing and accuracy
- **3 skills** for AEC analysis and markdown conversion

All organized into **10 focused plugins** for granular installation via Claude Code marketplace, or install skills via the manifest-driven scripts.

## Repository structure

```
.claude-plugin/
└── marketplace.json         # Plugin marketplace definition
plugins/                     # Plugin-based organization (10 plugins)
├── aec-analysis-toolkit/
│   ├── agents/
│   └── skills/
├── backend-architecture/
│   └── agents/
├── python-development/
│   └── agents/
├── dotnet-development/
│   └── agents/
├── quality-and-testing/
│   └── agents/
├── documentation-and-visualization/
│   └── agents/
├── research-and-analysis/
│   └── agents/
├── workflow-orchestration/
│   └── commands/
├── prompt-templates/
│   └── commands/
└── markdown-utilities/
    └── skills/
skills-registry.json        # Skill manifest (name → plugin path)
install-skills.sh            # Installation script (Unix/macOS/Linux)
install-skills.bat           # Installation script (Windows)
README.md
LICENSE
CLAUDE.md
```

## Installation

### Option 1: [Claude Code marketplace](https://docs.claude.com/en/docs/claude-code/plugin-marketplaces) (recommended)

Add this marketplace to Claude Code for granular plugin installation:

```bash
/plugin marketplace add sonomirco/agents-and-commands
```

This makes **10 focused plugins** available for installation without loading anything into context. Install only what you need:

```bash
# Install specific plugins
/plugin install aec-analysis-toolkit
/plugin install python-development
/plugin install backend-architecture

# Or install multiple at once
/plugin install aec-analysis-toolkit python-development quality-and-testing
```

**Benefits:**
- Install only the agents, commands, and skills you need
- Minimal token usage - plugins load only their specific resources
- Easy updates via `/plugin update`
- Browse available plugins with `/plugin list`

### Option 2: Quick install (skills only)

Install all skills with one command:

```bash
# Unix/macOS/Linux
./install-skills.sh

# Windows
install-skills.bat
```

Or install specific skills:

```bash
./install-skills.sh grasshopper-analyzer dynamo-analyzer
```

### Option 3: Manual installation

Inspect the manifest to view available skills and their plugin paths:

```bash
jq '.skills[] | {name, path}' skills-registry.json
```

Copy the desired skill directories (paths are manifest relative) to `~/.claude/skills/`:

```bash
cp -r plugins/aec-analysis-toolkit/skills/grasshopper-analyzer ~/.claude/skills/
cp -r plugins/aec-analysis-toolkit/skills/dynamo-analyzer ~/.claude/skills/
cp -r plugins/markdown-utilities/skills/markdown-to-xml ~/.claude/skills/
```

## Usage

### Agent invocation

Use agents explicitly in natural language within Claude Code or Codex. Examples:

```
"Use python-pro to optimize this async function."
"Have backend-architect design the service boundaries for this feature."
"Ask tdd-orchestrator to drive the red-green-refactor cycle for this change."
"Use mermaid-expert to diagram the system interactions."
```

### Commands

Command files in `commands/` outline repeatable workflows. Open a command file and follow the steps, or paste sections into your assistant to run the flow.

- `commands/generate-code-base-context.md` — Build a concise repository context for faster onboarding and reasoning
- `commands/experiment-development.md` — Guide exploratory spikes and small experiments with safety rails

### Prompts

Prompt templates in `prompts/` help set intent and constraints quickly. AEC-focused analyzers include utilities to parse Dynamo and Grasshopper files and generate diagrams or summaries.

- `prompts/clear-and-accurate.md` — Precision-first writing template
- `prompts/humanise-response.md` — Make responses warmer without losing accuracy
- `prompts/reduce-hallucination.md` — Improve reliability and source awareness
- `prompts/dynamo-analyser/` — Extract nodes/flows from Dynamo scripts; generate flow diagrams
- `prompts/grasshopper-analyser/` — Analyze .gh/.ghx graphs; extract C# nodes; diagram connections

### Skills

Claude Code skills live inside plugin directories. `skills-registry.json` is the canonical manifest used by the installation scripts; update it whenever skills are added, moved, or removed. Copy the manifest-listed directories to `~/.claude/skills/` (or run the install scripts) to make them globally available, then invoke by name in natural language or via the Skill tool.

**grasshopper-analyzer** — Analyze Grasshopper (.ghx/.xml) files
- Location: `plugins/aec-analysis-toolkit/skills/grasshopper-analyzer/` (see manifest)
- Input: Path to .ghx or .xml file (binary .gh not supported)
- Output: Comprehensive Markdown report with workflow topology, custom scripts, algorithmic analysis, and C# migration guidance
- Usage: `"Use grasshopper-analyzer to analyze this definition"`

**dynamo-analyzer** — Analyze Dynamo (.dyn) graphs
- Location: `plugins/aec-analysis-toolkit/skills/dynamo-analyzer/` (see manifest)
- Input: Path to .dyn file (Dynamo 2.x JSON)
- Output: Comprehensive Markdown report with workflow topology, Python/DesignScript code, Revit API patterns, and C# migration guidance
- Usage: `"Analyze this Dynamo graph with dynamo-analyzer"`

**markdown-to-xml** — Convert markdown articles to XML format
- Location: `plugins/markdown-utilities/skills/markdown-to-xml/` (see manifest)
- Input: Article name from Obsidian vault
- Output: XML-formatted article with preserved formatting (bold, blockquotes, headers)
- Usage: `"Convert this article to XML"`

### Plan validation workflow

Use `plan-validator` to validate and iteratively improve plans using Codex feedback loops:

- Claude drafts a plan → `plan-validator` crafts a Codex prompt and executes it
- Codex streams output to the CLI; Claude reads it, updates the plan, and repeats until satisfied
- Typical command (invoked by the agent): `codex --full-auto exec --sandbox workspace-write "[prompt]"`

Long-running validations can exceed 2 minutes. To prevent timeouts, set extended bash timeouts for Claude Code:

In `~/.claude/settings.json`:
```
"env": {
  "BASH_DEFAULT_TIMEOUT_MS": "1800000",  // 30 minutes
  "BASH_MAX_TIMEOUT_MS": "7200000"      // 2 hours
}
```

Or export environment variables before starting the session:
```
export BASH_DEFAULT_TIMEOUT_MS=800000   # ~13 minutes
export BASH_MAX_TIMEOUT_MS=7200000      # 2 hours
```

Alternative: Run Codex as an MCP server and call it from Claude Code. This shifts execution to the MCP tool runtime and mitigates CLI timeout constraints for long operations.

Example Codex prompt used by plan-validator:
```
Review and validate the following implementation plan for the <feature/topic> in this repository.

Context:
- Repo root: $WORKSPACE
- Relevant dirs: src/, server/, scripts/

Please analyze:
1) Missing steps or dependencies
2) Risks and edge cases
3) Conflicts with current code
4) Concrete improvements (be specific)

If helpful, read files to verify assumptions. Then return:
- A concise feedback summary
- A numbered list of fixes/improvements
- Any commands, file changes, or tests to add

Plan:
<paste the full plan here>
```

MCP setup (optional):
- You can expose [Codex as an MCP server](https://developers.openai.com/codex/mcp/#running-codex-as-an-mcp-server) and register it with Claude Code.
- Example config snippet (adjust to your environment):
```
{
  "mcpServers": {
    "codex": {
      "command": "codex",
      "args": ["mcp-server"],
      "env": {
        "BASH_DEFAULT_TIMEOUT_MS": "1800000",
        "BASH_MAX_TIMEOUT_MS": "7200000"
      }
    }
  }
}
```

## Available plugins

The 17 agents, 2 commands, 4 prompts, and 3 skills are organized into **10 focused plugins** optimized for granular installation:

| Plugin | Description | Agents | Commands | Skills |
|--------|-------------|--------|----------|--------|
| **aec-analysis-toolkit** | Dynamo/Grasshopper analysis with C# migration guidance | 2 | 0 | 2 |
| **backend-architecture** | API design, microservices, security patterns | 3 | 0 | 0 |
| **python-development** | Modern Python 3.12+, async, FastAPI/Django | 2 | 0 | 0 |
| **dotnet-development** | C#/.NET with testing and performance | 1 | 0 | 0 |
| **quality-and-testing** | TDD, plan validation, code quality review, Codex integration | 3 | 0 | 0 |
| **documentation-and-visualization** | Diagrams, prompts, technical writing | 2 | 0 | 0 |
| **research-and-analysis** | Codebase research, document parsing, pattern analysis, best practices | 4 | 0 | 0 |
| **workflow-orchestration** | Context generation, experimental development | 0 | 2 | 0 |
| **prompt-templates** | Precision writing, accuracy templates | 0 | 3 | 0 |
| **markdown-utilities** | Markdown to XML conversion | 0 | 0 | 1 |

## Agent categories

### Architecture & system design

- [backend-architect](agents/backend-architect.md) (opus) — Design RESTful APIs, service boundaries, schemas
- [backend-security-coder](agents/backend-security-coder.md) (opus) — Secure backend patterns and hardening
- [api-documenter](agents/api-documenter.md) (sonnet) — OpenAPI and developer docs

### Programming languages

- [python-pro](agents/python-pro.md) (sonnet) — Modern Python 3.12+, async, performance
- [python-developer](agents/python-developer.md) (sonnet) — Practical Python, Django/FastAPI
- [csharp-pro](agents/csharp-pro.md) (sonnet) — Modern C#/.NET with testing and performance

### Quality & testing

- [tdd-orchestrator](agents/tdd-orchestrator.md) (opus) — Red/green/refactor workflow leadership
- [plan-validator](agents/plan-validator.md) (opus) — Validates and iteratively upgrades plans via Codex feedback loops
- [code-simplicity-reviewer](agents/code-simplicity-reviewer.md) (sonnet) — Reviews code for simplicity, minimalism, and YAGNI principles

### Documentation & visualization

- [mermaid-expert](agents/mermaid-expert.md) (sonnet) — Diagrams for systems and flows
- [prompt-engineer](agents/prompt-engineer.md) (opus) — Design and refine system prompts

### Research & analysis

- [codebase-researcher](agents/codebase-researcher.md) (opus) — Study and summarize codebases
- [document-parser-searcher](agents/document-parser-searcher.md) (haiku) — Parse and search large document sets
- [pattern-recognition-specialist](agents/pattern-recognition-specialist.md) (sonnet) — Analyze code for design patterns, anti-patterns, and code quality
- [best-practices-researcher](agents/best-practices-researcher.md) (sonnet) — Research and synthesize external best practices, documentation, and industry standards

### AEC domain

- [aec-research-consultant](agents/aec-research-consultant.md) (opus) — Industry research and analysis
- [grasshopper-analyzer](agents/grasshopper-analyzer.md) (sonnet) — Analyze Grasshopper files and extract C# nodes

## Model configuration

Agents specify a target Claude model when appropriate:

- haiku: 1
- sonnet: 9
- opus: 7

Use lighter models for quick, deterministic tasks; sonnet for day-to-day engineering; opus for complex reasoning, architecture, and rigorous analysis.

## Contributing

To add new agents, commands, prompts, or skills:

1. **Keep everything generic**: All contributions must be generic and reusable. Carefully eliminate any specific references to:
   - Personal projects or proprietary codebases
   - Company names or internal tools
   - Specific file paths or directory structures
   - Personal workflows or Obsidian vaults
   - API endpoints or internal services

2. **File naming**: Use lowercase, hyphen-separated file names
3. **File placement**: Place in the appropriate plugin directory (e.g., `plugins/<plugin>/agents/`, `plugins/<plugin>/commands/`, `plugins/<plugin>/skills/`)
4. **Content quality**: Keep concise, actionable, and production-focused
5. **Frontmatter**: For agents, include at least `name`, `description`, and optionally `model`

### Generic examples

❌ Bad (specific): "Fetch data from the CompanyX API at https://internal.companyx.com/api"
✅ Good (generic): "Fetch data from the API endpoint"

❌ Bad (specific): "Read files from /Users/john/Documents/MyProject/"
✅ Good (generic): "Read files from the project directory"

❌ Bad (specific): "Connect to our MongoDB instance at prod-db-01"
✅ Good (generic): "Connect to the database"

### Templates

For agent templates, check the [Claude Code documentation](https://docs.claude.com/en/docs/claude-code/sub-agents)

For skill templates, check the [Claude Code skills documentation](https://docs.claude.com/en/docs/claude-code/agent-skills)

## Sharing and distribution

### Option 1: Claude Code marketplace (recommended)

This repository is configured as a **Claude Code plugin marketplace**. Users simply add the marketplace:

```bash
/plugin marketplace add yourusername/agents-and-commands
```

Then install specific plugins:

```bash
/plugin install aec-analysis-toolkit python-development
```

**Benefits for users:**
- Browse 10 focused plugins with `/plugin list`
- Install only what they need
- Minimal token usage (plugins load only their resources)
- Easy updates with `/plugin update`

### Option 2: Direct installation (skills only)

Users clone and run installation scripts:

```bash
git clone https://github.com/sonomirco/agents-and-commands.git
cd agents-and-commands
./install-skills.sh
```

### Option 3: Individual resources

Copy specific agents, commands, prompts, or skills:
- Copy `agents/agent-name.md` to `.claude/agents/`
- Copy manifest-listed skill directories (e.g., `plugins/aec-analysis-toolkit/skills/grasshopper-analyzer/`) to `~/.claude/skills/`
- Copy commands or prompts as needed

### Creating your own plugin marketplace

1. Fork this repository
2. Update `.claude-plugin/marketplace.json`:
   - Change owner name, email, URL
   - Update repository URLs (replace `sonomirco` with your GitHub username)
   - Customize plugin descriptions
3. Add/remove plugins to match your content
4. Ensure all paths in `marketplace.json` are correct
5. Push to GitHub
6. Share with: `/plugin marketplace add your-github-username/your-repo`

**Marketplace structure:**
```json
{
  "name": "your-marketplace-name",
  "owner": { "name": "...", "email": "...", "url": "..." },
  "metadata": { "description": "...", "version": "1.0.0" },
  "plugins": [
    {
      "name": "plugin-name",
      "description": "...",
      "agents": ["./plugins/sample-plugin/agents/agent.md"],
      "commands": ["./plugins/sample-plugin/commands/command.md"],
      "skills": ["./plugins/sample-plugin/skills/skill/SKILL.md"]
    }
  ]
}
```

## License

Apache License 2.0 — see `LICENSE` for details.

## Resources

### Official documentation
- Claude Code documentation: https://docs.anthropic.com/en/docs/claude-code
- Subagents: https://docs.anthropic.com/en/docs/claude-code/sub-agents
- Claude Code on GitHub: https://github.com/anthropics/claude-code

### Community resources
- Awesome Claude Code: https://github.com/hesreallyhim/awesome-claude-code
- Claude Code Templates: https://www.aitmpl.com
- Awesome Codex: https://github.com/KarelDO/awesome-codex

### External AECO LLM Collection
- **[External AECO LLM Technologies Collection](EXTERNAL_AECO_COLLECTION.md)** — Comprehensive reference to 60+ external MCP servers, prompt libraries, and Claude Code skills found across the AECO ecosystem. Includes tools for Revit, Rhino, Tekla, AutoCAD, GIS platforms, and structural analysis software.

### Skills marketplaces and cross-platform tools
- **Intellectronica Skills Marketplace** (http://skills.intellectronica.net/) — Community-curated collection of generic Claude Code skills across multiple domains. Browse for inspiration, reference implementations, or ready-to-use skills that complement the AEC-focused toolkit in this repository.
- **OpenSkills** (https://github.com/numman-ali/openskills) — Cross-platform adapter that makes Claude Code skills accessible to other AI models and frameworks. Use this to extend your skills beyond Claude Code and maintain portability across different development environments.
