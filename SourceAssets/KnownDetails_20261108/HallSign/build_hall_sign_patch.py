import bpy,pathlib,json,math,hashlib,array,shutil
from mathutils import Vector
root=pathlib.Path('D:/Cyrus/OneDrive/文件/香港仔工業學校/ATS')
research=pathlib.Path(__file__).parent
out=root/'SourceAssets/KnownDetails_20261108/HallSign'
out.mkdir(parents=True,exist_ok=True)
source=root/'SourceAssets/Walkthrough/ATS_Walkthrough.blend'
source_hash=hashlib.sha256(source.read_bytes()).hexdigest()
assert not (out/'ATS_HallSign_ReadingOrder.blend').exists(),'Do not overwrite an existing generated revision without inspection.'
bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False)
ob=bpy.data.objects['SM_Walk_Hall_Black']
assert len(ob.modifiers)==0
c,s=math.cos(math.radians(20)),math.sin(math.radians(20))
def campus(p):
 x=p.x+8;y=p.y+24
 return (c*x+s*y,-s*x+c*y,p.z+24.55)
def coordinates():return [tuple(v.co) for v in ob.data.vertices]
def worlds():return [campus(ob.matrix_world@v.co) for v in ob.data.vertices]
def sha(obj):return hashlib.sha256(json.dumps(obj,separators=(',',':'),ensure_ascii=False).encode('utf-8')).hexdigest()
before=coordinates();before_world=worlds()
faces_before=[list(p.vertices) for p in ob.data.polygons]
uvs_before={uv.name:[list(p.uv) for p in uv.data] for uv in ob.data.uv_layers}
normals_before=[list(p.normal) for p in ob.data.polygons]
audit=json.loads((research/'hall_sign_geometry_audit.json').read_text(encoding='utf-8'))
assert source_hash==audit['source_sha256'] and len(before)==audit['mesh_vertices']
groups=audit['groups_left_to_right'];ids={i for g in groups for i in g['vertex_indices']}
assert len(ids)==2852 and len(before)-len(ids)==512
assert all(34.5<before_world[i][0]<39.5 and 22.6<before_world[i][1]<23.1 and 6.8<before_world[i][2]<7.8 for i in ids)
groups_by_vertex={i:k for k,g in enumerate(groups) for i in g['vertex_indices']}
assert all(len({groups_by_vertex.get(i,-1) for i in f})==1 for f in faces_before),'Faces must not connect glyph groups or other geometry.'
lo=min(before_world[i][0] for i in ids);hi=max(before_world[i][0] for i in ids)
inverse=ob.matrix_world.inverted().to_3x3();changes=[]
for group in groups:
 old_min,old_max=group['bounds_campus_m'];centre=(old_min[0]+old_max[0])/2
 new_centre=lo+hi-centre;du=new_centre-centre
 # Translate each original glyph as a rigid piece. Never reflect its vertices.
 local_delta=inverse@Vector((c*du,s*du,0))
 for i in group['vertex_indices']:ob.data.vertices[i].co+=local_delta
 changes.append({'glyph':group['glyph'],'vertices':len(group['vertex_indices']),'old_slot_centre_u':centre,'new_slot_centre_u':new_centre,'translation_campus_m':[du,0,0],'bounds_before_campus_m':group['bounds_campus_m']})
ob.data.update();after=coordinates();after_world=worlds()
unchanged=[i for i in range(len(before)) if i not in ids]
assert [before[i] for i in unchanged]==[after[i] for i in unchanged]
assert faces_before==[list(p.vertices) for p in ob.data.polygons]
assert uvs_before=={uv.name:[list(p.uv) for p in uv.data] for uv in ob.data.uv_layers}
assert all(before[i][2]==after[i][2] for i in range(len(before)))
for group,change in zip(groups,changes):
 ii=group['vertex_indices'];change['bounds_after_campus_m']=[[min(after_world[i][a] for i in ii) for a in range(3)],[max(after_world[i][a] for i in ii) for a in range(3)]]
 for a in [1,2]:assert max(abs(after_world[i][a]-before_world[i][a]) for i in ii)<1e-5
 assert max(abs((after_world[i][0]-before_world[i][0])-change['translation_campus_m'][0]) for i in ii)<1e-5
assert abs(min(after_world[i][0] for i in ids)-lo)<1e-5
assert abs(max(after_world[i][0] for i in ids)-hi)<1e-5
assert [x['glyph'] for x in sorted(changes,key=lambda x:x['new_slot_centre_u'])]==list('堂德理夏')
for other in list(bpy.data.objects):
 if other!=ob:bpy.data.objects.remove(other,do_unlink=True)
ob.name='SM_Hall_Black_CorrectReadingOrder';ob.data.name=ob.name
bpy.ops.outliner.orphans_purge(do_recursive=True)
bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);bpy.context.view_layer.objects.active=ob
fbx=out/'ATS_HallSign_ReadingOrder.fbx'
bpy.ops.export_scene.fbx(filepath=str(fbx),use_selection=True,object_types={'MESH'},apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',axis_forward='-Z',axis_up='Y',mesh_smooth_type='FACE',add_leaf_bones=False,bake_anim=False,path_mode='STRIP')
bpy.context.preferences.filepaths.save_version=0
blend=out/'ATS_HallSign_ReadingOrder.blend';bpy.ops.wm.save_as_mainfile(filepath=str(blend))
assert source_hash==hashlib.sha256(source.read_bytes()).hexdigest()
for p in [research/'hall_sign_geometry_audit.json',pathlib.Path(__file__)]:shutil.copy2(p,out/p.name)
report={
 'status':'asset_prepared_not_imported',
 'source':str(source),'source_sha256_before':source_hash,'source_sha256_after':hashlib.sha256(source.read_bytes()).hexdigest(),
 'source_object':'SM_Walk_Hall_Black','output_object':ob.name,
 'target_actor':'StaticMeshActor_552','target_label':'Hall | M_Interior_Black',
 'existing_asset':'/Game/ATS/Revision8/Architecture/ATS_FacadeRevision_SM_Walk_Hall_Black',
 'only_change':'Rigid translations of four original glyph groups, reversing their physical left-to-right order. No glyph mirroring, font replacement, scale, baseline, height, depth, material, UV or other geometry changes.',
 'text_before_left_to_right':'夏 理 德 堂','text_after_left_to_right':'堂 德 理 夏','reading':'Traditional right-to-left signage reads 夏理德堂.',
 'glyph_changes':changes,
 'vertices_total':len(before),'moved_text_vertices':len(ids),'untouched_other_vertices':len(unchanged),
 'other_vertices_sha256_before':sha([before[i] for i in unchanged]),'other_vertices_sha256_after':sha([after[i] for i in unchanged]),
 'topology_sha256_before':sha(faces_before),'topology_sha256_after':sha([list(p.vertices) for p in ob.data.polygons]),
 'uvs_sha256_before':sha(uvs_before),'uvs_sha256_after':sha({uv.name:[list(p.uv) for p in uv.data] for uv in ob.data.uv_layers}),
 'sign_u_bounds_before':[lo,hi],'sign_u_bounds_after':[min(after_world[i][0] for i in ids),max(after_world[i][0] for i in ids)],
 'material_slots':[m.name for m in ob.data.materials],
 'photo_evidence':['work/research/photos/HK-Aberdeen-Technical-School-03@1200x1200.JPG','work/research/photos/HK-Aberdeen-Technical-School-08@1200x1200.JPG'],
 'files':[{'path':str(p),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in [fbx,blend]],
 'limitations':'This correction verifies only character order. Existing hall dimensions, facade and other objects are not certified as a measured 1:1 reconstruction.',
 'UE_changes':0
}
(out/'hall_sign_patch_manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'output':str(out),'text_vertices_moved':len(ids),'other_vertices_unchanged':len(unchanged),'source_unchanged':True},ensure_ascii=False))
