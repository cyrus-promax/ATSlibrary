from pathlib import Path
import json,shutil,datetime,hashlib
root=Path('D:/Cyrus/OneDrive/文件/香港仔工業學校/ATS')
work=Path('C:/Users/Cyrus/Documents/Codex/2026-11-06/dao/work')
out=root/'SourceAssets/Dining/UserAlignment_20261107';out.mkdir(parents=True,exist_ok=True)
source=Path('D:/Cyrus/OneDrive/文件/香港仔工業學校/餐廳結構圖.png')
shutil.copy2(source,out/'餐廳結構圖_更新原圖.png')
for a,b in [('user_dining_alignment_snapshot.json','ue_view_and_scene_before.json'),('user_dining_aligned_view.png','UE_用戶對好視角.png')]:shutil.copy2(work/a,out/b)
# Fit the two court centre-lines horizontally. Match the two court top edges
# vertically and their average drawn depth to the existing seven-metre model.
# This registration locates the sketch; its pixel lengths are NOT a survey.
sx=(26.6-13.2)/(738.5-318.0)
sy=7.0/((213.0+237.0)/2.0)
def point(x,y):return [20+(y-254)*sy,13.2+(x-318)*sx,0.15]
features=[
 ('room','餐廳',[200,16,505,258]),
 ('outdoor','露天桌椅區',[150,10,200,261]),
 ('vita','維他天地',[200,157,289,258]),
 ('door_right_upper','右側門 1',[478,36,505,79]),
 ('door_right_lower','右側門 2',[475,126,505,177]),
 ('door_bottom','靠天井門',[303,232,361,258]),
 ('washbasin','洗手池',[368,238,459,258]),
 ('water','飲水機',[459,216,505,258])]
rows=[]
for key,label,(x0,y0,x1,y1) in features:
    rows.append({'id':key,'label':label,'diagram_rect':[x0,y0,x1,y1],'approx_center_campus':point((x0+x1)/2,(y0+y1)/2),'approx_corners_campus':[point(x0,y0),point(x1,y0),point(x1,y1),point(x0,y1)],'position_status':'registered_sketch_not_measured'})
courts=[]
for key,rect,model in [('left',[193,256,443,469],[20,27,9,17.4]),('right',[591,252,886,489],[20,27,22.6,30.6])]:
    x0,y0,x1,y1=rect;u0,u1,v0,v1=model
    residuals=[]
    for pix,real in zip([(x0,y0),(x1,y0),(x1,y1),(x0,y1)],[(u0,v0),(u0,v1),(u1,v1),(u1,v0)]):
        p=point(*pix);residuals.append(((p[0]-real[0])**2+(p[1]-real[1])**2)**.5)
    courts.append({'id':key,'diagram_rect':rect,'model_campus_bounds_uuvv':model,'registration_corner_residual_m':residuals})
prior=json.loads((root/'SourceAssets/Dining/dining_placement.json').read_text(encoding='utf-8'))
r=next(x for x in rows if x['id']=='room');u0,v0,_=r['approx_corners_campus'][0];u1,v1,_=r['approx_corners_campus'][2]
furniture=[]
for p in prior['placements']:
    if p['kind']=='table':
        u,v,_=p['campus_m'];furniture.append({'group':p['group'],'campus_m':p['campus_m'],'inside_approx_room':u0<=u<=u1 and v0<=v<=v1})
confirmation=json.loads((root/'SourceAssets/Dining/user_location_confirmation.json').read_text(encoding='utf-8'))
data={'recorded_at':datetime.datetime.now().astimezone().isoformat(),'user_statement':'我想起來了，是這樣的，UE視角我對好了','source_image':'餐廳結構圖_更新原圖.png','source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
 'anchor_confirmation':{'question':'新圖下方兩個沒有文字的方框，是否就是 UE 畫面下方並排、凹下去的兩個天井？','answer':'是，就是兩個天井'},
 'status':'orientation_and_relative_adjacency_user_confirmed_dimensions_unverified',
 'confirmed_relationships':['餐廳位於左邊天井圖上方','露天桌椅區位於餐廳圖左側','右側兩扇門和靠左天井一側的門','維他天地在餐廳左下；洗手池在下方門右邊；飲水機在右下角'],
 'transform':{'u':'20 + (image_y - 254) * sy','v':'13.2 + (image_x - 318) * sx','sx_metres_per_pixel_for_registration_only':sx,'sy_metres_per_pixel_for_registration_only':sy,'world_rotation_degrees':20,'world_enu_origin':[-8,-24,-24.55]},
 'features':rows,'courtyard_anchors':courts,'maximum_anchor_corner_residual_m':max(e for c in courts for e in c['registration_corner_residual_m']),
 'registration_is_measurement':False,'room_dimensions_verified':False,'door_destinations_verified':False,
 'old_table_centres_compared_to_new_diagram':furniture,'old_inside_confirmation_still_within_registered_area':u0<=13.5113964<=u1 and v0<=12.0470482<=v1,
 'limitations':['兩個天井在原圖的寬高比例與模型不完全相同，因此草圖不能用作精確量尺','絕對門寬、開門方向、牆厚、天花高度和完整柱網未核實','露天區新位置是依兩個天井對位的圖示範圍；此前靠街長廊的點位作歷史保留','家具數量、排列與設備型號未核實','右側兩門去向仍未知；靠天井門未與任何未核實通道接通'],
 'implementation':'Editor-only plan projection and G-floor reference markers, not physical partitions, equipment or room completion.'}
(out/'alignment.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'registration_bounds':[[u0,v0],[u1,v1]],'maximum_anchor_residual_m':data['maximum_anchor_corner_residual_m'],'old_tables':furniture,'old_inside_point_compatible':data['old_inside_confirmation_still_within_registered_area']},ensure_ascii=False))
