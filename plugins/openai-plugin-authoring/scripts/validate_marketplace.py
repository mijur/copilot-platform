#!/usr/bin/env python3
"""Validate host-native plugin packages in any cross-harness marketplace."""

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
    "claude": {"catalog": ".claude-plugin/marketplace.json", "manifest": ".claude-plugin/plugin.json"},
    "openai": {"catalog": ".agents/plugins/marketplace.json", "manifest": ".codex-plugin/plugin.json"},
    "github": {"catalog": ".github/plugin/marketplace.json", "manifest": "plugin.json"},
}


def parse_hosts(value):
    hosts = [host.strip() for host in value.split(",") if host.strip()]
    invalid = sorted(set(hosts) - set(HOST_SPECS))
    if not hosts or invalid or len(hosts) != len(set(hosts)):
        valid = ", ".join(HOST_SPECS)
        raise ValueError(f"--hosts must be a unique comma-separated subset of: {valid}")
    return hosts


def parse_args():
    parser = argparse.ArgumentParser(description="Validate native plugin packages.")
    parser.add_argument("--marketplace", type=Path, required=True, help="Target marketplace root")
    parser.add_argument("--plugin", help="Validate one kebab-case plugin")
    parser.add_argument(
        "--hosts",
        default="claude,openai,github",
        help="Comma-separated hosts to validate (default: claude,openai,github)",
    )
    parser.add_argument(
        "--require-all-hosts",
        action="store_true",
        help="Require --plugin to be present in every selected host catalog",
    )
    return parser.parse_args()


def is_semver(value):
    return isinstance(value, str) and SEMVER_PATTERN.fullmatch(value) is not None


def read_json(path, errors):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        errors.append(f"Missing JSON file: {path}")
    except json.JSONDecodeError as error:
        errors.append(f"Invalid JSON in {path}: {error}")
    return None


def catalog_entries(catalog, path, errors):
    if not isinstance(catalog, dict):
        return {}
    plugins = catalog.get("plugins")
    if not isinstance(plugins, list):
        errors.append(f"{path}: plugins must be an array")
        return {}
    entries = {}
    for entry in plugins:
        name = entry.get("name") if isinstance(entry, dict) else None
        if not isinstance(name, str) or not NAME_PATTERN.fullmatch(name):
            errors.append(f"{path}: every plugin entry needs a kebab-case name")
            continue
        if name in entries:
            errors.append(f"{path}: duplicate plugin entry '{name}'")
            continue
        entries[name] = entry
    return entries


def local_source(host, entry, label, errors):
    source = entry.get("source")
    if host == "openai":
        if not isinstance(source, dict) or source.get("source") != "local":
            errors.append(f"{label}: only OpenAI target-path sources can be validated")
            return None
        source = source.get("path")
    if not isinstance(source, str) or not source.startswith("./"):
        errors.append(f"{label}: source must be a ./ path")
        return None
    return source


def inside_root(root, candidate):
    try:
        candidate.relative_to(root)
        return True
    except ValueError:
        return False


def frontmatter(path, errors):
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        errors.append(f"{path}: SKILL.md must begin with YAML frontmatter")
        return
    end = text.find("\n---\n", 4)
    if end < 0:
        errors.append(f"{path}: SKILL.md frontmatter is not terminated")
        return
    values = {}
    for line in text[4:end].splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            values[key.strip()] = value.strip()
    if not values.get("name") or not NAME_PATTERN.fullmatch(values["name"]):
        errors.append(f"{path}: frontmatter needs a non-empty kebab-case name")
    if not values.get("description"):
        errors.append(f"{path}: frontmatter needs a non-empty description")


def validate_entry(marketplace, host, name, entry, errors):
    label = f"{host} catalog '{name}'"
    source = local_source(host, entry, label, errors)
    if source is None:
        return
    package = (marketplace / source.removeprefix("./")).resolve()
    if not inside_root(marketplace, package):
        errors.append(f"{label}: source escapes the marketplace root")
        return
    manifest_path = package / HOST_SPECS[host]["manifest"]
    manifest = read_json(manifest_path, errors)
    if manifest is None:
        return
    if manifest.get("name") != name:
        errors.append(f"{manifest_path}: name must equal catalog entry '{name}'")
    if not is_semver(manifest.get("version")):
        errors.append(f"{manifest_path}: version must be a Semantic Version")
    elif host != "openai":
        catalog_version = entry.get("version")
        if not is_semver(catalog_version):
            errors.append(f"{label}: version must be a Semantic Version")
        elif catalog_version != manifest["version"]:
            errors.append(f"{label}: version must equal {manifest_path}")
    if not isinstance(manifest.get("description"), str) or not manifest["description"].strip():
        errors.append(f"{manifest_path}: description must be a non-empty string")
    skills_root = package / "skills"
    skills = list(skills_root.rglob("SKILL.md")) if skills_root.is_dir() else []
    if not skills:
        errors.append(f"{package}: must include at least one skills/*/SKILL.md")
    for skill in skills:
        frontmatter(skill, errors)
    return manifest.get("version")


def main():
    args = parse_args()
    hosts = parse_hosts(args.hosts)
    if args.plugin and not NAME_PATTERN.fullmatch(args.plugin):
        raise ValueError("--plugin must be lowercase kebab-case")
    marketplace = args.marketplace.resolve()
    errors = []
    entries = {}
    versions = {}
    for host in hosts:
        catalog_path = marketplace / HOST_SPECS[host]["catalog"]
        entries[host] = catalog_entries(read_json(catalog_path, errors), catalog_path, errors)

    checks = []
    if args.plugin:
        missing_hosts = [host for host in hosts if args.plugin not in entries[host]]
        if args.require_all_hosts and missing_hosts:
            errors.append(f"Plugin '{args.plugin}' is missing from: {', '.join(missing_hosts)}")
        for host in hosts:
            entry = entries[host].get(args.plugin)
            if entry is not None:
                checks.append((host, args.plugin, entry))
    else:
        for host, host_entries in entries.items():
            checks.extend((host, name, entry) for name, entry in host_entries.items())

    for host, name, entry in checks:
        version = validate_entry(marketplace, host, name, entry, errors)
        if version:
            versions.setdefault(name, {})[host] = version
    if args.require_all_hosts and args.plugin and len(set(versions.get(args.plugin, {}).values())) > 1:
        errors.append(f"Plugin '{args.plugin}' must use one version across selected hosts")

    if errors:
        print("Marketplace validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        raise SystemExit(1)
    checked = ", ".join(f"{host}:{name}" for host, name, _ in checks) or "no plugins"
    print(f"Marketplace validation passed: {checked}")


if __name__ == "__main__":
    try:
        main()
    except ValueError as error:
        print(f"error: {error}", file=sys.stderr)
        raise SystemExit(2)
