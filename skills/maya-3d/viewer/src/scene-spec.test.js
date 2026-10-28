import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import test from 'node:test';
import { buildBlockout, evaluateBlockout, validateSceneSpec } from './scene-spec.js';

const templateUrl = new URL('../../assets/scene_spec_template.json', import.meta.url);
const template = JSON.parse(await readFile(templateUrl, 'utf8'));

test('template validates and builds every named part', () => {
  const validation = validateSceneSpec(template);
  assert.deepEqual(validation.errors, []);
  const root = buildBlockout(template);
  assert.equal(root.getObjectByName('BODY_MAIN').isMesh, true);
  assert.equal(root.getObjectByName('ROOF_CURVE').isMesh, true);
});

test('template satisfies required-part and endpoint-anchor checks', () => {
  const root = buildBlockout(template);
  const results = evaluateBlockout(root, template);
  assert.equal(results.some((item) => item.code === 'required-parts' && item.severity === 'pass'), true);
  assert.equal(results.filter((item) => item.code === 'anchor' && item.severity === 'pass').length, 2);
});

test('invalid part and missing anchor are rejected before generation', () => {
  const invalid = structuredClone(template);
  invalid.parts[0].type = 'unknown';
  invalid.parts[1].endAnchor = 'missing_anchor';
  const validation = validateSceneSpec(invalid);
  assert.equal(validation.errors.some((message) => message.includes('type must be')), true);
  assert.equal(validation.errors.some((message) => message.includes('undefined anchor')), true);
});
