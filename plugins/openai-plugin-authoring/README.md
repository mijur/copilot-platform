# Plugin Authoring for OpenAI Codex and ChatGPT

Host-native `plugin-authoring` package for OpenAI Codex and ChatGPT. It initializes shared cross-harness marketplaces and authors, validates, and releases native plugins.

## Package contents

- `.codex-plugin/plugin.json` — OpenAI plugin manifest, which declares `skills/` as the package skill directory.
- `skills/` — marketplace initialization, general plugin authoring, and component-specific authoring and versioning workflows.
- `scripts/` — Python helpers plus PowerShell and Bash launchers for initialize, scaffold, validate, and release operations.

OpenAI packages skills only; this package intentionally contains no Claude Code or GitHub Copilot agent-frontmatter compatibility layer.

## Workflow and tooling

The package provides two deliberately separate workflows:

- **`marketplace-initialization` skill** — inspects the target first, avoids scaffolding when selected catalogs already exist, and requires explicit confirmation before scaffolding a nonempty directory. It does not create plugins.
- **`marketplace-plugin-authoring` skill** — inspects target catalogs and routes uninitialized targets to the initialization workflow; it creates, modifies, and validates native plugin packages only after required catalogs exist.

The helper scripts validate marketplace metadata, scaffold host-native package skeletons, validate catalogs and manifests, and synchronize Semantic Versions. Component-specific skills cover reusable skills, host-native agents, MCP-backed capabilities, hooks, OpenAI-only connectors, and versioning.

### Script language selection

The Python helpers are the independent, cross-platform fallback. `marketplace-tools.ps1` is the native PowerShell alternative; it accepts an operation first (`initialize`, `scaffold`, `validate`, or `release`) followed by the matching helper's options. Use it on Windows with PowerShell 7+: `& /absolute/path/to/marketplace-tools.ps1 scaffold ...`.

`marketplace-tools.sh` is the Bash entry point: `bash /absolute/path/to/marketplace-tools.sh scaffold ...`. It forwards to the colocated PowerShell implementation and requires `pwsh`; on a POSIX environment without `pwsh`, use the corresponding Python helper. Script choice is based on the caller's runtime, never the target marketplace host.

### Initialize, scaffold, and validate

Initialize a target marketplace explicitly before authoring its first plugin. For a nonempty target missing requested catalogs, inspect and list its existing entries, obtain explicit user confirmation, then append `--allow-existing-files` to the initialization command.

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

## OpenAI integration

OpenAI Codex calls bundled servers **plugin-provided MCP servers**. User policy addresses them at `plugins.<plugin>.mcp_servers.<server>` and filters discovered tool names with `enabled_tools` or `disabled_tools`. Do not add a Claude Code or GitHub Copilot agent-frontmatter shim to this package.

## Releasing and preserving versions

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
