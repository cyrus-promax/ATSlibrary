import unreal,pathlib,json
rp_root=pathlib.Path('D:/Cyrus/OneDrive/文件/香港仔工業學校/ATS');rp_out=rp_root/'SourceAssets/Dining/PhotoFinishes_20261108'
rp_ed=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem);rp_level=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);rp_sub=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
assert not rp_ed.get_game_world()
rp_report=json.loads((rp_root/'dining_photo_finishes_final.json').read_text(encoding='utf-8'));assert rp_report['status']=='saved_and_walk_verified'
rp_expected=json.loads((rp_out/'scene_after.json').read_text(encoding='utf-8'))
assert rp_level.load_level('/Game/ATS/Maps/ATS_StudentCampus')
rp_actors={a.get_name():a for a in rp_sub.get_all_level_actors()};assert len(rp_actors)==896
for rp_n,rp_a in rp_actors.items():assert ff_snapshot(rp_a)==rp_expected[rp_n],rp_n
rp_shutters=[a for a in rp_actors.values() if a.get_class().get_name()=='ATSRollerShutter'];assert len(rp_shutters)==3
for rp_a in rp_shutters:
 assert rp_a.get_editor_property('slats').get_instance_count()==38
 assert rp_a.get_editor_property('current_lift')==0
rp_prep=json.loads((rp_out/'preparation.json').read_text(encoding='utf-8'))
rp_ed.set_level_viewport_camera_info(unreal.Vector(*rp_prep['camera_world']),unreal.Rotator(**rp_prep['rotation']))
rp_sub.set_selected_level_actors([rp_actors[n] for n in rp_prep['selected'] if n in rp_actors])
rp_report.update(status='saved_walk_and_reload_verified',reload_verification_pending=False,reloaded_actor_snapshots_matched=len(rp_actors),preserved_user_sink_transform=rp_expected['StaticMeshActor_621']['transform'])
(rp_root/'dining_photo_finishes_final.json').write_text(json.dumps(rp_report,ensure_ascii=False,indent=2),encoding='utf-8')
(rp_root/'Saved/Validation/dining_photo_finishes_persistence.json').write_text(json.dumps({'status':'passed','matched_actors':896,'roller_shutters_persisted_closed':3,'user_camera_restored':True,'user_sink_translation_preserved':True},ensure_ascii=False,indent=2),encoding='utf-8')
print('PHOTO_FINISHES_RELOAD_VERIFIED',len(rp_actors))
