import unreal,pathlib,json,re,shutil,datetime
ff_root=pathlib.Path('D:/Cyrus/OneDrive/文件/香港仔工業學校/ATS');ff_out=ff_root/'SourceAssets/Dining/PhotoFinishes_20261108';ff_work=pathlib.Path('C:/Users/Cyrus/Documents/Codex/2026-11-06/dao/work')
ff_ed=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem);ff_sub=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);ff_level=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
assert not ff_ed.get_game_world() and ff_ed.get_editor_world().get_name()=='ATS_StudentCampus'
ff_validation=json.loads((ff_root/'dining_photo_finishes_validation.json').read_text(encoding='utf-8'));assert ff_validation['status']=='passed',ff_validation['status']
ff_prep=json.loads((ff_out/'preparation.json').read_text(encoding='utf-8'));ff_before=json.loads((pathlib.Path(ff_prep['backup'])/'scene_before.json').read_text(encoding='utf-8'))
ff_furniture=json.loads((ff_out/'furniture_placement.json').read_text(encoding='utf-8'));ff_sink=json.loads((ff_out/'sink_import.json').read_text(encoding='utf-8'));ff_mat=json.loads((ff_out/'material_application.json').read_text(encoding='utf-8'))
ff_changed={ff_sink['actor']}|{x['actor'] for x in ff_mat['changes']};ff_added={x['actor'] for x in ff_furniture['placements']}
def ff_snapshot(a):
 d={'name':a.get_name(),'label':a.get_actor_label(),'class':a.get_class().get_name(),'transform':re.sub(r'0x[0-9A-Fa-f]+','ADDR',str(a.get_actor_transform())),'tags':[str(t) for t in a.tags],'folder':str(a.get_folder_path()),'editor_only':a.get_editor_property('is_editor_only_actor'),'hidden':a.get_editor_property('hidden'),'editor_hidden':a.is_temporarily_hidden_in_editor(),'collision':a.get_actor_enable_collision()}
 if isinstance(a,unreal.StaticMeshActor):
  m=a.static_mesh_component;d.update(mesh=m.static_mesh.get_path_name() if m.static_mesh else None,materials=[x.get_path_name() if x else None for x in m.get_materials()],component_collision=str(m.get_collision_enabled()),component_visible=m.get_editor_property('visible'))
 return d
ff_after={a.get_name():a for a in ff_sub.get_all_level_actors()};assert set(ff_after)==set(ff_before)|ff_added
ff_unchanged=[]
for ff_name,ff_row in ff_before.items():
 if ff_name not in ff_changed:assert ff_snapshot(ff_after[ff_name])==ff_row,ff_name;ff_unchanged.append(ff_name)
for ff_a in ff_after.values():
 if ff_a.get_class().get_name()=='ATSRollerShutter':ff_a.rebuild_shutter()
ff_ed.set_level_viewport_camera_info(unreal.Vector(*ff_prep['camera_world']),unreal.Rotator(**ff_prep['rotation']))
ff_sub.set_selected_level_actors([ff_after[n] for n in ff_prep['selected'] if n in ff_after])
assert unreal.EditorAssetLibrary.save_directory('/Game/ATS/Dining/PhotoFinishes_20261108',only_if_is_dirty=True,recursive=True)
assert ff_level.save_current_level()
ff_report={'status':'saved_and_walk_verified','created':datetime.datetime.now().isoformat(),'actors_before':len(ff_before),'actors_after':len(ff_after),'changed_existing':sorted(ff_changed),'added':sorted(ff_added),'unaffected_existing_verified':len(ff_unchanged),'backup':ff_prep['backup'],'sink_length_model_m':4.5,'sink_previous_model_m':2.82,'tables_added':2,'chairs_added':8,'table_zone_basis':'User confirmed both central and window-side seating. White rectangular tables, blue plastic chairs, dark frames and opposing long-side seating come from actual school photos.','partial_furniture_only':True,'exact_layout_and_dimensions_verified':False,'floor':'Photo-informed dry warm beige fine-aggregate terrazzo; native world-space shader, approximate grain size, no invented full-room dark band grid.','upper_walls_and_ceiling':'Low-gloss off-white paint on existing geometry.','lower_wall_limit':'Sources show both pale rectangular basket mosaic and pink square-grid areas. Location correspondence remains unresolved; existing lower-wall finish has not been certified or extended.','ceiling_limit':'Photos show exposed white structural beams, but an exact beam/column grid is not known and has not been added.','validation':{'static_passed':sum(x['passed'] for x in ff_validation['static_checks']),'static_total':len(ff_validation['static_checks']),'walk_waypoints':len(ff_validation['walk_checks']),'shutter_hold_checks':len(ff_validation['hold_open_checks']),'report':'dining_photo_finishes_validation.json'},'user_camera_and_selection_restored':True,'reload_verification_pending':True}
(ff_root/'dining_photo_finishes_final.json').write_text(json.dumps(ff_report,ensure_ascii=False,indent=2),encoding='utf-8')
(ff_out/'scene_after.json').write_text(json.dumps({n:ff_snapshot(a) for n,a in ff_after.items()},ensure_ascii=False,indent=2),encoding='utf-8')
print('PHOTO_FINISHES_FINAL_SAVED',ff_report)
