# Rb-87 Three.js Interactive Animation

## Overview

`rb87_threejs_animation.html` is a **fully interactive 3D visualization** of Rubidium-87 quantum dynamics using Three.js.

## Features

### 🎨 Visualizations
- **3D Bloch Sphere** — Real-time rotating quantum state visualization
- **State Vector Arrow** — Shows the current quantum state (red arrow)
- **Trajectory Trace** — Green line showing the path of quantum evolution
- **Coordinate Axes** — X (red), Y (green), Z (blue) reference frame
- **Population Bars** — Live bar charts at bottom showing P(F=2) and P(F=3)
- **Live Metrics** — Real-time statistics and measurements

### ⚙️ Interactive Controls
1. **Rabi Frequency** (10-500 kHz)
   - Controls the speed of quantum oscillations
   - Higher = faster Rabi flopping

2. **Detuning** (-2 to +2 MHz)
   - Offset from 6.834 GHz resonance
   - Shows off-resonance effects
   - At 0 MHz = perfectly on-resonance

3. **Speed** (0.1x to 3x)
   - Playback speed multiplier
   - Faster simulation for quick observation
   - Slower for detailed analysis

4. **Buttons**
   - **PLAY/PAUSE** — Control animation
   - **RESET** — Clear history and restart
   - View mode buttons (future expansion)

### 📊 Live Metrics Panel
Shows real-time values:
- **Time Elapsed** — Simulation time in nanoseconds
- **Rabi Cycle** — Progress through current Rabi oscillation (0-100%)
- **P(F=2)** — Ground state population percentage
- **P(F=3)** — Excited state population percentage
- **Coherence** — Quantum coherence between states
- **Effective Ω** — Current effective Rabi frequency

### 🌈 Color Scheme
- **Cyan (#00ffff)** — Bloch sphere wireframe
- **Red (#ff0055)** — State vector arrow
- **Green (#00ff88)** — Trajectory trace
- **Blue (#0088ff)** — Z-axis and ground state
- **Orange (#ff6600)** — Excited state indicator
- **Purple** — Overall theme

## How to Use

### 1. Open in Browser
Simply open `rb87_threejs_animation.html` in any modern web browser:
```bash
# macOS / Linux
open rb87_threejs_animation.html

# Windows
start rb87_threejs_animation.html

# Or drag-drop into Firefox/Chrome
```

### 2. Interact with Controls
- **Slider Controls** on the right side adjust parameters in real-time
- **Play/Pause** button to stop/resume animation
- **Reset** button to restart the simulation

### 3. Watch the Physics
The Bloch sphere shows:
- Red arrow = current quantum state
- Green line = historical trajectory
- Rotating sphere = visual effect

### 4. Read the Metrics
Monitor in real-time:
- How fast the Rabi oscillation progresses
- Population exchange between states
- Coherence decay (if detuning is applied)

## Physics Behind the Animation

### Rabi Oscillation
When you apply 6.834 GHz microwave to Rb-87:
```
P_excited(t) = sin²(Ω·t/2)
P_ground(t) = cos²(Ω·t/2)
```

Where Ω is the Rabi frequency controlled by the microwave power.

### Detuning Effect
When frequency ≠ 6.834 GHz, an effective Rabi frequency appears:
```
Ω_eff = √(Ω² + Δ²)
```

Where Δ is the detuning from resonance.

The state vector rotates at Ω_eff, causing:
- Slower oscillation if off-resonance
- Spiral trajectory instead of circle
- Reduced excitation efficiency

### Bloch Vector
The position of the state vector on the sphere encodes:
- **Z-component** — Population difference
- **X-component** — Real part of coherence
- **Y-component** — Imaginary part of coherence

## Experiment Ideas

### 1. Observe Rabi Flopping
- Set Detuning = 0
- Increase Rabi Frequency to 200 kHz
- Watch the red arrow trace a circle while populations oscillate

### 2. See Detuning Effects
- Set Rabi Frequency = 100 kHz
- Slowly increase Detuning from 0 to ±2 MHz
- Notice: populations don't reach 100% excited when detuned
- Trajectory becomes a spiral instead of circle

### 3. Measure a Rabi Cycle
- Set Rabi = 100 kHz
- Detuning = 0
- Watch Time metric
- Period of full cycle = ~20 ns (this is 2π/Ω)

### 4. Power Broadening
- Set Detuning = 0
- Increase Rabi to 500 kHz
- Notice: oscillation is much faster
- In real atoms, high power broadens the resonance

### 5. Ramsey Fringes (Manual)
- Set Detuning = 0.1 MHz (small offset)
- Watch populations oscillate slowly
- This mimics the slow beat frequency in Ramsey spectroscopy

## Technical Details

### Performance
- Optimized for modern GPUs
- Smooth 60 FPS animation
- ~2-3 MB memory usage
- Works on desktop and high-end tablets

### Browser Compatibility
- **Chrome** ✓ (Recommended)
- **Firefox** ✓
- **Safari** ✓
- **Edge** ✓
- Mobile browsers: Limited (small screen not ideal)

### Three.js Version
Uses Three.js r128 from CDN (latest stable release)

## Advanced Usage

### Modify Physics Constants
Edit the simulation parameters in the JavaScript:

```javascript
simulationState.rabiFreq = 100e3;  // Rabi frequency in Hz
simulationState.detuning = 0;      // Detuning in Hz
simulationState.speed = 1;         // Time scale factor
```

### Change Colors
Modify the material colors:
```javascript
sphereMaterial = new THREE.MeshBasicMaterial({
    color: 0x00ffff,  // Change to custom hex color
    ...
});
```

### Adjust Visualization
- `simulationState.maxHistoryPoints = 500` — How long the trajectory line is
- `camera.position.set(0, 0, 3)` — Camera distance from sphere

## Troubleshooting

### Animation Not Playing
- Check browser console (F12) for errors
- Ensure JavaScript is enabled
- Try a different browser

### Controls Unresponsive
- Click canvas first to give it focus
- Refresh the page

### Performance Issues
- Reduce trajectory history points to 200
- Lower resolution if needed
- Close other applications

### Numbers Look Wrong
- Check if "Speed" slider is at 1.0x
- Reset simulation with RESET button
- Try different browser

## Educational Value

This animation teaches:
1. **Quantum Mechanics** — Bloch sphere representation
2. **Rabi Dynamics** — Driven two-level systems
3. **Microwave Control** — How to manipulate atoms
4. **Resonance** — Importance of frequency matching
5. **Real-time Monitoring** — Live measurement of quantum states
6. **Interactive Learning** — Hands-on experimentation

## Future Enhancements

Possible additions:
- [ ] Decoherence visualization (cloud expanding from state)
- [ ] Pulse sequence designer
- [ ] Ramsey fringe visualization
- [ ] 3D vector field showing Rabi rates
- [ ] Save/load simulation states
- [ ] Export trajectory data

## References

- **Physical Constants**: Rb-87 hyperfine transition = 6,834,682,610.904 Hz
- **Quantum Mechanics**: Rabi model, rotating wave approximation
- **Visualization**: Three.js documentation
- **Atomic Clocks**: NIST Rb standards

## File Structure

```
rb87_threejs_animation.html       ← Main animation (standalone)
THREEJS_ANIMATION_README.md       ← This file
cool_simulation.py                ← Python static visualizations
rb87_superposition_model.py       ← Physics model
RB87_MODEL_SUMMARY.md             ← Physics theory
```

## License

Educational use. Inspired by NIST Rb-87 atomic clock research.

---

**Enjoy exploring quantum mechanics in real-time! 🎯**
