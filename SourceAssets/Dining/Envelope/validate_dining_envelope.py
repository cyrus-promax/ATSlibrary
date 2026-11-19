import unreal,json,pathlib,math,re,hashlib
ev_root=pathlib.Path('D:/Cyrus/OneDrive/文件/香港仔工業學校/ATS')
ev_sub=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
ev_ed=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
assert not ev_ed.get_game_world()
ev_world=ev_ed.get_editor_world()
ev_build=json.loads((ev_root/'dining_envelope_build_report.json').read_text(encoding='utf-8'))
ev_before=json.loads((pathlib.Path(ev_build['backup'])/'scene_before.json').read_text(encoding='utf-8'))
ev_actors={a.get_name():a for a in ev_sub.get_all_level_actors()}
def ev_snapshot(a):
    row={'name':a.get_name(),'label':a.get_actor_label(),'class':a.get_class().get_name(),'transform':re.sub(r'0x[0-9A-Fa-f]+','ADDR',str(a.get_actor_transform()))}
    if isinstance(a,unreal.StaticMeshActor):
        c=a.static_mesh_component
        row.update(mesh=c.static_mesh.get_path_name() if c.static_mesh else None,materials=[m.get_path_name() if m else None for m in c.get_materials()],collision=str(c.get_collision_enabled()))
    return row
for ev_n,ev_row in ev_before.items():assert ev_snapshot(ev_actors[ev_n])==ev_row,ev_n
assert len(ev_actors)==850
ev_c,ev_s=math.cos(math.radians(20)),math.sin(math.radians(20))
def ev_p(u,v,h):return unreal.Vector((-8+ev_c*u-ev_s*v)*100,(24-ev_s*u-ev_c*v)*100,(-24.55+h)*100)
def ev_local(p):
    x=p.x/100+8;y=-p.y/100+24
    return [ev_c*x+ev_s*y,-ev_s*x+ev_c*y,p.z/100+24.55]
ev_checks=[]
def ev_trace(label,start,end,expected_name,coordinate,expected_value,tolerance=.015):
    hit=unreal.SystemLibrary.line_trace_single(ev_world,ev_p(*start),ev_p(*end),unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,True,[],unreal.DrawDebugTrace.NONE,True)
    t=hit.to_tuple() if hit else None
    p=ev_local(t[4]) if t else None
    passed=bool(t and t[0] and t[9].get_actor_label()==expected_name and abs(p[coordinate]-expected_value)<tolerance)
    ev_checks.append({'check':label,'passed':passed,'hit_actor':t[9].get_actor_label() if t else None,'campus_m':p})
    assert passed,label
for ev_u,ev_v in [(8,12),(12,14),(18,20)]:
    ev_trace('Ceiling underside', (ev_u,ev_v,3),(ev_u,ev_v,4.5),'Dining Photo Detail | Ceiling',2,3.96)
ev_trace('Crossbeam underside',(12,16.2,3),(12,16.2,4.5),'Dining Photo Detail | Ceiling',2,3.63)
for ev_v in [12,17,21]:
    ev_trace('Lower wall finish',(19,ev_v,1.05),(19.8,ev_v,1.05),'Dining Photo Detail | WallFinish',0,19.6345)
    ev_trace('Upper wall paint',(19,ev_v,2.5),(19.8,ev_v,2.5),'Dining Photo Detail | WallPaint',0,19.645)
ev_furniture=json.loads((ev_root/'dining_furniture_build_report.json').read_text(encoding='utf-8'))
for ev_item in ev_furniture['placements']:
    ev_u,ev_v,_=ev_item['campus_m'];ev_a=ev_actors[ev_item['actor_name']]
    ev_z0,ev_z1=(1,.65) if ev_item['kind']=='table' else (.54,.30)
    ev_hit=unreal.SystemLibrary.line_trace_single(ev_world,ev_p(ev_u,ev_v,ev_z0),ev_p(ev_u,ev_v,ev_z1),unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,True,[],unreal.DrawDebugTrace.NONE,True)
    ev_ok=bool(ev_hit and ev_hit.to_tuple()[0] and ev_hit.to_tuple()[9]==ev_a)
    ev_checks.append({'check':ev_a.get_actor_label(),'passed':ev_ok});assert ev_ok
ev_door_count=sum(a.get_class().get_name()=='ATSAutoDoor' for a in ev_actors.values())
ev_ref_count=sum('ATS.OutdoorSeatingReference' in [str(t) for t in a.tags] for a in ev_actors.values())
assert ev_door_count==26 and ev_ref_count==1
assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
ev_report={'status':'passed','actor_count':len(ev_actors),'preexisting_actors_preserved':len(ev_before),'automatic_doors':ev_door_count,'outdoor_reference_count':ev_ref_count,'checks':ev_checks,'map_sha256':hashlib.sha256((ev_root/'Content/ATS/Maps/ATS_StudentCampus.umap').read_bytes()).hexdigest(),'full_room_verified':False}
(ev_root/'dining_envelope_validation.json').write_text(json.dumps(ev_report,ensure_ascii=False,indent=2),encoding='utf-8')
print('DINING_ENVELOPE_VALIDATION',len(ev_checks))
