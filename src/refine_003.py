from pathlib import Path
p=Path('src/build_character.py');s=p.read_text()
s=s.replace('scene.cycles.use_denoising=False','scene.cycles.use_denoising=True')
s=s.replace('def cap_end(t): return 1.20+.91*((1-cos(t))*.5)**.55',"def cap_end(t): return float(np.interp(math.acos(cos(t)),[0,.65,1.05,1.35,1.57,2.2,pi],[1.12,1.14,1.22,1.55,1.80,2.12,2.18]))")
s=s.replace('.0232','.0180').replace('.0082','.0073').replace('.0055)*sin(a)*r','.0048)*sin(a)*r').replace("else -.0055)","else -.0048)")
s=s.replace('r=.0067; cy=face_y(cx,cz)-.0040','r=.0059; cy=face_y(cx,cz)-.0040')
s=s.replace("t=2*pi*j/N;iv.append(H((cx+r*cos(t),cy+.0004,cz+r*sin(t))));iu.append((.5+.5*cos(t),.5+.5*sin(t)))", "t=2*pi*j/N;xx=cx+r*cos(t);zz=cz+r*sin(t)\n        lower=cz-.0048*sqrt(max(0,1-((xx-cx)/.018)**2))+side*(xx-cx)*.07\n        upper=cz+.0073*sqrt(max(0,1-((xx-cx)/.018)**2))+side*(xx-cx)*.07\n        zz=max(lower+.0006,min(upper-.0005,zz))\n        iv.append(H((xx,face_y(xx,zz)-.0040,zz)));iu.append((.5+.5*cos(t),.5+.5*sin(t)))")
s=s.replace("curve('Sleeve compression fold',[(x-sx*.024,y,z+.009),(x,y-.008,z),(x+sx*.024,y+.006,z+.007)],.00065,SEAM)","# Folds are displaced in the sleeve surface itself, not floating curves.\n        pass")
start=s.index('for side in [-1,1]:\n    rows=[]',s.index('# Shaped collar leaves'))
end=s.index('# Small blue embroidered',start)
s=s[:start]+'''# Curved standing collar with an open front.
cv=[];cu=[];cf=[]
for i in range(2):
    for j in range(65):
        a=.55+(2*pi-1.10)*j/64
        cv.append((.023+.040*sin(a),.005-.034*cos(a),1.334-.020*cos(a)-.017*(1-i)))
        cu.append((j/64,i))
for j in range(64):cf.append((j,j+1,j+66,j+65))
co=mesh('Open standing shirt collar',cv,cf,SHIRT,cu,1)
md=co.modifiers.new('Collar band thickness','SOLIDIFY');md.thickness=.0015
for side in [-1,1]:
    top=[(.023+side*.020,-.032,1.310),(.023+side*.038,-.005,1.348),(.023+side*.040,.023,1.343)]
    hem=[(.023+side*.048,-.080,1.254),(.023+side*.070,-.056,1.295),(.023+side*.055,.035,1.329)]
    rows=[]
    for i in range(9):
        t=i/8;row=[]
        for j in range(13):
            u=j/12*2;k=min(int(u),1);a=u-k
            v0=Vector(top[k]).lerp(Vector(top[k+1]),a);v1=Vector(hem[k]).lerp(Vector(hem[k+1]),a)
            q=v0.lerp(v1,t);q.y-=.005*sin(pi*t);row.append(q)
        rows.append(row)
    patch('Folded shirt collar '+str(side),rows,SHIRT)
    curve('Collar fine topstitch',[q+Vector((0,-.0008,0)) for q in rows[-1]],.00030,SEAM)
''' + s[end:]
s=s.replace("(.014,.128,1.185),(.246,.108,.310)","(.014,.128,1.170),(.238,.102,.282)")
s=s.replace("(-.029,.124,1.330),(-.027,.128,1.377),(.055,.128,1.377),(.057,.124,1.330)","(-.029,.124,1.314),(-.027,.128,1.342),(.055,.128,1.342),(.057,.124,1.314)")
s=s.replace(".095,1.327", ".095,1.314").replace(".030,1.329", ".030,1.318")
s=s.replace("[.115,.145,.202]","[.102,.124,.175]").replace("[.084,.088,.097]","[.058,.063,.074]")
s=s.replace("210,2.4,(.80,.88,1.0)","125,2.4,(.80,.88,1.0)")
s=s.replace("420,2.0,(1.0,.95,.86)","285,2.0,(1.0,.95,.86)")
old="bpy.ops.object.camera_add(location=(.06,-4.5,1.48));cam=bpy.context.object;cam.name='Reference portrait camera';scene.camera=cam\ncam.rotation_euler=(Vector((.01,0,.83))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=1.81;cam.data.lens=70"
new="""bpy.ops.object.camera_add(location=(.06,-3.8,1.35));cam=bpy.context.object;cam.name='Reference portrait camera';scene.camera=cam
cam.rotation_euler=(Vector((.015,0,.855))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='PERSP';cam.data.lens=70
# Fit the authored 3D bounds to a portrait camera, never by analyzing reference pixels.
from bpy_extras.object_utils import world_to_camera_view
bpy.context.view_layer.update()
coords=[world_to_camera_view(scene,cam,o.matrix_world@Vector(c)) for o in CHAR.objects for c in o.bound_box]
span=max(p.y for p in coords)-min(p.y for p in coords)
cam.data.lens*=.92/span
"""
if old not in s:raise RuntimeError('Camera source block changed')
s=s.replace(old,new);p.write_text(s)
# Use a simple portable official-binary launcher; distro wrapper remains a documented fallback.
Path('src/blender_official.sh').write_text('#!/usr/bin/env bash\nset -euo pipefail\nexec /home/dev/.local/opt/blender-4.2.3-linux-x64/blender "$@"\n')
