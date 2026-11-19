import unreal,pathlib,json,re,datetime
st_root=pathlib.Path('D:/Cyrus/OneDrive/文件/香港仔工業學校/ATS');st_out=st_root/'SourceAssets/Dining/StructuralSurfaces_20261108'
st_ed=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem);st_sub=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);st_level=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
assert not st_ed.get_game_world() and st_ed.get_editor_world().get_name()=='ATS_StudentCampus'
st_validation=json.loads((st_root/'dining_structural_surfaces_validation.json').read_text(encoding='utf-8'));assert st_validation['status']=='passed'
st_prep=json.loads((st_out/'preparation.json').read_text(encoding='utf-8'))
st_cam=json.loads((st_out/'user_cross_wall_camera.json').read_text(encoding='utf-8'))
# User may currently be aiming the viewport to provide an exact cross anchor.
# Save without moving/reloading the live view while that question is pending.
assert unreal.EditorAssetLibrary.save_directory('/Game/ATS/Dining/StructuralSurfaces_20261108',only_if_is_dirty=True,recursive=True)
assert st_level.save_current_level()
st_actual={a.get_name():ss_snapshot(a) for a in st_sub.get_all_level_actors()}
st_report={'status':'surfaces_saved_geometry_registration_incomplete','timestamp':datetime.datetime.now().isoformat(),'actor_count':len(st_actual),'modified_actors':st_validation['modified_actors'],'all_other_actors_unchanged':st_validation['all_other_actors_unchanged'],'static_checks_passed':len(st_validation['static_checks']),'reload_not_repeated':'Preserve the active user viewport while awaiting their cross-position anchor. Current map and new assets saved successfully; render and collision checks passed.','backup':st_prep['backup'],'changes':['Main-hall pale interwoven rectangular mosaic appearance replaces generic square tiles','Charcoal tile cap and speckled dark skirting','Dry terrazzo grain contrast and distant mean colour improved; thresholds match floor'],'room_identity_user_confirmed':True,'cross_wall_direction_user_confirmed':'u=.23 (currently blank wall directly ahead in captured user view)','cross_exact_position_confirmed':False,'full_reconstruction_complete':False,'not_added_without_coordinates':['Full floor black-band layout','Interior beam/column grid','Unregistered reflective-wall zones','Unknown whole-wall window count and spacing'],'ceiling_status':'Existing off-white painted ceiling retained. Exposed beams are photo-confirmed but their positions and spans are not yet established.','latest_user_camera_untouched':True,'sources':'SourceAssets/Dining/StructuralSurfaces_20261108/References','previews':['Previews/C24_Dining_Mosaic_Wall_Detail.png','Previews/C25_Dining_Mosaic_and_Terrazzo.png']}
(st_root/'dining_structural_surfaces_final.json').write_text(json.dumps(st_report,ensure_ascii=False,indent=2),encoding='utf-8')
(st_out/'scene_after.json').write_text(json.dumps(st_actual,ensure_ascii=False,indent=2),encoding='utf-8')
print('DINING_STRUCTURAL_SURFACES_FINAL',st_report)
