import unreal,pathlib,json,re,hashlib,datetime
lw_root=pathlib.Path('D:/Cyrus/OneDrive/文件/香港仔工業學校/ATS');lw_out=lw_root/'SourceAssets/LibraryWorkshop_20261108';lw_stage='/Game/ATS/LibraryWorkshop_20261108'
lw_tools=unreal.AssetToolsHelpers.get_asset_tools();lw_lib=unreal.EditorAssetLibrary
lw_import_sources=['Architecture','Furniture']
lw_result=json.loads((lw_out/'mesh_import_report.json').read_text(encoding='utf-8')) if (lw_out/'mesh_import_report.json').exists() else {'groups':{}}
for group in lw_import_sources:
 src=lw_out/(group+'.fbx');data=json.loads((lw_out/(group.lower()+'_manifest.json')).read_text(encoding='utf-8'));expected={x['name']:x for x in data['meshes']}
 destination=lw_stage+'/Meshes/'+group
 existing=lw_lib.list_assets(destination,recursive=False) if lw_lib.does_directory_exist(destination) else []
 if existing:
  assert group in lw_result['groups'] and destination.startswith('/Game/ATS/LibraryWorkshop_20261108/Meshes/'),destination
 opt=unreal.FbxImportUI();opt.import_mesh=True;opt.import_as_skeletal=False;opt.import_materials=False;opt.import_textures=False;opt.import_animations=False;opt.automated_import_should_detect_type=False;opt.mesh_type_to_import=unreal.FBXImportType.FBXIT_STATIC_MESH
 opts=opt.static_mesh_import_data;opts.combine_meshes=False;opts.auto_generate_collision=False;opts.transform_vertex_to_absolute=True;opts.convert_scene_unit=True;opts.generate_lightmap_u_vs=False;opts.normal_import_method=unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS
 task=unreal.AssetImportTask();task.filename=str(src);task.destination_path=destination;task.automated=True;task.replace_existing=bool(existing);task.replace_existing_settings=True;task.save=False;task.options=opt;task.factory=unreal.FbxFactory()
 lw_tools.import_asset_tasks([task]);meshes=[o for o in task.get_objects() if isinstance(o,unreal.StaticMesh)]
 assert len(meshes)==len(expected),(group,len(meshes),len(expected))
 records=[]
 for mesh in meshes:
  name=re.search('SM_LW_.*',mesh.get_name()).group();assert name in expected,name;item=expected[name]
  body=mesh.get_editor_property('body_setup');body.set_editor_property('collision_trace_flag',unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
  slots=[str(s.get_editor_property('imported_material_slot_name')) for s in mesh.get_editor_property('static_materials')]
  assert slots==[item['material']],(name,slots,item['material'])
  box=mesh.get_bounding_box();bounds={'min':[box.min.x,box.min.y,box.min.z],'max':[box.max.x,box.max.y,box.max.z]}
  if 'bounds_m' in item:
   mn=item['bounds_m']['min'];mx=item['bounds_m']['max'];expect=[mn[0]*100,-mx[1]*100,mn[2]*100,mx[0]*100,-mn[1]*100,mx[2]*100]
   error=max(abs(a-b) for a,b in zip(bounds['min']+bounds['max'],expect));assert error<.1,(name,error,bounds,expect)
  records.append({'name':name,'asset':mesh.get_path_name(),'module':item['module'],'material_slots':slots,'collision':item['collision'],'bounds_cm':bounds})
 current_paths={m.get_path_name().split('.')[0] for m in meshes}
 for stale in existing:
  if stale.split('.')[0] not in current_paths:
   assert stale.startswith(destination+'/')
   assert lw_lib.delete_asset(stale)
 assert lw_lib.save_directory(destination,only_if_is_dirty=True,recursive=True)
 lw_result['groups'][group]={'fbx':str(src),'sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'mesh_count':len(meshes),'meshes':records}
 (lw_out/'mesh_import_report.json').write_text(json.dumps(lw_result,ensure_ascii=False,indent=2),encoding='utf-8')
 print('WORKSHOP_MESH_IMPORT',group,len(meshes))
