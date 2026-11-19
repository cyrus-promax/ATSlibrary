import unreal,pathlib,json,re
ls_root=pathlib.Path('D:/Cyrus/OneDrive/文件/香港仔工業學校/ATS');ls_out=ls_root/'SourceAssets/Dining/PhotoFinishes_20261108'
ls_prep=json.loads((ls_out/'preparation.json').read_text(encoding='utf-8'))
ls_ed=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem);ls_sub=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
assert not ls_ed.get_game_world() and ls_ed.get_editor_world().get_name()=='ATS_StudentCampus'
ls_assetpath='/Game/ATS/Dining/PhotoFinishes_20261108/Meshes'
assert not unreal.EditorAssetLibrary.does_directory_exist(ls_assetpath),'Inspect existing import before retry.'
ls_opts=unreal.FbxImportUI();ls_opts.import_mesh=True;ls_opts.import_as_skeletal=False;ls_opts.import_materials=False;ls_opts.import_textures=False;ls_opts.import_animations=False;ls_opts.automated_import_should_detect_type=False;ls_opts.mesh_type_to_import=unreal.FBXImportType.FBXIT_STATIC_MESH
ls_data=ls_opts.static_mesh_import_data;ls_data.combine_meshes=False;ls_data.auto_generate_collision=False;ls_data.transform_vertex_to_absolute=True;ls_data.convert_scene_unit=True;ls_data.generate_lightmap_u_vs=False;ls_data.normal_import_method=unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS
ls_task=unreal.AssetImportTask();ls_task.filename=str(ls_out/'SM_Dining_LongWashbasin.fbx');ls_task.destination_path=ls_assetpath;ls_task.automated=True;ls_task.replace_existing=False;ls_task.save=False;ls_task.options=ls_opts;ls_task.factory=unreal.FbxFactory()
unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([ls_task])
ls_meshes=[o for o in ls_task.get_objects() if isinstance(o,unreal.StaticMesh)];assert len(ls_meshes)==1
ls_mesh=ls_meshes[0]
for ls_i,ls_slot in enumerate(ls_mesh.get_editor_property('static_materials')):
 ls_mat=unreal.load_asset('/Game/ATS/Dining/BuiltFromUserPlan/Materials/'+str(ls_slot.get_editor_property('imported_material_slot_name')));assert ls_mat;ls_mesh.set_material(ls_i,ls_mat)
ls_mesh.get_editor_property('body_setup').set_editor_property('collision_trace_flag',unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
ls_a=next(a for a in ls_sub.get_all_level_actors() if a.get_actor_label()=='餐廳實體｜Washbasin')
ls_old=ls_a.static_mesh_component.static_mesh.get_path_name();ls_a.modify();ls_a.static_mesh_component.set_static_mesh(ls_mesh)
ls_a.static_mesh_component.set_collision_profile_name('BlockAll');ls_a.static_mesh_component.set_collision_enabled(unreal.CollisionEnabled.QUERY_AND_PHYSICS)
assert unreal.EditorAssetLibrary.save_directory(ls_assetpath,only_if_is_dirty=True,recursive=True)
assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
(ls_out/'sink_import.json').write_text(json.dumps({'actor':ls_a.get_name(),'old_mesh':ls_old,'new_mesh':ls_mesh.get_path_name(),'backup':ls_prep['backup'],'status':'saved'},ensure_ascii=False,indent=2),encoding='utf-8')
print('LONG_SINK_IMPORTED',ls_a.get_name(),ls_mesh.get_path_name())
