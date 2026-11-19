import unreal,pathlib,json,math,re
fi_root=pathlib.Path('D:/Cyrus/OneDrive/文件/香港仔工業學校/ATS');fi_out=fi_root/'SourceAssets/Dining/FullGroundFloor_20261108'
fi_manifest=json.loads((fi_out/'construction_manifest.json').read_text(encoding='utf-8'));fi_prep=json.loads((fi_out/'preparation.json').read_text(encoding='utf-8'))
fi_before=json.loads((pathlib.Path(fi_prep['backup'])/'scene_before.json').read_text(encoding='utf-8'))
fi_sub=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);fi_ed=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem);fi_level=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
assert not fi_ed.get_game_world() and fi_ed.get_editor_world().get_name()=='ATS_StudentCampus'
fi_path='/Game/ATS/Dining/FullGroundFloor_20261108';fi_lib=unreal.EditorAssetLibrary;fi_tools=unreal.AssetToolsHelpers.get_asset_tools()
assert not fi_lib.does_directory_exist(fi_path),'Inspect existing revision before retrying.'
fi_all=fi_sub.get_all_level_actors();fi_owned=[a for a in fi_all if 'ATS.Dining.BuiltFromUserPlan' in [str(t) for t in a.tags]];assert len(fi_owned)==28
fi_class=unreal.load_class(None,'/Script/ATS.ATSRollerShutter');assert fi_class
def fi_snapshot(a):
 d={'name':a.get_name(),'label':a.get_actor_label(),'class':a.get_class().get_name(),'transform':re.sub(r'0x[0-9A-Fa-f]+','ADDR',str(a.get_actor_transform())),'tags':[str(t) for t in a.tags],'folder':str(a.get_folder_path()),'editor_only':a.get_editor_property('is_editor_only_actor'),'hidden':a.get_editor_property('hidden'),'editor_hidden':a.is_temporarily_hidden_in_editor(),'collision':a.get_actor_enable_collision()}
 if isinstance(a,unreal.StaticMeshActor):
  m=a.static_mesh_component;d.update(mesh=m.static_mesh.get_path_name() if m.static_mesh else None,materials=[x.get_path_name() if x else None for x in m.get_materials()],component_collision=str(m.get_collision_enabled()),component_visible=m.get_editor_property('visible'))
 return d
def fi_import(file,folder):
 opts=unreal.FbxImportUI();opts.import_mesh=True;opts.import_as_skeletal=False;opts.import_materials=False;opts.import_textures=False;opts.import_animations=False;opts.automated_import_should_detect_type=False;opts.mesh_type_to_import=unreal.FBXImportType.FBXIT_STATIC_MESH
 data=opts.static_mesh_import_data;data.combine_meshes=False;data.auto_generate_collision=False;data.transform_vertex_to_absolute=True;data.convert_scene_unit=True;data.generate_lightmap_u_vs=False;data.normal_import_method=unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS
 task=unreal.AssetImportTask();task.filename=str(file);task.destination_path=folder;task.automated=True;task.replace_existing=False;task.save=False;task.options=opts;task.factory=unreal.FbxFactory();fi_tools.import_asset_tasks([task]);return [o for o in task.get_objects() if isinstance(o,unreal.StaticMesh)]
fi_meshes=fi_import(fi_out/'ATS_Dining_Built.fbx',fi_path+'/Meshes');assert len(fi_meshes)==13,len(fi_meshes)
fi_mats={}
for fi_name in fi_manifest['materials']:
 fi_key='M_DiningBuild_'+fi_name;fi_mats[fi_key]=unreal.load_asset('/Game/ATS/Dining/BuiltFromUserPlan/Materials/'+fi_key);assert fi_mats[fi_key]
fi_changed=[];fi_added=[];fi_removed=[]
for fi_mesh in fi_meshes:
 fi_key=re.search('SM_Dining(?:Built|Patch)_.*',fi_mesh.get_name()).group()
 fi_mesh.get_editor_property('body_setup').set_editor_property('collision_trace_flag',unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
 if fi_key=='SM_DiningPatch_OldWall':
  fi_a=next(a for a in fi_all if a.get_name()=='StaticMeshActor_49');fi_mesh.set_material(0,fi_a.static_mesh_component.get_material(0));fi_a.modify();fi_a.static_mesh_component.set_static_mesh(fi_mesh);fi_changed.append(fi_a.get_name());continue
 fi_item=next(x for x in fi_manifest['meshes'] if x['name']==fi_key)
 for fi_i,fi_slot in enumerate(fi_mesh.get_editor_property('static_materials')):fi_mesh.set_material(fi_i,fi_mats[str(fi_slot.get_editor_property('imported_material_slot_name'))])
 fi_a=next(a for a in fi_owned if a.get_actor_label()=='餐廳實體｜'+fi_item['group']);fi_a.modify();fi_c=fi_a.static_mesh_component;fi_c.set_static_mesh(fi_mesh)
 fi_c.set_collision_profile_name('BlockAll' if fi_item['collision'] else 'NoCollision');fi_c.set_collision_enabled(unreal.CollisionEnabled.QUERY_AND_PHYSICS if fi_item['collision'] else unreal.CollisionEnabled.NO_COLLISION)
 fi_a.set_actor_hidden_in_game(False);fi_a.set_is_temporarily_hidden_in_editor(False);fi_changed.append(fi_a.get_name())
fi_slat=fi_import(fi_out/'SM_Dining_ShutterSlat.fbx',fi_path+'/Shutters')[0]
fi_slat.set_material(0,fi_mats['M_DiningBuild_Frame'])
fi_extent=fi_slat.get_bounds().box_extent;assert abs(fi_extent.x-50)<.1 and abs(fi_extent.z-3.75)<.1,str(fi_extent)
fi_c,fi_s=math.cos(math.radians(20)),math.sin(math.radians(20))
def fi_point(p):u,v,h=p;return unreal.Vector((-8+fi_c*u-fi_s*v)*100,(24-fi_s*u-fi_c*v)*100,(-24.55+h)*100)
fi_shutters=[]
for fi_d in fi_manifest['doors']:
 fi_old=next(a for a in fi_owned if 'ATS.DiningDoor.'+fi_d['id'] in [str(t) for t in a.tags]);fi_removed.append(fi_old.get_name());assert fi_sub.destroy_actor(fi_old)
 fi_a=fi_sub.spawn_actor_from_class(fi_class,fi_point(fi_d['hinge']),unreal.Rotator(pitch=0,yaw=fi_d['yaw'],roll=0));fi_a.set_actor_label('餐廳捲閘｜'+fi_d['id']);fi_a.set_folder_path('Campus/Dining')
 fi_a.tags=[unreal.Name('ATS.Dining.BuiltFromUserPlan'),unreal.Name('ATS.Dining.FullGroundFloor'),unreal.Name('ATS.Floor.G'),unreal.Name('ATS.DiningDoor.'+fi_d['id'])]
 fi_a.get_editor_property('slats').set_static_mesh(fi_slat)
 for fi_prop,fi_value in [('width',fi_d['width']*100),('height',fi_d['height']*100),('slat_pitch',7.5),('lift_speed',180),('approach_distance',230),('hold_open_seconds',2)]:fi_a.set_editor_property(fi_prop,fi_value)
 fi_a.rebuild_shutter();fi_added.append(fi_a.get_name());fi_shutters.append({'id':fi_d['id'],'actor':fi_a.get_name()})
fi_old_lights=sorted([a for a in fi_owned if isinstance(a,unreal.RectLight)],key=lambda a:a.get_actor_label());assert len(fi_old_lights)==13
for fi_i,fi_l in enumerate(fi_manifest['lights']):
 if fi_i<len(fi_old_lights):fi_a=fi_old_lights[fi_i];fi_a.modify();fi_changed.append(fi_a.get_name())
 else:
  fi_a=fi_sub.spawn_actor_from_class(unreal.RectLight,fi_point(fi_l['campus_m']));fi_a.tags=[unreal.Name('ATS.Dining.BuiltFromUserPlan'),unreal.Name('ATS.Floor.G')];fi_a.set_folder_path('Campus/Dining');fi_added.append(fi_a.get_name())
 fi_a.set_actor_label('餐廳照明 %02d'%(fi_i+1));fi_a.set_actor_location_and_rotation(fi_point(fi_l['campus_m']),unreal.Rotator(pitch=-90,yaw=-20,roll=0),False,True);fi_light=fi_a.get_component_by_class(unreal.RectLightComponent)
 for fi_prop,fi_val in [('intensity_units',unreal.LightUnits.LUMENS),('intensity',fi_l['lumens']),('source_width',fi_l['width_cm']),('source_height',fi_l['height_cm']),('attenuation_radius',900),('use_temperature',True),('temperature',5300),('cast_shadows',True)]:fi_light.set_editor_property(fi_prop,fi_val)
 fi_light.set_mobility(unreal.ComponentMobility.MOVABLE)
fi_ed.set_level_viewport_camera_info(unreal.Vector(*fi_prep['camera_world']),unreal.Rotator(**fi_prep['rotation']))
assert fi_lib.save_directory(fi_path,only_if_is_dirty=True,recursive=True);assert fi_level.save_current_level()
fi_after={a.get_name():a for a in fi_sub.get_all_level_actors()};assert len(fi_after)==len(fi_before)+len(fi_added)-len(fi_removed)
for fi_name,fi_row in fi_before.items():
 if fi_name not in fi_changed+fi_removed:assert fi_snapshot(fi_after[fi_name])==fi_row,fi_name
fi_report={'status':'full_ground_floor_imported','backup':fi_prep['backup'],'actors_before':len(fi_before),'actors_after':len(fi_after),'changed_actors':fi_changed,'added_actors':fi_added,'removed_swing_doors':fi_removed,'shutters':fi_shutters,'unaffected_actors_verified':len(fi_before)-len(set(fi_changed+fi_removed)),'bounds':fi_manifest['room_campus_bounds'],'kiosk':fi_manifest['full_G_floor']['kiosk_bounds'],'kiosk_front_normal':[0,1,0],'user_camera_restored':True,'validation_pending':True}
(fi_root/'dining_full_floor_scene.json').write_text(json.dumps(fi_report,ensure_ascii=False,indent=2),encoding='utf-8')
print('FULL_G_FLOOR_IMPORTED',len(fi_after))
