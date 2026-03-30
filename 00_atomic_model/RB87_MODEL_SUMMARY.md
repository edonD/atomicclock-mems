# Rb-87 Atomic Superposition Model

## Overview
This model visualizes the quantum behavior of Rubidium-87 atoms when exposed to microwave radiation at **6.834 GHz** (the hyperfine transition frequency). It shows how atoms enter quantum superposition states and how their spins precess and evolve.

---

## 1. ATOMIC STRUCTURE & SPINS

### Nuclear Spin: I = 5/2
- Rubidium-87 nucleus has **6 magnetic sublevels**: m_I = -5/2, -3/2, -1/2, +1/2, +3/2, +5/2
- Nuclear magnetic moment μ_I ∝ I

### Electron Spin: S = 1/2
- Ground state is **5S₁/₂** (orbital angular momentum L = 0)
- **2 spin states**: m_S = ±1/2 (spin up/down)
- Electronic magnetic moment μ_S ∝ S

### Hyperfine Coupling (I·S interaction)
The nucleus and electron spin couple via magnetic hyperfine interaction:
- Creates **two energy levels**: F = I + S and F = I - S
- **F = 3** (upper): 7 magnetic sublevels (m_F = -3 to +3)
- **F = 2** (lower): 5 magnetic sublevels (m_F = -2 to +2)

### Hyperfine Splitting
- **Frequency**: ν_HF = **6,834,682,610.904 Hz** = **6.834 GHz**
- This is the signature line of the Rb-87 atomic clock
- Natural linewidth: 5.7 MHz (due to spontaneous emission lifetime)

---

## 2. QUANTUM SUPERPOSITION ON THE BLOCH SPHERE

When a microwave field at 6.834 GHz drives the F=2 ↔ F=3 transition:

### Pure States
- **|F=2⟩ (ground)** - South pole of Bloch sphere
- **|F=3⟩ (excited)** - North pole

### Superposition States
- **|+⟩ = (|F=2⟩ + |F=3⟩)/√2** - Equator (+X direction)
- **|-⟩ = (|F=2⟩ - |F=3⟩)/√2** - Opposite equator (-X direction)
- **|↻⟩ = (|F=2⟩ + i|F=3⟩)/√2** - Circular superposition (+Y)
- **|↺⟩ = (|F=2⟩ - i|F=3⟩)/√2** - Opposite circular (-Y)

Any point on the Bloch sphere represents a valid quantum state.

---

## 3. RABI OSCILLATIONS (Time Evolution)

When microwave power Ω drives the transition at resonance:

**Population dynamics:**
```
P_excited(t) = sin²(Ω·t/2)
P_ground(t) = cos²(Ω·t/2)
```

### Key Pulse Times
- **π/2 pulse**: Ω·t = π/2 → Equal superposition (50/50)
- **π pulse**: Ω·t = π → Complete flip (ground ↔ excited)
- **2π pulse**: Ω·t = 2π → Returns to initial state

For Ω/(2π) = 50 kHz:
- π/2 pulse takes ~**5 μs**
- π pulse takes ~**10 μs**

---

## 4. FREQUENCY RESPONSE AT 6.834 GHz

### Narrow Resonance
The atomic resonance is **extremely sharp**:
- Peak at 6.834 GHz
- Natural FWHM: ~5.7 MHz
- But CPT narrows it to ~100 Hz (1/50,000 the linewidth!)

### Why This Matters
- **Frequency selectivity**: Atom responds ONLY to ~6.834 GHz ±5.7 MHz
- **Off-resonance rejection**: 30 MHz away ≈ 0 response
- **Frequency discriminator**: Used for servo feedback to lock oscillator

### CPT Dark State
- Coherent Population Trapping creates **ultra-narrow resonance** (~100 Hz)
- Used in all modern Rb atomic clocks
- Achieved with specific laser/RF configurations

---

## 5. SUPERPOSITION & DECOHERENCE

### Quantum Coherence
When in superposition |ψ⟩ = (|2⟩ + |3⟩)/√2:
- Off-diagonal density matrix elements oscillate at **6.834 GHz**
- Time-domain: coherence_amplitude = e^(i·2π·ν_HF·t)

### Decoherence Mechanisms
Coherence decays due to:

1. **Magnetic field noise** (Zeeman shifting)
2. **Collisions** with buffer gas atoms
3. **Spontaneous emission** (lifetime: 27.7 ns)
4. **Thermal motion** (Doppler dephasing)

Decoherence envelope: e^(-t/τ_c), where τ_c ≈ 100-200 ns

### Practical Impact
- Forces re-initialization of quantum state
- Limits interrogation time in clocks
- Limits long-term stability

---

## 6. RAMSEY FRINGE VISIBILITY

**Two-pulse interference method:**

1. **π/2 pulse**: Creates superposition
2. **Drift time T**: Coherence oscillates at 6.834 GHz
3. **π/2 pulse**: Projects back to populations

**Fringe pattern:**
```
Population(T) ∝ cos(2π·ν_HF·T) · e^(-T/τ_c)
```

**Visibility decay:**
- Initial visibility: 100%
- After T = τ_c: Visibility ≈ 37%
- After T = 3τ_c: Visibility < 5%

Shorter decoherence time τ_c → narrower clock linewidth

---

## 7. FREQUENCY DISCRIMINATOR (Error Signal)

For atomic clock servo loop:

**Method**: Compare absorption at ±5 kHz sidebands
```
Error_signal = Response(ν₀ - 5kHz) - Response(ν₀ + 5kHz)
```

**Properties:**
- Zero-crossing at 6.834 GHz → lock point
- Slope = sensitivity for servo gain
- Used to feedback-correct RF oscillator frequency

---

## Physical Constants (Rb-87)

| Parameter | Value |
|-----------|-------|
| Nuclear spin I | 5/2 |
| Electron spin S | 1/2 |
| Ground state | 5S₁/₂ |
| Excited state | 5P₁/₂ |
| Hyperfine frequency | 6,834,682,610.904 Hz |
| Hyperfine frequency | 6.834682611 GHz |
| Natural linewidth | 5.746 MHz |
| Spontaneous emission lifetime | 27.70 ns |
| Bohr magneton | 9.274 × 10⁻²⁴ J/T |

---

## Generated Visualizations

### 1. **01_spin_configuration.png**
Shows how nuclear I and electron S combine via hyperfine coupling to create F=2 and F=3 levels with 6.834 GHz splitting.

### 2. **02_bloch_sphere_rabi.png**
- **Left**: Bloch sphere with key quantum states
- **Right**: Rabi oscillations showing population exchange under resonant microwave

### 3. **03_frequency_response.png**
- **Top-left**: Ultra-narrow resonance (±200 kHz view)
- **Top-right**: Wide frequency response (±30 MHz)
- **Bottom-left**: CPT-narrowed dark state (~100 Hz linewidth)
- **Bottom-right**: Frequency discriminator for servo feedback

### 4. **04_superposition_evolution.png**
- **Top-left**: Quantum coherence oscillation at 6.834 GHz
- **Top-right**: Decoherence envelope (exponential decay)
- **Bottom-left**: π/2 – drift – π/2 pulse sequence
- **Bottom-right**: Ramsey fringe visibility decay with decoherence

---

## How This Relates to Atomic Clocks

**Frequency stability chain:**

1. Rb atom absorbs **precisely at 6.834 GHz**
2. CPT narrows resonance to **~100 Hz**
3. Frequency discriminator detects deviation
4. Servo locks oscillator **to atomic resonance**
5. Result: Ultra-stable frequency source (ppm-level stability)

The quantum superposition is the key: atoms oscillate coherently in two states, and we exploit this coherence to measure time with atomic precision.

---

## Code Reference

**File**: `rb87_superposition_model.py`

**Key functions:**
- `get_rb87_structure()` - Atomic constants
- `bloch_vector()` - Superposition state vectors
- `visualize_spin_configuration()` - I, S, F diagram
- `visualize_bloch_sphere()` - 3D state space + Rabi
- `frequency_response_lorentzian()` - Resonance line
- `visualize_frequency_response()` - 6.834 GHz responses
- `visualize_superposition_evolution()` - Coherence dynamics
