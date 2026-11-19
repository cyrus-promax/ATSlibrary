"""Give only the five G-floor west-wing panes a dedicated material slot.

This writes an isolated replacement mesh. The source campus blend is read only.
No Unreal Editor calls are made. Upper-floor materials and geometry stay intact.
"""
import array
import hashlib
import json
import math
import pathlib

import bpy

task = pathlib.Path('C:/Users/Cyrus/Documents/Codex/2026-11-06/dao')
root = pathlib.Path('D:/Cyrus/OneDrive/文件/香港仔工業學校/ATS')
source = root / 'SourceAssets/Walkthrough/ATS_Walkthrough.blend'
revision_source = task / 'work/ATS_before_structure_removal/Walkthrough/ATS_FacadeRevision.fbx'
output = root / 'SourceAssets/Dining/ScaleCorrection_20261108/WindowCorrection'
output.mkdir(parents=True, exist_ok=True)
c, s = math.cos(math.radians(20)), math.sin(math.radians(20))


def file_hash(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def campus(p):
    x, y = p.x + 8, p.y + 24
    return (c * x + s * y, -s * x + c * y, p.z + 24.55)


def find_glass():
    exact = bpy.data.objects.get('SM_Walk_HistoricWestWing_FacadeGlass')
    if exact and exact.type == 'MESH':
        return exact
    candidates = [obj for obj in bpy.data.objects if obj.type == 'MESH'
                  and 'HistoricWestWing' in obj.name and 'Glass' in obj.name]
    assert len(candidates) == 1, [(obj.name, len(obj.data.polygons)) for obj in candidates]
    return candidates[0]


def geometry_signature(obj):
    """Compare FBX and blend surface geometry despite vertex/face reordering.

    Round world coordinates to 1 mm; the original points are in metres.
    No room dimensions are inferred from this comparison.
    """
    points = [tuple(round(value, 3) for value in obj.matrix_world @ vertex.co)
              for vertex in obj.data.vertices]
    faces = sorted(tuple(sorted(points[index] for index in face.vertices))
                   for face in obj.data.polygons)
    return hashlib.sha256(repr(faces).encode('ascii')).hexdigest()


def exact_mesh_state(obj):
    vertices = array.array('f', [0]) * (3 * len(obj.data.vertices))
    obj.data.vertices.foreach_get('co', vertices)
    loops = array.array('i', [0]) * len(obj.data.loops)
    obj.data.loops.foreach_get('vertex_index', loops)
    totals = array.array('i', [0]) * len(obj.data.polygons)
    obj.data.polygons.foreach_get('loop_total', totals)
    uv_states = []
    for layer in obj.data.uv_layers:
        coords = array.array('f', [0]) * (2 * len(layer.data))
        layer.data.foreach_get('uv', coords)
        uv_states.append((layer.name, coords.tobytes()))
    return (vertices.tobytes(), loops.tobytes(), totals.tobytes(), tuple(uv_states),
            tuple(tuple(row) for row in obj.matrix_world),
            tuple(face.use_smooth for face in obj.data.polygons))


source_hash_before = file_hash(source)
bpy.ops.wm.open_mainfile(filepath=str(source))
original_obj = find_glass()
source_name = original_obj.name
source_signature = geometry_signature(original_obj)
source_counts = [len(original_obj.data.vertices), len(original_obj.data.polygons)]
source_material_names = [material.name if material else None for material in original_obj.data.materials]
assert source_counts == [120, 90], source_counts

# The live Revision8 actor was imported from this archived facade FBX.
# Stop rather than silently substitute different facade geometry.
assert revision_source.is_file(), str(revision_source)
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=str(revision_source))
revision_obj = find_glass()
revision_signature = geometry_signature(revision_obj)
revision_counts = [len(revision_obj.data.vertices), len(revision_obj.data.polygons)]
assert source_signature == revision_signature, {
    'error': 'Revision8 facade glass geometry differs from source blend',
    'source_counts': source_counts, 'revision_counts': revision_counts,
    'source_signature': source_signature, 'revision_signature': revision_signature,
}

bpy.ops.wm.open_mainfile(filepath=str(source))
obj = find_glass()
before_geometry = exact_mesh_state(obj)
before_indices = [face.material_index for face in obj.data.polygons]
before_names = [material.name if material else None for material in obj.data.materials]
points = [campus(obj.matrix_world @ vertex.co) for vertex in obj.data.vertices]
all_vertices = set()
all_faces = set()
windows = []
epsilon = .0002
for center_u in [5.5, 8.7, 11.9, 15.1, 18.3]:
    bounds = [(center_u - 1.25, center_u + 1.25), (3.531, 3.549), (1.05, 3.15)]
    vertices = {index for index, point in enumerate(points)
                if all(lo - epsilon <= value <= hi + epsilon
                       for value, (lo, hi) in zip(point, bounds))}
    faces = {face.index for face in obj.data.polygons if set(face.vertices) <= vertices}
    assert len(vertices) == 8, (center_u, len(vertices))
    assert len(faces) == 6, (center_u, len(faces))
    assert not (all_vertices & vertices) and not (all_faces & faces)
    all_vertices.update(vertices)
    all_faces.update(faces)
    windows.append({'center_campus_u': center_u, 'bounds_campus_m': bounds,
                    'vertices': sorted(vertices), 'faces': sorted(faces)})
assert len(all_vertices) == 40 and len(all_faces) == 30

glass = bpy.data.materials.get('M_DiningBuild_Glass')
if glass is None:
    glass = bpy.data.materials.new('M_DiningBuild_Glass')
    glass.diffuse_color = (.72, .86, .88, .16)
    glass.use_nodes = True
    principled = glass.node_tree.nodes.get('Principled BSDF')
    principled.inputs['Base Color'].default_value = (.72, .86, .88, 1)
    principled.inputs['Roughness'].default_value = .08
    principled.inputs['IOR'].default_value = 1.45
    principled.inputs['Transmission Weight'].default_value = 1
obj.data.materials.append(glass)
new_slot = len(obj.data.materials) - 1
for index in all_faces:
    obj.data.polygons[index].material_index = new_slot

assert exact_mesh_state(obj) == before_geometry
after_indices = [face.material_index for face in obj.data.polygons]
changed = {index for index, (before, after) in enumerate(zip(before_indices, after_indices)) if before != after}
assert changed == all_faces
assert [material.name if material else None for material in obj.data.materials][:-1] == before_names
assert all(after_indices[index] == before_indices[index]
           for index in range(len(after_indices)) if index not in all_faces)
assert geometry_signature(obj) == source_signature

for other in list(bpy.data.objects):
    if other != obj:
        bpy.data.objects.remove(other, do_unlink=True)
bpy.context.scene.unit_settings.system = 'METRIC'
bpy.context.scene.unit_settings.scale_length = 1
bpy.ops.object.select_all(action='DESELECT')
obj.select_set(True)
bpy.context.view_layer.objects.active = obj
blend_path = output / 'ATS_DiningWindowCorrection.blend'
fbx_path = output / 'ATS_Dining_WindowGlass.fbx'
bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_as_mainfile(filepath=str(blend_path), compress=True)
bpy.ops.export_scene.fbx(
    filepath=str(fbx_path), use_selection=True, object_types={'MESH'},
    apply_unit_scale=True, apply_scale_options='FBX_SCALE_UNITS',
    axis_forward='-Z', axis_up='Y', mesh_smooth_type='FACE',
    add_leaf_bones=False, bake_anim=False, path_mode='STRIP')
assert exact_mesh_state(obj) == before_geometry
assert file_hash(source) == source_hash_before
report = {
    'status': 'passed', 'source_blend': str(source), 'source_sha256': source_hash_before,
    'source_unchanged': True, 'mesh_name': obj.name,
    'revision8_reference_fbx': str(revision_source),
    'revision8_reference_sha256': file_hash(revision_source),
    'revision8_geometry_matches_source_at_1mm': True,
    'source_surface_sha256_at_1mm': source_signature,
    'revision8_surface_sha256_at_1mm': revision_signature,
    'replacement_surface_sha256_at_1mm': geometry_signature(obj),
    'exact_mesh_state_sha256_before': hashlib.sha256(repr(before_geometry).encode('utf-8')).hexdigest(),
    'exact_mesh_state_sha256_after': hashlib.sha256(repr(exact_mesh_state(obj)).encode('utf-8')).hexdigest(),
    'revision8_mesh_counts': revision_counts,
    'original_material_names': source_material_names,
    'material_slots': [material.name if material else None for material in obj.data.materials],
    'new_ground_floor_material_slot': new_slot,
    'vertex_count': len(obj.data.vertices), 'face_count': len(obj.data.polygons),
    'matched_ground_vertices': len(all_vertices), 'changed_ground_faces': len(changed),
    'changed_face_indices': sorted(changed),
    'unchanged_other_face_materials': len(after_indices) - len(changed),
    'exact_geometry_uvs_transform_smoothing_unchanged': True,
    'windows': windows, 'blend': str(blend_path), 'fbx': str(fbx_path),
    'limits': 'Position-based identification in the existing model; not a site measurement. Unreal materials/collision and live appearance are not tested by this script.',
}
(output / 'window_manifest.json').write_text(
    json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
print('DINING_WINDOW_CORRECTION_PASSED', json.dumps({
    'mesh': obj.name, 'changed_faces': len(changed), 'matched_vertices': len(all_vertices),
    'unchanged_other_faces': len(after_indices) - len(changed), 'material_slots': report['material_slots'],
    'fbx': str(fbx_path)}, ensure_ascii=False))
