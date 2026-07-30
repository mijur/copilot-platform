#!/usr/bin/env python3
"""Initialize native catalogs for a cross-harness marketplace."""

import argparse
import json
import re
import sys
from pathlib import Path

NAME_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
HOST_SPECS = {
    "claude": {"catalog": ".claude-plugin/marketplace.json"},
    "openai": {"catalog": ".agents/plugins/marketplace.json"},
    "github": {"catalog": ".github/plugin/marketplace.json"},
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
        description="Initialize Claude, OpenAI, and Copilot marketplace catalogs."
    )
    parser.add_argument("--marketplace", type=Path, required=True, help="Marketplace root to create or initialize")
    parser.add_argument("--name", required=True, help="Kebab-case marketplace name")
    parser.add_argument("--description", required=True, help="Marketplace purpose")
    parser.add_argument("--author", required=True, help="Marketplace publisher or team name")
    parser.add_argument("--version", default="1.0.0", help="Initial marketplace version")
    parser.add_argument(
        "--hosts",
        default="claude,openai,github",
        help="Comma-separated catalogs to create (default: claude,openai,github)",
    )
    parser.add_argument(
        "--allow-existing-files",
        action="store_true",
        help="Confirm scaffolding into a nonempty target directory",
    )
    return parser.parse_args()


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def catalog_for(host, args, author):
    if host == "claude":
        return {
            "name": args.name,
            "owner": author,
            "description": args.description,
            "version": args.version,
            "plugins": [],
        }
    if host == "openai":
        return {
            "name": args.name,
            "interface": {"displayName": args.name.replace("-", " ").title()},
            "plugins": [],
        }
    return {
        "name": args.name,
        "owner": author,
        "metadata": {"description": args.description, "version": args.version},
        "plugins": [],
    }


def main():
    args = parse_args()
    hosts = parse_hosts(args.hosts)
    if not NAME_PATTERN.fullmatch(args.name):
        raise ValueError("--name must be lowercase kebab-case")
    if not args.description.strip() or not args.author.strip() or not args.version.strip():
        raise ValueError("--description, --author, and --version cannot be empty")

    marketplace = args.marketplace.resolve()
    if marketplace.exists() and not marketplace.is_dir():
        raise ValueError(f"--marketplace must be a directory: {marketplace}")
    existing_entries = list(marketplace.iterdir()) if marketplace.exists() else []
    catalogs = {host: marketplace / HOST_SPECS[host]["catalog"] for host in hosts}
    existing = [path for path in catalogs.values() if path.exists()]
    if existing:
        joined = ", ".join(str(path) for path in existing)
        raise ValueError(f"Refusing to overwrite existing host catalog(s): {joined}")
    if existing_entries and not args.allow_existing_files:
        entries = ", ".join(str(path) for path in existing_entries)
        raise ValueError(
            "Target contains existing entries; rerun with --allow-existing-files only after user confirmation: "
            f"{entries}"
        )

    marketplace.mkdir(parents=True, exist_ok=True)
    (marketplace / "plugins").mkdir(exist_ok=True)
    author = {"name": args.author.strip()}
    for host, path in catalogs.items():
        write_json(path, catalog_for(host, args, author))

    print(f"Initialized '{args.name}' for: {', '.join(hosts)}")
    print("Create plugins with scaffold_plugin.py, then run validate_marketplace.py.")


if __name__ == "__main__":
    try:
        main()
    except ValueError as error:
        print(f"error: {error}", file=sys.stderr)
        raise SystemExit(2)
