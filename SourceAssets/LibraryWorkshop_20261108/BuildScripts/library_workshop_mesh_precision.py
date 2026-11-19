import unreal,pathlib,json
lw_out=pathlib.Path('D:/Cyrus/OneDrive/文件/香港仔工業學校/ATS/SourceAssets/LibraryWorkshop_20261108')
lw_data=json.loads((lw_out/'mesh_import_report.json').read_text(encoding='utf-8'))
lw_sme=unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
lw_checks=[]
for group,info in lw_data['groups'].items():
 for item in info['meshes']:
  mesh=unreal.EditorAssetLibrary.load_asset(item['asset']);settings=lw_sme.get_lod_build_settings(mesh,0)
  settings.set_editor_property('use_full_precision_u_vs',True);settings.set_editor_property('use_high_precision_tangent_basis',True)
  lw_sme.set_lod_build_settings(mesh,0,settings)
  check=lw_sme.get_lod_build_settings(mesh,0)
  assert check.get_editor_property('use_full_precision_u_vs') and check.get_editor_property('use_high_precision_tangent_basis')
  lw_checks.append({'mesh':mesh.get_path_name(),'full_precision_uv':True,'high_precision_tangents':True})
assert unreal.EditorAssetLibrary.save_directory('/Game/ATS/LibraryWorkshop_20261108/Meshes',only_if_is_dirty=True,recursive=True)
(lw_out/'mesh_precision_validation.json').write_text(json.dumps({'count':len(lw_checks),'meshes':lw_checks},indent=2),encoding='utf-8')
print('LW_PRECISION_COMPLETE',len(lw_checks))
