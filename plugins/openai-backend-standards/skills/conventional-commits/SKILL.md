---
name: conventional-commits
description: Draft a Conventional Commit message for the current change. Use when asked to write, review, or choose a commit message.
---

Create one Conventional Commit message that reflects the requested or observed change.

1. Determine the change's intent and affected scope from the supplied context or relevant files. Ask one concise clarification question if the intent cannot be determined.
2. Choose the narrowest valid type: `feat`, `fix`, `refactor`, `perf`, `test`, `build`, `ci`, `docs`, `style`, or `chore`.
3. Write the subject as `type(scope): imperative summary`, using a scope only when it adds useful context. Keep the subject at or below 72 characters.
4. Add a body only when it explains a non-obvious reason, behavior change, or migration. Add a `BREAKING CHANGE:` footer when applicable.
5. Return the message in a fenced `text` block and do not claim it was committed.
