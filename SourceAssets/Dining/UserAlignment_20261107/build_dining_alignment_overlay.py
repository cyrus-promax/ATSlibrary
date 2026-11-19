import bpy,math,json,pathlib
from mathutils import Matrix,Vector
out=pathlib.Path('D:/Cyrus/OneDrive/文件/香港仔工業學校/ATS/SourceAssets/Dining/UserAlignment_20261107')
data=json.loads((out/'alignment.json').read_text(encoding='utf-8'))
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.context.scene.unit_settings.system='METRIC';bpy.context.scene.unit_settings.scale_length=1
c,s=math.cos(math.radians(20)),math.sin(math.radians(20))
height=13.35
def world(u,v,h=height):return Vector((-8+c*u-s*v,-24+s*u+c*v,-24.55+h))
colors={'Plan':[.015,.25,.72],'Door':[.95,.24,.015],'Facility':[.13,.45,.10],'Text':[.008,.018,.045],'Plate':[.94,.96,.92],'Courtyard':[.35,.19,.62]}
mats={}
for n,col in colors.items():
    m=bpy.data.materials.new('M_DiningPlan_'+n);m.diffuse_color=(*col,1);mats[n]=m
groups={}
def box(n,center,size,mat):
    bpy.ops.mesh.primitive_cube_add(size=1,location=world(*center));o=bpy.context.object;o.name=n;o.dimensions=size;o.rotation_euler.z=math.radians(20)
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(mats[mat]);groups.setdefault(mat,[]).append(o)
def rect(n,bounds,mat,width=.045):
    u0,u1,v0,v1=bounds
    for u in [u0,u1]:box(n,(u,(v0+v1)/2,height),[width,v1-v0,.018],mat)
    for v in [v0,v1]:box(n,((u0+u1)/2,v,height),[u1-u0,width,.018],mat)
font=bpy.data.fonts.load('C:/Windows/Fonts/msjh.ttc')
def label(body,u,v,size=.25):
    # Text local X goes right (+v); local Y goes towards diagram top (-u).
    curve=bpy.data.curves.new('PlanLabel','FONT');curve.body=body;curve.font=font;curve.size=size;curve.align_x='CENTER';curve.align_y='CENTER';curve.extrude=.0005
    o=bpy.data.objects.new('PlanLabel',curve);bpy.context.collection.objects.link(o);o.location=world(u,v,height+.025);o.rotation_euler.z=math.radians(110);o.data.materials.append(mats['Text'])
    bpy.context.view_layer.update()
    width=max(.5,o.dimensions.length)
    box('TextPlate',(u,v,height+.011),[size*1.6,max(size*(len(body)*.7)+.25,width+.2),.008],'Plate')
    bpy.context.view_layer.objects.active=o;o.select_set(True)
    for other in bpy.context.selected_objects:
        if other!=o:other.select_set(False)
    bpy.ops.object.convert(target='MESH');groups.setdefault('Text',[]).append(bpy.context.object)
for f in data['features']:
    p0,p1,p2,p3=f['approx_corners_campus'];u0,v0,_=p0;u1,v1,_=p2
    mat='Door' if f['id'].startswith('door') else ('Plan' if f['id'] in ['room','outdoor'] else 'Facility')
    rect(f['id'],[u0,u1,v0,v1],mat,.065 if f['id']=='room' else .045)
    uc,vc,_=f['approx_center_campus']
    if f['id']=='room':label('餐廳',uc-.6,vc,.45)
    elif f['id']=='outdoor':
        for i,t in enumerate(['露天','桌椅區']):label(t,uc-.3+i*.6,vc,.26)
    elif f['id']=='washbasin':label(f['label'],uc,vc,.19)
    elif f['id']=='water':label(f['label'],uc,vc,.19)
    elif f['id']=='vita':label(f['label'],uc,vc,.28)
    elif f['id']=='door_bottom':label('門',uc,vc,.24)
    else:label('門',uc,vc,.24)
for court in data['courtyard_anchors']:
    u0,u1,v0,v1=court['model_campus_bounds_uuvv'];rect('SurveyCourt',[u0,u1,v0,v1],'Courtyard',.05)
    label('左天井' if court['id']=='left' else '右天井',(u0+u1)/2,(v0+v1)/2,.36)
label('G 層位置投影｜非實體內裝',10.9,16,.31)
for mat,objs in groups.items():
    bpy.ops.object.select_all(action='DESELECT')
    for o in objs:o.select_set(True)
    bpy.context.view_layer.objects.active=objs[0];bpy.ops.object.join();o=bpy.context.object;o.name='SM_DiningPlan_'+mat
    bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
bpy.ops.object.select_all(action='SELECT')
bpy.ops.export_scene.fbx(filepath=str(out/'ATS_Dining_Plan_Reference.fbx'),use_selection=True,apply_unit_scale=True,axis_forward='-Y',axis_up='Z',object_types={'MESH'},add_leaf_bones=False)
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(out/'ATS_Dining_Plan_Reference.blend'))
(out/'overlay_manifest.json').write_text(json.dumps({'projection_height_campus_m':height,'editor_only':True,'not_physical_geometry':True,'materials':colors,'meshes':['SM_DiningPlan_'+n for n in groups]},ensure_ascii=False,indent=2),encoding='utf-8')
