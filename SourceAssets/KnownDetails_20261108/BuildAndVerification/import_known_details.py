import unreal,pathlib,json,hashlib,re,datetime
kd_root=pathlib.Path('D:/Cyrus/OneDrive/文件/香港仔工業學校/ATS')
kd_out=kd_root/'SourceAssets/KnownDetails_20261108'
kd_work=pathlib.Path('C:/Users/Cyrus/Documents/Codex/2026-11-06/dao/work')
kd_stage='/Game/ATS/KnownDetails_20261108'
kd_ed=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
kd_sub=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
kd_level=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
assert not kd_ed.get_game_world() and kd_ed.get_editor_world().get_name()=='ATS_StudentCampus'
assert not (kd_out/'import_report.json').exists()
kd_before=json.loads((kd_out/'scene_before.json').read_text(encoding='utf-8'))
kd_actors={a.get_name():a for a in kd_sub.get_all_level_actors()}
assert len(kd_actors)==901
kd_frames=json.loads((kd_out/'TeachingFrames/frame_finish_manifest.json').read_text(encoding='utf-8'))
kd_ac=json.loads((kd_out/'DiningAC/ac_front_manifest.json').read_text(encoding='utf-8'))
kd_hall=json.loads((kd_out/'HallSign/hall_sign_patch_manifest.json').read_text(encoding='utf-8'))
kd_teaching=json.loads((kd_work/'research/known_parts_20261108/teaching_candidates.json').read_text(encoding='utf-8'))
kd_strips=kd_teaching['candidates'][1]['targets']
kd_targets=[r['actor_name'] for r in kd_frames['meshes']]+[r['actor_name'] for r in kd_strips]+[kd_hall['target_actor'],kd_ac['target_actor']]
assert len(set(kd_targets))==32
for n in kd_targets:assert kd_snapshot(kd_actors[n])==kd_before[n],n
for manifest in [kd_frames,kd_ac,kd_hall]:
 assert hashlib.sha256(pathlib.Path(manifest['source']).read_bytes()).hexdigest()==manifest['source_sha256_before']
kd_lib=unreal.EditorAssetLibrary;kd_assets=unreal.AssetToolsHelpers.get_asset_tools();kd_ml=unreal.MaterialEditingLibrary
kd_materials={};kd_new_materials=[]
def kd_node(m,cls):return kd_ml.create_material_expression(m,cls,-200,0)
def kd_constant(m,val,prop):
 n=kd_node(m,unreal.MaterialExpressionConstant);n.set_editor_property('r',float(val));kd_ml.connect_material_property(n,'',prop)
def kd_newmat(name):
 path=kd_stage+'/Materials/'+name
 m=kd_lib.load_asset(path) if kd_lib.does_asset_exist(path) else kd_assets.create_asset(name,kd_stage+'/Materials',unreal.Material,unreal.MaterialFactoryNew());assert m
 kd_ml.delete_all_material_expressions(m)
 kd_materials[name]=m;kd_new_materials.append(m);return m
def kd_simple(name,rgb,rough,metal=0):
 m=kd_newmat(name);n=kd_node(m,unreal.MaterialExpressionConstant3Vector);n.set_editor_property('constant',unreal.LinearColor(*rgb,1))
 kd_ml.connect_material_property(n,'',unreal.MaterialProperty.MP_BASE_COLOR)
 kd_constant(m,rough,unreal.MaterialProperty.MP_ROUGHNESS);kd_constant(m,metal,unreal.MaterialProperty.MP_METALLIC)
 kd_ml.recompile_material(m);return m
kd_simple('M_ATS_Window_OffWhitePaint',[.68,.69,.66],.38)
kd_materials['M_Interior_YellowFrame']=kd_lib.load_asset('/Game/ATS/Campus/Materials/M_Interior_YellowFrame')
for name,path in kd_ac['existing_material_map'].items():kd_materials[name]=kd_lib.load_asset(path);assert kd_materials[name]
for name,spec in kd_ac['new_material_specs'].items():kd_simple(name,spec['linear_rgb'],spec['roughness'],spec['metallic'])
kd_materials['M_Interior_Black']=kd_lib.load_asset('/Game/ATS/Campus/Materials/M_Interior_Black');assert kd_materials['M_Interior_Black']
m=kd_newmat('M_ATS_Corridor_DarkSquareMosaic');uv=kd_node(m,unreal.MaterialExpressionTextureCoordinate)
tile=.048;grout=.0015
common=f'''float2 g=UV*{2/tile:.9f};
float2 f=frac(g);float2 edge=min(f,1-f);
float2 aa=max(fwidth(g)*.65,.0001);
float2 inside=smoothstep({grout/(tile*2):.9f}-aa,{grout/(tile*2):.9f}+aa,edge);
float fade=saturate((max(aa.x,aa.y)-.15)*2.5);
float mask=lerp(inside.x*inside.y,{(1-grout/tile)**2:.9f},fade);
'''
for code,typ,prop in [(common+'return lerp(float3(.28,.285,.27),float3(.014,.019,.018),mask);',unreal.CustomMaterialOutputType.CMOT_FLOAT3,unreal.MaterialProperty.MP_BASE_COLOR),(common+'return lerp(.8,.36,mask);',unreal.CustomMaterialOutputType.CMOT_FLOAT1,unreal.MaterialProperty.MP_ROUGHNESS)]:
 n=kd_node(m,unreal.MaterialExpressionCustom);i=unreal.CustomInput();i.set_editor_property('input_name','UV');n.set_editor_property('inputs',[i]);n.set_editor_property('code',code);n.set_editor_property('output_type',typ);kd_ml.connect_material_expressions(uv,'',n,'UV');kd_ml.connect_material_property(n,'',prop)
kd_constant(m,0,unreal.MaterialProperty.MP_METALLIC);kd_ml.recompile_material(m)
def kd_import(src,subdir):
 dest=kd_stage+'/Meshes/'+subdir
 existing=[kd_lib.load_asset(p) for p in kd_lib.list_assets(dest,recursive=False)] if kd_lib.does_directory_exist(dest) else []
 if existing:
  meshes=[x for x in existing if isinstance(x,unreal.StaticMesh)]
  if subdir=='HallSign':assert len(meshes)==1;return {kd_hall['output_object']:meshes[0]}
  if subdir=='DiningAC':assert len(meshes)==1;return {kd_ac['mesh_name']:meshes[0]}
  assert len(meshes)==24;return {re.search('SM_.*',x.get_name()).group():x for x in meshes}
 opt=unreal.FbxImportUI();opt.import_mesh=True;opt.import_as_skeletal=False;opt.import_materials=False;opt.import_textures=False;opt.import_animations=False;opt.automated_import_should_detect_type=False;opt.mesh_type_to_import=unreal.FBXImportType.FBXIT_STATIC_MESH
 d=opt.static_mesh_import_data;d.combine_meshes=False;d.auto_generate_collision=False;d.transform_vertex_to_absolute=True;d.convert_scene_unit=True;d.generate_lightmap_u_vs=False;d.normal_import_method=unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS
 t=unreal.AssetImportTask();t.filename=str(src);t.destination_path=kd_stage+'/Meshes/'+subdir;t.automated=True;t.replace_existing=False;t.save=False;t.options=opt;t.factory=unreal.FbxFactory()
 kd_assets.import_asset_tasks([t]);meshes=[x for x in t.get_objects() if isinstance(x,unreal.StaticMesh)]
 if subdir=='HallSign':assert len(meshes)==1;return {kd_hall['output_object']:meshes[0]}
 if subdir=='DiningAC':assert len(meshes)==1;return {kd_ac['mesh_name']:meshes[0]}
 return {re.search('SM_.*',x.get_name()).group():x for x in meshes}
kd_fmeshes=kd_import(kd_out/'TeachingFrames/ATS_Teaching_FrameFinishes.fbx','TeachingFrames');assert len(kd_fmeshes)==24
kd_hmeshes=kd_import(kd_out/'HallSign/ATS_HallSign_ReadingOrder.fbx','HallSign');assert len(kd_hmeshes)==1
kd_ameshes=kd_import(kd_out/'DiningAC/ATS_Dining_AC_PhotoFronts.fbx','DiningAC');assert len(kd_ameshes)==1
kd_replacements={r['actor_name']:kd_fmeshes[r['new_mesh']] for r in kd_frames['meshes']}
kd_replacements[kd_hall['target_actor']]=kd_hmeshes[kd_hall['output_object']]
kd_replacements[kd_ac['target_actor']]=kd_ameshes[kd_ac['mesh_name']]
kd_report={'timestamp':datetime.datetime.now().isoformat(),'status':'prepared','targets':kd_targets,'materials':[m.get_path_name() for m in kd_new_materials],'replacements':[],'limits':['Existing classroom geometry and fixture sizes retained; no new architecture or measured full-campus 1:1 claim.','Mosaic pitch retains existing model convention, not newly measured tile size.','AC front colour zones only; unresolved grille count and labels not invented.']}
def kd_vec(v):return [float(v.x),float(v.y),float(v.z)]
for name,mesh in kd_replacements.items():
 c=kd_actors[name].static_mesh_component;old=c.static_mesh
 bs=mesh.get_editor_property('body_setup');bs.set_editor_property('collision_trace_flag',old.get_editor_property('body_setup').get_editor_property('collision_trace_flag'))
 slots=[]
 for i,slot in enumerate(mesh.get_editor_property('static_materials')):
  sn=str(slot.get_editor_property('imported_material_slot_name'));assert sn in kd_materials,(mesh.get_name(),sn);mesh.set_material(i,kd_materials[sn]);slots.append(sn)
 b1=old.get_bounding_box();b2=mesh.get_bounding_box()
 err=max(abs(x-y) for x,y in zip(kd_vec(b1.min)+kd_vec(b1.max),kd_vec(b2.min)+kd_vec(b2.max)))
 assert err<(.02 if name!=kd_ac['target_actor'] else 1.2),(name,err)
 kd_report['replacements'].append({'actor':name,'old_mesh':old.get_path_name(),'new_mesh':mesh.get_path_name(),'slots':slots,'bounds_max_delta_cm':err,'collision_trace_flag':str(bs.get_editor_property('collision_trace_flag'))})
kd_rollback={n:(kd_actors[n].static_mesh_component.static_mesh,list(kd_actors[n].static_mesh_component.get_editor_property('override_materials'))) for n in kd_targets}
try:
 for name,mesh in kd_replacements.items():
  c=kd_actors[name].static_mesh_component;c.set_static_mesh(mesh);c.set_editor_property('override_materials',[])
  for i in range(len(mesh.get_editor_property('static_materials'))):c.set_material(i,mesh.get_material(i))
 for row in kd_strips:kd_actors[row['actor_name']].static_mesh_component.set_material(0,kd_materials['M_ATS_Corridor_DarkSquareMosaic'])
 assert len(kd_sub.get_all_level_actors())==901
 assert kd_lib.save_directory(kd_stage,only_if_is_dirty=True,recursive=True)
 assert kd_level.save_current_level()
 kd_report['status']='imported_saved';kd_report['actor_count']=901
 (kd_out/'import_report.json').write_text(json.dumps(kd_report,ensure_ascii=False,indent=2),encoding='utf-8')
 print('KNOWN_DETAILS_IMPORTED_SAVED',len(kd_replacements),'mesh actors +',len(kd_strips),'material actors')
except Exception:
 for n,(mesh,mats) in kd_rollback.items():
  c=kd_actors[n].static_mesh_component;c.set_static_mesh(mesh);c.set_editor_property('override_materials',mats)
 kd_level.save_current_level();raise
