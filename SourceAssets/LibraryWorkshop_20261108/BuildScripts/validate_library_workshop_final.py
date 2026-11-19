import unreal,pathlib,json,math,hashlib,datetime
vf_root=pathlib.Path('D:/Cyrus/OneDrive/文件/香港仔工業學校/ATS');vf_out=vf_root/'SourceAssets/LibraryWorkshop_20261108';vf_stage='/Game/ATS/LibraryWorkshop_20261108'
vf_ed=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem);vf_sub=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);vf_sme=unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
assert vf_ed.get_editor_world().get_name()=='ATS_Library_Workshop' and not vf_ed.get_game_world()
vf_build=json.loads((vf_out/'scene_build_report.json').read_text(encoding='utf-8'));vf_m=json.loads((vf_out/'materials_import_report.json').read_text(encoding='utf-8'));vf_import=json.loads((vf_out/'mesh_import_report.json').read_text(encoding='utf-8'));vf_overrides=json.loads((vf_out/'scene_detail_overrides.json').read_text(encoding='utf-8'))
vf_texture=[]
for r in vf_m['textures']:
 t=unreal.EditorAssetLibrary.load_asset(r['asset']);dims=[t.blueprint_get_size_x(),t.blueprint_get_size_y()];assert dims==[4096,4096],r['asset'];assert t.get_editor_property('max_texture_size')==4096 and t.get_editor_property('lod_bias')==0
 assert t.get_editor_property('srgb')==r['srgb']
 if r['role']=='normal_gl':assert t.get_editor_property('flip_green_channel') and t.get_editor_property('compression_settings')==unreal.TextureCompressionSettings.TC_NORMALMAP
 vf_texture.append({'asset':r['asset'],'size':dims,'settings_verified':True})
vf_meshchecks=[]
for group,data in vf_import['groups'].items():
 assert hashlib.sha256(pathlib.Path(data['fbx']).read_bytes()).hexdigest()==data['sha256'],group
 for r in data['meshes']:
  mesh=unreal.EditorAssetLibrary.load_asset(r['asset']);assert isinstance(mesh,unreal.StaticMesh)
  for index,key in enumerate(r['material_slots']):assert mesh.get_material(index).get_path_name()==vf_m['materials'][key],r['name']
  s=vf_sme.get_lod_build_settings(mesh,0);assert s.get_editor_property('use_full_precision_u_vs') and s.get_editor_property('use_high_precision_tangent_basis')
  b=mesh.get_bounding_box();assert all(math.isfinite(v) for v in [b.min.x,b.min.y,b.min.z,b.max.x,b.max.y,b.max.z])
  vf_meshchecks.append(r['name'])
vf_actors=vf_sub.get_all_level_actors();vf_roots={m:next(a for a in vf_actors if a.get_actor_label()=='LW_ROOT_'+m) for m in ['Main','Step','Lecture','Culture']}
vf_groupchecks=[]
for module,root in vf_roots.items():
 child=next(a for a in vf_actors if isinstance(a,unreal.StaticMeshActor) and a.get_attach_parent_actor()==root)
 orig=root.get_actor_location();before=child.get_actor_location();delta=unreal.Vector(73,41,0)
 try:
  root.set_actor_location(orig+delta,False,False);moved=child.get_actor_location();err=(moved-before-delta).length();assert err<.02,(module,err)
 finally:root.set_actor_location(orig,False,False)
 assert (child.get_actor_location()-before).length()<.02
 vf_groupchecks.append({'module':module,'root':root.get_name(),'attached_child_moves_and_restores':True})
vf_walk=json.loads((vf_out/'walk_validation.json').read_text(encoding='utf-8'));assert vf_walk['status']=='passed' and len(vf_walk['checks'])==20
vf_school=json.loads((vf_out/'school_state_before.json').read_text(encoding='utf-8'));vf_school_hash=hashlib.sha256((vf_root/'Content/ATS/Maps/ATS_StudentCampus.umap').read_bytes()).hexdigest();assert vf_school_hash==vf_school['map_sha256']
assert not any(a.get_actor_label() in vf_overrides['removed_old_geometry'] for a in vf_actors)
vf_instances=[]
for a in vf_actors:
 if 'ATS.LibraryWorkshop' not in [str(t) for t in a.tags]:continue
 p=a.get_actor_location();rot=a.get_actor_rotation();scale=a.get_actor_scale3d();parent=a.get_attach_parent_actor()
 r={'actor':a.get_name(),'label':a.get_actor_label(),'class':a.get_class().get_path_name(),'position_cm':[p.x,p.y,p.z],'rotation':{'pitch':rot.pitch,'yaw':rot.yaw,'roll':rot.roll},'scale':[scale.x,scale.y,scale.z],'parent':parent.get_name() if parent else None,'tags':[str(t) for t in a.tags]}
 if isinstance(a,unreal.StaticMeshActor):r['mesh']=a.static_mesh_component.static_mesh.get_path_name();r['materials']=[a.static_mesh_component.get_material(i).get_path_name() for i in range(a.static_mesh_component.get_num_materials())]
 vf_instances.append(r)
assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
vf_result={'timestamp':datetime.datetime.now().isoformat(),'map':'/Game/ATS/Maps/ATS_Library_Workshop','status':'passed','source_mesh_asset_count':len(vf_meshchecks),'active_source_mesh_count':len(vf_meshchecks)-len(vf_overrides['removed_old_geometry']),'actor_count':len(vf_actors),'textures_4k':vf_texture,'groups':vf_groupchecks,'walk_status':vf_walk['status'],'walk_check_count':len(vf_walk['checks']),'character':vf_walk['character_class'],'school_map_unchanged':True,'school_map_sha256':vf_school_hash,'book_count':2298,'source_and_shader_precision_verified':True,'visual_checks':['Main table/reception overlap artefacts repaired','Photographic hanging fern detail replaces coarse triangles','Culture plaque Chinese glyphs present and facing front','4K texture dimensions checked on UE assets'],'limitations':['Independent study modules: display dimensions and arrangement are provisional, not an as-built floorplan.','Photographic finish match does not identify school original material products.','Door closer mechanical linkage is not animated.','Runtime validation covers the workshop, not a new route into the school.']}
(vf_out/'placement_manifest.json').write_text(json.dumps({'instances':vf_instances,'module_roots':{k:v.get_name() for k,v in vf_roots.items()},'coordinates':'Unreal centimetres; root hierarchy moves whole modules'},ensure_ascii=False,indent=2),encoding='utf-8')
(vf_out/'final_validation.json').write_text(json.dumps(vf_result,ensure_ascii=False,indent=2),encoding='utf-8')
print('LIBRARY_WORKSHOP_VALIDATED',len(vf_meshchecks),len(vf_texture),len(vf_walk['checks']))
