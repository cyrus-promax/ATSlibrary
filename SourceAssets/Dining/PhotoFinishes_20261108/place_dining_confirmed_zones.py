import unreal,pathlib,json,math
dz_root=pathlib.Path('D:/Cyrus/OneDrive/文件/香港仔工業學校/ATS');dz_out=dz_root/'SourceAssets/Dining/PhotoFinishes_20261108'
dz_ed=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem);dz_sub=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
assert not dz_ed.get_game_world() and dz_ed.get_editor_world().get_name()=='ATS_StudentCampus'
assert not any('ATS.Dining.PhotoConfirmedZones' in [str(t) for t in a.tags] for a in dz_sub.get_all_level_actors()),'Inspect placed furniture before retry.'
dz_table=unreal.load_asset('/Game/ATS/Dining/Meshes/SM_Dining_WhiteTable');dz_chair=unreal.load_asset('/Game/ATS/Dining/Meshes/SM_Dining_BlueChair');assert dz_table and dz_chair
dz_mat=unreal.AssetToolsHelpers.get_asset_tools().create_asset('M_DiningPhoto_DarkFurnitureFrame','/Game/ATS/Dining/PhotoFinishes_20261108/Materials',unreal.Material,unreal.MaterialFactoryNew());assert dz_mat
dz_ml=unreal.MaterialEditingLibrary
dz_col=dz_ml.create_material_expression(dz_mat,unreal.MaterialExpressionConstant3Vector,0,0);dz_col.set_editor_property('constant',unreal.LinearColor(.016,.019,.020,1));assert dz_ml.connect_material_property(dz_col,'',unreal.MaterialProperty.MP_BASE_COLOR)
for dz_prop,dz_val in [(unreal.MaterialProperty.MP_ROUGHNESS,.43),(unreal.MaterialProperty.MP_METALLIC,.35)]:
 dz_n=dz_ml.create_material_expression(dz_mat,unreal.MaterialExpressionConstant,0,0);dz_n.set_editor_property('r',dz_val);assert dz_ml.connect_material_property(dz_n,'',dz_prop)
dz_ml.recompile_material(dz_mat)
dz_c,dz_s=math.cos(math.radians(20)),math.sin(math.radians(20))
def dz_point(u,v,h):return unreal.Vector((-8+dz_c*u-dz_s*v)*100,(24-dz_s*u-dz_c*v)*100,(-24.55+h)*100)
dz_items=[]
# The user confirms central and window-side zones. These are minimal local samples,
# not a claim that the school has only two tables or four chairs per table.
for dz_zone,dz_u,dz_v in [('中央',8.0,19.8),('靠窗',8.7,5.6)]:
 dz_items.append({'kind':'table','zone':dz_zone,'campus_m':[dz_u,dz_v,.02],'yaw':-20})
 for dz_side in [-1,1]:
  for dz_dx in [-.48,.48]:dz_items.append({'kind':'chair','zone':dz_zone,'campus_m':[dz_u+dz_dx,dz_v+dz_side*.76,.02],'yaw':-20 if dz_side>0 else 160})
for dz_item in dz_items:
 dz_u,dz_v,_=dz_item['campus_m'];dz_hit=unreal.SystemLibrary.line_trace_single(dz_ed.get_editor_world(),dz_point(dz_u,dz_v,.18),dz_point(dz_u,dz_v,-.2),unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,True,[],unreal.DrawDebugTrace.NONE,True)
 assert dz_hit and dz_hit.to_tuple()[0],dz_item
 assert abs(dz_hit.to_tuple()[4].z/100+24.55-.02)<.03,dz_item
for dz_i,dz_item in enumerate(dz_items):
 dz_mesh=dz_table if dz_item['kind']=='table' else dz_chair
 dz_a=dz_sub.spawn_actor_from_class(unreal.StaticMeshActor,dz_point(*dz_item['campus_m']),unreal.Rotator(pitch=0,yaw=dz_item['yaw'],roll=0))
 dz_a.set_actor_label('餐廳桌椅｜'+dz_item['zone']+'｜'+('白枱' if dz_item['kind']=='table' else '藍椅')+' %02d'%(dz_i+1));dz_a.set_folder_path('Campus/Dining/Confirmed Zones')
 dz_a.tags=[unreal.Name(t) for t in ['ATS.Dining.PhotoConfirmedZones','ATS.Floor.G','ATS.Furniture.PhotoBased','ATS.Layout.UserConfirmedZone','ATS.Layout.ExactSpacingUnverified']]
 dz_comp=dz_a.static_mesh_component;dz_comp.set_static_mesh(dz_mesh)
 for dz_j,dz_slot in enumerate(dz_mesh.get_editor_property('static_materials')):
  if 'BrushedSteel' in str(dz_slot.get_editor_property('imported_material_slot_name')):dz_comp.set_material(dz_j,dz_mat)
 dz_comp.set_collision_profile_name('BlockAll');dz_comp.set_collision_enabled(unreal.CollisionEnabled.QUERY_AND_PHYSICS)
 dz_item.update(actor=dz_a.get_name(),label=dz_a.get_actor_label(),mesh=dz_mesh.get_path_name())
assert unreal.EditorAssetLibrary.save_loaded_asset(dz_mat)
assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
dz_report={'status':'minimal_furniture_groups_saved_in_user_confirmed_zones','tables_added':2,'chairs_added':8,'placements':dz_items,'user_confirmation':'中央和靠窗都有，可以參考網上圖片，但一定要確認了再做','photo_confirmation':'White rectangular tables, independent blue moulded chairs, dark frames and at least two opposite seats along each long side.','sources':['http://www.ats.edu.hk/images/PostImage/boarding_intro_10.jpg','http://www.ats.edu.hk/images/doc/2627_School_News_1.pdf'],'limitations':['Only central and window-side zones are user-confirmed. Exact coordinates and orientation are model-fitting estimates.','Two tables and eight chairs are a minimal partial reconstruction, not a verified whole-room count or standard per-table capacity.','Furniture dimensions remain visual modelling estimates.'],'preserved_clearances':'Window wall and serving frontage kept clear; central walking path at u10 retained; washbasin and shutter approaches unobstructed.'}
(dz_out/'furniture_placement.json').write_text(json.dumps(dz_report,ensure_ascii=False,indent=2),encoding='utf-8')
print('CONFIRMED_ZONE_FURNITURE_SAVED',len(dz_items))
