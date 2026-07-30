#!/usr/bin/env python3
import fnmatch
import json
import sys

PROTECTED = [
    "*.csproj",
    "*.sln",
    "azure-pipelines*.yml",
    ".github/workflows/*",
    "Directory.Build.props",
]
EDIT_TOOLS = {"edit", "write", "apply_patch", "applypatch", "replace"}


def tool_input(event):
    value = event.get("tool_input") or event.get("toolInput") or event.get("tool_args")
    if isinstance(value, dict):
        return value

    value = event.get("toolArgs")
    if isinstance(value, str):
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return {}
    return value if isinstance(value, dict) else {}


def is_edit(event):
    name = event.get("tool_name") or event.get("toolName")
    return name is None or str(name).lower() in EDIT_TOOLS


def is_protected(path):
    normalized = path.replace("\\", "/")
    name = normalized.rsplit("/", 1)[-1]
    return any(
        fnmatch.fnmatch(normalized, pattern) or fnmatch.fnmatch(name, pattern)
        for pattern in PROTECTED
    )


def main():
    try:
        event = json.load(sys.stdin)
    except json.JSONDecodeError:
        return 0

    if not is_edit(event):
        return 0

    payload = tool_input(event)
    path = payload.get("path") or payload.get("file_path") or payload.get("filePath") or ""
    if isinstance(path, str) and is_protected(path):
        print(
            f"BLOCKED by backend-standards: {path} is protected infrastructure. Open a PR instead.",
            file=sys.stderr,
        )
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
