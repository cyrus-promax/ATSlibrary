import bpy,pathlib,json,math,hashlib
root=pathlib.Path('D:/Cyrus/OneDrive/文件/香港仔工業學校/ATS');out=root/'SourceAssets/Dining/WallFloorDetail_20261108'
source=root/'SourceAssets/Dining/CrossWindowWall_20261108/ATS_Dining_CrossWindows.blend';before=hashlib.sha256(source.read_bytes()).hexdigest()
bpy.ops.wm.read_factory_settings(use_empty=True)
with bpy.data.libraries.load(str(source),link=False) as (src,dst):dst.objects=['SM_DiningCross_Tiles']
ob=dst.objects[0];bpy.context.collection.objects.link(ob);changed=[];oldpoints={i:tuple(v.co) for i,v in enumerate(ob.data.vertices)}
tileverts=set();otherverts=set()
for p in ob.data.polygons:
 (tileverts if ob.data.materials[p.material_index].name=='M_Dining_Hall_BasketMosaic' else otherverts).update(p.vertices)
assert not tileverts&otherverts
for i in tileverts:
 v=ob.data.vertices[i];h=(ob.matrix_world@v.co).z+24.55
 if abs(h-.15)<.00002:v.co.z-=.02;changed.append(i)
assert len(changed)>10
for i in otherverts:assert tuple(ob.data.vertices[i].co)==oldpoints[i]
ob.data.update();ob.name='SM_Dining_WallFloorJoinedPanels';ob.data.name=ob.name
bpy.context.scene.unit_settings.system='METRIC';bpy.context.scene.unit_settings.scale_length=1
bpy.ops.object.select_all(action='DESELECT');ob.select_set(True)
bpy.ops.export_scene.fbx(filepath=str(out/'SM_Dining_WallFloorJoinedPanels.fbx'),use_selection=True,object_types={'MESH'},apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',axis_forward='-Z',axis_up='Y',mesh_smooth_type='FACE',add_leaf_bones=False,bake_anim=False,path_mode='STRIP')
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(out/'ATS_Dining_WallFloorJoinedPanels.blend'))
assert before==hashlib.sha256(source.read_bytes()).hexdigest()
report={'source':str(source),'source_sha256_unchanged':before,'modified_vertices':len(changed),'change':'Extend existing pale mosaic panels down from h=.15 to the existing black skirting top h=.13, removing a continuous 20mm bare-paint sliver left by the old tile generator.','no_floor_or_dado_height_change':True,'black_skirting_cap_window_and_door_positions_unchanged':True,'render_only_no_collision':True,'new_partitions_or_floor_strips_added':False}
(out/'junction_mesh.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');print('JOINED_PANELS',report)
