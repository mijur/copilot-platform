# Cross-Harness Agent Plugin Marketplace

This marketplace ships host-native packages for the same workflow, intentionally duplicating shared content because each host resolves plugin manifests from a different location and OpenAI plugins do not package custom agents.

| Host | Marketplace catalog | Plugin package | Components |
| --- | --- | --- | --- |
| Claude Code | `.claude-plugin/marketplace.json` | `plugins/claude-*/` | `plugin-authoring` |
| OpenAI Codex / ChatGPT | `.agents/plugins/marketplace.json` | `plugins/openai-*/` | `plugin-authoring` |
| GitHub Copilot | `.github/plugin/marketplace.json` | `plugins/<plugin-name>/` | `plugin-authoring` |

## Plugins

- `plugin-authoring` — portable marketplace tooling that initializes shared cross-harness marketplaces, then scaffolds, validates, reviews, and releases host-native plugins. Package documentation: [Claude Code](plugins/claude-plugin-authoring/README.md), [OpenAI Codex / ChatGPT](plugins/openai-plugin-authoring/README.md), and [GitHub Copilot](plugins/plugin-authoring/README.md).

## Add this marketplace

Use the repository URL `https://github.com/mijur/aitoollab-plugins` in the applicable host client, then install `plugin-authoring` from the `ai-tool-lab-plugins` marketplace.

### Claude Code
Navigated within the session

```shell
/plugin marketplace add https://github.com/mijur/aitoollab-plugins
```
```shell
/plugin install plugin-authoring@ai-tool-lab-plugins
```

### GitHub Copilot CLI

Navigated within the session

```shell
/plugin marketplace add https://github.com/mijur/aitoollab-plugins
```
```shell
/plugin add plugin-authoring
```

### OpenAI Codex

```shell
codex plugin marketplace add https://github.com/mijur/aitoollab-plugins
```
```shell
codex plugin add plugin-authoring@ai-tool-lab-plugins
```

Each package uses a host-native manifest. Do not point a catalog at a package for another host: `.claude-plugin/plugin.json`, `.codex-plugin/plugin.json`, and root `plugin.json` are distinct entry points.
