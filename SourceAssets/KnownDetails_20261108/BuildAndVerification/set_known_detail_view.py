import unreal,pathlib,json,math
kv_work=pathlib.Path('C:/Users/Cyrus/Documents/Codex/2026-11-06/dao/work');kv_root=pathlib.Path('D:/Cyrus/OneDrive/文件/香港仔工業學校/ATS')
kv_request=json.loads((kv_work/'known_detail_view_request.json').read_text(encoding='utf-8'));kv_ed=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
def kv_pos(x,y,z,teaching=False):
 if teaching:
  a=math.radians(-22.5);x,y=98+math.cos(a)*(x-94)-math.sin(a)*(y-31.9),15.5+math.sin(a)*(x-94)+math.cos(a)*(y-31.9)
 a=math.radians(20);c,s=math.cos(a),math.sin(a)
 return unreal.Vector((-8+c*x-s*y)*100,(24-s*x-c*y)*100,(-24.55+z)*100)
kv_cv=json.loads((kv_root/'SourceAssets/Dining/CrossWindowWall_20261108/anchor_confirmation.json').read_text(encoding='utf-8'))['confirmed_horizontal_v']
kv_views={
 'corridor':[(86.4,31.9,22.65,True),(60,31.9,22.3,True)],
 'skirting':[(81.5,31.7,22.15,True),(79.5,30.895,21.35,True)],
 'hall':[(37.1,5.5,2.4),(37.1,22.8,7.0)],
 'ac':[(2.8,kv_cv-1.1,2.7),(.3,kv_cv-1.1,2.8)]}
if kv_request['view']=='restore':
 p=json.loads((kv_root/'SourceAssets/KnownDetails_20261108/preparation.json').read_text(encoding='utf-8'))
 kv_ed.set_level_viewport_camera_info(unreal.Vector(*p['camera_world']),unreal.Rotator(**p['rotation']))
else:
 eye,target=kv_views[kv_request['view']];e,t=kv_pos(*eye),kv_pos(*target)
 kv_ed.set_level_viewport_camera_info(e,unreal.MathLibrary.find_look_at_rotation(e,t))
