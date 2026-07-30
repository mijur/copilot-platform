---
name: marketplace-hook-authoring
description: Add or revise lifecycle hooks in a native Claude Code, OpenAI Codex, or GitHub Copilot marketplace plugin. Use when deterministic policy or automation must run at a host lifecycle event.
---

Use hooks only for deterministic lifecycle work. Do not implement a conversational workflow, reusable instruction, or model-callable tool as a hook.

## Use the host-native schema

- **Claude Code:** package `hooks/hooks.json`; use the Claude hook schema and `${CLAUDE_PLUGIN_ROOT}` for bundled commands. The existing package pattern registers a `PreToolUse` command under a matcher.
- **OpenAI Codex:** package a host-supported hook configuration and use `${PLUGIN_ROOT}` for bundled commands. Review and trust hooks before enabling them; do not assume Claude's root variable or manifest behavior applies.
- **GitHub Copilot:** point a standalone root `plugin.json` or reusable adapter `.github/plugin/plugin.json` `hooks` field at an in-package `hooks/hooks.json`. The existing pattern uses `version: 1`, a hook `type: "command"`, platform-specific `bash` and `powershell` commands, `${PLUGIN_ROOT}`, and `timeoutSec`. Hooks remain package-specific; only agents and skills use the marketplace-level reusable collections.

## Author and validate

1. Select the narrowest event and matcher; reject or no-op outside the policy boundary.
2. Keep commands noninteractive, bounded by a timeout, and safe for repeated invocation. Validate untrusted event input before use.
3. Store code and configuration inside the host-native package; never call a sibling package.
4. Test allow and block paths with representative event payloads, then verify the installed host runs the hook at the intended lifecycle point.