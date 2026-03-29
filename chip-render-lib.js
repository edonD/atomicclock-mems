// ═══════════════════════════════════════════════════════════════════════════
//  ChipRender v1.0  —  nanotech product visualization engine
//  Shared library for all chip product renders.
//  Import into an HTML page that already has a three.js importmap.
// ═══════════════════════════════════════════════════════════════════════════
//
//  Usage:
//    import { initRenderer, initScene, initCamera, initLights,
//             initFloor, buildChip, addVignette, startLoop }
//      from './chip-render-lib.js';
//
//  Chip config shape:
//    {
//      dims:   { w, h, d, r }             — package size (1 unit = 10 mm)
//      case:   { color:[r,g,b], metalness, roughness }
//      camera: { pos:[x,y,z], target:[x,y,z] }
//      rotation: number                   — initial Y rotation (radians)
//      label: {
//        bg, stripColor, stripAccent, stripText,
//        company, bigName, model, descriptor,
//        specs: [{ sym, val }, ...]
//      }
//    }
// ═══════════════════════════════════════════════════════════════════════════

import * as THREE              from 'three';
import { OrbitControls }       from 'three/addons/controls/OrbitControls.js';
import { RoundedBoxGeometry }  from 'three/addons/geometries/RoundedBoxGeometry.js';

// ─── Renderer ────────────────────────────────────────────────────────────────
export function initRenderer(container = document.body) {
  const r = new THREE.WebGLRenderer({ antialias: true });
  r.setPixelRatio(Math.min(devicePixelRatio, 2));
  r.setSize(innerWidth, innerHeight);
  r.shadowMap.enabled   = true;
  r.shadowMap.type      = THREE.PCFSoftShadowMap;
  r.toneMapping         = THREE.ACESFilmicToneMapping;
  r.toneMappingExposure = 1.05;
  r.outputColorSpace    = THREE.SRGBColorSpace;
  container.appendChild(r.domElement);
  return r;
}

// ─── Scene: background gradient + neutral studio env map ─────────────────────
export function initScene(renderer) {
  const scene = new THREE.Scene();

  // Background
  const bgCv = document.createElement('canvas');
  bgCv.width = 2; bgCv.height = 256;
  const bc = bgCv.getContext('2d');
  const bgGr = bc.createLinearGradient(0, 0, 0, 256);
  bgGr.addColorStop(0,   '#1e2535');
  bgGr.addColorStop(0.5, '#141825');
  bgGr.addColorStop(1,   '#080b12');
  bc.fillStyle = bgGr; bc.fillRect(0, 0, 2, 256);
  scene.background = new THREE.CanvasTexture(bgCv);

  // Neutral studio env map (grey/white → correct steel reflections, no blue bleed)
  const envCv = document.createElement('canvas');
  envCv.width = 512; envCv.height = 256;
  const ec = envCv.getContext('2d');
  ec.fillStyle = '#707070'; ec.fillRect(0, 0, 512, 256);
  const etop = ec.createLinearGradient(0, 0, 0, 170);
  etop.addColorStop(0, '#e4e4e2'); etop.addColorStop(1, '#909090');
  ec.fillStyle = etop; ec.fillRect(0, 0, 512, 170);
  const ebot = ec.createLinearGradient(0, 170, 0, 256);
  ebot.addColorStop(0, '#303030'); ebot.addColorStop(1, '#080808');
  ec.fillStyle = ebot; ec.fillRect(0, 170, 512, 86);
  const ekl = ec.createRadialGradient(90, 45, 0, 90, 45, 150);
  ekl.addColorStop(0, 'rgba(255,253,248,1)'); ekl.addColorStop(1, 'rgba(255,253,248,0)');
  ec.fillStyle = ekl; ec.fillRect(0, 0, 512, 256);
  const efl = ec.createRadialGradient(440, 90, 0, 440, 90, 100);
  efl.addColorStop(0, 'rgba(210,225,255,0.5)'); efl.addColorStop(1, 'rgba(210,225,255,0)');
  ec.fillStyle = efl; ec.fillRect(0, 0, 512, 256);

  const envTex = new THREE.CanvasTexture(envCv);
  envTex.mapping    = THREE.EquirectangularReflectionMapping;
  envTex.colorSpace = THREE.SRGBColorSpace;
  const pm = new THREE.PMREMGenerator(renderer);
  pm.compileEquirectangularShader();
  scene.environment = pm.fromEquirectangular(envTex).texture;
  envTex.dispose(); pm.dispose();

  return scene;
}

// ─── Camera + OrbitControls ───────────────────────────────────────────────────
export function initCamera(renderer, cfg) {
  const cam = new THREE.PerspectiveCamera(30, innerWidth / innerHeight, 0.01, 100);
  cam.position.set(...cfg.camera.pos);
  cam.lookAt(...cfg.camera.target);

  const controls = new OrbitControls(cam, renderer.domElement);
  controls.enableDamping  = true;
  controls.dampingFactor  = 0.055;
  controls.target.set(...cfg.camera.target);
  controls.minDistance    = 1.2;
  controls.maxDistance    = 10;
  controls.maxPolarAngle  = Math.PI * 0.52;

  return { camera: cam, controls };
}

// ─── 5-light studio rig ───────────────────────────────────────────────────────
export function initLights(scene) {
  const key = new THREE.DirectionalLight(0xfff8f0, 2.5);
  key.position.set(-3, 6, 3);
  key.castShadow = true;
  key.shadow.mapSize.set(2048, 2048);
  key.shadow.camera.near   = 0.5;   key.shadow.camera.far   = 20;
  key.shadow.camera.left   = -2.5;  key.shadow.camera.right = 2.5;
  key.shadow.camera.top    = 2.5;   key.shadow.camera.bottom = -2.5;
  key.shadow.bias          = -0.0003;
  key.shadow.normalBias    = 0.012;
  scene.add(key);

  const fill = new THREE.DirectionalLight(0xd8e8ff, 1.0);
  fill.position.set(6, 2, -1);
  scene.add(fill);

  const front = new THREE.DirectionalLight(0xfff5e8, 0.8);
  front.position.set(1, 3, 6);
  scene.add(front);

  const rim = new THREE.DirectionalLight(0xffffff, 1.0);
  rim.position.set(0, 5, -5);
  scene.add(rim);

  const topL = new THREE.DirectionalLight(0xffffff, 0.8);
  topL.position.set(0, 10, 0);
  scene.add(topL);

  scene.add(new THREE.AmbientLight(0x253040, 3.5));
}

// ─── Floor + gloss reflection ─────────────────────────────────────────────────
export function initFloor(scene) {
  const floor = new THREE.Mesh(
    new THREE.PlaneGeometry(18, 18),
    new THREE.MeshStandardMaterial({ color: new THREE.Color(0.05, 0.06, 0.10), roughness: 0.88 })
  );
  floor.rotation.x = -Math.PI / 2;
  floor.receiveShadow = true;
  scene.add(floor);

  const gloss = new THREE.Mesh(
    new THREE.PlaneGeometry(3, 3),
    new THREE.MeshStandardMaterial({
      color: new THREE.Color(0.08, 0.10, 0.20),
      metalness: 0.3, roughness: 0.25,
      transparent: true, opacity: 0.30,
    })
  );
  gloss.rotation.x = -Math.PI / 2;
  gloss.position.y = 0.0005;
  gloss.receiveShadow = true;
  scene.add(gloss);
}

// ─── Label canvas — config-driven ─────────────────────────────────────────────
export function buildLabelCanvas(cfg) {
  const L = cfg.label;
  const SZ = 1024;
  const STRIP = 110;
  const USABLE_W = SZ - STRIP - 20;

  const cv = document.createElement('canvas');
  cv.width = cv.height = SZ;
  const g = cv.getContext('2d');

  // Background
  g.fillStyle = L.bg;
  g.fillRect(0, 0, SZ, SZ);

  // Brushed metal striations
  for (let y = 0; y < SZ; y += 3) {
    g.fillStyle = `rgba(255,255,255,${0.006 + Math.random() * 0.010})`;
    g.fillRect(0, y, SZ, 1);
  }

  // Right colour strip
  g.fillStyle = L.stripColor;
  g.fillRect(SZ - STRIP, 0, STRIP, SZ);
  g.fillStyle = L.stripAccent;
  g.fillRect(SZ - STRIP - 5, 0, 5, SZ);

  // Strip: rotated text
  g.save();
  g.translate(SZ - STRIP / 2, SZ / 2 + 55);
  g.rotate(-Math.PI / 2);
  g.font = 'bold 28px Arial, sans-serif';
  g.fillStyle = 'rgba(255,255,255,0.88)';
  g.textAlign = 'center';
  g.fillText(L.stripText, 0, 0);
  g.textAlign = 'left';
  g.restore();

  // Strip: small triangle logo
  g.fillStyle = 'rgba(255,255,255,0.50)';
  g.beginPath();
  g.moveTo(SZ - STRIP + 18, 50);
  g.lineTo(SZ - STRIP / 2,  22);
  g.lineTo(SZ - 18,         50);
  g.closePath();
  g.fill();

  // ── Main label area (clip so text never bleeds into strip) ───
  g.save();
  g.beginPath();
  g.rect(0, 0, SZ - STRIP - 10, SZ);
  g.clip();

  // Company name
  g.font = 'bold 34px Arial, sans-serif';
  g.fillStyle = L.companyColor ?? '#2a2a30';
  g.fillText(L.company, 44, 68);

  // Huge product name
  g.font = 'bold 210px "Arial Black", Arial, sans-serif';
  g.fillStyle = L.nameColor ?? '#141418';
  g.fillText(L.bigName, 36, 322);

  // Model number
  g.font = 'bold 64px Arial, sans-serif';
  g.fillStyle = L.modelColor ?? '#22222a';
  g.fillText(L.model, 44, 406);

  // Descriptor
  g.font = 'italic 28px Arial, sans-serif';
  g.fillStyle = L.descriptorColor ?? '#484858';
  g.fillText(L.descriptor, 44, 452);

  g.restore();

  // Rule 1
  g.strokeStyle = '#9a9da8'; g.lineWidth = 1.5;
  g.beginPath(); g.moveTo(44, 474); g.lineTo(USABLE_W, 474); g.stroke();

  // Specs
  let sy = 516;
  for (const { sym, val } of L.specs) {
    g.font = 'bold 23px "Courier New", monospace';
    g.fillStyle = L.specKeyColor ?? '#303040';
    g.fillText(sym, 44, sy);
    g.font = '21px "Courier New", monospace';
    g.fillStyle = L.specValColor ?? '#4a4a5a';
    g.fillText(val, 44 + 78, sy);
    sy += 46;
  }

  // Rule 2
  g.strokeStyle = '#9a9da8'; g.lineWidth = 1.5;
  g.beginPath(); g.moveTo(44, sy + 4); g.lineTo(USABLE_W, sy + 4); g.stroke();
  sy += 26;

  // S/N fill line
  g.font = 'bold 22px Arial, sans-serif';
  g.fillStyle = '#4a4a58';
  g.fillText('S/N', 44, sy + 26);
  g.strokeStyle = '#8a8a98'; g.lineWidth = 1.2;
  g.setLineDash([5, 4]);
  g.beginPath(); g.moveTo(108, sy + 28); g.lineTo(USABLE_W - 10, sy + 28); g.stroke();
  g.setLineDash([]);

  // Border
  g.strokeStyle = '#8898a8'; g.lineWidth = 5;
  g.strokeRect(3, 3, SZ - 6, SZ - 6);

  return cv;
}

// ─── Chip group: rounded case + label plane ───────────────────────────────────
export function buildChip(scene, renderer, cfg) {
  const { w, h, d, r } = cfg.dims;
  const group = new THREE.Group();
  group.rotation.y = cfg.rotation ?? -0.48;
  scene.add(group);

  // Case — metallic material
  const caseMesh = new THREE.Mesh(
    new RoundedBoxGeometry(w, h, d, 6, r),
    new THREE.MeshStandardMaterial({
      color:           new THREE.Color(...cfg.case.color),
      metalness:       cfg.case.metalness,
      roughness:       cfg.case.roughness,
      envMapIntensity: 1.8,
    })
  );
  caseMesh.position.y    = h / 2;
  caseMesh.castShadow    = true;
  caseMesh.receiveShadow = true;
  group.add(caseMesh);

  // Label — fully matte plane on top face; ONLY rotation.x = -PI/2
  const labelTex = new THREE.CanvasTexture(buildLabelCanvas(cfg));
  labelTex.colorSpace = THREE.SRGBColorSpace;
  labelTex.anisotropy = renderer.capabilities.getMaxAnisotropy();

  const labelMesh = new THREE.Mesh(
    new THREE.PlaneGeometry(w - r * 1.6, d - r * 1.6),
    new THREE.MeshStandardMaterial({
      map:             labelTex,
      metalness:       0.0,
      roughness:       0.95,
      envMapIntensity: 0.05,
    })
  );
  labelMesh.rotation.x = -Math.PI / 2;
  labelMesh.position.y = h + 0.0008;
  group.add(labelMesh);

  return group;
}

// ─── CSS vignette overlay ─────────────────────────────────────────────────────
export function addVignette() {
  const v = document.createElement('div');
  v.style.cssText = `
    position:absolute; inset:0; pointer-events:none;
    background:radial-gradient(ellipse at 50% 46%,
      transparent 32%, rgba(4,7,18,0.72) 100%);
  `;
  document.body.appendChild(v);
}

// ─── Animation loop with gentle auto-spin ─────────────────────────────────────
export function startLoop(renderer, scene, camera, controls, group, cfg) {
  const base = cfg.rotation ?? -0.48;
  let autoSpin = true, lastT = 0;
  controls.addEventListener('start', () => { autoSpin = false; lastT = Date.now(); });
  controls.addEventListener('end',   () => { lastT = Date.now(); });
  const clock = new THREE.Clock();

  (function loop() {
    requestAnimationFrame(loop);
    const t = clock.getElapsedTime();
    if (!autoSpin && Date.now() - lastT > 3500) autoSpin = true;
    if (autoSpin) group.rotation.y = base + Math.sin(t * 0.18) * 0.06;
    controls.update();
    renderer.render(scene, camera);
  })();

  window.addEventListener('resize', () => {
    camera.aspect = innerWidth / innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(innerWidth, innerHeight);
  });
}
