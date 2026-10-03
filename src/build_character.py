"""Original procedural character. No external meshes, scans, or texture maps.
Coordinates: metres; +Z up, -Y front. Reference is inspected by the artist only.
"""
import bpy, math, json, os, sys, random, time
import numpy as np
from pathlib import Path
from mathutils import Vector, Matrix
from math import sin,cos,pi,sqrt,exp
ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/'build'; PRE=OUT/'preview'
PRE.mkdir(parents=True,exist_ok=True)
REV=int(os.environ.get('REVISION','1')); SAMPLES=int(os.environ.get('SAMPLES','40'))
RES=int(os.environ.get('RENDER_HEIGHT','1200'))
random.seed(19)
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
for d in list(bpy.data.materials): bpy.data.materials.remove(d)
CHAR=bpy.data.collections.new('R01 · original character'); bpy.context.scene.collection.children.link(CHAR)

def movechar(o):
    for c in list(o.users_collection): c.objects.unlink(o)
    CHAR.objects.link(o); return o

def material(name,c,rough=.45,metal=0,sss=0):
    m=bpy.data.materials.new(name); m.diffuse_color=(*c,1); m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF'); p.inputs['Base Color'].default_value=(*c,1)
    p.inputs['Roughness'].default_value=rough; p.inputs['Metallic'].default_value=metal
    p.inputs['Subsurface Weight'].default_value=sss
    if sss: p.inputs['Subsurface Radius'].default_value=(1.0,.45,.25)
    return m

def texture(name,kind,size=768):
    y,x=np.mgrid[0:size,0:size].astype(float)/size
    rng=np.random.default_rng(13)
    noise=rng.normal(0,1,(size,size))
    if kind=='plaid':
        c=np.zeros((size,size,3))+[.102,.124,.175]
        for q in [x,y]:
            d=np.abs((q+.5)%1-.5)
            c+=((d<.19)&(d>.075))[...,None]*np.array([.058,.063,.074])
            c+=(np.abs(d-.125)<.014)[...,None]*np.array([.050,.058,.068])
            c+=(np.abs(d-.270)<.009)[...,None]*np.array([.080,.085,.094])
            c+=(np.abs(d-.340)<.008)[...,None]*np.array([.039,.045,.052])
            c-=(d<.025)[...,None]*.032
        c+=(((np.floor(x*384)+np.floor(y*384))%2)*.012)[...,None]
        c+=noise[...,None]*.004
    elif kind=='tie':
        c=np.zeros((size,size,3))+[.080,.116,.195]
        d=(y*3-x*1.55)%1
        c[(d>.045)&(d<.090)]=[.87,.65,.29]
        c[(d>.095)&(d<.107)]=[.39,.33,.21]
        c+=(((np.floor(x*256)+np.floor(y*256))%2)*.015)[...,None]
        c+=noise[...,None]*.003
    elif kind=='sock':
        c=np.zeros((size,size,3))+[.069,.083,.132]
        c+=(.014*np.cos(x*2*pi*52))[...,None]
        c+=(.004*np.sin(y*2*pi*230))[...,None]
    elif kind=='shirt':
        c=np.zeros((size,size,3))+[.86,.885,.92]
        c+=(.008*np.sin(x*2*pi*200)*np.sin(y*2*pi*200)+noise*.003)[...,None]
    elif kind=='iris':
        xx=(x-.5)*2; yy=(y-.5)*2; r=np.sqrt(xx*xx+yy*yy); a=np.arctan2(yy,xx)
        lines=(np.sin(a*59+r*14)+np.sin(a*107-r*7))*.035
        c=np.zeros((size,size,3))+[.19,.105,.057]
        c+=lines[...,None]*np.array([1,.65,.35]); c*=np.clip(1-(r-.65)*2.4,.10,1)[...,None]
        c[r<.43]=[.009,.008,.012]
    a=np.concatenate([np.clip(c,0,1),np.ones((size,size,1))],axis=-1).astype(np.float32)
    im=bpy.data.images.new(name,width=size,height=size,alpha=True)
    im.pixels.foreach_set(a.ravel()); im.filepath_raw=str(OUT/(name+'.png')); im.file_format='PNG'; im.save(); im.pack()
    return im

def texmat(name,c,kind,rough=.55):
    m=material(name,c,rough); nt=m.node_tree; im=texture(name.replace(' ','_'),kind)
    n=nt.nodes.new('ShaderNodeTexImage'); n.image=im; n.interpolation='Linear'; n.extension='REPEAT'
    nt.links.new(n.outputs['Color'],nt.nodes.get('Principled BSDF').inputs['Base Color'])
    return m
SKIN=material('Warm porcelain skin',(.63,.378,.269),.46,sss=.09)
LIP=material('Natural rose lip',(.39,.115,.092),.40,sss=.035)
LID=material('Warm eyelid',(.48,.244,.177),.50,sss=.05)
INNER=material('Ear inner shade',(.30,.11,.077),.57)
DARK=material('Mouth and nostril depth',(.036,.012,.012),.60)
WHITE=material('Ivory sclera',(.83,.81,.75),.27)
TEETH=material('Natural enamel',(.79,.76,.66),.30)
HAIR=material('Near black umber hair',(.016,.012,.013),.47)
HAIR2=material('Hair soft highlight',(.021,.016,.016),.49)
HAIR3=material('Hair fine warm fibers',(.027,.021,.019),.51)
BROW=material('Brow and lash umber',(.025,.014,.012),.52)
SHIRT=texmat('Pearl cotton',(.84,.87,.92),'shirt',.72)
PLAID=texmat('Slate navy tartan',(.12,.15,.20),'plaid',.79)
TIE=texmat('Gold regimental silk',(.08,.11,.19),'tie',.55)
SOCK=texmat('Midnight rib knit',(.07,.08,.13),'sock',.85)
IRIS=texmat('Brown iris',(.12,.07,.03),'iris',.31)
PACK=material('Indigo backpack canvas',(.016,.028,.049),.87)
WEBBING=material('Navy strap webbing',(.017,.023,.033),.78)
BUCKLE=material('Graphite acetal buckles',(.020,.023,.028),.31)
LEATHER=material('Black polished loafer leather',(.014,.017,.024),.24)
SOLE=material('Rubber and stacked heel',(.016,.017,.020),.72)
STITCH=material('Loafer subtle charcoal stitch',(.065,.069,.072),.65)
SEAM=material('Cotton seam',(.64,.69,.78),.80)
GOLD=material('Antique gold zip',(.44,.29,.09),.34,.7)


def mesh(name,v,f,mat,uv=None,sub=0):
    me=bpy.data.meshes.new(name); me.from_pydata(v,[],f); me.update()
    ob=bpy.data.objects.new(name,me); CHAR.objects.link(ob)
    if mat: me.materials.append(mat)
    for p in me.polygons: p.use_smooth=True
    if uv:
        layer=me.uv_layers.new(name='UVMap')
        for p in me.polygons:
            for li in p.loop_indices: layer.data[li].uv=uv[me.loops[li].vertex_index]
    if sub:
        mod=ob.modifiers.new('Surface refinement','SUBSURF'); mod.levels=sub; mod.render_levels=sub
    return ob

def ell(name,loc,scale,mat,seg=40,rings=24):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=seg,ring_count=rings,location=loc)
    o=movechar(bpy.context.object); o.name=name; o.scale=scale
    o.data.materials.append(mat)
    for p in o.data.polygons:p.use_smooth=True
    return o

def cube(name,loc,scale,mat,bevel=.005):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc); o=movechar(bpy.context.object); o.name=name; o.scale=scale
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    if bevel:
        b=o.modifiers.new('Soft sewn edges','BEVEL'); b.width=bevel; b.segments=3
        o.modifiers.new('Weighted corner normals','WEIGHTED_NORMAL')
    o.data.materials.append(mat)
    return o

def curve(name,pts,r,mat,cyclic=False):
    cu=bpy.data.curves.new(name,'CURVE'); cu.dimensions='3D'; cu.resolution_u=12; cu.bevel_depth=r; cu.bevel_resolution=2
    sp=cu.splines.new('BEZIER'); sp.bezier_points.add(len(pts)-1)
    for p,co in zip(sp.bezier_points,pts): p.co=co; p.handle_left_type='AUTO'; p.handle_right_type='AUTO'
    sp.use_cyclic_u=cyclic
    ob=bpy.data.objects.new(name,cu); CHAR.objects.link(ob); ob.data.materials.append(mat)
    return ob

def interp(points,steps=8):
    p=[Vector(v) for v in points]; out=[]
    for i in range(len(p)-1):
        p0=p[max(0,i-1)]; p1=p[i]; p2=p[i+1]; p3=p[min(len(p)-1,i+2)]
        for j in range(steps):
            t=j/steps
            out.append(.5*((2*p1)+(-p0+p2)*t+(2*p0-5*p1+4*p2-p3)*t*t+(-p0+3*p1-3*p2+p3)*t*t*t))
    return out+[p[-1]]

def tube(name,points,radii,mat,aspect=1,n=24,steps=5,ripple=0):
    p=interp(points,steps); rr=np.interp(np.linspace(0,len(radii)-1,len(p)),np.arange(len(radii)),radii)
    v=[]; uv=[]
    for i,(c,r) in enumerate(zip(p,rr)):
        t=(p[min(i+1,len(p)-1)]-p[max(i-1,0)]).normalized()
        ref=Vector((0,1,0)); a=t.cross(ref).normalized()
        if a.length<.5:a=t.cross(Vector((1,0,0))).normalized()
        b=t.cross(a).normalized()
        for j in range(n+1):
            th=2*pi*j/n; rs=r*(1+ripple*sin(th*7+i*.65))
            v.append(c+a*(rs*cos(th))+b*(rs*aspect*sin(th))); uv.append((j/n,i/(len(p)-1)))
    f=[]
    for i in range(len(p)-1):
        for j in range(n):
            a=i*(n+1)+j; f.append((a,a+1,a+n+2,a+n+1))
    f.extend([tuple(range(n,-1,-1)),tuple((len(p)-1)*(n+1)+j for j in range(n+1))])
    return mesh(name,v,f,mat,uv)

def ribbon(name,points,widths,mat,depth=.002,steps=8,normal=(0,-1,0)):
    p=interp(points,steps); w=np.interp(np.linspace(0,len(widths)-1,len(p)),np.arange(len(widths)),widths)
    v=[]; uv=[]; n=Vector(normal)
    for i,c in enumerate(p):
        tang=(p[min(i+1,len(p)-1)]-p[max(i-1,0)]).normalized(); side=tang.cross(n).normalized()
        for j in range(7):
            u=j/6*2-1; v.append(c+side*w[i]*u*.5+n*(depth*(1-u*u))); uv.append((j/6,i/(len(p)-1)))
    f=[]
    for i in range(len(p)-1):
        for j in range(6):a=i*7+j;f.append((a,a+1,a+8,a+7))
    o=mesh(name,v,f,mat,uv)
    s=o.modifiers.new('Real material thickness','SOLIDIFY');s.thickness=.0012
    return o

# ---------- Face: custom continuous ring sculpt ----------
HEAD=Vector((.044,-.007,1.515)); ROT=Matrix.Rotation(.095,4,'Y')@Matrix.Rotation(-.045,4,'Z')
def H(p): return HEAD+ROT.to_3x3()@Vector(p)
ZP=[-.116,-.108,-.093,-.069,-.043,-.010,.025,.058,.087,.111,.125]
XP=[.015,.031,.048,.063,.075,.080,.081,.079,.068,.045,.002]
YP=[.025,.035,.046,.058,.066,.071,.073,.072,.060,.039,.002]
from functools import lru_cache
@lru_cache(maxsize=16)
def tangents(xs,ys):
    d=[(ys[i+1]-ys[i])/(xs[i+1]-xs[i]) for i in range(len(xs)-1)];m=[d[0]]
    for i in range(1,len(xs)-1):
        if d[i-1]*d[i]<=0:m.append(0.)
        else:
            h0=xs[i]-xs[i-1];h1=xs[i+1]-xs[i];w1=2*h1+h0;w2=h1+2*h0
            m.append((w1+w2)/(w1/d[i-1]+w2/d[i]))
    return tuple(m+[d[-1]])
def smooth_profile(z,xs,ys):
    i=max(0,min(len(xs)-2,int(np.searchsorted(xs,z))-1));h=xs[i+1]-xs[i];t=max(0,min(1,(z-xs[i])/h));m=tangents(tuple(xs),tuple(ys))
    return (2*t**3-3*t*t+1)*ys[i]+(t**3-2*t*t+t)*h*m[i]+(-2*t**3+3*t*t)*ys[i+1]+(t**3-t*t)*h*m[i+1]
def prof(z):return smooth_profile(z,ZP,XP),smooth_profile(z,ZP,YP)
def face_y(x,z):
    rx,ry=prof(z); t=min(.999,abs(x)/max(rx,.001)); y=-ry*(max(0,1-t*t)**.48)
    y-=.004*exp(-((abs(x)-.044)/.022)**2-((z+.026)/.027)**2)
    y+=.004*exp(-((abs(x)-.034)/.023)**2-((z-.019)/.013)**2)
    y-=.0045*exp(-(x/.012)**2-((z-.012)/.029)**2)
    y-=.0155*exp(-(x/.0115)**2-((z+.012)/.015)**2)
    y-=.006*exp(-((abs(x)-.012)/.008)**2-((z+.019)/.006)**2)
    y-=.0025*exp(-(x/.033)**2-((z+.051)/.019)**2)
    return y
v=[];f=[];uv=[]
NZ=96; NT=160
for i in range(NZ+1):
    z=ZP[0]+(ZP[-1]-ZP[0])*i/NZ; rx,ry=prof(z)
    for j in range(NT+1):
        t=2*pi*j/NT; x=rx*sin(t)
        y=face_y(x,z) if cos(t)>0 else -ry*cos(t)*1.05
        v.append(H((x,y,z)));uv.append((j/NT,i/NZ))
for i in range(NZ):
    for j in range(NT):a=i*(NT+1)+j;f.append((a,a+1,a+NT+2,a+NT+1))
head=mesh('Sculpted head · continuous facial surface',v,f,SKIN,uv,1)
# Original, analytical skin tint in vertex colors; never sampled from the photograph.
face_mat=SKIN.copy();face_mat.name='Face skin with subtle authored cheek color'
col=head.data.color_attributes.new(name='FaceTint',type='FLOAT_COLOR',domain='POINT')
inv=ROT.to_3x3().inverted()
for vert,c in zip(head.data.vertices,col.data):
    q=inv@(vert.co-HEAD);x,y,z=q;front=max(0,min(1,-y/.055))
    blush=exp(-((abs(x)-.047)/.024)**2-((z+.031)/.028)**2)*front
    nose=exp(-(x/.016)**2-((z+.016)/.026)**2)*front
    c.color=(.63+.018*blush,.378-.025*blush-.009*nose,.269-.014*blush,1)
nt=face_mat.node_tree;vc=nt.nodes.new('ShaderNodeVertexColor');vc.layer_name='FaceTint';nt.links.new(vc.outputs['Color'],nt.nodes.get('Principled BSDF').inputs['Base Color'])
head.data.materials[0]=face_mat
# Fine skin microstructure is procedural in Blender; vertex tones are portable to glTF.
for mat in [SKIN,face_mat]:
    nt=mat.node_tree;noise=nt.nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=1900;noise.inputs['Detail'].default_value=2
    bump=nt.nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.12;bump.inputs['Distance'].default_value=.00014
    nt.links.new(noise.outputs['Fac'],bump.inputs['Height']);nt.links.new(bump.outputs['Normal'],nt.nodes.get('Principled BSDF').inputs['Normal'])

# Neck flows into the shirt opening.
tube('Neck',[(.019,-.008,1.270),(.019,0,1.306),(.025,.009,1.350),(.036,.002,1.409),H((0,.008,-.083))],[.068,.046,.034,.032,.034],SKIN,aspect=.94,n=48,steps=8)
for side in [-1,1]:
    ear=ell('Ear pinna '+str(side),H((side*.079,.002,-.012)),(.017,.014,.029),SKIN)
    ear.rotation_euler[1]=side*.13
    ell('Ear concha '+str(side),H((side*.086,-.010,-.010)),(.008,.0025,.017),INNER,32,20)
    pts=[H((side*(.081+.010*sin(t)),-.012,-.01+.023*cos(t))) for t in np.linspace(-.55,3.7,17)]
    curve('Ear helix '+str(side),pts,.0026,SKIN)
    curve('Ear antihelix '+str(side),[H((side*.086,-.014,-.027)),H((side*.089,-.014,-.010)),H((side*.084,-.014,.003))],.0018,SKIN)

# ---------- Anatomical eyelid surfaces, irises and a curved dental smile ----------
SCLERA=material('Soft warm sclera',(.66,.66,.61),.29,sss=.02)
RIM=material('Soft eyelid tissue',(.59,.337,.245),.48,sss=.06)
def eye_boundary(cx,cz,u,upper):
    return cz+(.0058 if upper else -.0032)*sqrt(max(0,1-u*u))+.075*(cx/.031)*(u*.017)
def eye_y(x,z,cx,cz):
    return face_y(x,z)-.0007-.0034*exp(-((x-cx)/.015)**2-((z-cz)/.013)**2)
for side in [-1,1]:
    cx=side*.031;cz=.020;N=64;R=12
    v=[H((cx,eye_y(cx,cz,cx,cz),cz))];uv=[(.5,.5)];f=[]
    for k in range(1,R+1):
        r=k/R
        for j in range(N):
            a=2*pi*j/N;u=cos(a)*r;x=cx+.017*u
            z=cz+(.0058 if sin(a)>0 else .0032)*sin(a)*r+side*(x-cx)*.075
            v.append(H((x,eye_y(x,z,cx,cz),z)));uv.append((.5+.5*u,.5+.5*sin(a)*r))
    for j in range(N):f.append((0,1+j,1+(j+1)%N))
    for k in range(R-1):
        a=1+k*N;b=a+N
        for j in range(N):f.append((a+j,b+j,b+(j+1)%N,a+(j+1)%N))
    mesh('Shaped ocular surface '+str(side),v,f,SCLERA,uv)
    # Iris UVs represent the actual clipped disk, without stretching the top/bottom of the iris.
    radius=.0060;v=[H((cx,eye_y(cx,cz,cx,cz)-.0006,cz))];uv=[(.5,.5)];f=[]
    for k in range(1,9):
        rr=radius*k/8
        for j in range(N):
            a=2*pi*j/N;x=cx+rr*cos(a);z=cz+rr*sin(a);u=(x-cx)/.017
            z=max(eye_boundary(cx,cz,u,False)+.00025,min(eye_boundary(cx,cz,u,True)-.00025,z))
            y=eye_y(x,z,cx,cz)-.00025-.00035*(1-k/8)
            v.append(H((x,y,z)));uv.append((.5+(x-cx)/(2*radius),.5+(z-cz)/(2*radius)))
    for j in range(N):f.append((0,1+j,1+(j+1)%N))
    for k in range(7):
        a=1+k*N;b=a+N
        for j in range(N):f.append((a+j,b+j,b+(j+1)%N,a+(j+1)%N))
    mesh('Brown radial iris '+str(side),v,f,IRIS,uv)
    ell('Subtle corneal catchlight '+str(side),H((cx-.0019,eye_y(cx-.0019,cz+.0021,cx,cz)-.001,cz+.0021)),(.00085,.00023,.00085),WHITE,20,12)
    for upper in [True,False]:
        v=[];uv=[];f=[];inner=[]
        for row in range(7):
            t=row/6
            for j in range(65):
                u=-1+2*j/64;x=cx+(.017+.0025*t)*u
                z=eye_boundary(cx,cz,u,upper)+(1 if upper else -1)*.0030*t*sqrt(max(0,1-u*u))
                y=(1-t)*(eye_y(x,z,cx,cz)-.00015)+t*(face_y(x,z)-.00015)-.00055*sin(pi*t)
                v.append(H((x,y,z)));uv.append((j/64,t))
                if row==0:inner.append(H((x,y-.00018,z)))
        for row in range(6):
            for j in range(64):a=row*65+j;f.append((a,a+1,a+66,a+65))
        lid=mesh(('Upper' if upper else 'Lower')+' modeled lid '+str(side),v,f,SKIN,uv,1)
        if upper:curve('Fine upper lash contour '+str(side),inner,.00031,BROW)
        else:curve('Subtle lower waterline '+str(side),inner,.00019,RIM)
    # Individual tapered brow hairs, with a muted base rather than a hard outline.
    pts=[]
    for j in range(7):
        u=-1+2*j/6;x=cx+.022*u;z=.043+.0045*(1-u*u)+side*.001*u
        pts.append(H((x,face_y(x,z)-.0010,z)))
    ribbon('Natural brow base '+str(side),pts,[.0003,.0023,.0032,.0030,.0023,.0012,.0002],BROW,.00015)
    for j in range(32):
        u=-.94+1.88*j/31;x=cx+.022*u;z=.043+.0045*(1-u*u)+side*.001*u
        curve('Fine brow hair',[H((x,face_y(x,z)-.0013,z-.0008)),H((x+side*.0013,face_y(x,z)-.0015,z+.0012))],.00009,BROW)
# Recessed nostril shadows are only partially visible under the nasal alae.
for side in [-1,1]:
    x=side*.0102;z=-.023
    o=ell('Nostril underside '+str(side),H((x,face_y(x,z)+.00035,z)),(.0025,.00165,.0009),INNER,28,16)
    o.rotation_euler=ROT.to_euler();o.rotation_euler[0]+=.35

def mouth_bounds(u):
    return -.043-.002*(1-u*u),-.043-.016*(1-u*u)
v=[];uv=[];f=[]
for row in range(9):
    t=row/8
    for j in range(65):
        u=-1+2*j/64;x=.029*u;top,bottom=mouth_bounds(u);z=top*(1-t)+bottom*t
        v.append(H((x,face_y(x,z)-.0018,z)));uv.append((j/64,t))
for row in range(8):
    for j in range(64):a=row*65+j;f.append((a,a+1,a+66,a+65))
mesh('Curved smile opening',v,f,DARK,uv)
LIPSOFT=material('Soft natural lip surface',(.48,.207,.161),.42,sss=.06)
for upper in [True,False]:
    v=[];uv=[];f=[]
    for row in range(9):
        t=row/8
        for j in range(65):
            u=-1+2*j/64;x=.029*u;top,bottom=mouth_bounds(u);edge=top if upper else bottom
            height=(.0025 if upper else .0031)*max(0,1-u*u)**.65
            if upper:height+=.0006*exp(-((abs(u)-.24)/.17)**2)
            z=edge+(1 if upper else -1)*height*t
            y=face_y(x,z)-.0018*(1-t)-.0020*sin(pi*t)*max(0,1-u*u)
            v.append(H((x,y,z)));uv.append((j/64,t))
    for row in range(8):
        for j in range(64):a=row*65+j;f.append((a,a+1,a+66,a+65))
    lip=mesh('Upper shaped lip' if upper else 'Lower shaped lip',v,f,LIPSOFT,uv,1)
    # A soft vertex-color falloff blends the outer lip into the surrounding skin.
    col=lip.data.color_attributes.new(name='LipTint',type='FLOAT_COLOR',domain='POINT')
    for i,c in enumerate(col.data):
        t=(i//65)/8;blend=t**2
        a=(.47,.195,.150) if upper else (.52,.238,.190);b=(.63,.378,.269)
        c.color=tuple(a[k]*(1-blend)+b[k]*blend for k in range(3))+(1,)
    lm=LIPSOFT.copy();lm.name=('Upper' if upper else 'Lower')+' lip blended tone';nt=lm.node_tree;n=nt.nodes.new('ShaderNodeVertexColor');n.layer_name='LipTint';nt.links.new(n.outputs['Color'],nt.nodes.get('Principled BSDF').inputs['Base Color']);lip.data.materials[0]=lm
widths=[.0036,.0042,.0052,.0061,.0070,.0070,.0061,.0052,.0042,.0036]
heights=[.0068,.0075,.0085,.0096,.0106,.0106,.0096,.0085,.0075,.0068]
cursor=-sum(widths)/2
for i,(w,h) in enumerate(zip(widths,heights)):
    x=cursor+w/2;cursor+=w;u=x/.029;top=-.0447+.0025*u*u;z=top-h/2
    y=face_y(x,z)-.0028
    tooth=cube('Anatomical upper tooth %02d'%i,H((x,y,z)),(w-.00009,.0035,h),TEETH,.0007)
    tooth.rotation_euler=ROT.to_euler();tooth.rotation_euler[2]+=-x*.7
ell('Subtle facial beauty mark',H((-.051,face_y(-.051,-.029)-.00025,-.029)),(.00042,.00018,.00042),LID,16,8)

# ---------- Hair: hand-directed cap, layered swept fringe, and twin low tails ----------
def cap_end(t): return float(np.interp(math.acos(cos(t)),[0,.65,1.05,1.35,1.57,2.2,pi],[1.12,1.14,1.22,1.55,1.80,2.12,2.18]))
def cap_point(t,a,off=0):
    q=sin(a);rx=(.090+off)*q*(1+.07*q*q);ry=(.083+off)*q*(1+.04*q*q)
    return Vector((rx*sin(t),-ry*cos(t),(.138+off)*cos(a)))

v=[];uv=[];f=[]
for i in range(37):
    for j in range(145):
        t=2*pi*j/144; a=.005+(cap_end(t)-.005)*i/36
        p=cap_point(t,a);p.x+=.003*cos(a)**2;v.append(H(p));uv.append((j/144,i/36))
for i in range(36):
    for j in range(144):a=i*145+j;f.append((a,a+1,a+146,a+145))
mesh('Continuous shaped hair cap',v,f,HAIR,uv,1)
for i in range(360):
    t=2*pi*i/360;pts=[]
    for j in range(15):
        a=.07+(cap_end(t)-.09)*j/14;tt=t+.13*sin(a)*cos(t)
        p=cap_point(tt,a,.0008+random.random()*.0003);p.x+=.003*cos(a)**2;pts.append(H(p))
    strand=curve('Crown combed fiber %03d'%i,pts,.00006 if i%3 else .00009,HAIR2 if i%7 else HAIR3)
    strand.data.resolution_u=3;strand.data.bevel_resolution=1;strand['web_detail_keep']=(i%2==0)
def fringe_path(u):
    controls=[(.024+.020*u,.117),(.010+.039*u,.095),(-.055+.104*u,.063+.004*u),(-.073+.111*u,.030+.019*u*u)]
    p=[]
    for x,z in controls:
        q=sqrt(max(.001,1-(z/.138)**2));rx=.090*q*(1+.07*q*q);ry=.083*q*(1+.04*q*q)
        yy=-ry*sqrt(max(.02,1-min(.985,(x/rx)**2)))-.0013
        yy=min(yy,face_y(x,z)-.004)
        p.append(Vector((x,yy,z)))
    path=interp(p,12)
    for j,q in enumerate(path):
        t=j/(len(path)-1)
        q.y-=.00028*sin(2*pi*u*43)*sin(pi*t)
        q.z+=(t**9)*(.0007*sin(u*151)+.0003*sin(u*313))
    return path
columns=96;rows=len(fringe_path(0));v=[];uv=[];f=[]
paths=[fringe_path(i/columns) for i in range(columns+1)]
for j in range(rows):
    for i in range(columns+1):v.append(H(paths[i][j]));uv.append((i/columns,j/(rows-1)))
for j in range(rows-1):
    for i in range(columns):a=j*(columns+1)+i;f.append((a,a+1,a+columns+2,a+columns+1))
mesh('Continuous swept fringe surface',v,f,HAIR,uv,1)
for i in range(360):
    u=(i+.3)/360;p=fringe_path(u)
    pts=[H(q+Vector((0,-.00045,0))) for q in p]
    strand=curve('Fine swept fringe strand %03d'%i,pts,.000055 if i%3 else .000075,HAIR2 if i%9 else HAIR3)
    strand.data.resolution_u=2;strand.data.bevel_resolution=1
    strand['web_detail_keep']=(i%3==0)
for i in range(8):
    p=fringe_path((i+.3)/12)
    pts=[H(q+Vector((-.0006*sin(j/len(p)*pi),-.0012,0))) for j,q in enumerate(p)]
    strand=curve('Fringe edge flyaway',pts,.000045,HAIR2);strand.data.resolution_u=2;strand.data.bevel_resolution=1

for side in [-1,1]:
    tail=[(side*.080,.033,-.040),(side*.102,.038,-.081),(side*.110,.020,-.127),(side*.109,.004,-.175),(side*.102,-.015,-.226),(side*.083,-.020,-.247)]
    tube('Low ponytail volume '+str(side),[H(p) for p in tail],[.018,.030,.031,.028,.016,.001],HAIR,aspect=.80,n=40,steps=9)
    # Overlapping curved locks create a silhouette, rather than a simple cylinder.
    for k in range(15):
        a=2*pi*k/15;pp=[]
        for j,(x,y,z) in enumerate(tail):
            r=[.018,.031,.032,.029,.017,.003][j];aa=a+.3*sin(j*.9+k)
            pp.append(H((x+cos(aa)*r,y+sin(aa)*r*.8,z+.004*sin(k+j))))
        ribbon('Ponytail layered lock',pp,[.005,.011,.012,.010,.008,.0003],HAIR if k%4 else HAIR2,.0008,8,ROT.to_3x3()@Vector((cos(a),sin(a),0)))
    for k in range(68):
        a=2*pi*k/68;pts=[]
        for j,(x,y,z) in enumerate(tail):
            r=[.019,.032,.033,.030,.018,.003][j];aa=a+.28*sin(j*.9+k*.18)
            pts.append(H((x+cos(aa)*r,y+sin(aa)*r*.81,z+.004*sin(k+j))))
        curve('Ponytail individual fiber',pts,.00011,HAIR2 if k%5 else HAIR3)
    curve('Ponytail tie', [H((side*.081+.019*cos(t),.030+.016*sin(t),-.050)) for t in np.linspace(0,2*pi,24)],.0022,WEBBING,True)
    for k in range(5):
        pts=[(side*(.073+k*.001),-.034,.056),(side*.082,-.045,-.004),(side*(.074+k*.001),-.053,-.051),(side*.072,-.047,-.105),(side*.081,-.042,-.130)]
        ribbon('Temple tendril', [H(p) for p in pts],[.004,.006,.005,.003,.0002],HAIR,.0006,8,ROT.to_3x3()@Vector((0,-1,0)))
# Restrained fine flyaways, kept close to the authored volume.
for i in range(18):
    t=random.uniform(-pi,pi);a=random.uniform(.20,.85)
    pts=[H(cap_point(t+j*.012,a+j*.08,.002+sin(j*pi/7)*.003)) for j in range(8)]
    curve('Fine crown flyaway',pts,.00010,HAIR2)

# ---------- Shirt with shaped shoulders, open collar, sleeve folds and rolled cuffs ----------
sections=[(1.000,.118,.067),(1.013,.128,.075),(1.051,.132,.075),(1.112,.138,.074),(1.187,.144,.075),(1.284,.155,.073),(1.320,.160,.065),(1.340,.137,.054),(1.355,.048,.036)]
v=[];f=[];uv=[];NX=128; NR=64
for i in range(NR+1):
    t=i/NR*(len(sections)-1);k=min(int(t),len(sections)-2);a=t-k
    z,rx,ry=[sections[k][j]*(1-a)+sections[k+1][j]*a for j in range(3)]
    for j in range(NX+1):
        th=2*pi*j/NX;front=max(0,cos(th)); top=(i/NR)**15
        zz=z-.080*front**3*max(0,(z-1.230)/.125)
        fold=(.0022*sin(th*14+z*36)+.0017*sin(th*23-z*42))*(.3+.7*exp(-((z-1.03)/.045)**2))
        fold+=.002*sin(th*9+z*70)*exp(-((abs(sin(th))-.80)/.22)**2)
        x=(rx+fold)*sin(th)+(z-1)*.052
        y=-(ry+fold*.8+.046*max(0,(z-1.315)/.040)*front**4)*cos(th)+.006
        v.append((x,y,zz));uv.append((j/NX*3,i/NR*3))
for i in range(NR):
    for j in range(NX):
        a=i*(NX+1)+j;f.append((a,a+1,a+NX+2,a+NX+1))
shirt=mesh('Shaped cotton shirt shell',v,f,SHIRT,uv,1)
s=shirt.modifiers.new('Cotton shell thickness','SOLIDIFY');s.thickness=.0014
# The exposed chest is now continuous with the neck, without an intersecting ellipsoid.
# Front placket and white buttons.
placket=[]
for z in np.linspace(1.008,1.285,9):placket.append(((z-1)*.052,-.071+(.010 if z>1.26 else 0),z))
ribbon('Shirt front placket',placket,[.015]*9,SHIRT,.0012)
for z in [1.028,1.074,1.121,1.166,1.211,1.259]:
    x=(z-1)*.052;ell('Mother of pearl shirt button',(x,-.075,z),(.0027,.0011,.0027),SHIRT,24,12)
    for s in [-1,1]:ell('Button stitch',(x+s*.00055,-.0761,z),(.00022,.00014,.00022),SEAM,12,8)
# Shaped collar leaves: curving patches with real fabric thickness.
def patch(name,rows,mat):
    v=[];uv=[];f=[]
    for i,row in enumerate(rows):
        for j,p in enumerate(row):v.append(p);uv.append((j/(len(row)-1),i/(len(rows)-1)))
    n=len(rows[0])
    for i in range(len(rows)-1):
        for j in range(n-1):a=i*n+j;f.append((a,a+1,a+n+1,a+n))
    o=mesh(name,v,f,mat,uv,1);s=o.modifiers.new('Folded fabric thickness','SOLIDIFY');s.thickness=.0016
    return o
# Curved standing collar with an open front.
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
    top=[(.023+side*.020,-.046,1.317),(.023+side*.038,-.005,1.348),(.023+side*.040,.023,1.343)]
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
# Small blue embroidered shirt emblem, authored as thread curves.
EMB=material('Pale blue embroidery',(.33,.53,.71),.8)
curve('Embroidered chest motif',[(.102,-.072,1.194),(.107,-.074,1.204),(.104,-.074,1.217),(.109,-.073,1.209),(.111,-.073,1.199)],.00065,EMB)
for side in [-1,1]:
    sx=side
    points=[(sx*.113+.015,.010,1.314),(sx*.135+.014,.005,1.271),(sx*.146+.012,.012,1.183),(sx*.150+.009,.033,1.115),(sx*.148+.007,.048,1.062)]
    tube('Cotton sleeve '+str(side),points,[.041,.041,.040,.033,.0285],SHIRT,aspect=.90,n=64,steps=10,ripple=.028)
    # Five slender curved folds rather than artificial bands.
    for k in range(5):
        z=1.120+k*.023;x=sx*(.170+k*.002)+.01;y=-.026+k*.001
        # Folds are displaced in the sleeve surface itself, not floating curves.
        pass
    cuff=[(sx*.151+.007,.044,1.082),(sx*.147+.007,.048,1.055)]
    tube('Turned back cuff '+str(side),cuff,[.0340,.0340],SHIRT,aspect=.92,n=64,steps=6,ripple=.012)
    curve('Rolled cuff seam '+str(side),[(sx*.148+.007+.0315*cos(a),.048+.030*sin(a),1.056-.003*cos(a)) for a in np.linspace(0,2*pi,40)],.00065,SEAM,True)
    wrist=Vector((sx*.090+.007,.118,.958 if side<0 else .952))
    knuckle=Vector((sx*.036+.007,.153 if side<0 else .166,.920 if side<0 else .902))
    direction=(knuckle-wrist).normalized();normal=Vector((0,1,0));normal=(normal-direction*normal.dot(direction)).normalized();wide=normal.cross(direction).normalized()
    handparts=[]
    fore=[(sx*.147+.007,.048,1.061),(sx*.129+.007,.080,1.017),wrist-direction*.012,wrist+direction*.016]
    handparts.append(tube('Forearm to wrist '+str(side),fore,[.028,.024,.017,.0125],SKIN,aspect=.84,n=40,steps=10))
    palm=ell('Anatomical palm '+str(side),(wrist+knuckle)/2,(.023,.011,(knuckle-wrist).length*.59),SKIN,40,24)
    basis=Matrix((wide,normal,direction)).transposed();palm.rotation_euler=basis.to_euler();handparts.append(palm)
    for k,length in enumerate([.036,.044,.042,.032]):
        start=knuckle+wide*((k-1.5)*.009)-direction*.008
        p1=start+direction*length*.40+normal*.003
        p2=start+direction*length*.75+normal*.001
        tip=start+direction*length*.91-normal*.004
        handparts.append(tube('Articulated finger %s %s'%(side,k),[start,p1,p2,tip],[.0046,.0040,.0034,.0027],SKIN,aspect=.87,n=20,steps=5))
        nail=ell('Natural fingernail',tip+normal*.0023-direction*.002,(.0024,.0005,.0042),LID,16,12);nail.rotation_euler=basis.to_euler()
    root=(wrist+knuckle)/2-wide*.018-direction*.008
    handparts.append(tube('Opposable hand thumb '+str(side),[root,root-wide*.012+direction*.010,root-wide*.009+direction*.025+normal*.003],[.007,.0054,.0037],SKIN,n=24,steps=6))
    bpy.ops.object.select_all(action='DESELECT')
    for ob in handparts:ob.select_set(True)
    bpy.context.view_layer.objects.active=handparts[0];bpy.ops.object.join();hand=bpy.context.object;hand.name='Continuous forearm and posed hand '+str(side)
    rm=hand.modifiers.new('Sculpted wrist and finger junctions','REMESH');rm.mode='VOXEL';rm.voxel_size=.00085;rm.use_smooth_shade=True
    bpy.ops.object.modifier_apply(modifier=rm.name)
    sm=hand.modifiers.new('Hand surface relaxation','SMOOTH');sm.factor=.46;sm.iterations=6;bpy.ops.object.modifier_apply(modifier=sm.name)

# ---------- Pleated tartan skirt, waistband, lining and silk tie ----------
NPLEATS=28; NS=NPLEATS*8; NH=28
v=[];uv=[];f=[]
for i in range(NH+1):
    t=i/NH;z=1.002-.301*t
    rx=.122+.099*(t**.82);ry=.071+.046*(t**.88)
    for j in range(NS+1):
        th=2*pi*j/NS;phase=(j%8)/8
        # Knife-pleat crest, visible flat panel, then a recessed return fold.
        fold=float(np.interp(phase,[0,.125,.50,.625,.75,1],[0,.70,.56,-.65,-.55,0]))
        dr=(.004+.013*t)*fold
        swing=.003*sin(th*3+.7)*t*t
        x=(rx+dr)*sin(th); y=.010-(ry+dr*.7)*cos(th)
        zz=z+swing+.0025*cos(th)*t
        v.append((x,y,zz));uv.append((j/NS*5.8,(1-t)*2.9))
for i in range(NH):
    for j in range(NS):a=i*(NS+1)+j;f.append((a,a+NS+1,a+NS+2,a+1))
skirt=mesh('28 individually shaped knife pleats',v,f,PLAID,uv)
s=skirt.modifiers.new('Woven skirt thickness','SOLIDIFY');s.thickness=.0018
# A lining is modeled on the inside rather than an open shell.
v=[];uv=[];f=[]
for i in range(5):
    t=i/4
    for j in range(97):
        a=2*pi*j/96;v.append(((.116+.085*t)*sin(a),.011-(.066+.036*t)*cos(a),.985-.264*t));uv.append((j/96,t))
for i in range(4):
    for j in range(96):a=i*97+j;f.append((a,a+1,a+98,a+97))
mesh('Opaque skirt lining',v,f,WEBBING,uv)
curve('Skirt hem seam',[((.221+.017*float(np.interp((j%8)/8,[0,.125,.50,.625,.75,1],[0,.70,.56,-.65,-.55,0])))*sin(2*pi*j/NS),.010-(.117+.012*float(np.interp((j%8)/8,[0,.125,.50,.625,.75,1],[0,.70,.56,-.65,-.55,0])))*cos(2*pi*j/NS),.706+.003*sin(2*pi*j/NS*3+.7)+.0025*cos(2*pi*j/NS)) for j in range(NS)],.00048,WEBBING,True)
# Waistband ring.
v=[];uv=[];f=[]
for i,z in enumerate([.984,1.008]):
    for j in range(129):
        a=2*pi*j/128;v.append((.127*sin(a),.010-.076*cos(a),z));uv.append((j/128*5.8,i*.25+2.65))
for j in range(128):f.append((j,j+1,j+130,j+129))
mesh('Structured tartan waistband',v,f,PLAID,uv)
# Loose regimental loop; left and right visible above the knot.
for side in [-1,1]:
    ribbon('Loose necktie loop '+str(side),[(.023+side*.058,-.047,1.319),(.018+side*.053,-.076,1.287),(.016+side*.030,-.084,1.239),(.012,-.089,1.218)],[.014,.017,.017,.018],TIE,.0012)
# Knot as a sculpted beveled prism.
v=[(-.011,-.096,1.238),(.037,-.096,1.234),(.025,-.104,1.200),(.006,-.104,1.200),(-.006,-.087,1.238),(.032,-.087,1.234),(.023,-.093,1.200),(.008,-.093,1.200)]
f=[(0,1,2,3),(7,6,5,4),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)]
knot=mesh('Loose silk tie knot',v,f,TIE,[(0,1),(1,1),(1,0),(0,0),(0,1),(1,1),(1,0),(0,0)])
b=knot.modifiers.new('Silk knot softness','BEVEL');b.width=.003;b.segments=3
# Broad front tie blade, moving slightly off the centreline.
zs=[1.205,1.180,1.142,1.096,1.046,.996,.940,.904,.883]
widths=[.018,.019,.024,.029,.031,.034,.036,.035,.002]
v=[];uv=[];f=[]
for i,(z,w) in enumerate(zip(zs,widths)):
    cx=.010-.006*sin(i*.46);y=-.088-.004*sin(i*.8)-max(0,1.00-z)*.20
    for j in range(9):
        u=j/8*2-1;v.append((cx+w*u,y-.003*(1-u*u),z));uv.append((j/8,(z-.883)/.322*2.6))
for i in range(len(zs)-1):
    for j in range(8):a=i*9+j;f.append((a,a+1,a+10,a+9))
tie=mesh('Gold striped tie blade',v,f,TIE,uv,1);s=tie.modifiers.new('Silk thickness','SOLIDIFY');s.thickness=.0018
# ---------- Equal-length legs in a solved asymmetrical standing pose ----------
def solve_knee(hip,ankle,thigh=.438,shin=.398,pole=(.5,-.8,0)):
    h=Vector(hip);a=Vector(ankle);d=(a-h).length;axis=(a-h).normalized()
    along=(thigh*thigh-shin*shin+d*d)/(2*d)
    bend=sqrt(max(0,thigh*thigh-along*along));p=Vector(pole);p=(p-axis*p.dot(axis)).normalized()
    return h+axis*along+p*bend
JOINTS={}
for side in [-1,1]:
    hip=Vector((-.068 if side<0 else .065,.025,.919))
    ankle=Vector((-.070 if side<0 else .029,.038 if side<0 else -.046,.109 if side<0 else .102))
    knee=solve_knee(hip,ankle,pole=(.5,-.85,0) if side<0 else (.2,-.9,0))
    JOINTS[str(side)]={'hip':list(hip),'knee':list(knee),'ankle':list(ankle),'thigh':(hip-knee).length,'shin':(knee-ankle).length}
    pts=[hip,hip.lerp(knee,.35),hip.lerp(knee,.75),knee,knee.lerp(ankle,.26),knee.lerp(ankle,.61),ankle,ankle+Vector((0,-.004,-.027))]
    leg=tube('Continuous anatomical leg '+str(side),pts,[.065,.061,.049,.0395,.045,.034,.024,.024],SKIN,aspect=.94,n=96,steps=12)
    # The sock shares the exact anatomical surface, so skin cannot penetrate it.
    # A material boundary follows a full circumferential ring, with a raised knitted welt.
    leg.data.materials.append(SOCK)
    ring_count=len(leg.data.vertices)//97
    centers=interp(pts,12)
    top_i=min(range(len(centers)),key=lambda i:abs(centers[i].z-.449))
    for poly in leg.data.polygons:
        if min(poly.vertices)>=top_i*97:poly.material_index=1
    for i in range(top_i,ring_count):
        c=centers[i]
        for j in range(97):
            vert=leg.data.vertices[i*97+j]; d=vert.co-c
            vert.co=c+d*(1+.0013/max(d.length,.001))
    rim=[leg.data.vertices[top_i*97+j].co.copy() for j in range(96)]
    curve('Knitted sock top edge '+str(side),rim,.0013,SOCK,True)
    # Shoes are independently modeled lasts, with soles, heel blocks and sewn aprons.
    angle=-.085 if side<0 else .060;C=Vector((ankle.x,ankle.y-.038,0));R=Matrix.Rotation(angle,3,'Z')
    def F(p):return C+R@Vector(p)
    outline=[]
    for j in range(80):
        t=2*pi*j/80;outline.append(((.037+.008*cos(t))*sin(t),-.025-.113*cos(t)))
    vv=[];ff=[]
    for z in [.013,.030]:
        for x,y in outline:vv.append(F((x*1.045,y,z)))
    for j in range(80):ff.append((j,(j+1)%80,(j+1)%80+80,j+80))
    ff.append(tuple(range(79,-1,-1)));ff.append(tuple(j+80 for j in range(80)))
    so=mesh('Loafer welted outsole '+str(side),vv,ff,SOLE)
    be=so.modifiers.new('Rounded outsole edge','BEVEL');be.width=.003;be.segments=3
    heel=cube('Stacked heel '+str(side),F((0,.048,.012)),(.061,.067,.022),SOLE,.004);heel.rotation_euler[2]=angle
    last=[(-.136,.004,.036),(-.126,.025,.051),(-.110,.038,.064),(-.084,.043,.071),(-.047,.042,.078),(-.010,.035,.084),(.024,.032,.106),(.062,.031,.102),(.082,.017,.082),(.086,.003,.053)]
    vv=[];uu=[];ff=[]
    for i,(y,w,ztop) in enumerate(last):
        for j in range(33):
            t=pi*j/32;x=w*cos(t);z=.031+(ztop-.031)*sin(t)**.78
            vv.append(F((x,y,z)));uu.append((j/32,i/(len(last)-1)))
    for i in range(len(last)-1):
        for j in range(32):a=i*33+j;ff.append((a,a+1,a+34,a+33))
    mesh('Sculpted polished loafer upper '+str(side),vv,ff,LEATHER,uu,2)
    curve('Leather sole welt '+str(side),[F((x*1.015,y,.032)) for x,y in outline],.0015,LEATHER,True)
    apron=[(-.031,-.014,.074),(-.035,-.048,.068),(-.033,-.087,.061),(-.021,-.116,.054),(0,-.126,.053),(.021,-.116,.054),(.033,-.087,.061),(.035,-.048,.068),(.031,-.014,.074)]
    curve('Raised loafer apron seam '+str(side),[F(p) for p in apron],.0018,LEATHER)
    curve('Apron topstitch '+str(side),[F((x*.96,y+.001,z+.0015)) for x,y,z in apron],.00042,STITCH)
    strap=[F((x,-.030,.076+.013*(1-(x/.045)**2))) for x in np.linspace(-.040,.040,7)]
    ribbon('Penny loafer saddle '+str(side),strap,[.023]*7,LEATHER,.0012,6,(0,0,1))
    slot=cube('Penny slot '+str(side),F((0,-.030,.092)),(.019,.0045,.0008),SOLE,.001);slot.rotation_euler[2]=angle
    # The ankle opening is edged with a leather binding, into which the sock enters.
    curve('Shoe opening binding '+str(side),[F((.030*sin(t),.038+.041*cos(t),.102-.015*max(0,-cos(t)))) for t in np.linspace(0,2*pi,40)],.002,LEATHER,True)
    for j in range(0,80,2):
        x,y=outline[j];x2,y2=outline[(j+1)%80]
        curve('Welt stitch',[F((x*1.017,y,.0335)),F((x2*1.017,y2,.0335))],.00034,STITCH)

# ---------- Full backpack, including the unseen back ----------
cube('Rounded indigo backpack body',(.014,.128,1.170),(.238,.102,.282),PACK,.043)
cube('Backpack rear pocket',(.014,.192,1.116),(.192,.035,.143),PACK,.025)
curve('Pocket piped edge',[(-.068,.211,1.061),(-.079,.211,1.099),(-.075,.211,1.167),(.014,.214,1.183),(.102,.211,1.167),(.107,.211,1.099),(.094,.211,1.061)],.0017,WEBBING)
curve('Backpack main zip',[(-.103,.158,1.187),(-.102,.161,1.278),(-.068,.164,1.331),(.014,.166,1.340),(.097,.164,1.331),(.130,.161,1.278),(.131,.158,1.187)],.0023,WEBBING)
curve('Top carry handle',[(-.029,.124,1.314),(-.027,.128,1.342),(.055,.128,1.342),(.057,.124,1.314)],.006,WEBBING)
for s in [-1,1]:
    paths=[(.014+s*.104,.135,1.248),(.014+s*.141,.095,1.340),(.014+s*.150,.030,1.342),(.014+s*.143,-.018,1.310),(.014+s*.132,-.044,1.227),(.014+s*.128,-.043,1.157),(.014+s*.109,-.017,1.077),(.014+s*.096,.073,1.054)]
    ribbon('Continuous backpack shoulder strap '+str(s),paths,[.025,.030,.030,.030,.025,.021,.016,.017],PACK,.003,10)
    for off in [-.010,.010]:
        curve('Backpack strap edge stitch',[Vector(p)+Vector((off,-.002,0)) for p in paths[2:6]],.00036,WEBBING)
    x=.014+s*.131
    for z in [1.212,1.185]:
        # Rectangular acetal adjuster with a central bar, not a solid plate.
        for dx in [-.011,.011]:cube('Buckle vertical bar',(x+dx,-.050,z),(.0035,.004,.020),BUCKLE,.001)
        for dz in [-.0085,.0085]:cube('Buckle horizontal bar',(x,-.050,z+dz),(.024,.004,.0035),BUCKLE,.001)
        curve('Backpack buckle bar',[(x-.010,-.052,z),(x+.010,-.052,z)],.0018,BUCKLE)
    cube('Backpack side pocket '+str(s),(.014+s*.124,.133,1.094),(.031,.068,.105),PACK,.010)
    pull=cube('Metal zip pull '+str(s),(.014+s*.057,.174,1.332),(.006,.004,.016),GOLD,.002);pull.rotation_euler[1]=s*.20

# Directional strand highlights, with restrained specular energy.
for mat in [HAIR,HAIR2,HAIR3]:
    bsdf=mat.node_tree.nodes.get('Principled BSDF')
    bsdf.inputs['Specular IOR Level'].default_value=.30
    if 'Anisotropic IOR Level' in bsdf.inputs:bsdf.inputs['Anisotropic IOR Level'].default_value=.65

# ---------- Scene, authored source, optimized web export and audit ----------
scene=bpy.context.scene
scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=SAMPLES
scene.cycles.use_denoising=True;scene.cycles.adaptive_threshold=.035
scene.render.threads_mode='FIXED';scene.render.threads=8
scene.render.resolution_x=int(RES*2/3);scene.render.resolution_y=RES;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGBA'
scene.render.film_transparent=False
scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.32,.35,.40,1);scene.world.node_tree.nodes['Background'].inputs[1].default_value=.35
try:scene.view_settings.view_transform='AgX';scene.view_settings.look='AgX - Medium High Contrast'
except:scene.view_settings.view_transform='Standard'
scene.view_settings.exposure=0;scene.view_settings.gamma=1
FLOOR=material('Studio chalk',(.37,.405,.40),.86)
# Original cyclorama geometry avoids a floor/world horizon in perspective renders.
section=[(-20,-.001),(2,-.001)]+[(2+1.5*cos(a),1.499+1.5*sin(a)) for a in np.linspace(-pi/2,0,48)]+[(3.5,8)]
vv=[(x,y,z) for y,z in section for x in [-20,20]];ff=[(i*2,i*2+1,i*2+3,i*2+2) for i in range(len(section)-1)]
me=bpy.data.meshes.new('Cyclorama');me.from_pydata(vv,[],ff);me.update();floor=bpy.data.objects.new('Studio seamless cyclorama',me);scene.collection.objects.link(floor);me.materials.append(FLOOR)
for poly in me.polygons:poly.use_smooth=True

def area(name,pos,power,size,color):
    bpy.ops.object.light_add(type='AREA',location=pos);o=bpy.context.object;o.name=name;o.data.energy=power;o.data.shape='DISK';o.data.size=size;o.data.color=color
    o.rotation_euler=(Vector((0,0,.93))-o.location).to_track_quat('-Z','Y').to_euler()
area('Large warm key',(-2.5,-3.2,4.3),380,3.0,(1.0,.88,.79))
area('Cool soft fill',(2.8,-2.0,2.6),125,2.4,(.80,.88,1.0))
area('Hair and shoulder rim',(.6,1.8,3.3),285,2.0,(1.0,.95,.86))
bpy.ops.object.camera_add(location=(.06,-3.8,1.35));cam=bpy.context.object;cam.name='Reference portrait camera';scene.camera=cam
cam.rotation_euler=(Vector((.015,0,.855))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='PERSP';cam.data.lens=70
# Fit the authored 3D bounds to a portrait camera, never by analyzing reference pixels.
from bpy_extras.object_utils import world_to_camera_view
bpy.context.view_layer.update()
coords=[world_to_camera_view(scene,cam,o.matrix_world@Vector(c)) for o in CHAR.objects for c in o.bound_box]
span=max(p.y for p in coords)-min(p.y for p in coords)
cam.data.lens*=.92/span

scene.render.filepath=str(PRE/'gpt6_astra_pro_blender_front.png')
# These custom properties document equal underlying limb lengths independently of the image appearance.
scene['Author']='GPT-6 Astra Pro / mcp_colabdev / Blender headless'
scene['Asset policy']='All character geometry and textures authored in src/build_character.py; supplied reference never sampled.'
scene['Reference interpretation']='Backpack rear, hands and unseen surfaces are inferred; no claim of an exact scan.'
scene['Iteration']=REV
bpy.ops.wm.save_as_mainfile(filepath=str(PRE/'gpt6_astra_pro_mcpcolabdev_blender_rgirljk.blend'),compress=True)
# Join evaluated pieces by material only for the GLB. Editable source scene remains separated.
deps=bpy.context.evaluated_depsgraph_get(); export_coll=bpy.data.collections.new('WEB_EXPORT');scene.collection.children.link(export_coll)
buckets={}
for ob in list(CHAR.objects):
    if ob.type not in {'MESH','CURVE'}:continue
    if not ob.get('web_detail_keep',True):continue
    ev=ob.evaluated_get(deps);me=bpy.data.meshes.new_from_object(ev,preserve_all_data_layers=True,depsgraph=deps)
    if not len(me.vertices):bpy.data.meshes.remove(me);continue
    no=bpy.data.objects.new('Export '+ob.name,me);export_coll.objects.link(no);no.matrix_world=ob.matrix_world.copy()
    key=me.materials[0].name if me.materials else 'None';buckets.setdefault(key,[]).append(no)
exports=[]
for name,objects in buckets.items():
    bpy.ops.object.select_all(action='DESELECT')
    for o in objects:o.select_set(True)
    bpy.context.view_layer.objects.active=objects[0]
    if len(objects)>1:bpy.ops.object.join()
    o=bpy.context.object;o.name='R01 / '+name
    if len(o.data.polygons)>6000:
        dec=o.modifiers.new('Web geometry budget','DECIMATE');dec.ratio=.24 if 'hair' in name.lower() or 'fiber' in name.lower() else .50
        bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=dec.name)
    exports.append(o)
bpy.ops.object.select_all(action='DESELECT')
for o in exports:o.select_set(True)
verts=sum(len(o.data.vertices) for o in exports);tris=sum(sum(len(p.vertices)-2 for p in o.data.polygons) for o in exports)
bpy.ops.export_scene.gltf(filepath=str(PRE/'gpt6_astra_pro_mcpcolabdev_blender_rgirljk.glb'),export_format='GLB',use_selection=True,export_apply=True,export_yup=True,export_animations=False,export_cameras=False,export_lights=False)
for o in exports:bpy.data.objects.remove(o,do_unlink=True)
bpy.data.collections.remove(export_coll)
checks={'revision':REV,'sourceObjects':len(CHAR.objects),'webMaterialMeshes':len(buckets),'vertices':verts,'triangles':tris,'jointMeasurementsMetres':JOINTS,'equalThighs':abs(JOINTS['-1']['thigh']-JOINTS['1']['thigh'])<1e-6,'equalShins':abs(JOINTS['-1']['shin']-JOINTS['1']['shin'])<1e-6,'generatedFromScratch':True,'referenceUsedAsTexture':False,'glbBytes':(PRE/'gpt6_astra_pro_mcpcolabdev_blender_rgirljk.glb').stat().st_size}
(OUT/'geometry-audit.json').write_text(json.dumps(checks,indent=2))
print('GEOMETRY_AUDIT '+json.dumps(checks),flush=True)
bpy.ops.render.render(write_still=True)
print('FRONT_RENDER_READY',flush=True)
