import unreal,pathlib,json,re,hashlib
ad_root=pathlib.Path('D:/Cyrus/OneDrive/文件/香港仔工業學校/ATS/SourceAssets/LibraryWorkshop_20261108');ad_stage='/Game/ATS/LibraryWorkshop_20261108'
ad_ed=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem);ad_sub=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);ad_sme=unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
assert ad_ed.get_editor_world().get_name()=='ATS_Library_Workshop' and not ad_ed.get_game_world()
ad_lib=unreal.EditorAssetLibrary;ad_tools=unreal.AssetToolsHelpers.get_asset_tools();ad_ml=unreal.MaterialEditingLibrary
ad_materials=json.loads((ad_root/'materials_import_report.json').read_text(encoding='utf-8'));ad_mats={k:ad_lib.load_asset(v) for k,v in ad_materials['materials'].items()}
ad_new={'LW_SignGold':((.53,.33,.095),.48,.25),'LW_PlantDark':((.025,.08,.018),.66,0),'LW_PlantLight':((.105,.245,.045),.65,0)}
for key,(colour,rough,metal) in ad_new.items():
 path=ad_stage+'/Materials/M_'+key
 m=ad_lib.load_asset(path) if ad_lib.does_asset_exist(path) else ad_tools.create_asset('M_'+key,ad_stage+'/Materials',unreal.Material,unreal.MaterialFactoryNew())
 ad_ml.delete_all_material_expressions(m);n=ad_ml.create_material_expression(m,unreal.MaterialExpressionConstant3Vector,0,0);n.set_editor_property('constant',unreal.LinearColor(*colour,1));assert ad_ml.connect_material_property(n,'',unreal.MaterialProperty.MP_BASE_COLOR)
 for val,prop in [(rough,unreal.MaterialProperty.MP_ROUGHNESS),(metal,unreal.MaterialProperty.MP_METALLIC)]:
  n=ad_ml.create_material_expression(m,unreal.MaterialExpressionConstant,0,0);n.set_editor_property('r',val);assert ad_ml.connect_material_property(n,'',prop)
 if 'Plant' in key:m.set_editor_property('two_sided',True)
 ad_ml.recompile_material(m);ad_mats[key]=m;ad_materials['materials'][key]=m.get_path_name()
ad_mats['LW_Plant'].set_editor_property('two_sided',True);ad_ml.recompile_material(ad_mats['LW_Plant'])
ad_report=json.loads((ad_root/'mesh_import_report.json').read_text(encoding='utf-8'));ad_added=[]
for group,manifest_file in [('Addons','addons_manifest.json'),('PlantDetail','plant_detail_manifest.json')]:
 data=json.loads((ad_root/manifest_file).read_text(encoding='utf-8'));src=ad_root/(group+'.fbx');expected={r['name']:r for r in data['meshes']};destination=ad_stage+'/Meshes/'+group
 assert not ad_lib.does_directory_exist(destination),destination
 opt=unreal.FbxImportUI();opt.import_mesh=True;opt.import_as_skeletal=False;opt.import_materials=False;opt.import_textures=False;opt.import_animations=False;opt.automated_import_should_detect_type=False;opt.mesh_type_to_import=unreal.FBXImportType.FBXIT_STATIC_MESH
 d=opt.static_mesh_import_data;d.combine_meshes=False;d.auto_generate_collision=False;d.transform_vertex_to_absolute=True;d.convert_scene_unit=True;d.generate_lightmap_u_vs=False;d.normal_import_method=unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS
 t=unreal.AssetImportTask();t.filename=str(src);t.destination_path=destination;t.automated=True;t.save=False;t.replace_existing=False;t.options=opt;t.factory=unreal.FbxFactory();ad_tools.import_asset_tasks([t]);meshes=[m for m in t.get_objects() if isinstance(m,unreal.StaticMesh)];assert len(meshes)==len(expected)
 rows=[]
 for mesh in meshes:
  name=re.search('SM_LW_.*',mesh.get_name()).group();item=expected[name];slots=[str(s.get_editor_property('imported_material_slot_name')) for s in mesh.get_editor_property('static_materials')]
  for i,key in enumerate(slots):mesh.set_material(i,ad_mats[key])
  settings=ad_sme.get_lod_build_settings(mesh,0);settings.set_editor_property('use_full_precision_u_vs',True);settings.set_editor_property('use_high_precision_tangent_basis',True);ad_sme.set_lod_build_settings(mesh,0,settings)
  a=ad_sub.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector());a.set_actor_label(name);a.set_folder_path('LibraryWorkshop/'+item['module']);a.tags=[unreal.Name('ATS.LibraryWorkshop'),unreal.Name('ATS.LibraryWorkshop.'+item['module'])];a.static_mesh_component.set_static_mesh(mesh);a.static_mesh_component.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
  if group=='PlantDetail':a.static_mesh_component.set_editor_property('cast_shadow',False)
  parent=next(p for p in ad_sub.get_all_level_actors() if p.get_actor_label()=='LW_ROOT_'+item['module']);assert a.attach_to_actor(parent,unreal.Name('None'),unreal.AttachmentRule.KEEP_WORLD,unreal.AttachmentRule.KEEP_WORLD,unreal.AttachmentRule.KEEP_WORLD,False)
  ad_added.append(name);b=mesh.get_bounding_box();rows.append({'name':name,'asset':mesh.get_path_name(),'module':item['module'],'material_slots':slots,'collision':False,'bounds_cm':{'min':[b.min.x,b.min.y,b.min.z],'max':[b.max.x,b.max.y,b.max.z]}})
 ad_report['groups'][group]={'fbx':str(src),'sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'mesh_count':len(meshes),'meshes':rows}
ad_removed=[]
for a in list(ad_sub.get_all_level_actors()):
 if a.get_actor_label()=='SM_LW_Step_Plants_Plant':
  assert 'ATS.LibraryWorkshop' in [str(t) for t in a.tags];ad_removed.append(a.get_actor_label());assert ad_sub.destroy_actor(a)
assert len(ad_removed)==1
assert ad_lib.save_directory(ad_stage,only_if_is_dirty=True,recursive=True);assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
(ad_root/'mesh_import_report.json').write_text(json.dumps(ad_report,ensure_ascii=False,indent=2),encoding='utf-8')
(ad_root/'materials_import_report.json').write_text(json.dumps(ad_materials,ensure_ascii=False,indent=2),encoding='utf-8')
(ad_root/'scene_detail_overrides.json').write_text(json.dumps({'added':ad_added,'removed_old_geometry':ad_removed,'reason':'Photo visible culture plaque and higher detail hanging foliage.'},ensure_ascii=False,indent=2),encoding='utf-8')
print('LW_DETAIL_COMPLETE',len(ad_added))
