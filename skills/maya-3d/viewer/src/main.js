import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { GLTFExporter } from 'three/addons/exporters/GLTFExporter.js';
import { buildBlockout, evaluateBlockout, toMeters, validateSceneSpec } from './scene-spec.js';
import './style.css';

const viewport = document.querySelector('#viewport');
const statusElement = document.querySelector('#status');
const partsElement = document.querySelector('#parts');
const partCountElement = document.querySelector('#part-count');
const metricsElement = document.querySelector('#metrics');
const dimensionResults = document.querySelector('#dimension-results');
const referenceOverlay = document.querySelector('#reference-overlay');
const dropHint = document.querySelector('#drop-hint');
const selectionElement = document.querySelector('#selection');
const validationElement = document.querySelector('#validation-results');
const validationCountElement = document.querySelector('#validation-count');
const exportBlockoutButton = document.querySelector('#export-blockout');

const scene = new THREE.Scene();
scene.background = new THREE.Color(0x101317);

const camera = new THREE.PerspectiveCamera(45, 1, 0.01, 2000);
camera.position.set(4, 3, 6);

const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.1;
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFShadowMap;
viewport.prepend(renderer.domElement);

const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.dampingFactor = 0.06;

scene.add(new THREE.HemisphereLight(0xd8e8ff, 0x27303a, 2.2));
const keyLight = new THREE.DirectionalLight(0xffffff, 3.2);
keyLight.position.set(5, 8, 6);
keyLight.castShadow = true;
scene.add(keyLight);

const grid = new THREE.GridHelper(20, 40, 0x58606a, 0x2d333b);
scene.add(grid);

const loader = new GLTFLoader();
const exporter = new GLTFExporter();
const raycaster = new THREE.Raycaster();
const pointer = new THREE.Vector2();
const selectionBox = new THREE.Box3Helper(new THREE.Box3(), 0xffcc5c);
selectionBox.visible = false;
scene.add(selectionBox);

let modelRoot = null;
let dimensionSpec = null;
let sceneSpec = null;
let modelIsBlockout = false;
let wireframeEnabled = false;
let edgesEnabled = false;
let autoRotateEnabled = false;
let referenceUrl = null;

function setStatus(message, tone = 'neutral') {
  statusElement.textContent = message;
  statusElement.dataset.tone = tone;
}

function disposeObject(root) {
  root.traverse((object) => {
    object.geometry?.dispose();
    const materials = Array.isArray(object.material) ? object.material : [object.material];
    for (const material of materials) {
      if (!material) continue;
      for (const value of Object.values(material)) {
        if (value?.isTexture) value.dispose();
      }
      material.dispose?.();
    }
  });
}

function clearModel() {
  if (!modelRoot) return;
  scene.remove(modelRoot);
  disposeObject(modelRoot);
  modelRoot = null;
  selectionBox.visible = false;
  selectionElement.textContent = 'Nothing selected';
  exportBlockoutButton.disabled = true;
  modelIsBlockout = false;
}

function fitCamera() {
  if (!modelRoot) return;
  const bounds = new THREE.Box3().setFromObject(modelRoot);
  if (bounds.isEmpty()) return;
  const size = bounds.getSize(new THREE.Vector3());
  const center = bounds.getCenter(new THREE.Vector3());
  const maxDimension = Math.max(size.x, size.y, size.z);
  const distance = maxDimension / (2 * Math.tan(THREE.MathUtils.degToRad(camera.fov / 2)));
  camera.position.copy(center).add(new THREE.Vector3(1, 0.7, 1).normalize().multiplyScalar(distance * 1.7));
  camera.near = Math.max(maxDimension / 1000, 0.001);
  camera.far = Math.max(maxDimension * 100, 100);
  camera.updateProjectionMatrix();
  controls.target.copy(center);
  controls.update();
}

function formatMeters(value) {
  if (!Number.isFinite(value)) return '—';
  if (value < 0.01) return `${(value * 1000).toFixed(1)} mm`;
  if (value < 1) return `${(value * 100).toFixed(1)} cm`;
  return `${value.toFixed(3)} m`;
}

function measuredBounds() {
  if (!modelRoot) return null;
  const box = new THREE.Box3().setFromObject(modelRoot);
  return box.isEmpty() ? null : box.getSize(new THREE.Vector3());
}

function updateMetrics() {
  const size = measuredBounds();
  const values = size ? [size.x, size.y, size.z] : [null, null, null];
  [...metricsElement.querySelectorAll('dd')].forEach((element, index) => {
    element.textContent = formatMeters(values[index]);
  });
  compareDimensionSpec(size);
}

function compareDimensionSpec(size = measuredBounds()) {
  if (!dimensionSpec || !size) {
    dimensionResults.textContent = 'Load a dimension specification to compare expected and actual size.';
    dimensionResults.className = 'results muted';
    return;
  }
  const sourceUnit = dimensionSpec.units?.source ?? 'cm';
  const expected = {
    width: toMeters(dimensionSpec.overall?.width, sourceUnit),
    height: toMeters(dimensionSpec.overall?.height, sourceUnit),
    depth: toMeters(dimensionSpec.overall?.depth, sourceUnit),
  };
  const actual = { width: size.x, height: size.y, depth: size.z };
  const tolerancePercent = Number.isFinite(dimensionSpec.tolerance?.relativePercent)
    ? dimensionSpec.tolerance.relativePercent
    : 1;
  const toleranceAbsolute = toMeters(
    dimensionSpec.tolerance?.absolute,
    dimensionSpec.tolerance?.unit ?? sourceUnit,
  ) ?? 0;
  const rows = Object.entries(expected)
    .filter(([, value]) => value !== null)
    .map(([axis, value]) => {
      const delta = actual[axis] - value;
      const percent = value === 0 ? 0 : (delta / value) * 100;
      const row = document.createElement('div');
      const label = document.createElement('strong');
      const values = document.createElement('span');
      const result = document.createElement('em');
      const passes = Math.abs(delta) <= toleranceAbsolute || Math.abs(percent) <= tolerancePercent;
      label.textContent = axis;
      values.textContent = `${formatMeters(actual[axis])} / ${formatMeters(value)}`;
      result.className = passes ? 'pass' : 'warn';
      result.textContent = `${percent >= 0 ? '+' : ''}${percent.toFixed(1)}%`;
      row.append(label, values, result);
      return row;
    });

  const names = new Set();
  modelRoot.traverse((object) => names.add(object.name));
  const required = Array.isArray(dimensionSpec.requiredParts) ? dimensionSpec.requiredParts : [];
  const missing = required.filter((name) => !names.has(name));
  if (missing.length) {
    const row = document.createElement('div');
    row.className = 'missing';
    const label = document.createElement('strong');
    const values = document.createElement('span');
    label.textContent = 'Missing parts';
    values.textContent = missing.join(', ');
    row.append(label, values);
    rows.push(row);
  }
  if (!rows.length) {
    const row = document.createElement('div');
    row.textContent = 'No overall dimensions or required parts are defined.';
    rows.push(row);
  }
  dimensionResults.replaceChildren(...rows);
  dimensionResults.className = 'results';
}

function renderValidation(preflight = null) {
  validationElement.replaceChildren();
  if (!sceneSpec || !modelRoot) {
    validationElement.textContent = 'Load a scene specification and generate or load a model.';
    validationElement.className = 'validation muted';
    validationCountElement.textContent = '0';
    return;
  }
  const specValidation = preflight ?? validateSceneSpec(sceneSpec);
  const results = [
    ...specValidation.warnings.map((message) => ({ severity: 'warning', code: 'spec-warning', message })),
    ...evaluateBlockout(modelRoot, sceneSpec, dimensionSpec),
  ];
  for (const item of results) {
    const row = document.createElement('div');
    row.className = `validation-row ${item.severity}`;
    const marker = document.createElement('span');
    marker.textContent = item.severity === 'pass' ? 'PASS' : item.severity === 'warning' ? 'CHECK' : 'FAIL';
    const message = document.createElement('p');
    message.textContent = item.message;
    row.append(marker, message);
    validationElement.append(row);
  }
  const failures = results.filter((item) => item.severity === 'error').length;
  validationCountElement.textContent = failures ? `${failures} fail` : 'pass';
  validationCountElement.dataset.tone = failures ? 'error' : 'success';
  validationElement.className = 'validation';
}

function applyWireframe() {
  if (!modelRoot) return;
  modelRoot.traverse((object) => {
    if (!object.isMesh) return;
    const materials = Array.isArray(object.material) ? object.material : [object.material];
    materials.forEach((material) => {
      material.wireframe = wireframeEnabled;
      material.needsUpdate = true;
    });
  });
}

function applyEdges() {
  if (!modelRoot) return;
  const meshes = [];
  modelRoot.traverse((object) => {
    if (object.isMesh) meshes.push(object);
  });
  for (const mesh of meshes) {
    let lines = mesh.userData.__reviewEdges;
    if (!lines) {
      lines = new THREE.LineSegments(
        new THREE.EdgesGeometry(mesh.geometry, 35),
        new THREE.LineBasicMaterial({ color: 0x111111, transparent: true, opacity: 0.8 }),
      );
      lines.name = '__review_edges';
      lines.raycast = () => {};
      mesh.add(lines);
      mesh.userData.__reviewEdges = lines;
    }
    lines.visible = edgesEnabled;
  }
}

function selectObject(object) {
  if (!object) {
    selectionBox.visible = false;
    selectionElement.textContent = 'Nothing selected';
    return;
  }
  selectionBox.box.setFromObject(object);
  selectionBox.visible = true;
  selectionElement.textContent = object.name || '(unnamed mesh)';
}

function buildPartTree() {
  partsElement.replaceChildren();
  if (!modelRoot) {
    partsElement.textContent = 'No model loaded.';
    partsElement.className = 'parts muted';
    partCountElement.textContent = '0';
    return;
  }
  const objects = [];
  modelRoot.traverse((object) => {
    if ((object.isMesh || object.isGroup) && object.name && object.name !== '__review_edges') objects.push(object);
  });
  partCountElement.textContent = String(objects.length);
  partsElement.className = 'parts';
  for (const object of objects) {
    const row = document.createElement('div');
    row.className = 'part-row';
    const toggle = document.createElement('input');
    toggle.type = 'checkbox';
    toggle.checked = object.visible;
    toggle.title = `Show or hide ${object.name}`;
    toggle.addEventListener('change', () => {
      object.visible = toggle.checked;
      updateMetrics();
    });
    const button = document.createElement('button');
    button.type = 'button';
    button.textContent = object.name;
    button.title = `Select ${object.name}`;
    button.addEventListener('click', () => selectObject(object));
    row.append(toggle, button);
    partsElement.append(row);
  }
}

function acceptScene(root, label, { blockout = false } = {}) {
  clearModel();
  modelRoot = root;
  modelRoot.name ||= 'GLB_ROOT';
  modelRoot.traverse((object) => {
    if (object.isMesh) {
      object.castShadow = true;
      object.receiveShadow = true;
    }
  });
  scene.add(modelRoot);
  applyWireframe();
  applyEdges();
  buildPartTree();
  fitCamera();
  updateMetrics();
  renderValidation();
  dropHint.hidden = true;
  modelIsBlockout = blockout;
  exportBlockoutButton.disabled = !blockout;
  setStatus(`${label} loaded`, 'success');
}

function acceptModel(gltf, label) {
  acceptScene(gltf.scene, label);
}

function generateBlockout(spec, label = 'Scene specification') {
  const validation = validateSceneSpec(spec);
  if (validation.errors.length) {
    sceneSpec = null;
    clearModel();
    validationElement.replaceChildren();
    for (const message of validation.errors) {
      const row = document.createElement('div');
      row.className = 'validation-row error';
      const marker = document.createElement('span');
      marker.textContent = 'FAIL';
      const text = document.createElement('p');
      text.textContent = message;
      row.append(marker, text);
      validationElement.append(row);
    }
    validationElement.className = 'validation';
    validationCountElement.textContent = `${validation.errors.length} fail`;
    validationCountElement.dataset.tone = 'error';
    setStatus('Scene specification has validation errors.', 'error');
    return;
  }
  sceneSpec = spec;
  acceptScene(buildBlockout(spec), `${label} blockout`, { blockout: true });
  renderValidation(validation);
}

function loadUrl(url) {
  if (!url) return;
  setStatus('Loading model…');
  loader.load(url, (gltf) => acceptModel(gltf, url.split('/').pop() || 'Model'), undefined, (error) => {
    console.error(error);
    setStatus('Could not load that model URL.', 'error');
  });
}

function loadGlbFile(file) {
  if (!file?.name.toLowerCase().endsWith('.glb')) {
    setStatus('Choose a self-contained .glb file.', 'error');
    return;
  }
  setStatus('Reading GLB…');
  file.arrayBuffer()
    .then((buffer) => loader.parseAsync(buffer, ''))
    .then((gltf) => acceptModel(gltf, file.name))
    .catch((error) => {
      console.error(error);
      setStatus('The GLB could not be parsed.', 'error');
    });
}

document.querySelector('#model-file').addEventListener('change', (event) => loadGlbFile(event.target.files[0]));
document.querySelector('#load-url').addEventListener('click', () => loadUrl(document.querySelector('#model-url').value.trim()));
document.querySelector('#model-url').addEventListener('keydown', (event) => {
  if (event.key === 'Enter') loadUrl(event.currentTarget.value.trim());
});

document.querySelector('#scene-spec-file').addEventListener('change', async (event) => {
  const [file] = event.target.files;
  if (!file) return;
  try {
    generateBlockout(JSON.parse(await file.text()), file.name);
  } catch (error) {
    console.error(error);
    setStatus('Scene specification is not valid JSON.', 'error');
  }
});

document.querySelector('#dimension-file').addEventListener('change', async (event) => {
  const [file] = event.target.files;
  if (!file) return;
  try {
    dimensionSpec = JSON.parse(await file.text());
    compareDimensionSpec();
    renderValidation();
    setStatus('Dimension specification loaded', 'success');
  } catch (error) {
    console.error(error);
    setStatus('Dimension specification is not valid JSON.', 'error');
  }
});

exportBlockoutButton.addEventListener('click', async () => {
  if (!modelRoot || !modelIsBlockout) return;
  const visibility = [];
  modelRoot.traverse((object) => {
    visibility.push([object, object.visible]);
    object.visible = object.name !== '__review_edges';
  });
  try {
    const data = await exporter.parseAsync(modelRoot, { binary: true, onlyVisible: true });
    if (!(data instanceof ArrayBuffer) || data.byteLength === 0) throw new Error('GLB exporter returned no binary data.');
    const blob = new Blob([data], { type: 'model/gltf-binary' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `${sceneSpec?.name || 'blockout'}.glb`;
    document.body.append(link);
    link.click();
    link.remove();
    window.setTimeout(() => URL.revokeObjectURL(url), 1000);
    setStatus(`Blockout GLB exported for Maya handoff (${(data.byteLength / 1024).toFixed(1)} kB).`, 'success');
  } catch (error) {
    console.error(error);
    setStatus('Blockout GLB export failed.', 'error');
  } finally {
    for (const [object, visible] of visibility) object.visible = visible;
  }
});

document.querySelector('#reference-file').addEventListener('change', (event) => {
  const [file] = event.target.files;
  if (!file) return;
  if (referenceUrl) URL.revokeObjectURL(referenceUrl);
  referenceUrl = URL.createObjectURL(file);
  referenceOverlay.src = referenceUrl;
  referenceOverlay.hidden = false;
});

document.querySelector('#reference-opacity').addEventListener('input', (event) => {
  const value = Number(event.target.value);
  referenceOverlay.style.opacity = String(value / 100);
  document.querySelector('#opacity-value').value = `${value}%`;
});

function toggleButton(id, onToggle) {
  const button = document.querySelector(id);
  button.addEventListener('click', () => {
    const active = button.getAttribute('aria-pressed') !== 'true';
    button.setAttribute('aria-pressed', String(active));
    onToggle(active);
  });
}

document.querySelector('#fit-view').addEventListener('click', fitCamera);
toggleButton('#toggle-wireframe', (active) => {
  wireframeEnabled = active;
  applyWireframe();
});
toggleButton('#toggle-edges', (active) => {
  edgesEnabled = active;
  applyEdges();
});
toggleButton('#toggle-grid', (active) => {
  grid.visible = active;
});
toggleButton('#toggle-rotate', (active) => {
  autoRotateEnabled = active;
});

for (const eventName of ['dragenter', 'dragover']) {
  viewport.addEventListener(eventName, (event) => {
    event.preventDefault();
    viewport.classList.add('dragging');
  });
}
for (const eventName of ['dragleave', 'drop']) {
  viewport.addEventListener(eventName, (event) => {
    event.preventDefault();
    viewport.classList.remove('dragging');
  });
}
viewport.addEventListener('drop', (event) => loadGlbFile(event.dataTransfer.files[0]));

renderer.domElement.addEventListener('pointerdown', (event) => {
  if (!modelRoot) return;
  const rect = renderer.domElement.getBoundingClientRect();
  pointer.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
  pointer.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;
  raycaster.setFromCamera(pointer, camera);
  const hit = raycaster.intersectObject(modelRoot, true).find((item) => item.object.isMesh);
  selectObject(hit?.object ?? null);
});

function resize() {
  const width = viewport.clientWidth;
  const height = viewport.clientHeight;
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.setSize(width, height, false);
  camera.aspect = width / height;
  camera.updateProjectionMatrix();
}
new ResizeObserver(resize).observe(viewport);
resize();

function animate() {
  controls.autoRotate = autoRotateEnabled;
  controls.update();
  if (selectionBox.visible && selectionBox.box.isEmpty()) selectionBox.visible = false;
  renderer.render(scene, camera);
}
renderer.setAnimationLoop(animate);
