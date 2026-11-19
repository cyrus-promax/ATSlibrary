import unreal,pathlib,json,math,hashlib,datetime
lw_root=pathlib.Path('D:/Cyrus/OneDrive/文件/香港仔工業學校/ATS');lw_out=lw_root/'SourceAssets/LibraryWorkshop_20261108';lw_stage='/Game/ATS/LibraryWorkshop_20261108';lw_map='/Game/ATS/Maps/ATS_Library_Workshop'
lw_ed=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem);lw_sub=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);lw_level=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);lw_lib=unreal.EditorAssetLibrary
assert not lw_ed.get_game_world()
lw_original=json.loads((lw_out/'school_state_before.json').read_text(encoding='utf-8'))
assert hashlib.sha256((lw_root/'Content/ATS/Maps/ATS_StudentCampus.umap').read_bytes()).hexdigest()==lw_original['map_sha256']
if lw_ed.get_editor_world().get_name()=='ATS_StudentCampus':
 assert {a.get_name():kd_snapshot(a) for a in lw_sub.get_all_level_actors()}==json.loads((lw_out/'school_scene_before.json').read_text(encoding='utf-8'))
 assert not unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()
lw_mr=json.loads((lw_out/'materials_import_report.json').read_text(encoding='utf-8'))
lw_mats={k:lw_lib.load_asset(v) for k,v in lw_mr['materials'].items()};assert all(lw_mats.values())
lw_meshdata=json.loads((lw_out/'mesh_import_report.json').read_text(encoding='utf-8'))
lw_arch=json.loads((lw_out/'architecture_manifest.json').read_text(encoding='utf-8'))
lw_furn=json.loads((lw_out/'furniture_manifest.json').read_text(encoding='utf-8'))
lw_doorspec=json.loads((lw_out/'door_assembly_manifest.json').read_text(encoding='utf-8'))['doors']
lw_meshes={};lw_items={}
for group,info in lw_meshdata['groups'].items():
 assert hashlib.sha256(pathlib.Path(info['fbx']).read_bytes()).hexdigest()==info['sha256'],group+' changed after import'
 for item in info['meshes']:
  mesh=lw_lib.load_asset(item['asset']);assert isinstance(mesh,unreal.StaticMesh)
  for i,key in enumerate(item['material_slots']):mesh.set_material(i,lw_mats[key])
  lw_meshes[item['name']]=mesh;lw_items[item['name']]=item
assert len(lw_meshes)==len(lw_arch['meshes'])+len(lw_furn['meshes'])
if lw_lib.does_asset_exist(lw_map):
 assert (lw_out/'scene_build_started.json').exists(),'Existing unrelated map must not be replaced'
 if lw_ed.get_editor_world().get_name()!='ATS_Library_Workshop':assert lw_level.load_level(lw_map)
 for actor in list(lw_sub.get_all_level_actors()):
  if 'ATS.LibraryWorkshop' in [str(t) for t in actor.tags]:assert lw_sub.destroy_actor(actor)
else:assert lw_level.new_level(lw_map)
(lw_out/'scene_build_started.json').write_text(json.dumps({'timestamp':datetime.datetime.now().isoformat(),'map':lw_map}),encoding='utf-8')
lw_added=[];lw_instances={};lw_roots={};lw_dooractors=[]
def lw_p(p):return unreal.Vector(p[0]*100,-p[1]*100,p[2]*100)
def lw_mark(actor,label,module='Display'):
 actor.set_actor_label(label);actor.set_folder_path('LibraryWorkshop/'+module);actor.tags=[unreal.Name('ATS.LibraryWorkshop'),unreal.Name('ATS.LibraryWorkshop.'+module)];lw_added.append(actor);return actor
def lw_attach(actor,parent):
 assert actor.attach_to_actor(parent,unreal.Name('None'),unreal.AttachmentRule.KEEP_WORLD,unreal.AttachmentRule.KEEP_WORLD,unreal.AttachmentRule.KEEP_WORLD,False)
def lw_rootactor(label,point,module):
 actor=lw_mark(lw_sub.spawn_actor_from_class(unreal.TargetPoint,lw_p(point)),label,module);actor.get_editor_property('root_component').set_mobility(unreal.ComponentMobility.STATIC);return actor
lw_master=lw_rootactor('LW_ALL | 圖書館獨立製作區',(0,0,0),'Display')
for module,spec in lw_arch['modules'].items():
 root=lw_rootactor('LW_ROOT_'+module,spec['origin'],module);lw_attach(root,lw_master);lw_roots[module]=root
lw_doorwood={d['wood_mesh'] for d in lw_doorspec}
for name,mesh in lw_meshes.items():
 if name in lw_doorwood:continue
 item=lw_items[name];a=lw_mark(lw_sub.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector()),name,item['module']);c=a.static_mesh_component;c.set_static_mesh(mesh)
 c.set_collision_profile_name('BlockAll' if item['collision'] else 'NoCollision');c.set_collision_enabled(unreal.CollisionEnabled.QUERY_AND_PHYSICS if item['collision'] else unreal.CollisionEnabled.NO_COLLISION)
 if item['material_slots'][0] in ['LW_Glass','LW_Light']:c.set_editor_property('cast_shadow',False)
 lw_attach(a,lw_roots[item['module']]);lw_instances[name]=a

lw_doorclass=unreal.load_class(None,'/Script/ATS.ATSAutoDoor')
for spec in lw_doorspec:
 p=lw_p(spec['hinge_m']);v=spec['leaf_direction_vector'];yaw=math.degrees(math.atan2(-v[1],v[0]));r=math.radians(yaw);c,s=math.cos(r),math.sin(r)
 a=lw_mark(lw_sub.spawn_actor_from_class(lw_doorclass,p,unreal.Rotator(pitch=0,yaw=yaw,roll=0)),'LW_DOOR_'+spec['id'],spec['module']);leaf=a.get_editor_property('leaf');leaf.set_static_mesh(lw_meshes[spec['wood_mesh']]);leaf.set_relative_location(unreal.Vector(-c*p.x-s*p.y,s*p.x-c*p.y,-p.z),False,False);leaf.set_relative_rotation(unreal.Rotator(pitch=0,yaw=-yaw,roll=0),False,False)
 a.set_editor_property('approach_distance',170.0);a.set_editor_property('open_angle',float(spec['suggested_open_angle_ue_degrees']));a.set_editor_property('close_delay',2.0);lw_attach(a,lw_roots[spec['module']]);hinge=a.get_editor_property('hinge')
 for name in spec['moving_leaf_parts']:
  part=lw_instances[name];part.static_mesh_component.set_mobility(unreal.ComponentMobility.MOVABLE);part.static_mesh_component.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
  assert part.attach_to_component(hinge,unreal.Name('None'),unreal.AttachmentRule.KEEP_WORLD,unreal.AttachmentRule.KEEP_WORLD,unreal.AttachmentRule.KEEP_WORLD,False)
 lw_dooractors.append({'actor':a.get_name(),'label':a.get_actor_label(),'source':spec['id'],'hinge_world_cm':[p.x,p.y,p.z],'yaw':yaw,'open_angle':spec['suggested_open_angle_ue_degrees']})

# Neutral support deck belongs only to the workshop, never to the reconstructed school.
lw_ground=lw_mark(lw_sub.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(1450,-1100,-22)),'LW_Display_SupportDeck')
lw_ground.static_mesh_component.set_static_mesh(lw_lib.load_asset('/Engine/BasicShapes/Cube'));lw_ground.static_mesh_component.set_material(0,lw_mats['LW_DisplayBase']);lw_ground.set_actor_scale3d(unreal.Vector(42,34,.20));lw_ground.static_mesh_component.set_collision_profile_name('BlockAll')
lw_attach(lw_ground,lw_master)
lw_lightrecords=[]
for module,centres in {'Main':[(2.8,2.2),(2.8,5.9),(7.1,2.2),(7.1,5.9),(11.5,2.2),(11.5,5.9)],'Step':[(22.0,1.8),(25.2,1.8),(27.3,4.0)],'Lecture':[(2.1,18.5),(5.2,19.2)],'Culture':[(21.9,18.4),(24.3,18.4)]}.items():
 for i,(x,y) in enumerate(centres):
  a=lw_mark(lw_sub.spawn_actor_from_class(unreal.RectLight,lw_p((x,y,3.15)),unreal.Rotator(pitch=-90,yaw=0,roll=0)),f'LW_{module}_SoftLight_{i+1}',module);light=a.get_component_by_class(unreal.RectLightComponent)
  for k,v in [('intensity_units',unreal.LightUnits.LUMENS),('intensity',3200.0 if module!='Culture' else 2300.0),('source_width',140.0),('source_height',100.0),('attenuation_radius',850.0),('use_temperature',True),('temperature',4800.0),('cast_shadows',True)]:light.set_editor_property(k,v)
  light.set_mobility(unreal.ComponentMobility.MOVABLE);lw_attach(a,lw_roots[module]);lw_lightrecords.append(a.get_name())
lw_sun=lw_mark(lw_sub.spawn_actor_from_class(unreal.DirectionalLight,unreal.Vector(0,0,3000),unreal.Rotator(pitch=-45,yaw=-38,roll=0)),'LW_Daylight')
lw_sun.light_component.set_editor_property('intensity',18000.0);lw_sun.light_component.set_editor_property('atmosphere_sun_light',True);lw_sun.light_component.set_editor_property('light_source_angle',1.8);lw_sun.light_component.set_mobility(unreal.ComponentMobility.MOVABLE)
lw_mark(lw_sub.spawn_actor_from_class(unreal.SkyAtmosphere,unreal.Vector(0,0,-3000)),'LW_SkyAtmosphere')
lw_sky=lw_mark(lw_sub.spawn_actor_from_class(unreal.SkyLight,unreal.Vector(0,0,500)),'LW_SkyFill');lw_sky.light_component.set_editor_property('real_time_capture',True);lw_sky.light_component.set_editor_property('intensity',.8);lw_sky.light_component.set_mobility(unreal.ComponentMobility.MOVABLE)
lw_pp=lw_mark(lw_sub.spawn_actor_from_class(unreal.PostProcessVolume,unreal.Vector()),'LW_InteriorExposure');lw_pp.set_editor_property('unbound',True);lw_settings=lw_pp.get_editor_property('settings')
for k,v in [('override_auto_exposure_method',True),('auto_exposure_method',unreal.AutoExposureMethod.AEM_HISTOGRAM),('override_auto_exposure_min_brightness',True),('auto_exposure_min_brightness',6.3),('override_auto_exposure_max_brightness',True),('auto_exposure_max_brightness',6.3),('override_auto_exposure_bias',True),('auto_exposure_bias',0.0),('override_bloom_intensity',True),('bloom_intensity',.15)]:lw_settings.set_editor_property(k,v)
lw_pp.set_editor_property('settings',lw_settings)
lw_start=lw_mark(lw_sub.spawn_actor_from_class(unreal.PlayerStart,lw_p((.9,5.65,.96)),unreal.Rotator(pitch=0,yaw=0,roll=0)),'LW_WalkStart','Main')
lw_ed.get_editor_world().get_world_settings().set_editor_property('default_game_mode',unreal.load_class(None,'/Script/ATS.ATSTourGameMode'))
lw_views={'Main':((.7,4.0,1.65),(12.8,4.0,1.60)),'Step':((20.7,.9,1.65),(26.0,4.4,1.45)),'Lecture':((2.6,18.8,1.65),(7.7,19.0,1.45)),'Culture':((20.2,16.2,1.65),(24.4,20.0,1.45))}
for module,(pos,target) in lw_views.items():
 a=lw_mark(lw_sub.spawn_actor_from_class(unreal.CameraActor,lw_p(pos),unreal.MathLibrary.find_look_at_rotation(lw_p(pos),lw_p(target))),'LW_View_'+module,module);a.camera_component.set_editor_property('field_of_view',82.0);lw_attach(a,lw_roots[module])
lw_ed.set_level_viewport_camera_info(lw_p(lw_views['Main'][0]),unreal.MathLibrary.find_look_at_rotation(lw_p(lw_views['Main'][0]),lw_p(lw_views['Main'][1])));lw_sub.set_selected_level_actors([])
assert lw_lib.save_directory(lw_stage,only_if_is_dirty=True,recursive=True);assert lw_level.save_current_level()
lw_report={'timestamp':datetime.datetime.now().isoformat(),'map':lw_map,'status':'built_saved','mesh_count':len(lw_meshes),'actor_count':len(lw_sub.get_all_level_actors()),'module_roots':{k:v.get_name() for k,v in lw_roots.items()},'master_root':lw_master.get_name(),'doors':lw_dooractors,'rect_lights':len(lw_lightrecords),'views':lw_views,'textures_4k':lw_mr['texture_count'],'furniture_counts':lw_furn['counts'],'source_polygons_architecture':lw_arch['summary']['polygons'],'source_triangles_furniture':lw_furn['total_triangles'],'main_school_sha256_unchanged':hashlib.sha256((lw_root/'Content/ATS/Maps/ATS_StudentCampus.umap').read_bytes()).hexdigest()==lw_original['map_sha256'],'limits':['Display dimensions and arrangement remain provisional. No complete as-built plan claimed.','Four modules can move independently; no school connection or original campus placement changed.','Book titles are unlabelled generic detail; counts are not a real library inventory.','Door closer bodies/arms are visual detail; articulated closer linkage is not simulated.']}
(lw_out/'scene_build_report.json').write_text(json.dumps(lw_report,ensure_ascii=False,indent=2),encoding='utf-8')
print('LIBRARY_WORKSHOP_BUILT',len(lw_meshes),lw_report['actor_count'])
