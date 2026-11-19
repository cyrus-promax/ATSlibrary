import unreal,pathlib,json
wa_root=pathlib.Path('D:/Cyrus/OneDrive/文件/香港仔工業學校/ATS');wa_out=wa_root/'SourceAssets/Dining/WallFloorDetail_20261108'
wa_ed=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem);wa_sub=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
assert not wa_ed.get_game_world() and not (wa_out/'application.json').exists()
wa_mats={k:unreal.load_asset(v) for k,v in json.loads((wa_out/'material_creation.json').read_text(encoding='utf-8'))['materials'].items()};assert all(wa_mats.values())
wa_changes=[];wa_lights=[]
for wa_a in wa_sub.get_all_level_actors():
 if wa_a.get_actor_label() in ['餐廳實體｜Floor','餐廳實體｜Thresholds']:
  wa_a.modify();wa_comp=wa_a.static_mesh_component
  for wa_i,wa_old in enumerate(wa_comp.get_materials()):
   wa_comp.set_material(wa_i,wa_mats['floor']);wa_changes.append({'actor':wa_a.get_name(),'slot':wa_i,'before':wa_old.get_path_name(),'after':wa_mats['floor'].get_path_name()})
 if wa_a.get_actor_label()=='餐廳實體｜Tiles':
  wa_a.modify();wa_comp=wa_a.static_mesh_component
  for wa_i,wa_old in enumerate(wa_comp.get_materials()):
   wa_key={'M_Dining_Hall_BasketMosaic':'mosaic','M_Dining_Hall_CharcoalCap':'border','M_Dining_Hall_DarkTerrazzoSkirting':'skirting'}[wa_old.get_name()]
   wa_comp.set_material(wa_i,wa_mats[wa_key]);wa_changes.append({'actor':wa_a.get_name(),'slot':wa_i,'before':wa_old.get_path_name(),'after':wa_mats[wa_key].get_path_name()})
 if isinstance(wa_a,unreal.RectLight) and 'ATS.Dining.BuiltFromUserPlan' in [str(t) for t in wa_a.tags]:
  wa_c=wa_a.light_component;wa_before=float(wa_c.get_editor_property('temperature'));wa_a.modify();wa_c.set_editor_property('temperature',6000)
  wa_lights.append({'actor':wa_a.get_name(),'before':wa_before,'after':6000,'purpose':'Rendering white-balance adjustment toward neutral photographed surfaces, not a verified lamp specification.'})
assert len(wa_changes)==5 and len(wa_lights)==21,(len(wa_changes),len(wa_lights))
assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
(wa_out/'application.json').write_text(json.dumps({'status':'applied_pending_visual_check','materials':wa_changes,'lighting':wa_lights,'brightness_positions_and_lamp_geometry_unchanged':True},ensure_ascii=False,indent=2),encoding='utf-8')
print('WALL_FLOOR_APPLIED',len(wa_changes),len(wa_lights))
