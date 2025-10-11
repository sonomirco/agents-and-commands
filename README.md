# Agents, commands & prompts

A curated repository of agent commands and prompt templates, specifically for the AEC (Architecture, Engineering, Construction). While it naturally includes general-purpose coding for day-to-day development, the primary goal is to provide construction-focused agents, commands, and prompts that address domain-specific tasks (e.g., BIM/parametric workflows, Dynamo/Grasshopper analysis, technical documentation, and AEC research).

## Overview

This repository provides ready-to-use building blocks for effective, agent-driven development:

- 14 specialized agents — architecture, languages, testing, documentation, research, AEC
- 2 command workflows — reusable, multi-step commands for common tasks
- 6 prompt templates — task-focused prompts to steer assistants
- AEC analysis utilities — Dynamo/Grasshopper analysis scripts for extracting structure and flows

## Repository structure

```
agents/                      # Specialized agent definitions (Claude Code/Codex)
commands/                    # Simple workflow/command orchestrators
prompts/                     # Task-specific prompt templates
├── dynamo-analyser/         # Dynamo (.dyn) analysis utilities and prompts
└── grasshopper-analyser/    # Grasshopper (.gh/.ghx) analysis utilities and prompts
README.md
LICENSE
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

### Documentation & visualization

- [mermaid-expert](agents/mermaid-expert.md) (sonnet) — Diagrams for systems and flows
- [prompt-engineer](agents/prompt-engineer.md) (opus) — Design and refine system prompts

### Research & analysis

- [codebase-researcher](agents/codebase-researcher.md) (opus) — Study and summarize codebases
- [document-parser-searcher](agents/document-parser-searcher.md) (haiku) — Parse and search large document sets

### AEC domain

- [aec-research-consultant](agents/aec-research-consultant.md) (opus) — Industry research and analysis
- [grasshopper-analyzer](agents/grasshopper-analyzer.md) (sonnet) — Analyze Grasshopper files and extract C# nodes

## Model configuration

Agents specify a target Claude model when appropriate:

- haiku: 1
- sonnet: 6
- opus: 7

Use lighter models for quick, deterministic tasks; sonnet for day-to-day engineering; opus for complex reasoning, architecture, and rigorous analysis.

## Contributing

To add new agents, commands, or prompts:

1. Use lowercase, hyphen-separated file names
2. Place files in the appropriate directory (`agents/`, `commands/`, `prompts/`)
3. Keep content concise, actionable, and production-focused
4. For agents, include frontmatter with at least `name`, `description`, and optionally `model`

### Agent file template
For more instrunctions check the [Claude Code documentation](https://docs.claude.com/en/docs/claude-code/sub-agents)

## License

Apache License 2.0 — see `LICENSE` for details.

## Resources

- Claude Code documentation: https://docs.anthropic.com/en/docs/claude-code
- Subagents: https://docs.anthropic.com/en/docs/claude-code/sub-agents
- Claude Code on GitHub: https://github.com/anthropics/claude-code
- Awesome Claude Code: https://github.com/hesreallyhim/awesome-claude-code
- Claude Code Templates: https://www.aitmpl.com
- Awesome Codex: https://github.com/KarelDO/awesome-codex
