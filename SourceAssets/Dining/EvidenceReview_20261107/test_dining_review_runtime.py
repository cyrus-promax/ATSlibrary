import unreal,pathlib,json,math,time,traceback
drt_root=pathlib.Path('D:/Cyrus/OneDrive/文件/香港仔工業學校/ATS')
drt_ed=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
drt_level=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
assert not drt_ed.get_game_world()
drt_camera=drt_ed.get_level_viewport_camera_info()
drt_c,drt_s=math.cos(math.radians(20)),math.sin(math.radians(20))
def drt_point(u,v,h=.92):return unreal.Vector((-8+drt_c*u-drt_s*v)*100,(24-drt_s*u-drt_c*v)*100,(-24.55+h)*100)
drt_route=[('Original dining area approach',(11.45,12.5)),('Through former estimated furniture area',(11.45,17.95)),('Through former estimated ceiling coverage',(11.45,22))]
drt_report={'status':'running','checks':[],'method':'Inspect game-world reference actors and walk through the cleared area using CharacterMovement. No claim about real-world layout.'}
drt_start=time.monotonic();drt_way=drt_start;drt_i=0;drt_pawn=None;drt_finishing=False
def drt_save():(drt_root/'dining_evidence_review_runtime.json').write_text(json.dumps(drt_report,ensure_ascii=False,indent=2),encoding='utf-8')
def drt_end(status):
    global drt_finishing
    drt_report['status']=status;drt_report['seconds']=round(time.monotonic()-drt_start,2);drt_save()
    drt_finishing=True;drt_level.editor_request_end_play()
def drt_tick(dt):
    global drt_pawn,drt_way,drt_i
    try:
        now=time.monotonic()
        if drt_finishing:
            if not drt_ed.get_game_world():
                drt_ed.set_level_viewport_camera_info(*drt_camera)
                drt_report['camera_restored']=True;drt_save()
                unreal.unregister_slate_post_tick_callback(drt_handle)
            return
        if drt_pawn is None:
            world=drt_ed.get_game_world()
            if not world:
                if now-drt_start>30:drt_end('no_game_world')
                return
            drt_pawn=unreal.GameplayStatics.get_player_character(world,0)
            if drt_pawn is None:
                if now-drt_start>30:drt_end('no_character')
                return
            refs=unreal.GameplayStatics.get_all_actors_with_tag(world,unreal.Name('ATS.ReferenceOnly.UnverifiedDining'))
            observed=[]
            for a in refs:
                ok=a.get_editor_property('hidden') and not a.get_actor_enable_collision()
                for c in a.get_components_by_class(unreal.SceneComponent):
                    ok=ok and not c.get_editor_property('visible') and c.get_editor_property('hidden_in_game')
                    if isinstance(c,unreal.PrimitiveComponent):ok=ok and c.get_collision_enabled()==unreal.CollisionEnabled.NO_COLLISION
                observed.append({'name':a.get_name(),'inactive':bool(ok)})
            drt_report['game_world_reference_actors']=observed
            assert all(r['inactive'] for r in observed),'Reference actor active in game'
            drt_report['checks'].append({'name':'Unverified reference actors are absent or inactive in play','passed':True,'observed_count':len(refs)})
            drt_pawn.set_actor_location(drt_point(13.51,12.05),False,True);drt_way=now;drt_save();return
        p=drt_pawn.get_actor_location();label,xy=drt_route[drt_i];target=drt_point(*xy)
        dx,dy=target.x-p.x,target.y-p.y;distance=math.hypot(dx,dy)
        if distance<16:
            passed=abs(p.z-target.z)<25
            drt_report['checks'].append({'name':label,'passed':passed,'distance_cm':distance,'height_error_cm':abs(p.z-target.z)})
            drt_pawn.character_movement.stop_movement_immediately();drt_save()
            if not passed:drt_end('failed');return
            drt_i+=1;drt_way=now
            if drt_i==len(drt_route):drt_end('passed')
            return
        if now-drt_way>30:
            drt_report['blocked_at']=label;drt_end('failed');return
        drt_pawn.add_movement_input(unreal.Vector(dx/distance,dy/distance,0),min(1,distance/100),True)
    except:
        drt_report['error']=traceback.format_exc();drt_end('error')
drt_save();drt_level.editor_request_begin_play();drt_handle=unreal.register_slate_post_tick_callback(drt_tick)
