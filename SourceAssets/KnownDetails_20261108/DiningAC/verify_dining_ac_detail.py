import bpy, json, pathlib, math
from mathutils import Vector

out=pathlib.Path('D:/Cyrus/OneDrive/文件/香港仔工業學校/ATS/SourceAssets/KnownDetails_20261108/DiningAC')
manifest=json.loads((out/'ac_front_manifest.json').read_text(encoding='utf-8'))
bpy.ops.wm.open_mainfile(filepath=str(out/'ATS_Dining_AC_PhotoFronts.blend'))
meshes=[ob for ob in bpy.context.scene.objects if ob.type=='MESH']
assert len(meshes)==1
ob=meshes[0]
assert ob.name=='SM_DiningAC_PhotoFronts'
assert ob.matrix_world==__import__('mathutils').Matrix.Identity(4)
assert [m.name for m in ob.data.materials]==manifest['material_slots']
assert all(p.area>0 for p in ob.data.polygons)
blend_points=[tuple(ob.matrix_world@v.co) for v in ob.data.vertices]
def bounds(points):return [[min(p[k] for p in points),max(p[k] for p in points)] for k in range(3)]
blend_bounds=bounds(blend_points)
report={'blend_meshes':1,'mesh':ob.name,'vertices':len(ob.data.vertices),'polygons':len(ob.data.polygons),'zero_area_faces':0,'transform_identity':True,'materials':[m.name for m in ob.data.materials]}
for mat in ob.data.materials:
 mat.use_nodes=True
 shader=mat.node_tree.nodes.get('Principled BSDF')
 shader.inputs['Base Color'].default_value=mat.diffuse_color
 shader.inputs['Roughness'].default_value=manifest['new_material_specs'].get(mat.name,{}).get('roughness',.65)

# One representative unit, viewed from the dining-room side. This is a render
# of the prepared source mesh only, not a screenshot of the live UE project.
c,s=math.cos(math.radians(20)),math.sin(math.radians(20))
def site(u,v,h):return Vector((-8+c*u-s*v,-24+s*u+c*v,-24.55+h))
target=site(.18,16.12444727917336,2.812499809265137)
camera_data=bpy.data.cameras.new('ReviewCamera');camera=bpy.data.objects.new('ReviewCamera',camera_data);bpy.context.collection.objects.link(camera)
camera.location=target+Vector((c,s,0))*2
camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler()
camera_data.type='ORTHO';camera_data.ortho_scale=.82;bpy.context.scene.camera=camera
light_data=bpy.data.lights.new('ReviewLight','AREA');light=bpy.data.objects.new('ReviewLight',light_data);bpy.context.collection.objects.link(light)
light.location=target+Vector((c,s,.6))*2;light.rotation_euler=(target-light.location).to_track_quat('-Z','Y').to_euler();light_data.energy=160;light_data.shape='DISK';light_data.size=2
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=24
scene.render.resolution_x=820;scene.render.resolution_y=660;scene.render.resolution_percentage=100
scene.world=bpy.data.worlds.new('ReviewWorld');scene.world.color=(.18,.18,.18)
scene.view_settings.view_transform='Standard';scene.render.image_settings.file_format='PNG';scene.render.filepath=str(out/'source_mesh_front_review.png')
bpy.ops.render.render(write_still=True)

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=str(out/'ATS_Dining_AC_PhotoFronts.fbx'))
meshes=[ob for ob in bpy.context.scene.objects if ob.type=='MESH']
assert len(meshes)==1
ob=meshes[0]
fbx_bounds=bounds([tuple(ob.matrix_world@v.co) for v in ob.data.vertices])
error=max(abs(fbx_bounds[k][j]-blend_bounds[k][j]) for k in range(3) for j in range(2))
assert error<.00001,error
assert set(m.name for m in ob.data.materials)==set(manifest['material_slots'])
report.update({'fbx_meshes':1,'fbx_vertices':len(ob.data.vertices),'fbx_bounds_world_m':fbx_bounds,'fbx_roundtrip_max_bounds_error_m':error,'fbx_materials':[m.name for m in ob.data.materials],'ue_changes':False})
(out/'independent_asset_verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print('AC_INDEPENDENT_VERIFIED',json.dumps(report,ensure_ascii=False))
