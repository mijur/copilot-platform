---
name: marketplace-mcp-authoring
description: Add or revise MCP-backed capabilities in a native Claude Code, OpenAI Codex, or GitHub Copilot marketplace plugin. Use when a workflow needs model-callable tools backed by a server or external service.
---

MCP is shared protocol, not shared package syntax. Create a server only when a skill or agent needs model-callable operations; supporting scripts are not automatically tools.

## Use the host-native contract

- **Claude Code:** package servers in a root `.mcp.json` or inline `mcpServers` in `.claude-plugin/plugin.json`. Use `${CLAUDE_PLUGIN_ROOT}` for packaged paths. Claude exposes names as `mcp__plugin_<plugin-name>_<server-name>__<tool-name>`; commands and agents must use that full name when allowlisting tools.
- **OpenAI Codex:** use a plugin-provided MCP server. Codex policy controls it under `plugins.<plugin>.mcp_servers.<server>` and can allow or deny discovered names with `enabled_tools` and `disabled_tools`. Configure approval mode per server or tool; do not copy Claude's prefixed identifier.
- **GitHub Copilot:** use a standalone root `plugin.json` or a reusable adapter's `.github/plugin/plugin.json` `mcpServers` reference to an in-package `.mcp.json`. Share agents and skills through marketplace-level collections, but keep MCP configuration, executables, and credentials inside the adapter package. In a custom-agent profile, target individual tools as `<server>/<tool>` or all server tools as `<server>/*`.

## Author and validate

1. Give the server and every operation stable, descriptive names; define input schema, output shape, errors, authentication, side effects, and least privileges.
2. Keep the MCP manifest, executable or endpoint configuration, and assets inside the native package. Never reference a sibling package.
3. Use environment-variable references or host secret stores; never place credentials in the manifest or prompt.
4. Exercise each operation in the installed target host, including approval and authentication behavior. The marketplace validator checks package structure only.