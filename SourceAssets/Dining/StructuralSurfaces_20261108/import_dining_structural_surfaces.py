import unreal,pathlib,json
hs_root=pathlib.Path('D:/Cyrus/OneDrive/文件/香港仔工業學校/ATS');hs_out=hs_root/'SourceAssets/Dining/StructuralSurfaces_20261108'
hs_ed=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem);hs_sub=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
assert not hs_ed.get_game_world() and hs_ed.get_editor_world().get_name()=='ATS_StudentCampus'
hs_path='/Game/ATS/Dining/StructuralSurfaces_20261108';assert not unreal.EditorAssetLibrary.does_directory_exist(hs_path+'/Meshes')
hs_names=['M_Dining_Hall_BasketMosaic','M_Dining_Hall_CharcoalCap','M_Dining_Hall_DarkTerrazzoSkirting']
hs_mats={n:unreal.load_asset(hs_path+'/Materials/'+n) for n in hs_names};assert all(hs_mats.values())
hs_floor=unreal.load_asset(hs_path+'/Materials/M_Dining_DryTerrazzo_StableGrain');assert hs_floor
hs_opts=unreal.FbxImportUI();hs_opts.import_mesh=True;hs_opts.import_as_skeletal=False;hs_opts.import_materials=False;hs_opts.import_textures=False;hs_opts.import_animations=False;hs_opts.automated_import_should_detect_type=False;hs_opts.mesh_type_to_import=unreal.FBXImportType.FBXIT_STATIC_MESH
hs_data=hs_opts.static_mesh_import_data;hs_data.combine_meshes=False;hs_data.auto_generate_collision=False;hs_data.transform_vertex_to_absolute=True;hs_data.convert_scene_unit=True;hs_data.generate_lightmap_u_vs=False;hs_data.normal_import_method=unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS
hs_task=unreal.AssetImportTask();hs_task.filename=str(hs_out/'SM_Dining_HallSurfacePanels.fbx');hs_task.destination_path=hs_path+'/Meshes';hs_task.automated=True;hs_task.replace_existing=False;hs_task.save=False;hs_task.options=hs_opts;hs_task.factory=unreal.FbxFactory()
unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([hs_task]);hs_meshes=[o for o in hs_task.get_objects() if isinstance(o,unreal.StaticMesh)];assert len(hs_meshes)==1
hs_mesh=hs_meshes[0]
for hs_i,hs_slot in enumerate(hs_mesh.get_editor_property('static_materials')):hs_mesh.set_material(hs_i,hs_mats[str(hs_slot.get_editor_property('imported_material_slot_name'))])
hs_actor=next(a for a in hs_sub.get_all_level_actors() if a.get_actor_label()=='餐廳實體｜Tiles')
hs_oldmesh=hs_actor.static_mesh_component.static_mesh.get_path_name();hs_actor.modify();hs_actor.static_mesh_component.set_static_mesh(hs_mesh)
hs_actor.static_mesh_component.set_collision_profile_name('NoCollision');hs_actor.static_mesh_component.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION);hs_actor.static_mesh_component.set_editor_property('cast_shadow',False)
hs_changes=[{'actor':hs_actor.get_name(),'kind':'mesh','before':hs_oldmesh,'after':hs_mesh.get_path_name()}]
for hs_a in hs_sub.get_all_level_actors():
 if hs_a.get_actor_label() in ['餐廳實體｜Floor','餐廳實體｜Thresholds']:
  hs_a.modify();hs_c=hs_a.static_mesh_component
  for hs_i,hs_old in enumerate(hs_c.get_materials()):
   hs_c.set_material(hs_i,hs_floor);hs_changes.append({'actor':hs_a.get_name(),'kind':'material','slot':hs_i,'before':hs_old.get_path_name(),'after':hs_floor.get_path_name()})
assert unreal.EditorAssetLibrary.save_directory(hs_path,only_if_is_dirty=True,recursive=True)
assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
(hs_out/'surface_import.json').write_text(json.dumps({'status':'saved_pending_visual_validation','changes':hs_changes,'room_identity_confirmed_by_user':'是，就是這個大廳','floor_grid_not_invented':True,'ceiling_beam_geometry_pending_registration':True},ensure_ascii=False,indent=2),encoding='utf-8')
print('DINING_STRUCTURAL_SURFACES_IMPORTED',hs_changes)
