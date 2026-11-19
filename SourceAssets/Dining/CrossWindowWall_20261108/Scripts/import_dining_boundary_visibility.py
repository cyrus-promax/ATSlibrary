import unreal,pathlib,json
bv_root=pathlib.Path('D:/Cyrus/OneDrive/文件/香港仔工業學校/ATS');bv_out=bv_root/'SourceAssets/Dining/CrossWindowWall_20261108';bv_dir=bv_out/'BoundaryProxyCorrection';bv_path='/Game/ATS/Dining/CrossWindowWall_20261108/BoundaryProxyCorrection'
bv_ed=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem);bv_sub=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
assert not bv_ed.get_game_world() and not unreal.EditorAssetLibrary.does_directory_exist(bv_path)
bv_a=next(a for a in bv_sub.get_all_level_actors() if a.get_name()=='StaticMeshActor_187');bv_old=bv_a.static_mesh_component.static_mesh.get_path_name();bv_mat=bv_a.static_mesh_component.get_material(0)
bv_opts=unreal.FbxImportUI();bv_opts.import_mesh=True;bv_opts.import_as_skeletal=False;bv_opts.import_materials=False;bv_opts.import_textures=False;bv_opts.import_animations=False;bv_opts.automated_import_should_detect_type=False;bv_opts.mesh_type_to_import=unreal.FBXImportType.FBXIT_STATIC_MESH
bv_data=bv_opts.static_mesh_import_data;bv_data.combine_meshes=False;bv_data.auto_generate_collision=False;bv_data.transform_vertex_to_absolute=True;bv_data.convert_scene_unit=True;bv_data.generate_lightmap_u_vs=False;bv_data.normal_import_method=unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS
bv_task=unreal.AssetImportTask();bv_task.filename=str(bv_dir/'ATS_Dining_BoundaryVisibility.fbx');bv_task.destination_path=bv_path;bv_task.automated=True;bv_task.replace_existing=False;bv_task.save=False;bv_task.options=bv_opts;bv_task.factory=unreal.FbxFactory()
unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([bv_task]);bv_meshes={o.get_name().split('SM_DiningBoundary_')[-1]:o for o in bv_task.get_objects() if isinstance(o,unreal.StaticMesh)}
assert set(bv_meshes)=={'RetainedOtherSections','NonVisualWestCollision'},list(bv_meshes)
for bv_mesh in bv_meshes.values():bv_mesh.set_material(0,bv_mat);bv_mesh.get_editor_property('body_setup').set_editor_property('collision_trace_flag',unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
bv_a.modify();bv_a.static_mesh_component.set_static_mesh(bv_meshes['RetainedOtherSections'])
bv_hidden=bv_sub.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector());bv_hidden.set_actor_label('非實景｜西側未建區隱形遊戲邊界');bv_hidden.set_folder_path('Campus/NonVisualBoundaries');bv_hidden.tags=[unreal.Name('ATS.NonVisualBoundary'),unreal.Name('ATS.Dining.CrossWindowWall')]
bv_comp=bv_hidden.static_mesh_component;bv_comp.set_static_mesh(bv_meshes['NonVisualWestCollision']);bv_comp.set_collision_profile_name('BlockAll');bv_comp.set_collision_enabled(unreal.CollisionEnabled.QUERY_AND_PHYSICS);bv_comp.set_editor_property('visible',False);bv_comp.set_editor_property('cast_shadow',False);bv_hidden.set_actor_hidden_in_game(True)
assert unreal.EditorAssetLibrary.save_directory(bv_path,only_if_is_dirty=True,recursive=True)
assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
bv_report=json.loads((bv_out/'import_result.json').read_text(encoding='utf-8'))
bv_report['changes'].append({'actor':bv_a.get_name(),'role':'BoundaryRetained','before':bv_old,'after':bv_meshes['RetainedOtherSections'].get_path_name()})
bv_report['added'].append({'actor':bv_hidden.get_name(),'role':'BoundaryCollision','mesh':bv_meshes['NonVisualWestCollision'].get_path_name()})
bv_report.update(actor_count=len(bv_sub.get_all_level_actors()),unverified_west_stone_proxy_removed_visually=True,original_west_boundary_collision_preserved=True)
(bv_out/'import_result.json').write_text(json.dumps(bv_report,ensure_ascii=False,indent=2),encoding='utf-8')
print('BOUNDARY_VISIBLE_PROXY_REMOVED',bv_hidden.get_name())
