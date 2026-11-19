"""Run in the editor after importing the complete G-floor dining revision.

Only the initial school-gate placement teleports the pawn. All subsequent travel
uses CharacterMovement. Every shutter is held open under the pawn for longer
than its close delay; the two rear recesses are entered and exited separately.
"""
import json
import math
import pathlib
import time
import traceback
import unreal

vtf_root = pathlib.Path('D:/Cyrus/OneDrive/文件/香港仔工業學校/ATS')
vtf_manifest_path = vtf_root / 'SourceAssets/Dining/FullGroundFloor_20261108/construction_manifest.json'
vtf_manifest = json.loads(vtf_manifest_path.read_text(encoding='utf-8'))
vtf_report_path = vtf_root / 'dining_full_floor_validation.json'
vtf_ed = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
vtf_level = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
vtf_sub = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
assert not vtf_ed.get_game_world(), 'Stop an existing PIE session before validation.'
vtf_world = vtf_ed.get_editor_world()
assert vtf_world.get_name() == 'ATS_StudentCampus'
vtf_camera = vtf_ed.get_level_viewport_camera_info()
vtf_c, vtf_s = math.cos(math.radians(20)), math.sin(math.radians(20))


def vtf_point(u, v, h):
    return unreal.Vector((-8 + vtf_c * u - vtf_s * v) * 100,
                         (24 - vtf_s * u - vtf_c * v) * 100,
                         (-24.55 + h) * 100)


def vtf_local(p):
    x, y = p.x / 100 + 8, -p.y / 100 + 24
    return [vtf_c * x + vtf_s * y, -vtf_s * x + vtf_c * y, p.z / 100 + 24.55]


def vtf_match_shutters(actors):
    result = {}
    for definition in vtf_manifest['doors']:
        tag = 'ATS.DiningDoor.' + definition['id']
        matched = [a for a in actors if tag in [str(t) for t in a.tags]]
        assert len(matched) == 1, (tag, len(matched))
        actor = matched[0]
        assert actor.get_class().get_name() == 'ATSRollerShutter', (tag, actor.get_class().get_name())
        result[definition['id']] = actor
    assert len(result) == 3
    return result


def vtf_match_gate(actors):
    result = {}
    for actor in actors:
        if actor.get_class().get_name() != 'ATSAutoDoor':
            continue
        u, v, h = vtf_local(actor.get_actor_location())
        if abs(u - 27.8) < 2.5 and abs(v + 4.1) < .5 and abs(h) < .15:
            result[actor.get_name()] = actor
    assert len(result) == 2, ('Expected the two original swing-gate leaves', list(result))
    return result


vtf_editor_actors = vtf_sub.get_all_level_actors()
vtf_editor_shutters = vtf_match_shutters(vtf_editor_actors)
vtf_editor_gate = vtf_match_gate(vtf_editor_actors)


def vtf_hit(a, b, ignore_shutters=True, world=None, shutters=None):
    world = world or vtf_world
    shutters = vtf_editor_shutters if shutters is None else shutters
    ignore = list(shutters.values()) if ignore_shutters else []
    hit = unreal.SystemLibrary.line_trace_single(
        world, vtf_point(*a), vtf_point(*b), unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,
        True, ignore, unreal.DrawDebugTrace.NONE, True)
    if not hit:
        return None
    row = hit.to_tuple()
    actor = row[9]
    return {'blocking': row[0], 'actor': actor.get_name() if actor else None,
            'label': actor.get_actor_label() if actor else None,
            'point': vtf_local(row[4])}


vtf_static = []


def vtf_check(name, a, b, blocked, ignore_shutters=True, expected_actor=None, height_range=None):
    hit = vtf_hit(a, b, ignore_shutters)
    passed = bool(hit and hit['blocking']) == blocked
    if passed and blocked and expected_actor is not None:
        passed = hit['actor'] == expected_actor.get_name()
    if passed and blocked and height_range is not None:
        passed = height_range[0] <= hit['point'][2] <= height_range[1]
    vtf_static.append({'name': name, 'passed': passed, 'expected_blocking': blocked,
                       'from_campus': a, 'to_campus': b, 'hit': hit})


for vtf_definition in vtf_manifest['doors']:
    vtf_id = vtf_definition['id']
    vtf_u, vtf_v, _ = vtf_definition['center']
    vtf_shutter = vtf_editor_shutters[vtf_id]
    for vtf_height in [.2, .9, 1.75, 2.5]:
        if vtf_definition['axis'] == 'u':
            vtf_a, vtf_b = (vtf_u, vtf_v - .8, vtf_height), (vtf_u, vtf_v + .8, vtf_height)
        else:
            vtf_a, vtf_b = (vtf_u - .8, vtf_v, vtf_height), (vtf_u + .8, vtf_v, vtf_height)
        vtf_check(vtf_id + ' open structural aperture ' + str(vtf_height), vtf_a, vtf_b, False)
    vtf_check(vtf_id + ' closed curtain blocks',
              (vtf_u, vtf_v - .7, 1.4) if vtf_definition['axis'] == 'u' else (vtf_u - .7, vtf_v, 1.4),
              (vtf_u, vtf_v + .7, 1.4) if vtf_definition['axis'] == 'u' else (vtf_u + .7, vtf_v, 1.4),
              True, False, vtf_shutter)
    vtf_expected_count = math.ceil(vtf_shutter.get_editor_property('height') / vtf_shutter.get_editor_property('slat_pitch'))
    vtf_state_ok = (abs(vtf_shutter.get_editor_property('current_lift')) < .01
                    and vtf_shutter.get_editor_property('slats').get_instance_count() == vtf_expected_count == 38
                    and vtf_shutter.get_editor_property('curtain_collision').get_collision_enabled()
                    == unreal.CollisionEnabled.QUERY_AND_PHYSICS)
    vtf_static.append({'name': vtf_id + ' saved closed shutter state', 'passed': vtf_state_ok,
                       'expected_slat_count': vtf_expected_count})

for vtf_name, vtf_a, vtf_b, vtf_blocked in [
    ('Former v19.159 internal room wall removed', (10, 18.5, 1.4), (10, 20, 1.4), False),
    ('Former kiosk front u16.98 removed at solid-wall height', (16.4, 5.2, .65), (17.5, 5.2, .65), False),
    ('Former kiosk side v6.506 removed', (18, 5.9, 1.5), (18, 7.1, 1.5), False),
    ('New kiosk serving opening faces positive v', (16.25, 10.2, 1.7), (16.25, 9.0, 1.7), False),
    ('New kiosk serving counter', (16.25, 10.2, 1.04), (16.25, 9.0, 1.04), True),
    ('Enlarged kiosk side wall', (12.8, 6.0, 1.5), (14.0, 6.0, 1.5), True),
    ('Existing west exterior wall', (1.0, 20, 1.4), (-.5, 20, 1.4), True),
    ('Rear boundary remains between two shutters', (7.5, 29.7, 1.4), (7.5, 31.2, 1.4), True),
    ('Original upper courtyard wall retained', (19.1, 13.646, 5), (20.5, 13.646, 5), True),
]:
    vtf_check(vtf_name, vtf_a, vtf_b, vtf_blocked)

for vtf_u in [5.5, 8.7, 11.9, 15.1, 18.3]:
    vtf_check('Original G window blocks ' + str(vtf_u),
              (vtf_u, 4.25, 1.75), (vtf_u, 2.85, 1.75), True)
for vtf_u in [6, 12, 18]:
    vtf_check('Retained rear G column ' + str(vtf_u),
              (vtf_u - .6, 28.25, 1.5), (vtf_u + .6, 28.25, 1.5), True)
for vtf_u, vtf_v in [(2, 8), (10, 12), (10, 23), (16, 26)]:
    vtf_check('Whole-floor ceiling ' + str((vtf_u, vtf_v)),
              (vtf_u, vtf_v, 2.8), (vtf_u, vtf_v, 4.6), True, height_range=(3.0, 4.3))
vtf_check('Existing first-floor veranda slab retained', (17.3, 1.9, 3.0),
          (17.3, 1.9, 5.0), True, height_range=(3.8, 4.4))
for vtf_u, vtf_v in [(1.5, 5), (10, 12), (10, 21), (16.25, 10.7), (18.2, 26.55),
                    (17.1, 29.3), (3.775, 31.3), (11.805, 31.3), (20.3, 13.646), (17.3, 1.9)]:
    vtf_check('Walkable floor ' + str((vtf_u, vtf_v)),
              (vtf_u, vtf_v, .5), (vtf_u, vtf_v, -.5), True, height_range=(-.1, .1))

# The rear outdoor recesses are isolated: return through each same shutter.
# Circumvent the retained columns before entering the rear strip at v=29.3.
# The enlarged kiosk occupies u>=13.4 and v<=9.6, so never cut through it.
vtf_route = [
    ('Existing school entrance', (27.8, -2), None),
    ('Existing lobby', (27.8, 5), None),
    ('Existing left lobby opening', (23.5, 5), None),
    ('Existing courtyard approach', (23.5, 13.646), None),
    ('Approach courtyard shutter', (21.25, 13.646), None),
    ('Stand under courtyard shutter', (19.8, 13.646), 'CourtyardSide'),
    ('Enter full-floor restaurant', (18.6, 13.646), None),
    ('Face the enlarged tuck shop', (16.25, 10.7), None),
    ('Move through the main hall', (10, 16), None),
    ('Cross the removed internal boundary', (10, 23.5), None),
    ('Washbasin approach', (18.2, 26.55), None),
    ('Clear the column before moving rearward', (17.1, 26.55), None),
    ('Pass beside the retained u18 column', (17.1, 29.3), None),
    ('Drinking fountain approach', (18.2, 29.3), None),
    ('Return beside the u18 column', (17.1, 29.3), None),
    ('Return to clear main aisle', (17.1, 27.3), None),
    ('Go left of retained u12 column', (10.8, 27.3), None),
    ('Pass beside retained u12 column', (10.8, 29.3), None),
    ('Approach lower rear shutter', (11.805, 29.3), None),
    ('Stand under lower rear shutter', (11.805, 30.4), 'RightLower'),
    ('Exit lower rear shutter into its recess', (11.805, 31.3), None),
    ('Return through lower rear shutter', (11.805, 29.3), None),
    ('Clear lower shutter and column', (10.8, 29.3), None),
    ('Approach upper rear shutter inside the hall', (3.775, 29.3), None),
    ('Stand under upper rear shutter', (3.775, 30.4), 'RightUpper'),
    ('Exit upper rear shutter into its recess', (3.775, 31.3), None),
    ('Return through upper rear shutter', (3.775, 29.3), None),
    ('Clear retained columns on west side', (3.775, 26.8), None),
    ('Walk the length of the enlarged hall', (3, 12), None),
    ('Original window side', (3, 5), None),
    ('Stop before enlarged kiosk side wall', (11.7, 5), None),
    ('Pass around kiosk front corner', (11.7, 12), None),
    ('Return to courtyard shutter from inside', (18.6, 13.646), None),
    ('Exit courtyard shutter', (21.25, 13.646), None),
    ('Existing courtyard route', (23.5, 13.646), None),
    ('Return to existing left lobby opening', (23.5, 5), None),
    ('Re-enter existing lobby', (27.8, 5), None),
    ('Leave through existing left lobby opening', (23.5, 5), None),
    ('Turn onto original front veranda', (23.5, 1.9), None),
    ('Walk along original front veranda', (17.3, 1.9), None),
]

vtf_report = {
    'status': 'running', 'manifest': str(vtf_manifest_path),
    'dimensions_basis': 'User-confirmed entire G-floor use; metric dimensions fit the existing exterior model and are not a site survey.',
    'static_checks': vtf_static, 'walk_checks': [], 'hold_open_checks': [],
    'shutter_observations': {}, 'gate_observations': {},
    'route': [{'name': label, 'campus_xy': xy, 'hold_under_shutter': hold} for label, xy, hold in vtf_route],
    'initial_placements': 0,
    'method': 'One initial placement outside the school gate. All later movement uses CharacterMovement; each rear recess is entered and left through the same shutter, without crossing the unbuilt exterior area.',
}


def vtf_save():
    vtf_report_path.write_text(json.dumps(vtf_report, ensure_ascii=False, indent=2), encoding='utf-8')


if not all(row['passed'] for row in vtf_static):
    vtf_report['status'] = 'static_failed'
    vtf_save()
    raise RuntimeError('Dining full-floor static checks failed; inspect dining_full_floor_validation.json')

vtf_pawn = None
vtf_start = time.monotonic()
vtf_way_started = vtf_start
vtf_index = 0
vtf_finishing = False
vtf_wait_close = None
vtf_hold = None
vtf_runtime_shutters = {}
vtf_runtime_gate = {}
vtf_game_world = None


def vtf_finish(status):
    global vtf_finishing
    vtf_report['status'] = status
    vtf_report['seconds'] = round(time.monotonic() - vtf_start, 2)
    vtf_save()
    vtf_finishing = True
    vtf_level.editor_request_end_play()


def vtf_advance(now):
    global vtf_index, vtf_way_started, vtf_wait_close
    vtf_index += 1
    vtf_way_started = now
    if vtf_index == len(vtf_route):
        vtf_wait_close = unreal.GameplayStatics.get_time_seconds(vtf_game_world)


def vtf_observe():
    for shutter_id, actor in vtf_runtime_shutters.items():
        lift = actor.get_editor_property('current_lift')
        count = actor.get_editor_property('slats').get_instance_count()
        collision = actor.get_editor_property('curtain_collision').get_collision_enabled()
        height = actor.get_editor_property('height')
        record = vtf_report['shutter_observations'][shutter_id]
        record['max_lift_cm'] = max(record['max_lift_cm'], lift)
        record['minimum_visible_slats'] = min(record['minimum_visible_slats'], count)
        record['fully_opened'] |= lift >= height - .05 and count == 0 and collision == unreal.CollisionEnabled.NO_COLLISION
    for name, actor in vtf_runtime_gate.items():
        angle = abs(actor.get_editor_property('current_angle'))
        record = vtf_report['gate_observations'][name]
        record['max_angle'] = max(record['max_angle'], angle)
        record['opened_as_swing_gate'] |= angle > 85


def vtf_tick(delta):
    global vtf_pawn, vtf_way_started, vtf_hold, vtf_runtime_shutters, vtf_runtime_gate, vtf_game_world
    try:
        now = time.monotonic()
        if vtf_finishing:
            if not vtf_ed.get_game_world():
                vtf_ed.set_level_viewport_camera_info(*vtf_camera)
                vtf_report['camera_restored'] = True
                vtf_save()
                unreal.unregister_slate_post_tick_callback(vtf_handle)
            return
        if vtf_pawn is None:
            vtf_game_world = vtf_ed.get_game_world()
            if not vtf_game_world:
                if now - vtf_start > 30:
                    vtf_finish('no_game_world')
                return
            vtf_pawn = unreal.GameplayStatics.get_player_character(vtf_game_world, 0)
            if not vtf_pawn:
                if now - vtf_start > 30:
                    vtf_finish('no_pawn')
                return
            actors = unreal.GameplayStatics.get_all_actors_of_class(vtf_game_world, unreal.Actor)
            vtf_runtime_shutters = vtf_match_shutters(actors)
            vtf_runtime_gate = vtf_match_gate(actors)
            for shutter_id, actor in vtf_runtime_shutters.items():
                vtf_report['shutter_observations'][shutter_id] = {
                    'actor': actor.get_name(), 'height_cm': actor.get_editor_property('height'),
                    'max_lift_cm': 0, 'minimum_visible_slats': actor.get_editor_property('slats').get_instance_count(),
                    'fully_opened': False, 'closed_after_leaving': False,
                }
            for name, actor in vtf_runtime_gate.items():
                vtf_report['gate_observations'][name] = {
                    'class': actor.get_class().get_name(), 'max_angle': 0,
                    'opened_as_swing_gate': False, 'closed_after_leaving': False,
                }
            vtf_pawn.set_actor_location(vtf_point(27.8, -8, .96), False, True)
            vtf_report['initial_placements'] += 1
            vtf_way_started = now
            return

        vtf_observe()
        game_time = unreal.GameplayStatics.get_time_seconds(vtf_game_world)
        if vtf_wait_close is not None:
            if game_time - vtf_wait_close > 5.0:
                for shutter_id, actor in vtf_runtime_shutters.items():
                    record = vtf_report['shutter_observations'][shutter_id]
                    record['closed_after_leaving'] = abs(actor.get_editor_property('current_lift')) < .05
                    record['closed_visible_slats'] = actor.get_editor_property('slats').get_instance_count()
                    record['slats_restored'] = record['closed_visible_slats'] == 38
                    record['collision_restored'] = actor.get_editor_property('curtain_collision').get_collision_enabled() == unreal.CollisionEnabled.QUERY_AND_PHYSICS
                    definition = next(d for d in vtf_manifest['doors'] if d['id'] == shutter_id)
                    u, v, _ = definition['center']
                    a, b = ((u, v-.7, 1.4), (u, v+.7, 1.4)) if definition['axis'] == 'u' else ((u-.7, v, 1.4), (u+.7, v, 1.4))
                    hit = vtf_hit(a, b, False, vtf_game_world, vtf_runtime_shutters)
                    record['closed_curtain_trace_blocks'] = bool(hit and hit['blocking'] and hit['actor'] == actor.get_name())
                for name, actor in vtf_runtime_gate.items():
                    record = vtf_report['gate_observations'][name]
                    record['closed_after_leaving'] = abs(actor.get_editor_property('current_angle')) < 1
                    record['collision_restored'] = actor.get_editor_property('leaf').get_collision_enabled() == unreal.CollisionEnabled.QUERY_AND_PHYSICS
                shutter_ok = all(r['fully_opened'] and r['closed_after_leaving'] and r['slats_restored'] and r['collision_restored'] and r['closed_curtain_trace_blocks'] for r in vtf_report['shutter_observations'].values())
                gate_ok = all(r['class'] == 'ATSAutoDoor' and r['opened_as_swing_gate'] and r['closed_after_leaving'] and r['collision_restored'] for r in vtf_report['gate_observations'].values())
                hold_ok = len(vtf_report['hold_open_checks']) == 3 and all(r['passed'] for r in vtf_report['hold_open_checks'])
                vtf_finish('passed' if shutter_ok and gate_ok and hold_ok and vtf_report['initial_placements'] == 1 else 'runtime_checks_failed')
            return

        if vtf_hold is not None:
            actor = vtf_runtime_shutters[vtf_hold['id']]
            lift = actor.get_editor_property('current_lift')
            height = actor.get_editor_property('height')
            count = actor.get_editor_property('slats').get_instance_count()
            collision = actor.get_editor_property('curtain_collision').get_collision_enabled()
            vtf_pawn.character_movement.stop_movement_immediately()
            if vtf_hold['full_open_game_time'] is None:
                if lift >= height-.05 and count == 0 and collision == unreal.CollisionEnabled.NO_COLLISION:
                    vtf_hold['full_open_game_time'] = game_time
                elif now-vtf_hold['wall_start'] > 8:
                    vtf_report['failed_hold'] = dict(vtf_hold, lift_cm=lift, slats=count)
                    vtf_finish('shutter_not_fully_open_under_pawn')
                return
            vtf_hold['minimum_lift_cm'] = min(vtf_hold['minimum_lift_cm'], lift)
            vtf_hold['kept_fully_open'] &= lift >= height-.05 and count == 0 and collision == unreal.CollisionEnabled.NO_COLLISION
            elapsed = game_time-vtf_hold['full_open_game_time']
            if elapsed >= vtf_hold['required_game_seconds']:
                record = {'shutter': vtf_hold['id'], 'passed': bool(vtf_hold['kept_fully_open']),
                          'game_seconds_under_open_shutter': elapsed,
                          'configured_hold_delay_seconds': actor.get_editor_property('hold_open_seconds'),
                          'minimum_lift_cm': vtf_hold['minimum_lift_cm'],
                          'pawn_campus_position': vtf_local(vtf_pawn.get_actor_location())}
                vtf_report['hold_open_checks'].append(record)
                vtf_hold = None
                vtf_save()
                if not record['passed']:
                    vtf_finish('shutter_lowered_under_pawn')
                    return
                vtf_advance(now)
            return

        label, xy, hold_id = vtf_route[vtf_index]
        position = vtf_pawn.get_actor_location()
        target = vtf_point(*xy, .95)
        dx, dy = target.x-position.x, target.y-position.y
        distance = math.hypot(dx, dy)
        if distance < 19:
            ok = abs(position.z-target.z) < 25
            vtf_report['walk_checks'].append({'name': label, 'passed': ok,
                                             'campus_position': vtf_local(position),
                                             'height_error_cm': abs(position.z-target.z)})
            vtf_pawn.character_movement.stop_movement_immediately()
            vtf_save()
            if not ok:
                vtf_finish('walk_height_failed')
                return
            if hold_id:
                actor = vtf_runtime_shutters[hold_id]
                vtf_hold = {'id': hold_id, 'wall_start': now, 'full_open_game_time': None,
                            'required_game_seconds': max(3.2, actor.get_editor_property('hold_open_seconds')+1.2),
                            'minimum_lift_cm': actor.get_editor_property('height'), 'kept_fully_open': True}
            else:
                vtf_advance(now)
            return
        if now-vtf_way_started > 30:
            vtf_report['blocked_at'] = {'name': label, 'campus_position': vtf_local(position), 'target': xy}
            vtf_finish('walk_blocked')
            return
        vtf_pawn.add_movement_input(unreal.Vector(dx/distance, dy/distance, 0), min(1, distance/100), True)
    except Exception:
        vtf_report['error'] = traceback.format_exc()
        vtf_finish('error')


vtf_save()
vtf_level.editor_request_begin_play()
vtf_handle = unreal.register_slate_post_tick_callback(vtf_tick)
