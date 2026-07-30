#!/usr/bin/env python3
"""Scaffold host-native packages in any cross-harness marketplace."""

import argparse
import json
import re
import sys
from pathlib import Path

NAME_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
SEMVER_PATTERN = re.compile(
    r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)"
    r"(?:-[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?"
    r"(?:\+[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?$"
)
HOST_SPECS = {
    "claude": {
        "catalog": ".claude-plugin/marketplace.json",
        "package": "plugins/claude-{name}",
        "manifest": ".claude-plugin/plugin.json",
    },
    "openai": {
        "catalog": ".agents/plugins/marketplace.json",
        "package": "plugins/openai-{name}",
        "manifest": ".codex-plugin/plugin.json",
    },
    "github": {
        "catalog": ".github/plugin/marketplace.json",
        "package": "plugins/{name}",
        "manifest": "plugin.json",
    },
}


def parse_hosts(value):
    hosts = [host.strip() for host in value.split(",") if host.strip()]
    invalid = sorted(set(hosts) - set(HOST_SPECS))
    if not hosts or invalid or len(hosts) != len(set(hosts)):
        valid = ", ".join(HOST_SPECS)
        raise ValueError(f"--hosts must be a unique comma-separated subset of: {valid}")
    return hosts


def parse_args():
    parser = argparse.ArgumentParser(
        description="Scaffold a plugin for one or more Claude, OpenAI, and Copilot marketplaces."
    )
    parser.add_argument("--marketplace", type=Path, required=True, help="Target marketplace root")
    parser.add_argument("--name", required=True, help="Kebab-case plugin name")
    parser.add_argument("--skill", required=True, help="Kebab-case initial skill name")
    parser.add_argument("--description", required=True, help="Plugin and initial-skill purpose")
    parser.add_argument("--author", required=True, help="Publisher or team name for generated manifests")
    parser.add_argument("--version", default="1.0.0", help="Initial plugin version")
    parser.add_argument(
        "--hosts",
        default="claude,openai,github",
        help="Comma-separated hosts to target (default: claude,openai,github)",
    )
    return parser.parse_args()


def load_json(path):
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as error:
        raise ValueError(f"Target host catalog is missing: {path}") from error
    except json.JSONDecodeError as error:
        raise ValueError(f"Invalid JSON in {path}: {error}") from error
    if not isinstance(value, dict) or not isinstance(value.get("plugins"), list):
        raise ValueError(f"Catalog must contain a plugins array: {path}")
    return value


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def skill_template(name, description):
    return f"""---
name: {name}
description: {description}
---

Use this skill when the user's request matches its description.

1. Identify required inputs and ask one concise question when one is missing.
2. Follow the smallest safe workflow that completes the requested task.
3. State the result, changed artifacts, and validation performed.
4. Do not invent tool results, file contents, or external state.
"""


def manifest_for(host, args, author):
    shared = {
        "name": args.name,
        "description": args.description,
        "version": args.version,
        "author": author,
        "license": "MIT",
        "keywords": ["agent-plugin"],
    }
    if host == "claude":
        return shared
    if host == "openai":
        return {
            **shared,
            "skills": "./skills/",
            "interface": {
                "displayName": args.name.replace("-", " ").title(),
                "shortDescription": args.description,
                "longDescription": args.description,
                "developerName": args.author,
                "category": "Productivity",
                "capabilities": ["Read"],
            },
        }
    return {**shared, "skills": "skills/"}


def catalog_entry_for(host, args, author, package_source):
    if host == "openai":
        return {
            "name": args.name,
            "source": {"source": "local", "path": package_source},
            "policy": {"installation": "AVAILABLE", "authentication": "ON_INSTALL"},
            "category": "Productivity",
        }
    return {
        "name": args.name,
        "source": package_source,
        "description": args.description,
        "version": args.version,
        "author": author,
        "license": "MIT",
        "keywords": ["agent-plugin"],
    }


def main():
    args = parse_args()
    hosts = parse_hosts(args.hosts)
    if not NAME_PATTERN.fullmatch(args.name):
        raise ValueError("--name must be lowercase kebab-case")
    if not NAME_PATTERN.fullmatch(args.skill):
        raise ValueError("--skill must be lowercase kebab-case")
    if not args.description.strip() or not args.author.strip():
        raise ValueError("--description and --author cannot be empty")
    if not SEMVER_PATTERN.fullmatch(args.version):
        raise ValueError("--version must be a Semantic Version such as 1.2.3 or 1.2.3-rc.1")

    marketplace = args.marketplace.resolve()
    author = {"name": args.author.strip()}
    catalogs = {
        host: marketplace / HOST_SPECS[host]["catalog"]
        for host in hosts
    }
    catalog_data = {host: load_json(path) for host, path in catalogs.items()}
    packages = {
        host: marketplace / HOST_SPECS[host]["package"].format(name=args.name)
        for host in hosts
    }

    for package in packages.values():
        if package.exists():
            raise ValueError(f"Refusing to overwrite existing package: {package}")
    for host, catalog in catalog_data.items():
        if any(entry.get("name") == args.name for entry in catalog["plugins"] if isinstance(entry, dict)):
            raise ValueError(f"Refusing to overwrite {host} catalog entry: {args.name}")

    for host, package in packages.items():
        skill_path = package / "skills" / args.skill / "SKILL.md"
        skill_path.parent.mkdir(parents=True)
        skill_path.write_text(skill_template(args.skill, args.description), encoding="utf-8")
        manifest_path = package / HOST_SPECS[host]["manifest"]
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        write_json(manifest_path, manifest_for(host, args, author))

    for host, catalog in catalog_data.items():
        source = "./" + HOST_SPECS[host]["package"].format(name=args.name)
        catalog["plugins"].append(catalog_entry_for(host, args, author, source))
        write_json(catalogs[host], catalog)

    print(f"Created '{args.name}' for: {', '.join(hosts)}")
    print("Replace the generated skill instructions, then run validate_marketplace.py.")


if __name__ == "__main__":
    try:
        main()
    except ValueError as error:
        print(f"error: {error}", file=sys.stderr)
        raise SystemExit(2)
