#!/usr/bin/env bash
set -euo pipefail
export BLENDER_SYSTEM_SCRIPTS=/home/dev/.local/sysroot/usr/share/blender/scripts
export BLENDER_SYSTEM_DATAFILES=/home/dev/.local/sysroot/usr/share/blender/datafiles
export PYTHONPATH=/home/dev/.local/sysroot/usr/lib/python3/dist-packages:${PYTHONPATH:-}
exec /home/dev/.local/sysroot/usr/bin/blender "$@"
