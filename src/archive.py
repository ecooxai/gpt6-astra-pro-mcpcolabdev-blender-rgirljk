from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
import json,time
root=Path(__file__).resolve().parents[1];out=root/'build';dest=out/'downloads/gpt6_astra_pro_mcpcolabdev_blender_rgirljk_source.zip';dest.parent.mkdir(exist_ok=True)
files=[]
for folder in ['src','web','tools','reference']:
    files.extend(p for p in (root/folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts)
for n in ['README.md','Agents.md','review-log.json','package.json','package-lock.json','.gitignore']:
    if (root/n).is_file():files.append(root/n)
with ZipFile(str(dest)+'.tmp','w',ZIP_DEFLATED,compresslevel=6) as z:
    for p in files:z.write(p,p.relative_to(root))
    for p in out.rglob('*'):
        if not p.is_file() or 'downloads' in p.relative_to(out).parts or p.suffix in ['.blend1','.tmp'] or '.tmp.' in p.name:continue
        z.write(p,Path('build')/p.relative_to(out))
Path(str(dest)+'.tmp').replace(dest)
print('ARCHIVE_READY',dest,dest.stat().st_size)
