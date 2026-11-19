import unreal,time,json,math,pathlib,traceback
wt_out=pathlib.Path('D:/Cyrus/OneDrive/文件/香港仔工業學校/ATS/SourceAssets/LibraryWorkshop_20261108')
wt_ed=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem);wt_level=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
assert wt_ed.get_editor_world().get_name()=='ATS_Library_Workshop' and not wt_ed.get_game_world()
wt_route=[('Main start',(.9,5.65,0),False),('Main aisle',(13.0,5.65,0),False),('Main cutaway exit',(15.0,5.65,-.12),False),('Step approach',(18.5,1.8,-.12),False),('Step entry',(20.8,1.8,0),False),('Step aisle',(25.0,1.8,0),False),('Double door approach',(27.7,.8,0),True),('Double door through',(27.7,-1.3,-.12),True),('Double door return',(27.7,1.1,0),True),('Step leave',(20.8,1.8,0),False),('Display route',(18.5,1.8,-.12),False),('Lecture approach',(12.0,12.0,-.12),False),('Lecture door outside',(9.3,16.6,-.12),True),('Lecture door through',(7.1,16.6,0),True),('Lecture floor',(4.4,18.5,0),False),('Lecture return',(7.1,16.6,0),True),('Lecture exit',(9.3,16.6,-.12),True),('Culture approach',(17.0,16.6,-.12),False),('Culture entry',(20.3,16.8,0),False),('Culture side aisle',(23.0,16.75,0),False)]
wt_report={'status':'running','method':'Existing ATS character; AddMovementInput only; no pawn teleport or position setting.','checks':[],'samples':[]}
wt_started=time.monotonic();wt_way=wt_started;wt_index=0;wt_pawn=None;wt_world=None;wt_nextsample=0;wt_prev=None;wt_peak=0
def wt_save():(wt_out/'walk_validation.json').write_text(json.dumps(wt_report,ensure_ascii=False,indent=2),encoding='utf-8')
def wt_finish(status):
 wt_report['status']=status;wt_report['elapsed_seconds']=round(time.monotonic()-wt_started,2);wt_save();unreal.unregister_slate_post_tick_callback(wt_handle);wt_level.editor_request_end_play()
def wt_tick(delta):
 global wt_way,wt_index,wt_pawn,wt_world,wt_nextsample,wt_prev,wt_peak
 try:
  now=time.monotonic()
  if wt_pawn is None:
   if now-wt_started<5:return
   wt_world=wt_ed.get_game_world();wt_pawn=unreal.GameplayStatics.get_player_character(wt_world,0) if wt_world else None
   if not wt_pawn:
    if now-wt_started>40:raise RuntimeError('No runtime player')
    return
   wt_report['character_class']=wt_pawn.get_class().get_path_name();wt_way=now
  p=wt_pawn.get_actor_location()
  if wt_prev:wt_peak=max(wt_peak,(p-wt_prev).length())
  wt_prev=p;wt_report['max_frame_displacement_cm']=round(wt_peak,2)
  if now>=wt_nextsample:
   wt_report['samples'].append({'seconds':round(now-wt_started,2),'location_cm':[p.x,p.y,p.z]});wt_nextsample=now+1
  label,xyz,doorcheck=wt_route[wt_index];target=unreal.Vector(xyz[0]*100,-xyz[1]*100,xyz[2]*100+90);dx,dy=target.x-p.x,target.y-p.y;dist=math.hypot(dx,dy)
  if dist<18:
   row={'name':label,'passed':abs(p.z-target.z)<32,'height_error_cm':round(abs(p.z-target.z),2),'actual_cm':[p.x,p.y,p.z]}
   if doorcheck:
    near=[{'label':a.get_actor_label(),'angle':a.get_editor_property('current_angle')} for a in unreal.GameplayStatics.get_all_actors_of_class(wt_world,unreal.load_class(None,'/Script/ATS.ATSAutoDoor')) if (a.get_actor_location()-p).length2d()<230]
    row['nearby_doors']=near;row['passed']=row['passed'] and any(abs(d['angle'])>8 for d in near)
   wt_report['checks'].append(row);wt_save()
   if not row['passed']:wt_finish('failed');return
   wt_pawn.character_movement.stop_movement_immediately();wt_index+=1;wt_way=now
   if wt_index==len(wt_route):wt_finish('passed')
   return
  if now-wt_way>28:
   wt_report['checks'].append({'name':label,'passed':False,'reason':'Movement blocked or timed out','actual_cm':[p.x,p.y,p.z],'target_cm':[target.x,target.y,target.z]});wt_finish('failed');return
  wt_pawn.add_movement_input(unreal.Vector(dx/dist,dy/dist,0),min(1.0,dist/140),True)
  controller=unreal.GameplayStatics.get_player_controller(wt_world,0);rot=unreal.Rotator(pitch=0,yaw=math.degrees(math.atan2(dy,dx)),roll=0);controller.set_control_rotation(rot)
  wt_pawn.get_editor_property('arm').set_world_rotation(rot,False,False)
 except Exception:wt_report['error']=traceback.format_exc();wt_finish('error')
wt_save();wt_level.editor_request_begin_play();wt_handle=unreal.register_slate_post_tick_callback(wt_tick)
