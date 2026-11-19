"""Run in the ATS editor after importing the dining scale correction.

The dimensions checked here belong to the existing model, not a site survey.
This script saves a report, performs one initial pawn placement, and then uses
CharacterMovement for the complete route. It restores the editor camera.
"""
import json
import math
import pathlib
import time
import traceback
import unreal

ds_root = pathlib.Path('D:/Cyrus/OneDrive/文件/香港仔工業學校/ATS')
ds_manifest_path = ds_root / 'SourceAssets/Dining/ScaleCorrection_20261108/construction_manifest.json'
ds_data = json.loads(ds_manifest_path.read_text(encoding='utf-8'))
ds_report_path = ds_root / 'dining_scale_validation.json'
ds_ed = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
ds_level = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
ds_sub = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
ds_c, ds_s = math.cos(math.radians(20)), math.sin(math.radians(20))
ds_camera = ds_ed.get_level_viewport_camera_info()
ds_world = ds_ed.get_editor_world()


def ds_point(u, v, h):
    return unreal.Vector((-8 + ds_c * u - ds_s * v) * 100,
                         (24 - ds_s * u - ds_c * v) * 100,
                         (-24.55 + h) * 100)


def ds_local(p):
    x, y = p.x / 100 + 8, -p.y / 100 + 24
    return [ds_c * x + ds_s * y, -ds_s * x + ds_c * y, p.z / 100 + 24.55]


def ds_match_doors(actors):
    """Match physical door locations, without assuming an import tag name."""
    candidates = [a for a in actors if a.get_class().get_name() == 'ATSAutoDoor']
    matched = {}
    for definition in ds_data['doors']:
        center = ds_point(*definition['center'])
        near = []
        for actor in candidates:
            p = actor.get_actor_location()
            distance = math.sqrt((p.x - center.x) ** 2 + (p.y - center.y) ** 2 + (p.z - center.z) ** 2)
            # The existing door actor origin is at the hinge, 58 cm off centre.
            if distance < 150:
                near.append((distance, actor))
        if len(near) != 1:
            raise RuntimeError('Expected one door near ' + definition['id'] + '; found ' + str(len(near)))
        actor = near[0][1]
        if actor in matched.values():
            raise RuntimeError('One actor matched more than one dining door')
        matched[definition['id']] = actor
    if len(matched) != 3:
        raise RuntimeError('Expected exactly three dining doors')
    return matched


ds_doors_by_id = ds_match_doors(ds_sub.get_all_level_actors())
ds_doors = list(ds_doors_by_id.values())


def ds_hit(a, b):
    hit = unreal.SystemLibrary.line_trace_single(
        ds_world, ds_point(*a), ds_point(*b), unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,
        True, ds_doors, unreal.DrawDebugTrace.NONE, True)
    if not hit:
        return None
    row = hit.to_tuple()
    return {'blocking': row[0], 'actor': row[9].get_actor_label() if row[9] else None,
            'point': ds_local(row[4])}


ds_checks = []


def ds_check(name, a, b, blocked, height_range=None):
    hit = ds_hit(a, b)
    passed = bool(hit and hit['blocking']) == blocked
    if passed and blocked and height_range is not None:
        passed = height_range[0] <= hit['point'][2] <= height_range[1]
    ds_checks.append({'name': name, 'passed': passed, 'expected_blocking': blocked,
                      'from_campus': a, 'to_campus': b, 'hit': hit})


for ds_d in ds_data['doors']:
    ds_u, ds_v, ds_h = ds_d['center']
    for ds_height in [.2, .9, 1.75, 2.5]:
        if ds_d['axis'] == 'u':
            ds_a, ds_b = (ds_u, ds_v - .7, ds_height), (ds_u, ds_v + .7, ds_height)
        else:
            ds_a, ds_b = (ds_u - .7, ds_v, ds_height), (ds_u + .7, ds_v, ds_height)
        ds_check(ds_d['id'] + ' clear door aperture at ' + str(ds_height), ds_a, ds_b, False)

for ds_name, ds_a, ds_b, ds_blocked in [
    ('Former short-room u wall removed', (11.8, 14, 1.4), (13.3, 14, 1.4), False),
    ('Former false window wall removed', (14.5, 8.6, 1.4), (14.5, 10.2, 1.4), False),
    ('Existing west outer wall retained', (1.0, 12, 1.4), (-.5, 12, 1.4), True),
    ('Right wall between the two doors', (7.5, 18.4, 1.4), (7.5, 19.8, 1.4), True),
    ('Tuck shop side partition', (18, 7.1, 1.4), (18, 6.0, 1.4), True),
    ('Tuck shop serving opening', (16.4, 5.2, 1.6), (17.5, 5.2, 1.6), False),
    ('Original upper courtyard wall retained', (19.1, 13.646, 5), (20.5, 13.646, 5), True),
]:
    ds_check(ds_name, ds_a, ds_b, ds_blocked)

for ds_u in [5.5, 8.7, 11.9, 15.1, 18.3]:
    ds_check('Original veranda window blocks at u=' + str(ds_u),
             (ds_u, 4.25, 1.75), (ds_u, 2.85, 1.75), True)

for ds_u, ds_v in [(2, 8), (10, 12), (16, 15)]:
    ds_check('Expanded dining ceiling ' + str((ds_u, ds_v)),
             (ds_u, ds_v, 2.8), (ds_u, ds_v, 4.6), True, (3.0, 4.3))

# The earlier sky-clearance check was wrong: the existing veranda has floors
# above it. Check those floors and the restored roof independently instead.
ds_check('Existing first-floor veranda slab retained', (17.3, 1.9, 3.0),
         (17.3, 1.9, 5.0), True, (3.8, 4.4))
ds_check('Unsupported roof cut restored', (16, 8.6, 12.3),
         (16, 8.6, 13.3), True, (12.6, 13.1))

for ds_u, ds_v in [(1.5, 5), (5.5, 15), (10, 9.44), (18, 14),
                    (18.5, 18), (17.3, 1.9), (20.3, 13.646)]:
    ds_check('Walkable floor ' + str((ds_u, ds_v)),
             (ds_u, ds_v, .5), (ds_u, ds_v, -.5), True, (-.1, .1))

ds_route = [
    ('Existing school entrance', (27.8, -2)),
    ('Existing lobby', (27.8, 5)),
    ('Existing left lobby opening', (23.5, 5)),
    ('Existing courtyard approach', (23.5, 13.646)),
    ('Approach courtyard-side dining door', (21.25, 13.646)),
    ('Enter dining through courtyard-side door', (18.60, 13.646)),
    ('Clear the tuck shop before turning', (15.7, 13.646)),
    ('Approach tuck shop from the open hall', (15.7, 5.2)),
    ('Tuck shop serving window', (16.0, 5.2)),
    ('Return along the front of the tuck shop', (15.7, 5.2)),
    ('Clear tuck shop on the way to the washbasin', (15.7, 13.646)),
    ('Washbasin approach', (18.25, 16.15)),
    ('Drinking fountain approach', (18.20, 18.25)),
    ('Approach lower right door', (11.805, 17.8)),
    ('Exit lower right door', (11.805, 20.6)),
    ('Outside upper right door', (3.775, 20.6)),
    ('Enter upper right door', (3.775, 17.8)),
    ('Walk to the existing far end of the hall', (1.5, 17.8)),
    ('Walk the full hall beside the original window wall', (1.5, 5.0)),
    ('Return through the expanded hall', (15.7, 5.0)),
    ('Clear tuck shop when returning to the courtyard door', (15.7, 13.646)),
    ('Approach courtyard door from inside', (18.6, 13.646)),
    ('Exit courtyard-side dining door', (21.25, 13.646)),
    ('Return to the existing courtyard route', (23.5, 13.646)),
    ('Return to the left lobby doorway', (23.5, 5)),
    ('Re-enter the existing lobby', (27.8, 5)),
    ('Leave lobby through its existing left doorway', (23.5, 5)),
    ('Turn onto the existing front veranda', (23.5, 1.9)),
    ('Walk along the actual open veranda', (17.3, 1.9)),
]

ds_report = {
    'status': 'running', 'manifest': str(ds_manifest_path),
    'dimensions_basis': 'Existing model envelope fit; not a measured dining-room survey.',
    'static_checks': ds_checks, 'walk_checks': [], 'door_observations': {},
    'route': [{'name': name, 'campus_xy': xy} for name, xy in ds_route],
    'initial_placements': 0,
    'method': 'One initial placement outside the school gate; all subsequent travel uses CharacterMovement, including the expanded hall, three dining doors, lobby and existing veranda.',
}


def ds_save():
    ds_report_path.write_text(json.dumps(ds_report, ensure_ascii=False, indent=2), encoding='utf-8')


if not all(row['passed'] for row in ds_checks):
    ds_report['status'] = 'static_failed'
    ds_save()
    raise RuntimeError('Dining scale static checks failed; inspect dining_scale_validation.json')

ds_pawn = None
ds_start = time.monotonic()
ds_way = ds_start
ds_index = 0
ds_finishing = False
ds_wait_close = None
ds_runtime_doors = {}


def ds_finish(status):
    global ds_finishing
    ds_report['status'] = status
    ds_report['seconds'] = round(time.monotonic() - ds_start, 2)
    ds_save()
    ds_finishing = True
    ds_level.editor_request_end_play()


def ds_tick(delta):
    global ds_pawn, ds_way, ds_index, ds_wait_close, ds_runtime_doors
    try:
        now = time.monotonic()
        if ds_finishing:
            if not ds_ed.get_game_world():
                ds_ed.set_level_viewport_camera_info(*ds_camera)
                ds_report['camera_restored'] = True
                ds_save()
                unreal.unregister_slate_post_tick_callback(ds_handle)
            return
        if ds_pawn is None:
            world = ds_ed.get_game_world()
            if not world:
                if now - ds_start > 30:
                    ds_finish('no_game_world')
                return
            ds_pawn = unreal.GameplayStatics.get_player_character(world, 0)
            if not ds_pawn:
                if now - ds_start > 30:
                    ds_finish('no_pawn')
                return
            actors = unreal.GameplayStatics.get_all_actors_of_class(
                world, unreal.load_class(None, '/Script/ATS.ATSAutoDoor'))
            ds_runtime_doors = ds_match_doors(actors)
            for door_id, actor in ds_runtime_doors.items():
                ds_report['door_observations'][door_id] = {
                    'actor': actor.get_name(), 'max_angle': 0,
                    'opened': False, 'closed_after_leaving': False,
                }
            ds_pawn.set_actor_location(ds_point(27.8, -8, .96), False, True)
            ds_report['initial_placements'] += 1
            ds_way = now
            return
        for door_id, actor in ds_runtime_doors.items():
            angle = abs(actor.get_editor_property('current_angle'))
            record = ds_report['door_observations'][door_id]
            record['max_angle'] = max(record['max_angle'], angle)
            record['opened'] |= angle > 85
        if ds_wait_close is not None:
            if now - ds_wait_close > 4:
                for door_id, actor in ds_runtime_doors.items():
                    record = ds_report['door_observations'][door_id]
                    record['closed_after_leaving'] = abs(actor.get_editor_property('current_angle')) < 1
                    record['collision_restored'] = actor.get_editor_property('leaf').get_collision_enabled() == unreal.CollisionEnabled.QUERY_AND_PHYSICS
                doors_ok = len(ds_report['door_observations']) == 3 and all(
                    record['opened'] and record['closed_after_leaving'] and record['collision_restored']
                    for record in ds_report['door_observations'].values())
                ds_finish('passed' if doors_ok and ds_report['initial_placements'] == 1 else 'door_failed')
            return
        label, xy = ds_route[ds_index]
        position = ds_pawn.get_actor_location()
        target = ds_point(*xy, .95)
        dx, dy = target.x - position.x, target.y - position.y
        distance = math.hypot(dx, dy)
        if distance < 19:
            ok = abs(position.z - target.z) < 25
            ds_report['walk_checks'].append({
                'name': label, 'passed': ok, 'campus_position': ds_local(position),
                'height_error_cm': abs(position.z - target.z),
            })
            ds_pawn.character_movement.stop_movement_immediately()
            ds_save()
            if not ok:
                ds_finish('walk_height_failed')
                return
            ds_index += 1
            ds_way = now
            if ds_index == len(ds_route):
                ds_wait_close = now
            return
        if now - ds_way > 24:
            ds_report['blocked_at'] = {'name': label, 'campus_position': ds_local(position), 'target': xy}
            ds_finish('walk_blocked')
            return
        ds_pawn.add_movement_input(unreal.Vector(dx / distance, dy / distance, 0), min(1, distance / 100), True)
    except Exception:
        ds_report['error'] = traceback.format_exc()
        ds_finish('error')


ds_save()
ds_level.editor_request_begin_play()
ds_handle = unreal.register_slate_post_tick_callback(ds_tick)
