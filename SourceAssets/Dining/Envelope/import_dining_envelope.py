import unreal,pathlib,json,math,shutil,datetime,re

di_root=pathlib.Path('D:/Cyrus/OneDrive/文件/香港仔工業學校/ATS')
di_work=pathlib.Path('C:/Users/Cyrus/Documents/Codex/2026-11-06/dao/work')
di_out=di_root/'SourceAssets/Dining/Envelope'
di_manifest=json.loads((di_out/'dining_envelope_manifest.json').read_text(encoding='utf-8'))
di_ed=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
di_sub=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
di_level=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
assert not di_ed.get_game_world()
assert di_ed.get_editor_world().get_name()=='ATS_StudentCampus'
assert not any('ATS.DiningEnvelope.PhotoBasedPartial' in [str(t) for t in a.tags] for a in di_sub.get_all_level_actors())
di_tools=unreal.AssetToolsHelpers.get_asset_tools();di_lib=unreal.EditorAssetLibrary;di_ml=unreal.MaterialEditingLibrary
di_stage='/Game/ATS/Dining/Envelope'
di_backup=di_root/'Saved/Backups'/datetime.datetime.now().strftime('DiningEnvelope_%Y%m%d_%H%M%S')
di_backup.mkdir(parents=True)
di_map=di_root/'Content/ATS/Maps/ATS_StudentCampus.umap'
shutil.copy2(di_map,di_backup/'ATS_StudentCampus_last_disk_save.umap')
def di_snapshot(a):
    row={'name':a.get_name(),'label':a.get_actor_label(),'class':a.get_class().get_name(),'transform':re.sub(r'0x[0-9A-Fa-f]+','ADDR',str(a.get_actor_transform()))}
    if isinstance(a,unreal.StaticMeshActor):
        c=a.static_mesh_component
        row.update(mesh=c.static_mesh.get_path_name() if c.static_mesh else None,materials=[m.get_path_name() if m else None for m in c.get_materials()],collision=str(c.get_collision_enabled()))
    return row
di_before={a.get_name():di_snapshot(a) for a in di_sub.get_all_level_actors()}
(di_backup/'scene_before.json').write_text(json.dumps(di_before,ensure_ascii=False,indent=2),encoding='utf-8')
assert di_level.save_current_level()
shutil.copy2(di_map,di_backup/'ATS_StudentCampus_before_envelope.umap')
for di_rel in ['使用說明.txt','SourceAssets/Walkthrough/walkthrough_manifest.json','SourceAssets/Dining/dining_furniture_manifest.json']:
    di_dest=di_backup/di_rel;di_dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(di_root/di_rel,di_dest)
di_loc,di_rot=di_ed.get_level_viewport_camera_info()
(di_work/'dining_envelope_preparation.json').write_text(json.dumps({'backup':str(di_backup),'actor_count':len(di_before),'camera_world':[di_loc.x,di_loc.y,di_loc.z],'rotation':{'pitch':di_rot.pitch,'yaw':di_rot.yaw,'roll':di_rot.roll}},ensure_ascii=False,indent=2),encoding='utf-8')

def di_const(mat,value,prop):
    n=di_ml.create_material_expression(mat,unreal.MaterialExpressionConstant,0,0);n.set_editor_property('r',value);di_ml.connect_material_property(n,'',prop)
di_mats={}
for di_name,di_spec in di_manifest['materials'].items():
    di_mname='M_DiningEnvelope_'+di_name
    di_mat=di_tools.create_asset(di_mname,di_stage+'/Materials',unreal.Material,unreal.MaterialFactoryNew())
    assert di_mat
    di_n=di_ml.create_material_expression(di_mat,unreal.MaterialExpressionConstant3Vector,0,0)
    di_n.set_editor_property('constant',unreal.LinearColor(*di_spec['colour_linear'],1))
    di_ml.connect_material_property(di_n,'',unreal.MaterialProperty.MP_BASE_COLOR)
    di_const(di_mat,di_spec['roughness'],unreal.MaterialProperty.MP_ROUGHNESS)
    di_const(di_mat,di_spec['metallic'],unreal.MaterialProperty.MP_METALLIC)
    if di_spec['emissive_strength']:
        di_mul=di_ml.create_material_expression(di_mat,unreal.MaterialExpressionMultiply,250,100)
        di_mul.set_editor_property('const_b',di_spec['emissive_strength'])
        di_ml.connect_material_expressions(di_n,'',di_mul,'A');di_ml.connect_material_property(di_mul,'',unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    di_ml.recompile_material(di_mat);di_mats[di_mname]=di_mat
di_opts=unreal.FbxImportUI();di_opts.import_mesh=True;di_opts.import_as_skeletal=False;di_opts.import_materials=False;di_opts.import_textures=False;di_opts.import_animations=False;di_opts.automated_import_should_detect_type=False;di_opts.mesh_type_to_import=unreal.FBXImportType.FBXIT_STATIC_MESH
di_data=di_opts.static_mesh_import_data;di_data.combine_meshes=False;di_data.auto_generate_collision=False;di_data.generate_lightmap_u_vs=False;di_data.transform_vertex_to_absolute=True;di_data.convert_scene_unit=True;di_data.normal_import_method=unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS
di_task=unreal.AssetImportTask();di_task.filename=str(di_out/'ATS_Dining_Envelope.fbx');di_task.destination_path=di_stage+'/Meshes';di_task.automated=True;di_task.replace_existing=False;di_task.save=False;di_task.options=di_opts;di_task.factory=unreal.FbxFactory()
di_tools.import_asset_tasks([di_task])
di_meshes=[o for o in di_task.get_objects() if isinstance(o,unreal.StaticMesh)]
assert len(di_meshes)==5,len(di_meshes)
di_added=[]
for di_mesh in di_meshes:
    di_key=re.search('SM_DiningEnvelope_.*',di_mesh.get_name()).group()
    di_item=next(x for x in di_manifest['meshes'] if x['name']==di_key)
    for di_i,di_slot in enumerate(di_mesh.get_editor_property('static_materials')):
        di_slot_name=str(di_slot.get_editor_property('imported_material_slot_name'));assert di_slot_name in di_mats
        di_mesh.set_material(di_i,di_mats[di_slot_name])
    di_body=di_mesh.get_editor_property('body_setup');di_body.set_editor_property('collision_trace_flag',unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
    di_a=di_sub.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector())
    di_a.set_actor_label('Dining Photo Detail | '+di_item['group'])
    di_a.set_folder_path('Campus/Dining Photo Details')
    di_a.tags=[unreal.Name(t) for t in ['ATS.DiningEnvelope.PhotoBasedPartial','ATS.Floor.G','ATS.CoverageEdges.NotRoomBoundaries','ATS.Dimensions.Estimated']]
    di_a.static_mesh_component.set_static_mesh(di_mesh)
    di_a.static_mesh_component.set_collision_profile_name('BlockAll' if di_item['collision'] else 'NoCollision')
    di_a.static_mesh_component.set_collision_enabled(unreal.CollisionEnabled.QUERY_AND_PHYSICS if di_item['collision'] else unreal.CollisionEnabled.NO_COLLISION)
    di_added.append({'name':di_a.get_name(),'label':di_a.get_actor_label(),'mesh':di_mesh.get_path_name()})
di_c,di_s=math.cos(math.radians(20)),math.sin(math.radians(20))
def di_point(u,v,h):return unreal.Vector((-8+di_c*u-di_s*v)*100,(24-di_s*u-di_c*v)*100,(-24.55+h)*100)
for di_i,di_light in enumerate(di_manifest['lights'],1):
    di_a=di_sub.spawn_actor_from_class(unreal.RectLight,di_point(*di_light['campus_m']),unreal.Rotator(pitch=-90,yaw=-20,roll=0))
    di_a.set_actor_label('Dining Photo Light %02d'%di_i);di_a.set_folder_path('Campus/Dining Photo Details')
    di_a.tags=[unreal.Name('ATS.DiningEnvelope.PhotoBasedPartial')]
    di_comp=di_a.get_component_by_class(unreal.RectLightComponent)
    di_comp.set_editor_property('intensity_units',unreal.LightUnits.LUMENS)
    di_comp.set_editor_property('intensity',di_light['lumens'])
    di_comp.set_editor_property('source_width',di_light['width_cm']);di_comp.set_editor_property('source_height',di_light['height_cm'])
    di_comp.set_editor_property('attenuation_radius',1250)
    di_comp.set_editor_property('use_temperature',True);di_comp.set_editor_property('temperature',di_light['temperature_k'])
    di_comp.set_mobility(unreal.ComponentMobility.MOVABLE)
    di_added.append({'name':di_a.get_name(),'label':di_a.get_actor_label(),'light':True})
assert di_lib.save_directory(di_stage,only_if_is_dirty=True,recursive=True)
assert di_level.save_current_level()
di_after={a.get_name():a for a in di_sub.get_all_level_actors()}
assert len(di_after)==len(di_before)+9
for di_name,di_row in di_before.items():assert di_snapshot(di_after[di_name])==di_row,di_name
di_report={'status':'partial_photo_details_saved','preserved_existing_actors':len(di_before),'actors_now':len(di_after),'added_actors':di_added,'backup':str(di_backup),'new_room_boundaries':0,'new_door_window_openings':0,'full_room_verified':False,'coverage_is_partial':True,'furniture_unchanged':True,'geometry_manifest':'SourceAssets/Dining/Envelope/dining_envelope_manifest.json'}
(di_root/'dining_envelope_build_report.json').write_text(json.dumps(di_report,ensure_ascii=False,indent=2),encoding='utf-8')
print('DINING_ENVELOPE_IMPORTED',di_report)
