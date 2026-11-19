"""Isolated G-floor aperture patches for the existing rear-wing facade.

No UE calls, no original-source writes, and no changes to the retained pillars.
"""
from pathlib import Path
import bpy,math,json,hashlib,array
from mathutils import Vector
from mathutils.bvhtree import BVHTree
root=Path('D:/Cyrus/OneDrive/文件/香港仔工業學校/ATS')
work=Path('C:/Users/Cyrus/Documents/Codex/2026-11-06/dao/work')
source=root/'SourceAssets/Walkthrough/ATS_Walkthrough.blend'
out=root/'SourceAssets/Dining/FullGroundFloor_20261108/RearShutterApertures'
out.mkdir(parents=True,exist_ok=True)
prep=json.loads((out.parent/'preparation.json').read_text(encoding='utf-8'))
scene=json.loads((Path(prep['backup'])/'scene_before.json').read_text(encoding='utf-8'))
targets={
 'Cream':('StaticMeshActor_19',work/'ATS_before_facade_detail/Walkthrough/ATS_InteriorCleanup.fbx'),
 'Metal':('StaticMeshActor_21',work/'ATS_before_structure_removal/Walkthrough/ATS_FacadeRevision.fbx'),
 'WindowShade':('StaticMeshActor_26',work/'ATS_before_unverified_interior_removal/SourceAssets/Walkthrough/ATS_Northwest_Addition.fbx')}
cuts=[(2.675,4.875,0.0,2.80),(10.705,12.905,0.0,2.80)]
c,s=math.cos(math.radians(20)),math.sin(math.radians(20))
def campus(p):
 x,y=p.x+8,p.y+24
 return(c*x+s*y,-s*x+c*y,p.z+24.55)
def world(p):
 u,v,h=p
 return Vector((-8+c*u-s*v,-24+s*u+c*v,-24.55+h))
def digest(path):
 h=hashlib.sha256()
 with path.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
def signature(obj):
 pts=[tuple(round(q,3) for q in obj.matrix_world@v.co) for v in obj.data.vertices]
 faces=sorted(tuple(sorted(pts[k] for k in p.vertices)) for p in obj.data.polygons)
 return hashlib.sha256(repr(faces).encode()).hexdigest()
def surface(obj):
 points=[tuple(obj.matrix_world@v.co) for v in obj.data.vertices]
 return points,[tuple(p.vertices) for p in obj.data.polygons]
def verify_surface(reference,current,tolerance=.00002):
 # Avoid quantized hashes rejecting identical FBX coordinates on rounding edges.
 rp,rf=reference;cp,cf=current
 assert len(rp)==len(cp) and len(rf)==len(cf)
 canonical={p:i for i,p in enumerate(sorted(set(rp)))}
 mapped=[];maximum=0.0
 for p in cp:
  q=min(canonical,key=lambda q:math.dist(p,q));distance=math.dist(p,q)
  assert distance<tolerance,(p,q,distance)
  maximum=max(maximum,distance);mapped.append(canonical[q])
 expected=sorted(tuple(sorted(canonical[rp[i]] for i in f)) for f in rf)
 actual=sorted(tuple(sorted(mapped[i] for i in f)) for f in cf)
 assert expected==actual,'Matched vertices do not form the same polygon surfaces'
 return maximum
def components(obj):
 adj=[set() for _ in obj.data.vertices]
 for e in obj.data.edges:
  a,b=e.vertices;adj[a].add(b);adj[b].add(a)
 seen=set();result=[]
 for start in range(len(adj)):
  if start in seen:continue
  stack=[start];comp=set()
  while stack:
   i=stack.pop()
   if i in comp:continue
   comp.add(i);stack.extend(adj[i]-comp)
  seen.update(comp);result.append(comp)
 return result
def find_object(suffix):
 name='SM_Walk_NorthwestRearWing_'+suffix
 obj=bpy.data.objects.get(name)
 assert obj and obj.type=='MESH',name
 return obj
source_before=digest(source)
bpy.ops.wm.open_mainfile(filepath=str(source))
source_sigs={k:signature(find_object(k)) for k in targets}
source_surfaces={k:surface(find_object(k)) for k in targets}
reference_report={}
for suffix,(actor,path) in targets.items():
 assert path.is_file(),str(path)
 bpy.ops.wm.read_factory_settings(use_empty=True)
 bpy.ops.import_scene.fbx(filepath=str(path))
 obj=find_object(suffix);sig=signature(obj)
 max_distance=verify_surface(source_surfaces[suffix],surface(obj))
 reference_report[suffix]={'actor':actor,'live_mesh':scene[actor]['mesh'],'reference_fbx':str(path),'reference_sha256':digest(path),'source_surface_sha256_at_1mm':source_sigs[suffix],'reference_surface_sha256_at_1mm':sig,'verification':'equal vertex and face counts; every vertex within tolerance; all mapped polygon surfaces equal','tolerance_m':.00002,'maximum_vertex_distance_m':max_distance,'matches_live_import_source':True}
bpy.ops.wm.open_mainfile(filepath=str(source))
facebox=[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
def normalize(v):
 q=round(v,5)
 return 0.0 if abs(q)<.00002 else q
def cut_box(box,cut):
 (a,b),(v0,v1),(z0,z1)=box;ca,cb,cz0,cz1=cut
 ia,ib=max(a,ca),min(b,cb);iz0,iz1=max(z0,cz0),min(z1,cz1)
 if ib-ia<1e-7 or iz1-iz0<1e-7:return [box]
 pieces=[]
 if ia-a>1e-7:pieces.append([[a,ia],[v0,v1],[z0,z1]])
 if b-ib>1e-7:pieces.append([[ib,b],[v0,v1],[z0,z1]])
 if iz0-z0>1e-7:pieces.append([[ia,ib],[v0,v1],[z0,iz0]])
 if z1-iz1>1e-7:pieces.append([[ia,ib],[v0,v1],[iz1,z1]])
 return pieces
results=[];new_objects=[]
for suffix in targets:
 obj=find_object(suffix);old=obj.data;pts=[campus(obj.matrix_world@v.co) for v in old.vertices]
 selected=[];removed=set();new_boxes=[]
 for comp in components(obj):
  bounds=[[normalize(min(pts[i][axis] for i in comp)),normalize(max(pts[i][axis] for i in comp))] for axis in range(3)]
  if bounds[1][0]<30.2 or bounds[1][1]>30.6:continue
  pieces=[bounds]
  for cut in cuts:pieces=[piece for current in pieces for piece in cut_box(current,cut)]
  if pieces==[bounds]:continue
  faces=[p for p in old.polygons if any(i in comp for i in p.vertices)]
  assert len(comp)==8 and len(faces)==6,(suffix,bounds,len(comp),len(faces))
  assert all(set(p.vertices)<=comp for p in faces)
  removed.update(comp);new_boxes.extend(pieces);selected.append({'original_vertex_indices':sorted(comp),'original_face_indices':[p.index for p in faces],'original_bounds_campus_m':bounds,'replacement_boxes_campus_m':pieces})
 assert selected,suffix
 kept=[i for i in range(len(old.vertices)) if i not in removed];remap={i:j for j,i in enumerate(kept)}
 verts=[tuple(old.vertices[i].co) for i in kept]
 faces=[];mat_indices=[];uv_rows={layer.name:[] for layer in old.uv_layers}
 kept_polygons=[p for p in old.polygons if not any(i in removed for i in p.vertices)]
 for p in kept_polygons:
  faces.append(tuple(remap[i] for i in p.vertices));mat_indices.append(p.material_index)
  for layer in old.uv_layers:uv_rows[layer.name].extend(tuple(layer.data[i].uv) for i in p.loop_indices)
 inv=obj.matrix_world.inverted()
 for (a,b),(v0,v1),(z0,z1) in new_boxes:
  points=[(a,v0,z0),(b,v0,z0),(b,v1,z0),(a,v1,z0),(a,v0,z1),(b,v0,z1),(b,v1,z1),(a,v1,z1)]
  start=len(verts);verts.extend(tuple(inv@world(p)) for p in points)
  faces.extend(tuple(start+i for i in face) for face in facebox);mat_indices.extend([0]*6)
  for layer in old.uv_layers:
   for fi,face in enumerate(facebox):
    for i in face:
     u,v,h=points[i];uv_rows[layer.name].append((u,v) if fi in [0,1] else ((u,h) if fi in [2,4] else (v,h)))
 mesh=bpy.data.meshes.new('RearShutterPatch_'+suffix);mesh.from_pydata(verts,[],faces);mesh.update()
 for material in old.materials:mesh.materials.append(material)
 for p,index in zip(mesh.polygons,mat_indices):p.material_index=index
 for name,values in uv_rows.items():
  layer=mesh.uv_layers.new(name=name);assert len(layer.data)==len(values)
  for item,uv in zip(layer.data,values):item.uv=uv
 # All untouched original coordinates, polygon order and UV loops remain exact.
 assert all(tuple(mesh.vertices[remap[i]].co)==tuple(old.vertices[i].co) for i in kept)
 for j,p in enumerate(kept_polygons):
  assert tuple(mesh.polygons[j].vertices)==tuple(remap[i] for i in p.vertices)
  mesh.polygons[j].use_smooth=p.use_smooth
  for layer in old.uv_layers:
   for new_li,old_li in zip(mesh.polygons[j].loop_indices,p.loop_indices):assert tuple(mesh.uv_layers[layer.name].data[new_li].uv)==tuple(layer.data[old_li].uv)
 patched=bpy.data.objects.new('SM_DiningRearAperture_'+suffix,mesh);bpy.context.collection.objects.link(patched);patched.matrix_world=obj.matrix_world.copy();new_objects.append(patched)
 # No positive-volume piece remains in either aperture; unchanged pieces were
 # excluded by intersection or retained outside the specified facade strip.
 for box in new_boxes:
  for cut in cuts:assert cut_box(box,cut)==[box]
 actor=targets[suffix][0]
 results.append({'suffix':suffix,'actor_name':actor,'actor_label':scene[actor]['label'],'original_live_mesh':scene[actor]['mesh'],'original_material_paths':scene[actor]['materials'],'original_actor_transform':scene[actor]['transform'],'replacement_object':patched.name,'original_vertices':len(old.vertices),'original_faces':len(old.polygons),'unchanged_original_vertices':len(kept),'unchanged_original_faces':len(kept_polygons),'patched_components':selected,'new_vertices':len(mesh.vertices),'new_faces':len(mesh.polygons),'materials':[m.name for m in mesh.materials],'untouched_geometry_and_uv_exact':True})
for obj in list(bpy.data.objects):
 if obj not in new_objects:bpy.data.objects.remove(obj,do_unlink=True)
bpy.context.scene.unit_settings.system='METRIC';bpy.context.scene.unit_settings.scale_length=1
bpy.ops.object.select_all(action='DESELECT')
for obj in new_objects:obj.select_set(True)
fbx=out/'ATS_DiningRearApertures.fbx';blend=out/'ATS_DiningRearApertures.blend'
bpy.ops.export_scene.fbx(filepath=str(fbx),use_selection=True,object_types={'MESH'},apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',axis_forward='-Z',axis_up='Y',mesh_smooth_type='FACE',add_leaf_bones=False,bake_anim=False,path_mode='STRIP')
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(blend))
expected_export={obj.name:surface(obj) for obj in new_objects}
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.fbx(filepath=str(fbx))
roundtrip={};trees=[]
for name,expected in expected_export.items():
 obj=bpy.data.objects[name]
 roundtrip[name]={'maximum_vertex_distance_m':verify_surface(expected,surface(obj)),'polygon_surfaces_match':True}
 points,faces=surface(obj);trees.append(BVHTree.FromPolygons(points,faces,all_triangles=False))
tested=0
for a,b,z0,z1 in cuts:
 for ui in range(41):
  for zi in range(29):
   u=a+.02+(b-a-.04)*ui/40;h=z0+.02+(z1-z0-.04)*zi/28
   origin=world((u,30.0,h));target=world((u,30.8,h));direction=(target-origin).normalized()
   assert all(tree.ray_cast(origin,direction,.8)[0] is None for tree in trees),(u,h,'facade aperture obstructed')
   tested+=1
assert digest(source)==source_before
report={'status':'passed','source_blend':str(source),'source_sha256':source_before,'source_unchanged':True,'cuts_campus_m':[{'u':[a,b],'v':'full local facade thickness between 30.2 and 30.6','h':[z0,z1]} for a,b,z0,z1 in cuts],'live_source_verification':reference_report,'patches':results,'untouched_groups':['White including G columns at u6/12/18,v28.25','TerrazzoRose floor slabs','PinkTile','AnnexPlaster','WeatheredRoof'],'upper_floors_unchanged':True,'original_other_ground_floor_geometry_preserved':True,'fbx_roundtrip_verification':roundtrip,'aperture_ray_verification':{'tested':tested,'obstructions':0,'plane_v_m':[30.0,30.8],'coverage':'41 columns by 29 heights per aperture, 20 mm inside opening borders'},'outputs':{'fbx':str(fbx),'blend':str(blend)},'warning':'Existing hidden UE rear-wing access boundary begins v30.45; it is not part of these meshes and is not modified here.'}
(out/'aperture_manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print('REAR_APERTURES_PASSED',json.dumps([{'suffix':x['suffix'],'cut_components':len(x['patched_components']),'unchanged_faces':x['unchanged_original_faces']} for x in results]))
