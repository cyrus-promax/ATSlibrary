import unreal,pathlib,json
wj_root=pathlib.Path('D:/Cyrus/OneDrive/文件/香港仔工業學校/ATS');wj_out=wj_root/'SourceAssets/Dining/WallFloorDetail_20261108';wj_path='/Game/ATS/Dining/WallFloorDetail_20261108/Meshes'
wj_ed=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem);wj_sub=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
assert not wj_ed.get_game_world() and not unreal.EditorAssetLibrary.does_directory_exist(wj_path)
wj_actor=next(a for a in wj_sub.get_all_level_actors() if a.get_actor_label()=='餐廳實體｜Tiles');wj_comp=wj_actor.static_mesh_component
wj_before=wj_comp.static_mesh.get_path_name();wj_mats={str(slot.get_editor_property('imported_material_slot_name')):wj_comp.get_material(i) for i,slot in enumerate(wj_comp.static_mesh.get_editor_property('static_materials'))}
wj_opts=unreal.FbxImportUI();wj_opts.import_mesh=True;wj_opts.import_as_skeletal=False;wj_opts.import_materials=False;wj_opts.import_textures=False;wj_opts.import_animations=False;wj_opts.automated_import_should_detect_type=False;wj_opts.mesh_type_to_import=unreal.FBXImportType.FBXIT_STATIC_MESH
wj_data=wj_opts.static_mesh_import_data;wj_data.combine_meshes=False;wj_data.auto_generate_collision=False;wj_data.transform_vertex_to_absolute=True;wj_data.convert_scene_unit=True;wj_data.generate_lightmap_u_vs=False;wj_data.normal_import_method=unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS
wj_task=unreal.AssetImportTask();wj_task.filename=str(wj_out/'SM_Dining_WallFloorJoinedPanels.fbx');wj_task.destination_path=wj_path;wj_task.automated=True;wj_task.replace_existing=False;wj_task.save=False;wj_task.options=wj_opts;wj_task.factory=unreal.FbxFactory()
unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([wj_task]);wj_meshes=[o for o in wj_task.get_objects() if isinstance(o,unreal.StaticMesh)];assert len(wj_meshes)==1;wj_mesh=wj_meshes[0]
wj_list=[wj_mats[str(slot.get_editor_property('imported_material_slot_name'))] for slot in wj_mesh.get_editor_property('static_materials')]
for wj_i,wj_m in enumerate(wj_list):wj_mesh.set_material(wj_i,wj_m)
wj_actor.modify();wj_comp.set_static_mesh(wj_mesh);wj_comp.set_editor_property('override_materials',[])
for wj_i,wj_m in enumerate(wj_list):wj_comp.set_material(wj_i,wj_m)
wj_comp.set_collision_profile_name('NoCollision');wj_comp.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION);wj_comp.set_editor_property('cast_shadow',False)
assert unreal.EditorAssetLibrary.save_directory(wj_path,only_if_is_dirty=True,recursive=True);assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
wj_report=json.loads((wj_out/'application.json').read_text(encoding='utf-8'));wj_report['mesh_change']={'actor':wj_actor.get_name(),'before':wj_before,'after':wj_mesh.get_path_name()}
(wj_out/'application.json').write_text(json.dumps(wj_report,ensure_ascii=False,indent=2),encoding='utf-8');print('WALL_FLOOR_JOIN_IMPORTED')
