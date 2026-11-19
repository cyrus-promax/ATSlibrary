import unreal,pathlib,json
fa_root=pathlib.Path('D:/Cyrus/OneDrive/文件/香港仔工業學校/ATS');fa_out=fa_root/'SourceAssets/Dining/FullGroundFloor_20261108/RearShutterApertures'
fa_manifest=json.loads((fa_out/'aperture_manifest.json').read_text(encoding='utf-8'));assert fa_manifest['status']=='passed'
fa_sub=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);fa_path='/Game/ATS/Dining/FullGroundFloor_20261108/RearShutterApertures'
assert not unreal.EditorAssetLibrary.does_directory_exist(fa_path),'Inspect prior import before retry.'
fa_actors={a.get_name():a for a in fa_sub.get_all_level_actors()};fa_changed=[]
fa_meshes=fi_import(fa_out/'ATS_DiningRearApertures.fbx',fa_path);assert len(fa_meshes)==3
for fa_patch in fa_manifest['patches']:
 fa_actor=fa_actors[fa_patch['actor_name']];assert fa_actor.static_mesh_component.static_mesh.get_path_name()==fa_patch['original_live_mesh']
 fa_mesh=next(m for m in fa_meshes if m.get_name().endswith(fa_patch['replacement_object']))
 fa_original_bounds=fa_actor.get_actor_bounds(False)
 for fa_i,fa_material in enumerate(fa_patch['original_material_paths']):fa_mesh.set_material(fa_i,unreal.load_asset(fa_material))
 fa_mesh.get_editor_property('body_setup').set_editor_property('collision_trace_flag',unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
 fa_actor.modify();fa_actor.static_mesh_component.set_static_mesh(fa_mesh);fa_new_bounds=fa_actor.get_actor_bounds(False)
 assert all(abs(getattr(old,k)-getattr(new,k))<.2 for old,new in zip(fa_original_bounds,fa_new_bounds) for k in ['x','y','z']),fa_patch['suffix']
 fa_changed.append(fa_actor.get_name())
fa_boundary=fa_actors['StaticMeshActor_148'];assert fa_boundary.get_actor_label()=='Unmodeled Area Boundary | Rear wing unmodeled interior'
fa_boundary_mesh=fi_import(fa_out/'ATS_Dining_RearBoundaryClearance.fbx',fa_path)[0]
fa_boundary_mesh.get_editor_property('body_setup').set_editor_property('collision_trace_flag',unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
fa_boundary.modify();fa_boundary.static_mesh_component.set_static_mesh(fa_boundary_mesh);fa_boundary.set_actor_transform(unreal.Transform(),False,True)
fa_boundary.set_actor_hidden_in_game(True);fa_boundary.static_mesh_component.set_visibility(False);fa_boundary.static_mesh_component.set_collision_profile_name('BlockAll');fa_boundary.static_mesh_component.set_collision_enabled(unreal.CollisionEnabled.QUERY_AND_PHYSICS);fa_changed.append(fa_boundary.get_name())
assert unreal.EditorAssetLibrary.save_directory(fa_path,only_if_is_dirty=True,recursive=True);assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
fa_scene=json.loads((fa_root/'dining_full_floor_scene.json').read_text(encoding='utf-8'));fa_scene['changed_actors']+=fa_changed;fa_scene['unaffected_actors_verified']-=len(fa_changed);fa_scene['rear_aperture_patches']=fa_changed;fa_scene['unknown_rear_interiors_not_built']=True;fa_scene['limited_threshold_clearance_v']=[30.45,32.1]
fa_before=json.loads((pathlib.Path(fa_scene['backup'])/'scene_before.json').read_text(encoding='utf-8'));fa_after={a.get_name():a for a in fa_sub.get_all_level_actors()}
for fa_name,fa_row in fa_before.items():
 if fa_name not in fa_scene['changed_actors']+fa_scene['removed_swing_doors']:assert fi_snapshot(fa_after[fa_name])==fa_row,fa_name
(fa_root/'dining_full_floor_scene.json').write_text(json.dumps(fa_scene,ensure_ascii=False,indent=2),encoding='utf-8')
print('REAR_SHUTTER_APERTURES_SAVED',fa_changed)
