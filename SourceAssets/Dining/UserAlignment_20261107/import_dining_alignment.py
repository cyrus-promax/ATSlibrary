import unreal,pathlib,json,datetime,shutil,re,math
da_root=pathlib.Path('D:/Cyrus/OneDrive/文件/香港仔工業學校/ATS')
da_out=da_root/'SourceAssets/Dining/UserAlignment_20261107'
da_data=json.loads((da_out/'alignment.json').read_text(encoding='utf-8'))
da_manifest=json.loads((da_out/'overlay_manifest.json').read_text(encoding='utf-8'))
da_sub=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
da_ed=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
da_level=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
assert not da_ed.get_game_world() and da_ed.get_editor_world().get_name()=='ATS_StudentCampus'
da_all=da_sub.get_all_level_actors()
assert not any('ATS.DiningPlan.Aligned20261107' in [str(t) for t in a.tags] for a in da_all)
def da_snapshot(a):
    d={'name':a.get_name(),'label':a.get_actor_label(),'transform':re.sub(r'0x[0-9A-Fa-f]+','ADDR',str(a.get_actor_transform())),'tags':[str(t) for t in a.tags],'folder':str(a.get_folder_path()),'editor_only':a.get_editor_property('is_editor_only_actor'),'hidden':a.get_editor_property('hidden'),'editor_hidden':a.is_temporarily_hidden_in_editor(),'collision':a.get_actor_enable_collision()}
    if isinstance(a,unreal.StaticMeshActor):d.update(mesh=a.static_mesh_component.static_mesh.get_path_name() if a.static_mesh_component.static_mesh else None,component_visible=a.static_mesh_component.get_editor_property('visible'),component_collision=str(a.static_mesh_component.get_collision_enabled()))
    return d
da_before={a.get_name():da_snapshot(a) for a in da_all}
da_camera=da_ed.get_level_viewport_camera_info()
da_backup=da_root/'Saved/Backups'/datetime.datetime.now().strftime('DiningUserAlignment_%Y%m%d_%H%M%S');da_backup.mkdir(parents=True)
da_map=da_root/'Content/ATS/Maps/ATS_StudentCampus.umap'
shutil.copy2(da_map,da_backup/'ATS_StudentCampus_last_disk_save.umap');assert da_level.save_current_level();shutil.copy2(da_map,da_backup/'ATS_StudentCampus_before_alignment.umap')
(da_backup/'scene_before.json').write_text(json.dumps(da_before,ensure_ascii=False,indent=2),encoding='utf-8')
for da_rel in ['SourceAssets/Walkthrough/walkthrough_manifest.json','SourceAssets/References/user_ground_floor_approximate_evidence.json','使用說明.txt']:
    da_dest=da_backup/da_rel;da_dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(da_root/da_rel,da_dest)
da_tools=unreal.AssetToolsHelpers.get_asset_tools();da_ml=unreal.MaterialEditingLibrary;da_stage='/Game/ATS/Dining/PlanReference'
da_mats={}
for da_name,da_color in da_manifest['materials'].items():
    da_m=da_tools.create_asset('M_DiningPlan_'+da_name,da_stage+'/Materials',unreal.Material,unreal.MaterialFactoryNew())
    assert da_m
    da_m.set_editor_property('blend_mode',unreal.BlendMode.BLEND_TRANSLUCENT)
    da_m.set_editor_property('shading_model',unreal.MaterialShadingModel.MSM_UNLIT)
    da_m.set_editor_property('disable_depth_test',True)
    da_m.set_editor_property('two_sided',True)
    da_n=da_ml.create_material_expression(da_m,unreal.MaterialExpressionConstant3Vector,0,0);da_n.set_editor_property('constant',unreal.LinearColor(*da_color,1))
    da_inv=da_ml.create_material_expression(da_m,unreal.MaterialExpressionEyeAdaptationInverse,250,0)
    da_inputs=da_ml.get_material_expression_input_names(da_inv)
    da_one=da_ml.create_material_expression(da_m,unreal.MaterialExpressionConstant,0,200);da_one.set_editor_property('r',1)
    assert da_ml.connect_material_expressions(da_n,'',da_inv,str(da_inputs[0]))
    assert da_ml.connect_material_expressions(da_one,'',da_inv,str(da_inputs[1]))
    assert da_ml.connect_material_property(da_inv,'',unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    da_op=da_ml.create_material_expression(da_m,unreal.MaterialExpressionConstant,0,100);da_op.set_editor_property('r',1);da_ml.connect_material_property(da_op,'',unreal.MaterialProperty.MP_OPACITY)
    da_ml.recompile_material(da_m);da_mats['M_DiningPlan_'+da_name]=da_m
da_opts=unreal.FbxImportUI();da_opts.import_mesh=True;da_opts.import_as_skeletal=False;da_opts.import_materials=False;da_opts.import_textures=False;da_opts.import_animations=False;da_opts.automated_import_should_detect_type=False;da_opts.mesh_type_to_import=unreal.FBXImportType.FBXIT_STATIC_MESH
da_opts.static_mesh_import_data.combine_meshes=False;da_opts.static_mesh_import_data.auto_generate_collision=False;da_opts.static_mesh_import_data.transform_vertex_to_absolute=True;da_opts.static_mesh_import_data.convert_scene_unit=True
da_task=unreal.AssetImportTask();da_task.filename=str(da_out/'ATS_Dining_Plan_Reference.fbx');da_task.destination_path=da_stage+'/Meshes';da_task.automated=True;da_task.replace_existing=False;da_task.save=False;da_task.options=da_opts;da_task.factory=unreal.FbxFactory()
da_tools.import_asset_tasks([da_task]);da_meshes=[o for o in da_task.get_objects() if isinstance(o,unreal.StaticMesh)];assert len(da_meshes)==6
da_added=[]
def da_reference(a,label):
    a.set_actor_label(label);a.set_folder_path('References/Dining_Aligned_User_Plan')
    a.tags=[unreal.Name(t) for t in ['ATS.DiningPlan.Aligned20261107','ATS.ReferenceOnly','ATS.Floor.G','ATS.ExcludeFromWalkthrough']]
    a.set_editor_property('is_editor_only_actor',True);a.set_actor_hidden_in_game(True);a.set_actor_enable_collision(False)
    da_added.append(a)
for da_mesh in da_meshes:
    for da_i,da_slot in enumerate(da_mesh.get_editor_property('static_materials')):
        da_mname=str(da_slot.get_editor_property('imported_material_slot_name'));da_mesh.set_material(da_i,da_mats[da_mname])
    da_a=da_sub.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector())
    da_group=da_mesh.get_name().split('SM_DiningPlan_')[-1]
    da_reference(da_a,'G 層餐廳平面投影｜'+da_group)
    da_comp=da_a.static_mesh_component;da_comp.set_static_mesh(da_mesh);da_comp.set_collision_profile_name('NoCollision');da_comp.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION);da_comp.set_editor_property('cast_shadow',False)
    da_comp.set_editor_property('translucency_sort_priority',10 if da_group=='Text' else (9 if da_group=='Plate' else 8))
da_c,da_s=math.cos(math.radians(20)),math.sin(math.radians(20))
def da_point(p):
    u,v,h=p;return unreal.Vector((-8+da_c*u-da_s*v)*100,(24-da_s*u-da_c*v)*100,(-24.55+h)*100)
da_markers=[]
for da_f in da_data['features']:
    da_a=da_sub.spawn_actor_from_class(unreal.TargetPoint,da_point(da_f['approx_center_campus']))
    da_reference(da_a,'G 層定位｜'+da_f['label']+'｜依新圖對位，尺寸待核實')
    da_a.tags=list(da_a.tags)+[unreal.Name('ATS.DiningPlan.Feature.'+da_f['id'])]
    if da_f['id']=='outdoor':da_a.tags=list(da_a.tags)+[unreal.Name('ATS.OutdoorSeatingReference')]
    da_a.set_is_temporarily_hidden_in_editor(True)
    da_markers.append({'feature':da_f['id'],'actor':da_a.get_name(),'campus_m':da_f['approx_center_campus']})
da_superseded=[]
for da_a in da_all:
    if 'ATS.OutdoorSeatingReference' in [str(t) for t in da_a.tags]:
        da_a.modify();da_a.tags=[t for t in da_a.tags if str(t)!='ATS.OutdoorSeatingReference']+[unreal.Name('ATS.OutdoorSeatingReference.SupersededByUserPlan')]
        da_a.set_actor_label('歷史點位｜靠街長廊桌椅區｜已被新餐廳圖取代');da_a.set_is_temporarily_hidden_in_editor(True);da_superseded.append(da_a.get_name())
assert len(da_superseded)==1
assert unreal.EditorAssetLibrary.save_directory(da_stage,only_if_is_dirty=True,recursive=True)
assert da_level.save_current_level()
da_after={a.get_name():a for a in da_sub.get_all_level_actors()}
for da_n,da_state in da_before.items():
    if da_n not in da_superseded:assert da_snapshot(da_after[da_n])==da_state,da_n
assert len(da_after)==len(da_before)+14
assert da_ed.get_level_viewport_camera_info()==da_camera
da_report={'status':'aligned_reference_saved','backup':str(da_backup),'actors_before':len(da_before),'actors_after':len(da_after),'unchanged_existing_actors':len(da_before)-1,'historical_marker_superseded':da_superseded,'added_reference_meshes':6,'added_ground_markers':da_markers,'all_new_actors_editor_only':all(a.get_editor_property('is_editor_only_actor') for a in da_added),'all_new_actors_hidden_in_game':all(a.get_editor_property('hidden') for a in da_added),'all_new_actors_no_collision':all(not a.get_actor_enable_collision() for a in da_added),'physical_room_geometry_added':0,'actual_door_connections_added':0,'unverified_furniture_restored':False,'camera_preserved':True}
(da_root/'dining_user_alignment_scene.json').write_text(json.dumps(da_report,ensure_ascii=False,indent=2),encoding='utf-8')
unreal.EditorLevelLibrary.editor_set_game_view(False)
