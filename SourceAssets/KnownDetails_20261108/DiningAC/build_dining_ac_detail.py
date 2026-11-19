import bpy,bmesh,pathlib,json,math,hashlib
from mathutils import Vector

root=pathlib.Path('D:/Cyrus/OneDrive/文件/香港仔工業學校/ATS')
out=root/'SourceAssets/KnownDetails_20261108/DiningAC'
out.mkdir(parents=True,exist_ok=True)
source=root/'SourceAssets/Dining/CrossWindowWall_20261108/ATS_Dining_CrossWindows.blend'
before_hash=hashlib.sha256(source.read_bytes()).hexdigest()
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.context.scene.unit_settings.system='METRIC';bpy.context.scene.unit_settings.scale_length=1
with bpy.data.libraries.load(str(source),link=False) as (src,dst):
 assert 'SM_DiningCross_Aircon' in src.objects
 dst.objects=['SM_DiningCross_Aircon']
original=dst.objects[0]
cc,ss=math.cos(math.radians(20)),math.sin(math.radians(20))
def local(p):
 x=p.x+8;y=p.y+24
 return (cc*x+ss*y,-ss*x+cc*y,p.z+24.55)
def site(p):
 u,v,h=p;return (-8+cc*u-ss*v,-24+ss*u+cc*v,-24.55+h)
def bounds(points):return [[min(p[k] for p in points),max(p[k] for p in points)] for k in range(3)]
def material(n,color):
 m=bpy.data.materials.get(n) or bpy.data.materials.new(n);m.diffuse_color=(*color,1)
 return m

# Original casings and existing lower trims are retained as exact source vertices,
# faces, UVs and bevel geometry. Only the unsupported full-width black panels and
# the eight full-width slat boxes per unit are removed.
adj={v.index:set() for v in original.data.vertices}
for e in original.data.edges:
 a,b=e.vertices;adj[a].add(b);adj[b].add(a)
todo=set(adj);components=[]
while todo:
 seed=todo.pop();ids={seed};stack=[seed]
 while stack:
  k=stack.pop()
  for n in adj[k]:
   if n in todo:todo.remove(n);ids.add(n);stack.append(n)
 points=[local(original.matrix_world@original.data.vertices[i].co) for i in ids]
 b=bounds(points);ext=[hi-lo for lo,hi in b]
 mats=sorted({original.data.materials[p.material_index].name for p in original.data.polygons if p.vertices[0] in ids})
 components.append({'ids':ids,'bounds':b,'extents':ext,'materials':mats})
assert len(components)==22,len(components)
casings=[co for co in components if abs(co['extents'][0]-.42)<.0001 and abs(co['extents'][1]-.65)<.0001 and abs(co['extents'][2]-.58)<.0001]
trims=[co for co in components if abs(co['extents'][0]-.02)<.0001 and abs(co['extents'][1]-.60)<.0001 and abs(co['extents'][2]-.08)<.0001]
assert len(casings)==2 and len(trims)==2
keep_ids=set().union(*(co['ids'] for co in casings+trims))
orig_world=[tuple(original.matrix_world@v.co) for v in original.data.vertices]
orig_keep=sorted(tuple(original.data.vertices[i].co) for i in keep_ids)
orig_bounds=bounds(orig_world)
patched=bpy.data.objects.new('SM_DiningAC_PhotoFronts',original.data.copy());patched.matrix_world=original.matrix_world.copy();bpy.context.collection.objects.link(patched)
bm=bmesh.new();bm.from_mesh(patched.data);bm.verts.ensure_lookup_table()
bmesh.ops.delete(bm,geom=[bm.verts[i] for i in range(len(bm.verts)) if i not in keep_ids],context='VERTS')
bm.to_mesh(patched.data);bm.free();patched.data.update()
retained_before=sorted(tuple(v.co) for v in patched.data.vertices)
assert retained_before==orig_keep
retained_vertex_count=len(patched.data.vertices)
retained_polygon_count=len(patched.data.polygons)
new_parts=[]
new_specs={
 'M_DiningAC_PaleIntake':{'linear_rgb':[.39,.40,.365],'roughness':.70,'metallic':0.0},
 'M_DiningAC_DarkOutlet':{'linear_rgb':[.012,.015,.014],'roughness':.60,'metallic':0.0},
 'M_DiningAC_ControlPatch':{'linear_rgb':[.045,.065,.070],'roughness':.62,'metallic':0.0}
}
for n,spec in new_specs.items():material(n,spec['linear_rgb'])
facebox=[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
records=[]
def addbox(name,p,sz,mat):
 x,y,z=p;dx,dy,dz=[a/2 for a in sz]
 v=[(x-dx,y-dy,z-dz),(x+dx,y-dy,z-dz),(x+dx,y+dy,z-dz),(x-dx,y+dy,z-dz),(x-dx,y-dy,z+dz),(x+dx,y-dy,z+dz),(x+dx,y+dy,z+dz),(x-dx,y+dy,z+dz)]
 me=bpy.data.meshes.new(name);me.from_pydata([site(q) for q in v],[],facebox);me.materials.append(bpy.data.materials[mat]);me.update()
 ob=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(ob)
 bpy.context.view_layer.objects.active=ob;ob.select_set(True)
 mod=ob.modifiers.new('Front trim shallow edge radius','BEVEL');mod.width=.0015;mod.segments=3;bpy.ops.object.modifier_apply(modifier=mod.name)
 ob.select_set(False);new_parts.append(ob)
 records.append({'part':name,'centre_campus_m':p,'size_m':sz,'material':mat})

for index,co in enumerate(sorted(casings,key=lambda a:a['bounds'][1][0]),1):
 v0,v1=co['bounds'][1];z0,z1=co['bounds'][2];vc=(v0+v1)/2;zc=(z0+z1)/2
 # Front arrangement from the same photograph, within the existing casing.
 # No physical product, readable control, slot count or manufacturer invented.
 addbox(f'AC{index}_BroadPaleLeft',(.339,vc-.091,zc+.020),(.018,.398,.355),'M_DiningAC_PaleIntake')
 addbox(f'AC{index}_NarrowDarkRight',(.346,vc+.222,zc+.080),(.025,.150,.330),'M_DiningAC_DarkOutlet')
 addbox(f'AC{index}_UnlabelledLowerRight',(.345,vc+.222,zc-.160),(.020,.150,.105),'M_DiningAC_ControlPatch')

bpy.ops.object.select_all(action='DESELECT');patched.select_set(True)
for ob in new_parts:ob.select_set(True)
bpy.context.view_layer.objects.active=patched;bpy.ops.object.join()
# Source retained mesh vertex order stays first through join; do not re-bevel it.
assert sorted(tuple(v.co) for v in patched.data.vertices[:retained_vertex_count])==orig_keep
used=sorted(set(p.material_index for p in patched.data.polygons));oldmats=list(patched.data.materials)
mapping={idx:i for i,idx in enumerate(used)}
poly_new=[mapping[p.material_index] for p in patched.data.polygons]
patched.data.materials.clear()
for idx in used:patched.data.materials.append(oldmats[idx])
for p,idx in zip(patched.data.polygons,poly_new):p.material_index=idx
patched.data.name=patched.name
new_bounds=bounds([tuple(patched.matrix_world@v.co) for v in patched.data.vertices])
casings_report=[]
for co in sorted(casings,key=lambda a:a['bounds'][1][0]):
 original_points=sorted(tuple(original.data.vertices[i].co) for i in co['ids'])
 current_points=[tuple(v.co) for v in patched.data.vertices if tuple(v.co) in set(original_points)]
 assert sorted(current_points)==original_points
 casings_report.append({'bounds_campus_m':co['bounds'],'vertex_count':len(co['ids']),'preserved_exact_vertices':True,'preserved_existing_bevel':True})
bpy.data.objects.remove(original,do_unlink=True)
bpy.ops.object.select_all(action='DESELECT');patched.select_set(True);bpy.context.view_layer.objects.active=patched
fbx=out/'ATS_Dining_AC_PhotoFronts.fbx'
bpy.ops.export_scene.fbx(filepath=str(fbx),use_selection=True,object_types={'MESH'},apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',axis_forward='-Z',axis_up='Y',mesh_smooth_type='FACE',add_leaf_bones=False,bake_anim=False,path_mode='STRIP')
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(out/'ATS_Dining_AC_PhotoFronts.blend'))
after_hash=hashlib.sha256(source.read_bytes()).hexdigest();assert after_hash==before_hash
report={
 'status':'isolated_source_built_not_imported',
 'target_actor':'StaticMeshActor_625','mesh_name':patched.name,
 'source':str(source),'source_sha256_before':before_hash,'source_sha256_after':after_hash,
 'source_unchanged':True,'source_components':22,'retained_components':4,'removed_components':18,'added_components':6,
 'retained_vertex_count':retained_vertex_count,'retained_polygon_count':retained_polygon_count,
 'source_retained_vertices_bitwise_equal':True,'casings':casings_report,
 'overall_mesh_bounds_world_m_before':orig_bounds,'overall_mesh_bounds_world_m_after':new_bounds,
 'overall_bounds_delta_m':[[new_bounds[k][j]-orig_bounds[k][j] for j in range(2)] for k in range(3)],
 'new_parts':records,'material_slots':[m.name for m in patched.data.materials],
 'new_material_specs':new_specs,
 'existing_material_map':{'M_Dining_OffWhitePaint_Matte':'/Game/ATS/Dining/PhotoFinishes_20261108/Materials/M_Dining_OffWhitePaint_Matte'},
 'evidence':{'image':'work/research/dining_shutters/hk01_flood_06.jpg','photo_supported':'Broad pale/grey left front region, narrow dark right region, smaller darker patch beneath right region on BOTH units.','not_supported':'Exact fine louvre count, legible controls, manufacturer, measured appliance size.','slat_policy':'No discrete slats generated: exact count unresolved. The correction is front-face subdivision only.'},
 'metric_limit':'Retains current casing size/placement; local panel proportions are visual interpretation inside that existing box, not a real appliance survey.',
 'ue_changes':False,'fbx':str(fbx),'blend':str(out/'ATS_Dining_AC_PhotoFronts.blend')
}
(out/'ac_front_manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print('DINING_AC_PHOTO_FRONTS_BUILT',json.dumps({'source_unchanged':True,'casings_exact':len(casings_report),'vertices':len(patched.data.vertices),'materials':report['material_slots'],'bounds_delta':report['overall_bounds_delta_m']},ensure_ascii=False))
