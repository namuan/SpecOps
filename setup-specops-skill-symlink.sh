#!/usr/bin/env bash

set -euo pipefail

SKILL_NAME="specops"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SOURCE_SKILL_DIR="${SCRIPT_DIR}/specops"
TARGET_SKILLS_DIR="${HOME}/.agents/skills"
TARGET_LINK="${TARGET_SKILLS_DIR}/${SKILL_NAME}"

if [[ ! -d "${SOURCE_SKILL_DIR}" ]]; then
  echo "Error: expected skill directory not found: ${SOURCE_SKILL_DIR}" >&2
  exit 1
fi

mkdir -p "${TARGET_SKILLS_DIR}"

if [[ -e "${TARGET_LINK}" && ! -L "${TARGET_LINK}" ]]; then
  echo "Error: ${TARGET_LINK} exists and is not a symlink. Move/remove it and retry." >&2
  exit 1
fi

ln -sfn "${SOURCE_SKILL_DIR}" "${TARGET_LINK}"

echo "SpecOps skill linked successfully."
echo "  Link:   ${TARGET_LINK}"
echo "  Target: ${SOURCE_SKILL_DIR}"
echo
echo "You can now trigger the skill with: /${SKILL_NAME}"
