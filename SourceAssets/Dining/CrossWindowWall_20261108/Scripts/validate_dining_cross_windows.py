import unreal,pathlib,json,re,math
cv_root=pathlib.Path('D:/Cyrus/OneDrive/文件/香港仔工業學校/ATS');cv_out=cv_root/'SourceAssets/Dining/CrossWindowWall_20261108'
cv_ed=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem);cv_sub=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
assert not cv_ed.get_game_world()
cv_prep=json.loads((cv_out/'preparation.json').read_text(encoding='utf-8'));cv_before=json.loads((pathlib.Path(cv_prep['backup'])/'scene_before.json').read_text(encoding='utf-8'))
cv_import=json.loads((cv_out/'import_result.json').read_text(encoding='utf-8'));cv_manifest=json.loads((cv_out/'construction_manifest.json').read_text(encoding='utf-8'))
cv_source=pathlib.Path('C:/Users/Cyrus/Documents/Codex/2026-11-06/dao/work/prepare_dining_cross_windows.py').read_text(encoding='utf-8')
exec(compile(cv_source[cv_source.index('def cw_snapshot'):cv_source.index('cw_before=')],'cross_snapshot_function','exec'))
cv_actors={a.get_name():a for a in cv_sub.get_all_level_actors()};cv_changed={x['actor'] for x in cv_import['changes']};cv_added={x['actor'] for x in cv_import['added']}
assert set(cv_actors)==set(cv_before)|cv_added
cv_diff=[]
for cv_n,cv_row in cv_before.items():
 cv_now=cw_snapshot(cv_actors[cv_n])
 if cv_n not in cv_changed:assert cv_row==cv_now,(cv_n,cv_row,cv_now)
 else:
  cv_d=[k for k in cv_row if cv_row[k]!=cv_now[k]];assert set(cv_d)<= {'mesh','materials'},(cv_n,cv_d);cv_diff.append({'actor':cv_n,'fields':cv_d})
cv_roles={x['role']:cv_actors[x['actor']] for x in cv_import['changes']+cv_import['added']}
cv_tiles=cv_roles['Tiles'].static_mesh_component
assert cv_tiles.get_collision_enabled()==unreal.CollisionEnabled.NO_COLLISION
for cv_i,cv_slot in enumerate(cv_tiles.static_mesh.get_editor_property('static_materials')):
 assert str(cv_slot.get_editor_property('imported_material_slot_name'))==cv_tiles.get_material(cv_i).get_name()
cv_c,cv_s=math.cos(math.radians(20)),math.sin(math.radians(20))
def cv_p(u,v,h):return unreal.Vector((-8+cv_c*u-cv_s*v)*100,(24-cv_s*u-cv_c*v)*100,(-24.55+h)*100)
cv_tests=[]
def cv_trace(name,start,end,blocked,ignore=None,actor=None):
 hit=unreal.SystemLibrary.line_trace_single(cv_ed.get_editor_world(),cv_p(*start),cv_p(*end),unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,True,ignore or [],unreal.DrawDebugTrace.NONE,True)
 row=hit.to_tuple() if hit else None;actual=bool(row and row[0]);a=row[9] if actual else None
 cv_tests.append({'name':name,'passed':actual==blocked and (actor is None or a==actor),'expected_blocking':blocked,'hit_actor':a.get_name() if a else None,'from':start,'to':end})
cv_ignore=[cv_roles[n] for n in ['Frames','Glass','Aircon','Cross']]
for cv_idx,cv_wc in enumerate(cv_manifest['window_centres_campus_m']):
 cv_v=cv_wc[1]
 for cv_d in [-.32,.32]:
  for cv_h in [1.3,2.2]:
   cv_trace('all wall layers open bay%d offset%.2f h%.1f'%(cv_idx,cv_d,cv_h),(.55,cv_v+cv_d,cv_h),(-.2,cv_v+cv_d,cv_h),False,cv_ignore)
   cv_trace('glass blocks inside bay%d offset%.2f h%.1f'%(cv_idx,cv_d,cv_h),(.55,cv_v+cv_d,cv_h),(-.2,cv_v+cv_d,cv_h),True,actor=cv_roles['Glass'])
   cv_trace('glass blocks outside bay%d offset%.2f h%.1f'%(cv_idx,cv_d,cv_h),(-.2,cv_v+cv_d,cv_h),(.55,cv_v+cv_d,cv_h),True,actor=cv_roles['Glass'])
 for cv_h in [.5,3.5,4.8,9.0]:cv_trace('wall above/below opening bay%d h%.1f'%(cv_idx,cv_h),(.55,cv_v,cv_h),(-.2,cv_v,cv_h),True,cv_ignore)
 for cv_d in [-.9,.9]:cv_trace('solid jamb bay%d offset%.1f'%(cv_idx,cv_d),(.55,cv_v+cv_d,2.2),(-.2,cv_v+cv_d,2.2),True,cv_ignore)
cv_v=cv_manifest['cross_campus_m'][1]
cv_trace('solid wall between bays',(.6,cv_v,2.0),(-.2,cv_v,2.0),True,cv_ignore)
cv_trace('cross at confirmed horizontal location',(.65,cv_v,2.62),(.26,cv_v,2.62),True,actor=cv_roles['Cross'])
if 'BoundaryCollision' in cv_roles:
 cv_boundary=cv_roles['BoundaryCollision'];cv_comp=cv_boundary.static_mesh_component
 assert not cv_comp.get_editor_property('visible') and not cv_comp.get_editor_property('cast_shadow') and cv_boundary.get_editor_property('hidden')
 for cv_v in [1,16.2,20.2,40]:cv_trace('nonvisual west boundary retained v'+str(cv_v),(-.4,cv_v,2),(-1.5,cv_v,2),True,actor=cv_boundary)
 cv_trace('other rear boundary retained',(73,43.8,7),(73,45,7),True,actor=cv_roles['BoundaryRetained'])
 cv_trace('other east boundary retained',(121.3,22,2),(122.7,22,2),True,actor=cv_roles['BoundaryRetained'])
# Recheck the existing door, floor, sink and seating collision assertions.
cv_oldtest=pathlib.Path('C:/Users/Cyrus/Documents/Codex/2026-11-06/dao/work/test_dining_photo_finishes.py').read_text(encoding='utf-8')
exec(compile(cv_oldtest[:cv_oldtest.index('# The rear outdoor recesses are isolated:')],'cross_window_existing_static_checks','exec'))
cv_report={'status':'passed' if all(x['passed'] for x in cv_tests+vtf_static) else 'failed','actor_count':len(cv_actors),'all_other_original_actors_unchanged':len(cv_before)-len(cv_changed),'modified_fields':cv_diff,'new_window_checks':cv_tests,'existing_static_checks':vtf_static,'user_sink_transform_preserved':cw_snapshot(cv_actors['StaticMeshActor_621'])['transform']==cv_before['StaticMeshActor_621']['transform'],'material_slot_names_match':True,'glass_collision_enabled':str(cv_roles['Glass'].static_mesh_component.get_collision_enabled()),'unverified_west_boundary_proxy_now_nonvisual':'BoundaryCollision' in cv_roles}
(cv_root/'dining_cross_windows_validation.json').write_text(json.dumps(cv_report,ensure_ascii=False,indent=2),encoding='utf-8')
(cv_out/'scene_after.json').write_text(json.dumps({n:cw_snapshot(a) for n,a in cv_actors.items()},ensure_ascii=False,indent=2),encoding='utf-8')
assert cv_report['status']=='passed',[x for x in cv_tests+vtf_static if not x['passed']]
print('CROSS_WINDOWS_VALIDATED',len(cv_tests),'NEW +',len(vtf_static),'EXISTING;',cv_report['all_other_original_actors_unchanged'],'UNCHANGED')
