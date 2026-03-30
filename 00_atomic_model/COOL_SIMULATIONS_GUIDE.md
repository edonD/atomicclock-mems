# COOL RB-87 QUANTUM SIMULATIONS GUIDE

## 6 Beautiful Quantum Physics Visualizations

This collection showcases the quantum behavior of Rb-87 atoms under microwave driving at 6.834 GHz in visually stunning ways.

---

## 1. **COOL_01_bloch_trajectories.png** — Bloch Sphere Evolution

### What You're Seeing
Four 3D Bloch spheres showing quantum state trajectories under different driving conditions:

- **Top-Left: Resonant Drive (On-Resonance, Δ = 0)**
  - Microwave frequency perfectly matches 6.834 GHz
  - Clearest Rabi oscillation path
  - Population oscillates symmetrically between F=2 and F=3
  - Trajectory is a perfect circle in the rotation plane

- **Top-Right: Red Detuned (Δ = -500 kHz)**
  - Microwave is 500 kHz below 6.834 GHz
  - Atom responds more weakly
  - Trajectory spirals rather than circles
  - Shows the effect of off-resonance driving

- **Bottom-Left: Blue Detuned (Δ = +500 kHz)**
  - Microwave is 500 kHz above 6.834 GHz
  - Mirror image of red detuning
  - Shows frequency selectivity of atomic transition

- **Bottom-Right: AC Stark Shift (High Power)**
  - Same frequency but double the power (200 kHz Rabi)
  - Trajectory changes due to power-broadening
  - Shows that intensity affects dynamics

### Physics
The sphere surface is the set of all possible pure quantum states. Each point on the sphere represents a unique quantum superposition. The trajectory shows the *adiabatic path* the atom takes as you apply microwave.

---

## 2. **COOL_02_heatmap_dynamics.png** — Frequency & Time Evolution

### Panel 1: Population Heatmap (Top-Left)
- **X-axis**: Time (0-200 ns)
- **Y-axis**: Frequency offset from 6.834 GHz (-2 MHz to +2 MHz)
- **Color**: Excited state (F=3) population (black=0%, yellow=100%)

Shows that:
- At resonance (center), atoms flop rapidly between states
- Off-resonance, oscillations are slower/weaker
- Width reveals the resonance linewidth (~5 MHz)

### Panel 2: Rabi Resonance Profile (Top-Right)
Shows the response curve after 100 ns of driving:
- Blue: Population that actually oscillates
- Red dashed: Natural linewidth envelope
- Green: On-resonance peak

### Panel 3: Phase Space Trajectories (Bottom-Left)
Different spiral patterns for different detunings in the complex plane:
- Shows the *coherence* (quantum correlation) between F=2 and F=3
- Each color traces a different frequency offset
- Spirals show how phase evolves over time

### Panel 4: Power-Level Comparison (Bottom-Right)
How different microwave powers (Rabi frequencies) affect the oscillation speed:
- Blue (50 kHz): Slow, gentle Rabi flopping
- Red (500 kHz): Fast, energetic driving
- Circles mark π/2 pulse times, squares mark π pulse times

---

## 3. **COOL_03_phase_portrait.png** — 3D Population Dynamics

### Left: 3D Phase Space
- **X-axis**: P_ground (F=2 population)
- **Y-axis**: P_excited (F=3 population)
- **Z-axis**: Time (evolution direction)

Shows 4 simultaneous Rabi trajectories:
- Start points (circles) all begin at pure ground state (1,0)
- End points (squares) show where the trajectory leads
- Yellow vertical tube is the constraint surface (populations sum to 1)
- Faster oscillations = tighter spirals

### Right: 2D Phase Plane with Vector Field
- Shows the population plane (must satisfy P_ground + P_excited = 1)
- Gray arrows show the *direction field* — which way populations evolve
- Black dashed line is the constraint
- Colored curves show actual trajectories for 4 Rabi frequencies

---

## 4. **COOL_04_pulse_sequences.png** — Quantum Pulse Choreography

Shows population dynamics under 4 quantum pulse sequences used in atomic clocks:

### Simple π/2 Pulse (Top-Left)
- Single 10 ns microwave pulse
- Population rises to 50% excited state
- Used to create superposition

### Ramsey Sequence (Top-Right)
- π/2 pulse, then 400 ns wait, then π/2 pulse again
- Second pulse probes the quantum coherence built up during wait
- Creates quantum *fringes* (oscillatory response with frequency)

### Spin Echo (Bottom-Left)
- π/2 — T — π — T — π/2
- π pulse (180° flip) reverses decoherence
- Extends coherence time for longer measurements

### CPMG Train (Bottom-Right)
- Multiple π pulses applied in sequence
- Refocuses decoherence even more effectively
- Used in high-precision atomic clocks

**Key feature**: The colored rectangles indicate when microwave is ON. The population curves show the quantum state evolution.

---

## 5. **COOL_05_ramsey_fringes.png** — Quantum Interference Patterns

This is one of the most beautiful quantum effects!

### Top-Left: 2D Ramsey Map
- **X-axis**: Drift time between pulses (0-1000 ns)
- **Y-axis**: Frequency offset from 6.834 GHz
- **Color**: Brightness shows excited state probability

Shows the classic *Ramsey fringe* pattern:
- Horizontal stripes = oscillation in frequency direction
- Vertical stripes = oscillation in time direction
- The crosshatch pattern is pure quantum interference

### Top-Right: Individual Fringe Curves
Shows how the pattern changes at different drift times:
- T=100 ns: Few oscillations
- T=1000 ns: Many rapid oscillations
- Shows quantum beats between two atomic states

### Bottom-Left: Visibility Decay
How the fringe contrast decreases with time:
- τ_c = 500 ns: Fast decoherence (blue curve)
- τ_c = 2000 ns: Slow decoherence (red curve)
- Shows the *coherence lifetime* — how long atoms stay coherent

### Bottom-Right: 3D Ramsey Surface
Combines both dimensions with decoherence envelope:
- Peak colors (yellow) show highest probability
- Shape shows the mountain-like structure of Ramsey fringes
- Envelope decays exponentially with time

**This is what Rb atomic clocks actually measure!**

---

## 6. **COOL_06_state_tomography.png** — Quantum State Reconstruction

How to completely characterize a quantum state from measurements.

### Panel 1: Measurements in 3 Bases (Top-Left)
Measure the atom in 3 different ways:
- **Z basis** (blue): Simple F=2 vs F=3 measurement → shows population difference
- **X basis** (red): Linear superposition measurement → shows real part of coherence
- **Y basis** (green): Circular superposition measurement → shows imaginary part

All three curves needed to fully describe the quantum state!

### Panel 2: Reconstructed Bloch Sphere (Top-Right)
3D sphere rebuilt from the measurements:
- Colored arrows: Bloch vectors at different times
- Trajectory shows how state evolves
- Can reconstruct any pure state if you measure in 3 bases

### Panel 3: Density Matrix Evolution (Bottom-Left)
Shows the quantum state as a 2×2 matrix:
- Diagonal elements: populations (F=2 and F=3)
- Off-diagonal elements: quantum coherence
- Darkness indicates strength

### Panel 4: Coherence & Purity (Bottom-Right)
Two key quantum measures:
- **Blue line (Purity)**: How "pure" the state is (pure quantum state = 1)
- **Red line (Coherence)**: How much quantum correlation exists between states
- Over time, decoherence destroys coherence

---

## Physics Summary

### What Makes These Cool?

1. **Bloch Sphere** — Visualizes all possible quantum states in 3D
2. **Heatmaps** — Show how multiple physical parameters interact
3. **Phase Portraits** — Reveal hidden structure in population dynamics
4. **Pulse Sequences** — Demonstrate how to manipulate quantum states
5. **Ramsey Fringes** — Showcase quantum interference (the *quantum* part of quantum mechanics)
6. **State Tomography** — Prove you can measure everything about a quantum state

### Connection to Atomic Clocks

Rb-87 atomic clocks work by:
1. Driving the 6.834 GHz transition
2. Creating quantum superposition (Ramsey sequence)
3. Measuring the oscillation frequency with incredible precision (~100 mHz accuracy)
4. Using the oscillations to lock an oscillator frequency

The 6.834 GHz line is so stable and well-defined that it defines the second in the SI system.

---

## Running the Simulations

```bash
cd 00_atomic_model
python cool_simulation.py
```

All 6 plots saved to `plots/` directory.

---

## Key Equations

**Rabi Oscillation:**
```
P_excited(t) = sin²(Ω·t/2)
```
where Ω/(2π) is the Rabi frequency.

**Ramsey Fringe:**
```
Population ∝ 1 + cos(2π·Δν·T)
```
where T is the drift time between pulses.

**Decoherence:**
```
Visibility(T) = e^(-T/τ_coherence)
```
where τ_c is the coherence lifetime (~100-1000 ns).

---

## Summary

These six visualizations capture the essence of quantum mechanics applied to atoms:
- **State superposition** (Bloch sphere)
- **Coherent evolution** (Rabi oscillations)
- **Frequency selectivity** (heatmaps)
- **Quantum control** (pulse sequences)
- **Quantum interference** (Ramsey fringes)
- **Quantum measurement** (state tomography)

Together, they show how to manipulate and measure quantum states with the precision required for modern quantum technology.
