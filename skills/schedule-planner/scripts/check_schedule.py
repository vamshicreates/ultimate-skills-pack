#!/usr/bin/env python3
"""Check a scene/actor/timeline schedule model. Standard library only."""
import argparse
import datetime as dt
import json
from pathlib import Path
from zoneinfo import ZoneInfo


def integer(value, label):
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(f'{label}: nonnegative integer minutes required')
    return value


def strings(value, label, allow_empty=False):
    if not isinstance(value, list) or (not value and not allow_empty):
        raise ValueError(f'{label}: list required')
    if any(not isinstance(x, str) or not x.strip() for x in value) or len(set(value)) != len(value):
        raise ValueError(f'{label}: empty or duplicate identifier')
    return value


def check(model):
    zone = ZoneInfo(model.get('timezone', ''))
    required = set(strings(model.get('scenes'), 'scenes'))
    days = model.get('days')
    if not isinstance(days, list) or not days:
        raise ValueError('days must be nonempty')
    ids, covered, actor_shifts, reports = set(), set(), {}, []
    dated = ['date' in d for d in days]
    if any(dated) and not all(dated):
        raise ValueError('Supply dates for all day blocks or none')
    minimum_break = integer(model.get('minimum_break_minutes_per_day', 0), 'minimum_break_minutes_per_day')
    minimum_turn = model.get('minimum_turnaround_minutes')
    if minimum_turn is not None:
        minimum_turn = integer(minimum_turn, 'minimum_turnaround_minutes')
        if not all(dated):
            raise ValueError('Turnaround check requires a real start date for every block')
    for day in days:
        key = day.get('id')
        if not isinstance(key, str) or not key.strip() or key in ids:
            raise ValueError(f'Invalid / duplicate day ID: {key!r}')
        ids.add(key)
        begin = integer(day.get('call_start'), f'{key}.call_start')
        end = integer(day.get('call_end'), f'{key}.call_end')
        if end <= begin:
            raise ValueError(f'{key}: unit release must follow unit call')
        origin = None
        if all(dated):
            date = dt.date.fromisoformat(day['date'])
            origin = dt.datetime.combine(date, dt.time(), tzinfo=zone)
            first = origin + dt.timedelta(minutes=begin)
            last = origin + dt.timedelta(minutes=end)
            if any((origin + dt.timedelta(minutes=x)).utcoffset() != first.utcoffset() for x in range(begin, end + 1)):
                raise ValueError(f'{key}: timezone offset changes inside call; use an explicit-offset check')
        actors = {}
        calls = day.get('calls')
        if not isinstance(calls, list):
            raise ValueError(f'{key}: calls list required')
        for actor in calls:
            name = actor.get('character')
            if not isinstance(name, str) or not name.strip() or name in actors:
                raise ValueError(f'{key}: empty/duplicate actor call')
            call, ready, release = [integer(actor.get(f), f'{key}.{name}.{f}') for f in ('call', 'ready', 'release')]
            if not begin <= call <= ready <= release <= end:
                raise ValueError(f'{key}/{name}: call, ready or release outside unit timeline/order')
            actors[name] = (ready, release)
            if origin is not None:
                actor_shifts.setdefault(name, []).append((origin+dt.timedelta(minutes=call), origin+dt.timedelta(minutes=release), key))
        events = day.get('events')
        if not isinstance(events, list) or not events:
            raise ValueError(f'{key}: events required')
        cursor, breaks, shooting = begin, 0, 0
        for index, event in enumerate(events):
            a = integer(event.get('start'), f'{key}.events[{index}].start')
            b = integer(event.get('end'), f'{key}.events[{index}].end')
            kind = event.get('kind')
            if a != cursor or b <= a or b > end:
                raise ValueError(f'{key}: event {index} gap, overlap or invalid duration')
            if kind not in ('Setup', 'Blocking', 'Shoot', 'Break', 'Move', 'Buffer', 'Wrap'):
                raise ValueError(f'{key}: unknown event kind {kind!r}')
            refs = event.get('scene_refs', [])
            if kind == 'Shoot':
                refs = strings(refs, f'{key}.event[{index}].scene_refs')
                if set(refs) - required:
                    raise ValueError(f'{key}: unknown scene/component IDs {set(refs)-required}')
                cast = strings(event.get('cast'), f'{key}.event[{index}].cast', allow_empty=True)
                for name in cast:
                    if name not in actors or not actors[name][0] <= a < b <= actors[name][1]:
                        raise ValueError(f'{key}: {name} unavailable / not ready / released during event {index}')
                covered.update(refs)
                shooting += b-a
            elif refs:
                raise ValueError(f'{key}: only Shoot events can claim scene coverage')
            if kind == 'Break':
                breaks += b-a
            cursor = b
        if cursor != end or breaks < minimum_break:
            raise ValueError(f'{key}: incomplete call coverage or insufficient declared breaks')
        reports.append({'day': key, 'call_minutes': end-begin, 'shoot_minutes': shooting, 'break_minutes': breaks, 'characters_called': len(actors)})
    if required-covered:
        raise ValueError(f'Missing required scene/component coverage: {sorted(required-covered)}')
    if minimum_turn is not None:
        for actor, shifts in actor_shifts.items():
            shifts.sort()
            for previous, current in zip(shifts, shifts[1:]):
                gap = (current[0].astimezone(dt.timezone.utc)-previous[1].astimezone(dt.timezone.utc)).total_seconds()/60
                if gap < minimum_turn:
                    raise ValueError(f'{actor}: only {gap:g} minutes between {previous[2]} and {current[2]}')
    return {'active_days': len(days), 'components_covered': len(covered), 'dated_turnaround_checked': minimum_turn is not None, 'days': reports}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('model', type=Path)
    args = parser.parse_args()
    try:
        result = check(json.loads(args.model.read_text(encoding='utf-8')))
    except (ValueError, TypeError, KeyError, AttributeError, OSError) as exc:
        parser.exit(1, f'Schedule check failed: {exc}\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
