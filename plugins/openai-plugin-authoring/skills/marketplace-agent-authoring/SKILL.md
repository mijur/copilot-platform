---
name: marketplace-agent-authoring
description: Decide whether a marketplace workflow needs a host-native specialist agent, and author it only in the harnesses that package agents. Use when a user requests an agent or subagent for a cross-harness plugin.
---

Agents are host-native. Use this after general plugin creation; never copy an agent file or its `tools` array between hosts.

## Host layout and capability names

- **Claude Code:** add `agents/<agent-name>.agent.md` beneath `plugins/claude-<plugin>/`. Use Claude names such as `tools: ["Read", "Grep", "Glob"]` for a read-only reviewer. Add only the capabilities the agent needs.
- **GitHub Copilot:** add `agents/<agent-name>.agent.md` beneath `plugins/<plugin>/`, with the root manifest's `agents: "agents/"` entry. Use documented Copilot primary aliases: `read`, `search`, `edit`, `execute`, and `agent`. For a read-only reviewer use `tools: ["read", "search"]`. Copilot aliases are case-insensitive, but do not use Claude spellings or product-internal names such as `view`.
- **OpenAI Codex:** the native package in this marketplace does not define packaged agents. Use a skill, connector, MCP server, hook, or other supported Codex component instead; do not add an agent compatibility shim.

## Author the agent

1. Give the agent a lowercase kebab-case `name` and an activation-focused `description` in YAML frontmatter.
2. Bound its authority with the smallest valid host-native `tools` array. A read-only task must not receive editing or shell capability.
3. Put the full role, scope, inputs, output format, refusal cases, and validation requirements in the Markdown body.
4. Keep the agent and all referenced assets in its host-native package. Do not delegate to an unavailable host component.

## Validate

Validate the package, then invoke the agent in its target host and confirm its declared capabilities—not a copied capability vocabulary—are recognized.