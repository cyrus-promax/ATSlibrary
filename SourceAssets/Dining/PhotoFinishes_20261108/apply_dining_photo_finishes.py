import unreal,pathlib,json,math
af_root=pathlib.Path('D:/Cyrus/OneDrive/文件/香港仔工業學校/ATS');af_out=af_root/'SourceAssets/Dining/PhotoFinishes_20261108'
af_ed=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem);af_sub=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
assert not af_ed.get_game_world() and af_ed.get_editor_world().get_name()=='ATS_StudentCampus'
af_floor=unreal.load_asset('/Game/ATS/Dining/PhotoFinishes_20261108/Materials/M_Dining_BeigeFineTerrazzo_Dry')
af_paint=unreal.load_asset('/Game/ATS/Dining/PhotoFinishes_20261108/Materials/M_Dining_OffWhitePaint_Matte');assert af_floor and af_paint
af_changes=[]
for af_a in af_sub.get_all_level_actors():
 if af_a.get_actor_label() not in ['餐廳實體｜Floor','餐廳實體｜Walls','餐廳實體｜Ceiling','餐廳實體｜Kiosk']:continue
 af_comp=af_a.static_mesh_component
 for af_i,af_m in enumerate(af_comp.get_materials()):
  if af_m.get_name() not in ['M_DiningBuild_Terrazzo','M_DiningBuild_Paint','M_DiningBuild_Ceiling']:continue
  af_new=af_floor if af_m.get_name()=='M_DiningBuild_Terrazzo' else af_paint
  af_a.modify();af_comp.set_material(af_i,af_new)
  af_changes.append({'actor':af_a.get_name(),'label':af_a.get_actor_label(),'slot':af_i,'before':af_m.get_path_name(),'after':af_new.get_path_name()})
assert len(set(x['actor'] for x in af_changes))==3
# Keep 1.2 m between the window wall and rear of the closest chair for walking.
af_furniture=json.loads((af_out/'furniture_placement.json').read_text(encoding='utf-8'))
af_lookup={a.get_name():a for a in af_sub.get_all_level_actors()}
af_c,af_s=math.cos(math.radians(20)),math.sin(math.radians(20))
for af_item in af_furniture['placements']:
 if af_item['zone']!='靠窗':continue
 af_item['campus_m'][1]+=.30
 af_u,af_v,af_h=af_item['campus_m'];af_a=af_lookup[af_item['actor']];af_a.modify()
 af_a.set_actor_location(unreal.Vector((-8+af_c*af_u-af_s*af_v)*100,(24-af_s*af_u-af_c*af_v)*100,(-24.55+af_h)*100),False,True)
af_furniture['window_wall_to_chair_back_clearance_m']=1.2
(af_out/'furniture_placement.json').write_text(json.dumps(af_furniture,ensure_ascii=False,indent=2),encoding='utf-8')
assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
(af_out/'material_application.json').write_text(json.dumps({'status':'saved_pending_visual_validation','changes':af_changes,'lower_walls':'Existing lower-wall tiling remains unresolved; photo sources show different finishes and no positive wall registration. No whole-room pattern replacement or floor-band grid invented.'},ensure_ascii=False,indent=2),encoding='utf-8')
print('PHOTO_FINISHES_APPLIED',len(af_changes))
