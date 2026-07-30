# Cross-Harness Agent Plugin Marketplace

This marketplace ships host-native packages for the same workflow, intentionally duplicating shared content because each host resolves plugin manifests from a different location and OpenAI plugins do not package custom agents.

| Host | Marketplace catalog | Plugin package | Components |
| --- | --- | --- | --- |
| Claude Code | `.claude-plugin/marketplace.json` | `plugins/claude-*/` | `plugin-authoring` |
| OpenAI Codex / ChatGPT | `.agents/plugins/marketplace.json` | `plugins/openai-*/` | `plugin-authoring` |
| GitHub Copilot | `.github/plugin/marketplace.json` | `plugins/<plugin-name>/` | `plugin-authoring` |

## Plugins

- `plugin-authoring` — portable marketplace tooling that initializes shared cross-harness marketplaces, then scaffolds, validates, reviews, and releases host-native plugins. Package documentation: [Claude Code](plugins/claude-plugin-authoring/README.md), [OpenAI Codex / ChatGPT](plugins/openai-plugin-authoring/README.md), and [GitHub Copilot](plugins/plugin-authoring/README.md).

## Try each native marketplace

Run the corresponding command from the repository root, then install `plugin-authoring` from the named marketplace.

```shell
# Claude Code
/plugin marketplace add ./
/plugin install plugin-authoring@ai-tool-lab-plugins

# GitHub Copilot CLI
copilot plugin marketplace add ./
copilot plugin install plugin-authoring@ai-tool-lab-plugins

# Codex CLI
codex plugin marketplace add ./
```

OpenAI marketplaces are exposed to Codex and the ChatGPT desktop app from `.agents/plugins/marketplace.json`. Restart the client after changing a package, then select the `AIToolLab-plugins` marketplace and install `plugin-authoring`.

Each package uses a host-native manifest. Do not point a catalog at a package for another host: `.claude-plugin/plugin.json`, `.codex-plugin/plugin.json`, and root `plugin.json` are distinct entry points.
