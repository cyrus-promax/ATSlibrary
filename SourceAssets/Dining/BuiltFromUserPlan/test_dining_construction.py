import unreal,pathlib,json,math,time,traceback
dt_root=pathlib.Path('D:/Cyrus/OneDrive/文件/香港仔工業學校/ATS')
dt_data=json.loads((dt_root/'SourceAssets/Dining/BuiltFromUserPlan/construction_manifest.json').read_text(encoding='utf-8'))
dt_ed=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem);dt_level=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);dt_sub=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
dt_c,dt_s=math.cos(math.radians(20)),math.sin(math.radians(20))
def dt_point(u,v,h):return unreal.Vector((-8+dt_c*u-dt_s*v)*100,(24-dt_s*u-dt_c*v)*100,(-24.55+h)*100)
def dt_local(p):
 x=p.x/100+8;y=-p.y/100+24;return [dt_c*x+dt_s*y,-dt_s*x+dt_c*y,p.z/100+24.55]
dt_world=dt_ed.get_editor_world();dt_doors=[a for a in dt_sub.get_all_level_actors() if 'ATS.Dining.BuiltFromUserPlan' in [str(t) for t in a.tags] and a.get_class().get_name()=='ATSAutoDoor']
assert len(dt_doors)==3
def dt_hit(a,b,ignore=dt_doors):
 h=unreal.SystemLibrary.line_trace_single(dt_world,dt_point(*a),dt_point(*b),unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,True,ignore,unreal.DrawDebugTrace.NONE,True)
 if not h:return None
 row=h.to_tuple();return {'blocking':row[0],'actor':row[9].get_actor_label() if row[9] else None,'point':dt_local(row[4])}
dt_checks=[]
for d in dt_data['doors']:
 u,v,h=d['center']
 for height in [.2,.9,1.75,2.5]:
  a,b=((u,v-.7,height),(u,v+.7,height)) if d['axis']=='u' else ((u-.7,v,height),(u+.7,v,height))
  hit=dt_hit(a,b);dt_checks.append({'name':d['id']+' open aperture at '+str(height),'passed':not hit or not hit['blocking'],'hit':hit})
for name,a,b,blocked in [('Top wall',(13.1,14,1.4),(12.1,14,1.4),True),('Right wall',(15.2,18.4,1.4),(15.2,19.8,1.4),True),('Shop partition',(18,12.9,1.4),(18,11.9,1.4),True),('Shop serving opening',(16.4,10.8,1.6),(17.5,10.8,1.6),False),('Indoor ceiling',(15,14,2.8),(15,14,5),True),('Open-air strip',(16,8.6,.5),(16,8.6,30),False),('Original upper wall retained',(19.1,13.65,5),(20.5,13.65,5),True)]:
 hit=dt_hit(a,b);dt_checks.append({'name':name,'passed':bool(hit and hit['blocking'])==blocked,'hit':hit})
for u,v in [(14,14),(18,14),(18.5,18),(16,8.6),(20.3,13.65)]:
 hit=dt_hit((u,v,.5),(u,v,-.5));dt_checks.append({'name':'Floor '+str((u,v)),'passed':bool(hit and hit['blocking'] and abs(hit['point'][2])<.1),'hit':hit})
dt_report={'status':'running','static_checks':dt_checks,'walk_checks':[],'door_observations':{},'method':'One initial placement outside the existing school gate; every later waypoint uses CharacterMovement. Existing entrance and all three new doors are physically traversed.'}
def dt_save():(dt_root/'dining_construction_validation.json').write_text(json.dumps(dt_report,ensure_ascii=False,indent=2),encoding='utf-8')
if not all(r['passed'] for r in dt_checks):
 dt_report['status']='static_failed';dt_save();raise RuntimeError('Dining static checks failed')
dt_camera=dt_ed.get_level_viewport_camera_info()
dt_route=[('Existing school entrance',(27.8,-2)),('Existing lobby',(27.8,5)),('Existing left lobby opening',(23.5,5)),('Existing courtyard approach',(23.5,13.646)),('Approach new courtyard door',(21.25,13.646)),('Enter dining through courtyard door',(18.60,13.646)),('Tuck shop serving window',(16.15,10.85)),('Washbasin approach',(18.25,16.15)),('Drinking fountain approach',(18.20,18.25)),('Approach lower right door',(16.811,17.8)),('Exit lower right door',(16.811,20.6)),('Outside upper right door',(13.887,20.6)),('Enter upper right door',(13.887,17.8)),('Dining window side',(14.5,10.3)),('Return to upper right door',(13.887,17.8)),('Exit upper right door',(13.887,20.6)),('Around northern room wall',(11.6,20.6)),('Approach open-air strip',(11.6,8.64)),('Walk along open-air strip',(17.3,8.64))]
dt_pawn=None;dt_start=time.monotonic();dt_way=dt_start;dt_index=0;dt_finishing=False;dt_wait_close=None;dt_runtime_doors=[]
def dt_finish(status):
 global dt_finishing
 dt_report['status']=status;dt_report['seconds']=round(time.monotonic()-dt_start,2);dt_save();dt_finishing=True;dt_level.editor_request_end_play()
def dt_tick(delta):
 global dt_pawn,dt_way,dt_index,dt_wait_close,dt_runtime_doors
 try:
  now=time.monotonic()
  if dt_finishing:
   if not dt_ed.get_game_world():
    dt_ed.set_level_viewport_camera_info(*dt_camera);dt_report['camera_restored']=True;dt_save();unreal.unregister_slate_post_tick_callback(dt_handle)
   return
  if dt_pawn is None:
   w=dt_ed.get_game_world()
   if not w:
    if now-dt_start>30:dt_finish('no_game_world')
    return
   dt_pawn=unreal.GameplayStatics.get_player_character(w,0)
   if not dt_pawn:
    if now-dt_start>30:dt_finish('no_pawn')
    return
   dt_runtime_doors=[a for a in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.load_class(None,'/Script/ATS.ATSAutoDoor')) if 'ATS.Dining.BuiltFromUserPlan' in [str(t) for t in a.tags]]
   for a in dt_runtime_doors:dt_report['door_observations'][a.get_name()]={'max_angle':0,'opened':False,'closed_after_leaving':False}
   dt_pawn.set_actor_location(dt_point(27.8,-8,.96),False,True);dt_way=now;return
  for a in dt_runtime_doors:
   angle=abs(a.get_editor_property('current_angle'));record=dt_report['door_observations'][a.get_name()];record['max_angle']=max(record['max_angle'],angle);record['opened']|=angle>85
  if dt_wait_close is not None:
   if now-dt_wait_close>4:
    for a in dt_runtime_doors:
     record=dt_report['door_observations'][a.get_name()];record['closed_after_leaving']=abs(a.get_editor_property('current_angle'))<1;record['collision_restored']=a.get_editor_property('leaf').get_collision_enabled()==unreal.CollisionEnabled.QUERY_AND_PHYSICS
    dt_finish('passed' if all(r['opened'] and r['closed_after_leaving'] and r['collision_restored'] for r in dt_report['door_observations'].values()) else 'door_failed')
   return
  label,xy=dt_route[dt_index];p=dt_pawn.get_actor_location();target=dt_point(*xy,.95);dx,dy=target.x-p.x,target.y-p.y;distance=math.hypot(dx,dy)
  if distance<19:
   ok=abs(p.z-target.z)<25;dt_report['walk_checks'].append({'name':label,'passed':ok,'campus_position':dt_local(p),'height_error_cm':abs(p.z-target.z)})
   dt_pawn.character_movement.stop_movement_immediately();dt_save()
   if not ok:dt_finish('walk_height_failed');return
   dt_index+=1;dt_way=now
   if dt_index==len(dt_route):dt_wait_close=now
   return
  if now-dt_way>24:
   dt_report['blocked_at']={'name':label,'campus_position':dt_local(p),'target':xy};dt_finish('walk_blocked');return
  dt_pawn.add_movement_input(unreal.Vector(dx/distance,dy/distance,0),min(1,distance/100),True)
 except:
  dt_report['error']=traceback.format_exc();dt_finish('error')
dt_save();dt_level.editor_request_begin_play();dt_handle=unreal.register_slate_post_tick_callback(dt_tick)
