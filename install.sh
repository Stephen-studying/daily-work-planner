#!/usr/bin/env sh
set -eu

destination="${CODEX_HOME:-"$HOME/.codex"}/skills"
force=0

while [ "$#" -gt 0 ]; do
  case "$1" in
    --dest)
      destination="$2"
      shift 2
      ;;
    --force)
      force=1
      shift
      ;;
    -h|--help)
      echo "Usage: sh install.sh [--dest PATH] [--force]"
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      exit 2
      ;;
  esac
done

repo_root="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
source_dir="$repo_root/daily-work-planner"

if [ ! -f "$source_dir/SKILL.md" ]; then
  echo "Cannot find SKILL.md at $source_dir/SKILL.md. Run this script from the repository root." >&2
  exit 1
fi

mkdir -p "$destination"
destination_abs="$(CDPATH= cd -- "$destination" && pwd)"
target="$destination_abs/daily-work-planner"

if [ -e "$target" ]; then
  if [ "$force" -ne 1 ]; then
    echo "Target already exists: $target. Re-run with --force to replace it." >&2
    exit 1
  fi
  case "$target" in
    "$destination_abs"/daily-work-planner)
      rm -rf "$target"
      ;;
    *)
      echo "Refusing to remove target outside destination: $target" >&2
      exit 1
      ;;
  esac
fi

cp -R "$source_dir" "$target"

echo "Installed Daily Work Planner skill to:"
echo "$target"
echo ""
echo 'Restart Codex, then use: Use $daily-work-planner to plan my work session.'
