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

## Portable plugin-authoring tooling

`plugin-authoring` is an installable authoring toolkit for **any existing local cross-harness marketplace**. It does not assume or target this repository when used.

- **`marketplace-plugin-authoring` skill** — guides creation and modification of native Claude, OpenAI, and Copilot plugin packages in an explicit target marketplace.
- **`scaffold_plugin.py`** — validates caller-provided names and publisher metadata, checks every selected catalog for collisions, creates host-native package skeletons, seeds a portable skill, and registers the selected catalogs.
- **`validate_marketplace.py`** — validates local catalog sources, native manifests, package containment, and portable skill frontmatter. It supports individual hosts or `--require-all-hosts` for a cross-host plugin.
- **`marketplace-plugin-reviewer` agent** — available in Claude Code and GitHub Copilot; reviews the supplied target marketplace without modifying it.

The toolkit expects the target marketplace to already provide the conventional catalog files for the hosts it will target. Run the bundled utilities with an explicit path and publisher:

```shell
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

## Try each native marketplace

Run the corresponding command from the repository root, then install `backend-standards` from the named marketplace.

```shell
# Claude Code
/plugin marketplace add ./
/plugin install backend-standards@copilot-platform-claude

# GitHub Copilot CLI
copilot plugin marketplace add ./
copilot plugin install backend-standards@copilot-platform-github

# Codex CLI
codex plugin marketplace add ./
```

OpenAI local marketplaces are exposed to Codex and the ChatGPT desktop app from `.agents/plugins/marketplace.json`. Restart the client after changing a local package, then select the `Copilot Platform — OpenAI` marketplace and install `backend-standards`.

Each package uses a host-native manifest. Do not point a catalog at a package for another host: `.claude-plugin/plugin.json`, `.codex-plugin/plugin.json`, and root `plugin.json` are distinct entry points.
