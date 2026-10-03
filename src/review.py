import json,sys,shutil,time
from pathlib import Path
root=Path(__file__).resolve().parents[1];out=root/'build'
i=int(sys.argv[1]);score=float(sys.argv[2]);title=sys.argv[3];notes=sys.argv[4]
p=out/'status.json';s=json.loads(p.read_text())
img=out/'preview/gpt6_astra_pro_blender_front.png';rev=out/'reviews'/('iteration-%03d.png'%i)
if img.exists():shutil.copy2(img,rev)
h={'iteration':i,'score':score,'title':title,'notes':notes,'image':str(rev.relative_to(out)),'reviewedAt':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())}
s['history']=[x for x in s.get('history',[]) if x['iteration']!=i]+[h]
s.update(iteration=i,quality=score,stage=notes,version=s.get('version',0)+1,modelVersion=i,views=[n for n in ['front','threequarter','side','back','face'] if (out/'preview'/('gpt6_astra_pro_blender_'+n+'.png')).exists()])
p.write_text(json.dumps(s,indent=2));(root/'review-log.json').write_text(json.dumps(s,indent=2))
print('Recorded actual review',i,score)
