import unreal,pathlib,json,datetime
fl_root=pathlib.Path('D:/Cyrus/OneDrive/文件/香港仔工業學校/ATS');fl_out=fl_root/'SourceAssets/Dining/CrossWindowWall_20261108'
fl_ed=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem);fl_sub=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);fl_level=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
assert not fl_ed.get_game_world()
fl_static=json.loads((fl_root/'dining_cross_windows_validation.json').read_text(encoding='utf-8'));fl_runtime=json.loads((fl_root/'dining_cross_windows_runtime.json').read_text(encoding='utf-8'))
assert fl_static['status']==fl_runtime['status']=='passed'
fl_expected=json.loads((fl_out/'scene_after.json').read_text(encoding='utf-8'))
assert len(fl_expected)==901
assert unreal.EditorAssetLibrary.save_directory('/Game/ATS/Dining/CrossWindowWall_20261108',only_if_is_dirty=True,recursive=True)
assert fl_level.save_current_level()
assert fl_level.load_level('/Game/ATS/Maps/ATS_StudentCampus')
fl_actual={a.get_name():a for a in fl_sub.get_all_level_actors()}
assert set(fl_actual)==set(fl_expected)
for fl_n,fl_a in fl_actual.items():assert cw_snapshot(fl_a)==fl_expected[fl_n],fl_n
fl_prep=json.loads((fl_out/'preparation.json').read_text(encoding='utf-8'))
fl_ed.set_level_viewport_camera_info(unreal.Vector(*fl_prep['camera_world']),unreal.Rotator(**fl_prep['rotation']))
fl_sub.set_selected_level_actors([fl_actual[n] for n in fl_prep['selected'] if n in fl_actual])
fl_shutters=[a for a in fl_actual.values() if a.get_class().get_name()=='ATSRollerShutter'];assert len(fl_shutters)==3
for fl_a in fl_shutters:assert fl_a.get_editor_property('slats').get_instance_count()==38 and abs(fl_a.get_editor_property('current_lift'))<.001
fl_report={'status':'saved_static_runtime_and_reload_verified','timestamp':datetime.datetime.now().isoformat(),'actor_count':len(fl_actual),'reload_matched_actor_snapshots':len(fl_actual),'all_other_original_actors_unchanged':fl_static['all_other_original_actors_unchanged'],'new_static_checks':len(fl_static['new_window_checks']),'existing_static_checks':len(fl_static['existing_static_checks']),'runtime_walk_waypoints':len(fl_runtime['route']),'runtime_jump_into_window_blocked':fl_runtime['window_blocked_jump'],'original_three_roller_shutters_restored_closed':True,'user_camera_restored':True,'sink_transform_preserved':True,'backup':fl_prep['backup'],'user_confirmation':'正中央就是十字架位置','cross_horizontal_campus_v':17.59944733735314,'cross_height_model_estimate_m':2.62,'vertical_interpretation_disclosed_to_user':True,'photo_visible_windows_added':2,'whole_wall_window_count_not_established':True,'cross_dimensions_window_dimensions_and_spacing_are_unmeasured_estimates':True,'unverified_west_boundary_visible_proxy_removed':True,'west_boundary_collision_remains_nonvisual':True,'other_two_boundary_sections_retained':True,'full_reconstruction_complete':False,'remaining_unconfirmed':['Ceiling beam and interior column positions/spans','Floor black-band widths and registered layout','Reflective wall-zone coordinates','Full seating count and layout','Exact outside view through this wall; existing exterior scene retained'],'previews':['Previews/C26_Dining_CrossWall_UserView.png','Previews/C27_Dining_CrossWall_Detail.png'],'sources':['https://www.hk01.com/article/939149','https://media.goodschool.hk/storage/upload/ebook/2021-11-02-175925-108203.pdf']}
(fl_root/'dining_cross_windows_final.json').write_text(json.dumps(fl_report,ensure_ascii=False,indent=2),encoding='utf-8')
(fl_root/'Saved/Validation/dining_cross_windows_persistence.json').write_text(json.dumps({'status':'passed','matched_actor_snapshots':len(fl_actual),'original_user_camera_restored':True,'roller_shutters_closed':3},ensure_ascii=False,indent=2),encoding='utf-8')
print('CROSS_WINDOWS_FINAL',fl_report)
