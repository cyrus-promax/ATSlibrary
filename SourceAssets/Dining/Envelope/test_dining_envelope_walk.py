import unreal
import pathlib
import json
import math
import time
import traceback

ew_root=pathlib.Path('D:/Cyrus/OneDrive/文件/香港仔工業學校/ATS')
ew_level=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
ew_c,ew_s=math.cos(math.radians(20)),math.sin(math.radians(20))
def ew_point(u,v,h=.92):return unreal.Vector((-8+ew_c*u-ew_s*v)*100,(24-ew_s*u-ew_c*v)*100,(-24.55+h)*100)
def ew_local(p):
    x=p.x/100+8;y=-p.y/100+24
    return [ew_c*x+ew_s*y,-ew_s*x+ew_c*y,p.z/100+24.55]
ew_route=[('Approach from user position',(11.45,12.5)),('Central aisle',(11.45,17.95)),('Between dining rows',(8.3,17.95)),('Return into central aisle',(11.45,17.95)),('Behind dining sets',(11.45,22)),('Right outer passage',(14.8,22)),('Return to entrance side',(14.8,12.5))]
ew_report={'status':'running','method':'One initial test placement at user-indicated area, then CharacterMovement AddMovementInput only','checks':[]}
ew_start=time.monotonic();ew_way=ew_start;ew_i=0;ew_pawn=None
def ew_save():(ew_root/'dining_envelope_walk_verification.json').write_text(json.dumps(ew_report,ensure_ascii=False,indent=2),encoding='utf-8')
def ew_end(status):
    ew_report['status']=status;ew_report['seconds']=round(time.monotonic()-ew_start,2);ew_save()
    unreal.unregister_slate_post_tick_callback(ew_handle);ew_level.editor_request_end_play()
def ew_tick(dt):
    global ew_pawn,ew_way,ew_i
    try:
        now=time.monotonic()
        if ew_pawn is None:
            world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
            if not world:
                if now-ew_start>30:ew_end('no_game_world')
                return
            ew_pawn=unreal.GameplayStatics.get_player_character(world,0)
            if ew_pawn is None:return
            ew_pawn.set_actor_location(ew_point(13.51,12.05),False,True);ew_way=now;return
        p=ew_pawn.get_actor_location();label,xy=ew_route[ew_i];target=ew_point(*xy)
        dx,dy=target.x-p.x,target.y-p.y;distance=math.hypot(dx,dy)
        if distance<16:
            passed=abs(p.z-target.z)<25
            ew_report['checks'].append({'name':label,'passed':passed,'campus_position':ew_local(p),'height_error_cm':abs(p.z-target.z)})
            ew_pawn.character_movement.stop_movement_immediately();ew_save()
            if not passed:ew_end('failed');return
            ew_i+=1;ew_way=now
            if ew_i==len(ew_route):ew_end('passed')
            return
        if now-ew_way>30:
            ew_report['blocked_at']={'name':label,'position':ew_local(p)};ew_end('failed');return
        ew_pawn.add_movement_input(unreal.Vector(dx/distance,dy/distance,0),min(1,distance/100),True)
    except:
        ew_report['error']=traceback.format_exc();ew_end('error')
ew_save();ew_level.editor_request_begin_play();ew_handle=unreal.register_slate_post_tick_callback(ew_tick)
