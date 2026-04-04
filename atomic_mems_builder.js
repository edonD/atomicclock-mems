(function () {
const errorBanner = document.getElementById("error-banner");

function showFatalError(message) {
    if (errorBanner) {
        errorBanner.style.display = "block";
        errorBanner.textContent = message;
    }
}

if (!window.THREE) {
    showFatalError("Three.js failed to load from the local package copy. Make sure `../micro-radar-fusion/node_modules/three/build/three.cjs` exists relative to this page.");
    return;
}

try {
const canvas = document.getElementById("scene");

const ui = {
    stageLabel: document.getElementById("stage-label"),
    stageSubtitle: document.getElementById("stage-subtitle"),
    tempLabel: document.getElementById("temp-label"),
    laserLabel: document.getElementById("laser-label"),
    outputLabel: document.getElementById("output-label"),
    linewidthLabel: document.getElementById("linewidth-label"),
    contrastLabel: document.getElementById("contrast-label"),
    sidebandLabel: document.getElementById("sideband-label"),
    stabilityLabel: document.getElementById("stability-label"),
    pipelineList: document.getElementById("pipeline-list"),
    notesList: document.getElementById("notes-list"),
    stageButtons: [...document.querySelectorAll("[data-stage]")],
    resetViewButton: document.getElementById("reset-view-button"),
    autoBuildButton: document.getElementById("auto-build-button"),
};

const renderer = new THREE.WebGLRenderer({
    canvas,
    antialias: true,
    powerPreference: "high-performance",
});
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 1.85));
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.06;
renderer.outputColorSpace = THREE.SRGBColorSpace;

const scene = new THREE.Scene();
scene.background = new THREE.Color(0x05090d);
scene.fog = new THREE.Fog(0x05090d, 42, 110);

const camera = new THREE.PerspectiveCamera(42, window.innerWidth / window.innerHeight, 0.1, 300);
camera.position.set(14.2, 10.8, 18.6);

class SimpleOrbitControls {
    constructor(cameraRef, domElement) {
        this.camera = cameraRef;
        this.domElement = domElement;
        this.target = new THREE.Vector3();
        this.enableDamping = true;
        this.dampingFactor = 0.08;
        this.minDistance = 8;
        this.maxDistance = 70;
        this.minPolarAngle = 0.18;
        this.maxPolarAngle = Math.PI * 0.48;
        this.rotateSpeed = 0.002;
        this.panSpeed = 0.28;
        this.zoomSpeed = 0.00045;

        this.spherical = new THREE.Spherical();
        this.sphericalDelta = new THREE.Spherical(0, 0, 0);
        this.panOffset = new THREE.Vector3();
        this.pointerState = null;
        this.prev = { x: 0, y: 0 };

        this.updateFromCamera();
        this.bindEvents();
    }

    bindEvents() {
        this.domElement.addEventListener("contextmenu", (event) => event.preventDefault());
        this.domElement.addEventListener("pointerdown", (event) => this.onPointerDown(event));
        window.addEventListener("pointermove", (event) => this.onPointerMove(event));
        window.addEventListener("pointerup", () => this.onPointerUp());
        this.domElement.addEventListener("wheel", (event) => this.onWheel(event), { passive: false });
    }

    updateFromCamera() {
        const offset = this.camera.position.clone().sub(this.target);
        this.spherical.setFromVector3(offset);
    }

    onPointerDown(event) {
        this.pointerState = event.button === 2 ? "pan" : "rotate";
        this.prev.x = event.clientX;
        this.prev.y = event.clientY;
    }

    onPointerMove(event) {
        if (!this.pointerState) {
            return;
        }

        const dx = event.clientX - this.prev.x;
        const dy = event.clientY - this.prev.y;
        this.prev.x = event.clientX;
        this.prev.y = event.clientY;

        if (this.pointerState === "rotate") {
            this.sphericalDelta.theta -= dx * this.rotateSpeed;
            this.sphericalDelta.phi -= dy * this.rotateSpeed;
        } else {
            const offset = this.camera.position.clone().sub(this.target);
            const distance = offset.length();
            const panX = (-dx / this.domElement.clientHeight) * distance * this.panSpeed;
            const panY = (dy / this.domElement.clientHeight) * distance * this.panSpeed;
            const pan = new THREE.Vector3();
            pan.copy(this.camera.up).setLength(panY);
            pan.add(new THREE.Vector3().crossVectors(this.camera.up, offset).setLength(panX));
            this.panOffset.add(pan);
        }
    }

    onPointerUp() {
        this.pointerState = null;
    }

    onWheel(event) {
        event.preventDefault();
        const zoomScale = Math.exp(event.deltaY * this.zoomSpeed);
        this.spherical.radius = THREE.MathUtils.clamp(
            this.spherical.radius * zoomScale,
            this.minDistance,
            this.maxDistance
        );
    }

    update() {
        this.spherical.theta += this.sphericalDelta.theta;
        this.spherical.phi += this.sphericalDelta.phi;
        this.spherical.phi = THREE.MathUtils.clamp(this.spherical.phi, this.minPolarAngle, this.maxPolarAngle);
        this.target.add(this.panOffset);

        const offset = new THREE.Vector3().setFromSpherical(this.spherical);
        this.camera.position.copy(this.target).add(offset);
        this.camera.lookAt(this.target);

        if (this.enableDamping) {
            this.sphericalDelta.theta *= 1 - this.dampingFactor;
            this.sphericalDelta.phi *= 1 - this.dampingFactor;
            this.panOffset.multiplyScalar(1 - this.dampingFactor);
        } else {
            this.sphericalDelta.theta = 0;
            this.sphericalDelta.phi = 0;
            this.panOffset.set(0, 0, 0);
        }
    }
}

const controls = new SimpleOrbitControls(camera, renderer.domElement);
controls.target.set(0, 3.15, 0.2);
controls.minDistance = 12;
controls.maxDistance = 60;
controls.maxPolarAngle = Math.PI * 0.47;
controls.updateFromCamera();

const hemiLight = new THREE.HemisphereLight(0xb6d7f3, 0x0e1419, 0.72);
scene.add(hemiLight);

const keyLight = new THREE.DirectionalLight(0xfff1db, 2.5);
keyLight.position.set(24, 30, 20);
keyLight.castShadow = true;
keyLight.shadow.mapSize.set(2048, 2048);
keyLight.shadow.camera.left = -34;
keyLight.shadow.camera.right = 34;
keyLight.shadow.camera.top = 34;
keyLight.shadow.camera.bottom = -34;
keyLight.shadow.camera.far = 120;
keyLight.shadow.bias = -0.00025;
scene.add(keyLight);

const fillLight = new THREE.DirectionalLight(0x85c7ff, 0.58);
fillLight.position.set(-18, 14, -16);
scene.add(fillLight);

const rimLight = new THREE.PointLight(0xf6bf7c, 1.25, 90, 2);
rimLight.position.set(0, 18, -20);
scene.add(rimLight);

const stageDefs = [
    {
        name: "MEMS Stack",
        subtitle: "Stacking the silicon cavity and bonded glass windows inside the package.",
        notes: [
            "<strong>Geometry:</strong> 3x3 mm die with a 1.5 mm cavity and bonded glass caps, scaled up visually so the internal build stays readable.",
            "<strong>Materials:</strong> ceramic package, metallic die attach, silicon frame, and borofloat-style transparent windows rather than abstract blocks.",
            "<strong>Why it matters:</strong> the cavity is the physical volume that holds the rubidium vapor and buffer gas for the atomic reference.",
        ],
    },
    {
        name: "Thermal Control",
        subtitle: "Pt serpentine heater and RTD lift the vapor cell to the 85 C operating point.",
        notes: [
            "<strong>Heater:</strong> the serpentine trace represents the platinum heater that drives the cell to the target temperature.",
            "<strong>Sensor:</strong> the smaller trace is the RTD feedback path used to hold the cell near the thermal setpoint.",
            "<strong>Spec anchor:</strong> your local design sheet calls for about 73.84 mW heater power and extremely tight temperature stability.",
        ],
    },
    {
        name: "Optical Pumping",
        subtitle: "The VCSEL launches the 794.979 nm beam and its RF-generated sidebands through the cell.",
        notes: [
            "<strong>Laser:</strong> the left optical block acts as the VCSEL source, and the beam path shows the two optical components driving the Rb-87 transition.",
            "<strong>Photodiode:</strong> the receiver on the far side measures transmitted optical power after the beam crosses the vapor cell.",
            "<strong>Physics link:</strong> the sideband spacing is driven toward the 6.834682610 GHz hyperfine splitting needed for CPT.",
        ],
    },
    {
        name: "CPT Dark State",
        subtitle: "Rubidium atoms build ground-state coherence and open the narrow transparency dip.",
        notes: [
            "<strong>Atom cloud:</strong> the animated vapor in the cavity tightens as the two optical fields drive the coherent dark state.",
            "<strong>Resonance:</strong> the cyan ring in the cell represents the CPT transparency window rather than a generic glow effect.",
            "<strong>Result:</strong> this is the usable clock signal, with the local model targeting a linewidth near 3 kHz and strong contrast.",
        ],
    },
    {
        name: "Locked Output",
        subtitle: "Photodiode signal closes the servo loop and the package presents a disciplined 10 MHz output.",
        notes: [
            "<strong>Control loop:</strong> the traveling pulses on the interconnects represent detector feedback, PLL control, and heater stabilization acting together.",
            "<strong>Output:</strong> once lock is established, the package behaves like a compact frequency reference rather than just a heated optical cavity.",
            "<strong>Performance:</strong> the numbers shown here follow the local CSAC spec sheet: 10 MHz output, 30 Hz lock bandwidth, and simulated ADEV of 8.84e-12 at 1 s.",
        ],
    },
];

const state = {
    targetStage: 0,
    presentationStage: 0,
    autoBuild: false,
    lastAutoSwitch: 0,
    fps: 60,
};

const TMP = {
    v1: new THREE.Vector3(),
    v2: new THREE.Vector3(),
};

scene.add(createLabEnvironment());
const assembly = createAtomicClockAssembly();
scene.add(assembly.group);

setStage(0, true);
syncAutoButton();

ui.stageButtons.forEach((button) => {
    button.addEventListener("click", () => {
        setStage(Number(button.dataset.stage), false);
    });
});

ui.resetViewButton.addEventListener("click", () => resetView());
ui.autoBuildButton.addEventListener("click", () => {
    state.autoBuild = !state.autoBuild;
    state.lastAutoSwitch = clock.getElapsedTime();
    syncAutoButton();
});

window.addEventListener("resize", onResize);
window.addEventListener("keydown", (event) => {
    if (event.code === "Space") {
        state.autoBuild = !state.autoBuild;
        state.lastAutoSwitch = clock.getElapsedTime();
        syncAutoButton();
        return;
    }

    if (event.code === "KeyF") {
        resetView();
        return;
    }

    const match = event.code.match(/^Digit([1-5])$/);
    if (match) {
        setStage(Number(match[1]) - 1, false);
    }
});

const clock = new THREE.Clock();
animate();

function animate() {
    requestAnimationFrame(animate);

    const delta = Math.min(clock.getDelta(), 0.04);
    const elapsed = clock.getElapsedTime();

    if (state.autoBuild && elapsed - state.lastAutoSwitch > 5.5) {
        state.targetStage = (state.targetStage + 1) % stageDefs.length;
        state.lastAutoSwitch = elapsed;
        syncStageButtons();
    }

    state.presentationStage = damp(state.presentationStage, state.targetStage, 4.4, delta);
    updateAtomicClockAssembly(assembly, state.presentationStage, elapsed, delta);
    updateHud(state.presentationStage, elapsed, delta);

    controls.update();
    renderer.render(scene, camera);
}

function updateHud(stageValue, elapsed, delta) {
    state.fps = THREE.MathUtils.lerp(state.fps, 1 / Math.max(delta, 0.0001), 0.09);

    const activeStageIndex = THREE.MathUtils.clamp(Math.round(stageValue), 0, stageDefs.length - 1);
    const activeStage = stageDefs[activeStageIndex];
    const timeline = stageValue + 1;
    const stackLevel = smoothstep01(rangeProgress(timeline, 0.0, 1.0));
    const heatLevel = smoothstep01(rangeProgress(timeline, 1.0, 2.0));
    const opticalLevel = smoothstep01(rangeProgress(timeline, 2.0, 3.0));
    const cptLevel = smoothstep01(rangeProgress(timeline, 3.0, 4.0));
    const lockLevel = smoothstep01(rangeProgress(timeline, 4.0, 5.0));

    const cellTemp = THREE.MathUtils.lerp(25, 85, heatLevel);
    const detectorPowerUw = 168.8 * opticalLevel * (0.35 + cptLevel * 0.65);
    const linewidthKhz = opticalLevel < 0.22 ? "--" : `${THREE.MathUtils.lerp(12.5, 3.01, cptLevel).toFixed(2)} kHz`;
    const contrastPct = cptLevel < 0.1 ? "--" : `${(34.78 * cptLevel).toFixed(1)}%`;
    const sidebandOffsetGhz = 3.417341305 * opticalLevel;
    const sidebandGHz = opticalLevel < 0.04 ? "0 GHz" : `±${sidebandOffsetGhz.toFixed(3)} GHz`;
    const adevText = lockLevel < 0.08 ? "--" : `${(8.84e-12 / Math.max(lockLevel, 0.25)).toExponential(2)}`;
    const outputJitter = Math.sin(elapsed * 16) * (1 - lockLevel) * 0.0012 + Math.sin(elapsed * 63) * 0.0000005;
    const outputValue = 10 + outputJitter;

    if (ui.stageLabel) {
        ui.stageLabel.textContent = activeStage.name;
    }
    if (ui.stageSubtitle) {
        ui.stageSubtitle.textContent = activeStage.subtitle;
    }
    if (ui.tempLabel) {
        ui.tempLabel.textContent = `${cellTemp.toFixed(1)} C`;
    }
    if (ui.laserLabel) {
        ui.laserLabel.textContent = `${detectorPowerUw.toFixed(1)} uW`;
    }
    if (ui.outputLabel) {
        ui.outputLabel.textContent = lockLevel < 0.08 ? "Acquiring" : `${outputValue.toFixed(6)} MHz`;
    }
    if (ui.linewidthLabel) {
        ui.linewidthLabel.textContent = linewidthKhz;
    }
    if (ui.contrastLabel) {
        ui.contrastLabel.textContent = contrastPct;
    }
    if (ui.sidebandLabel) {
        ui.sidebandLabel.textContent = opticalLevel < 0.04 ? "0 GHz" : `+/-${sidebandOffsetGhz.toFixed(3)} GHz`;
    }
    if (ui.stabilityLabel) {
        ui.stabilityLabel.textContent = adevText;
    }
    if (ui.notesList) {
        ui.notesList.innerHTML = activeStage.notes.map((note) => `<div>${note}</div>`).join("");
    }

    const stages = [
        {
            name: "Wafer Stack",
            value: stackLevel,
            label: "3x3 mm die",
            caption: "Glass caps, silicon cavity, and package geometry build the physical atomic cell volume.",
        },
        {
            name: "Thermal Loop",
            value: heatLevel,
            label: `${cellTemp.toFixed(1)} C`,
            caption: "The heater and RTD push the cell toward its tightly regulated operating point.",
        },
        {
            name: "VCSEL + Optics",
            value: opticalLevel,
            label: `${detectorPowerUw.toFixed(0)} uW`,
            caption: "A modulated VCSEL sends the D1-line light through the vapor cell to the photodiode.",
        },
        {
            name: "CPT Resonance",
            value: cptLevel,
            label: contrastPct === "--" ? "Building" : contrastPct,
            caption: "Ground-state coherence forms the dark state that produces the narrow resonance feature.",
        },
        {
            name: "Servo Lock",
            value: lockLevel,
            label: lockLevel < 0.08 ? "Open" : "Locked",
            caption: "Electronics steer the system onto the atomic resonance and divide down the stable reference.",
        },
    ];

    if (ui.pipelineList) {
        ui.pipelineList.innerHTML = stages.map((stage) => `
            <div class="pipeline-stage">
                <div class="pipeline-stage-head">
                    <strong>${stage.name}</strong>
                    <span>${stage.label}</span>
                </div>
                <div class="pipeline-bar">
                    <div class="pipeline-bar-fill" style="transform: scaleX(${THREE.MathUtils.clamp(stage.value, 0.02, 1)})"></div>
                </div>
                <div class="pipeline-caption">${stage.caption}</div>
            </div>
        `).join("");
    }
}

function setStage(index, preserveAuto) {
    state.targetStage = THREE.MathUtils.clamp(index, 0, stageDefs.length - 1);
    if (!preserveAuto) {
        state.autoBuild = false;
        syncAutoButton();
    }
    syncStageButtons();
}

function syncStageButtons() {
    ui.stageButtons.forEach((button) => {
        button.classList.toggle("active", Number(button.dataset.stage) === state.targetStage);
    });
}

function syncAutoButton() {
    ui.autoBuildButton.classList.toggle("active", state.autoBuild);
    ui.autoBuildButton.innerHTML = state.autoBuild
        ? "<strong>Auto Build On</strong><span>Running the full assembly and lock sequence in a loop.</span>"
        : "<strong>Auto Build</strong><span>Cycle through the full assembly and lock sequence.</span>";
}

function resetView() {
    controls.target.set(0, 3.15, 0.2);
    camera.position.set(14.2, 10.8, 18.6);
    controls.updateFromCamera();
}

function onResize() {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
}

function createLabEnvironment() {
    const group = new THREE.Group();

    const floor = new THREE.Mesh(
        new THREE.CircleGeometry(74, 64),
        new THREE.MeshStandardMaterial({
            color: 0x141a1f,
            roughness: 0.9,
            metalness: 0.08,
        })
    );
    floor.rotation.x = -Math.PI / 2;
    floor.receiveShadow = true;
    group.add(floor);

    const pedestal = new THREE.Mesh(
        new THREE.CylinderGeometry(15.5, 17.2, 1.4, 40),
        new THREE.MeshStandardMaterial({
            color: 0x222a31,
            roughness: 0.54,
            metalness: 0.3,
        })
    );
    pedestal.position.y = 0.7;
    pedestal.castShadow = true;
    pedestal.receiveShadow = true;
    group.add(pedestal);

    const topPlate = new THREE.Mesh(
        new THREE.CylinderGeometry(12.8, 13.6, 0.28, 40),
        new THREE.MeshStandardMaterial({
            color: 0x7d848d,
            roughness: 0.34,
            metalness: 0.74,
        })
    );
    topPlate.position.y = 1.56;
    topPlate.castShadow = true;
    topPlate.receiveShadow = true;
    group.add(topPlate);

    const backdropTexture = makeBackdropTexture();
    const backdrop = new THREE.Mesh(
        new THREE.PlaneGeometry(88, 42),
        new THREE.MeshBasicMaterial({
            map: backdropTexture,
            transparent: true,
            opacity: 0.94,
        })
    );
    backdrop.position.set(0, 22, -28);
    group.add(backdrop);

    const leftWing = backdrop.clone();
    leftWing.position.set(-28, 16, -18);
    leftWing.rotation.y = THREE.MathUtils.degToRad(38);
    leftWing.scale.set(0.85, 0.8, 1);
    group.add(leftWing);

    const rightWing = leftWing.clone();
    rightWing.position.x = 28;
    rightWing.rotation.y *= -1;
    group.add(rightWing);

    return group;
}

function createAtomicClockAssembly() {
    const group = new THREE.Group();
    group.position.set(0, 1.64, 0);

    const parts = {};
    const links = [];
    const opticsScale = 1.28;
    const opticsY = 2.58;
    const opticsZ = 0.0;
    const vcselX = -4.25;
    const photodiodeX = 4.25;
    const vcselEmitterLocalX = 1.38;
    const photodiodeReceiverLocalX = -1.42;
    const beamStartX = vcselX + vcselEmitterLocalX * opticsScale;
    const beamEndX = photodiodeX + photodiodeReceiverLocalX * opticsScale;
    const beamLength = beamEndX - beamStartX;
    const beamCenterX = (beamStartX + beamEndX) * 0.5;
    const beamLocalStartX = -beamLength * 0.5;

    const ceramicMaterial = new THREE.MeshStandardMaterial({
        color: 0xdbd6cb,
        roughness: 0.88,
        metalness: 0.05,
    });
    const ceramicDarkMaterial = new THREE.MeshStandardMaterial({
        color: 0x8b8478,
        roughness: 0.84,
        metalness: 0.06,
    });
    const dieAttachMaterial = new THREE.MeshStandardMaterial({
        color: 0x606a73,
        roughness: 0.42,
        metalness: 0.76,
    });
    const siliconMaterial = new THREE.MeshStandardMaterial({
        color: 0x5b636b,
        roughness: 0.28,
        metalness: 0.56,
    });
    const goldMaterial = new THREE.MeshStandardMaterial({
        color: 0xc59b4b,
        roughness: 0.28,
        metalness: 0.92,
    });

    const packageBase = createBox(18, 1.6, 18, ceramicMaterial);
    packageBase.position.set(0, 0.8, 0);
    packageBase.castShadow = true;
    packageBase.receiveShadow = true;
    group.add(packageBase);

    const cavityFloor = createBox(12.2, 0.14, 12.2, ceramicDarkMaterial);
    cavityFloor.position.set(0, 1.67, 0);
    cavityFloor.receiveShadow = true;
    group.add(cavityFloor);

    const wallHeight = 2.1;
    [
        [-5.4, 2.72, 0, 1.2, wallHeight, 12.2],
        [5.4, 2.72, 0, 1.2, wallHeight, 12.2],
        [0, 2.72, -5.4, 10.8, wallHeight, 1.2],
        [0, 2.12, 5.15, 10.8, 0.9, 0.7],
    ].forEach(([x, y, z, sx, sy, sz]) => {
        const wall = createBox(sx, sy, sz, ceramicMaterial);
        wall.position.set(x, y, z);
        wall.castShadow = true;
        wall.receiveShadow = true;
        group.add(wall);
    });

    for (let i = -3; i <= 3; i += 2) {
        const leadA = createBox(1.45, 0.18, 0.72, goldMaterial);
        leadA.position.set(-8.7, 0.36, i * 2);
        leadA.castShadow = true;
        group.add(leadA);

        const leadB = leadA.clone();
        leadB.position.x *= -1;
        group.add(leadB);

        const leadC = createBox(0.72, 0.18, 1.45, goldMaterial);
        leadC.position.set(i * 2, 0.36, -8.7);
        group.add(leadC);

        const leadD = leadC.clone();
        leadD.position.z *= -1;
        group.add(leadD);
    }

    const dieAttach = createBox(5.6, 0.18, 5.6, dieAttachMaterial);
    dieAttach.position.set(0, 1.9, 0);
    dieAttach.castShadow = true;
    dieAttach.receiveShadow = true;
    group.add(dieAttach);

    const bottomGlass = createBox(3.0, 0.3, 3.0, new THREE.MeshPhysicalMaterial({
        color: 0xc4ddf7,
        roughness: 0.04,
        metalness: 0.02,
        transparent: true,
        opacity: 0.34,
        transmission: 0.72,
    }));
    bottomGlass.castShadow = true;
    bottomGlass.receiveShadow = true;
    parts.bottomGlass = createPart(bottomGlass, new THREE.Vector3(0, 2.14, 0), new THREE.Vector3(0, 3.2, 0), 1);
    group.add(bottomGlass);

    const siliconFrame = new THREE.Group();
    [
        [0, 0, -1.22, 3.0, 0.5, 0.55],
        [0, 0, 1.22, 3.0, 0.5, 0.55],
        [-1.22, 0, 0, 0.55, 0.5, 1.9],
        [1.22, 0, 0, 0.55, 0.5, 1.9],
    ].forEach(([x, y, z, sx, sy, sz]) => {
        const wall = createBox(sx, sy, sz, siliconMaterial);
        wall.position.set(x, y, z);
        wall.castShadow = true;
        wall.receiveShadow = true;
        siliconFrame.add(wall);
    });

    const cavityRing = new THREE.Mesh(
        new THREE.TorusGeometry(0.84, 0.08, 18, 48),
        new THREE.MeshStandardMaterial({
            color: 0x747d85,
            roughness: 0.24,
            metalness: 0.78,
        })
    );
    cavityRing.rotation.x = Math.PI / 2;
    cavityRing.position.y = 0.04;
    siliconFrame.add(cavityRing);

    parts.siliconFrame = createPart(siliconFrame, new THREE.Vector3(0, 2.54, 0), new THREE.Vector3(0, 2.4, 0), 1);
    group.add(siliconFrame);

    const cavityAura = new THREE.Mesh(
        new THREE.CylinderGeometry(0.72, 0.72, 0.92, 32, 1, true),
        new THREE.MeshBasicMaterial({
            color: 0xf7b270,
            transparent: true,
            opacity: 0.06,
            side: THREE.DoubleSide,
            depthWrite: false,
            blending: THREE.AdditiveBlending,
        })
    );
    cavityAura.position.set(0, 2.55, 0);
    group.add(cavityAura);

    const topGlass = createBox(3.0, 0.3, 3.0, new THREE.MeshPhysicalMaterial({
        color: 0xcde0f7,
        roughness: 0.03,
        metalness: 0.02,
        transparent: true,
        opacity: 0.38,
        transmission: 0.82,
    }));
    topGlass.castShadow = true;
    topGlass.receiveShadow = true;
    parts.topGlass = createPart(topGlass, new THREE.Vector3(0, 2.94, 0), new THREE.Vector3(0, 3.7, 0), 1);
    group.add(topGlass);

    const heater = createTubePath([
        new THREE.Vector3(-1.2, 0, 1.05),
        new THREE.Vector3(1.2, 0, 1.05),
        new THREE.Vector3(1.2, 0, 0.72),
        new THREE.Vector3(-1.2, 0, 0.72),
        new THREE.Vector3(-1.2, 0, 0.34),
        new THREE.Vector3(1.2, 0, 0.34),
        new THREE.Vector3(1.2, 0, -0.06),
        new THREE.Vector3(-1.2, 0, -0.06),
        new THREE.Vector3(-1.2, 0, -0.46),
        new THREE.Vector3(1.2, 0, -0.46),
        new THREE.Vector3(1.2, 0, -0.88),
        new THREE.Vector3(-1.2, 0, -0.88),
    ], 0.035, new THREE.MeshStandardMaterial({
        color: 0xa88456,
        roughness: 0.36,
        metalness: 0.8,
        emissive: 0xff8d43,
        emissiveIntensity: 0,
    }));
    parts.heater = createPart(heater, new THREE.Vector3(0, 2.81, 0), new THREE.Vector3(0, 1.4, 0), 1);
    group.add(heater);

    const rtd = createTubePath([
        new THREE.Vector3(-1.05, 0, 1.18),
        new THREE.Vector3(-0.48, 0, 1.18),
        new THREE.Vector3(-0.48, 0, 0.82),
        new THREE.Vector3(-0.96, 0, 0.82),
        new THREE.Vector3(-0.96, 0, 0.48),
        new THREE.Vector3(-0.36, 0, 0.48),
    ], 0.022, new THREE.MeshStandardMaterial({
        color: 0xb2bac1,
        roughness: 0.42,
        metalness: 0.82,
        emissive: 0x89d7ff,
        emissiveIntensity: 0,
    }));
    parts.rtd = createPart(rtd, new THREE.Vector3(0, 2.835, 0), new THREE.Vector3(0, 1.1, 0), 1);
    group.add(rtd);

    const atomCloud = createAtomCloud(220, 0.66, 0.68);
    atomCloud.points.position.set(0, 2.55, 0);
    group.add(atomCloud.points);

    const stateLobeA = createStateLobe(0xffc07d);
    const stateLobeB = createStateLobe(0x95dcff);
    stateLobeA.position.set(-0.28, 2.55, 0);
    stateLobeB.position.set(0.28, 2.55, 0);
    group.add(stateLobeA);
    group.add(stateLobeB);

    const superpositionShell = new THREE.Mesh(
        new THREE.SphereGeometry(0.34, 26, 22),
        new THREE.MeshBasicMaterial({
            color: 0xc7b6ff,
            transparent: true,
            opacity: 0,
            depthWrite: false,
            blending: THREE.AdditiveBlending,
        })
    );
    superpositionShell.position.set(0, 2.55, 0);
    group.add(superpositionShell);

    const superpositionCloud = new THREE.Mesh(
        new THREE.SphereGeometry(0.24, 24, 20),
        new THREE.MeshBasicMaterial({
            color: 0xff8fb7,
            transparent: true,
            opacity: 0,
            depthWrite: false,
            blending: THREE.AdditiveBlending,
        })
    );
    superpositionCloud.position.set(0, 2.55, 0);
    group.add(superpositionCloud);

    const darkStateHalo = new THREE.Mesh(
        new THREE.TorusGeometry(0.54, 0.05, 16, 64),
        new THREE.MeshBasicMaterial({
            color: 0xff8d7a,
            transparent: true,
            opacity: 0,
            depthWrite: false,
            blending: THREE.AdditiveBlending,
        })
    );
    darkStateHalo.position.set(0, 2.55, 0);
    darkStateHalo.rotation.x = Math.PI / 2;
    group.add(darkStateHalo);

    const darkStateCore = new THREE.Mesh(
        new THREE.SphereGeometry(0.33, 24, 24),
        new THREE.MeshBasicMaterial({
            color: 0xffb4a5,
            transparent: true,
            opacity: 0,
            depthWrite: false,
            blending: THREE.AdditiveBlending,
        })
    );
    darkStateCore.position.set(0, 2.55, 0);
    group.add(darkStateCore);

    const vcselGroup = createOpticsModule("vcsel");
    vcselGroup.group.scale.setScalar(opticsScale);
    parts.vcsel = createPart(vcselGroup.group, new THREE.Vector3(vcselX, opticsY, opticsZ), new THREE.Vector3(-6.2, 0.35, 0), 1);
    group.add(vcselGroup.group);

    const photodiodeGroup = createOpticsModule("photodiode");
    photodiodeGroup.group.scale.setScalar(opticsScale);
    parts.photodiode = createPart(photodiodeGroup.group, new THREE.Vector3(photodiodeX, opticsY, opticsZ), new THREE.Vector3(6.2, 0.35, 0), 1);
    group.add(photodiodeGroup.group);

    const pllBlock = createElectronicsBlock(2.1, 1.0, 1.85, 0x2b343c, 0x7fd2ff);
    parts.pllBlock = createPart(pllBlock, new THREE.Vector3(-5.9, 3.6, -5.2), new THREE.Vector3(0, 2.2, -1.2), 1);
    group.add(pllBlock);

    const controllerBlock = createElectronicsBlock(3.0, 1.1, 1.95, 0x253039, 0xf4bc7e);
    parts.controllerBlock = createPart(controllerBlock, new THREE.Vector3(0, 3.82, -5.35), new THREE.Vector3(0, 2.6, -0.8), 1);
    group.add(controllerBlock);

    const outputBlock = createElectronicsBlock(2.2, 1.0, 1.85, 0x2f363d, 0xb8f1ff);
    parts.outputBlock = createPart(outputBlock, new THREE.Vector3(5.95, 3.55, -5.2), new THREE.Vector3(0, 1.8, -1.2), 1);
    group.add(outputBlock);

    const beamGroup = new THREE.Group();
    const beamCore = createBeamCylinder(beamLength, 0.095, 0xff3b2f, 0.16);
    const beamUpper = createBeamCylinder(beamLength, 0.14, 0xff6a57, 0.08);
    const beamLower = createBeamCylinder(beamLength, 0.055, 0xffb1a5, 0.12);
    const beamWaves = [
        createBeamWave(beamLength, 0.045, 0xff4e3b, 0.0, 5.0),
        createBeamWave(beamLength, 0.075, 0xff715e, 0.22, 6.2),
        createBeamWave(beamLength, 0.105, 0xffa08f, 0.58, 6.8),
    ];
    beamUpper.position.z = 0;
    beamLower.position.z = 0;
    beamGroup.position.set(beamCenterX, opticsY, opticsZ);
    beamGroup.add(beamCore);
    beamGroup.add(beamUpper);
    beamGroup.add(beamLower);
    beamWaves.forEach((wave) => beamGroup.add(wave.line));

    const beamPulses = [];
    for (let i = 0; i < 4; i += 1) {
        const pulse = new THREE.Mesh(
            new THREE.RingGeometry(0.06, 0.14, 24),
            new THREE.MeshBasicMaterial({
                color: i % 2 === 0 ? 0xff6e58 : 0xffb0a3,
                transparent: true,
                opacity: 0.18,
                side: THREE.DoubleSide,
                depthWrite: false,
                blending: THREE.AdditiveBlending,
            })
        );
        pulse.rotation.y = Math.PI / 2;
        beamGroup.add(pulse);
        beamPulses.push(pulse);
    }

    const modulatorRings = [];
    for (let i = 0; i < 3; i += 1) {
        const ring = new THREE.Mesh(
            new THREE.TorusGeometry(0.32, 0.018, 12, 40),
            new THREE.MeshBasicMaterial({
                color: i === 1 ? 0xff806c : 0xffb3a0,
                transparent: true,
                opacity: 0.16,
                depthWrite: false,
                blending: THREE.AdditiveBlending,
            })
        );
        ring.position.set(beamStartX - 0.28, opticsY, opticsZ);
        ring.rotation.y = Math.PI / 2;
        group.add(ring);
        modulatorRings.push(ring);
    }

    group.add(beamGroup);

    links.push(createFlowLink(
        [
            new THREE.Vector3(0, 3.82, -5.35),
            new THREE.Vector3(0, 3.9, -2.5),
            new THREE.Vector3(0, 3.35, -1.1),
            new THREE.Vector3(0, 2.84, 0.18),
        ],
        0xf4bc7e,
        0.07
    ));

    links.push(createFlowLink(
        [
            new THREE.Vector3(-5.9, 3.6, -5.2),
            new THREE.Vector3(-5.8, 3.4, -2.7),
            new THREE.Vector3(-5.15, 3.0, -0.9),
            new THREE.Vector3(vcselX, opticsY, opticsZ),
        ],
        0x8fdcff,
        0.05
    ));

    links.push(createFlowLink(
        [
            new THREE.Vector3(photodiodeX, opticsY, opticsZ),
            new THREE.Vector3(5.8, 3.12, -1.8),
            new THREE.Vector3(4.2, 3.78, -4.1),
            new THREE.Vector3(0.8, 3.82, -5.35),
        ],
        0xa8ecff,
        0.1
    ));

    links.push(createFlowLink(
        [
            new THREE.Vector3(0.5, 3.82, -5.35),
            new THREE.Vector3(2.8, 3.9, -5.45),
            new THREE.Vector3(4.9, 3.7, -5.3),
            new THREE.Vector3(5.95, 3.55, -5.2),
        ],
        0xf5c690,
        0.13
    ));

    links.forEach((link) => {
        group.add(link.tube);
        group.add(link.pulse);
    });

    return {
        group,
        parts,
        optics: {
            beamLocalStartX,
            beamLength,
        },
        atomCloud,
        stateLobeA,
        stateLobeB,
        superpositionShell,
        superpositionCloud,
        cavityAura,
        darkStateHalo,
        darkStateCore,
        beamGroup,
        beamCore,
        beamUpper,
        beamLower,
        beamWaves,
        beamPulses,
        modulatorRings,
        vcselGroup,
        photodiodeGroup,
        links,
    };
}

function updateAtomicClockAssembly(assemblyRef, stageValue, elapsed, delta) {
    const timeline = stageValue + 1;
    const stackLevel = smoothstep01(rangeProgress(timeline, 0.0, 1.0));
    const heatLevel = smoothstep01(rangeProgress(timeline, 1.0, 2.0));
    const opticalLevel = smoothstep01(rangeProgress(timeline, 2.0, 3.0));
    const cptLevel = smoothstep01(rangeProgress(timeline, 3.0, 4.0));
    const lockLevel = smoothstep01(rangeProgress(timeline, 4.0, 5.0));
    const componentPreview = Math.max(stackLevel * 0.8, opticalLevel);
    const vaporPreview = Math.max(stackLevel * 0.6, opticalLevel * 0.82 + cptLevel * 0.18);
    const beamPreview = Math.max(stackLevel * 0.42, opticalLevel);
    const superpositionLevel = smoothstep01(rangeProgress(timeline, 2.3, 4.0));
    const resonanceLevel = smoothstep01(rangeProgress(timeline, 3.0, 4.2));

    applyPart(assemblyRef.parts.bottomGlass, stackLevel);
    applyPart(assemblyRef.parts.siliconFrame, stackLevel);
    applyPart(assemblyRef.parts.topGlass, stackLevel);
    applyPart(assemblyRef.parts.heater, heatLevel);
    applyPart(assemblyRef.parts.rtd, heatLevel);
    applyPart(assemblyRef.parts.vcsel, componentPreview);
    applyPart(assemblyRef.parts.photodiode, componentPreview);
    applyPart(assemblyRef.parts.pllBlock, opticalLevel * 0.9 + lockLevel * 0.1);
    applyPart(assemblyRef.parts.controllerBlock, cptLevel * 0.5 + lockLevel * 0.5);
    applyPart(assemblyRef.parts.outputBlock, lockLevel);

    const heaterMaterials = getMaterials(assemblyRef.parts.heater.object);
    heaterMaterials.forEach((material) => {
        if ("emissiveIntensity" in material) {
            material.emissiveIntensity = 0.08 + heatLevel * 1.6;
            material.color.setHex(heatLevel > 0.2 ? 0xd09a58 : 0xa88456);
        }
    });

    const rtdMaterials = getMaterials(assemblyRef.parts.rtd.object);
    rtdMaterials.forEach((material) => {
        if ("emissiveIntensity" in material) {
            material.emissiveIntensity = 0.03 + heatLevel * 0.75;
        }
    });

    const topGlassMaterials = getMaterials(assemblyRef.parts.topGlass.object);
    topGlassMaterials.forEach((material) => {
        if ("opacity" in material && material.userData.baseOpacity !== undefined) {
            material.opacity = material.userData.baseOpacity * stackLevel * (1 - opticalLevel * 0.2 - cptLevel * 0.28);
        }
    });

    assemblyRef.cavityAura.material.opacity = 0.03 + heatLevel * 0.11 + cptLevel * 0.06;
    assemblyRef.cavityAura.material.color.set(heatLevel < 0.85 ? 0xf4b06b : 0x86dfff);
    assemblyRef.cavityAura.scale.set(
        1 + Math.sin(elapsed * 1.9) * 0.015,
        1 + heatLevel * 0.08,
        1 + Math.cos(elapsed * 1.5) * 0.015
    );

    updateAtomCloud(assemblyRef.atomCloud, elapsed, vaporPreview, cptLevel, lockLevel);

    const lobeOffset = THREE.MathUtils.lerp(0.34, 0.03, resonanceLevel);
    const lobeScaleX = THREE.MathUtils.lerp(1.35, 0.84, resonanceLevel);
    const lobeScaleY = THREE.MathUtils.lerp(0.78, 1.08, resonanceLevel);
    const lobeOpacity = superpositionLevel * (0.16 + (1 - resonanceLevel) * 0.22 + lockLevel * 0.05);
    assemblyRef.stateLobeA.visible = superpositionLevel > 0.03;
    assemblyRef.stateLobeB.visible = superpositionLevel > 0.03;
    assemblyRef.stateLobeA.position.set(-lobeOffset, 2.55 + Math.sin(elapsed * 2.1) * 0.02, 0);
    assemblyRef.stateLobeB.position.set(lobeOffset, 2.55 - Math.sin(elapsed * 2.1) * 0.02, 0);
    assemblyRef.stateLobeA.scale.set(lobeScaleX, lobeScaleY, 1.02 + Math.sin(elapsed * 1.3) * 0.03);
    assemblyRef.stateLobeB.scale.set(lobeScaleX, lobeScaleY, 1.02 - Math.sin(elapsed * 1.3) * 0.03);
    assemblyRef.stateLobeA.material.opacity = lobeOpacity;
    assemblyRef.stateLobeB.material.opacity = lobeOpacity;

    assemblyRef.superpositionShell.visible = resonanceLevel > 0.04;
    assemblyRef.superpositionShell.material.opacity = resonanceLevel * 0.16 + lockLevel * 0.08;
    assemblyRef.superpositionShell.rotation.x = elapsed * 0.35;
    assemblyRef.superpositionShell.rotation.y = elapsed * 0.48;
    assemblyRef.superpositionShell.scale.set(
        0.94 + resonanceLevel * 0.28 + Math.sin(elapsed * 1.6) * 0.03,
        1.05 + resonanceLevel * 0.22,
        0.94 + resonanceLevel * 0.28 + Math.cos(elapsed * 1.6) * 0.03
    );

    assemblyRef.superpositionCloud.visible = superpositionLevel > 0.04;
    assemblyRef.superpositionCloud.material.opacity = superpositionLevel * 0.08 + resonanceLevel * 0.18 + lockLevel * 0.06;
    assemblyRef.superpositionCloud.scale.set(
        0.82 + resonanceLevel * 0.36 + Math.sin(elapsed * 1.4) * 0.03,
        1.04 + resonanceLevel * 0.18,
        0.82 + resonanceLevel * 0.36 + Math.cos(elapsed * 1.4) * 0.03
    );

    assemblyRef.darkStateHalo.visible = cptLevel > 0.04;
    assemblyRef.darkStateCore.visible = cptLevel > 0.04;
    assemblyRef.darkStateHalo.material.opacity = cptLevel * 0.18 + lockLevel * 0.1;
    assemblyRef.darkStateCore.material.opacity = cptLevel * 0.12 + lockLevel * 0.1;
    assemblyRef.darkStateHalo.scale.setScalar(0.9 + Math.sin(elapsed * 3.4) * 0.04 + lockLevel * 0.1);
    assemblyRef.darkStateCore.scale.setScalar(0.92 + Math.sin(elapsed * 2.8) * 0.03 + cptLevel * 0.22);

    assemblyRef.beamGroup.visible = beamPreview > 0.03;
    assemblyRef.beamCore.material.opacity = 0.03 + beamPreview * 0.18;
    assemblyRef.beamUpper.material.opacity = 0.02 + beamPreview * 0.22;
    assemblyRef.beamLower.material.opacity = 0.02 + beamPreview * 0.19;
    assemblyRef.beamWaves.forEach((wave, index) => {
        updateBeamWave(
            wave,
            elapsed,
            beamPreview,
            resonanceLevel,
            index === 0 ? 5.4 : 6.9,
            index === 0 ? 1.4 : 2.0 + index * 0.18
        );
    });

    assemblyRef.beamPulses.forEach((pulse, index) => {
        const phase = (elapsed * (1.7 + cptLevel * 0.7) + index * 0.28) % 1;
        pulse.position.set(assemblyRef.optics.beamLocalStartX + phase * assemblyRef.optics.beamLength, 0, 0);
        pulse.scale.setScalar(0.78 + beamPreview * 0.24 + cptLevel * 0.4);
        pulse.material.opacity = beamPreview * (0.08 + cptLevel * 0.16);
    });

    assemblyRef.modulatorRings.forEach((ring, index) => {
        const phase = (elapsed * 1.4 + index / assemblyRef.modulatorRings.length) % 1;
        const scale = 0.86 + phase * 1.05;
        ring.scale.setScalar(scale);
        ring.material.opacity = opticalLevel * (1 - phase) * 0.22;
    });

    assemblyRef.vcselGroup.emitter.material.opacity = 0.03 + beamPreview * 0.18;
    assemblyRef.vcselGroup.emitter.scale.setScalar(0.92 + beamPreview * 0.16 + Math.sin(elapsed * 10) * 0.02);
    assemblyRef.vcselGroup.face.material.emissiveIntensity = 0.1 + beamPreview * 0.38;
    assemblyRef.photodiodeGroup.receiver.material.opacity = 0.08 + beamPreview * 0.26 + cptLevel * 0.18 + lockLevel * 0.18;
    assemblyRef.photodiodeGroup.receiver.scale.setScalar(0.96 + beamPreview * 0.14 + cptLevel * 0.26 + Math.sin(elapsed * 8 + 0.6) * 0.02);
    assemblyRef.photodiodeGroup.face.material.emissiveIntensity = 0.06 + beamPreview * 0.18 + lockLevel * 0.22;

    updateFlowLink(assemblyRef.links[0], elapsed, heatLevel, 0.3);
    updateFlowLink(assemblyRef.links[1], elapsed, opticalLevel, 0.46);
    updateFlowLink(assemblyRef.links[2], elapsed, cptLevel, 0.38);
    updateFlowLink(assemblyRef.links[3], elapsed, lockLevel, 0.5);

    assemblyRef.group.rotation.y = THREE.MathUtils.lerp(assemblyRef.group.rotation.y, -0.42, 0.04);
    assemblyRef.group.position.y = 1.64 + Math.sin(elapsed * 0.7) * 0.04;
}

function createPart(object, target, introOffset, baseOpacity) {
    object.position.copy(target);
    object.userData.baseScale = object.scale.clone();
    return {
        object,
        target: target.clone(),
        introOffset: introOffset.clone(),
        baseOpacity,
    };
}

function applyPart(part, reveal) {
    const eased = smoothstep01(reveal);
    TMP.v1.copy(part.target).add(part.introOffset);
    part.object.position.lerpVectors(TMP.v1, part.target, eased);
    part.object.visible = eased > 0.02;

    if (part.object.userData.baseScale) {
        part.object.scale.copy(part.object.userData.baseScale).multiplyScalar(0.82 + eased * 0.18);
    }

    setObjectOpacity(part.object, part.baseOpacity * eased);
}

function updateAtomCloud(atomCloud, elapsed, opticalLevel, cptLevel, lockLevel) {
    atomCloud.points.visible = opticalLevel > 0.03;
    atomCloud.points.material.opacity = 0.05 + opticalLevel * 0.12 + cptLevel * 0.18;
    atomCloud.points.material.size = 0.08 + lockLevel * 0.05;

    const coherence = cptLevel * 0.78 + lockLevel * 0.22;
    const preparation = THREE.MathUtils.clamp(opticalLevel * 0.9 + cptLevel * 0.35, 0, 1);
    const jitterScale = 0.06 + opticalLevel * 0.03;
    const stateSeparation = THREE.MathUtils.lerp(0.26, 0.025, coherence);
    const stateBlend = preparation * (1 - coherence * 0.32);

    for (let i = 0; i < atomCloud.count; i += 1) {
        const baseIndex = i * 3;
        const phase = elapsed * (0.65 + atomCloud.frequencies[i]) + atomCloud.phases[i];
        const coherenceScale = 1 - coherence * 0.36;
        const stateSign = atomCloud.basePositions[baseIndex] >= 0 ? 1 : -1;
        const splitTargetX = stateSign * stateSeparation;
        const splitX = THREE.MathUtils.lerp(
            atomCloud.basePositions[baseIndex] * coherenceScale,
            splitTargetX,
            stateBlend
        );
        atomCloud.positions[baseIndex] = splitX + Math.sin(phase) * jitterScale;
        atomCloud.positions[baseIndex + 1] =
            atomCloud.basePositions[baseIndex + 1] * (1 - coherence * 0.42) +
            Math.cos(phase * 1.3) * jitterScale;
        atomCloud.positions[baseIndex + 2] =
            atomCloud.basePositions[baseIndex + 2] * coherenceScale +
            Math.sin(phase * 0.8) * jitterScale;
    }

    atomCloud.points.geometry.attributes.position.needsUpdate = true;
}

function createAtomCloud(count, radius, height) {
    const geometry = new THREE.BufferGeometry();
    const positions = new Float32Array(count * 3);
    const basePositions = new Float32Array(count * 3);
    const phases = new Float32Array(count);
    const frequencies = new Float32Array(count);

    for (let i = 0; i < count; i += 1) {
        const angle = Math.random() * Math.PI * 2;
        const radial = Math.sqrt(Math.random()) * radius;
        const y = (Math.random() - 0.5) * height;
        const baseIndex = i * 3;
        basePositions[baseIndex] = Math.cos(angle) * radial;
        basePositions[baseIndex + 1] = y;
        basePositions[baseIndex + 2] = Math.sin(angle) * radial;
        positions[baseIndex] = basePositions[baseIndex];
        positions[baseIndex + 1] = basePositions[baseIndex + 1];
        positions[baseIndex + 2] = basePositions[baseIndex + 2];
        phases[i] = Math.random() * Math.PI * 2;
        frequencies[i] = 0.4 + Math.random() * 0.7;
    }

    geometry.setAttribute("position", new THREE.BufferAttribute(positions, 3));

    const points = new THREE.Points(
        geometry,
        new THREE.PointsMaterial({
            color: 0xffbf7e,
            size: 0.1,
            transparent: true,
            opacity: 0.12,
            depthWrite: false,
            blending: THREE.AdditiveBlending,
            sizeAttenuation: true,
        })
    );
    points.frustumCulled = false;

    return { points, positions, basePositions, phases, frequencies, count };
}

function createStateLobe(colorHex) {
    return new THREE.Mesh(
        new THREE.SphereGeometry(0.26, 28, 28),
        new THREE.MeshBasicMaterial({
            color: colorHex,
            transparent: true,
            opacity: 0,
            depthWrite: false,
            blending: THREE.AdditiveBlending,
        })
    );
}

function createOpticsModule(type) {
    const group = new THREE.Group();
    const isVcsel = type === "vcsel";
    const addShadowed = (mesh) => {
        mesh.castShadow = true;
        mesh.receiveShadow = true;
        group.add(mesh);
        return mesh;
    };

    const carrierMaterial = new THREE.MeshStandardMaterial({
        color: isVcsel ? 0xd8d2c8 : 0x4b545e,
        roughness: isVcsel ? 0.82 : 0.58,
        metalness: isVcsel ? 0.08 : 0.22,
    });
    const darkCeramicMaterial = new THREE.MeshStandardMaterial({
        color: isVcsel ? 0x3f2f22 : 0x1a232b,
        roughness: isVcsel ? 0.38 : 0.5,
        metalness: isVcsel ? 0.42 : 0.54,
    });
    const steelMaterial = new THREE.MeshStandardMaterial({
        color: 0xbfc9d3,
        roughness: 0.22,
        metalness: 0.96,
    });
    const copperMaterial = new THREE.MeshStandardMaterial({
        color: 0xbc8248,
        roughness: 0.24,
        metalness: 0.92,
    });
    const goldMaterial = new THREE.MeshStandardMaterial({
        color: 0xc69c52,
        roughness: 0.22,
        metalness: 0.94,
    });

    const mountBase = addShadowed(createBox(1.78, 0.12, 1.26, new THREE.MeshStandardMaterial({
        color: 0x3b454f,
        roughness: 0.48,
        metalness: 0.56,
    })));
    mountBase.position.y = -0.5;

    const carrier = addShadowed(createBox(1.42, 0.2, 0.98, carrierMaterial));
    carrier.position.y = -0.34;

    const submount = addShadowed(createBox(1.02, 0.14, 0.7, new THREE.MeshStandardMaterial({
        color: isVcsel ? 0x6d5842 : 0x2c343d,
        roughness: 0.34,
        metalness: 0.64,
    })));
    submount.position.y = -0.14;

    for (let i = -1; i <= 1; i += 1) {
        const pad = addShadowed(createBox(0.18, 0.05, 0.16, goldMaterial.clone()));
        pad.position.set(-0.34 + i * 0.34, -0.23, isVcsel ? 0.4 : -0.4);
    }

    let emitter;
    let receiver;
    let face;

    if (isVcsel) {
        const packageBody = addShadowed(createBox(0.92, 0.44, 0.7, carrierMaterial.clone()));
        packageBody.position.set(-0.08, 0.08, 0);

        const heatSpreader = addShadowed(createBox(0.56, 0.12, 0.56, copperMaterial.clone()));
        heatSpreader.position.set(-0.18, 0.26, 0);

        const die = addShadowed(createBox(0.24, 0.05, 0.22, new THREE.MeshStandardMaterial({
            color: 0x141a1f,
            roughness: 0.22,
            metalness: 0.34,
        })));
        die.position.set(0.14, 0.29, 0);

        [
            [
                new THREE.Vector3(0.05, 0.315, -0.08),
                new THREE.Vector3(-0.1, 0.48, -0.2),
                new THREE.Vector3(-0.33, 0.03, -0.22),
            ],
            [
                new THREE.Vector3(0.05, 0.315, 0.08),
                new THREE.Vector3(-0.1, 0.5, 0.22),
                new THREE.Vector3(-0.33, 0.03, 0.22),
            ],
        ].forEach((points) => {
            const bond = createTubePath(points, 0.012, goldMaterial.clone());
            group.add(bond);
        });

        const barrel = addShadowed(createCylinder(0.19, 0.19, 0.54, 24, steelMaterial.clone()));
        barrel.rotation.z = Math.PI / 2;
        barrel.position.x = 1.0;

        face = addShadowed(createCylinder(0.25, 0.25, 0.09, 24, new THREE.MeshStandardMaterial({
            color: 0x1c252d,
            roughness: 0.22,
            metalness: 0.82,
            emissive: 0xffd08f,
            emissiveIntensity: 0.1,
        })));
        face.rotation.z = Math.PI / 2;
        face.position.x = 1.24;

        const apertureRing = addShadowed(createCylinder(0.17, 0.17, 0.05, 20, copperMaterial.clone()));
        apertureRing.rotation.z = Math.PI / 2;
        apertureRing.position.x = 1.31;

        const lens = createCylinder(
            0.13,
            0.13,
            0.06,
            20,
            new THREE.MeshPhysicalMaterial({
                color: 0xffe3ba,
                roughness: 0.04,
                metalness: 0.0,
                transparent: true,
                opacity: 0.62,
                transmission: 0.94,
            })
        );
        lens.rotation.z = Math.PI / 2;
        lens.position.x = 1.36;
        lens.castShadow = true;
        lens.receiveShadow = true;
        group.add(lens);

        emitter = new THREE.Mesh(
            new THREE.CircleGeometry(0.09, 24),
            new THREE.MeshBasicMaterial({
                color: 0xff5442,
                transparent: true,
                opacity: 0.08,
                depthWrite: false,
                blending: THREE.AdditiveBlending,
            })
        );
        emitter.rotation.y = -Math.PI / 2;
        emitter.position.x = 1.34;
        group.add(emitter);

        receiver = new THREE.Mesh(
            new THREE.CircleGeometry(0.12, 24),
            new THREE.MeshBasicMaterial({
                color: 0xff8a78,
                transparent: true,
                opacity: 0.05,
                depthWrite: false,
                blending: THREE.AdditiveBlending,
            })
        );
        receiver.rotation.y = -Math.PI / 2;
        receiver.position.x = 1.39;
        group.add(receiver);
    } else {
        const packageBody = addShadowed(createBox(1.04, 0.5, 0.8, darkCeramicMaterial.clone()));
        packageBody.position.set(0.12, 0.06, 0);

        const detectorBody = addShadowed(createBox(0.48, 0.38, 0.62, new THREE.MeshStandardMaterial({
            color: 0x0f171d,
            roughness: 0.52,
            metalness: 0.34,
        })));
        detectorBody.position.set(-0.58, 0.06, 0);

        const sensorFrame = addShadowed(createCylinder(0.26, 0.26, 0.12, 24, steelMaterial.clone()));
        sensorFrame.rotation.z = Math.PI / 2;
        sensorFrame.position.x = -1.12;

        face = addShadowed(createCylinder(0.2, 0.2, 0.06, 24, new THREE.MeshStandardMaterial({
            color: 0x050a0f,
            roughness: 0.34,
            metalness: 0.22,
            emissive: 0x8bdfff,
            emissiveIntensity: 0.04,
        })));
        face.rotation.z = Math.PI / 2;
        face.position.x = -1.24;

        const filterWindow = createCylinder(
            0.14,
            0.14,
            0.06,
            20,
            new THREE.MeshPhysicalMaterial({
                color: 0x9edfff,
                roughness: 0.04,
                metalness: 0.0,
                transparent: true,
                opacity: 0.5,
                transmission: 0.9,
            })
        );
        filterWindow.rotation.z = Math.PI / 2;
        filterWindow.position.x = -1.35;
        filterWindow.castShadow = true;
        filterWindow.receiveShadow = true;
        group.add(filterWindow);

        const sensor = new THREE.Mesh(
            new THREE.PlaneGeometry(0.28, 0.28),
            new THREE.MeshStandardMaterial({
                color: 0x08131a,
                roughness: 0.18,
                metalness: 0.1,
                emissive: 0x69d0ff,
                emissiveIntensity: 0.08,
            })
        );
        sensor.rotation.y = Math.PI / 2;
        sensor.position.x = -1.16;
        group.add(sensor);

        [
            [
                new THREE.Vector3(-0.92, 0.08, -0.09),
                new THREE.Vector3(-0.58, 0.42, -0.18),
                new THREE.Vector3(-0.08, 0.18, -0.18),
            ],
            [
                new THREE.Vector3(-0.92, 0.08, 0.09),
                new THREE.Vector3(-0.58, 0.44, 0.18),
                new THREE.Vector3(-0.08, 0.18, 0.18),
            ],
        ].forEach((points) => {
            const bond = createTubePath(points, 0.012, goldMaterial.clone());
            group.add(bond);
        });

        receiver = new THREE.Mesh(
            new THREE.PlaneGeometry(0.34, 0.34),
            new THREE.MeshBasicMaterial({
                color: 0xa4e2ff,
                transparent: true,
                opacity: 0.12,
                depthWrite: false,
                blending: THREE.AdditiveBlending,
            })
        );
        receiver.rotation.y = Math.PI / 2;
        receiver.position.x = -1.42;
        group.add(receiver);
    }

    return { group, emitter, receiver, face };
}
function createBeamWave(length, radius, colorHex, phaseOffset, cycles) {
    const pointCount = 72;
    const positions = new Float32Array(pointCount * 3);
    const geometry = new THREE.BufferGeometry();
    geometry.setAttribute("position", new THREE.BufferAttribute(positions, 3));

    const line = new THREE.Line(
        geometry,
        new THREE.LineBasicMaterial({
            color: colorHex,
            transparent: true,
            opacity: 0,
            depthWrite: false,
            blending: THREE.AdditiveBlending,
        })
    );
    line.frustumCulled = false;

    return { line, positions, pointCount, length, radius, phaseOffset, cycles };
}

function updateBeamWave(wave, elapsed, strength, resonance, cycles, speed) {
    const amplitude = wave.radius * (0.25 + strength * 0.82) * (0.78 + resonance * 0.35);
    const effectiveCycles = cycles + resonance * 0.9;

    for (let i = 0; i < wave.pointCount; i += 1) {
        const t = i / (wave.pointCount - 1);
        const baseIndex = i * 3;
        const angle = t * effectiveCycles * Math.PI * 2 - elapsed * speed + wave.phaseOffset * Math.PI * 2;
        wave.positions[baseIndex] = -wave.length * 0.5 + t * wave.length;
        wave.positions[baseIndex + 1] = Math.cos(angle) * amplitude;
        wave.positions[baseIndex + 2] = Math.sin(angle) * amplitude * 0.9;
    }

    wave.line.geometry.attributes.position.needsUpdate = true;
    wave.line.material.opacity = strength * (0.06 + resonance * 0.12);
}

function createBillboardLabel(text, tintHex, options = {}) {
    const canvasTex = document.createElement("canvas");
    canvasTex.width = 512;
    canvasTex.height = 128;
    const ctx = canvasTex.getContext("2d");

    ctx.clearRect(0, 0, canvasTex.width, canvasTex.height);
    ctx.fillStyle = `rgba(7, 16, 22, ${options.backgroundAlpha ?? 0.72})`;
    roundRect(ctx, 10, 18, canvasTex.width - 20, canvasTex.height - 36, 24);
    ctx.fill();
    ctx.strokeStyle = `rgba(149, 220, 255, ${options.borderAlpha ?? 0.3})`;
    ctx.lineWidth = 3;
    roundRect(ctx, 10, 18, canvasTex.width - 20, canvasTex.height - 36, 24);
    ctx.stroke();

    ctx.fillStyle = tintHex;
    ctx.font = `700 ${options.fontSize ?? 38}px Bahnschrift, Segoe UI, sans-serif`;
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    ctx.fillText(text, canvasTex.width / 2, canvasTex.height / 2 + 2);

    const texture = new THREE.CanvasTexture(canvasTex);
    texture.colorSpace = THREE.SRGBColorSpace;

    const sprite = new THREE.Sprite(new THREE.SpriteMaterial({
        map: texture,
        transparent: true,
        opacity: 0,
        depthWrite: false,
    }));
    sprite.scale.set(options.scaleX ?? 2.8, options.scaleY ?? 0.72, 1);
    return sprite;
}

function createElectronicsBlock(width, height, depth, colorHex, accentHex) {
    const group = new THREE.Group();

    const body = createBox(width, height, depth, new THREE.MeshStandardMaterial({
        color: colorHex,
        roughness: 0.38,
        metalness: 0.52,
    }));
    body.castShadow = true;
    body.receiveShadow = true;
    group.add(body);

    const accent = createBox(width * 0.78, 0.08, depth * 0.78, new THREE.MeshStandardMaterial({
        color: 0x10151b,
        roughness: 0.48,
        metalness: 0.24,
        emissive: accentHex,
        emissiveIntensity: 0.18,
    }));
    accent.position.y = height * 0.52;
    group.add(accent);

    return group;
}

function createFlowLink(points, colorHex, phaseOffset) {
    const curve = new THREE.CatmullRomCurve3(points, false, "centripetal");
    const tube = new THREE.Mesh(
        new THREE.TubeGeometry(curve, 48, 0.06, 10, false),
        new THREE.MeshStandardMaterial({
            color: 0x3c464f,
            roughness: 0.48,
            metalness: 0.52,
            transparent: true,
            opacity: 0,
        })
    );
    tube.castShadow = true;
    tube.receiveShadow = true;

    const pulse = new THREE.Mesh(
        new THREE.SphereGeometry(0.11, 14, 14),
        new THREE.MeshBasicMaterial({
            color: colorHex,
            transparent: true,
            opacity: 0,
            depthWrite: false,
            blending: THREE.AdditiveBlending,
        })
    );

    return { curve, tube, pulse, phaseOffset };
}

function updateFlowLink(link, elapsed, strength, speed) {
    const visible = strength > 0.03;
    link.tube.visible = visible;
    link.pulse.visible = visible;
    link.tube.material.opacity = strength * 0.24;
    link.pulse.material.opacity = strength * 0.6;

    if (!visible) {
        return;
    }

    const t = (elapsed * speed + link.phaseOffset) % 1;
    link.pulse.position.copy(link.curve.getPointAt(t));
    link.pulse.scale.setScalar(0.7 + strength * 0.7);
}

function createBeamCylinder(length, radius, colorHex, opacity) {
    const mesh = createCylinder(
        radius,
        radius,
        length,
        18,
        new THREE.MeshBasicMaterial({
            color: colorHex,
            transparent: true,
            opacity,
            depthWrite: false,
            blending: THREE.AdditiveBlending,
        })
    );
    mesh.rotation.z = Math.PI / 2;
    return mesh;
}

function createTubePath(points, radius, material) {
    const curve = new THREE.CatmullRomCurve3(points, false, "catmullrom");
    const geometry = new THREE.TubeGeometry(curve, Math.max(20, points.length * 8), radius, 10, false);
    const mesh = new THREE.Mesh(geometry, material);
    mesh.castShadow = true;
    mesh.receiveShadow = true;
    return mesh;
}

function createBox(width, height, depth, material) {
    return new THREE.Mesh(new THREE.BoxGeometry(width, height, depth), material);
}

function createCylinder(radiusTop, radiusBottom, height, segments, material) {
    return new THREE.Mesh(new THREE.CylinderGeometry(radiusTop, radiusBottom, height, segments), material);
}

function makeBackdropTexture() {
    const canvasTex = document.createElement("canvas");
    canvasTex.width = 32;
    canvasTex.height = 1024;
    const ctx = canvasTex.getContext("2d");

    const gradient = ctx.createLinearGradient(0, 0, 0, canvasTex.height);
    gradient.addColorStop(0.0, "#64717d");
    gradient.addColorStop(0.22, "#4d5863");
    gradient.addColorStop(0.56, "#232b35");
    gradient.addColorStop(1.0, "#0b1015");
    ctx.fillStyle = gradient;
    ctx.fillRect(0, 0, canvasTex.width, canvasTex.height);

    ctx.fillStyle = "rgba(255,255,255,0.08)";
    ctx.fillRect(0, canvasTex.height * 0.18, canvasTex.width, canvasTex.height * 0.05);
    ctx.fillStyle = "rgba(142, 210, 255, 0.09)";
    ctx.fillRect(0, canvasTex.height * 0.42, canvasTex.width, canvasTex.height * 0.04);
    ctx.fillStyle = "rgba(245, 188, 127, 0.06)";
    ctx.fillRect(0, canvasTex.height * 0.54, canvasTex.width, canvasTex.height * 0.04);
    ctx.fillStyle = "rgba(255,255,255,0.04)";
    ctx.fillRect(0, canvasTex.height * 0.72, canvasTex.width, canvasTex.height * 0.03);

    const texture = new THREE.CanvasTexture(canvasTex);
    texture.colorSpace = THREE.SRGBColorSpace;
    return texture;
}

function roundRect(ctx, x, y, width, height, radius) {
    ctx.beginPath();
    ctx.moveTo(x + radius, y);
    ctx.lineTo(x + width - radius, y);
    ctx.quadraticCurveTo(x + width, y, x + width, y + radius);
    ctx.lineTo(x + width, y + height - radius);
    ctx.quadraticCurveTo(x + width, y + height, x + width - radius, y + height);
    ctx.lineTo(x + radius, y + height);
    ctx.quadraticCurveTo(x, y + height, x, y + height - radius);
    ctx.lineTo(x, y + radius);
    ctx.quadraticCurveTo(x, y, x + radius, y);
    ctx.closePath();
}

function getMaterials(root) {
    const materials = [];
    root.traverse((child) => {
        if (!child.material) {
            return;
        }

        if (Array.isArray(child.material)) {
            child.material.forEach((material) => materials.push(material));
        } else {
            materials.push(child.material);
        }
    });
    return materials;
}

function setObjectOpacity(root, opacity) {
    root.traverse((child) => {
        if (!child.material) {
            return;
        }

        const materials = Array.isArray(child.material) ? child.material : [child.material];
        materials.forEach((material) => {
            if (material.userData.baseOpacity === undefined) {
                material.userData.baseOpacity = material.opacity === undefined ? 1 : material.opacity;
            }
            if ("opacity" in material) {
                material.transparent = true;
                material.opacity = material.userData.baseOpacity * opacity;
            }
        });
    });
}

function updateBillboardLabel(label, opacity) {
    label.visible = opacity > 0.02;
    label.material.opacity = THREE.MathUtils.clamp(opacity, 0, 0.96);
}

function rangeProgress(value, min, max) {
    return THREE.MathUtils.clamp((value - min) / Math.max(max - min, 0.0001), 0, 1);
}

function smoothstep01(value) {
    return value * value * (3 - 2 * value);
}

function damp(current, target, lambda, delta) {
    return THREE.MathUtils.lerp(current, target, 1 - Math.exp(-lambda * delta));
}

} catch (error) {
    showFatalError(`Simulation startup failed: ${error.message}`);
    console.error(error);
}
})();

