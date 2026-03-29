# Circuit Design — SKY130 CMOS Readout IC

## Overview

This folder contains the electronic circuit design for the CSAC atomic clock readout IC. The design targets the **SKY130** 130 nm CMOS process (open-source, cost-effective, MEMS-compatible).

The IC integrates:
- **VCO** (Voltage-Controlled Oscillator) — generates 6.835 GHz clock locked to Rb-87 resonance
- **TIA** (Transimpedance Amplifier) — converts photodiode current to voltage
- **PID Servo Controller** — closes feedback loop to maintain lock
- **Frequency Divider** — outputs 1 Hz for external counter/clock
- **Thermal Controller** — manages heater power for temperature stability
- **SPI Interface** — allows external MCU to read status and configure parameters
- **DACs** — drive VCO tuning and heater control

---

## Files

| File | Description |
|------|-------------|
| `vco_sky130.sp` | SPICE simulation of VCO (LC-tank cross-coupled pair, varactor tuning) |
| `tia_photodetector.sp` | SPICE simulation of photodetector readout TIA + LPF |
| `digital_top.v` | Verilog RTL for frequency divider, PID servo, SPI, thermal control |
| `README.md` | This file |

---

## Architecture

```
┌────────────────────────────────────────────────────────────────────┐
│                                                                    │
│  ANALOG FRONTEND (MEMS cavity + optical path)                     │
│  ┌─────────────────────────────────────────┐                      │
│  │  Photodiode (780 nm laser light)        │                      │
│  │  Rb-87 atoms in 3×3 mm cavity           │                      │
│  │  CPT resonance dip → variable photocurrent                     │
│  └─────────────────────────────────────────┘                      │
│                 │                                                  │
│                 ▼                                                  │
│  ┌─────────────────────────────────────────┐                      │
│  │  TIA (Transimpedance Amplifier)         │                      │
│  │  • Integrates photodiode on-chip        │                      │
│  │  • Converts pA–nA currents to mV signal │                      │
│  │  • LPF cuts high-frequency noise        │                      │
│  │  Output: 0–100 mV (proportional to absorption)                 │
│  └─────────────────────────────────────────┘                      │
│                 │                                                  │
│                 ▼                                                  │
│  ┌─────────────────────────────────────────┐                      │
│  │  Analog-to-Digital Converter (ADC)      │                      │
│  │  • 8-bit SAR ADC (simple, low-power)    │                      │
│  │  • Samples photodetector at ~100 kHz    │                      │
│  │  • Output: photo_adc[7:0]               │                      │
│  └─────────────────────────────────────────┘                      │
│                 │                                                  │
│                 ▼                                                  │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │  DIGITAL SERVO LOOP (on SKY130 IC)                          │  │
│  │                                                             │  │
│  │  PID Controller (clk_100hz clock domain)                   │  │
│  │  • Error = photo_adc[7:0] − setpoint (≈50)                 │  │
│  │  • Proportional term: Kp × error                           │  │
│  │  • Integral: Ki × ∫error dt                                │  │
│  │  • Derivative: Kd × d(error)/dt                            │  │
│  │  • Output: dac_vco_tune[9:0]                               │  │
│  │                                                             │  │
│  │  Lock detector                                              │  │
│  │  • If error < threshold for 8 consecutive samples          │  │
│  │  • Set valid_lock = 1                                      │  │
│  └─────────────────────────────────────────────────────────────┘  │
│                 │                                                  │
│                 ▼                                                  │
│  ┌─────────────────────────────────────────┐                      │
│  │  Digital-to-Analog Converter (DAC)      │                      │
│  │  • 10-bit R-2R or capacitive DAC        │                      │
│  │  • Drives VCO varactor (Vtune)          │                      │
│  │  • Frequency tuning range: ±500 MHz     │                      │
│  └─────────────────────────────────────────┘                      │
│                 │                                                  │
│                 ▼                                                  │
│  ┌─────────────────────────────────────────┐                      │
│  │  VCO (Voltage-Controlled Oscillator)    │                      │
│  │  • LC-tank, 6.835 GHz center frequency  │                      │
│  │  • Varactor (varicap) tuned by Vtune    │                      │
│  │  • Phase noise: ~−90 dBc/Hz @ 1 MHz     │                      │
│  │  • Output: clk_vco (feeds back to atoms)                       │
│  └─────────────────────────────────────────┘                      │
│                 │                                                  │
│                 ▼                                                  │
│  ┌─────────────────────────────────────────┐                      │
│  │  Laser Modulation (external chip)       │                      │
│  │  • Laser sidebands at VCO frequency     │                      │
│  │  • EOM (electro-optic modulator) driven │                      │
│  │  • Locks atoms to dark state            │                      │
│  └─────────────────────────────────────────┘                      │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘
                            ▲
                            │ Feedback loop closure
                            │ Frequency = 6.835 GHz
                            └──────────────────────
```

---

## Frequency Divider Chain

The VCO outputs 6.835 GHz. To generate 1 Hz (or other submultiples), we use a chain of binary dividers:

```
VCO: 6.835 GHz
  ÷ 2^33 = 8,589,934,592
  ≈ 1 Hz (calibration trim done in firmware)

Intermediate taps for servo and monitoring:
  clk_vco[23] ≈ 0.4 MHz (digital control reference)
  clk_vco[26] ≈ 100 Hz (PID update rate)
  vco_counter[32] overflow = 1 Hz output

Output: count_1hz[31:0] increments at ~1 Hz
```

---

## Simulation Instructions

### VCO (`vco_sky130.sp`)

**Tool:** ngspice (free), Cadence Spectre (commercial)

```bash
ngspice vco_sky130.sp
```

Or with SKY130 models:
```bash
ngspice -r vco_results.raw \
  -i vco_sky130.sp \
  /path/to/sky130_fd_pr/models/sky130.lib.spice
```

**What to look for:**
- **Oscillation frequency:** Should be 6.8–6.9 GHz (depending on parasitics)
- **Phase noise:** ~−90 dBc/Hz @ 1 MHz offset (expected for 130 nm CMOS)
- **Tuning sensitivity:** 200–300 MHz/V (varactor dependence)
- **Startup time:** <100 ns to reach full swing

**Expected plot:**
- `v(vtank_p)`: Oscillating at 6.835 GHz, amplitude ~0.5–1.0 V
- `v(vout_vco)`: Buffered output, low jitter, ready to drive laser modulator

---

### TIA (`tia_photodetector.sp`)

**Tool:** ngspice

```bash
ngspice tia_photodetector.sp
```

**What to look for:**
- **Gain:** 1 nA input → 1 mV output (10^6 V/A transimpedance)
- **Bandwidth:** −3dB point at ~100 kHz (limited by Rf × Cf)
- **Noise:** Input-referred ~100 nV/√Hz (thermal from differential pair)
- **Linearity:** 0–20 nA input = 0–20 mV output

**Expected plot:**
- `v(pd_node)`: Photodiode voltage (small ~10 mV ripple from photocurrent)
- `v(tia_out)`: TIA output, low-impedance, ready for ADC
- `v(servo_in)`: After LPF, ~1 kHz cutoff, very clean

---

### Digital Control (`digital_top.v`)

**Tool:** Vivado, IVerilog, or other Verilog simulator

```bash
iverilog -o csac_sim digital_top.v && vvp csac_sim
```

Or use Vivado for synthesis/P&R on SKY130:
```bash
# Create Vivado project targeting SKY130
# Synthesize digital_top.v
# Run place & route
# Extract timing / power reports
```

**Test scenarios:**
- **Lock test:** Inject photo_adc = 50 ± 5, watch valid_lock go high
- **Unlock test:** Inject photo_adc = 100 (bright), watch error grow, lock clears
- **Thermal control:** Step temp_adc, watch heater_pwm adjust
- **SPI readout:** Send SPI commands, verify count_1hz increments

---

## Integration with GDS-II Layout

Once SPICE simulations pass, move to physical layout:

### Step 1: Schematic → Netlist
- Export `vco_sky130.sp` + `tia_photodetector.sp` as a unified netlist
- Write testbench constraints (clock frequency, power rails, input signals)

### Step 2: Layout in Xschem + Magic
- Use **Xschem** (open-source schematic entry, SKY130-compatible)
- Capture schematics: vco, tia, opamp cells, etc.
- Generate layout cells in **Magic**
- Run DRC (Design Rule Check) on all cells

### Step 3: Analog Place & Route
- Manually place TIA + photodiode together (minimize parasitic inductance)
- Route VCO tank to minimize EMI
- Shield sensitive analog signals from digital switching

### Step 4: Digital P&R
- Synthesize `digital_top.v` with Yosys (open-source) or Vivado
- Place & route with OpenROAD (open-source) or Cadence Innovus
- Insert clock tree synthesis for clk_vco distribution
- Insert level shifters between analog and digital domains

### Step 5: Post-Layout Verification
- Extract parasitics with `ext2spice` (Magic)
- Run post-layout SPICE simulation (PLS)
- Verify timing with static timing analysis (STA)
- Verify power with transient simulation

---

## SKY130 Design Constraints

| Parameter | Limit | Notes |
|-----------|-------|-------|
| Supply voltage | 1.8 V ± 10% | Core voltage for all circuits |
| Gate length | ≥ 0.18 µm | Minimum for SKY130 |
| Metal spacing | ≥ 0.14 µm (M1), ≥ 0.28 µm (M2) | DRC rules; use open_pdks |
| Maximum current | ~100 mA/mm width | For power lines |
| Temperature range | −40…85°C | Process corners: ss, tt, ff, sf, fs |
| Oxide capacitance | ~8 fF/µm² | For varactor & MIM caps |

---

## Tapeout Checklist

- [ ] SPICE simulations pass (transient, AC, monte carlo)
- [ ] Layout DRC/LVS clean (Magic + `open_pdks`)
- [ ] Post-layout simulation matches schematic
- [ ] Static timing analysis passes (setup/hold)
- [ ] Power estimation < 150 mW (target)
- [ ] Glitch analysis on critical paths (e.g., clk_vco)
- [ ] ESD protection on all I/O pads
- [ ] Decoupling capacitors placed throughout
- [ ] Substrate biasing strategy defined (bulk connect)
- [ ] Test/probe points identified for bring-up
- [ ] Submit to SKY130 MPW (SkyWater or Cadence slot ~$12K)

---

## Power Budget

Estimated for 6.835 GHz operation:

| Block | Current | Voltage | Power |
|-------|---------|---------|-------|
| VCO (cross-coupled pair) | 10 mA | 1.8 V | 18 mW |
| VCO (biasing) | 5 mA | 1.8 V | 9 mW |
| TIA opamp | 2 mA | 1.8 V | 3.6 mW |
| Digital (counters, PID, SPI) | 5 mA | 1.8 V | 9 mW |
| Photodiode & sense | 1 mA | 1.8 V | 1.8 mW |
| DACs (10-bit) | 1 mA | 1.8 V | 1.8 mW |
| **Total IC** | **24 mA** | **1.8 V** | **~44 mW** |
| Heater (external) | — | 3.3 V (external supply) | ~50–80 mW |
| Laser driver (external) | — | 3.3 V | ~30 mW |
| **Total chip + externals** | — | — | **~124 mW** |

---

## Next Steps

1. **Validate SPICE models** — Run sims in ngspice with SKY130 PDK
2. **Design layout** — Use Xschem + Magic for analog cells
3. **Estimate parasitics** — Extract RC from layout, re-simulate
4. **Prepare testbench** — Bring-up strategy, test modes
5. **Tapeout** — Cadence/SkyWater MPW or ChipFoundry

Expected timeline: **6 months** from now to silicon samples in hand.

---

## References

- SKY130 PDK: https://github.com/google/skywater-pdk
- Open_pdks: https://github.com/RTimothyEdwards/open_pdks
- Xschem: https://xschem.sourceforge.io/
- Magic: http://opencircuitdesign.com/magic/
- Yosys: https://yosyshq.net/yosys/
- OpenROAD: https://openroad.readthedocs.io/

---

**Created:** 2026-03-29
**Status:** Early draft — awaiting SPICE simulation validation
