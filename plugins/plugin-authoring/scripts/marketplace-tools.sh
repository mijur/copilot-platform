#!/usr/bin/env bash
# Bash entry point for the cross-harness marketplace tooling.
# Requires PowerShell 7+ (pwsh); it forwards arguments to the native
# PowerShell implementation so every operation has identical behavior.
set -euo pipefail

script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)

pwsh_command=$(command -v pwsh || command -v pwsh.exe || true)
if [[ -z "$pwsh_command" && -x /mnt/c/Program\ Files/PowerShell/7/pwsh.exe ]]; then
  pwsh_command=/mnt/c/Program\ Files/PowerShell/7/pwsh.exe
fi
if [[ -z "$pwsh_command" ]]; then
  printf '%s\n' 'error: marketplace-tools.sh requires PowerShell 7+ (pwsh).' >&2
  printf '%s\n' 'Use marketplace-tools.ps1 directly on Windows, install PowerShell on Unix, or use the equivalent Python script.' >&2
  exit 127
fi

ps1_path="$script_dir/marketplace-tools.ps1"
if [[ "$ps1_path" =~ ^/mnt/([[:alpha:]])/(.*)$ ]]; then
  ps1_path="${BASH_REMATCH[1]^^}:/${BASH_REMATCH[2]}"
else
  cygpath_command=$(command -v cygpath || command -v cygpath.exe || true)
  if [[ -n "$cygpath_command" ]]; then
    ps1_path=$("$cygpath_command" -w "$ps1_path")
  fi
fi

exec "$pwsh_command" -NoProfile -File "$ps1_path" "$@"
