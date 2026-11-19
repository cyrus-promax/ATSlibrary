import unreal,pathlib,json
ce=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem);world=ce.get_editor_world();assert world.get_name()=='ATS_Library_Workshop'
for command in ['r.Streaming.PoolSize 1024','r.Shadow.Virtual.MaxPhysicalPages 1024','r.PostProcessAAQuality 4']:
 unreal.SystemLibrary.execute_console_command(world,command)
kept=[]
for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors():
 if isinstance(a,unreal.RectLight) and a.get_actor_label().startswith('LW_'):
  key=a.get_actor_label();cast=key.endswith('_1') or key=='LW_Main_SoftLight_6';a.light_component.set_editor_property('cast_shadows',cast)
  if cast:kept.append(key)
unreal.SystemLibrary.collect_garbage()
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
pathlib.Path('D:/Cyrus/OneDrive/文件/香港仔工業學校/ATS/SourceAssets/LibraryWorkshop_20261108/preview_memory_settings.json').write_text(json.dumps({'texture_pool_mb':1024,'virtual_shadow_pages':1024,'shadow_casting_rect_lights':kept,'source_textures_unchanged_4096':True,'cvar_scope':'Current editor session only'},indent=2),encoding='utf-8')
