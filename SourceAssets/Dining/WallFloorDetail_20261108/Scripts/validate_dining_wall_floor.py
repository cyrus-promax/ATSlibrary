import unreal,pathlib,json,re
vv_root=pathlib.Path('D:/Cyrus/OneDrive/文件/香港仔工業學校/ATS');vv_out=vv_root/'SourceAssets/Dining/WallFloorDetail_20261108'
vv_ed=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem);vv_sub=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
assert not vv_ed.get_game_world()
vv_app=json.loads((vv_out/'application.json').read_text(encoding='utf-8'));vv_prep=json.loads((vv_out/'preparation.json').read_text(encoding='utf-8'));vv_before=json.loads((pathlib.Path(vv_prep['backup'])/'scene_before.json').read_text(encoding='utf-8'))
vv_current={a.get_name():a for a in vv_sub.get_all_level_actors()};assert set(vv_current)==set(vv_before)
vv_mat_actors={x['actor'] for x in vv_app['materials']};vv_lights={x['actor'] for x in vv_app['lighting']};vv_changed=vv_mat_actors|vv_lights
vv_diffs=[]
for vv_n,vv_a in vv_current.items():
 vv_now=wf_snapshot(vv_a);vv_diff=[k for k in vv_before[vv_n] if vv_now[k]!=vv_before[vv_n][k]]
 if vv_n not in vv_changed:assert not vv_diff,(vv_n,vv_diff)
 elif vv_n in vv_lights:
  assert vv_diff==['light'],(vv_n,vv_diff)
  assert [k for k in vv_now['light'] if vv_now['light'][k]!=vv_before[vv_n]['light'][k]]==['temperature']
 else:assert set(vv_diff)<= {'mesh','materials'},(vv_n,vv_diff)
 if vv_diff:vv_diffs.append({'actor':vv_n,'fields':vv_diff})
vv_tiles=vv_current[vv_app['mesh_change']['actor']];assert vv_tiles.static_mesh_component.get_collision_enabled()==unreal.CollisionEnabled.NO_COLLISION
# Use the already meaningful cross-window and door route trace checks without
# their previous-revision snapshot/material-name assertions or file writes.
vv_code=pathlib.Path('C:/Users/Cyrus/Documents/Codex/2026-11-06/dao/work/validate_dining_cross_windows.py').read_text(encoding='utf-8')
cv_import=json.loads((vv_root/'SourceAssets/Dining/CrossWindowWall_20261108/import_result.json').read_text(encoding='utf-8'))
cv_manifest=json.loads((vv_root/'SourceAssets/Dining/CrossWindowWall_20261108/construction_manifest.json').read_text(encoding='utf-8'))
cv_ed=vv_ed;cv_roles={x['role']:vv_current[x['actor']] for x in cv_import['changes']+cv_import['added']}
import math
exec(compile(vv_code[vv_code.index('cv_c,cv_s='):vv_code.index('cv_report=')],'wall_floor_route_checks','exec'))
vv_all=cv_tests+vtf_static
vv_result={'status':'passed' if all(x['passed'] for x in vv_all) else 'failed','actor_count':len(vv_current),'all_other_actors_unchanged':len(vv_current)-len(vv_changed),'modified_fields':vv_diffs,'checks':vv_all,'checks_passed':sum(x['passed'] for x in vv_all),'render_only_wall_mesh_collision_disabled':True,'all_collision_geometry_and_profiles_unchanged':True,'lighting_change_only_temperature':True,'all_actor_transforms_unchanged':True,'no_new_partitions_or_floor_band_layout':True,'runtime_not_repeated_reason':'Only surface materials, non-colliding lower wall-panel edge and light colour temperature changed; all collision-bearing geometry, movement and shutter logic unchanged.'}
(vv_root/'dining_wall_floor_validation.json').write_text(json.dumps(vv_result,ensure_ascii=False,indent=2),encoding='utf-8')
(vv_out/'scene_after.json').write_text(json.dumps({n:wf_snapshot(a) for n,a in vv_current.items()},ensure_ascii=False,indent=2),encoding='utf-8')
assert vv_result['status']=='passed',[x for x in vv_all if not x['passed']]
print('WALL_FLOOR_VALIDATED',vv_result['checks_passed'],vv_result['all_other_actors_unchanged'])
