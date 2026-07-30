#!/usr/bin/env python3
"""Synchronize a plugin release version across native marketplace packages."""

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
        "marketplace_version": ("version",),
    },
    "openai": {
        "catalog": ".agents/plugins/marketplace.json",
        "package": "plugins/openai-{name}",
        "manifest": ".codex-plugin/plugin.json",
        "marketplace_version": None,
    },
    "github": {
        "catalog": ".github/plugin/marketplace.json",
        "package": "plugins/{name}",
        "manifest": "plugin.json",
        "marketplace_version": ("metadata", "version"),
    },
}


def parse_hosts(value):
    hosts = [host.strip() for host in value.split(",") if host.strip()]
    invalid = sorted(set(hosts) - set(HOST_SPECS))
    if not hosts or invalid or len(hosts) != len(set(hosts)):
        raise ValueError("--hosts must be a unique comma-separated subset of: " + ", ".join(HOST_SPECS))
    return hosts


def parse_args():
    parser = argparse.ArgumentParser(description="Release one plugin version across native marketplace packages.")
    parser.add_argument("--marketplace", type=Path, required=True, help="Marketplace root")
    parser.add_argument("--plugin", required=True, help="Kebab-case plugin name")
    parser.add_argument("--version", required=True, help="New Semantic Version")
    parser.add_argument("--marketplace-version", help="Optional new Claude and Copilot marketplace Semantic Version")
    parser.add_argument("--hosts", default="claude,openai,github", help="Comma-separated hosts to release")
    return parser.parse_args()


def load_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as error:
        raise ValueError(f"Missing JSON file: {path}") from error
    except json.JSONDecodeError as error:
        raise ValueError(f"Invalid JSON in {path}: {error}") from error


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def entry_for(catalog, plugin, path):
    plugins = catalog.get("plugins") if isinstance(catalog, dict) else None
    if not isinstance(plugins, list):
        raise ValueError(f"Catalog must contain a plugins array: {path}")
    entries = [entry for entry in plugins if isinstance(entry, dict) and entry.get("name") == plugin]
    if len(entries) != 1:
        raise ValueError(f"Catalog must contain exactly one '{plugin}' entry: {path}")
    return entries[0]




def set_path(value, keys, replacement):
    for key in keys[:-1]:
        value = value.setdefault(key, {})
    value[keys[-1]] = replacement


def main():
    args = parse_args()
    hosts = parse_hosts(args.hosts)
    if not NAME_PATTERN.fullmatch(args.plugin):
        raise ValueError("--plugin must be lowercase kebab-case")
    if not SEMVER_PATTERN.fullmatch(args.version):
        raise ValueError("--version must be a Semantic Version such as 1.2.3 or 1.2.3-rc.1")
    if args.marketplace_version and not SEMVER_PATTERN.fullmatch(args.marketplace_version):
        raise ValueError("--marketplace-version must be a Semantic Version")

    marketplace = args.marketplace.resolve()
    releases = []
    current_versions = set()
    for host in hosts:
        spec = HOST_SPECS[host]
        catalog_path = marketplace / spec["catalog"]
        catalog = load_json(catalog_path)
        entry = entry_for(catalog, args.plugin, catalog_path)
        package = marketplace / spec["package"].format(name=args.plugin)
        manifest_path = package / spec["manifest"]
        manifest = load_json(manifest_path)
        if manifest.get("name") != args.plugin:
            raise ValueError(f"{manifest_path}: name must equal '{args.plugin}'")
        current = manifest.get("version")
        if not isinstance(current, str) or not SEMVER_PATTERN.fullmatch(current):
            raise ValueError(f"{manifest_path}: version must be a Semantic Version")
        current_versions.add(current)
        if host != "openai" and entry.get("version") != current:
            raise ValueError(f"{catalog_path}: '{args.plugin}' version must match {manifest_path}")
        releases.append((host, spec, catalog_path, catalog, entry, manifest_path, manifest))

    if len(current_versions) != 1:
        raise ValueError("Selected host packages must share one current plugin version before release")
    if args.version in current_versions:
        raise ValueError("--version must differ from the current plugin version")

    for host, spec, catalog_path, catalog, entry, manifest_path, manifest in releases:
        manifest["version"] = args.version
        if host != "openai":
            entry["version"] = args.version
        if args.marketplace_version and spec["marketplace_version"]:
            set_path(catalog, spec["marketplace_version"], args.marketplace_version)

    for _, _, catalog_path, catalog, _, manifest_path, manifest in releases:
        write_json(manifest_path, manifest)
        write_json(catalog_path, catalog)

    print(f"Released '{args.plugin}' {args.version} for: {', '.join(hosts)}")
    if args.marketplace_version:
        print(f"Updated supported marketplace catalog versions to {args.marketplace_version}")
    print("Create an immutable Git tag and publish the intended release channel after validation.")


if __name__ == "__main__":
    try:
        main()
    except ValueError as error:
        print(f"error: {error}", file=sys.stderr)
        raise SystemExit(2)
