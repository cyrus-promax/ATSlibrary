import bpy,pathlib,json,math
from mathutils import Vector
root=pathlib.Path('D:/Cyrus/OneDrive/文件/香港仔工業學校/ATS')
out=root/'SourceAssets/Dining/PhotoFinishes_20261108';out.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.context.scene.unit_settings.system='METRIC';bpy.context.scene.unit_settings.scale_length=1
c,s=math.cos(math.radians(20)),math.sin(math.radians(20))
def site(p):u,v,h=p;return (-8+c*u-s*v,-24+s*u+c*v,-24.55+h)
vs=[];fs=[];mi=[]
def geom(vertices,faces,mat):
 b=len(vs);vs.extend(vertices);fs.extend([tuple(b+i for i in f) for f in faces]);mi.extend([mat]*len(faces))
def box(p,sz,mat=0):
 x,y,z=p;dx,dy,dz=[t/2 for t in sz]
 geom([(x-dx,y-dy,z-dz),(x+dx,y-dy,z-dz),(x+dx,y+dy,z-dz),(x-dx,y+dy,z-dz),(x-dx,y-dy,z+dz),(x+dx,y-dy,z+dz),(x+dx,y+dy,z+dz),(x-dx,y+dy,z+dz)],[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],mat)
def rod(a,b,r=.015,mat=0,segments=24):
 a,b=Vector(a),Vector(b);d=(b-a).normalized();e=d.cross(Vector((0,0,1)))
 if e.length<.01:e=d.cross(Vector((0,1,0)))
 e.normalize();f=d.cross(e);verts=[]
 for p in [a,b]:
  for i in range(segments):verts.append(tuple(p+r*(math.cos(i*math.tau/segments)*e+math.sin(i*math.tau/segments)*f)))
 faces=[tuple(range(segments-1,-1,-1)),tuple(range(segments,2*segments))]+[(i,(i+1)%segments,(i+1)%segments+segments,i+segments) for i in range(segments)]
 geom(verts,faces,mat)
# User requests a longer basin in the same plan position. 4.5 m is an editable model value.
sv0,sv1=23.47,27.97;front,back=18.97,19.57
box(((front+back)/2,(sv0+sv1)/2,.73),(back-front,sv1-sv0,.045))
for u in [front,back]:box((u,(sv0+sv1)/2,.835),(.035,sv1-sv0,.22))
for v in [sv0,sv1]:box(((front+back)/2,v,.835),(back-front,.035,.22))
for u in [front+.05,back-.05]:
 for v in [sv0+.08,sv1-.08]:box((u,v,.38),(.045,.045,.72))
# Retain the existing three fittings; do not infer extra taps from increased length.
taps=[sv0+.46,(sv0+sv1)/2,sv1-.46]
for v in taps:
 rod((19.50,v,.94),(19.50,v,1.16),.022)
 rod((19.50,v,1.16),(19.26,v,1.16),.022)
 rod((19.26,v,1.16),(19.26,v,1.10),.022)
 rod((19.25,v,.752),(19.25,v,.757),.035,1)
me=bpy.data.meshes.new('Dining_LongWashbasin');me.from_pydata([site(p) for p in vs],[],fs);me.update()
for n,col in [('Steel',(.54,.57,.56,1)),('Black',(.014,.018,.019,1))]:
 m=bpy.data.materials.new('M_DiningBuild_'+n);m.diffuse_color=col;me.materials.append(m)
for p,i in zip(me.polygons,mi):p.material_index=i
ob=bpy.data.objects.new('SM_Dining_LongWashbasin',me);bpy.context.collection.objects.link(ob)
bpy.context.view_layer.objects.active=ob;ob.select_set(True)
mod=ob.modifiers.new('Manufactured edge radius','BEVEL');mod.width=.004;mod.segments=3;bpy.ops.object.modifier_apply(modifier=mod.name)
mod=ob.modifiers.new('Weighted normals','WEIGHTED_NORMAL');bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.export_scene.fbx(filepath=str(out/'SM_Dining_LongWashbasin.fbx'),use_selection=True,object_types={'MESH'},apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',axis_forward='-Z',axis_up='Y',mesh_smooth_type='FACE',add_leaf_bones=False,bake_anim=False,path_mode='STRIP')
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(out/'ATS_Dining_LongWashbasin.blend'))
report={'length_m':4.5,'previous_length_m':2.82,'bounds_campus_m':[front-.0175,back+.0175,sv0-.0175,sv1+.0175,.02,1.182],'retained_fitting_count':3,'fitting_v':taps,'basis':'User explicitly requested a longer washbasin in the drawn position. Length and retained generic fittings are not verified site measurements or a verified product. No new tap count inferred.','fountain_gap_m':29.69-.285-(sv1+.0175),'courtyard_door_gap_m':sv0-.0175-(13.64613555+1.1)}
(out/'sink_manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print('LONG_SINK_BUILT',report)
