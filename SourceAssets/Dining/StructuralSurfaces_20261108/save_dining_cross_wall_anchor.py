import json,pathlib,math,shutil
work=pathlib.Path(__file__).parent;root=pathlib.Path('D:/Cyrus/OneDrive/文件/香港仔工業學校/ATS');out=root/'SourceAssets/Dining/StructuralSurfaces_20261108'
cam=json.loads((out/'user_cross_wall_camera.json').read_text(encoding='utf-8'))
u,v,h=cam['camera_campus'];yaw=math.radians(cam['rotation']['yaw']);pitch=math.radians(cam['rotation']['pitch']);c,s=math.cos(math.radians(20)),math.sin(math.radians(20))
dx,dy,dz=math.cos(pitch)*math.cos(yaw),math.cos(pitch)*math.sin(yaw),math.sin(pitch)
du,dv=c*dx-s*dy,-s*dx-c*dy
distance=(.23-u)/du;assert distance>0
hit=[.23,v+distance*dv,h+distance*dz]
report={'user_reply':'現在視角正前方','fresh_camera':cam,'wall_identified':'u=.23; formerly blank western inner wall; top edge in the hand-drawn dining plan','photo_local_axes':{'W_cross_window_wall':'u=.23','L_continuous_window_wall':'v=3.67','R_opposite_reflective_wall_direction':'v=30.4'},'view_centre_ray_intersection_campus_m':hit,'cross_exact_position_confirmed':False,'warning':'The reply identifies a wall, not necessarily the cross exact position. Do not place the cross at this ray intersection until the user confirms or supplies another precise anchor.','remaining':['Window spacing and whole-wall bay count','Cross exact v and height','Interior column distances and main/transverse beam spans','Floor black-band widths and positions']}
(out/'cross_wall_direction.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
shutil.copy2(work/'dining_cross_wall_user_view.png',out/'User_CrossWall_View.png')
print('CROSS_WALL_DIRECTION',hit)
