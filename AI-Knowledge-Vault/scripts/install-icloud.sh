#!/bin/bash
# Install the AI Knowledge Vault into iCloud Drive on macOS.
#
# Safe by design:
#   * refuses to run anywhere that is not macOS with a real iCloud Drive
#   * never overwrites an existing file
#   * never invents an iCloud path
#   * keeps git metadata OUTSIDE the synchronized folder
#
# Usage:  ./scripts/install-icloud.sh [target-directory]

set -euo pipefail

SOURCE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ICLOUD="$HOME/Library/Mobile Documents/com~apple~CloudDocs"
TARGET="${1:-$ICLOUD/AI-Knowledge-Vault}"

echo "AI Knowledge Vault installer"
echo "  template : $SOURCE_DIR"

# ---- preflight -------------------------------------------------------------
if [ "$(uname -s)" != "Darwin" ]; then
  echo "ERROR: this is $(uname -s), not macOS. iCloud Drive does not exist here." >&2
  echo "  To use the vault on this machine anyway, pick a local path:" >&2
  echo "    python3 scripts/vault.py init --vault /path/to/vault --remember" >&2
  exit 1
fi

if [ ! -d "$HOME/Library/Mobile Documents" ]; then
  echo "ERROR: ~/Library/Mobile Documents does not exist." >&2
  echo "  iCloud Drive appears to be disabled. Enable it in System Settings >" >&2
  echo "  [your name] > iCloud > iCloud Drive, then re-run this installer." >&2
  exit 1
fi

if [ ! -d "$ICLOUD" ] && [ "${1:-}" = "" ]; then
  echo "ERROR: iCloud Drive container not found at:" >&2
  echo "  $ICLOUD" >&2
  echo "  Refusing to invent a location. Pass an explicit target directory:" >&2
  echo "    ./scripts/install-icloud.sh '/path/you/intend'" >&2
  exit 1
fi

command -v python3 >/dev/null 2>&1 || { echo "ERROR: python3 not found." >&2; exit 1; }
command -v git >/dev/null 2>&1 || echo "WARNING: git not found; provenance will be unavailable."

echo "  target   : $TARGET"

if [ -d "$TARGET" ] && [ -n "$(ls -A "$TARGET" 2>/dev/null)" ]; then
  echo "  NOTE: target already exists and is not empty."
  echo "        Existing files will NOT be overwritten."
fi

# ---- copy (never clobber) --------------------------------------------------
mkdir -p "$TARGET"
# -n = no-clobber. Copies the engine, docs, schemas, templates, and .claude/,
# and leaves any file already present exactly as it is.
(cd "$SOURCE_DIR" && tar cf - \
    --exclude='indexes/vault.db' --exclude='__pycache__' --exclude='.git' .) \
  | (cd "$TARGET" && tar xf - --keep-old-files 2>/dev/null || true)

# ---- initialize ------------------------------------------------------------
python3 "$TARGET/scripts/vault.py" init --vault "$TARGET" --remember

echo
echo "Verifying the installation:"
python3 "$TARGET/scripts/vault.py" health-check --vault "$TARGET" || true
echo
echo "Done. The vault root is remembered, so you can now run:"
echo "  python3 '$TARGET/scripts/vault.py' status"
echo
echo "Reminder: iCloud provides synchronization only. Keep the vault locally"
echo "available (Finder > right-click > Download Now, or 'brctl download') so"
echo "autonomous processing never runs against cloud-only placeholders."
