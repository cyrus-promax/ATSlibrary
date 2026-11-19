import unreal,pathlib,json,math,time,traceback
rw_ed=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem);rw_level=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
assert not rw_ed.get_game_world()
rw_camera=rw_ed.get_level_viewport_camera_info();rw_c,rw_s=math.cos(math.radians(20)),math.sin(math.radians(20))
rw_path=pathlib.Path('D:/Cyrus/OneDrive/文件/香港仔工業學校/ATS/dining_cross_windows_runtime.json')
def rw_p(u,v,h):return unreal.Vector((-8+rw_c*u-rw_s*v)*100,(24-rw_s*u-rw_c*v)*100,(-24.55+h)*100)
def rw_local(p):
 x,y=p.x/100+8,-p.y/100+24;return [rw_c*x+rw_s*y,-rw_s*x+rw_c*y,p.z/100+24.55]
rw_report={'status':'running','method':'One initial pawn placement, then CharacterMovement along both new windows and a jump toward the right window.','route':[],'initial_placements':0,'min_u':100,'max_jump_height':0}
rw_pawn=None;rw_index=0;rw_start=time.monotonic();rw_stage_started=rw_start;rw_finishing=False;rw_push_started=None;rw_jumped=False
rw_targets=[(1.15,16.18),(1.15,20.27)]
def rw_save():rw_path.write_text(json.dumps(rw_report,ensure_ascii=False,indent=2),encoding='utf-8')
def rw_finish(status):
 global rw_finishing
 rw_report['status']=status;rw_report['seconds']=round(time.monotonic()-rw_start,2);rw_save();rw_finishing=True;rw_level.editor_request_end_play()
def rw_tick(dt):
 global rw_pawn,rw_index,rw_stage_started,rw_push_started,rw_jumped
 try:
  now=time.monotonic()
  if rw_finishing:
   if not rw_ed.get_game_world():
    rw_ed.set_level_viewport_camera_info(*rw_camera);rw_report['camera_restored']=True;rw_save();unreal.unregister_slate_post_tick_callback(rw_handle)
   return
  world=rw_ed.get_game_world()
  if rw_pawn is None:
   if world:rw_pawn=unreal.GameplayStatics.get_player_character(world,0)
   if rw_pawn:
    rw_pawn.set_actor_location(rw_p(3,16.18,.96),False,True);rw_report['initial_placements']+=1;rw_stage_started=now
   elif now-rw_start>30:rw_finish('no_pawn')
   return
  pos=rw_pawn.get_actor_location();u,v,h=rw_local(pos)
  if rw_index<len(rw_targets):
   target=rw_p(*rw_targets[rw_index],.95);dx,dy=target.x-pos.x,target.y-pos.y;dist=math.hypot(dx,dy)
   if dist<17:
    rw_report['route'].append({'target':rw_targets[rw_index],'position':[u,v,h],'passed':abs(h-.95)<.25});rw_index+=1;rw_stage_started=now;rw_pawn.character_movement.stop_movement_immediately();rw_save()
   elif now-rw_stage_started>25:rw_report['blocked_at']=[u,v,h];rw_finish('walk_blocked')
   else:rw_pawn.add_movement_input(unreal.Vector(dx/dist,dy/dist,0),min(1,dist/100),True)
   return
  game_time=unreal.GameplayStatics.get_time_seconds(world)
  if rw_push_started is None:rw_push_started=game_time
  elapsed=game_time-rw_push_started
  rw_report['min_u']=min(rw_report['min_u'],u);rw_report['max_jump_height']=max(rw_report['max_jump_height'],h)
  rw_pawn.add_movement_input(unreal.Vector(-rw_c,rw_s,0),1,True)
  if elapsed>1.2 and not rw_jumped:rw_pawn.jump();rw_jumped=True
  if elapsed>1.7:rw_pawn.stop_jumping()
  if elapsed>5.5:
   rw_report['final_position']=[u,v,h];rw_report['window_blocked_jump']=rw_report['min_u']>.35 and rw_report['max_jump_height']>1.25
   rw_finish('passed' if rw_report['window_blocked_jump'] and all(x['passed'] for x in rw_report['route']) else 'failed')
 except Exception:rw_report['error']=traceback.format_exc();rw_finish('error')
rw_save();rw_level.editor_request_begin_play();rw_handle=unreal.register_slate_post_tick_callback(rw_tick)
