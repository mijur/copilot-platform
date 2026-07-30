# Cross-Harness Agent Plugin Marketplace

This marketplace demonstrates the same `backend-standards` workflow in the three native plugin formats. The packages intentionally duplicate shared content because each host resolves plugin manifests from a different location and OpenAI plugins do not package custom agents.

| Host | Marketplace catalog | Plugin package | Components |
| --- | --- | --- | --- |
| Claude Code | `.claude-plugin/marketplace.json` | `plugins/claude-backend-standards/` | Skill, read-only reviewer agent, infrastructure guard |
| OpenAI Codex / ChatGPT | `.agents/plugins/marketplace.json` | `plugins/openai-backend-standards/` | Skill and Codex-only infrastructure guard |
| GitHub Copilot | `.github/plugin/marketplace.json` | `plugins/backend-standards/` | Skill, read-only reviewer agent, infrastructure guard |

## Included workflow

`backend-standards` supplies three focused capabilities:

- **`conventional-commits` skill** — drafts a Conventional Commit from the current change intent.
- **`backend-code-reviewer` agent** — where the host supports packaged agents, reviews backend changes for dependency injection, structured logging, API error envelopes, and endpoint authorization.
- **Infrastructure guard hook** — blocks agent write tools from modifying project files that the team protects, including solution, project, and pipeline files.

The infrastructure guard is intentionally narrow and does not invoke network services or require credentials. Claude Code and Codex require the user to review and trust plugin hooks before they run; the Copilot package uses its native hook configuration.

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
