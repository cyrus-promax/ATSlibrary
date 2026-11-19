import unreal,pathlib,json
rv_sub=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);rv_ed=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
assert rv_ed.get_editor_world().get_name()=='ATS_Library_Workshop'
for a in rv_sub.get_all_level_actors():
 if a.get_actor_label()=='LW_InteriorExposure':
  s=a.get_editor_property('settings');s.set_editor_property('auto_exposure_min_brightness',80.0);s.set_editor_property('auto_exposure_max_brightness',80.0);a.set_editor_property('settings',s)
unreal.SystemLibrary.execute_console_command(rv_ed.get_editor_world(),'r.PostProcessAAQuality 4')
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
