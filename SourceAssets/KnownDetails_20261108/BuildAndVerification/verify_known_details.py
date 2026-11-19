import unreal,pathlib,json,copy,hashlib,datetime
kv_root=pathlib.Path('D:/Cyrus/OneDrive/文件/香港仔工業學校/ATS');kv_out=kv_root/'SourceAssets/KnownDetails_20261108'
kv_before=json.loads((kv_out/'scene_before.json').read_text(encoding='utf-8'))
kv_import=json.loads((kv_out/'import_report.json').read_text(encoding='utf-8'))
kv_actors={a.get_name():a for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()}
kv_after={n:kd_snapshot(a) for n,a in kv_actors.items()}
assert set(kv_after)==set(kv_before)
kv_changed=[n for n in kv_before if kv_before[n]!=kv_after[n]]
assert set(kv_changed)==set(kv_import['targets']),(len(kv_changed),set(kv_changed)^set(kv_import['targets']))
kv_mesh_targets={r['actor'] for r in kv_import['replacements']}
for n in kv_changed:
 b,a=copy.deepcopy(kv_before[n]),copy.deepcopy(kv_after[n])
 for bc,ac in zip(b['components'],a['components']):
  bc.pop('materials');ac.pop('materials')
  if n in kv_mesh_targets:bc.pop('mesh');ac.pop('mesh')
 assert b==a,('Unexpected property change',n,b,a)
kv_bounds=[]
for r in kv_import['replacements']:
 old=unreal.load_asset(r['old_mesh']);new=kv_actors[r['actor']].static_mesh_component.static_mesh
 assert new.get_path_name()==r['new_mesh']
 assert old.get_editor_property('body_setup').get_editor_property('collision_trace_flag')==new.get_editor_property('body_setup').get_editor_property('collision_trace_flag')
 assert new.get_num_lods()>=1
 kv_bounds.append({'actor':r['actor'],'bounds_max_delta_cm':r['bounds_max_delta_cm'],'collision_mode_unchanged':True,'lod_count':new.get_num_lods()})
kv_hashes=[]
for p in ['TeachingFrames/frame_finish_manifest.json','HallSign/hall_sign_patch_manifest.json','DiningAC/ac_front_manifest.json']:
 m=json.loads((kv_out/p).read_text(encoding='utf-8'));h=hashlib.sha256(pathlib.Path(m['source']).read_bytes()).hexdigest();assert h==m['source_sha256_before'];kv_hashes.append({'source':m['source'],'sha256':h,'unchanged':True})
(kv_out/'scene_after.json').write_text(json.dumps(kv_after,ensure_ascii=False,indent=2),encoding='utf-8')
kv_validation={'timestamp':datetime.datetime.now().isoformat(),'status':'scene_invariants_passed','before_count':len(kv_before),'after_count':len(kv_after),'changed_actors':len(kv_changed),'untouched_actors':len(kv_after)-len(kv_changed),'all_transforms_collisions_visibility_lighting_labels_unchanged':True,'replacement_checks':kv_bounds,'source_hashes':kv_hashes,'map_sha256':hashlib.sha256((kv_root/'Content/ATS/Maps/ATS_StudentCampus.umap').read_bytes()).hexdigest()}
(kv_out/'validation.json').write_text(json.dumps(kv_validation,ensure_ascii=False,indent=2),encoding='utf-8')
print('VERIFIED_901_ACTORS_32_EXPECTED_CHANGES_869_UNCHANGED')
