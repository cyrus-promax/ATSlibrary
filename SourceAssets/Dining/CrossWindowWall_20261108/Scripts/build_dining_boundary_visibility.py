import bpy,pathlib,json,math,hashlib
root=pathlib.Path('D:/Cyrus/OneDrive/文件/香港仔工業學校/ATS');out=root/'SourceAssets/Dining/CrossWindowWall_20261108/BoundaryProxyCorrection';out.mkdir(parents=True,exist_ok=True)
source=root/'SourceAssets/Walkthrough/ATS_Walkthrough.blend';before=hashlib.sha256(source.read_bytes()).hexdigest()
bpy.ops.wm.read_factory_settings(use_empty=True)
with bpy.data.libraries.load(str(source),link=False) as (src,dst):dst.objects=['SM_Walk_Boundary_Stone']
ob=dst.objects[0];c,s=math.cos(math.radians(20)),math.sin(math.radians(20))
def local(p):x,y=p.x+8,p.y+24;return(c*x+s*y,-s*x+c*y,p.z+24.55)
points=[ob.matrix_world@v.co for v in ob.data.vertices];camp=[local(p) for p in points]
west={i for i,p in enumerate(camp) if -1.251<p[0]<-.749 and -.501<p[1]<44.501 and -.001<p[2]<6.001}
assert len(west)==8,(len(west),[camp[i] for i in west])
faces=[p for p in ob.data.polygons if all(i in west for i in p.vertices)];keep=[p for p in ob.data.polygons if not any(i in west for i in p.vertices)]
assert len(faces)==6 and len(keep)==12,(len(faces),len(keep))
uv=ob.data.uv_layers.active
outputs=[]
for name,polys in [('SM_DiningBoundary_RetainedOtherSections',keep),('SM_DiningBoundary_NonVisualWestCollision',faces)]:
 vs=[];fs=[];uvs=[]
 for p in polys:
  n=len(vs);vs.extend([points[i] for i in p.vertices]);fs.append(tuple(range(n,len(vs))));uvs.append([tuple(uv.data[li].uv) for li in p.loop_indices])
 me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.materials.append(ob.data.materials[0]);me.update();newuv=me.uv_layers.new(name='UVMap')
 for p,uvrow in zip(me.polygons,uvs):
  for li,q in zip(p.loop_indices,uvrow):newuv.data[li].uv=q
 obj=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(obj);outputs.append(obj)
bpy.data.objects.remove(ob,do_unlink=True)
bpy.context.scene.unit_settings.system='METRIC';bpy.context.scene.unit_settings.scale_length=1
bpy.ops.object.select_all(action='DESELECT')
for obj in outputs:obj.select_set(True)
bpy.ops.export_scene.fbx(filepath=str(out/'ATS_Dining_BoundaryVisibility.fbx'),use_selection=True,object_types={'MESH'},apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',axis_forward='-Z',axis_up='Y',mesh_smooth_type='FACE',add_leaf_bones=False,bake_anim=False,path_mode='STRIP')
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(out/'ATS_Dining_BoundaryVisibility.blend'))
assert before==hashlib.sha256(source.read_bytes()).hexdigest()
report={'source':str(source),'source_sha256_unchanged':before,'west_box_campus_bounds':[[-1.25,-.75],[-.5,44.5],[0,6]],'removed_visible_faces':6,'preserved_other_boundary_faces_and_uv':12,'nonvisual_collision_retained':True,'reason':'Early generator explicitly describes the box as a mask for removed photogrammetric geometry. No source establishes a real six-metre stone wall immediately behind the dining windows. Remove unsupported appearance, not create matching false window tunnels.','no_new_exterior_scenery_created':True,'other_boundary_sections_retained_without_claiming_their_accuracy':True}
(out/'boundary_manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');print('BOUNDARY_VISIBILITY_BUILT',report)
