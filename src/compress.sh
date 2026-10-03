#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
file=build/preview/gpt6_astra_pro_mcpcolabdev_blender_rgirljk.glb
node_modules/.bin/gltf-transform meshopt "$file" build/preview/rgirljk-compressed.tmp.glb
mv build/preview/rgirljk-compressed.tmp.glb "$file"
python3 - <<'PY'
import json
from pathlib import Path
p=Path('build/geometry-audit.json');s=json.loads(p.read_text());s['uncompressedGlbBytes']=s['glbBytes'];s['glbBytes']=Path('build/preview/gpt6_astra_pro_mcpcolabdev_blender_rgirljk.glb').stat().st_size;s['webCompression']='EXT_meshopt_compression';p.write_text(json.dumps(s,indent=2))
PY
