---
name: marketplace-initialization
description: Initialize a cross-harness marketplace for native Claude Code, OpenAI Codex, and GitHub Copilot plugins. Use when a user needs a new marketplace repository or host catalog created.
---

Use the bundled scripts against the user's explicit target directory. Never assume that the current repository is the target.
## Script language selection

All three variants accept the same operation and options. Keep the Python helper as the independent fallback; select the executable for the caller's shell:

- **PowerShell — recommended on Windows:** run `& /absolute/path/to/marketplace-tools.ps1 initialize ...`. It is a native PowerShell implementation and needs PowerShell 7+.
- **Bash — Bash or POSIX-shell entry point:** run `bash /absolute/path/to/marketplace-tools.sh initialize ...`. It forwards to the colocated PowerShell implementation, so it also needs `pwsh`; use it when the caller is already in Bash but PowerShell Core is installed.
- **Python — independent fallback:** run `python /absolute/path/to/initialize_marketplace.py ...` when `pwsh` is unavailable or the existing Python workflow is preferred.

Command mapping is `initialize`, `scaffold`, `validate`, and `release` for `initialize_marketplace.py`, `scaffold_plugin.py`, `validate_marketplace.py`, and `release_plugin.py`, respectively. Do not use the Bash launcher when `pwsh` is unavailable.

## Decide whether scaffolding is needed

Inspect the explicit target directory and the catalogs for the requested hosts before collecting initialization inputs:

1. If every requested catalog exists, the marketplace is already initialized. Do not scaffold; use `marketplace-plugin-authoring` instead.
2. If any requested catalog is absent and the target directory does not exist or is empty, initialize it without a confirmation step.
3. If any requested catalog is absent and the target contains any entry, list those entries and ask the user to explicitly confirm scaffolding into that directory. Do not run the initializer until confirmed.

For initialization, collect the lowercase kebab-case marketplace name, user-facing description, publisher name, and target hosts (`claude`, `openai`, and/or `github`). Ask only for inputs that cannot be determined from the request.

## Initialize

1. Locate the host-native authoring adapter's `scripts/initialize_marketplace.py`. For a reusable GitHub Copilot skill, the shared skill lives at the marketplace root while the executable remains in `plugins/<adapter>/scripts/`.

   ```shell
   python /absolute/path/to/initialize_marketplace.py \
     --marketplace /path/to/marketplace \
     --name <marketplace-name> \
     --description "<purpose>" \
     --author "<publisher>" \
     --hosts claude,openai,github
   ```

   Omit hosts the user does not need. After explicit confirmation for a nonempty directory, append `--allow-existing-files`. The script creates the target directory when necessary, creates `plugins/`, refuses to overwrite a selected host catalog, and rejects nonempty targets without that flag.
2. Confirm the selected native catalog locations exist:
   - Claude Code: `.claude-plugin/marketplace.json`
   - OpenAI Codex / ChatGPT: `.agents/plugins/marketplace.json`
   - GitHub Copilot: `.github/plugin/marketplace.json`
3. Validate the initialized catalogs:

   ```shell
   python /absolute/path/to/validate_marketplace.py \
     --marketplace /path/to/marketplace \
     --hosts claude,openai,github
   ```

4. For host-native integration validation, add or list the initialized marketplace using the applicable host CLI. No package-level host validation applies until a plugin package exists.

## Next step

Use `marketplace-plugin-authoring` to create native plugin packages in the initialized marketplace. Do not create cross-host package stubs, plugins, or skills during initialization.
