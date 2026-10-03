#!/usr/bin/env bash
set -e
mkdir -p /home/dev/.local/opt
curl -fL --retry 3 https://download.blender.org/release/Blender4.2/blender-4.2.3-linux-x64.tar.xz -o /home/dev/.local/opt/blender-4.2.3-linux-x64.tar.xz
cd /home/dev/.local/opt
tar xf blender-4.2.3-linux-x64.tar.xz
printf 'OFFICIAL_BLENDER_READY\n'
