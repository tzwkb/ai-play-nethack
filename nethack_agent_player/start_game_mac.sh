#!/bin/bash
# macOS launcher for nethack_agent_player.
# play.py needs nle (built from source into the local .venv with Python 3.13).
# agent_helper.py only does /tmp file IPC and runs under any python3.
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CHAR="${1:-val-hum-fem-neu}"
exec "$DIR/.venv/bin/python" "$DIR/play.py" "$CHAR"
