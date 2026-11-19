import unreal,pathlib,json,math,time,traceback
kt_ed=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem);kt_level=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
assert not kt_ed.get_game_world()
kt_camera=kt_ed.get_level_viewport_camera_info()
kt_out=pathlib.Path('D:/Cyrus/OneDrive/文件/香港仔工業學校/ATS/SourceAssets/KnownDetails_20261108/door_runtime.json')
def kt_pos(x,y,h):
 a=math.radians(-22.5);u,v=98+math.cos(a)*(x-94)-math.sin(a)*(y-31.9),15.5+math.sin(a)*(x-94)+math.cos(a)*(y-31.9)
 c,s=math.cos(math.radians(20)),math.sin(math.radians(20))
 return unreal.Vector((-8+c*u-s*v)*100,(24-s*u-c*v)*100,(-24.55+h)*100)
kt_result={'status':'running','method':'One placement on existing first-floor corridor; actual CharacterMovement through existing Class_1_1 door and back.','initial_placements':0,'steps':[]}
kt_route=[('enter_classroom',(59.8,34.05,4.45)),('return_corridor',(59.8,31.8,4.45))]
kt_pawn=None;kt_i=0;kt_start=time.monotonic();kt_step=kt_start;kt_finishing=False;kt_settled=False
def kt_save():kt_out.write_text(json.dumps(kt_result,ensure_ascii=False,indent=2),encoding='utf-8')
def kt_finish(status):
 global kt_finishing
 kt_result['status']=status;kt_result['seconds']=round(time.monotonic()-kt_start,2);kt_save();kt_finishing=True;kt_level.editor_request_end_play()
def kt_tick(dt):
 global kt_pawn,kt_i,kt_step,kt_settled
 try:
  now=time.monotonic()
  if kt_finishing:
   if not kt_ed.get_game_world():kt_ed.set_level_viewport_camera_info(*kt_camera);kt_result['editor_restored']=True;kt_save();unreal.unregister_slate_post_tick_callback(kt_handle)
   return
  world=kt_ed.get_game_world()
  if kt_pawn is None:
   if world:kt_pawn=unreal.GameplayStatics.get_player_character(world,0)
   if kt_pawn:
    kt_pawn.set_actor_location(kt_pos(59.8,31.8,4.48),False,True);kt_pawn.character_movement.stop_movement_immediately();kt_result['initial_placements']+=1;kt_step=now
   elif now-kt_start>25:kt_finish('no_player')
   return
  if not kt_settled:
   if now-kt_step<1.5:return
   kt_settled=True;kt_step=now
  name,local=kt_route[kt_i];target=kt_pos(*local);p=kt_pawn.get_actor_location();dx,dy=target.x-p.x,target.y-p.y;dist=math.hypot(dx,dy)
  if dist<15:
   passed=abs(p.z-target.z)<30
   kt_result['steps'].append({'name':name,'passed':passed,'horizontal_error_cm':dist,'height_error_cm':abs(p.z-target.z),'world_position':[p.x,p.y,p.z]});kt_save();kt_pawn.character_movement.stop_movement_immediately()
   if not passed:kt_finish('wrong_floor');return
   kt_i+=1;kt_step=now
   if kt_i==len(kt_route):kt_finish('passed')
  elif now-kt_step>18:
   kt_result['blocked_at']={'step':name,'world_position':[p.x,p.y,p.z],'distance_cm':dist};kt_finish('blocked')
  else:kt_pawn.add_movement_input(unreal.Vector(dx/dist,dy/dist,0),min(1,dist/100),True)
 except Exception:kt_result['error']=traceback.format_exc();kt_finish('error')
kt_save();kt_level.editor_request_begin_play();kt_handle=unreal.register_slate_post_tick_callback(kt_tick)
