import * as THREE from 'three';

const UNIT_FACTORS = Object.freeze({ mm: 0.001, cm: 0.01, m: 1, in: 0.0254, ft: 0.3048 });
const PART_TYPES = new Set(['box', 'cylinder', 'sphere', 'tube', 'extrude']);
const MAYA_SAFE_NAME = /^[A-Za-z_][A-Za-z0-9_]*$/;

export function toMeters(value, unit) {
  return Number.isFinite(value) && UNIT_FACTORS[unit] ? value * UNIT_FACTORS[unit] : null;
}

function isVector(value, length) {
  return Array.isArray(value) && value.length === length && value.every(Number.isFinite);
}

function positive(value) {
  return Number.isFinite(value) && value > 0;
}

export function validateSceneSpec(spec) {
  const errors = [];
  const warnings = [];
  if (!spec || typeof spec !== 'object' || Array.isArray(spec)) {
    return { errors: ['Scene specification must be a JSON object.'], warnings };
  }
  if (spec.schemaVersion !== 1) errors.push('schemaVersion must be 1.');
  if (!UNIT_FACTORS[spec.units]) errors.push('units must be one of mm, cm, m, in, or ft.');
  if (!Array.isArray(spec.parts) || spec.parts.length === 0) errors.push('parts must contain at least one part.');
  const partDefinitions = Array.isArray(spec.parts) ? spec.parts : [];

  const materials = spec.materials && typeof spec.materials === 'object' ? spec.materials : {};
  const anchors = spec.anchors && typeof spec.anchors === 'object' ? spec.anchors : {};
  for (const [name, point] of Object.entries(anchors)) {
    if (!isVector(point, 3)) errors.push(`Anchor ${name} must be a three-number array.`);
  }

  const names = new Set();
  for (const [index, part] of partDefinitions.entries()) {
    const prefix = `parts[${index}]`;
    if (!part || typeof part !== 'object') {
      errors.push(`${prefix} must be an object.`);
      continue;
    }
    if (typeof part.name !== 'string' || !part.name.trim()) errors.push(`${prefix}.name is required.`);
    else if (!MAYA_SAFE_NAME.test(part.name)) errors.push(`${prefix}.name must be a Maya-safe identifier using letters, numbers, and underscores.`);
    else if (names.has(part.name)) errors.push(`Part name ${part.name} is duplicated.`);
    else names.add(part.name);
    if (!PART_TYPES.has(part.type)) errors.push(`${prefix}.type must be box, cylinder, sphere, tube, or extrude.`);
    if (part.position !== undefined && !isVector(part.position, 3)) errors.push(`${prefix}.position must be a three-number array.`);
    if (part.rotation !== undefined && !isVector(part.rotation, 3)) errors.push(`${prefix}.rotation must be a three-number array in degrees.`);
    if (part.scale !== undefined && (!isVector(part.scale, 3) || part.scale.some((value) => value <= 0))) errors.push(`${prefix}.scale must contain three positive numbers.`);
    if (part.material && !Object.hasOwn(materials, part.material)) errors.push(`${prefix}.material references undefined material ${part.material}.`);

    if (part.type === 'box' && (!isVector(part.size, 3) || part.size.some((value) => value <= 0))) errors.push(`${prefix}.size must contain three positive numbers.`);
    if (part.type === 'cylinder' && (!positive(part.radius) || !positive(part.height))) errors.push(`${prefix} cylinder requires positive radius and height.`);
    if (part.type === 'sphere' && !positive(part.radius)) errors.push(`${prefix} sphere requires a positive radius.`);
    if (part.type === 'tube') {
      if (!Array.isArray(part.path) || part.path.length < 2 || !part.path.every((point) => isVector(point, 3))) errors.push(`${prefix}.path must contain at least two three-number points.`);
      if (!positive(part.radius)) errors.push(`${prefix} tube requires a positive radius.`);
      if (part.startAnchor && !Object.hasOwn(anchors, part.startAnchor)) errors.push(`${prefix}.startAnchor references undefined anchor ${part.startAnchor}.`);
      if (part.endAnchor && !Object.hasOwn(anchors, part.endAnchor)) errors.push(`${prefix}.endAnchor references undefined anchor ${part.endAnchor}.`);
      if (!part.startAnchor || !part.endAnchor) warnings.push(`${part.name || prefix} has no complete endpoint-anchor constraint.`);
    }
    if (part.type === 'extrude') {
      if (!Array.isArray(part.profile) || part.profile.length < 3 || !part.profile.every((point) => isVector(point, 2))) errors.push(`${prefix}.profile must contain at least three two-number points.`);
      if (!positive(part.depth)) errors.push(`${prefix} extrude requires a positive depth.`);
    }
  }

  if (spec.connections !== undefined && !Array.isArray(spec.connections)) errors.push('connections must be an array.');
  for (const connection of Array.isArray(spec.connections) ? spec.connections : []) {
    if (!connection || typeof connection !== 'object') {
      errors.push('Each connection must be an object.');
      continue;
    }
    if (!names.has(connection.from)) errors.push(`Connection references unknown from part ${connection.from}.`);
    if (!names.has(connection.to)) errors.push(`Connection references unknown to part ${connection.to}.`);
    if (!Number.isFinite(connection.maxGap) || connection.maxGap < 0) errors.push(`Connection ${connection.from} → ${connection.to} requires a non-negative maxGap.`);
  }
  if (spec.symmetryPairs !== undefined && !Array.isArray(spec.symmetryPairs)) errors.push('symmetryPairs must be an array.');
  for (const pair of Array.isArray(spec.symmetryPairs) ? spec.symmetryPairs : []) {
    if (!pair || typeof pair !== 'object') {
      errors.push('Each symmetry pair must be an object.');
      continue;
    }
    if (!names.has(pair.left)) errors.push(`Symmetry pair references unknown left part ${pair.left}.`);
    if (!names.has(pair.right)) errors.push(`Symmetry pair references unknown right part ${pair.right}.`);
    if (!['X', 'Y', 'Z'].includes(pair.axis)) errors.push(`Symmetry pair ${pair.left} / ${pair.right} requires axis X, Y, or Z.`);
  }
  return { errors, warnings };
}

function materialFromDefinition(definition = {}) {
  return new THREE.MeshStandardMaterial({
    color: definition.color ?? '#a8b1bc',
    metalness: Number.isFinite(definition.metalness) ? definition.metalness : 0.05,
    roughness: Number.isFinite(definition.roughness) ? definition.roughness : 0.7,
  });
}

function makeGeometry(part, factor) {
  if (part.type === 'box') return new THREE.BoxGeometry(...part.size.map((value) => value * factor));
  if (part.type === 'cylinder') {
    return new THREE.CylinderGeometry(
      (part.radiusTop ?? part.radius) * factor,
      (part.radiusBottom ?? part.radius) * factor,
      part.height * factor,
      part.radialSegments ?? 24,
    );
  }
  if (part.type === 'sphere') return new THREE.SphereGeometry(part.radius * factor, part.widthSegments ?? 24, part.heightSegments ?? 16);
  if (part.type === 'tube') {
    const points = part.path.map((point) => new THREE.Vector3(...point.map((value) => value * factor)));
    const curve = new THREE.CatmullRomCurve3(points, Boolean(part.closed), part.curveType ?? 'centripetal', part.tension ?? 0.5);
    return new THREE.TubeGeometry(curve, part.tubularSegments ?? 48, part.radius * factor, part.radialSegments ?? 8, Boolean(part.closed));
  }
  const shape = new THREE.Shape();
  part.profile.forEach(([x, y], index) => {
    const method = index === 0 ? 'moveTo' : 'lineTo';
    shape[method](x * factor, y * factor);
  });
  shape.closePath();
  const geometry = new THREE.ExtrudeGeometry(shape, {
    depth: part.depth * factor,
    bevelEnabled: Boolean(part.bevel?.enabled),
    bevelSize: (part.bevel?.size ?? 0) * factor,
    bevelThickness: (part.bevel?.thickness ?? 0) * factor,
    bevelSegments: part.bevel?.segments ?? 1,
    curveSegments: part.curveSegments ?? 12,
  });
  geometry.translate(0, 0, -(part.depth * factor) / 2);
  return geometry;
}

export function buildBlockout(spec) {
  const validation = validateSceneSpec(spec);
  if (validation.errors.length) throw new Error(validation.errors.join('\n'));
  const factor = UNIT_FACTORS[spec.units];
  const root = new THREE.Group();
  root.name = spec.name || 'BLOCKOUT_ROOT';
  root.userData.sceneSpec = { schemaVersion: spec.schemaVersion, units: spec.units };
  const materials = new Map(Object.entries(spec.materials ?? {}).map(([name, definition]) => [name, materialFromDefinition(definition)]));
  const fallbackMaterial = materialFromDefinition();

  for (const part of spec.parts) {
    const mesh = new THREE.Mesh(makeGeometry(part, factor), materials.get(part.material) ?? fallbackMaterial);
    mesh.name = part.name;
    mesh.position.fromArray((part.position ?? [0, 0, 0]).map((value) => value * factor));
    mesh.rotation.set(...(part.rotation ?? [0, 0, 0]).map(THREE.MathUtils.degToRad));
    mesh.scale.fromArray(part.scale ?? [1, 1, 1]);
    mesh.castShadow = true;
    mesh.receiveShadow = true;
    mesh.userData.specType = part.type;
    if (part.type === 'tube') mesh.userData.localPathMeters = part.path.map((point) => point.map((value) => value * factor));
    root.add(mesh);
  }
  root.updateMatrixWorld(true);
  return root;
}

function boxGap(first, second) {
  const deltas = ['x', 'y', 'z'].map((axis) => Math.max(0, second.min[axis] - first.max[axis], first.min[axis] - second.max[axis]));
  return Math.hypot(...deltas);
}

function toleranceMeters(spec, dimensionSpec, key, fallback) {
  const dimensionTolerance = toMeters(dimensionSpec?.tolerance?.absolute, dimensionSpec?.tolerance?.unit ?? dimensionSpec?.units?.source);
  return toMeters(spec.validation?.[key], spec.units) ?? dimensionTolerance ?? fallback;
}

function result(severity, code, message, parts = []) {
  return { severity, code, message, parts };
}

export function evaluateBlockout(root, spec, dimensionSpec = null) {
  root.updateMatrixWorld(true);
  const results = [];
  const parts = new Map();
  root.traverse((object) => {
    if (object.isMesh && object.name) parts.set(object.name, object);
  });

  const required = new Set([
    ...spec.parts.filter((part) => part.required).map((part) => part.name),
    ...(Array.isArray(dimensionSpec?.requiredParts) ? dimensionSpec.requiredParts : []),
  ]);
  const missing = [...required].filter((name) => !parts.has(name));
  results.push(missing.length
    ? result('error', 'required-parts', `Missing required parts: ${missing.join(', ')}`, missing)
    : result('pass', 'required-parts', `All ${required.size} required parts are present.`));

  const anchorTolerance = toleranceMeters(spec, dimensionSpec, 'anchorTolerance', 0.005);
  for (const part of spec.parts.filter((candidate) => candidate.type === 'tube')) {
    const mesh = parts.get(part.name);
    if (!mesh) continue;
    const bindings = [
      ['start', part.startAnchor, mesh.userData.localPathMeters?.[0]],
      ['end', part.endAnchor, mesh.userData.localPathMeters?.at(-1)],
    ];
    for (const [endpoint, anchorName, localPoint] of bindings) {
      if (!anchorName) continue;
      const expected = new THREE.Vector3(...spec.anchors[anchorName].map((value) => value * UNIT_FACTORS[spec.units]));
      const distance = localPoint
        ? mesh.localToWorld(new THREE.Vector3(...localPoint)).distanceTo(expected)
        : new THREE.Box3().setFromObject(mesh).distanceToPoint(expected);
      results.push(distance <= anchorTolerance
        ? result('pass', 'anchor', `${part.name} ${endpoint} reaches ${anchorName}.`, [part.name])
        : result('error', 'anchor', `${part.name} geometry is ${(distance * 1000).toFixed(1)} mm from ${anchorName} at its ${endpoint} constraint.`, [part.name]));
    }
  }

  for (const connection of spec.connections ?? []) {
    const first = parts.get(connection.from);
    const second = parts.get(connection.to);
    if (!first || !second) continue;
    const gap = boxGap(new THREE.Box3().setFromObject(first), new THREE.Box3().setFromObject(second));
    const allowed = toMeters(connection.maxGap, spec.units) ?? toleranceMeters(spec, dimensionSpec, 'connectionTolerance', 0.005);
    results.push(gap <= allowed
      ? result('pass', 'connection', `${connection.from} connects to ${connection.to}.`, [connection.from, connection.to])
      : result('error', 'connection', `${connection.from} is ${(gap * 1000).toFixed(1)} mm from ${connection.to}; allowed gap is ${(allowed * 1000).toFixed(1)} mm.`, [connection.from, connection.to]));
  }

  for (const pair of spec.symmetryPairs ?? []) {
    const left = parts.get(pair.left);
    const right = parts.get(pair.right);
    if (!left || !right) continue;
    const leftCenter = new THREE.Box3().setFromObject(left).getCenter(new THREE.Vector3());
    const rightCenter = new THREE.Box3().setFromObject(right).getCenter(new THREE.Vector3());
    const axis = pair.axis.toLowerCase();
    rightCenter[axis] *= -1;
    const deviation = leftCenter.distanceTo(rightCenter);
    const allowed = toMeters(pair.tolerance, spec.units) ?? toleranceMeters(spec, dimensionSpec, 'anchorTolerance', 0.005);
    results.push(deviation <= allowed
      ? result('pass', 'symmetry', `${pair.left} and ${pair.right} satisfy ${pair.axis}-axis symmetry.`, [pair.left, pair.right])
      : result('error', 'symmetry', `${pair.left} and ${pair.right} differ by ${(deviation * 1000).toFixed(1)} mm after mirroring.`, [pair.left, pair.right]));
  }

  const bounds = new THREE.Box3().setFromObject(root).getSize(new THREE.Vector3());
  const sourceUnit = dimensionSpec?.units?.source;
  const expected = [dimensionSpec?.overall?.width, dimensionSpec?.overall?.height, dimensionSpec?.overall?.depth].map((value) => toMeters(value, sourceUnit));
  const relativeTolerance = Number.isFinite(dimensionSpec?.tolerance?.relativePercent) ? dimensionSpec.tolerance.relativePercent : 1;
  const absoluteTolerance = toleranceMeters(spec, dimensionSpec, 'dimensionTolerance', 0.005);
  ['width', 'height', 'depth'].forEach((label, index) => {
    if (expected[index] === null) return;
    const delta = Math.abs(bounds.toArray()[index] - expected[index]);
    const percent = expected[index] === 0 ? 0 : (delta / expected[index]) * 100;
    results.push(delta <= absoluteTolerance || percent <= relativeTolerance
      ? result('pass', 'dimension', `${label} is within tolerance.`)
      : result('error', 'dimension', `${label} differs by ${(delta * 1000).toFixed(1)} mm (${percent.toFixed(1)}%).`));
  });

  return results;
}
