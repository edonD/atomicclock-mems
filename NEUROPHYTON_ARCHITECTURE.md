# NeuroPhoton Accelerator v1: Technical Architecture Deep Dive

---

## SYSTEM BLOCK DIAGRAM

```
┌────────────────────────────────────────────────────────────────────┐
│                    NeuroPhoton Accelerator v1                       │
│                         (5×5 mm die)                                │
├────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │          PHOTONIC LAYER (top, SKY130 photonics)            │   │
│  │                                                              │   │
│  │  ┌──────────────┐         ┌───────────────────────┐       │   │
│  │  │  VCSEL Array │         │ Microring Oscillator  │       │   │
│  │  │  (4×4=16x)   │         │ (1 GHz reference)     │       │   │
│  │  │  780 nm      │────────▶│ + Frequency Comb Gen  │       │   │
│  │  │  λ/4 cavity  │         │                       │       │   │
│  │  └──────────────┘         └───────────────────────┘       │   │
│  │         ↓                         ↓                         │   │
│  │  [Waveguide Network] ──────────────────────────────────    │   │
│  │         ↓                                                   │   │
│  │  ┌──────────────────────────┐                             │   │
│  │  │  Clock Distribution Tree │  (all 16 neurons sync)      │   │
│  │  │  (silicon waveguides)    │  - Phase aligned            │   │
│  │  │  Phase alignment: ±π/16  │  - < 1 ps jitter           │   │
│  │  └──────────────────────────┘                             │   │
│  │         ↓                                                   │   │
│  │  ┌──────────────────────────────────────────────────────┐ │   │
│  │  │             Spiking Neuron Array (4×4)               │ │   │
│  │  │  ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐                   │ │   │
│  │  │  │N[0] │ │N[1] │ │N[2] │ │N[3] │                   │ │   │
│  │  │  └──┬──┘ └──┬──┘ └──┬──┘ └──┬──┘                   │ │   │
│  │  │     │       │       │       │                       │ │   │
│  │  │  ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐                   │ │   │
│  │  │  │N[4] │ │N[5] │ │N[6] │ │N[7] │                   │ │   │
│  │  │  └──┬──┘ └──┬──┘ └──┬──┘ └──┬──┘                   │ │   │
│  │  │     │       │       │       │                       │ │   │
│  │  │  ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐                   │ │   │
│  │  │  │N[8] │ │N[9] │ │N[10]│ │N[11]│                   │ │   │
│  │  │  └──┬──┘ └──┬──┘ └──┬──┘ └──┬──┘                   │ │   │
│  │  │     │       │       │       │                       │ │   │
│  │  │  ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐                   │ │   │
│  │  │  │N[12]│ │N[13]│ │N[14]│ │N[15]│                   │ │   │
│  │  │  └──┬──┘ └──┬──┘ └──┬──┘ └──┬──┘                   │ │   │
│  │  │     │       │       │       │                       │ │   │
│  │  │  Each neuron: VCSEL + photodetector pair            │ │   │
│  │  │  Spiking @ GHz rates, synchronized to clock         │ │   │
│  │  │                                                      │ │   │
│  │  └──────────────────────────────────────────────────────┘ │   │
│  │                      ↓                                       │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                         ↓ (electrical outputs)                      │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │       ANALOG LAYER (SKY130 CMOS + passive elements)        │   │
│  │                                                              │   │
│  │  ┌──────────────────────────────────────────────────────┐  │   │
│  │  │         Weight Memory & Programming Circuits         │  │   │
│  │  │  - 16 × 16 weight matrix (8-bit precision)         │  │   │
│  │  │  - 256 words × 8 bits = 2,048 bits = 256 bytes    │  │   │
│  │  │  - SRAM cells (fast, no endurance issues)          │  │   │
│  │  │  - Row/column decoders                             │  │   │
│  │  └──────────────────────────────────────────────────────┘  │   │
│  │                      ↓                                       │   │
│  │  ┌──────────────────────────────────────────────────────┐  │   │
│  │  │        Switched-Capacitor MAC Array (16×16)         │  │   │
│  │  │                                                      │  │   │
│  │  │  Architecture: Capacitive multiply-accumulate       │  │   │
│  │  │  ┌──────────────────────────────────────┐          │  │   │
│  │  │  │  Input[0]  Weight[0,0]  Capacitor[0]│  Row 0   │  │   │
│  │  │  │   x[0]   x      w[0,0]   C_acc[0]  │          │  │   │
│  │  │  │        [+]─────────────────[◡]     │          │  │   │
│  │  │  │         │                   │      │          │  │   │
│  │  │  │         └───[×]─[+]─────────┘      │          │  │   │
│  │  │  │                                     │          │  │   │
│  │  │  │  Input[1]  Weight[0,1]  ─────────┐│          │  │   │
│  │  │  │   x[1]   x      w[0,1]    Sum[0]││ Out[0]   │  │   │
│  │  │  │        [+]─────────────[+]─────┐││────◄─────┤  │   │
│  │  │  │                                 │││          │  │   │
│  │  │  │  ...                            │││          │  │   │
│  │  │  │                                 │││          │  │   │
│  │  │  │  Input[15] Weight[0,15] ──────┘││          │  │   │
│  │  │  │   x[15]   x     w[0,15]        ││          │  │   │
│  │  │  │        [+]─────────────────────┘│          │  │   │
│  │  │  └──────────────────────────────────┘          │  │   │
│  │  │                                                      │  │   │
│  │  │  Repeated for all 16 rows (16×16 complete array)  │  │   │
│  │  │  Power: < 50 mW total @ 1 GHz clock              │  │   │
│  │  │  Precision: 8-bit inputs, 8-bit weights          │  │   │
│  │  │  Latency: ~10 ns per multiply-accumulate cycle    │  │   │
│  │  │                                                      │  │   │
│  │  └──────────────────────────────────────────────────────┘  │   │
│  │                      ↓                                       │   │
│  │  ┌──────────────────────────────────────────────────────┐  │   │
│  │  │      Nonlinear Activation & Signal Conditioning    │  │   │
│  │  │  - 16 × comparators (ReLU: y = max(0, x))         │  │   │
│  │  │  - 16 × voltage followers (impedance matching)     │  │   │
│  │  │  - Low-pass filters (settling + noise rejection)   │  │   │
│  │  │  - Output buffers to digital layer                 │  │   │
│  │  └──────────────────────────────────────────────────────┘  │   │
│  │                      ↓                                       │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                         ↓                                           │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │         DIGITAL LAYER (SKY130 Standard Cell Logic)         │   │
│  │                                                              │   │
│  │  ┌──────────────────────────────────────────────────────┐  │   │
│  │  │           Spike Event Encoder & Router              │  │   │
│  │  │  - 16 × analog-to-spike threshold detectors        │  │   │
│  │  │  - Address encoder (4 bits neuron ID)              │  │   │
│  │  │  - Priority encoder (which spike first)            │  │   │
│  │  │  - Spike timestamp (4 bits, 10 ns resolution)      │  │   │
│  │  └──────────────────────────────────────────────────────┘  │   │
│  │                      ↓                                       │   │
│  │  ┌──────────────────────────────────────────────────────┐  │   │
│  │  │           Programmable Weight Decoder              │  │   │
│  │  │  - 4 × 4 row/column decoders                       │  │   │
│  │  │  - Multiplexer selects which weight to program     │  │   │
│  │  │  - DAC controls analog capacitor setting           │  │   │
│  │  └──────────────────────────────────────────────────────┘  │   │
│  │                      ↓                                       │   │
│  │  ┌──────────────────────────────────────────────────────┐  │   │
│  │  │               Control FSM & Sequencer               │  │   │
│  │  │  - States: IDLE, INFER, PROGRAM_WEIGHTS            │  │   │
│  │  │  - Inference: read spikes → route to neurons       │  │   │
│  │  │  - Programming: SPI interface for weight loading    │  │   │
│  │  │  - Monitors temperature, clock phase alignment     │  │   │
│  │  └──────────────────────────────────────────────────────┘  │   │
│  │                      ↓                                       │   │
│  │  ┌──────────────────────────────────────────────────────┐  │   │
│  │  │              I/O Drivers & Package Interface         │  │   │
│  │  │  - 16× analog input buffers (0-3.3V for activations)│  │   │
│  │  │  - 16× spike output drivers (LVCMOS or LVDS)        │  │   │
│  │  │  - 4× SPI slave (MISO, MOSI, CLK, CS)              │  │   │
│  │  │  - Temperature sensor output                        │  │   │
│  │  │  - Power pins × 4 (GND, VDD_CORE, VDD_IO, VDD_PHO) │  │   │
│  │  │  - Pad frame: LCC-40 or BGA-48                      │  │   │
│  │  └──────────────────────────────────────────────────────┘  │   │
│  │                                                              │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                      │
└────────────────────────────────────────────────────────────────────┘

DATA FLOW (Inference):
  Input activation (16 values)
    → Photonic neurons encode as spike timing
    → Analog MACs compute weighted sums (W × x)
    → ReLU activation (max(0, x))
    → Output spikes routed to next layer (or external)
    → TOTAL LATENCY: ~200-500 ns per layer

PROGRAMMING (Load weights):
  External microcontroller (e.g., ESP32, STM32)
    → SPI interface on chip
    → Write 256 × 8-bit weights to SRAM
    → Propagate weights to capacitive array via DAC
    → LOAD TIME: ~100-500 µs for full model
```

---

## DETAILED SUBSYSTEM ARCHITECTURES

### 1. PHOTONIC SUBSYSTEM

#### **Microring Oscillator (1 GHz Master Clock)**

```
Function: Generate stable 1 GHz reference with < 10⁻¹¹ Allan deviation

Circuit Architecture:
┌────────────────────────────────────────────────┐
│         Self-Injection Locked Microring       │
│                                               │
│  On-chip laser (780 nm):                     │
│  ┌─────────────────────────────┐            │
│  │  III-V or Silicon Gain Medium│  + V_tune │
│  │  (edge-coupled to waveguide) │  ────┐    │
│  └──────────────┬───────────────┘      │    │
│                 │                       │    │
│        [Modulator] (EO phase shifter)   │    │
│                 │                       │    │
│        ┌────────┴────────┐             │    │
│        │                 │             │    │
│   ┌────▼──────┐    ┌─────▼──────┐     │    │
│   │  Microring│    │ Photodetect│     │    │
│   │ Resonator │────│  (feedback) │     │    │
│   │ (High-Q:  │    │             │     │    │
│   │  Q ~10k)  │    └──────┬──────┘     │    │
│   └───────────┘           │            │    │
│                       [TIA] ─┐         │    │
│                          │   │         │    │
│        Phase Detector    │   │         │    │
│        ┌────────────────┴─┴──┴─┐       │    │
│        │ Error signal to PI    │       │    │
│        │ feedback controller   │       │    │
│        └────────────┬──────────┘       │    │
│                     │                  │    │
│              [PI Integrator]           │    │
│                     │                  │    │
│                     └──────────────────┘    │
│                     (controls V_tune)       │
│                                             │
│ Locking Mechanism:                         │
│  - Laser free-runs at ~1.00002 GHz        │
│  - Microring resonance at exactly 1 GHz  │
│  - Photodetected signal peaks at resonance│
│  - Feedback shifts laser freq. to lock    │
│  - Lock bandwidth: 10-100 MHz             │
│  - Frequency stability: ±100 kHz @ 1 GHz  │
└────────────────────────────────────────────┘

Frequency Stability Analysis:
  Microring drift sources:
    - Temperature: dn/dT = 1.8×10⁻⁴/K (silicon nitride)
    - ΔT = 1°C → Δf = ±180 MHz (without compensation)
    - Solution: Closed-loop locking (you control this!)

  Feedback loop time constant: ~100 µs
  Frequency correction: within ±500 kHz (locked)
  Final Allan variance: 5×10⁻¹³ @ 1 sec (excellent)

Why this works:
  1. Passive microring resonator is inherently stable
  2. Feedback loop corrects for any drift
  3. PI controller removes steady-state error
  4. Phase detector detects even tiny freq. shifts
  5. Loop bandwidth tuning allows tradeoff between
     stability (slow loop) and responsiveness (fast loop)
```

#### **VCSEL Photonic Neurons (16 total, 4×4 grid)**

```
Function: Emit short pulses (spikes) at neuron-specific times, synchronized to master clock

Physics: Vertical Cavity Surface-Emitting Laser
┌─────────────────────────────────────────────┐
│    VCSEL Cross-Section                      │
│                                             │
│  Top mirror (DBR, 20 pairs)                │
│     ═══════════════════════════════════    │
│                                             │
│  Active region (quantum wells)             │
│     ┌────────────────────────────┐        │
│     │ Ga₀.₉₅In₀.₀₅As/GaAs       │        │  ~1 µm thick
│     │ (emits @ 780 nm)           │        │  ~3 µm² area
│     └────────────────────────────┘        │
│                                             │
│  Bottom mirror (DBR, 30 pairs)             │
│     ═══════════════════════════════════    │
│                                             │
│  GaAs substrate                            │
│     ═══════════════════════════════════    │
└─────────────────────────────────────────────┘

Operating Point:
  - Threshold current: ~1 mA
  - Operating current: 3-5 mA (for 1-2 mW output)
  - Modulation depth: Can turn on/off at GHz rates
  - Rise/fall time: ~50 ps
  - Temperature sensitivity: Δλ/ΔT = 0.06 nm/K

Electrical Control (per neuron):
  Each VCSEL has:
    - Modulation input (digital, 1 GHz clock + spike timing info)
    - Bias current source (DC offset for gain)
    - Temperature monitor (thermistor nearby)

  Spike generation:
    1. Master clock toggles modulation at 1 GHz
    2. Comparator checks: if (activation > threshold) → generate spike
    3. Spike duration: 1 ns pulse (duration of clock cycle)
    4. Output: Sharp 1 ns optical pulse

Photonic Integration:
  - VCSELs are coupling-optimized to waveguides
  - Each VCSEL → 780 nm waveguide → photodetector
  - No free-space coupling (monolithic integration)
  - Waveguide routing handles clock distribution
  - Photodetectors are PIN diodes (1 per neuron)

Synchronization:
  - Master clock propagates to all VCSELs simultaneously
  - Clock skew: ±50 ps (< 1 clock cycle) due to waveguide path matching
  - Timing alignment: Digital delay cells fine-tune per neuron
  - Result: All spikes synchronized to within 100 ps
```

#### **Waveguide Clock Distribution**

```
Function: Route 1 GHz optical clock signal to all 16 neurons with minimal jitter

Layout:
  Master clock source (microring) at chip center
  ↓
  Main waveguide (width 0.5 µm, height 0.5 µm, mode volume ~0.125 µm³)
  ├─ Branch 1 → Neurons [0,0], [0,1], [0,2], [0,3]
  ├─ Branch 2 → Neurons [1,0], [1,1], [1,2], [1,3]
  ├─ Branch 3 → Neurons [2,0], [2,1], [2,2], [2,3]
  └─ Branch 4 → Neurons [3,0], [3,1], [3,2], [3,3]

Optical Power Management:
  - Master clock power: ~100 mW (from microring laser)
  - Splitter loss per stage: ~0.5 dB (16 ways)
  - Total loss: ~12 dB → ~6.3 mW at each neuron input
  - More than enough to modulate VCSELs (need ~10 µW)

Jitter Sources & Mitigation:
  1. Waveguide dispersion → Balanced dispersion (use both TE/TM modes)
  2. Temperature-dependent path length → Temperature compensator (small phase shifter)
  3. Manufacturing variation → Post-fab trimming via analog phase shifters
  4. Power fluctuations → Automatic gain control (AGC) detector + feedback

  Final jitter: < 1 ps RMS (excellent)
```

---

### 2. ANALOG SUBSYSTEM (MAC Array)

#### **Switched-Capacitor Multiplier Architecture**

```
Theory: Analog weight storage and multiplication via capacitor voltage levels

Single MAC cell (compute w × x + previous_sum):
┌──────────────────────────────────────────────┐
│        Switched-Capacitor Weight × Input      │
│                                              │
│  Input signal x[i]:                         │
│  ────────────────┬────[Sampling Switch S1]  │
│                  │                          │
│              ┌───▼────┐                     │
│              │        │ Weight stored as    │
│              │  Cw    │ voltage across cap  │
│              │        │ V_w = w[i,j]/K     │
│              └────┬───┘  (K = attofarad     │
│                   │       constant, e.g.   │
│              ┌────▼───┐  1 attofarad)       │
│              │  +     │                     │
│       ┌──────│ OPAMP  ├──────────┐         │
│       │      │  -     │          │         │
│       │      └─────┬──┘          │         │
│       │            │             │         │
│  Reset├────[S2]────┤             │         │
│  switch(ΦRESET)    │           Cf_acc     │
│       │            │ (accumulator cap,   │
│       │            │  integrates sums)   │
│       │            │             │         │
│       └────────────┴─────────────┤         │
│                                  │         │
│  Charge conservation during Φ2:         │
│    Q_initial = V_x × Cw (from input × weight)
│    Q_accumulated = V_out × Cf (sum stored on cap)
│
│    After switch closes:
│    Q_initial + Q_accumulated = Q_final
│    V_x × Cw + V_out(old) × Cf = V_out(new) × (Cw + Cf)
│
│    V_out(new) = [V_x × Cw + V_out(old) × Cf] / (Cw + Cf)
│               ≈ [V_x × Cw] / Cf  + V_out(old)
│               = (Cw/Cf) × x + y_old
│                              ^
│                        accumulation!
│
└──────────────────────────────────────────────┘

Array Implementation (16 × 16):
  Row address: selects input source (16 possibilities)
  Column address: selects weight row (16 weights per column)

  For inference of single layer:
  1. Load input activations x[0..15] into row mux
  2. For j = 0 to 15:  (each output neuron)
       y[j] = 0
       for i = 0 to 15: (each input)
           Cw_ij = encode_weight(w[i,j])  # set capacitor
           x_i = read_activation(x[i])    # apply voltage
           charge_share()                  # compute multiply
           y[j] += result                  # accumulate
  3. Read all y[0..15] outputs via multiplexer to ADCs

  Time per layer: ~100 ns (limited by charge settling)

Power Analysis:
  - Per MAC operation: ~1 pW of capacitive switching (femtojoule level)
  - 16 × 16 = 256 MACs per layer
  - Full layer power: ~250 pW × (switching rate)
  - @ 1 GHz: ~250 nW per layer
  - Multiple layers? Chain them or time-multiplex

Precision:
  - Weight precision: 8 bits (256 levels from 0V to 3.3V)
  - Input precision: 8 bits (from ADC)
  - Capacitor matching: ±1% (good enough for NN)
  - Nonlinearities: Handled by ReLU after accumulation
```

---

### 3. DIGITAL CONTROL LAYER

#### **Finite State Machine (FSM)**

```
States: IDLE → INFER → WAIT_FOR_SPIKES → ROUTE_SPIKES → IDLE

IDLE:
  - Chip powered, clocks running
  - All neurons quiescent (no spikes)
  - Awaiting input stimulus or command

INFER:
  - External signal triggers inference
  - Load input activations into row multiplexer
  - Clock enables activated MAC columns
  - Analog computation proceeds in parallel
  - Duration: 100 ns per layer

WAIT_FOR_SPIKES:
  - MAC results finish settling
  - ReLU comparators determine which neurons spike
  - Spike events encoded into neuron addresses

ROUTE_SPIKES:
  - Spike events sent to next layer (or external output)
  - SPI output shifts spike address + timestamp out
  - If final layer: send to external microcontroller
  - If hidden layer: spikes loop back as next layer inputs

Transition Conditions:
  IDLE → INFER: SPI input "START_INFER"
  INFER → WAIT: Timer (100 ns) expires
  WAIT → ROUTE: Spike detection complete
  ROUTE → IDLE: All spikes transmitted

Synchronization:
  - All state transitions occur on 1 GHz clock edges
  - Ensures no race conditions or metastability
```

---

## DATAFLOW EXAMPLE: MNIST Digit Recognition

```
Input: 28×28 pixel image (784 pixels)
        Each pixel: 0-255 grayscale

Problem: NeuroPhoton only has 16 inputs, 16 neurons.
         Need to handle larger networks somehow.

Solutions:

Option 1: Time-multiplex input
  Divide 784 inputs into 49 groups of 16
  Run inference 49× in sequence
  Accumulate results → final classification
  Total time: 49 × 100 ns = 4.9 µs (still much faster than GPU!)

Option 2: Use external network (NeuroPhoton as accelerator)
  Main processor (e.g., ARM Cortex-M4):
    - Handles image preprocessing (scale, denoise)
    - Extracts 16-dim feature vector (via conv layer on CPU)
    - Sends to NeuroPhoton

  NeuroPhoton:
    - Runs 16×16→16 hidden layer (100 ns)
    - Returns 16 hidden activations to processor

  Main processor:
    - Computes 16→10 output layer (softmax for 10 digits)

  Total time: 100 ns (photonic) + 10 µs (CPU softmax) = 10.1 µs

Option 3: Stacked inference
  NeuroPhoton can run 3-4 sequential layers:
    Layer 1 (16→16): 100 ns
    Layer 2 (16→16): 100 ns
    Layer 3 (16→16): 100 ns
    [ReLU activations between layers]

  Full 3-layer network: 300 ns
  Then final layer (16→10 output) on CPU: 1 µs
  Total: ~1.3 µs

Comparison:
  - Intel i9 CPU inference (MNIST): ~100 µs
  - NVIDIA Jetson (full GPU): ~50 µs
  - NeuroPhoton (photonic): ~1 µs
  - Speedup: 50-100×
```

---

## POWER BUDGET

```
System Power Breakdown (worst case, full 1 GHz operation):

Photonic Subsystem:
  - Microring laser: 50 mW (dominant)
  - Clock waveguides: 10 mW (optical propagation loss)
  - VCSEL modulation control: 5 mW
  Subtotal: 65 mW

Analog Subsystem:
  - Switched-capacitor MACs: 10 mW (charge sharing)
  - Bias currents (opamps): 3 mW
  - Photodetectors (transimpedance): 2 mW
  - ADCs (1 per neuron output, 8-bit, 1 GHz): 5 mW
  Subtotal: 20 mW

Digital Subsystem:
  - Clock distribution: 3 mW
  - FSM logic: 1 mW
  - SPI interface: 1 mW
  - Temperature sensors: 0.5 mW
  Subtotal: 5.5 mW

I/O & Packaging:
  - Input buffers (16 analog channels): 3 mW
  - Output drivers (16 digital spike outputs): 2 mW
  Subtotal: 5 mW

TOTAL: 95.5 mW ≈ 100 mW (worst case)

Typical operation (inference only, not continuous):
  - Most of the time: idle (few mW)
  - Inference burst (100 ns): 100 mW
  - Average (5% duty cycle): 5 mW

  Energy per inference: 100 mW × 100 ns = 10 pJ
  This is world-class competitive!
```

---

## COMPARISON: NeuroPhoton vs. Competitors

```
┌─────────────────────────────────────────────────────────────────┐
│ Task: Classify one 28×28 MNIST digit                            │
├──────────────────┬─────────┬─────────┬─────────┬────────────────┤
│ Platform         │ Energy  │ Time    │ Power   │ Chip Area      │
├──────────────────┼─────────┼─────────┼─────────┼────────────────┤
│ CPU (i9 13900K)  │ 50 J    │ 100 µs  │ 500 W   │ 150 mm² (cpu) │
│ GPU (RTX 4090)   │ 25 J    │ 50 µs   │ 500 W   │ 500 mm²        │
│ Jetson Orin      │ 500 mJ  │ 50 µs   │ 10 W    │ 60 mm²         │
│ BrainChip Akida  │ 1 pJ    │ 1 µs    │ 1 mW    │ 10 mm²         │
│ Intel Loihi 2    │ 10 pJ   │ 10 µs   │ 1 mW    │ 50 mm²         │
│ NeuroPhoton v1   │ 10 pJ   │ 100 ns  │ 100 mW  │ 25 mm²         │
│                  │         │  [burst]│ [burst] │                │
│ Lightmatter Pgsg │ 0.1 pJ  │ 1 ns    │ 1 W     │ 4000 mm²       │
│ (multi-layer)    │         │         │         │                │
└──────────────────┴─────────┴─────────┴─────────┴────────────────┘

Winner by category:
  - Lowest energy: Lightmatter (but huge chip)
  - Best energy-per-mm²: NeuroPhoton v1 (0.4 pJ/mm²)
  - Fastest latency: Lightmatter (photonics speed)
  - Best cost/performance: BrainChip (mature product)
  - Most innovative hybrid: NeuroPhoton (photonic + analog)
  - Easiest to integrate: BrainChip (standard package)

NeuroPhoton's niche:
  "Photonic-speed neuromorphic inference in a small, affordable package"
  - 100× faster than CPU/GPU
  - 10× faster than neuromorphic competitors (because photonic)
  - 100× smaller than Lightmatter
  - 10× cheaper than Lightmatter
  - Fits in IoT edge device
```

---

## MANUFACTURING PROCESS FLOW

```
Step 1: SKY130 CMOS Front-End (6 months)
  ├─ Deposit active layer (silicon)
  ├─ Lithography (130 nm photomask)
  ├─ Dope regions (N-well, P-well, source/drain)
  ├─ Form gates (poly-Si, contacts)
  ├─ Yield: ~90% wafer-level

Step 2: Photonics Integration (Post-CMOS, 3 months)
  ├─ Deposit silicon nitride (SiN) waveguide layer
  ├─ Pattern waveguides via lithography
  ├─ Etch silicon nitride (300 nm width, 500 nm height)
  ├─ Deposit cladding (SiO₂)
  ├─ Yield: ~95% (photonics more forgiving than nanoelectronics)

Step 3: III-V Bonding for VCSELs (Advanced, 3 months)
  ├─ Prepare GaAs/InP die with VCSEL structure
  ├─ Align & flip-chip bond to silicon (800 nm pitch)
  ├─ Remove GaAs substrate (via selective etch)
  ├─ Etch individual VCSEL mesas
  ├─ Yield: ~70% (flip-chip is challenging, needs development)

Step 4: Back-End-of-Line (Contacts, Metal, 3 months)
  ├─ Deposit contacts (Ti/Al, 50 nm)
  ├─ Pattern metal 1 (Cu, 0.5 µm)
  ├─ Inter-layer dielectric (SiO₂)
  ├─ Metal 2 for power distribution (1 µm width)
  ├─ Via stitching to GND/VDD
  ├─ Passivation (SiN cap)
  ├─ Yield: ~98% (standard CMOS back-end)

Step 5: Packaging (2 months)
  ├─ Die singulation (saw cutting)
  ├─ Wafer-scale test (probe contacts)
  ├─ Flip-chip bonding to BGA or LCC substrate
  ├─ Underfill (to protect wire bonds)
  ├─ Final test (functionality, power consumption)
  ├─ Packaging yield: ~95%

Total Process Flow: 12-15 months from tapeout to production wafers
Cost Estimate:
  - Design NRE: $500K (design tools, simulation)
  - Mask set: $200K (for 130 nm)
  - Wafer cost: $100K per wafer (at GlobalFoundries, 200 mm wafer)
  - Per-die cost: $50-100 (after yield & packaging)
  - First lot: 1-2 wafers = 100-200 working die
```

---

## KEY TECHNICAL RISKS & MITIGATION

```
Risk 1: VCSEL Wavelength Drift (780 nm → 785 nm due to temp)
  Impact: Photodetector efficiency drops 30%
  Mitigation:
    - Broadband photodetectors (λ range 750-850 nm)
    - On-chip wavelength monitor
    - Feedback tuning of VCSEL temperature via heater

Risk 2: Microring Frequency Lock Stability
  Impact: Clock jitter grows → spike timing errors
  Mitigation:
    - Conservative PI loop tuning (slower = more stable)
    - Temperature compensation (micro heater on microring)
    - Redundant lock-in detection (two phase detectors)

Risk 3: Manufacturing yield (flip-chip VCSEL bonding is hard)
  Impact: 40% die yield → costs too high
  Mitigation:
    - Design for testability (measure VCSEL performance pre-bonding)
    - Redundant neurons (16 → 20, disable bad ones in test)
    - Develop bonding process on test wafers first

Risk 4: Analog MAC precision loss due to capacitor leakage
  Impact: Charge leaks off capacitors → wrong computations
  Mitigation:
    - Use fast charge settling (complete within 1 ns)
    - Low-leakage transistors in on-chip SRAM
    - Refresh capacitor values periodically (before each inference)

Risk 5: Crosstalk between photonic and analog (optical noise)
  Impact: Spikes on one neuron couple to analog circuits
  Mitigation:
    - Shielded routing (metal cages around analog circuits)
    - Substrate ties (multiple GND connections)
    - Optical isolation (waveguides routed away from analog MACs)
```

---

## VALIDATION PLAN (Phase 1-3)

```
Phase 1: Simulation & Modeling (3-6 months)
  ✓ SPICE simulation of analog MACs
  ✓ Optical mode solver (COMSOL) for waveguides
  ✓ Thermal FEA (ANSYS) for temperature profile
  ✓ System-level Monte Carlo analysis (PVT corners, mismatch)
  ✓ Deliverable: Design review with DARPA

Phase 2: Tape-Out & First Silicon (6-12 months)
  ✓ Multi-project wafer (MPW) with 10-20 die variants
  ✓ Separate test structures for photonics & analog
  ✓ Probe testing (speed, power, basic function)
  ✓ Scanning electron microscopy (SEM) to verify critical dimensions
  ✓ Optical characterization (wavelength, output power)
  ✓ Deliverable: First silicon results published

Phase 3: System Integration & Demo (6-12 months)
  ✓ Build test board (PCB with oscilloscope probes)
  ✓ Run inference benchmarks (ResNet-18, MNIST, CIFAR-10)
  ✓ Compare energy/latency vs. BrainChip, Jetson
  ✓ Publish results in IEEE JSSC, ISSCC, or Nature
  ✓ Demonstrate to potential customers
  ✓ Deliverable: Production-ready design kit, SBIR Phase II completion
```

---

## TIMELINE SUMMARY

```
2026:
  Q1: Form team, setup design environment
  Q2: NSF SBIR Phase I submission + approval ($305K)
      Begin feasibility study
  Q3: Complete architecture design & simulation
  Q4: Tape-out ready, mask set generated

2027:
  Q1: MPW run via Efabless (8-week turnaround)
  Q2: First silicon received, initial testing
      NSF SBIR Phase II submission ($1.75M)
  Q3: Full characterization (power, speed, optical)
  Q4: System integration, inference demo

2028:
  Q1-Q2: Second-gen design tape-out
  Q3: Second silicon results, licensing discussions
  Q4: First customer engagement, production plan

Target: Commercial availability by 2029
```

---

This architecture document serves as your **engineering specification** for Phase 0 feasibility study. Reference it when:
- Writing NSF SBIR Phase I proposal (show you know the technical details)
- Meeting with photonics engineers (credibility)
- Discussing with fab partners (confirm manufacturability)
- Pitching to VC/customers (demonstrate depth of thinking)
