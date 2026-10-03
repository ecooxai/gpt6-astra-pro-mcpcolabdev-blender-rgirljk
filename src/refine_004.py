from pathlib import Path
p=Path('src/build_character.py');s=p.read_text()
# Smooth monotone interpolation keeps the head's contour continuously curved.
old='def prof(z):return float(np.interp(z,ZP,XP)),float(np.interp(z,ZP,YP))'
new='''from functools import lru_cache
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
def prof(z):return smooth_profile(z,ZP,XP),smooth_profile(z,ZP,YP)'''
assert old in s;s=s.replace(old,new)
s=s.replace('y-=.020*exp(-(x/.010)**2-((z+.010)/.014)**2)','y-=.0155*exp(-(x/.0115)**2-((z+.012)/.015)**2)')
s=s.replace('y-=.006*exp(-(x/.012)**2-((z-.012)/.029)**2)','y-=.0045*exp(-(x/.012)**2-((z-.012)/.029)**2)')
s=s.replace("mesh('Sculpted head · continuous facial surface',v,f,SKIN,uv,1)",'''head=mesh('Sculpted head · continuous facial surface',v,f,SKIN,uv,1)
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
''')
s=s.replace("[(.019,.016,1.306),(.025,.009,1.350),(.036,.002,1.409),H((0,.008,-.083))],[.040,.034,.032,.034]", "[(.019,.016,1.270),(.019,.016,1.306),(.025,.009,1.350),(.036,.002,1.409),H((0,.008,-.083))],[.055,.040,.034,.032,.034]")
s=s.replace("ell('Upper chest inside open collar',(.025,.003,1.326),(.055,.035,.052),SKIN)","# The exposed chest is now continuous with the neck, without an intersecting ellipsoid.")
s=s.replace("curve('Smile corner fold '+str(side),[H((side*.031,face_y(side*.031,-.042)-.0004,-.042)),H((side*.034,face_y(side*.034,-.048)-.0005,-.048))],.0004,LID)","pass # subtle smile corners are formed by the lip contour, without painted crease lines")
s=s.replace("(.00515,.0037,.0068*(1-.18*abs(u))),TEETH,.0011", "(.00515,.0037,.0088*(1-.20*abs(u))),TEETH,.0007")
# A rounded ellipsoidal scalp eliminates the previous conical crown and highlight bands.
a=s.index('def cap_point(t,a,off=0):');b=s.index('\nv=[];uv=[];f=[]',a)
s=s[:a]+'''def cap_point(t,a,off=0):
    q=sin(a);rx=(.090+off)*q*(1+.07*q*q);ry=(.083+off)*q*(1+.04*q*q)
    return Vector((rx*sin(t),-ry*cos(t),(.138+off)*cos(a)))
''' + s[b:]
s=s.replace("pp=[H(p) for p in points]\n    ribbon('Swept fringe", "points=[(x,(face_y(x,z)-.009 if j else y),z) for j,(x,y,z) in enumerate(points)]\n    pp=[H(p) for p in points]\n    ribbon('Swept fringe")
s=s.replace("[.006,.012,.013,.010,.0003],HAIR", "[.001,.011,.012,.009,.0002],HAIR")
s=s.replace("(.016,.012,.013),.37","(.016,.012,.013),.47").replace("(.021,.016,.016),.39","(.021,.016,.016),.49").replace("(.030,.023,.020),.42","(.027,.021,.019),.51")
# Replace separately capped wrists and palms by anatomically arranged, fused hand surfaces.
a=s.index('    wrist=Vector((sx*.103+.007,.114,.954))');b=s.index('\n# ---------- Pleated',a)
s=s[:a]+'''    wrist=Vector((sx*.090+.007,.118,.958 if side<0 else .952))
    knuckle=Vector((sx*.036+.007,.153 if side<0 else .166,.920 if side<0 else .902))
    direction=(knuckle-wrist).normalized();normal=Vector((0,1,0));normal=(normal-direction*normal.dot(direction)).normalized();wide=normal.cross(direction).normalized()
    handparts=[]
    fore=[(sx*.147+.007,.048,1.061),(sx*.129+.007,.080,1.017),wrist]
    handparts.append(tube('Forearm to wrist '+str(side),fore,[.028,.025,.0185],SKIN,aspect=.93,n=40,steps=10))
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
    sm=hand.modifiers.new('Hand surface relaxation','SMOOTH');sm.factor=.42;sm.iterations=3;bpy.ops.object.modifier_apply(modifier=sm.name)
''' +s[b:]
# Extend sock surfaces into correctly positioned shoe throats; bone lengths remain unchanged.
s=s.replace("knee.lerp(ankle,.61),ankle]", "knee.lerp(ankle,.61),ankle,ankle+Vector((0,-.004,-.027))]")
s=s.replace("[.065,.061,.049,.0395,.045,.034,.024],SKIN", "[.065,.061,.049,.0395,.045,.034,.024,.024],SKIN")
s=s.replace("C=Vector((ankle.x,ankle.y-.006,0))", "C=Vector((ankle.x,ankle.y-.038,0))")
old="bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.001));floor=bpy.context.object;floor.name='Studio seamless floor';floor.data.materials.append(FLOOR)"
new="""# Original cyclorama geometry avoids a floor/world horizon in perspective renders.
section=[(-20,-.001),(2,-.001)]+[(2+1.5*cos(a),1.499+1.5*sin(a)) for a in np.linspace(-pi/2,0,48)]+[(3.5,8)]
vv=[(x,y,z) for y,z in section for x in [-20,20]];ff=[(i*2,i*2+1,i*2+3,i*2+2) for i in range(len(section)-1)]
me=bpy.data.meshes.new('Cyclorama');me.from_pydata(vv,[],ff);me.update();floor=bpy.data.objects.new('Studio seamless cyclorama',me);scene.collection.objects.link(floor);me.materials.append(FLOOR)
for poly in me.polygons:poly.use_smooth=True
"""
assert old in s;s=s.replace(old,new)
p.write_text(s)
