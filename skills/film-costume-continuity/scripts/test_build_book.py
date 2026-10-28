"""Behavior checks for costume ownership, continuity, coverage, and exports."""
import base64
import copy
import csv
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

import build_book as book


def fixture(root):
    # Synthetic layout fixture, not a character or costume design.
    png = base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+aWQAAAABJRU5ErkJggg==')
    (root / 'test.png').write_bytes(png)
    evidence = [{'unit_id': 'P1', 'anchor': 'page 1, action', 'excerpt': 'Ravi returns wearing the same shirt, now stained with blood.'}]
    palette = [{'name': 'Deep blue', 'hex': '#244960', 'role': 'shirt', 'basis': 'proposed', 'rationale': 'Synthetic test palette.'}]
    scenes = [{'id': sid, 'printed_number': n, 'slugline': 'INT. HOUSE - DAY', 'source_unit_ids': ['P1'], 'story_day': '1',
               'on_screen_character_ids': ['C1'], 'non_visual_character_ids': ['C2'], 'costume_assessed': True,
               'palette': copy.deepcopy(palette), 'coordination_notes': 'Blue wardrobe against a proposed warm neutral set.'}
              for sid, n in [('SC-001', '1'), ('SC-004', '4')]]
    assets = [{'id': aid, 'path': 'test.png', 'kind': kind, 'subject_id': subject, 'caption': 'SYNTHETIC TEST ART',
               'review_status': 'passed', 'is_placeholder': False}
              for aid, kind, subject in [('AS1', 'character_board', 'C1'), ('AS2', 'look_board', 'L1'), ('AS3', 'state_board', 'ST2')]]
    return {
        'schema_version': '1.0', 'film': {'title': 'Synthetic layout — రవి', 'revision': 'test', 'design_status': 'proposed'},
        'source': {'filename': 'test.txt', 'sha256': hashlib.sha256(b'synthetic fixture').hexdigest(), 'scene_inventory_complete': True,
                   'units': [{'id': 'P1', 'locator': 'page 1', 'readable': True, 'reviewed': True}], 'warnings': []},
        'film_palette': palette,
        'characters': [{'id': 'C1', 'name': 'రవి / Ravi', 'kind': 'individual', 'identity_notes': 'Fictional layout fixture.', 'reference_notes': 'No actor reference.', 'identity_asset_id': 'AS1'},
                       {'id': 'C2', 'name': 'Voice only', 'kind': 'individual', 'identity_notes': 'Voice heard from another room.', 'reference_notes': '', 'identity_asset_id': None}],
        'scenes': scenes,
        'looks': [{'id': 'L1', 'character_id': 'C1', 'name': 'Blue shirt and jeans', 'basis': 'proposed', 'evidence': [], 'rationale': 'Layout test.',
                   'garments': [{'item': 'Shirt', 'description': 'Long-sleeved shirt', 'material': 'Cotton', 'colour': 'Blue', 'fit': 'Regular', 'details': 'Collar and buttons.'}],
                   'palette': copy.deepcopy(palette), 'design_notes': 'Test-only garment specification.', 'look_asset_id': 'AS2'}],
        'states': [{'id': 'ST1', 'look_id': 'L1', 'name': 'Clean', 'condition_notes': 'Clean and dry.', 'basis': 'proposed', 'evidence': [], 'rationale': 'Initial proposed condition.', 'requires_distinct_visual': False, 'state_asset_id': None},
                   {'id': 'ST2', 'look_id': 'L1', 'name': 'Blood stain', 'condition_notes': 'Wearer-left upper chest, front panel.', 'basis': 'explicit', 'evidence': copy.deepcopy(evidence), 'rationale': None,
                    'requires_distinct_visual': True, 'state_asset_id': 'AS3', 'parent_state_id': 'ST1'}],
        'appearances': [{'id': aid, 'scene_id': sid, 'character_id': 'C1', 'beat': 'whole scene', 'look_id': 'L1', 'state_id': st,
                         'basis': 'inferred', 'evidence': copy.deepcopy(evidence), 'rationale': 'Script states a repeat shirt.', 'continuity_note': note, 'hair_makeup_notes': 'Same hair parting.'}
                        for aid, sid, st, note in [('AP1', 'SC-001', 'ST1', 'Clean base state.'), ('AP4', 'SC-004', 'ST2', 'Same costume as Scene 1; blood added.')]],
        'continuity': [{'id': 'CT1', 'from_appearance_id': 'AP1', 'to_appearance_id': 'AP4', 'relation': 'progression', 'match_notes': 'Same shirt and jeans; add wearer-left chest stain.',
                        'basis': 'explicit', 'evidence': copy.deepcopy(evidence), 'rationale': None}],
        'assets': assets, 'questions': []}


class BibleTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='costume-skill-test-')
        self.root = Path(self.tmp.name)
        self.data = fixture(self.root)

    def tearDown(self):
        self.tmp.cleanup()

    def invalid(self, mutation):
        mutation(self.data)
        with self.assertRaises(book.InvalidBible):
            book.validate(self.data, self.root)

    def test_full_coverage_excludes_voice_only_boards(self):
        result = book.validate(self.data, self.root)
        self.assertTrue(result['complete'])
        self.assertEqual(result['characters'], 1)

    def test_unread_page_stays_partial(self):
        self.data['source']['units'].append({'id': 'P2', 'locator': 'page 2', 'readable': False, 'reviewed': False})
        self.assertFalse(book.validate(self.data, self.root)['complete'])

    def test_unconfirmed_inventory_stays_partial(self):
        self.data['source']['scene_inventory_complete'] = False
        self.assertFalse(book.validate(self.data, self.root)['complete'])

    def test_missing_appearance_stays_partial(self):
        self.data['appearances'].pop()
        self.data['continuity'] = []
        self.assertFalse(book.validate(self.data, self.root)['complete'])

    def test_missing_continuity_link_stays_partial(self):
        self.data['continuity'] = []
        self.assertFalse(book.validate(self.data, self.root)['complete'])

    def test_exact_repeat_reuses_look_and_state(self):
        self.data['appearances'][1]['state_id'] = 'ST1'
        self.data['continuity'][0]['relation'] = 'same_state'
        self.assertTrue(book.validate(self.data, self.root)['complete'])

    def test_within_scene_state_change_is_covered(self):
        self.data['appearances'][1].update(scene_id='SC-001', beat='after injury')
        self.data['scenes'][1]['on_screen_character_ids'] = []
        self.data['scenes'][1]['non_visual_character_ids'].append('C1')
        self.assertTrue(book.validate(self.data, self.root)['complete'])

    def test_pending_art_stays_partial(self):
        self.data['assets'][0]['review_status'] = 'pending'
        self.assertFalse(book.validate(self.data, self.root)['complete'])

    def test_placeholder_art_stays_partial(self):
        self.data['assets'][0]['is_placeholder'] = True
        self.assertFalse(book.validate(self.data, self.root)['complete'])

    def test_missing_state_visual_stays_partial(self):
        self.data['states'][1]['state_asset_id'] = None
        self.assertFalse(book.validate(self.data, self.root)['complete'])

    def test_missing_file_stays_partial(self):
        self.data['assets'][0]['path'] = 'missing.png'
        self.assertFalse(book.validate(self.data, self.root)['complete'])

    def test_voice_only_cannot_have_visual_assignment(self):
        self.invalid(lambda d: d['appearances'][0].update(character_id='C2'))

    def test_exact_repeat_cannot_change_state(self):
        self.invalid(lambda d: d['continuity'][0].update(relation='same_state'))

    def test_state_must_belong_to_look(self):
        self.invalid(lambda d: d['states'][0].update(look_id='MISSING'))

    def test_duplicate_appearance_beats_rejected(self):
        self.invalid(lambda d: d['appearances'].append({**copy.deepcopy(d['appearances'][0]), 'id': 'AP2'}))

    def test_state_cycles_rejected(self):
        self.invalid(lambda d: d['states'][0].update(parent_state_id='ST2'))

    def test_unknown_evidence_rejected(self):
        self.invalid(lambda d: d['appearances'][0]['evidence'][0].update(unit_id='MISSING'))

    def test_missing_inference_rationale_rejected(self):
        self.invalid(lambda d: d['appearances'][0].update(rationale=None))

    def test_path_escape_rejected(self):
        self.invalid(lambda d: d['assets'][0].update(path='../outside.png'))

    def test_remote_asset_rejected(self):
        self.invalid(lambda d: d['assets'][0].update(path='https://example.com/image.png'))

    def test_invalid_colour_rejected(self):
        self.invalid(lambda d: d['film_palette'][0].update(hex='red;display:none'))

    def test_wrong_file_signature_rejected(self):
        (self.root / 'test.png').write_text('not an image')
        with self.assertRaises(book.InvalidBible):
            book.validate(self.data, self.root)

    def test_exports_preserve_links_and_escape_input(self):
        self.data['characters'][0]['name'] = '<script>alert(1)</script>రవి'
        self.data['appearances'][0]['continuity_note'] = '=1+1'
        out = self.root / 'book'
        book.build(self.data, self.root, out, book.validate(self.data, self.root))
        page = (out / 'costume-bible.html').read_text()
        self.assertNotIn('<script>alert', page)
        self.assertIn('రవి', page)
        self.assertIn('href="#AP1"', page)
        self.assertNotIn('Visual reference pending', page)  # voice-only character needs no board
        with (out / 'scene-costume-matrix.csv').open(encoding='utf-8-sig') as stream:
            rows = list(csv.DictReader(stream))
        self.assertEqual(rows[0]['continuity_note'], "'=1+1")
        self.assertEqual(rows[1]['state_id'], 'ST2')
        self.assertEqual(len(list((out / 'assets').iterdir())), 3)
        json.loads((out / 'coverage.json').read_text())


if __name__ == '__main__':
    unittest.main()
