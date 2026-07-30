---
name: marketplace-skill-authoring
description: Add or revise a focused skill in a native Claude Code, OpenAI Codex, or GitHub Copilot marketplace package. Use when a plugin needs reusable instructions rather than an agent, hook, or model-callable tool.
---

Use this after `marketplace-plugin-authoring` has created or identified the target package. A skill is reusable instruction content; it is not an agent profile or a tool implementation.

## Select the native package

- Claude Code: `plugins/claude-<plugin>/skills/<skill>/SKILL.md`.
- OpenAI Codex: `plugins/openai-<plugin>/skills/<skill>/SKILL.md`; the manifest exposes `skills: "./skills/"`.
- GitHub Copilot standalone package: `plugins/<plugin>/skills/<skill>/SKILL.md`; a root manifest may expose `skills: "skills/"`.
- GitHub Copilot reusable adapter: `skills/<skill>/SKILL.md` at the marketplace root, declared explicitly as `"./skills/<skill>/"` in `plugins/<plugin>/.github/plugin/plugin.json`.

Reuse a marketplace-level GitHub skill from any number of adapter manifests instead of copying it. Keep Claude and OpenAI skill copies inside their installed packages.

## Author the skill

1. Choose a lowercase kebab-case name and a precise activation description that names the user intent and excludes nearby concepts.
2. Start `SKILL.md` with only non-empty `name` and `description` YAML frontmatter.
3. State required inputs, deterministic steps, outputs, and host-specific validation. Keep instructions imperative and task-focused.
4. Put references, examples, and helper assets beneath that skill directory. A helper script remains supporting material unless the host registers it as a tool or MCP server.
5. Do not use an agent `tools` array, hook schema, or MCP configuration in `SKILL.md`.

## Validate

Run the marketplace validator for the selected host. Exercise the skill from the installed target host when its trigger or workflow changes.