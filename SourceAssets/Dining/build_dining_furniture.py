import bpy
import json
import math
import pathlib
from mathutils import Vector

root = pathlib.Path('D:/Cyrus/OneDrive/文件/香港仔工業學校/ATS')
out = root / 'SourceAssets/Dining'
out.mkdir(parents=True, exist_ok=True)
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
bpy.context.scene.unit_settings.system = 'METRIC'
bpy.context.scene.unit_settings.scale_length = 1.0
materials = {}
specs = {
    'WhiteLaminate': ([.73, .73, .70], .33, 0),
    'BluePolypropylene': ([.009, .029, .38], .33, 0),
    'BrushedSteel': ([.43, .46, .48], .29, 1),
    'GreyEdge': ([.13, .14, .14], .46, 0),
    'Rubber': ([.012, .014, .016], .82, 0),
}
for name, (colour, roughness, metal) in specs.items():
    mat = bpy.data.materials.new('M_Dining_' + name)
    mat.diffuse_color = (*colour, 1)
    mat.use_nodes = True
    shader = mat.node_tree.nodes.get('Principled BSDF')
    shader.inputs['Base Color'].default_value = (*colour, 1)
    shader.inputs['Roughness'].default_value = roughness
    shader.inputs['Metallic'].default_value = metal
    materials[name] = mat

parts = []
def finish(obj, mat, bevel=0, segments=3):
    obj.data.materials.append(materials[mat])
    if bevel:
        mod = obj.modifiers.new('Rounded manufactured edges', 'BEVEL')
        mod.width = bevel
        mod.segments = segments
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.modifier_apply(modifier=mod.name)
    for p in obj.data.polygons:
        p.use_smooth = True
    mod = obj.modifiers.new('Weighted normals', 'WEIGHTED_NORMAL')
    mod.keep_sharp = True
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.modifier_apply(modifier=mod.name)
    parts.append(obj)
    return obj

def box(center, size, mat, bevel=.004):
    bpy.ops.mesh.primitive_cube_add(size=1, location=center)
    obj = bpy.context.object
    obj.dimensions = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return finish(obj, mat, bevel)

def tube(a, b, radius, mat='BrushedSteel'):
    a, b = Vector(a), Vector(b)
    bpy.ops.mesh.primitive_cylinder_add(vertices=20, radius=radius, depth=(b-a).length, location=(a+b)/2)
    obj = bpy.context.object
    obj.rotation_euler = (b-a).to_track_quat('Z', 'Y').to_euler()
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return finish(obj, mat, .0012, 2)

def combine(name):
    bpy.ops.object.select_all(action='DESELECT')
    for p in parts:
        p.select_set(True)
    bpy.context.view_layer.objects.active = parts[0]
    bpy.ops.object.join()
    obj = bpy.context.object
    obj.name = name
    bpy.context.scene.cursor.location = (0, 0, 0)
    bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    # Deduplicate material slots, keeping the FBX slot names stable.
    old = list(obj.data.materials)
    unique = list(dict.fromkeys(old))
    indices = [unique.index(old[p.material_index]) for p in obj.data.polygons]
    obj.data.materials.clear()
    for mat in unique:
        obj.data.materials.append(mat)
    for p, index in zip(obj.data.polygons, indices):
        p.material_index = index
    parts.clear()
    return obj

# Photo-supported overall appearance. Dimensions are practical modelling
# estimates, not measurements of the real school's furniture.
box((0, 0, .733), (1.80, .80, .034), 'WhiteLaminate', .009,)
box((0, 0, .710), (1.79, .79, .016), 'GreyEdge', .006)
for y in [-.32, .32]:
    box((0, y, .665), (1.64, .027, .060), 'BrushedSteel', .004)
for x in [-.79, .79]:
    box((x, 0, .665), (.027, .66, .060), 'BrushedSteel', .004)
    for y in [-.31, .31]:
        box((x, y, .356), (.033, .033, .672), 'BrushedSteel', .004)
        box((x, y, .014), (.037, .037, .028), 'Rubber', .005)
table = combine('SM_Dining_WhiteTable')

# Slightly dished injection-moulded chair seat with a rounded front edge.
vertices = []
faces = []
nx, ny = 20, 22
for j in range(ny + 1):
    fy = j / ny
    y = -.222 + fy * .434
    width = .422 - .032 * fy
    for i in range(nx + 1):
        fx = i / nx
        x = (fx - .5) * width
        z = .447 - .014 * math.sin(math.pi * fx) * math.sin(math.pi * fy)
        z -= .009 * max(0, (0.16 - fy) / .16)
        vertices.append((x, y, z))
for j in range(ny):
    for i in range(nx):
        k = j * (nx + 1) + i
        faces.append((k, k+1, k+nx+2, k+nx+1))
mesh = bpy.data.meshes.new('Moulded seat surface')
mesh.from_pydata(vertices, [], faces)
mesh.update()
obj = bpy.data.objects.new('Blue seat', mesh)
bpy.context.collection.objects.link(obj)
bpy.context.view_layer.objects.active = obj
solid = obj.modifiers.new('Moulded thickness', 'SOLIDIFY')
solid.thickness = .014
bpy.ops.object.modifier_apply(modifier=solid.name)
finish(obj, 'BluePolypropylene', .005, 3)

# Curved back, lower opening and rounded upper corners visible in the leaflet.
vertices, faces = [], []
nx, nz = 28, 30
for j in range(nz + 1):
    fz = j / nz
    z = .477 + fz * .365
    half_width = .195 + .014 * math.sin(math.pi * fz)
    if fz > .88:
        half_width -= .022 * ((fz - .88)/.12)**2
    for i in range(nx + 1):
        fx = i / nx
        x = (fx - .5) * 2 * half_width
        y = .200 + .070 * fz - .022 * (abs(2*fx-1)**2)
        vertices.append((x, y, z))
for j in range(nz):
    for i in range(nx):
        # A small lower-back ventilation/hand opening; rounded by bevel.
        if 3 <= j <= 7 and 4 <= i <= 23:
            continue
        k = j * (nx + 1) + i
        faces.append((k, k+1, k+nx+2, k+nx+1))
mesh = bpy.data.meshes.new('Moulded back surface')
mesh.from_pydata(vertices, [], faces)
mesh.update()
obj = bpy.data.objects.new('Blue back', mesh)
bpy.context.collection.objects.link(obj)
bpy.context.view_layer.objects.active = obj
solid = obj.modifiers.new('Moulded thickness', 'SOLIDIFY')
solid.thickness = .014
bpy.ops.object.modifier_apply(modifier=solid.name)
finish(obj, 'BluePolypropylene', .005, 3)

for x in [-.178, .178]:
    tube((x, -.175, .414), (x, .18, .414), .011)
    tube((x, .174, .405), (x, .240, .760), .010)
    for y in [-.175, .175]:
        foot = (x * 1.16, y * 1.35, .022)
        tube(foot, (x, y, .416), .012)
        tube((foot[0], foot[1], .000), (foot[0], foot[1], .036), .014, 'Rubber')
tube((-.18, -.16, .405), (.18, -.16, .405), .009)
tube((-.18, .17, .405), (.18, .17, .405), .009)
chair = combine('SM_Dining_BlueChair')

objects = [table, chair]
for obj in objects:
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.export_scene.fbx(
        filepath=str(out / (obj.name + '.fbx')),
        use_selection=True, object_types={'MESH'}, apply_unit_scale=True,
        apply_scale_options='FBX_SCALE_UNITS', axis_forward='-Z', axis_up='Y',
        mesh_smooth_type='FACE', add_leaf_bones=False, bake_anim=False,
        path_mode='STRIP',
    )
bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_as_mainfile(filepath=str(out / 'ATS_Dining_Furniture.blend'))
report = {
    'source_photo': 'http://www.ats.edu.hk/images/PostImage/boarding_intro_10.jpg',
    'source_leaflet': 'http://www.ats.edu.hk/images/doc/20261102.pdf',
    'source_leaflet_pdf_page': 2,
    'confirmed_appearance': ['White rectangular dining tables', 'Blue moulded chairs with lower-back opening', 'Metal furniture frames'],
    'uncertainties': ['Exact furniture dimensions', 'Frame details hidden in photographs', 'Number and arrangement of dining sets', 'Room boundaries and ceiling height'],
    'model_dimensions_are_estimates': True,
    'table_dimensions_m': [1.8, .8, .75],
    'chair_dimensions_m': [.45, .54, .85],
    'chair_seat_height_m': .447,
    'materials': {name: {'colour_linear': colour, 'roughness': roughness, 'metallic': metal} for name, (colour, roughness, metal) in specs.items()},
    'meshes': [{'name': obj.name, 'vertices': len(obj.data.vertices), 'faces': len(obj.data.polygons), 'materials': [m.name for m in obj.data.materials]} for obj in objects],
    'placement_status': 'See dining_placement.json for the latest placement state',
}
(out / 'dining_furniture_manifest.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
print('DINING_FURNITURE_BUILT', report['meshes'])
