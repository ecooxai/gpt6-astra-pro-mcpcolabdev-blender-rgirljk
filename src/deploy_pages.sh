#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p .deploy
if [[ ! -d .deploy/.git ]]; then
 git -C .deploy init -b gh-pages >/dev/null
 git -C .deploy config user.name 'GPT-6 Astra Pro'
 git -C .deploy config user.email 'gpt6-astra-pro@local.invalid'
 git -C .deploy remote add origin https://github.com/ecooxai/gpt6-astra-pro-mcpcolabdev-blender-rgirljk.git
fi
rsync -a --delete --exclude .git --exclude '*.blend1' --exclude '*.tmp' --exclude '*tmp.glb' build/ .deploy/
touch .deploy/.nojekyll
git -C .deploy add .
git -C .deploy diff --cached --quiet || git -C .deploy commit -m 'Publish current Blender study and review journal' >/dev/null
git -C .deploy -c credential.helper= -c 'credential.helper=!gh auth git-credential' push -q -u origin gh-pages
