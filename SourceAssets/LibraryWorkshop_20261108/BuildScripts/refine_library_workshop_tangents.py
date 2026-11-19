import unreal,pathlib,json
root=pathlib.Path('D:/Cyrus/OneDrive/文件/香港仔工業學校/ATS/SourceAssets/LibraryWorkshop_20261108');report=json.loads((root/'mesh_import_report.json').read_text(encoding='utf-8'))
target_names={'SM_LW_A_Step_PendantSuspension_BlackMetal','SM_LW_Culture_Shelving_DarkOak','SM_LW_Main_Reception_PaleOak','SM_LW_Main_Shelving_PaleOak'}
sme=unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem);fixed=[]
for group,info in report['groups'].items():
 for item in info['meshes']:
  if item['name'] not in target_names:continue
  mesh=unreal.EditorAssetLibrary.load_asset(item['asset']);s=sme.get_lod_build_settings(mesh,0)
  s.set_editor_property('use_mikk_t_space',False);s.set_editor_property('recompute_tangents',True);s.set_editor_property('recompute_normals',False);s.set_editor_property('use_full_precision_u_vs',True);s.set_editor_property('use_high_precision_tangent_basis',True)
  sme.set_lod_build_settings(mesh,0,s);unreal.EditorAssetLibrary.save_loaded_asset(mesh);fixed.append(item['name'])
assert len(fixed)==4
(root/'tangent_refinement.json').write_text(json.dumps({'meshes':fixed,'method':'Engine recomputed tangents for small bevel/curve geometry; full precision UV and normals retained.'},indent=2),encoding='utf-8')
