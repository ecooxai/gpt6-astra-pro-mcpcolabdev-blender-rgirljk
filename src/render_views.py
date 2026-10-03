import bpy,os
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];PRE=ROOT/'build/preview'
s=bpy.context.scene;s.cycles.use_denoising=False;s.cycles.samples=int(os.environ.get('SAMPLES','64'));s.render.threads_mode='FIXED';s.render.threads=8
views=os.environ.get('VIEWS','front').split(',')
for view in views:
    s.render.resolution_x=800;s.render.resolution_y=1200;s.camera.data.ortho_scale=1.81
    target=Vector((.01,0,.83))
    if view=='front':loc=(.06,-4.5,1.48)
    elif view=='threequarter':loc=(2.8,-4,1.9)
    elif view=='back':loc=(.1,4.5,1.48)
    elif view=='side':loc=(4.5,-.05,1.48)
    elif view=='face':
        loc=(.10,-4.5,1.55);target=Vector((.042,-.01,1.498));s.camera.data.ortho_scale=.36;s.render.resolution_x=1000;s.render.resolution_y=1000
    s.camera.location=loc;s.camera.rotation_euler=(target-s.camera.location).to_track_quat('-Z','Y').to_euler();s.render.filepath=str(PRE/('gpt6_astra_pro_blender_'+view+'.png'))
    bpy.ops.render.render(write_still=True);print('VIEW_READY '+view,flush=True)
