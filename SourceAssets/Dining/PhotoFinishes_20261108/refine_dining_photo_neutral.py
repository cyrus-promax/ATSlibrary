import unreal,pathlib,json
np_path='/Game/ATS/Dining/PhotoFinishes_20261108/Materials/M_Dining_OffWhitePaint_Matte';np_mat=unreal.load_asset(np_path);assert np_mat
np_n=unreal.MaterialEditingLibrary.get_material_property_input_node(np_mat,unreal.MaterialProperty.MP_BASE_COLOR)
assert isinstance(np_n,unreal.MaterialExpressionVectorParameter)
def np_linear(v):v=v/255.;return v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4
np_n.set_editor_property('default_value',unreal.LinearColor(*[np_linear(v) for v in (231,230,225)],1))
unreal.MaterialEditingLibrary.recompile_material(np_mat);assert unreal.EditorAssetLibrary.save_loaded_asset(np_mat)
np_report={'paint_srgb':[231,230,225],'reason':'Neutralized the yellow cast seen in the actual UE preview; photo-informed visual tuning, not measured site albedo.'}
pathlib.Path('D:/Cyrus/OneDrive/文件/香港仔工業學校/ATS/SourceAssets/Dining/PhotoFinishes_20261108/colour_refinement.json').write_text(json.dumps(np_report,indent=2),encoding='utf-8')
