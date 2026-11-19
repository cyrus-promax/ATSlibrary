import unreal,pathlib,json,datetime,shutil,re

dq_root=pathlib.Path('D:/Cyrus/OneDrive/文件/香港仔工業學校/ATS')
dq_work=pathlib.Path('C:/Users/Cyrus/Documents/Codex/2026-11-06/dao/work')
dq_ed=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
dq_sub=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
dq_level=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
assert not dq_ed.get_game_world(), 'Do not edit during play'
assert dq_ed.get_editor_world().get_name()=='ATS_StudentCampus'
dq_all=dq_sub.get_all_level_actors()
dq_tags={'ATS.DiningEnvelope.PhotoBasedPartial','ATS.Dining.PartialPhotoReconstruction'}
dq_targets=[a for a in dq_all if dq_tags.intersection(str(t) for t in a.tags)]
assert len(dq_targets)==30,len(dq_targets)
assert not any('ATS.ReferenceOnly.UnverifiedDining' in [str(t) for t in a.tags] for a in dq_targets), 'Already applied; inspect report instead of rerunning'

def dq_snapshot(a):
    d={'name':a.get_name(),'label':a.get_actor_label(),'class':a.get_class().get_name(),
       'transform':re.sub(r'0x[0-9A-Fa-f]+','ADDR',str(a.get_actor_transform())),
       'folder':str(a.get_folder_path()),'tags':[str(t) for t in a.tags],
       'editor_only':a.get_editor_property('is_editor_only_actor'),
       'hidden_in_game':a.get_editor_property('hidden'),
       'hidden_in_editor':a.is_temporarily_hidden_in_editor(),
       'actor_collision':a.get_actor_enable_collision()}
    components=[]
    for c in a.get_components_by_class(unreal.SceneComponent):
        row={'name':c.get_name(),'class':c.get_class().get_name(),'visible':c.get_editor_property('visible'),'hidden_in_game':c.get_editor_property('hidden_in_game')}
        if isinstance(c,unreal.PrimitiveComponent):
            row.update(collision=str(c.get_collision_enabled()),profile=str(c.get_collision_profile_name()))
        if isinstance(c,unreal.StaticMeshComponent):
            row.update(mesh=c.static_mesh.get_path_name() if c.static_mesh else None,materials=[m.get_path_name() if m else None for m in c.get_materials()])
        if isinstance(c,unreal.LightComponent):row['intensity']=c.get_editor_property('intensity')
        components.append(row)
    d['components']=components
    return d

dq_before={a.get_name():dq_snapshot(a) for a in dq_all}
dq_camera=dq_ed.get_level_viewport_camera_info()
dq_backup=dq_root/'Saved/Backups'/datetime.datetime.now().strftime('DiningEvidenceReview_%Y%m%d_%H%M%S')
dq_backup.mkdir(parents=True,exist_ok=False)
dq_map=dq_root/'Content/ATS/Maps/ATS_StudentCampus.umap'
shutil.copy2(dq_map,dq_backup/'ATS_StudentCampus_last_disk_save.umap')
assert dq_level.save_current_level()
shutil.copy2(dq_map,dq_backup/'ATS_StudentCampus_before_review.umap')
(dq_backup/'scene_before.json').write_text(json.dumps(dq_before,ensure_ascii=False,indent=2),encoding='utf-8')
for dq_rel in ['使用說明.txt','SourceAssets/Walkthrough/walkthrough_manifest.json','SourceAssets/Dining/dining_furniture_manifest.json','SourceAssets/Dining/dining_placement.json','SourceAssets/Dining/Envelope/dining_envelope_manifest.json','SourceAssets/Dining/Envelope/photo_evidence.json','SourceAssets/Dining/來源與核實範圍.txt','SourceAssets/Dining/Envelope/來源與核實範圍.txt']:
    dq_src=dq_root/dq_rel
    if dq_src.exists():
        dq_dest=dq_backup/dq_rel;dq_dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(dq_src,dq_dest)

for dq_a in dq_targets:
    dq_a.modify()
    dq_a.set_folder_path('References/Dining_Unverified_Excluded_From_Tour')
    dq_a.set_actor_label('待核實參考 | '+dq_a.get_actor_label())
    dq_a.tags=list(dq_a.tags)+[unreal.Name('ATS.ReferenceOnly.UnverifiedDining'),unreal.Name('ATS.ExcludeFromWalkthrough')]
    dq_a.set_editor_property('is_editor_only_actor',True)
    dq_a.set_actor_hidden_in_game(True)
    dq_a.set_actor_enable_collision(False)
    for dq_c in dq_a.get_components_by_class(unreal.SceneComponent):
        dq_c.modify();dq_c.set_visibility(False,True);dq_c.set_hidden_in_game(True,True)
        if isinstance(dq_c,unreal.PrimitiveComponent):dq_c.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
    dq_a.set_is_temporarily_hidden_in_editor(True)

dq_after={a.get_name():dq_snapshot(a) for a in dq_sub.get_all_level_actors()}
dq_names={a.get_name() for a in dq_targets}
assert dq_before.keys()==dq_after.keys()
for dq_name in dq_before:
    if dq_name not in dq_names:assert dq_before[dq_name]==dq_after[dq_name],dq_name
for dq_name in dq_names:
    dq_row=dq_after[dq_name]
    assert dq_row['editor_only'] and dq_row['hidden_in_game'] and dq_row['hidden_in_editor'] and not dq_row['actor_collision']
    assert dq_row['transform']==dq_before[dq_name]['transform']
    for dq_comp in dq_row['components']:
        assert not dq_comp['visible'] and dq_comp['hidden_in_game']
        if 'collision' in dq_comp:assert 'NO_COLLISION' in dq_comp['collision']
assert dq_level.save_current_level()
assert dq_ed.get_level_viewport_camera_info()==dq_camera
dq_report={'status':'saved_reference_only','reason':'Appearance is supported by photos; exact geometry placement, orientation and furniture arrangement are not verified. User requests no invented interiors.',
    'backup':str(dq_backup),'map':'/Game/ATS/Maps/ATS_StudentCampus','actors_total':len(dq_after),
    'other_actors_preserved':len(dq_after)-len(dq_names),'reference_only_actors':len(dq_names),
    'reference_folder':'References/Dining_Unverified_Excluded_From_Tour',
    'reference_only_mesh_actors':sum(isinstance(a,unreal.StaticMeshActor) for a in dq_targets),
    'reference_only_lights':sum(isinstance(a,unreal.Light) for a in dq_targets),
    'assets_deleted':0,'actors_deleted':0,'new_geometry_added':0,'new_door_connections':0,'full_layout_verified':False,
    'camera_preserved':True,'actor_states':{n:dq_after[n] for n in sorted(dq_names)}}
(dq_root/'dining_evidence_review_scene.json').write_text(json.dumps(dq_report,ensure_ascii=False,indent=2),encoding='utf-8')
print('DINING_REFERENCE_ONLY_SAVED',len(dq_names),dq_backup)
