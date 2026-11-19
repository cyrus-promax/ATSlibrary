import unreal,pathlib,json,math,re
dc_root=pathlib.Path('D:/Cyrus/OneDrive/文件/香港仔工業學校/ATS')
dc_out=dc_root/'SourceAssets/Dining/BuiltFromUserPlan'
dc_manifest=json.loads((dc_out/'construction_manifest.json').read_text(encoding='utf-8'))
dc_prep=json.loads((dc_out/'preparation.json').read_text(encoding='utf-8'))
dc_before=json.loads((pathlib.Path(dc_prep['backup'])/'scene_before.json').read_text(encoding='utf-8'))
dc_sub=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);dc_ed=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem);dc_level=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
assert not dc_ed.get_game_world() and dc_ed.get_editor_world().get_name()=='ATS_StudentCampus'
assert not any('ATS.Dining.BuiltFromUserPlan' in [str(t) for t in a.tags] for a in dc_sub.get_all_level_actors())
dc_tools=unreal.AssetToolsHelpers.get_asset_tools();dc_ml=unreal.MaterialEditingLibrary;dc_lib=unreal.EditorAssetLibrary;dc_path='/Game/ATS/Dining/BuiltFromUserPlan'
dc_camera=dc_ed.get_level_viewport_camera_info()
dc_textures={}
for dc_base in ['terrazzo_tiles','concrete_wall_003']:
 for dc_channel in ['diff','nor_dx','rough']:
  dc_filename=f'{dc_base}_{dc_channel}_4k.jpg';dc_t=unreal.AssetImportTask();dc_t.filename=str(dc_root/'SourceAssets/PBR'/dc_filename);dc_t.destination_path=dc_path+'/Textures';dc_t.automated=True;dc_t.replace_existing=False;dc_t.save=False
  dc_tools.import_asset_tasks([dc_t]);dc_tex=next(o for o in dc_t.get_objects() if isinstance(o,unreal.Texture2D))
  dc_tex.set_editor_property('srgb',dc_channel=='diff')
  if dc_channel=='nor_dx':dc_tex.set_editor_property('compression_settings',unreal.TextureCompressionSettings.TC_NORMALMAP)
  dc_textures[(dc_base,dc_channel)]=dc_tex
def dc_const(m,value,prop):
 n=dc_ml.create_material_expression(m,unreal.MaterialExpressionConstant,0,0);n.set_editor_property('r',value);assert dc_ml.connect_material_property(n,'',prop)
dc_mats={}
for dc_name,dc_spec in dc_manifest['materials'].items():
 dc_m=dc_tools.create_asset('M_DiningBuild_'+dc_name,dc_path+'/Materials',unreal.Material,unreal.MaterialFactoryNew());assert dc_m
 dc_n=dc_ml.create_material_expression(dc_m,unreal.MaterialExpressionConstant3Vector,0,0);dc_n.set_editor_property('constant',unreal.LinearColor(*dc_spec['colour_linear'],1));assert dc_ml.connect_material_property(dc_n,'',unreal.MaterialProperty.MP_BASE_COLOR)
 dc_const(dc_m,dc_spec['roughness'],unreal.MaterialProperty.MP_ROUGHNESS);dc_const(dc_m,dc_spec['metallic'],unreal.MaterialProperty.MP_METALLIC)
 if dc_name=='Glass':
  dc_m.set_editor_property('blend_mode',unreal.BlendMode.BLEND_TRANSLUCENT);dc_m.set_editor_property('two_sided',True);dc_const(dc_m,.16,unreal.MaterialProperty.MP_OPACITY)
 if dc_name=='Lamp':
  dc_mul=dc_ml.create_material_expression(dc_m,unreal.MaterialExpressionMultiply,200,0);dc_mul.set_editor_property('const_b',30);dc_ml.connect_material_expressions(dc_n,'',dc_mul,'A');dc_ml.connect_material_property(dc_mul,'',unreal.MaterialProperty.MP_EMISSIVE_COLOR)
 if dc_name in ['Terrazzo','Concrete']:
  dc_base='terrazzo_tiles' if dc_name=='Terrazzo' else 'concrete_wall_003'
  for dc_channel,dc_prop in [('diff',unreal.MaterialProperty.MP_BASE_COLOR),('nor_dx',unreal.MaterialProperty.MP_NORMAL),('rough',unreal.MaterialProperty.MP_ROUGHNESS)]:
   dc_sample=dc_ml.create_material_expression(dc_m,unreal.MaterialExpressionTextureSample,0,250);dc_sample.set_editor_property('texture',dc_textures[(dc_base,dc_channel)])
   dc_sample.set_editor_property('sampler_type',unreal.MaterialSamplerType.SAMPLERTYPE_NORMAL if dc_channel=='nor_dx' else (unreal.MaterialSamplerType.SAMPLERTYPE_COLOR if dc_channel=='diff' else unreal.MaterialSamplerType.SAMPLERTYPE_LINEAR_COLOR))
   assert dc_ml.connect_material_property(dc_sample,'RGB',dc_prop)
 if dc_name=='Terrazzo':
  dc_original=dc_ml.get_material_property_input_node(dc_m,unreal.MaterialProperty.MP_BASE_COLOR)
  dc_desat=dc_ml.create_material_expression(dc_m,unreal.MaterialExpressionDesaturation,250,0);dc_names=dc_ml.get_material_expression_input_names(dc_desat)
  dc_fraction=dc_ml.create_material_expression(dc_m,unreal.MaterialExpressionConstant,0,450);dc_fraction.set_editor_property('r',.90)
  assert dc_ml.connect_material_expressions(dc_original,'RGB',dc_desat,str(dc_names[0]))
  assert dc_ml.connect_material_expressions(dc_fraction,'',dc_desat,str(dc_names[1]))
  assert dc_ml.connect_material_property(dc_desat,'',unreal.MaterialProperty.MP_BASE_COLOR)
 dc_ml.recompile_material(dc_m);dc_mats['M_DiningBuild_'+dc_name]=dc_m
def dc_import(file,folder):
 opts=unreal.FbxImportUI();opts.import_mesh=True;opts.import_as_skeletal=False;opts.import_materials=False;opts.import_textures=False;opts.import_animations=False;opts.automated_import_should_detect_type=False;opts.mesh_type_to_import=unreal.FBXImportType.FBXIT_STATIC_MESH
 data=opts.static_mesh_import_data;data.combine_meshes=False;data.auto_generate_collision=False;data.transform_vertex_to_absolute=True;data.convert_scene_unit=True;data.generate_lightmap_u_vs=False;data.normal_import_method=unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS
 task=unreal.AssetImportTask();task.filename=str(dc_out/file);task.destination_path=folder;task.automated=True;task.replace_existing=False;task.save=False;task.options=opts;task.factory=unreal.FbxFactory();dc_tools.import_asset_tasks([task])
 return [o for o in task.get_objects() if isinstance(o,unreal.StaticMesh)]
dc_meshes=dc_import('ATS_Dining_Built.fbx',dc_path+'/Meshes');assert len(dc_meshes)==16,len(dc_meshes)
dc_actor_lookup={a.get_name():a for a in dc_sub.get_all_level_actors()}
dc_added=[];dc_modified=[]
def dc_tag(a,label):
 a.set_actor_label(label);a.set_folder_path('Campus/Dining');a.tags=[unreal.Name('ATS.Dining.BuiltFromUserPlan'),unreal.Name('ATS.Floor.G')];dc_added.append(a)
for dc_mesh in dc_meshes:
 dc_key=re.search('SM_Dining(?:Built|Patch)_.*',dc_mesh.get_name()).group()
 if dc_key.startswith('SM_DiningPatch_'):
  dc_label='HistoricWestWing | M_Interior_FacadeWhite' if dc_key.endswith('OldWall') else 'HistoricRoof | M_Interior_RoofConcrete'
  dc_old=next(a for a in dc_actor_lookup.values() if a.get_actor_label()==dc_label)
  dc_mesh.set_material(0,dc_old.static_mesh_component.get_material(0));dc_mesh.get_editor_property('body_setup').set_editor_property('collision_trace_flag',unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
  dc_old.modify();dc_old.static_mesh_component.set_static_mesh(dc_mesh);dc_modified.append(dc_old.get_name());continue
 dc_item=next(x for x in dc_manifest['meshes'] if x['name']==dc_key)
 for dc_i,dc_slot in enumerate(dc_mesh.get_editor_property('static_materials')):
  dc_mesh.set_material(dc_i,dc_mats[str(dc_slot.get_editor_property('imported_material_slot_name'))])
 dc_mesh.get_editor_property('body_setup').set_editor_property('collision_trace_flag',unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
 dc_a=dc_sub.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector());dc_tag(dc_a,'餐廳實體｜'+dc_item['group']);dc_c=dc_a.static_mesh_component;dc_c.set_static_mesh(dc_mesh)
 dc_c.set_collision_profile_name('BlockAll' if dc_item['collision'] else 'NoCollision');dc_c.set_collision_enabled(unreal.CollisionEnabled.QUERY_AND_PHYSICS if dc_item['collision'] else unreal.CollisionEnabled.NO_COLLISION)
 if dc_item['group'] in ['Glass','Tiles','Sign','Lighting']:dc_c.set_editor_property('cast_shadow',False)
dc_door_mesh=dc_import('SM_Dining_Door.fbx',dc_path+'/Doors')[0]
for dc_i,dc_slot in enumerate(dc_door_mesh.get_editor_property('static_materials')):dc_door_mesh.set_material(dc_i,dc_mats[str(dc_slot.get_editor_property('imported_material_slot_name'))])
dc_door_mesh.get_editor_property('body_setup').set_editor_property('collision_trace_flag',unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
dc_cos,dc_sin=math.cos(math.radians(20)),math.sin(math.radians(20))
def dc_point(p):
 u,v,h=p;return unreal.Vector((-8+dc_cos*u-dc_sin*v)*100,(24-dc_sin*u-dc_cos*v)*100,(-24.55+h)*100)
dc_door_class=unreal.load_class(None,'/Script/ATS.ATSAutoDoor')
dc_doors=[]
for dc_d in dc_manifest['doors']:
 dc_a=dc_sub.spawn_actor_from_class(dc_door_class,dc_point(dc_d['hinge']),unreal.Rotator(pitch=0,yaw=dc_d['yaw'],roll=0));dc_tag(dc_a,'餐廳自動門｜'+dc_d['id'])
 dc_a.get_editor_property('leaf').set_static_mesh(dc_door_mesh);dc_a.set_editor_property('open_angle',dc_d['open_angle']);dc_a.set_editor_property('approach_distance',170.0);dc_a.tags=list(dc_a.tags)+[unreal.Name('ATS.DiningDoor.'+dc_d['id'])];dc_doors.append({'id':dc_d['id'],'actor':dc_a.get_name()})
for dc_i,dc_l in enumerate(dc_manifest['lights']):
 dc_a=dc_sub.spawn_actor_from_class(unreal.RectLight,dc_point(dc_l['campus_m']),unreal.Rotator(pitch=-90,yaw=-20,roll=0));dc_tag(dc_a,'餐廳照明 %02d'%(dc_i+1));dc_c=dc_a.get_component_by_class(unreal.RectLightComponent)
 for dc_prop,dc_val in [('intensity_units',unreal.LightUnits.LUMENS),('intensity',dc_l['lumens']),('source_width',dc_l['width_cm']),('source_height',dc_l['height_cm']),('attenuation_radius',900),('use_temperature',True),('temperature',5300),('cast_shadows',True)]:dc_c.set_editor_property(dc_prop,dc_val)
 dc_c.set_mobility(unreal.ComponentMobility.MOVABLE)
# Remove the assistant-created drawing projection instead of calling it construction.
dc_removed=[]
for dc_a in dc_actor_lookup.values():
 if 'ATS.DiningPlan.Aligned20261107' in [str(t) for t in dc_a.tags]:dc_removed.append(dc_a.get_name());assert dc_sub.destroy_actor(dc_a)
assert len(dc_removed)==14
assert dc_lib.save_directory(dc_path,only_if_is_dirty=True,recursive=True)
assert dc_level.save_current_level()
dc_after={a.get_name():a for a in dc_sub.get_all_level_actors()}
assert len(dc_after)==len(dc_before)-14+22
for dc_name,dc_row in dc_before.items():
 if dc_name not in dc_removed+dc_modified:assert db_snapshot(dc_after[dc_name])==dc_row,dc_name
assert dc_ed.get_level_viewport_camera_info()==dc_camera
dc_report={'status':'physical_dining_saved','backup':dc_prep['backup'],'actors_before':len(dc_before),'actors_after':len(dc_after),'new_physical_mesh_actors':14,'new_auto_doors':dc_doors,'new_lights':5,'modified_existing_mesh_actors':dc_modified,'projection_actors_removed':dc_removed,'other_existing_actors_unchanged':len(dc_before)-len(dc_removed)-len(dc_modified),'user_kiosk_confirmation':'有售賣窗口的小賣部','camera_preserved':True,'new_actors':[{'name':a.get_name(),'label':a.get_actor_label()} for a in dc_added]}
(dc_root/'dining_construction_scene.json').write_text(json.dumps(dc_report,ensure_ascii=False,indent=2),encoding='utf-8')
print('PHYSICAL_DINING_SAVED',len(dc_after))
