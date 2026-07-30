---
name: marketplace-agent-authoring
description: Add or revise a host-native specialist agent in a Claude Code or GitHub Copilot marketplace package. Use when reusable autonomous behavior needs a dedicated prompt and explicitly bounded agent capabilities.
---

Agents are host-native. Use this after general plugin creation; never copy an agent file or its `tools` array between hosts.

## Host layout and capability names

- **Claude Code:** add `agents/<agent-name>.agent.md` beneath `plugins/claude-<plugin>/`. Use Claude names such as `tools: ["Read", "Grep", "Glob"]` for a read-only reviewer. Add only the capabilities the agent needs.
- **GitHub Copilot standalone package:** add `agents/<agent-name>.agent.md` beneath `plugins/<plugin>/`. Use documented Copilot primary aliases: `read`, `search`, `edit`, `execute`, and `agent`. For a read-only reviewer use `tools: ["read", "search"]`.- **GitHub Copilot reusable adapter:** add `agents/<agent-name>.agent.md` to the marketplace-level collection and list `"./agents/<agent-name>.agent.md"` explicitly in `plugins/<plugin>/.github/plugin/plugin.json`. Reuse that one agent from other adapters instead of copying it.
- **OpenAI Codex:** the native package in this marketplace does not define packaged agents. Use a skill, connector, MCP server, hook, or other supported Codex component instead; do not add an agent compatibility shim.

## Author the agent

1. Give the agent a lowercase kebab-case `name` and an activation-focused `description` in YAML frontmatter.
2. Bound its authority with the smallest valid host-native `tools` array. A read-only task must not receive editing or shell capability.
3. Put the full role, scope, inputs, output format, refusal cases, and validation requirements in the Markdown body.
4. Keep the agent and all referenced assets in its host-native package. Do not delegate to an unavailable host component.

## Validate

Validate the package, then invoke the agent in its target host and confirm its declared capabilities—not a copied capability vocabulary—are recognized.