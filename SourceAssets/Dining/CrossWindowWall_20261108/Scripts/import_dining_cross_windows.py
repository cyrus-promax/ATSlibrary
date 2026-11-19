import unreal,pathlib,json
cx_root=pathlib.Path('D:/Cyrus/OneDrive/文件/香港仔工業學校/ATS');cx_out=cx_root/'SourceAssets/Dining/CrossWindowWall_20261108'
cx_ed=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem);cx_sub=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
assert not cx_ed.get_game_world() and cx_ed.get_editor_world().get_name()=='ATS_StudentCampus'
cx_path='/Game/ATS/Dining/CrossWindowWall_20261108';assert not unreal.EditorAssetLibrary.does_directory_exist(cx_path+'/Meshes'),'Inspect partial import before retry.'
cx_actors={a.get_name():a for a in cx_sub.get_all_level_actors()}
cx_targets={'Shell':cx_actors['StaticMeshActor_51'],'Walls':cx_actors['StaticMeshActor_620'],'Tiles':cx_actors['StaticMeshActor_619']}
assert len(cx_actors)==896
cx_effective={k:list(a.static_mesh_component.get_materials()) for k,a in cx_targets.items()}
cx_mats={m.get_name():m for m in cx_effective['Tiles']}
for cx_n in ['M_DiningBuild_Frame','M_DiningBuild_Glass','M_DiningBuild_Black']:
 cx_mats[cx_n]=unreal.load_asset('/Game/ATS/Dining/BuiltFromUserPlan/Materials/'+cx_n)
cx_mats['M_Dining_OffWhitePaint_Matte']=unreal.load_asset('/Game/ATS/Dining/PhotoFinishes_20261108/Materials/M_Dining_OffWhitePaint_Matte')
assert all(cx_mats.values())
cx_wood=unreal.AssetToolsHelpers.get_asset_tools().create_asset('M_DiningCross_DarkWood',cx_path+'/Materials',unreal.Material,unreal.MaterialFactoryNew());assert cx_wood
cx_color=unreal.MaterialEditingLibrary.create_material_expression(cx_wood,unreal.MaterialExpressionConstant3Vector,-220,0);cx_color.set_editor_property('constant',unreal.LinearColor(.032,.015,.008,1))
unreal.MaterialEditingLibrary.connect_material_property(cx_color,'',unreal.MaterialProperty.MP_BASE_COLOR)
cx_rough=unreal.MaterialEditingLibrary.create_material_expression(cx_wood,unreal.MaterialExpressionConstant,-220,150);cx_rough.set_editor_property('r',.64)
unreal.MaterialEditingLibrary.connect_material_property(cx_rough,'',unreal.MaterialProperty.MP_ROUGHNESS);unreal.MaterialEditingLibrary.recompile_material(cx_wood)
cx_mats['M_DiningCross_DarkWood']=cx_wood
cx_opts=unreal.FbxImportUI();cx_opts.import_mesh=True;cx_opts.import_as_skeletal=False;cx_opts.import_materials=False;cx_opts.import_textures=False;cx_opts.import_animations=False;cx_opts.automated_import_should_detect_type=False;cx_opts.mesh_type_to_import=unreal.FBXImportType.FBXIT_STATIC_MESH
cx_data=cx_opts.static_mesh_import_data;cx_data.combine_meshes=False;cx_data.auto_generate_collision=False;cx_data.transform_vertex_to_absolute=True;cx_data.convert_scene_unit=True;cx_data.generate_lightmap_u_vs=False;cx_data.normal_import_method=unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS
cx_task=unreal.AssetImportTask();cx_task.filename=str(cx_out/'ATS_Dining_CrossWindows.fbx');cx_task.destination_path=cx_path+'/Meshes';cx_task.automated=True;cx_task.replace_existing=False;cx_task.save=False;cx_task.options=cx_opts;cx_task.factory=unreal.FbxFactory()
unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([cx_task]);cx_meshes={o.get_name().split('SM_DiningCross_')[-1]:o for o in cx_task.get_objects() if isinstance(o,unreal.StaticMesh)}
assert set(cx_meshes)=={'Shell','Walls','Tiles','Frames','Glass','Aircon','Cross'},list(cx_meshes)
cx_changes=[];cx_added=[]
for cx_role,cx_mesh in cx_meshes.items():
 cx_slots=cx_mesh.get_editor_property('static_materials')
 cx_assigned=[]
 for cx_i,cx_slot in enumerate(cx_slots):
  cx_n=str(cx_slot.get_editor_property('imported_material_slot_name'))
  cx_mat=cx_effective[cx_role][0] if cx_role in ['Shell','Walls'] else cx_mats[cx_n]
  cx_mesh.set_material(cx_i,cx_mat);cx_assigned.append(cx_mat)
 if cx_role!='Tiles':cx_mesh.get_editor_property('body_setup').set_editor_property('collision_trace_flag',unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
 if cx_role in cx_targets:
  cx_a=cx_targets[cx_role];cx_a.modify();cx_comp=cx_a.static_mesh_component
  cx_changes.append({'actor':cx_a.get_name(),'role':cx_role,'before':cx_comp.static_mesh.get_path_name(),'after':cx_mesh.get_path_name()})
 else:
  cx_a=cx_sub.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector());cx_a.set_actor_label('餐廳十字架窗牆｜'+cx_role);cx_a.set_folder_path('Campus/Dining/CrossWall');cx_a.tags=[unreal.Name('ATS.Dining.CrossWindowWall'),unreal.Name('ATS.Floor.G')];cx_comp=cx_a.static_mesh_component
  cx_added.append({'actor':cx_a.get_name(),'role':cx_role,'mesh':cx_mesh.get_path_name()})
 cx_comp.set_static_mesh(cx_mesh)
 # Reassign by imported slot name: Tiles order differs from the previous mesh.
 cx_comp.set_editor_property('override_materials',[])
 for cx_i,cx_mat in enumerate(cx_assigned):cx_comp.set_material(cx_i,cx_mat)
 if cx_role=='Tiles':
  cx_comp.set_collision_profile_name('NoCollision');cx_comp.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION);cx_comp.set_editor_property('cast_shadow',False)
 else:
  cx_comp.set_collision_profile_name('BlockAll');cx_comp.set_collision_enabled(unreal.CollisionEnabled.QUERY_AND_PHYSICS)
 if cx_role=='Glass':cx_comp.set_editor_property('cast_shadow',False)
assert unreal.EditorAssetLibrary.save_directory(cx_path,only_if_is_dirty=True,recursive=True)
assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
(cx_out/'import_result.json').write_text(json.dumps({'status':'saved_pending_validation','changes':cx_changes,'added':cx_added,'material_slots_remapped_by_name':True,'actor_count':len(cx_sub.get_all_level_actors())},ensure_ascii=False,indent=2),encoding='utf-8')
print('CROSS_WINDOWS_IMPORTED',cx_changes,cx_added)
