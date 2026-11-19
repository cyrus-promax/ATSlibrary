import unreal,pathlib,json,math,re
dr_root=pathlib.Path('D:/Cyrus/OneDrive/文件/香港仔工業學校/ATS')
dr_out=dr_root/'SourceAssets/Dining/ScaleCorrection_20261108'
dr_manifest=json.loads((dr_out/'construction_manifest.json').read_text(encoding='utf-8'))
dr_prep=json.loads((dr_out/'preparation.json').read_text(encoding='utf-8'))
dr_before=json.loads((pathlib.Path(dr_prep['backup'])/'scene_before.json').read_text(encoding='utf-8'))
dr_sub=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);dr_ed=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem);dr_level=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
assert not dr_ed.get_game_world() and dr_ed.get_editor_world().get_name()=='ATS_StudentCampus'
dr_path='/Game/ATS/Dining/ScaleCorrection_20261108';dr_lib=unreal.EditorAssetLibrary;dr_tools=unreal.AssetToolsHelpers.get_asset_tools()
assert not dr_lib.does_directory_exist(dr_path),'New revision already exists; inspect before retrying.'
dr_all=dr_sub.get_all_level_actors();dr_owned=[a for a in dr_all if 'ATS.Dining.BuiltFromUserPlan' in [str(t) for t in a.tags]]
assert len(dr_owned)==22,len(dr_owned)
dr_camera=dr_ed.get_level_viewport_camera_info()
dr_opts=unreal.FbxImportUI();dr_opts.import_mesh=True;dr_opts.import_as_skeletal=False;dr_opts.import_materials=False;dr_opts.import_textures=False;dr_opts.import_animations=False;dr_opts.automated_import_should_detect_type=False;dr_opts.mesh_type_to_import=unreal.FBXImportType.FBXIT_STATIC_MESH
dr_data=dr_opts.static_mesh_import_data;dr_data.combine_meshes=False;dr_data.auto_generate_collision=False;dr_data.transform_vertex_to_absolute=True;dr_data.convert_scene_unit=True;dr_data.generate_lightmap_u_vs=False;dr_data.normal_import_method=unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS
dr_task=unreal.AssetImportTask();dr_task.filename=str(dr_out/'ATS_Dining_Built.fbx');dr_task.destination_path=dr_path+'/Meshes';dr_task.automated=True;dr_task.replace_existing=False;dr_task.save=False;dr_task.options=dr_opts;dr_task.factory=unreal.FbxFactory();dr_tools.import_asset_tasks([dr_task])
dr_meshes=[o for o in dr_task.get_objects() if isinstance(o,unreal.StaticMesh)]
assert len(dr_meshes)==len(dr_manifest['meshes'])==12,len(dr_meshes)
dr_mats={}
for dr_name in dr_manifest['materials']:
 dr_key='M_DiningBuild_'+dr_name;dr_mats[dr_key]=unreal.load_asset('/Game/ATS/Dining/BuiltFromUserPlan/Materials/'+dr_key);assert dr_mats[dr_key]
dr_changed=[];dr_added=[];dr_removed=[]
for dr_mesh in dr_meshes:
 dr_key=re.search('SM_DiningBuilt_.*',dr_mesh.get_name()).group();dr_item=next(x for x in dr_manifest['meshes'] if x['name']==dr_key)
 for dr_i,dr_slot in enumerate(dr_mesh.get_editor_property('static_materials')):dr_mesh.set_material(dr_i,dr_mats[str(dr_slot.get_editor_property('imported_material_slot_name'))])
 dr_mesh.get_editor_property('body_setup').set_editor_property('collision_trace_flag',unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
 dr_a=next(a for a in dr_owned if a.get_actor_label()=='餐廳實體｜'+dr_item['group']);dr_a.modify();dr_c=dr_a.static_mesh_component;dr_c.set_static_mesh(dr_mesh)
 dr_c.set_collision_profile_name('BlockAll' if dr_item['collision'] else 'NoCollision');dr_c.set_collision_enabled(unreal.CollisionEnabled.QUERY_AND_PHYSICS if dr_item['collision'] else unreal.CollisionEnabled.NO_COLLISION)
 dr_a.set_actor_hidden_in_game(False);dr_a.set_is_temporarily_hidden_in_editor(False);dr_changed.append(dr_a.get_name())
for dr_group in ['WindowFrames','Glass']:
 dr_a=next(a for a in dr_owned if a.get_actor_label()=='餐廳實體｜'+dr_group);dr_removed.append(dr_a.get_name());assert dr_sub.destroy_actor(dr_a)
# The old roof cut followed the wrong interior strip. Restore the uncut source asset.
dr_roof=next(a for a in dr_all if a.get_actor_label()=='HistoricRoof | M_Interior_RoofConcrete')
dr_roof_original=unreal.load_asset('/Game/ATS/Revision8/Architecture/ATS_FacadeRevision_SM_Walk_HistoricRoof_RoofConcrete');assert dr_roof_original
dr_roof.modify();dr_roof.static_mesh_component.set_static_mesh(dr_roof_original);dr_changed.append(dr_roof.get_name())
dr_cos,dr_sin=math.cos(math.radians(20)),math.sin(math.radians(20))
def dr_point(p):
 u,v,h=p;return unreal.Vector((-8+dr_cos*u-dr_sin*v)*100,(24-dr_sin*u-dr_cos*v)*100,(-24.55+h)*100)
for dr_d in dr_manifest['doors']:
 dr_a=next(a for a in dr_owned if 'ATS.DiningDoor.'+dr_d['id'] in [str(t) for t in a.tags]);dr_a.modify()
 dr_a.set_actor_location_and_rotation(dr_point(dr_d['hinge']),unreal.Rotator(pitch=0,yaw=dr_d['yaw'],roll=0),False,True)
 dr_a.set_actor_scale3d(unreal.Vector(1,1,1));dr_a.set_editor_property('open_angle',dr_d['open_angle']);dr_a.set_editor_property('approach_distance',170.0);dr_changed.append(dr_a.get_name())
dr_old_lights=sorted([a for a in dr_owned if isinstance(a,unreal.RectLight)],key=lambda a:a.get_actor_label());assert len(dr_old_lights)==5
for dr_i,dr_l in enumerate(dr_manifest['lights']):
 if dr_i<len(dr_old_lights):dr_a=dr_old_lights[dr_i];dr_a.modify();dr_changed.append(dr_a.get_name())
 else:
  dr_a=dr_sub.spawn_actor_from_class(unreal.RectLight,dr_point(dr_l['campus_m']));dr_a.tags=[unreal.Name('ATS.Dining.BuiltFromUserPlan'),unreal.Name('ATS.Floor.G')];dr_a.set_folder_path('Campus/Dining');dr_added.append(dr_a.get_name())
 dr_a.set_actor_label('餐廳照明 %02d'%(dr_i+1));dr_a.set_actor_location_and_rotation(dr_point(dr_l['campus_m']),unreal.Rotator(pitch=-90,yaw=-20,roll=0),False,True);dr_c=dr_a.get_component_by_class(unreal.RectLightComponent)
 for dr_prop,dr_val in [('intensity_units',unreal.LightUnits.LUMENS),('intensity',dr_l['lumens']),('source_width',dr_l['width_cm']),('source_height',dr_l['height_cm']),('attenuation_radius',900),('use_temperature',True),('temperature',5300),('cast_shadows',True)]:dr_c.set_editor_property(dr_prop,dr_val)
 dr_c.set_mobility(unreal.ComponentMobility.MOVABLE)
assert dr_lib.save_directory(dr_path,only_if_is_dirty=True,recursive=True)
assert dr_level.save_current_level()
dr_after={a.get_name():a for a in dr_sub.get_all_level_actors()}
assert len(dr_after)==len(dr_before)+len(dr_added)-len(dr_removed)
for dr_name,dr_row in dr_before.items():
 if dr_name not in dr_changed+dr_removed:assert ds_snapshot(dr_after[dr_name])==dr_row,dr_name
assert dr_ed.get_level_viewport_camera_info()==dr_camera
dr_report={'status':'scale_correction_saved','backup':dr_prep['backup'],'actors_before':len(dr_before),'actors_after':len(dr_after),'changed_actors':dr_changed,'added_lights':dr_added,'removed_false_window_actors':dr_removed,'unaffected_actors_verified':len(dr_before)-len(set(dr_changed+dr_removed)),'room_bounds':dr_manifest['room_campus_bounds'],'room_extent_is_estimate':True,'roof_restored':dr_roof_original.get_path_name(),'original_courtyard_door_patch_preserved':True,'camera_preserved':True}
(dr_root/'dining_scale_scene.json').write_text(json.dumps(dr_report,ensure_ascii=False,indent=2),encoding='utf-8')
print('DINING_SCALE_SAVED',len(dr_after))
