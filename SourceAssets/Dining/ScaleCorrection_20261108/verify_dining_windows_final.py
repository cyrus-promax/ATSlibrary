import unreal,pathlib,json,math
wv_root=pathlib.Path('D:/Cyrus/OneDrive/文件/香港仔工業學校/ATS');wv_sub=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);wv_ed=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
wv_c,wv_s=math.cos(math.radians(20)),math.sin(math.radians(20))
def wv_point(u,v,h):return unreal.Vector((-8+wv_c*u-wv_s*v)*100,(24-wv_s*u-wv_c*v)*100,(-24.55+h)*100)
wv_a=next(a for a in wv_sub.get_all_level_actors() if a.get_name()=='StaticMeshActor_47')
wv_checks=[]
for wv_u in [5.5,8.7,11.9,15.1,18.3]:
 wv_hit=unreal.SystemLibrary.line_trace_single(wv_ed.get_editor_world(),wv_point(wv_u,4.25,1.75),wv_point(wv_u,2.85,1.75),unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,True,[],unreal.DrawDebugTrace.NONE,True)
 wv_tuple=wv_hit.to_tuple() if wv_hit else None;wv_ok=bool(wv_tuple and wv_tuple[0] and wv_tuple[9]==wv_a)
 wv_checks.append({'window_center_u':wv_u,'blocking_glass_preserved':wv_ok})
assert all(r['blocking_glass_preserved'] for r in wv_checks),str(wv_checks)
wv_scene=json.loads((wv_root/'dining_scale_scene.json').read_text(encoding='utf-8'))
wv_before=json.loads((pathlib.Path(wv_scene['backup'])/'scene_before.json').read_text(encoding='utf-8'))
wv_after={a.get_name():a for a in wv_sub.get_all_level_actors()}
wv_excluded=wv_scene['changed_actors']+wv_scene['removed_false_window_actors']
for wv_name,wv_row in wv_before.items():
 if wv_name not in wv_excluded:assert ds_snapshot(wv_after[wv_name])==wv_row,wv_name
wv_report=json.loads((wv_root/'dining_scale_window_correction.json').read_text(encoding='utf-8'));wv_report['post_import_window_collision_checks']=wv_checks;wv_report['unaffected_scene_actors_rechecked']=len(wv_before)-len(set(wv_excluded))
(wv_root/'dining_scale_window_correction.json').write_text(json.dumps(wv_report,ensure_ascii=False,indent=2),encoding='utf-8')
