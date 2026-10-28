#!/usr/bin/env python3
"""Validate one film's costume data and build a local HTML book and CSVs."""

import argparse
import csv
import html
import json
import re
import shutil
from collections import defaultdict
from pathlib import Path


class InvalidBible(ValueError):
    pass


def need(ok, message):
    if not ok:
        raise InvalidBible(message)


def text(value):
    return isinstance(value, str) and bool(value.strip())


def index(data, key):
    rows = data.get(key)
    need(isinstance(rows, list), f'{key} must be an array')
    result = {}
    for row in rows:
        need(isinstance(row, dict) and text(row.get('id')), f'{key}: record needs an id')
        need(row['id'] not in result, f'{key}: duplicate id {row["id"]}')
        result[row['id']] = row
    return result


def references(values, known, label, minimum=0):
    need(isinstance(values, list) and len(values) >= minimum, f'{label}: invalid reference list')
    need(all(isinstance(v, str) and v in known for v in values), f'{label}: unknown reference')
    need(len(values) == len(set(values)), f'{label}: duplicate reference')


def required_strings(row, keys):
    for key in keys:
        need(text(row.get(key)), f'{row.get("id", "record")}: missing {key}')


def check_basis(row, units, require_evidence=True):
    need(row.get('basis') in {'explicit', 'inferred', 'proposed', 'question'},
         f'{row["id"]}: invalid basis')
    items = row.get('evidence')
    minimum = 1 if require_evidence or row['basis'] in {'explicit', 'inferred'} else 0
    need(isinstance(items, list) and len(items) >= minimum, f'{row["id"]}: missing evidence')
    for e in items:
        need(isinstance(e, dict) and e.get('unit_id') in units and
             text(e.get('anchor')) and text(e.get('excerpt')), f'{row["id"]}: invalid evidence')
    if row['basis'] != 'explicit':
        need(text(row.get('rationale')), f'{row["id"]}: missing rationale')


def check_palette(values, label):
    need(isinstance(values, list), f'{label}: palette must be an array')
    for swatch in values:
        need(isinstance(swatch, dict), f'{label}: invalid swatch')
        required_strings(swatch, ['name', 'role', 'rationale'])
        need(isinstance(swatch.get('hex'), str) and re.fullmatch(r'#[0-9A-Fa-f]{6}', swatch['hex']),
             f'{label}: invalid HEX colour')
        need(swatch.get('basis') in {'explicit', 'inferred', 'proposed', 'question'},
             f'{label}: swatch needs basis')


def local_asset(root, value):
    need(text(value) and not Path(value).is_absolute() and '://' not in value,
         'Asset path must be local and relative to the JSON')
    path = (root / value).resolve()
    need(path.is_relative_to(root.resolve()), 'Asset path escapes the film folder')
    need(path.suffix.lower() in {'.png', '.jpg', '.jpeg', '.webp'}, 'Use PNG/JPEG/WebP assets')
    if path.is_file():
        with path.open('rb') as stream:
            sig = stream.read(16)
        valid = (sig.startswith(b'\x89PNG\r\n\x1a\n') if path.suffix.lower() == '.png' else
                 sig.startswith(b'\xff\xd8\xff') if path.suffix.lower() in {'.jpg', '.jpeg'} else
                 sig.startswith(b'RIFF') and sig[8:12] == b'WEBP')
        need(valid, f'Asset signature does not match its extension: {value}')
    return path


def validate(data, root):
    need(isinstance(data, dict) and data.get('schema_version') == '1.0', 'Unsupported schema')
    film, source = data.get('film'), data.get('source')
    need(isinstance(film, dict) and text(film.get('title')), 'Missing film title')
    need('revision' in film and film.get('design_status') in {'proposed', 'approved'}, 'Invalid film metadata')
    need(isinstance(source, dict) and text(source.get('filename')), 'Missing source')
    need(isinstance(source.get('sha256'), str) and re.fullmatch(r'[0-9a-f]{64}', source['sha256']), 'Invalid source hash')
    need(type(source.get('scene_inventory_complete')) is bool, 'Missing scene inventory status')
    need(isinstance(source.get('warnings'), list) and all(text(w) for w in source['warnings']), 'Invalid source warnings')
    units = index(source, 'units')
    need(units, 'No source units')
    for unit in units.values():
        required_strings(unit, ['locator'])
        need(type(unit.get('readable')) is bool and type(unit.get('reviewed')) is bool,
             f'{unit["id"]}: invalid coverage flags')
        need(not unit['reviewed'] or unit['readable'], f'{unit["id"]}: unreadable unit marked reviewed')
    collections = {k: index(data, k) for k in
                   ['characters', 'scenes', 'looks', 'states', 'appearances', 'continuity', 'assets', 'questions']}
    chars, scenes, looks, states, apps, links, assets, questions = collections.values()
    need(scenes, 'No scenes inventoried')
    check_palette(data.get('film_palette'), 'film')
    gaps = []
    if not source['scene_inventory_complete']:
        gaps.append('Full screenplay scene inventory not confirmed')
    gaps.extend(f'Source unit unread/unreadable: {u["id"]}' for u in units.values()
                if not (u['readable'] and u['reviewed']))
    if not data['film_palette']:
        gaps.append('Film palette missing')
    for char in chars.values():
        required_strings(char, ['name', 'identity_notes'])
        need(char.get('kind') in {'individual', 'background_group'}, f'{char["id"]}: invalid character kind')
        need(isinstance(char.get('reference_notes'), str) and 'identity_asset_id' in char,
             f'{char["id"]}: missing reference notes/asset field')
    for scene in scenes.values():
        required_strings(scene, ['slugline'])
        need('printed_number' in scene and 'story_day' in scene, f'{scene["id"]}: missing scene metadata')
        references(scene.get('source_unit_ids'), units, scene['id'], minimum=1)
        references(scene.get('on_screen_character_ids'), chars, scene['id'])
        references(scene.get('non_visual_character_ids'), chars, scene['id'])
        need(not set(scene['on_screen_character_ids']) & set(scene['non_visual_character_ids']),
             f'{scene["id"]}: visible and non-visual cast overlap')
        need(type(scene.get('costume_assessed')) is bool and isinstance(scene.get('coordination_notes'), str),
             f'{scene["id"]}: missing assessment/coordination')
        check_palette(scene.get('palette'), scene['id'])
        if not scene['costume_assessed']:
            gaps.append(f'{scene["id"]}: costume not assessed')
        if scene['on_screen_character_ids'] and not scene['palette']:
            gaps.append(f'{scene["id"]}: scene palette missing')
    for look in looks.values():
        need(look.get('character_id') in chars, f'{look["id"]}: unknown character')
        required_strings(look, ['name', 'design_notes'])
        check_basis(look, units, require_evidence=False)
        check_palette(look.get('palette'), look['id'])
        need(isinstance(look.get('garments'), list) and look['garments'], f'{look["id"]}: no garments')
        for garment in look['garments']:
            need(isinstance(garment, dict), f'{look["id"]}: invalid garment')
            required_strings(garment, ['item', 'description', 'material', 'colour', 'fit', 'details'])
        need('look_asset_id' in look, f'{look["id"]}: missing asset field')
    for state in states.values():
        need(state.get('look_id') in looks, f'{state["id"]}: unknown look')
        required_strings(state, ['name', 'condition_notes'])
        check_basis(state, units, require_evidence=False)
        need(type(state.get('requires_distinct_visual')) is bool and 'state_asset_id' in state,
             f'{state["id"]}: missing visual status')
        visited, current = {state['id']}, state
        while current.get('parent_state_id') is not None:
            parent = current['parent_state_id']
            need(parent in states and states[parent]['look_id'] == state['look_id'], f'{state["id"]}: invalid parent state')
            need(parent not in visited, f'{state["id"]}: cyclic state chain')
            visited.add(parent)
            current = states[parent]
    used_chars, used_looks, used_states = set(), set(), set()
    scene_char_apps = defaultdict(list)
    beats = set()
    for app in apps.values():
        need(app.get('scene_id') in scenes and app.get('character_id') in chars, f'{app["id"]}: unknown scene/character')
        need(app['character_id'] in scenes[app['scene_id']]['on_screen_character_ids'], f'{app["id"]}: character is not on screen')
        required_strings(app, ['beat', 'continuity_note'])
        need(isinstance(app.get('hair_makeup_notes'), str), f'{app["id"]}: missing grooming notes')
        need('look_id' in app and 'state_id' in app, f'{app["id"]}: missing look/state field')
        key = (app['scene_id'], app['character_id'], app['beat'])
        need(key not in beats, f'{app["id"]}: duplicate appearance beat')
        beats.add(key)
        check_basis(app, units)
        scene_char_apps[(app['scene_id'], app['character_id'])].append(app['id'])
        used_chars.add(app['character_id'])
        if app['look_id'] is None or app['state_id'] is None:
            need(app['look_id'] is None and app['state_id'] is None, f'{app["id"]}: assign both look and state or neither')
            gaps.append(f'{app["id"]}: costume look/state unassigned')
        else:
            need(app['look_id'] in looks and looks[app['look_id']]['character_id'] == app['character_id'],
                 f'{app["id"]}: look belongs to another character or is missing')
            need(app['state_id'] in states and states[app['state_id']]['look_id'] == app['look_id'],
                 f'{app["id"]}: state belongs to another look or is missing')
            used_looks.add(app['look_id'])
            used_states.add(app['state_id'])
    for scene in scenes.values():
        for cid in scene['on_screen_character_ids']:
            if not scene_char_apps[(scene['id'], cid)]:
                gaps.append(f'{scene["id"]}/{cid}: no appearance assignment')
    graph = defaultdict(set)
    for link in links.values():
        before, after = link.get('from_appearance_id'), link.get('to_appearance_id')
        need(before in apps and after in apps and before != after, f'{link["id"]}: invalid appearance link')
        a, b = apps[before], apps[after]
        need(a['character_id'] == b['character_id'], f'{link["id"]}: continuity crosses characters')
        relation = link.get('relation')
        need(relation in {'same_state', 'progression', 'reset', 'costume_change', 'possible_match'}, f'{link["id"]}: invalid relation')
        required_strings(link, ['match_notes'])
        check_basis(link, units)
        if relation == 'same_state':
            need(a['look_id'] is not None and a['look_id'] == b['look_id'] and a['state_id'] == b['state_id'], f'{link["id"]}: exact match differs')
        elif relation in {'progression', 'reset'}:
            need(a['look_id'] is not None and a['look_id'] == b['look_id'] and a['state_id'] != b['state_id'], f'{link["id"]}: invalid state transition')
        elif relation == 'costume_change':
            need(a['look_id'] is not None and b['look_id'] is not None and a['look_id'] != b['look_id'], f'{link["id"]}: change needs distinct looks')
        else:
            need(link['basis'] == 'question', f'{link["id"]}: possible match must be unresolved')
        graph[before].add(after)
        graph[after].add(before)
    for lid in used_looks:
        group = {a['id'] for a in apps.values() if a['look_id'] == lid}
        reached, pending = set(), [next(iter(group))]
        while pending:
            aid = pending.pop()
            if aid not in reached:
                reached.add(aid)
                pending.extend((graph[aid] & group) - reached)
        if reached != group:
            gaps.append(f'{lid}: repeated look has appearances without continuity links')
    for asset in assets.values():
        need(asset.get('kind') in {'character_board', 'look_board', 'state_board'}, f'{asset["id"]}: invalid asset kind')
        owners = {'character_board': chars, 'look_board': looks, 'state_board': states}[asset['kind']]
        need(asset.get('subject_id') in owners, f'{asset["id"]}: unknown asset subject')
        required_strings(asset, ['caption'])
        need(asset.get('review_status') in {'pending', 'passed', 'rejected'} and type(asset.get('is_placeholder')) is bool,
             f'{asset["id"]}: invalid review status')
        local_asset(root, asset.get('path'))

    def board(owner, field, kind):
        aid = owner.get(field)
        if aid is None:
            gaps.append(f'{owner["id"]}: missing {kind}')
            return
        need(aid in assets and assets[aid]['kind'] == kind and assets[aid]['subject_id'] == owner['id'],
             f'{owner["id"]}: asset subject/kind mismatch')
        asset = assets[aid]
        if not local_asset(root, asset['path']).is_file() or asset['review_status'] != 'passed' or asset['is_placeholder']:
            gaps.append(f'{owner["id"]}: artwork missing, unreviewed, rejected, or placeholder')

    for cid in used_chars:
        board(chars[cid], 'identity_asset_id', 'character_board')
    for lid in used_looks:
        board(looks[lid], 'look_asset_id', 'look_board')
        if not looks[lid]['palette']:
            gaps.append(f'{lid}: costume palette missing')
    for sid in used_states:
        state = states[sid]
        if state['requires_distinct_visual'] or state['state_asset_id'] is not None:
            board(state, 'state_asset_id', 'state_board')
    for question in questions.values():
        references(question.get('scene_ids'), scenes, question['id'])
        references(question.get('character_ids'), chars, question['id'])
        required_strings(question, ['text', 'owner'])
    return {'complete': not gaps, 'design_status': film['design_status'], 'scenes': len(scenes),
            'characters': len(used_chars), 'looks': len(used_looks), 'states': len(used_states),
            'appearances': len(apps), 'continuity_links': len(links), 'open_questions': len(questions), 'gaps': gaps}


def esc(value):
    return html.escape('Unknown' if value is None else str(value), quote=True)


def para(value, cls=''):
    return f'<p class="{cls}">{esc(value)}</p>'


def table(headers, rows):
    return '<table><thead><tr>' + ''.join(f'<th>{esc(h)}</th>' for h in headers) + '</tr></thead><tbody>' + ''.join(
        '<tr>' + ''.join(f'<td>{cell}</td>' for cell in row) + '</tr>' for row in rows) + '</tbody></table>'


def swatches(values):
    return '<div class="swatches">' + ''.join(
        f'<div class="swatch"><span style="background:{esc(s["hex"])}"></span><b>{esc(s["name"])} · {esc(s["hex"])}</b>'
        f'<small>{esc(s["role"])} · {esc(s["basis"])}</small><small>{esc(s["rationale"])}</small></div>' for s in values) + '</div>'


def cite(row):
    return para(' / '.join(f'{e["anchor"]}: “{e["excerpt"]}”' for e in row['evidence']), 'evidence')


def csv_value(value):
    if value is None:
        return ''
    value = json.dumps(value, ensure_ascii=False) if isinstance(value, (list, dict)) else str(value)
    return "'" + value if value.lstrip().startswith(('=', '+', '-', '@')) or value.startswith(('\t', '\n', '\r')) else value


def write_csv(path, fields, rows):
    with path.open('w', newline='', encoding='utf-8-sig') as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction='ignore')
        writer.writeheader()
        writer.writerows({f: csv_value(r.get(f)) for f in fields} for r in rows)


CSS = '''
@page { size:A4; margin:17mm 15mm 19mm; }
*{box-sizing:border-box} body{font:10pt/1.5 Arial,"Telugu Sangam MN","Noto Sans Telugu",sans-serif;color:#24313b;margin:0}
h1,h2,h3{color:#173f45;line-height:1.2;break-after:avoid}h1{font-size:29pt}h2{font-size:21pt}h3{font-size:14pt}
p{white-space:pre-wrap;overflow-wrap:anywhere}a{color:#195a66;text-decoration:none}section.chapter{break-before:page}
.kicker{font-size:9pt;text-transform:uppercase;letter-spacing:1.5px;color:#667c80}.badge{background:#e9f1ef;padding:9px;border-left:4px solid #29736a}
.draft{background:#fff1d6;border-color:#ac5c14}.muted,.evidence{font-size:8pt;color:#5e6d74}.evidence{border-left:2px solid #d6dfdf;padding-left:8px}
table{width:100%;border-collapse:collapse;font-size:8.5pt;margin:10px 0;table-layout:fixed}thead{display:table-header-group}
th{text-align:left;background:#e9f1ef;color:#173f45}th,td{padding:7px;border-bottom:1px solid #dbe3e3;vertical-align:top;overflow-wrap:anywhere;white-space:pre-wrap}
tr{break-inside:avoid}figure{margin:12px 0;break-inside:avoid}img{display:block;object-fit:contain;width:100%;max-height:166mm}
figcaption{font-size:8pt;color:#5e6d74;padding-top:5px}.thumb img{max-height:55mm}.comparison{display:flex;gap:14px}.comparison>div{width:50%}
.swatches{display:flex;flex-wrap:wrap;gap:8px;margin:12px 0}.swatch{width:calc(33.333% - 8px);break-inside:avoid;font-size:8pt;border:1px solid #e1e7e6;padding:7px}
.swatch span{display:block;height:24px;border:1px solid #a5b0b0;margin-bottom:5px}.swatch small,.swatch b{display:block;overflow-wrap:anywhere}
.missing{padding:18px;border:2px dashed #b36b30;background:#fff7eb}.keep{break-inside:avoid}.index{columns:2}.index p{margin:5px 0}
'''


def build(data, root, out, coverage):
    out.mkdir(parents=True, exist_ok=True)
    maps = {k: {r['id']: r for r in data[k]} for k in ['characters', 'looks', 'states', 'appearances', 'assets']}
    chars, looks, states, apps, assets = maps.values()
    copied = {}
    for aid, asset in assets.items():
        src = local_asset(root, asset['path'])
        if src.is_file():
            digest = __import__('hashlib').sha256(aid.encode()).hexdigest()[:16]
            target = out / 'assets' / (digest + src.suffix.lower())
            target.parent.mkdir(exist_ok=True)
            if src != target.resolve():
                shutil.copy2(src, target)
            copied[aid] = 'assets/' + target.name

    def image(aid, small=False):
        if aid not in copied:
            return '<div class="missing">Visual reference pending</div>'
        asset = assets[aid]
        label = ' · PLACEHOLDER' if asset['is_placeholder'] else ''
        return f'<figure class="{"thumb" if small else ""}"><img src="{copied[aid]}" alt="{esc(asset["caption"])}"><figcaption>{esc(aid)} · {esc(asset["caption"])}{label}</figcaption></figure>'

    def app_image(app, small=False):
        if app['state_id'] is None:
            return image(None, small)
        state = states[app['state_id']]
        aid = state['state_asset_id']
        if aid is None and not state['requires_distinct_visual']:
            aid = looks[app['look_id']]['look_asset_id']
        return image(aid, small)

    def link(target, label=None):
        return f'<a href="#{esc(target)}">{esc(label or target)}</a>'

    parts = ['<!doctype html><html lang="en"><head><meta charset="utf-8">',
             '<meta http-equiv="Content-Security-Policy" content="default-src &#39;none&#39;; img-src &#39;self&#39; data: file:; style-src &#39;unsafe-inline&#39;; font-src &#39;self&#39; file:;">',
             f'<title>{esc(data["film"]["title"])} — Costume Bible</title><style>{CSS}</style></head><body>',
             '<p class="kicker">Character · Costume · Colour · Continuity</p>',
             f'<h1>{esc(data["film"]["title"])}</h1>',
             para(f'Revision: {data["film"]["revision"] or "Unspecified"}'),
             para(('Complete coverage' if coverage['complete'] else 'DRAFT — INCOMPLETE COVERAGE') +
                  f' · Design status: {coverage["design_status"]}', 'badge' if coverage['complete'] else 'badge draft'),
             para(f'{coverage["scenes"]} scenes · {coverage["characters"]} visible characters/groups · {coverage["looks"]} looks · {coverage["states"]} states'),
             para('Generated references are costume design targets. Colour values are design references; physical fabric and camera matching remain to be checked.', 'muted'),
             para(f'Script: {data["source"]["filename"]}\nSHA-256: {data["source"]["sha256"]}', 'evidence')]
    if coverage['gaps'] or data['source']['warnings']:
        parts += ['<h3>Coverage gaps and source warnings</h3>'] + [para(g) for g in coverage['gaps'] + data['source']['warnings']]
    parts += ['<section class="chapter"><h2>Index</h2>', para('Film palette · Character boards · Costume looks · Scene plans · Continuity · Master assignments · Questions'), '<div class="index">']
    parts += [f'<p>{link(c["id"], c["name"])}</p>' for c in data['characters']]
    parts += [f'<p>{link(s["id"], s["id"] + " · " + s["slugline"])}</p>' for s in data['scenes']]
    parts += ['</div></section>', '<section class="chapter"><h2>Film colour palette</h2>', swatches(data['film_palette']), '</section>']
    visible_char_ids = {cid for s in data['scenes'] for cid in s['on_screen_character_ids']}
    assigned_look_ids = {a['look_id'] for a in data['appearances'] if a['look_id'] is not None}
    assigned_state_ids = {a['state_id'] for a in data['appearances'] if a['state_id'] is not None}
    for char in data['characters']:
        parts += [f'<section class="chapter" id="{esc(char["id"])}"><p class="kicker">Character {esc(char["id"])}</p><h2>{esc(char["name"])}</h2>',
                  para(char['identity_notes']), para(char['reference_notes'], 'muted'),
                  image(char['identity_asset_id']) if char['id'] in visible_char_ids else para('No on-screen costume requirement in this screenplay.'), '</section>']
        for look in [l for l in data['looks'] if l['character_id'] == char['id'] and l['id'] in assigned_look_ids]:
            look_apps = [a for a in data['appearances'] if a['look_id'] == look['id']]
            parts += [f'<section class="chapter" id="{esc(look["id"])}"><p class="kicker">{esc(char["name"])} · {esc(look["id"])}</p><h2>{esc(look["name"])}</h2>',
                      para(f'Design basis: {look["basis"]} · {look.get("rationale") or "Script/reference specified"}', 'badge'), image(look['look_asset_id']),
                      swatches(look['palette']), para(look['design_notes']), cite(look),
                      table(['Piece', 'Design and material', 'Colour / fit', 'Construction and accessories'],
                            [[esc(g['item']), esc(g['description'] + '\n' + g['material']), esc(g['colour'] + '\n' + g['fit']), esc(g['details'])] for g in look['garments']]),
                      '<h3>Scene appearances</h3>', '<p>' + ' · '.join(link(a['id'], a['scene_id'] + ' / ' + a['beat']) for a in look_apps) + '</p>', '</section>']
            for state in [s for s in data['states'] if s['look_id'] == look['id'] and s['id'] in assigned_state_ids]:
                parts += [f'<section class="chapter" id="{esc(state["id"])}"><p class="kicker">{esc(look["id"])} · {esc(state["id"])}</p><h3>{esc(state["name"])}</h3>',
                          para(state['condition_notes']), para(f'Basis: {state["basis"]} · {state.get("rationale") or "Script specified"}', 'muted'),
                          image(state['state_asset_id'] or (None if state['requires_distinct_visual'] else look['look_asset_id'])), cite(state),
                          para(state.get('reset_notes', 'Reset/duplicate requirements to be confirmed by costume department.')), '</section>']
    for scene in data['scenes']:
        parts += [f'<section class="chapter" id="{esc(scene["id"])}"><p class="kicker">Scene {esc(scene["printed_number"] or scene["id"])}</p><h2>{esc(scene["slugline"])}</h2>',
                  para(f'{scene["id"]} · Story day: {scene["story_day"] or "Unresolved"}'), swatches(scene['palette']), para(scene['coordination_notes'])]
        if scene['non_visual_character_ids']:
            parts += [para('Voice-only/mentioned, no visual costume assignment: ' + ', '.join(chars[c]['name'] for c in scene['non_visual_character_ids']), 'muted')]
        scene_apps = [a for a in data['appearances'] if a['scene_id'] == scene['id']]
        if not scene['on_screen_character_ids']:
            parts += [para('No visible characters in the inventoried scene.')]
        for app in scene_apps:
            parts += [f'<div id="{esc(app["id"])}"><h3>{esc(chars[app["character_id"]]["name"])} · {esc(app["beat"])}</h3>',
                      para(f'{app["id"]} · Look {app["look_id"] or "UNASSIGNED"} · State {app["state_id"] or "UNASSIGNED"}'), app_image(app, True),
                      para(app['continuity_note']), para('Hair/makeup match: ' + app['hair_makeup_notes']),
                      para(f'Assignment basis: {app["basis"]} · {app.get("rationale") or "Script specified"}', 'muted'), cite(app)]
            incoming = [l for l in data['continuity'] if l['to_appearance_id'] == app['id']]
            parts += [f'<p>{link(l["id"], "Continuity " + l["id"])} · {esc(l["relation"])} · match {link(l["from_appearance_id"])}: {esc(l["match_notes"])}</p>' for l in incoming]
            parts += ['</div>']
        parts += ['</section>']
    parts += ['<section class="chapter"><h2>Cross-scene continuity register</h2>']
    for item in data['continuity']:
        a, b = apps[item['from_appearance_id']], apps[item['to_appearance_id']]
        parts += [f'<article id="{esc(item["id"])}"><h3>{esc(item["id"])} · {esc(chars[a["character_id"]]["name"])} · {esc(item["relation"])}</h3>',
                  f'<p>{link(a["id"], a["scene_id"] + " / " + a["beat"])} → {link(b["id"], b["scene_id"] + " / " + b["beat"])}</p>',
                  '<div class="comparison"><div>' + app_image(a, True) + '</div><div>' + app_image(b, True) + '</div></div>',
                  para(item['match_notes']), para(f'Basis: {item["basis"]} · {item.get("rationale") or "Script specified"}', 'muted'), cite(item), '</article>']
    parts += ['</section>', '<section class="chapter"><h2>Master character / scene / costume assignments</h2>',
              table(['Character / scene', 'Beat / look / state', 'Continuity'],
                    [[link(a['id'], chars[a['character_id']]['name'] + ' / ' + a['scene_id']), esc(a['beat'] + '\n' + str(a['look_id']) + ' / ' + str(a['state_id'])), esc(a['continuity_note'])] for a in data['appearances']]), '</section>',
              '<section class="chapter"><h2>Questions for department review</h2>']
    parts += [para(f'{q["id"]} · {q["owner"]} · {", ".join(q["scene_ids"])}\n{q["text"]}') for q in data['questions']] or [para('No unresolved questions recorded.')]
    parts += ['</section></body></html>']
    (out / 'costume-bible.html').write_text('\n'.join(parts), encoding='utf-8')
    (out / 'coverage.json').write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    rows = []
    for a in data['appearances']:
        rows.append({**a, 'character_name': chars[a['character_id']]['name'],
                     'look_name': looks[a['look_id']]['name'] if a['look_id'] else None,
                     'state_name': states[a['state_id']]['name'] if a['state_id'] else None})
    write_csv(out / 'scene-costume-matrix.csv', ['id', 'scene_id', 'character_id', 'character_name', 'beat', 'look_id', 'look_name', 'state_id', 'state_name', 'basis', 'continuity_note', 'hair_makeup_notes', 'evidence'], rows)
    write_csv(out / 'continuity-register.csv', ['id', 'from_appearance_id', 'to_appearance_id', 'relation', 'match_notes', 'basis', 'rationale', 'evidence'], data['continuity'])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', type=Path)
    parser.add_argument('--out', type=Path)
    parser.add_argument('--allow-draft', action='store_true')
    parser.add_argument('--validate-only', action='store_true')
    args = parser.parse_args()
    try:
        data = json.loads(args.input.read_text(encoding='utf-8'))
        coverage = validate(data, args.input.resolve().parent)
        if not args.validate_only:
            need(coverage['complete'] or args.allow_draft, 'Incomplete package; resolve coverage gaps or use --allow-draft. Gaps: ' + '; '.join(coverage['gaps']))
            build(data, args.input.resolve().parent, args.out or args.input.parent / 'book', coverage)
        print(json.dumps(coverage, ensure_ascii=False, indent=2))
    except (ValueError, KeyError, TypeError, OSError) as exc:
        parser.exit(1, f'Costume bible validation/build failed: {exc}\n')


if __name__ == '__main__':
    main()
