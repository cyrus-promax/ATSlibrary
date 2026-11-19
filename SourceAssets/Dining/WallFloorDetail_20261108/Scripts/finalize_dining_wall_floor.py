import unreal,pathlib,json,datetime,re
fd_root=pathlib.Path('D:/Cyrus/OneDrive/文件/香港仔工業學校/ATS');fd_out=fd_root/'SourceAssets/Dining/WallFloorDetail_20261108'
fd_ed=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem);fd_sub=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);fd_level=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
assert not fd_ed.get_game_world()
fd_validation=json.loads((fd_root/'dining_wall_floor_validation.json').read_text(encoding='utf-8'));assert fd_validation['status']=='passed'
fd_expected=json.loads((fd_out/'scene_after.json').read_text(encoding='utf-8'))
assert unreal.EditorAssetLibrary.save_directory('/Game/ATS/Dining/WallFloorDetail_20261108',only_if_is_dirty=True,recursive=True);assert fd_level.save_current_level()
assert fd_level.load_level('/Game/ATS/Maps/ATS_StudentCampus')
fd_actors={a.get_name():a for a in fd_sub.get_all_level_actors()};assert set(fd_actors)==set(fd_expected)
for fd_n,fd_a in fd_actors.items():
 # UE repr embeds the transient address of Color structs; compare all values
 # while excluding that address, just as Transform snapshots already do.
 assert re.sub(r'0x[0-9A-Fa-f]+','ADDR',json.dumps(wf_snapshot(fd_a),sort_keys=True))==re.sub(r'0x[0-9A-Fa-f]+','ADDR',json.dumps(fd_expected[fd_n],sort_keys=True)),fd_n
fd_prep=json.loads((fd_out/'preparation.json').read_text(encoding='utf-8'))
fd_ed.set_level_viewport_camera_info(unreal.Vector(*fd_prep['camera_world']),unreal.Rotator(**fd_prep['rotation']));fd_sub.set_selected_level_actors([fd_actors[n] for n in fd_prep['selected'] if n in fd_actors])
fd_report={'status':'saved_visual_static_and_reload_verified','timestamp':datetime.datetime.now().isoformat(),'actor_count':len(fd_actors),'reloaded_actor_snapshots_matched':len(fd_actors),'all_other_actors_unchanged':fd_validation['all_other_actors_unchanged'],'static_checks_passed':fd_validation['checks_passed'],'changes':['More legible pale basket-mosaic with multi-scale colour filtering and fine recessed joint highlight response; original model tile-module size retained','Dry light terrazzo with more distinct dark/grey/ivory aggregate, reduced yellow cast, smooth surface without displacement','More legible aggregate in the dark terrazzo skirting','Close the old 20mm bare-paint gap between mosaic lower edge and black skirting','Dining lights adjusted from 5300K to 6000K for rendering appearance; intensity, placement and lamp models unchanged'],'lighting_temperature_is_rendering_choice_not_verified_lamp_spec':True,'backup':fd_prep['backup'],'user_camera_restored':True,'actor_transforms_collision_and_door_logic_unchanged':True,'runtime_not_repeated':fd_validation['runtime_not_repeated_reason'],'new_partition_or_floor_band_geometry_added':False,'full_reconstruction_complete':False,'not_yet_located':['Complete dark floor-band graph and widths','Floor slab-joint layout','Reflective wall panel bounds','Interior structural beam and column grid'],'surface_colours_grain_sizes_roughness_are_visual_estimates':True,'previews':['Previews/C28_Dining_Refined_Wall_Floor.png','Previews/C29_Dining_Mosaic_Terrazzo_Close.png'],'visual_limits':'Static rendered views checked; temporal shimmer during camera motion was not independently measured.'}
(fd_root/'dining_wall_floor_final.json').write_text(json.dumps(fd_report,ensure_ascii=False,indent=2),encoding='utf-8')
(fd_root/'Saved/Validation/dining_wall_floor_persistence.json').write_text(json.dumps({'status':'passed','matched_actor_snapshots':len(fd_actors),'restored_latest_user_camera':True},ensure_ascii=False,indent=2),encoding='utf-8')
print('WALL_FLOOR_FINAL',fd_report['status'],len(fd_actors))
