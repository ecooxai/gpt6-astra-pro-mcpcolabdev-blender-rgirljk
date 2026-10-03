import bpy,os
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];PRE=ROOT/'build/preview'
s=bpy.context.scene;s.cycles.use_denoising=True;s.cycles.samples=int(os.environ.get('SAMPLES','64'));s.render.threads_mode='FIXED';s.render.threads=8
views=os.environ.get('VIEWS','front').split(',')
for view in views:
    s.camera.data.type='ORTHO'
    s.render.resolution_y=int(os.environ.get('VIEW_HEIGHT','1200'));s.render.resolution_x=int(s.render.resolution_y*2/3);s.camera.data.ortho_scale=1.81
    target=Vector((.01,0,.83))
    if view=='front':loc=(.06,-4.5,1.48)
    elif view=='threequarter':loc=(2.8,-4,1.9)
    elif view=='back':loc=(.1,2.8,1.48)
    elif view=='side':loc=(4.5,-.05,1.48)
    elif view=='face':
        loc=(.10,-4.5,1.55);target=Vector((.042,-.01,1.498));s.camera.data.ortho_scale=.36;s.render.resolution_x=int(os.environ.get('FACE_RES','1000'));s.render.resolution_y=s.render.resolution_x
    elif view=='shirt':
        loc=(.06,-3,1.38);target=Vector((.02,0,1.272));s.camera.data.ortho_scale=.44;s.render.resolution_x=900;s.render.resolution_y=900
    elif view=='hands':
        loc=(.01,3,.95);target=Vector((.007,.145,.948));s.camera.data.ortho_scale=.23;s.render.resolution_x=900;s.render.resolution_y=900
    s.camera.location=loc;s.camera.rotation_euler=(target-s.camera.location).to_track_quat('-Z','Y').to_euler();s.render.filepath=str(PRE/('gpt6_astra_pro_blender_'+view+'.png'))
    bpy.ops.render.render(write_still=True);print('VIEW_READY '+view,flush=True)
