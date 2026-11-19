import unreal,pathlib,json,hashlib,shutil,datetime
kf_root=pathlib.Path('D:/Cyrus/OneDrive/文件/香港仔工業學校/ATS');kf_out=kf_root/'SourceAssets/KnownDetails_20261108';kf_work=pathlib.Path('C:/Users/Cyrus/Documents/Codex/2026-11-06/dao/work')
kf_ed=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem);kf_level=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);kf_sub=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
assert not kf_ed.get_game_world()
kf_run=json.loads((kf_out/'door_runtime.json').read_text(encoding='utf-8'));assert kf_run['status']=='passed' and kf_run['editor_restored']
kf_expected=json.loads((kf_out/'scene_after.json').read_text(encoding='utf-8'))
assert kf_level.load_level('/Game/ATS/Maps/ATS_StudentCampus')
kf_now={a.get_name():kd_snapshot(a) for a in kf_sub.get_all_level_actors()}
kf_diff=[n for n in set(kf_expected)|set(kf_now) if kf_expected.get(n)!=kf_now.get(n)]
(kf_out/'reload_check.json').write_text(json.dumps({'count':len(kf_now),'differing_actors':kf_diff,'passed':not kf_diff},ensure_ascii=False,indent=2),encoding='utf-8')
assert not kf_diff,kf_diff
kf_pre=json.loads((kf_out/'preparation.json').read_text(encoding='utf-8'))
kf_ed.set_level_viewport_camera_info(unreal.Vector(*kf_pre['camera_world']),unreal.Rotator(**kf_pre['rotation']))
kf_lookup={a.get_name():a for a in kf_sub.get_all_level_actors()}
kf_sub.set_selected_level_actors([kf_lookup[n] for n in kf_pre['selected']])
kf_val=json.loads((kf_out/'validation.json').read_text(encoding='utf-8'))
kf_val['reload_passed']=True;kf_val['camera_restored']=True;kf_val['door_runtime']='passed';kf_val['status']='passed'
(kf_out/'validation.json').write_text(json.dumps(kf_val,ensure_ascii=False,indent=2),encoding='utf-8')
kf_evidence=kf_out/'Evidence';kf_evidence.mkdir(exist_ok=True)
for src,dest in [
 ('video_reference/01/04_1.67.jpg','video01_1.67_white_profile.jpg'),
 ('video_reference/04/17_4.31.jpg','video04_4.31_dark_square_base.jpg'),
 ('video_reference/detail_7_6.jpg','video07_6_corridor.jpg'),
 ('research/photos/HK-Aberdeen-Technical-School-03@1200x1200.JPG','hall_source_photo.JPG'),
 ('research/known_parts_20261108/dining_left_window_detail.png','dining_left_window_detail.png'),
 ('research/known_parts_20261108/dining_right_window_detail.png','dining_right_window_detail.png'),
 ('research/known_parts_20261108/teaching_candidates.json','teaching_candidates.json'),
 ('research/known_parts_20261108/hall_candidates.json','hall_candidates.json')]:
 p=kf_work/src;assert p.exists(),str(p);shutil.copy2(p,kf_evidence/dest)
kf_scripts=kf_out/'BuildAndVerification';kf_scripts.mkdir(exist_ok=True)
for name in ['prepare_known_details.py','import_known_details.py','verify_known_details.py','check_known_detail_door_runtime.py','set_known_detail_view.py','finalize_known_details.py']:
 shutil.copy2(kf_work/name,kf_scripts/name)
kf_import=json.loads((kf_out/'import_report.json').read_text(encoding='utf-8'))
for path in kf_import['materials']+[r['new_mesh'] for r in kf_import['replacements']]:
 rel=path.split('.')[0].replace('/Game/','Content/')+'.uasset';assert (kf_root/rel).is_file(),rel
kf_final={'status':'completed_and_saved','timestamp':datetime.datetime.now().isoformat(),'project':str(kf_root/'ATS.uproject'),'map':'/Game/ATS/Maps/ATS_StudentCampus','changes':{'classroom_frame_finish_split':24,'dark_square_mosaic_base_strips':6,'hall_original_glyph_order_corrected':1,'dining_ac_fronts_corrected':2},'new_actors':0,'changed_actors':32,'unchanged_actors':869,'checks':{'source_geometry_and_source_file_hashes':True,'all_actor_positions_lighting_and_collision_settings_preserved':True,'native_UE_before_after_visually_reviewed':['hall','corridor','skirting','ac'],'actual_player_door_entry_and_return':True,'saved_map_reloaded_all_901_actors_identical':True,'original_user_camera_restored':True},'backup':kf_pre['backup'],'evidence_directory':str(kf_evidence),'limitations':kf_import['limits'],'unconfirmed_architecture_added':False,'map_sha256':hashlib.sha256((kf_root/'Content/ATS/Maps/ATS_StudentCampus.umap').read_bytes()).hexdigest()}
(kf_out/'known_details_final.json').write_text(json.dumps(kf_final,ensure_ascii=False,indent=2),encoding='utf-8')
print('KNOWN_DETAILS_FINALIZED_RELOADED_VERIFIED_CAMERA_RESTORED')
