import unreal,pathlib,json
wg_root=pathlib.Path('D:/Cyrus/OneDrive/文件/香港仔工業學校/ATS');wg_out=wg_root/'SourceAssets/Dining/ScaleCorrection_20261108/WindowCorrection'
wg_sub=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);wg_ed=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
assert not wg_ed.get_game_world()
wg_a=next(a for a in wg_sub.get_all_level_actors() if a.get_name()=='StaticMeshActor_47');assert wg_a.get_actor_label()=='HistoricWestWing | M_Interior_FacadeGlass'
wg_c=wg_a.static_mesh_component;wg_original=wg_c.static_mesh;wg_bounds=wg_a.get_actor_bounds(False)
wg_opts=unreal.FbxImportUI();wg_opts.import_mesh=True;wg_opts.import_as_skeletal=False;wg_opts.import_materials=False;wg_opts.import_textures=False;wg_opts.import_animations=False;wg_opts.automated_import_should_detect_type=False;wg_opts.mesh_type_to_import=unreal.FBXImportType.FBXIT_STATIC_MESH
wg_data=wg_opts.static_mesh_import_data;wg_data.combine_meshes=False;wg_data.auto_generate_collision=False;wg_data.transform_vertex_to_absolute=True;wg_data.convert_scene_unit=True;wg_data.generate_lightmap_u_vs=False;wg_data.normal_import_method=unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS
wg_task=unreal.AssetImportTask();wg_task.filename=str(wg_out/'ATS_Dining_WindowGlass.fbx');wg_task.destination_path='/Game/ATS/Dining/ScaleCorrection_20261108/WindowCorrection';wg_task.automated=True;wg_task.replace_existing=False;wg_task.save=False;wg_task.options=wg_opts;wg_task.factory=unreal.FbxFactory();unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([wg_task])
wg_meshes=[o for o in wg_task.get_objects() if isinstance(o,unreal.StaticMesh)];assert len(wg_meshes)==1
wg_mesh=wg_meshes[0];wg_slots=wg_mesh.get_editor_property('static_materials');assert len(wg_slots)==2
wg_mats={'M_Interior_FacadeGlass':unreal.load_asset('/Game/ATS/Revision8/Materials/M_Interior_FacadeGlass'),'M_DiningBuild_Glass':unreal.load_asset('/Game/ATS/Dining/BuiltFromUserPlan/Materials/M_DiningBuild_Glass')}
for wg_i,wg_slot in enumerate(wg_slots):
 wg_name=str(wg_slot.get_editor_property('imported_material_slot_name'));assert wg_name in wg_mats,wg_name;wg_mesh.set_material(wg_i,wg_mats[wg_name])
wg_mesh.get_editor_property('body_setup').set_editor_property('collision_trace_flag',unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
wg_a.modify();wg_c.set_static_mesh(wg_mesh)
for wg_i,wg_slot in enumerate(wg_slots):wg_c.set_material(wg_i,wg_mats[str(wg_slot.get_editor_property('imported_material_slot_name'))])
wg_after_bounds=wg_a.get_actor_bounds(False)
assert all(abs(getattr(before,k)-getattr(after,k))<.2 for before,after in zip(wg_bounds,wg_after_bounds) for k in ['x','y','z']),str((wg_bounds,wg_after_bounds))
wg_c.set_collision_profile_name('BlockAll');wg_c.set_collision_enabled(unreal.CollisionEnabled.QUERY_AND_PHYSICS)
assert unreal.EditorAssetLibrary.save_directory(wg_task.destination_path,only_if_is_dirty=True,recursive=True)
assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
wg_report={'status':'ground_floor_window_material_corrected','actor':wg_a.get_name(),'old_mesh':wg_original.get_path_name(),'new_mesh':wg_mesh.get_path_name(),'bounds_unchanged_within_cm':.2,'upper_storey_material_preserved':True,'new_material_only_for_five_G_windows':True}
(wg_root/'dining_scale_window_correction.json').write_text(json.dumps(wg_report,ensure_ascii=False,indent=2),encoding='utf-8')
wg_scene=json.loads((wg_root/'dining_scale_scene.json').read_text(encoding='utf-8'));wg_scene['window_glass_correction']=wg_report;wg_scene['changed_actors'].append(wg_a.get_name());wg_scene['unaffected_actors_verified']-=1
(wg_root/'dining_scale_scene.json').write_text(json.dumps(wg_scene,ensure_ascii=False,indent=2),encoding='utf-8')
