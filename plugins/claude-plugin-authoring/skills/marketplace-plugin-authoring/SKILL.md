---
name: marketplace-plugin-authoring
description: Create, extend, or validate native plugins in an initialized Claude Code, OpenAI Codex, or GitHub Copilot marketplace. Use when a marketplace already has the target host catalogs.
---

Use the bundled scripts against the user's explicit target marketplace. Never assume that the current repository is the target.

## Route the request

Determine the target hosts, then inspect the explicit target directory before asking for plugin metadata:

1. If every requested catalog exists, author or modify the plugin in that initialized marketplace.
2. If any requested catalog is absent, use the `marketplace-initialization` workflow instead. It determines whether the target is empty and requires explicit user confirmation before scaffolding a nonempty directory.

Never create marketplace catalogs directly from this skill. Once the marketplace is initialized, collect the plugin name, initial skill name, user-facing description, publisher name, and target hosts when they are not clear. Plugin and skill names must be lowercase kebab-case.

## Create a plugin

1. Locate this skill's `scripts/scaffold_plugin.py` and run it with an explicit target:

   ```shell
   python /absolute/path/to/scaffold_plugin.py \
     --marketplace /path/to/marketplace \
     --name <plugin-name> \
     --skill <skill-name> \
     --description "<purpose>" \
     --author "<publisher>" \
     --hosts claude,openai,github
   ```

   Omit hosts that the user does not need. The script refuses to overwrite packages or catalog entries.
2. Replace the generated `SKILL.md` template with focused trigger conditions, explicit inputs and outputs, and a deterministic workflow.
3. Add host-specific agents, hooks, MCP servers, or UI only when a supported host needs that capability. Keep each supporting resource inside the native package that needs it; do not create compatibility stubs.
4. Validate the new cross-host plugin:

   ```shell
   python /absolute/path/to/validate_marketplace.py \
     --marketplace /path/to/marketplace \
     --plugin <plugin-name> \
     --hosts claude,openai,github \
     --require-all-hosts
   ```

## Component guides

After the package skeleton exists, load the guide for the component being added rather than extending this general workflow:

- `marketplace-skill-authoring` for reusable instructions.
- `marketplace-agent-authoring` for host-native autonomous agents and their frontmatter capability names.
- `marketplace-mcp-authoring` for model-callable MCP capabilities.
- `marketplace-hook-authoring` for deterministic lifecycle automation.
- `marketplace-connector-authoring` for OpenAI authenticated external-service integrations only.

## Harness-specific tool names

“Tool collection” is only a planning term. Use each harness's native name and registration model:

- **Claude Code — MCP server.** Bundle it in `.mcp.json` or `plugin.json` `mcpServers`. Claude exposes each server tool as `mcp__plugin_<plugin-name>_<server-name>__<tool-name>`; use that full name in `allowed-tools` and avoid wildcard grants.
- **OpenAI Codex — plugin-provided MCP server.** Do not copy Claude's prefixed tool name or GitHub's `tools` field. Codex policy addresses a server as `plugins.<plugin>.mcp_servers.<server>` and controls its discovered tool names with `enabled_tools`, `disabled_tools`, and per-tool approval settings.
- **GitHub Copilot — custom tool or MCP server.** Use `tools` for direct custom-tool registrations. Use the root `plugin.json` `mcpServers` reference to an in-package `.mcp.json` for MCP-backed tools, as in this marketplace's GitHub package pattern.

Add a server or custom tool only when the workflow needs model-callable operations. Define each operation's input schema, output contract, error behavior, authentication boundary, and least privileges. Keep every manifest, executable or server, and supporting asset inside its host-native package; never cross-reference a sibling package or add a compatibility stub. Exercise each exposed operation through its target host before claiming it works; the marketplace validator checks package structure only.

## Agent frontmatter tool collections

Agent `tools` arrays are host-specific and separate from MCP tool names. Never copy a Claude collection into a Copilot agent.

- **Claude Code:** use the required Claude tool names, such as `tools: ["Read", "Grep", "Glob"]` for a read-only reviewer.
- **GitHub Copilot:** use documented primary aliases. For a read-only reviewer use `tools: ["read", "search"]`; use `edit` for modification, `execute` for shell access, and `agent` for custom-agent delegation only when required. Copilot aliases are case-insensitive, but `view`, `grep`, and `glob` are not the primary frontmatter aliases.
- **OpenAI Codex package:** this marketplace's native package ships skills, connectors, MCP servers, hooks, and other supported plugin components—not a Claude or Copilot agent-frontmatter shim.

Use the smallest host-native collection needed for the agent's task. Verify each tool name against the current host contract before adding capabilities.

## Modify an existing plugin

- Preserve native manifest locations: `.claude-plugin/plugin.json`, `.codex-plugin/plugin.json`, and root `plugin.json`.
- Keep every catalog source inside its own marketplace root. Do not point a host catalog at another host's package.
- Keep scripts and resources inside the package that needs them; installed plugins cannot reliably reference sibling packages.
- Run the validator for every changed host. It validates catalog sources; validate remote catalog sources with their host's installation flow instead.

## Host-native validation

The bundled validator checks catalog links, manifests, and skill frontmatter. It does not replace host-native validation:

- Claude Code: `claude plugin validate <claude-package> --strict`
- GitHub Copilot: add the marketplace and run `copilot plugin marketplace browse <marketplace-name>`
- OpenAI Codex: add and list the marketplace with `codex plugin marketplace add <marketplace-root>` and `codex plugin marketplace list`

Do not claim a plugin works until the applicable checks pass.
