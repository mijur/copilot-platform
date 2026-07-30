---
name: marketplace-versioning
description: Release, preserve, or maintain versions of a cross-harness marketplace plugin. Use when a user asks to bump a plugin, create a release, maintain an older major line, or make prior versions available.
---

Use one stable kebab-case plugin identity. Do not place duplicate entries with the same plugin name in one host catalog and do not create `plugin-v2` as a versioning substitute.

## Release the current line

Use Semantic Versioning: patch for compatible fixes, minor for compatible capabilities, and major for breaking skill, agent, hook, tool, or host-support changes. A cross-harness release has one plugin version across selected native packages.

Run the host-native authoring adapter's `scripts/release_plugin.py` before tagging. For a reusable GitHub Copilot skill, use the adapter package's script rather than expecting an executable beside the shared skill:

```shell
python /absolute/path/to/release_plugin.py \
  --marketplace /path/to/marketplace \
  --plugin <plugin-name> \
  --version 1.2.0 \
  --marketplace-version 1.2.0 \
  --hosts claude,openai,github
```

The script updates every selected native manifest and matching Claude/Copilot catalog entry together. The OpenAI catalog has no per-plugin version field; its native manifest is authoritative. Validate immediately after the release update.

## Preserve previous releases

Create an immutable Git tag for every release, for example `plugin-name-v1.2.0`. Keep a maintenance branch such as `release/1.x` only while that major line receives fixes.

Use release channels, not duplicate catalog entries:

- **Claude Code:** stable and legacy marketplaces may point at different Git refs or exact SHAs. Each channel must resolve to a distinct plugin version.
- **OpenAI Codex:** add a Git-backed marketplace with `--ref release/1.x` or an immutable release tag.
- **GitHub Copilot:** publish a separately named legacy marketplace channel or repository for the older line; its documented install flow selects `plugin@marketplace`, not `plugin@version`.

A user selects one channel for a plugin identity. Do not promise that an installed host can select an arbitrary historical SemVer from one catalog.

## Validate and publish

1. Run `validate_marketplace.py` for every released host with `--require-all-hosts`.
2. Run host-native validation and install/browse the intended release channel.
3. Create and push the immutable Git tag only after validation succeeds.
4. Publish or refresh the hosted marketplace source. Keep release notes and support status with the tag or maintenance branch.