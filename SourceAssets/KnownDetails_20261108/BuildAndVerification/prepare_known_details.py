import unreal,pathlib,json,re,datetime,shutil,hashlib,math
kd_root=pathlib.Path('D:/Cyrus/OneDrive/文件/香港仔工業學校/ATS')
kd_work=pathlib.Path('C:/Users/Cyrus/Documents/Codex/2026-11-06/dao/work')
kd_out=kd_root/'SourceAssets/KnownDetails_20261108';kd_out.mkdir(parents=True,exist_ok=True)
assert not (kd_out/'preparation.json').exists(),'Existing preparation must be inspected before retry.'
kd_ed=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem);kd_sub=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);kd_level=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
assert not kd_ed.get_game_world() and kd_ed.get_editor_world().get_name()=='ATS_StudentCampus'
def kd_clean(v):
 if isinstance(v,str):return re.sub(r'0x[0-9A-Fa-f]+','ADDR',v)
 if isinstance(v,list):return [kd_clean(x) for x in v]
 if isinstance(v,dict):return {k:kd_clean(x) for k,x in v.items()}
 return v
def kd_snapshot(a):
 d={'name':a.get_name(),'label':a.get_actor_label(),'class':a.get_class().get_name(),'transform':str(a.get_actor_transform()),'tags':[str(t) for t in a.tags],'folder':str(a.get_folder_path()),'hidden':a.get_editor_property('hidden'),'editor_hidden':a.is_temporarily_hidden_in_editor(),'collision':a.get_actor_enable_collision(),'components':[]}
 for c in a.get_components_by_class(unreal.StaticMeshComponent):
  m=c.static_mesh
  d['components'].append({'name':c.get_name(),'mesh':m.get_path_name() if m else None,'materials':[x.get_path_name() if x else None for x in c.get_materials()],'collision':str(c.get_collision_enabled()),'profile':str(c.get_collision_profile_name()),'visible':c.get_editor_property('visible'),'shadow':c.get_editor_property('cast_shadow'),'relative_transform':str(c.get_relative_transform())})
 if isinstance(a,unreal.Light):d['light']={k:str(a.light_component.get_editor_property(k)) for k in ['intensity','light_color','use_temperature','temperature']}
 return kd_clean(d)
kd_before={a.get_name():kd_snapshot(a) for a in kd_sub.get_all_level_actors()}
kd_backup=kd_root/'Saved/Backups'/datetime.datetime.now().strftime('KnownDetails_%Y%m%d_%H%M%S');kd_backup.mkdir(parents=True)
kd_map=kd_root/'Content/ATS/Maps/ATS_StudentCampus.umap'
shutil.copy2(kd_map,kd_backup/'ATS_StudentCampus_last_disk_save.umap')
assert kd_level.save_current_level();shutil.copy2(kd_map,kd_backup/'ATS_StudentCampus_before_known_details.umap')
(kd_out/'scene_before.json').write_text(json.dumps(kd_before,ensure_ascii=False,indent=2),encoding='utf-8')
shutil.copy2(kd_out/'scene_before.json',kd_backup/'scene_before.json')
kd_cam,kd_rot=kd_ed.get_level_viewport_camera_info()
kd_preparation={'backup':str(kd_backup),'actor_count':len(kd_before),'camera_world':[kd_cam.x,kd_cam.y,kd_cam.z],'rotation':{'pitch':kd_rot.pitch,'yaw':kd_rot.yaw,'roll':kd_rot.roll},'selected':[a.get_name() for a in kd_sub.get_selected_level_actors()],'map_before_sha256':hashlib.sha256(kd_map.read_bytes()).hexdigest()}
(kd_out/'preparation.json').write_text(json.dumps(kd_preparation,ensure_ascii=False,indent=2),encoding='utf-8')
print('KNOWN_DETAILS_PREPARED',len(kd_before))
