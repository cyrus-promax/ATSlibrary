import unreal,pathlib,json,re
sv_root=pathlib.Path('D:/Cyrus/OneDrive/文件/香港仔工業學校/ATS');sv_out=sv_root/'SourceAssets/Dining/StructuralSurfaces_20261108'
sv_ed=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem);sv_sub=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
assert not sv_ed.get_game_world()
sv_prep=json.loads((sv_out/'preparation.json').read_text(encoding='utf-8'));sv_before=json.loads((pathlib.Path(sv_prep['backup'])/'scene_before.json').read_text(encoding='utf-8'))
sv_import=json.loads((sv_out/'surface_import.json').read_text(encoding='utf-8'));sv_changed={x['actor'] for x in sv_import['changes']}
sv_after={a.get_name():a for a in sv_sub.get_all_level_actors()};assert set(sv_after)==set(sv_before)
for sv_n,sv_row in sv_before.items():
 if sv_n not in sv_changed:assert ss_snapshot(sv_after[sv_n])==sv_row,sv_n
sv_tiles=next(a for a in sv_after.values() if a.get_actor_label()=='餐廳實體｜Tiles')
assert sv_tiles.static_mesh_component.get_collision_enabled()==unreal.CollisionEnabled.NO_COLLISION
assert len(sv_tiles.static_mesh_component.get_materials())==3
assert all('/StructuralSurfaces_20261108/' in m.get_path_name() for m in sv_tiles.static_mesh_component.get_materials())
# Reuse the previous meaningful door, floor, sink and furniture static traces,
# without starting another full walk after a nonblocking surface-only change.
sv_source=pathlib.Path('C:/Users/Cyrus/Documents/Codex/2026-11-06/dao/work/test_dining_photo_finishes.py').read_text(encoding='utf-8')
sv_prefix=sv_source[:sv_source.index('# The rear outdoor recesses are isolated:')]
exec(compile(sv_prefix,'dining_surface_static_checks','exec'))
assert len(vtf_static)==63 and all(x['passed'] for x in vtf_static),[x for x in vtf_static if not x['passed']]
sv_report={'status':'passed','actor_count':len(sv_after),'modified_actors':sorted(sv_changed),'all_other_actors_unchanged':len(sv_before)-len(sv_changed),'static_checks':vtf_static,'surface_collision_disabled':True,'previous_49_point_walk_retained':'Geometry with collision, pawn and doors are unchanged; 63 static traces rerun after render-only panel replacement.','user_room_identity':'User confirms this is the main hall in the HK01 photograph.','unconfirmed':['Exact module and grout dimensions','Which current wall is the cross wall, pending user reply','Exact floor band positions and beam/column coordinates']}
(sv_root/'dining_structural_surfaces_validation.json').write_text(json.dumps(sv_report,ensure_ascii=False,indent=2),encoding='utf-8')
print('DINING_SURFACE_CHECKS_PASSED',len(vtf_static),'UNCHANGED_ACTORS',sv_report['all_other_actors_unchanged'])
