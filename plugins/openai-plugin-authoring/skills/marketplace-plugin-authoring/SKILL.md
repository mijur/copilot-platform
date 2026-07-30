---
name: marketplace-plugin-authoring
description: Create, extend, or validate a plugin in a local cross-harness marketplace. Use when a user wants native Claude Code, OpenAI Codex, or GitHub Copilot plugin packages and catalogs created or changed.
---

Use the bundled scripts against the user's target marketplace. Never assume that the current repository is the target.

## Preconditions

The target marketplace must already contain the host catalog files it needs:

- Claude Code: `.claude-plugin/marketplace.json`
- OpenAI Codex / ChatGPT: `.agents/plugins/marketplace.json`
- GitHub Copilot: `.github/plugin/marketplace.json`

Ask for the marketplace path, plugin name, initial skill name, user-facing description, publisher name, and target hosts when they are not clear. Plugin and skill names must be lowercase kebab-case.

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
3. Add host-specific agents, hooks, MCP servers, or UI only when a supported host needs that capability. Do not create compatibility stubs.
4. Validate the new cross-host plugin:

   ```shell
   python /absolute/path/to/validate_marketplace.py \
     --marketplace /path/to/marketplace \
     --plugin <plugin-name> \
     --hosts claude,openai,github \
     --require-all-hosts
   ```

## Modify an existing plugin

- Preserve native manifest locations: `.claude-plugin/plugin.json`, `.codex-plugin/plugin.json`, and root `plugin.json`.
- Keep every local catalog source inside its own marketplace root. Do not point a host catalog at another host's package.
- Keep scripts and resources inside the package that needs them; installed plugins cannot reliably reference sibling packages.
- Run the validator for every changed host. It validates local sources; validate remote catalog sources with their host's installation flow instead.

## Host-native validation

The bundled validator checks local catalog links, manifests, and skill frontmatter. It does not replace host-native validation:

- Claude Code: `claude plugin validate <claude-package> --strict`
- GitHub Copilot: add the marketplace and run `copilot plugin marketplace browse <marketplace-name>`
- OpenAI Codex: add and list the marketplace with `codex plugin marketplace add <marketplace-root>` and `codex plugin marketplace list`

Do not claim a plugin works until the applicable checks pass.
