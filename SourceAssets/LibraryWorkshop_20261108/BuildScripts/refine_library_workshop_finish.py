import unreal,pathlib,json
rf_path='/Game/ATS/LibraryWorkshop_20261108';rf_ml=unreal.MaterialEditingLibrary;rf_lib=unreal.EditorAssetLibrary
for key,strength in [('LW_Plaster',.08)]:
 m=rf_lib.load_asset(rf_path+'/Materials/M_'+key);sample=rf_ml.get_material_property_input_node(m,unreal.MaterialProperty.MP_AMBIENT_OCCLUSION)
 if not isinstance(sample,unreal.MaterialExpressionTextureSample):continue
 mul=rf_ml.create_material_expression(m,unreal.MaterialExpressionMultiply,300,600);mul.set_editor_property('const_b',strength);assert rf_ml.connect_material_expressions(sample,'R',mul,'A')
 add=rf_ml.create_material_expression(m,unreal.MaterialExpressionAdd,500,600);add.set_editor_property('const_b',1-strength);assert rf_ml.connect_material_expressions(mul,'',add,'A');assert rf_ml.connect_material_property(add,'',unreal.MaterialProperty.MP_AMBIENT_OCCLUSION);rf_ml.recompile_material(m)
for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors():
 if a.get_actor_label()=='LW_Daylight':a.light_component.set_editor_property('intensity',1500.0)
 if a.get_actor_label()=='LW_SkyFill':a.light_component.set_editor_property('intensity',.65)
rf_lib.save_directory(rf_path+'/Materials',only_if_is_dirty=True,recursive=True)
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
