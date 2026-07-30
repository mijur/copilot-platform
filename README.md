# Cross-Harness Agent Plugin Marketplace

This marketplace ships host-native packages for the same workflow, intentionally duplicating shared content because each host resolves plugin manifests from a different location and OpenAI plugins do not package custom agents.

| Host | Marketplace catalog | Plugin package | Components |
| --- | --- | --- | --- |
| Claude Code | `.claude-plugin/marketplace.json` | `plugins/claude-*/` | `backend-standards`, `plugin-authoring` |
| OpenAI Codex / ChatGPT | `.agents/plugins/marketplace.json` | `plugins/openai-*/` | `backend-standards`, `plugin-authoring` |
| GitHub Copilot | `.github/plugin/marketplace.json` | `plugins/<plugin-name>/` | `backend-standards`, `plugin-authoring` |

## Included workflow

`backend-standards` supplies three focused capabilities:

- **`conventional-commits` skill** — drafts a Conventional Commit from the current change intent.
- **`backend-code-reviewer` agent** — where the host supports packaged agents, reviews backend changes for dependency injection, structured logging, API error envelopes, and endpoint authorization.
- **Infrastructure guard hook** — blocks agent write tools from modifying project files that the team protects, including solution, project, and pipeline files.

The infrastructure guard is intentionally narrow and does not invoke network services or require credentials. Claude Code and Codex require the user to review and trust plugin hooks before they run; the Copilot package uses its native hook configuration.

## Portable marketplace-authoring tooling

`plugin-authoring` is an installable toolkit for shared cross-harness marketplaces. It has two deliberately separate workflows and never assumes or targets this repository when used.

- **`marketplace-initialization` skill** — inspects the target first, avoids scaffolding when selected catalogs already exist, and requires explicit confirmation before scaffolding a nonempty directory. It does not create plugins.
- **`marketplace-plugin-authoring` skill** — inspects target catalogs and routes uninitialized targets to the initialization workflow; it creates, modifies, and validates native plugin packages only after required catalogs exist.
- **`initialize_marketplace.py`** — validates marketplace metadata, creates `plugins/` and selected host-native catalogs, refuses to overwrite a catalog, and rejects nonempty targets unless passed `--allow-existing-files` after user confirmation.
- **`scaffold_plugin.py`** — validates caller-provided plugin metadata, checks selected catalogs for collisions, creates host-native package skeletons, seeds a portable skill, and registers the selected catalogs.
- **`validate_marketplace.py`** — validates catalog sources, native manifests, package containment, and portable skill frontmatter. It supports individual hosts or `--require-all-hosts` for a cross-host plugin.
- **`release_plugin.py`** — synchronizes a Semantic Version across selected native manifests and matching Claude/Copilot catalog entries; it can also update supported marketplace catalog versions.
- **`marketplace-plugin-reviewer` agent** — available in Claude Code and GitHub Copilot; reviews a supplied marketplace without modifying it.

Initialize a target marketplace explicitly before authoring its first plugin:

For a nonempty target missing requested catalogs, inspect and list its existing entries, obtain explicit user confirmation, then append `--allow-existing-files` to the initialization command.

```shell
python /absolute/path/to/initialize_marketplace.py \
  --marketplace /path/to/marketplace \
  --name example-developer-tools \
  --description "Internal developer-tool marketplace." \
  --author "Example Developer Tools" \
  --hosts claude,openai,github

python /absolute/path/to/scaffold_plugin.py \
  --marketplace /path/to/marketplace \
  --name api-design \
  --skill api-contract \
  --description "Guide API contract design." \
  --author "Example Developer Tools" \
  --hosts claude,openai,github

python /absolute/path/to/validate_marketplace.py \
  --marketplace /path/to/marketplace \
  --plugin api-design \
  --hosts claude,openai,github \
  --require-all-hosts
```

The scaffold intentionally creates only the portable skill. Add an agent, hook, MCP server, or other host-specific component only after the workflow needs it.

Component-specific skills supplement the general authoring workflow:

- `marketplace-skill-authoring` — reusable instructions.
- `marketplace-agent-authoring` — host-native agent prompts and frontmatter capability names.
- `marketplace-mcp-authoring` — MCP-backed model-callable capabilities.
- `marketplace-hook-authoring` — deterministic lifecycle automation.
- `marketplace-connector-authoring` — OpenAI-only authenticated external-service integrations.
- `marketplace-versioning` — Semantic Versioning, release channels, immutable tags, and maintained legacy lines.

### Reusable GitHub Copilot components

Follow the Awesome Copilot composition pattern for GitHub Copilot: keep reusable agents in the marketplace-level `agents/` collection and reusable skills in `skills/`. A thin adapter at `plugins/<plugin>/.github/plugin/plugin.json` lists the exact component paths, for example `"./agents/reviewer.agent.md"` and `"./skills/review-workflow/"`. Multiple adapters can reference the same component without copying it. This pattern is GitHub-specific; Claude and OpenAI packages remain self-contained because their installed packages must carry their own resources.

### Harness-specific tool names

“Tool collection” is a generic planning term, not a portable plugin API. **Claude Code** packages an **MCP server** in `.mcp.json` or `plugin.json` `mcpServers`; its exposed names are `mcp__plugin_<plugin-name>_<server-name>__<tool-name>`. **OpenAI Codex** calls bundled servers **plugin-provided MCP servers**; user policy addresses them at `plugins.<plugin>.mcp_servers.<server>` and filters discovered tool names with `enabled_tools` or `disabled_tools`. **GitHub Copilot** distinguishes direct custom-tool registrations (`tools`) from MCP-backed tools (`mcpServers` pointing at an in-package `.mcp.json`). Keep every registration and implementation inside its host-native package, and validate each exposed operation in the target host.

### Agent frontmatter tool collections

Agent capabilities use a separate, host-specific `tools` array; they are neither MCP tool names nor portable vocabulary. Claude Code uses its own names, for example `tools: ["Read", "Grep", "Glob"]` for a read-only reviewer. GitHub Copilot uses documented primary aliases: `tools: ["read", "search"]`; use `edit`, `execute`, or `agent` only when the agent needs those capabilities. Copilot aliases are case-insensitive, but `view`, `grep`, and `glob` are not its primary frontmatter aliases. The OpenAI Codex package must not receive a Claude or Copilot agent-frontmatter shim.

### Releasing and preserving versions

Run the release script with one logical plugin version across native packages, then validate, tag, and publish the intended channel:

```shell
python /absolute/path/to/release_plugin.py \
  --marketplace /path/to/marketplace \
  --plugin api-design \
  --version 1.2.0 \
  --marketplace-version 1.2.0 \
  --hosts claude,openai,github
```

Keep historical releases as immutable Git tags and maintenance branches. Expose legacy lines through separate marketplace channels: Claude can pin marketplace or plugin sources to refs or SHAs; Codex can add Git marketplaces with `--ref`; Copilot should use a separately named legacy marketplace channel. Do not duplicate a plugin name inside one catalog.

## Try each native marketplace

Run the corresponding command from the repository root, then install `backend-standards` from the named marketplace.

```shell
# Claude Code
/plugin marketplace add ./
/plugin install backend-standards@ai-tool-lab-plugins

# GitHub Copilot CLI
copilot plugin marketplace add ./
copilot plugin install backend-standards@ai-tool-lab-plugins

# Codex CLI
codex plugin marketplace add ./
```

OpenAI marketplaces are exposed to Codex and the ChatGPT desktop app from `.agents/plugins/marketplace.json`. Restart the client after changing a package, then select the `AIToolLab-plugins` marketplace and install `backend-standards`.

Each package uses a host-native manifest. Do not point a catalog at a package for another host: `.claude-plugin/plugin.json`, `.codex-plugin/plugin.json`, and root `plugin.json` are distinct entry points.
