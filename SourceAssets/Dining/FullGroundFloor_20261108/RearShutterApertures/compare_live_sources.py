from pathlib import Path
import bpy,json,math,hashlib
root=Path('D:/Cyrus/OneDrive/文件/香港仔工業學校/ATS')
work=Path('C:/Users/Cyrus/Documents/Codex/2026-11-06/dao/work')
out=root/'SourceAssets/Dining/FullGroundFloor_20261108/RearShutterApertures'
targets={'Cream':work/'ATS_before_facade_detail/Walkthrough/ATS_InteriorCleanup.fbx','Metal':work/'ATS_before_structure_removal/Walkthrough/ATS_FacadeRevision.fbx','WindowShade':work/'ATS_before_unverified_interior_removal/SourceAssets/Walkthrough/ATS_Northwest_Addition.fbx'}
c,s=math.cos(math.radians(20)),math.sin(math.radians(20))
def extract(k):
 obj=bpy.data.objects['SM_Walk_NorthwestRearWing_'+k]
 points=[obj.matrix_world@v.co for v in obj.data.vertices]
 campus=[(c*(p.x+8)+s*(p.y+24),-s*(p.x+8)+c*(p.y+24),p.z+24.55) for p in points]
 adj=[set() for _ in points]
 for e in obj.data.edges:
  a,b=e.vertices;adj[a].add(b);adj[b].add(a)
 seen=set();bounds=[]
 for i in range(len(points)):
  if i in seen:continue
  comp=set();todo=[i]
  while todo:
   j=todo.pop()
   if j in comp:continue
   comp.add(j);todo.extend(adj[j]-comp)
  seen.update(comp)
  bounds.append([[round(min(campus[j][axis] for j in comp),4),round(max(campus[j][axis] for j in comp),4)] for axis in range(3)])
 return {'vertices':len(points),'faces':len(obj.data.polygons),'bounds':sorted(bounds),'world_points':sorted(tuple(p) for p in points)}
bpy.ops.wm.open_mainfile(filepath=str(root/'SourceAssets/Walkthrough/ATS_Walkthrough.blend'))
original={k:extract(k) for k in targets};result={}
for k,path in targets.items():
 bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.fbx(filepath=str(path))
 live=extract(k);src=original[k]
 result[k]={'source_vertices':src['vertices'],'live_vertices':live['vertices'],'source_faces':src['faces'],'live_faces':live['faces'],'source_only_component_bounds':[b for b in src['bounds'] if b not in live['bounds']],'live_only_component_bounds':[b for b in live['bounds'] if b not in src['bounds']]}
 if len(live['world_points'])==len(src['world_points']):
  result[k]['max_nearest_vertex_distance_m']=max(min(math.dist(p,q) for q in live['world_points']) for p in src['world_points'])
(out/'live_source_comparison.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(result))
