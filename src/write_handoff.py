import json,time
from pathlib import Path
r=Path(__file__).resolve().parents[1];o=r/'build';s=json.loads((o/'status.json').read_text());g=json.loads((o/'geometry-audit.json').read_text()) if (o/'geometry-audit.json').exists() else {}
t=f'''# Agents.md — R01 continuation handoff

Updated: {time.strftime('%Y-%m-%d %H:%M UTC',time.gmtime())}

## User goal and non-negotiable provenance
Re-create the supplied fully clothed character as an inspectable 3D character using headless Blender in mcp_colabdev. Work from scratch, not existing local/Internet meshes or textures. Do not use image generation. Inspect the reference and render images visually; do not analyze the reference pixels with code. User requested 20,000 actual edit/render/review iterations and a score above 95/100. **Those targets have NOT been met.** Do not claim otherwise or inflate the iteration count.

Reference URL: https://lesswebdisk.my-team-8435.chatgpt.site/raw/u-oKDfM5n2PVKJ/3d/rgirljk/rgirljk.png
Local visual reference: {r}/reference/rgirljk.png

## Actual current reviewed state
- Completed reviewed iterations: {s['iteration']}
- Last visual self-assessment: {s['quality']}/100, subjective and not independently validated.
- Last review: {s['stage']}
- Current generator geometry audit revision: {g.get('revision','pending')} (may be ahead of the last visually reviewed iteration).
- Source is entirely procedural; hidden surfaces are interpretations, not observed reference facts.
- The model is static/posed, not rigged for production animation.

## Paths and environment
- Source: {r}
- Build: {o.resolve()}
- Source build folder is a symlink. To use mcp_colabdev.get_image, set workspace_id to the actual /build directory, not the source directory: otherwise the symlink triggers an escape check.
- Blender: /home/dev/.local/opt/blender-4.2.3-linux-x64/blender (official 4.2.3, denoising works).
- src/blender_official.sh is the launcher. The old distro wrapper is only a fallback and its renderer lacks OpenImageDenoise.
- Branch: gpt6-astra-pro-mcpcolabdev-blender-scratch
- Server: port 8794, src/serve.py, serving only the build directory.
- Public live tunnel: https://contamination-expo-rating-julian.trycloudflare.com
- PID files and complete build logs are in {r}/logs.

## Tool operational notes
Use mcp_colabdev for this environment. The session was ready; no local fallback was used. Terminal records can consume the 32-session limit even after commands finish. Close completed terminals belonging to this project, but DO NOT close the terminal hosting the live server/tunnel (initially terminal 1394) or unrelated projects. `webterm help` documents `stop`, `read` and `write`. Use retained `read ID --full` output after truncation; do not rerun builds just to read logs. Do not print base64. Use get_image for PNG inspection.

## Source and continuation
- src/build_character.py is the authoritative current generator. It contains all model/texture code, original 3D geometry, Cycles setup, source save, evaluated mesh joining/decimation, GLB export, and geometric audit.
- src/render_views.py renders orthographic inspection views. Main generator renders the portrait front view in perspective. Do not accidentally replace the perspective hero by the orthographic front preset unless intended.
- src/compress.sh applies Meshopt to the generated GLB atomically and updates size metadata. Viewer includes MeshoptDecoder. Compression warns about repeating UV coordinates and intentionally preserves those coordinates.
- src/review.py records a real completed review and copies its front PNG into the milestone journal.
- src/browser_test.mjs tests desktop/mobile and captures screenshots. The most recent audit may predate the latest geometry; rerun after final compression.
- web/ holds original HTML, CSS and viewer JS. `npm run bundle`; copy HTML/CSS to build after changing those files.
- Review log: review-log.json and build/status.json. Keep them synchronized.
- Do not reapply refine_003.py / refine_004.py patches: their changes are already in the generator. Git history is the authoritative change record.

## Important checks before claiming improvement
Inspect front, face, side, rear and three-quarter views; specifically check scalp penetration, iris/sclera occlusion, neck/chest seams, collar points, shoulder continuity, sleeves, finger connections, ankle-to-shoe joins, both leg silhouettes, back straps, and skirt/lining intersections. The first two passes had substantial defects, explicitly recorded. Both numerical thigh/shin length tests passed; that alone does not validate visible leg anatomy. Keep subjective likeness score separate from browser QA pass/fail.

## Publish / persistence
The user requested a Git push and public preview. Publish only this project's authored sources and build artifacts, never home-directory/configuration/credential files. Prefer the source branch for code and a gh-pages branch for the static build. The ZIP should include source plus a real build folder (not a broken /build symlink), excluding node_modules, .git, logs, temp files and old .blend1 backups. Update this handoff and the ZIP after the last reviewed pass. Do not imply that 20,000 iterations or the >95 target were reached.
'''
(r/'Agents.md').write_text(t);(o/'Agents.md').write_text(t)
print('Handoff updated:',s['iteration'],s['quality'])
