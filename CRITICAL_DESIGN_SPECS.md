# CRITICAL DESIGN SPECIFICATIONS
## RB-87 Atomic Clock MEMS Device

---

## 1. RF SUBSYSTEM - DETAILED DESIGN

### 1.1 6.834 GHz VCO Design

#### Circuit Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    VCO CIRCUIT DESIGN                    │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  Reference Clock           Frequency Divider             │
│  10 MHz OCXO              ADF4159                        │
│  (±0.5 ppm stability)     PLL Divider                   │
│       │                         │                        │
│       ├─────────────────────────┤                        │
│       │                         │                        │
│       │    ┌──────────────┐     │                        │
│       └────│ Phase Detector ───┬──────┐                 │
│            │ (PFD)         │   │      │                  │
│            └──────────────┘    │   ┌──────────┐         │
│                                │   │Loop Filter│         │
│                         ┌──────┴───│ (2nd order)        │
│                         │      │   └──────────┘         │
│                         │      │                         │
│                    ┌────▼──────▼───┐                     │
│                    │ Dielectric Res.│                    │
│                    │ VCO @ 6.834 GHz│                    │
│                    │ (Tuning: ±50MHz)                    │
│                    └────┬──────────┘                     │
│                         │                                │
│            ┌────────────┤                                │
│            │            │                                │
│   ┌────────▼────┐   ┌───▼──────┐                        │
│   │Output Buffer│   │ Feedback  │                        │
│   │(+13 dBm)    │   │ Divider   │                        │
│   └────┬────────┘   │ (÷1)      │                        │
│        │            └─────┬─────┘                        │
│        │                  │                              │
│        └──────────────────┘ (closed loop)               │
│                                                           │
└─────────────────────────────────────────────────────────┘
```

#### Component Specifications

**Main PLL IC: Analog Devices ADF4159**

```
PIN CONNECTIONS (48-pin BGA)
├─ VDD: 3.3V, 5V (separate supplies, bypass each)
├─ GND: Multiple pins (star-point grounding)
├─ MOSI/MISO: SPI interface to MCU
├─ CLK/CS: SPI timing signals
├─ REFIN: 10 MHz reference (AC coupled, -7 dBm)
├─ OUT: Differential RF output
└─ AUX_OUT: Monitoring/diagnostics

SPI Configuration (read from datasheet):
- Clock frequency: 10-20 MHz (use 10 MHz to match reference)
- Data format: 32-bit, MSB first
- Mode: CPOL=0, CPHA=0
- Chip select: Active low

Register Map:
├─ Reg0: Control bits (enabled/disabled, outputs)
├─ Reg1: N divider (high word)
├─ Reg2: N divider (low word)
├─ Reg4: R divider (reference divider)
├─ Reg5: Phase offset
├─ Reg6: Modulation (for sideband generation)
├─ Reg7: Power-down
└─ Reg11: Readback (for diagnostics)

N divider calculation:
N = (Output Frequency × R_divider) / Reference Frequency
N = (6,834,682,610 × 1) / 10,000,000
N = 683,468.2610
Integer: 683,468
Fractional: 26,100 (in fixed-point format)

Tuning range: ±50 MHz
├─ Lower limit: 6,784,682,610 Hz
├─ Upper limit: 6,884,682,610 Hz
├─ Calculated N range: 678,468 to 688,468
```

**Dielectric Resonator Oscillator (DRO)**

```
Component: Custom 6.8 GHz DRO
Vendor: Oscilent Corporation or custom design

Specifications:
├─ Frequency: 6,834,682,610 Hz ± 10 MHz (VCO range)
├─ Phase noise: -90 dBc/Hz @ 1 kHz offset
├─ Output power: +10 dBm (free-running)
├─ Tuning sensitivity: 1.5 MHz/V (capacitive diode tuning)
├─ Pulling: < 100 kHz (with 15 dB return loss load)
├─ Temperature stability: ±2 ppm/°C (before feedback control)
├─ Current consumption: 150 mA @ +12V
└─ Package: 2" × 1.5" × 0.5" (standard)

Tuning Diode: Macom MV33950
├─ Capacitance @ 2V: 4.2 pF ± 0.3 pF
├─ Q factor: 600 @ 1 GHz
├─ Reverse breakdown: 25V (safe operating)
├─ Reverse leakage: < 100 nA
└─ Impedance: Series RC parasitic

Tuning Network:
├─ Bypass C_bypass: 100 nF (HF isolation)
├─ Bulk C_bulk: 10 μF (low-frequency filtering)
├─ Series C_ser: 47 pF (AC decoupling from DAC)
├─ Series R_ser: 1 kΩ (damping, prevents ringing)
└─ Load R_load: 10 kΩ (DAC load resistance)

Tuning voltage range: 1.5V to 8.5V
├─ 1.5V → 6,784 MHz (lower tuning limit)
├─ 5.0V → 6,835 MHz (nominal frequency)
├─ 8.5V → 6,885 MHz (upper tuning limit)
```

**Reference Oscillator: 10 MHz OCXO**

```
Component: Vectron OR200 (TCXO upgrade path to OCXO)
Specifications:
├─ Frequency: 10.000000 MHz ± 0.5 ppm
├─ Stability: ±0.5 ppm over temperature (-10 to +60°C)
├─ Aging rate: < 1 ppm/year
├─ Short-term phase noise: < -130 dBc @ 1 Hz
├─ Phase noise @ 1 kHz: < -155 dBc
├─ Output: LVCMOS or sinusoidal selectable
├─ Output level: 0.5V to 3.3V selectable
├─ Power consumption: 50 mW
└─ Cost: $100-200

Oven Control (for OCXO upgrade):
├─ Oven temperature: 60°C ± 1°C
├─ Warm-up time: 30 seconds to ±0.1 ppm
├─ Output frequency during warm-up: 9.999997 MHz (worst case)
├─ Current consumption (steady): 200 mA
└─ Current consumption (warm-up): 500 mA

Connection to ADF4159:
├─ REFIN signal: AC coupled via 100 nF capacitor
├─ Series resistor: 50 Ω (impedance matching)
├─ Input level: -7 dBm ± 1 dB (4 mVrms into 50 Ω)
├─ Ground plane: Dedicated return path
└─ Shielding: Faraday cage around reference oscillator
```

### 1.2 Output Stage & Power Amplifier

#### Power Amplifier Design

```
VCO Output: +10 dBm → PA Input: -7 to -3 dBm (15 dB attenuation)

Matching Network (Input):
├─ Impedance: 50 Ω to PA input
├─ Type: Two-stage matching network
│   ├─ L-network: 50 Ω to 12.5 Ω
│   └─ Pi-network: 12.5 Ω to PA input impedance
├─ Q factor: 2.0 (balance matching and bandwidth)
├─ Bandwidth: ± 50 MHz (covers VCO tuning range)
└─ Insertion loss: < 1 dB

PA Device: MAGX-007160 (SiGe HBT)
├─ Frequency: DC to 18 GHz (covers 6.834 GHz)
├─ Operating mode: Class A (linear, low noise)
├─ Typical gain: 20 dB @ 6.8 GHz
├─ Input impedance: 6 - j8 Ω (matching required)
├─ Output impedance: 50 Ω (conjugate match)
├─ Maximum input power: +10 dBm (1:1 VSWR safe)
├─ Output power @ rated input: +23 dBm (200 mW)
├─ Efficiency: 35-40%
├─ Supply voltage: 5V or 12V selectable
├─ Supply current: 100 mA @ 5V
└─ Package: 6-pin SOT (surface mount)

Output Matching Network:
├─ Type: Pi-network (source impedance 50 Ω, load Rb cell ~50 Ω)
├─ Design goal: Maximize delivered power to cell
├─ L1: Series inductor (~2 nH, transmission line)
├─ C1: Shunt capacitor (~2 pF)
├─ L2: Series inductor (~1 nH)
├─ Bandwidth: ± 30 MHz around 6.834 GHz
├─ Insertion loss: < 0.5 dB
└─ VSWR into Rb cell: < 1.5:1

Output Power Control:
├─ Monitor: Directional coupler (output power sense)
├─ Feedback to MCU: ADC input, 0.1 dBm resolution
├─ Control: VGA (variable gain amplifier) on PA supply
└─ Automatic gain control: ±1 dB regulation

PA Bias Network:
├─ Base bias: Voltage divider from +5V
├─ Base resistor: 1 kΩ (for linearity)
├─ Emitter resistor: 100 Ω (for stability)
├─ Base-emitter voltage: ~0.65V (Vbe multiplier circuit)
├─ Stability: Temperature-compensated with thermistor
└─ Current mirror for bias current control

RF Transmission Line to Rb Cell:
├─ Type: Coaxial cable, 50 Ω (semi-rigid or flexible)
├─ Length: < 10 cm (minimize phase shift)
├─ Connector: SMA male (output) to SMA female (cell)
├─ Attenuation: < 0.5 dB @ 6.8 GHz
├─ Power rating: > 1 W (50 Ω, +23 dBm capable)
└─ Shielding: Double-braid copper (minimize EMI)

RF Safety:
├─ Maximum EIRP: +23 dBm + antenna gain (< -20 dBi in practice)
├─ FCC Part 15 compliance: Automatic via +20 dBm max (with antenna)
├─ Waveguide: Sealed (no direct RF exposure)
├─ Monitoring: RF power detector with alarm
└─ Kill switch: Manual RF enable/disable
```

---

## 2. OPTICAL SUBSYSTEM - DETAILED DESIGN

### 2.1 VCSEL Module Specifications

```
┌────────────────────────────────────────┐
│     VCSEL Optical Module Assembly      │
├────────────────────────────────────────┤
│                                        │
│  [TEC Controller IC]                   │
│       │ +5V, GND, PWM                  │
│       │                                │
│    ┌──▼──────────────────────────┐    │
│    │ Peltier TEC (-15°C to +30°C)│    │
│    │ Q = 4W cooling capacity     │    │
│    │ ΔT = 40°C max              │    │
│    └──┬──────────────────────────┘    │
│       │                                │
│    ┌──▼─────────────────────────┐    │
│    │ Laser Diode VCSEL          │    │
│    │ 794.98 nm (±0.1 nm)        │    │
│    │ 80 mW @ 80 mA              │    │
│    │ Wavelength vs I: 0.2 nm/mA │    │
│    │ Wavelength vs T: 0.08nm/°C │    │
│    └──┬──────────────────────────┘    │
│       │ Thermistor feedback           │
│       │ (NTC 10k@25°C)               │
│       │                                │
│    ┌──▼──────────────────────────┐    │
│    │ Collimation Lens            │    │
│    │ f = 5 mm, NA = 0.5          │    │
│    │ Beam diameter: 3 mm @ 1 m  │    │
│    └──┬──────────────────────────┘    │
│       │                                │
│    ┌──▼──────────────────────────┐    │
│    │ Optical Isolator (Faraday) │    │
│    │ Prevents back-reflections   │    │
│    │ Insertion loss: 0.5 dB      │    │
│    │ Isolation: > 40 dB          │    │
│    └──┬──────────────────────────┘    │
│       │                                │
│    ┌──▼──────────────────────────┐    │
│    │ Fiber Coupler              │    │
│    │ SMF-28 single-mode fiber   │    │
│    │ Coupling efficiency: 70%   │    │
│    │ Output power: 56 mW        │    │
│    └───────────────────────────┘    │
│                                        │
│    OUTPUT FIBER: SMF-28 (Panda)      │
│    Mode field diameter: 10.4 μm      │
│    Attenuation: 0.35 dB/km @ 794 nm │
│    Length: 2 meters (to AOM)         │
│                                        │
└────────────────────────────────────────┘

Power Budget:
VCSEL output:        80 mW (19 dBm)
Optical isolator:    -0.5 dB → 75 mW
Fiber coupler:       -1.5 dB → 56 mW (target)
Fiber attenuation:   -0.7 dB (2m @ 0.35 dB/km)
                     → 50 mW at AOM input
```

**VCSEL Specifications (Critical)**

```
Device: Custom III-V semiconductor VCSEL
Manufacturer: Broadcom HFBR-1524 (base technology)
Custom variant: 794 nm wavelength

Wavelength tolerance: 794.98 ± 0.1 nm
├─ Critical for CPT (Coherent Population Trapping)
├─ Rb-87 D1 line: 794.9788155 nm (literature value)
├─ Offset: < 0.001 nm (< 0.1 GHz detuning acceptable)
├─ Temperature tuning: 0.08 nm/°C
└─ Requires: ±0.01°C temperature control

Operating Current:
├─ Threshold current: ~15 mA
├─ Operating point: 80 mA (4× threshold, low noise)
├─ Maximum current: 120 mA (limit to prevent burnout)
├─ Current set by: Precision current source (DAC + Op-amp)

Wavelength Calibration:
├─ Initial tuning: Via Fabry-Perot etalon scan
├─ Factory calibration data provided
├─ In-service drift compensation: Via frequency counter feedback
└─ Tuning resolution: 0.001 nm (< 1 GHz)

Power vs Temperature:
├─ Operating range: 15 to 50°C
├─ Power change: -0.5%/°C (exponential with I)
├─ Therefore: -0.4 mW/°C @ 80 mA
├─ TEC control maintains constant temperature
└─ Effective power stability: ±1% (with TEC @ ±0.01°C)

Reliability:
├─ Mean time to failure (MTTF): 100,000+ hours
├─ Degradation rate: < 1%/1000 hours
├─ Aging: Wavelength drift ±0.1 nm/year
├─ Mechanism: Bandgap shrinkage + defect formation
└─ Mitigation: Over-design (operate at 70 mA instead of 100 mA maximum)
```

### 2.2 Acousto-Optic Modulator (AOM) Design

```
Critical for CPT (Coherent Population Trapping)
Creates ±3 GHz sidebands around 794 nm laser

┌─────────────────────────────────────────────────────┐
│            AOM CONFIGURATION (Bragg Cell)           │
├─────────────────────────────────────────────────────┤
│                                                      │
│  Input Laser Beam (794 nm, 50 mW, linear polarized)
│         │                                            │
│         ▼                                            │
│  ┌──────────────────────────────────────┐           │
│  │   RF DRIVE (6.834 GHz ± 3 MHz)       │           │
│  │   Power: 500 mW (+27 dBm)            │           │
│  │   Frequency: 6.834 GHz ± 3 MHz       │           │
│  │   (creates ±3 GHz sidebands)         │           │
│  │                                      │           │
│  │   ┌──────────────────────────────┐  │           │
│  │   │ Acoustic Transducer (PZT)    │  │           │
│  │   │ Resonant @ 6.834 GHz         │  │           │
│  │   │ Generates acoustic wave      │  │           │
│  │   └──────────────────────────────┘  │           │
│  └────┬─────────────────────────────────┘           │
│       │                                             │
│       │ Acousto-optic interaction                   │
│       │ (Bragg diffraction)                         │
│       │                                             │
│       ├─ 0th order: Undeviated beam (50%)          │
│       │   λ = 794 nm (original)                     │
│       │                                             │
│       ├─ +1st order: Frequency-up diffracted       │
│       │   λ = 794 - 3 GHz equivalent = 793.98 nm   │
│       │   Actually: 794 + Δν/c → f = f₀ + 3 GHz   │
│       │                                             │
│       └─ -1st order: Frequency-down diffracted     │
│           λ = 794 + 3 GHz equivalent               │
│           f = f₀ - 3 GHz                           │
│                                                     │
│  ┌──────────────────────────────┐                  │
│  │ Optical Output              │                  │
│  │ All 3 orders (+ balanced)   │                  │
│  │ Diffraction efficiency: 85% │                  │
│  └──────────────────────────────┘                  │
│         │     │      │                             │
│         ├─────┼──────┤                             │
│   (0.5× 0%)  (+3GHz) (-3GHz)                       │
│     50%      42.5%   42.5%                         │
│                                                     │
└─────────────────────────────────────────────────────┘

Design Details:

Cell (Acousto-optic crystal):
├─ Material: Quartz (SiO₂) or Tellurium Dioxide (TeO₂)
├─ Choice: TeO₂ (higher acousto-optic figure of merit)
├─ Dimension: ~10 mm long × 1 mm width × 1 mm height
├─ Cut: Anisotropic cut for 794 nm, 6.8 GHz
├─ Acoustic loss: < 3 dB/cm @ 6.8 GHz
└─ Thermal stability: ±0.01 nm/°C wavelength drift

Transducer:
├─ Material: Lithium niobate (LiNbO₃) or PZT ceramic
├─ Resonant frequency: 6.834 GHz ± 50 MHz
├─ Q factor: 100-150 (gives sharp resonance)
├─ Coupling efficiency: 90%+ to acoustic wave
├─ Acoustic impedance: Matched to TeO₂ via buffer layer
└─ Power handling: 500 mW continuous

RF Drive Circuit:
├─ Frequency: 6.834 GHz ± 3 MHz for CP T sweep
├─ Power: 500 mW minimum for 85% diffraction
├─ Amplifier: Custom broadband class C amp (50 Ω)
├─ Modulation: Amplitude modulation @ 1 MHz (for lock-in)
├─ Impedance matching: 50 Ω (T-network to transducer)
└─ Safety: RF monitor with alarm > 1W

Bragg Angle Calculation:
├─ Wavelength: 794 nm
├─ Acoustic frequency: 6.834 GHz
├─ Acoustic velocity (TeO₂): 4200 m/s (isotropic)
├─ Acoustic wavelength: Λ = v/f = 0.614 μm
├─ Bragg angle: θ_B = λ_light / (2Λ) = 794/1228 rad = 0.65 rad = 37°
└─ Diffraction angle: 2θ_B = 1.3 rad = 74° (separation)

Frequency Shift (Doppler):
├─ When acoustic wave has frequency f_a and velocity v_a
├─ Diffracted light shift: Δf = 2 × f_a (for 1st order)
├─ For ±3 GHz sidebands, need: f_a = ±1.5 GHz... but wait!
├─ Actually, transducer must oscillate at 6.834 GHz
├─ This creates sidebands at ±6.834 GHz from 794 nm (visible shift)
├─ But the electronic frequency of the sidebands = ±3 GHz
├─ (Details: Requires quantum optics analysis - approx here)
└─ Optical frequency ≫ RF frequency, so creates RF frequency shift

Power Budget (CPT configuration):
├─ Laser input: 50 mW
├─ 0th order (undeviated): 8 mW (50% × 85% × 20% residual)
├─ +1st order (π polarization): 21 mW (42.5% × 85% × 55%)
├─ -1st order (σ polarization): 21 mW
│  (π and σ are orthogonal polarizations for CPT)
├─ Total useful: 42 mW (out of 50 mW input)
├─ Fiber coupling efficiency (both orders): 70%
└─ To Rb cell: 29 mW (π + σ combined)

Lock-in Detection:
├─ RF drive amplitude modulation: 1 MHz, 10% depth
├─ This creates 1 MHz sidebands on AOM RF
├─ Which modulates the diffracted power at 1 MHz
├─ Photodetector sees 1 MHz modulation sideband
├─ Lock-in amplifier demodulates at 1 MHz → error signal
└─ Sensitivity: 10 ppm/Hz frequency offset
```

---

## 3. VACUUM & THERMAL SYSTEM

### 3.1 Rb Vapor Cell Specifications

```
Critical Parameters for Atomic Clock Performance

Cell Geometry:
├─ Shape: Spherical (uniform optical path length)
├─ Diameter (outer): 2.5 cm = 25 mm
├─ Diameter (inner): 20 mm (2 mm wall thickness)
├─ Volume: ~4.2 cm³
├─ Material: Borosilicate glass (Corning Pyrex 7740)
├─ Windows: 794 nm AR coated BK7 glass
└─ Cost: ~$200-300 (custom blown glass)

Rubidium Filling:
├─ Element: Rb-87 (natural rubidium is ~28% Rb-87)
├─ Mass: 8-12 mg of enriched Rb-87
├─ Purity: > 99.9%
├─ State in cell: Liquid Rb at room temp (liquid mercury-like)
├─ Vapor pressure @ 20°C: ~10^-8 Torr (negligible)
├─ Vapor pressure @ 60°C: ~10^-6 Torr (working condition)
├─ Saturation density @ 60°C: ~10^11 atoms/cm³
└─ Supplier: ISRA (Isotope Science, Inc.) or Sigma-Aldrich

Buffer Gas:
├─ Gas: Neon (Ne), stable isotope (inert)
├─ Pressure: 10 ± 1 Torr @ 60°C
├─ Purpose: Reduce collision broadening, increase coherence time
├─ Role: Anti-relaxation via elastic collisions (no depolarization)
├─ Polarization preservation: > 99.9% per collision
├─ Diffusion rate: Increases Doppler width slightly
└─ Consequence: Requires higher laser power for saturation

Anti-Relaxation Coating:
├─ Material: Polydimethylsiloxane (PDMS) or paraffin wax
├─ Thickness: 0.5-1 μm monolayer
├─ Purpose: Reduces magnetic relaxation at cell walls
├─ Effect: Extends coherence time to milliseconds (vs microseconds bare)
├─ Application: Oven baking @ 200°C in toluene vapor (PDMS)
├─ Verification: Ramsey fringe contrast measurement
└─ Shelf life: 2-3 years (coating degrades slowly)

Temperature Control:
├─ Set point: 60°C ± 0.5°C
├─ Stability requirement: ±0.5°C (frequency stability ~ ±100 ppm/°C)
├─ Warm-up time: < 60 seconds to reach 60°C
├─ Heating method: Nichrome wire wrap around cell
├─ Power: ~5W continuous (resistive heating)
├─ Temperature sensor: NTC 10k Ω thermistor @ cell
├─ Control loop: PID feedback via Eurotherm nanodac
└─ Copper block heat sink: ~50 cm³, 100g (provides thermal mass)

Optical Properties @ 794 nm:
├─ Transmission (empty cell, no coating): > 99% per window
├─ Transmission (with PDMS coating): > 95% per window
├─ Absorption (Rb vapor @ 60°C): ~50% (at resonance)
├─ Saturation intensity: ~1.6 mW/cm² (for D1 line)
├─ Beam profile in cell: Gaussian, diameter ~2 mm
├─ Power at cell: 29 mW (π + σ combined from AOM)
├─ Intensity in cell: ~91 mW/cm² (saturated regime)
└─ Expected absorption: ~25 mW absorbed (rest transmits)
```

### 3.2 Vacuum System Design

```
Two-stage vacuum system

STAGE 1: Turbomolecular Pump (Primary)
├─ Model: Edwards nXDS6i or Leybold Turbovac 90
├─ Pumping speed: 6 L/s
├─ Inlet pressure (max): 10 Torr
├─ Ultimate pressure: < 10^-7 Torr (no backing)
├─ Maximum outlet pressure: 1 Torr (with backing pump)
├─ Rotor speed: 90,000 rpm (contact bearings)
├─ Power consumption: 80 W (steady state)
├─ Warm-up time: 3 minutes to full speed
├─ Safety: High-vacuum cut-off (prevents reverse flow)
├─ Cost: ~$3000-4000
└─ IMPORTANT: Requires backing pump (cannot start at atmosphere)

STAGE 2: Backing/Rough Pump
├─ Type: Rotary vane pump (oil-sealed)
├─ Model: Trivac ILMVAC or equivalent
├─ Pumping speed: 0.6 L/s (at inlet)
├─ Compression ratio: 20:1
├─ Inlet pressure: 0.1 - 1 Torr (from turbo pump outlet)
├─ Outlet pressure: Atmosphere (1000 Torr)
├─ Power consumption: 150 W (steady state)
├─ Oil capacity: 0.5 L (requires regular replacement)
├─ Noise: 70-75 dB (fairly loud)
├─ Cost: ~$1500-2000
└─ Maintenance: Oil change every 40-50 hours

System Configuration:
├─ Start sequence:
│  1. Open backing pump isolation valve
│  2. Start backing pump (evacuate to ~10 Torr)
│  3. Open turbo pump isolation valve
│  4. Turn on turbo pump (ramp up over 1 minute)
│  5. When turbo speed reaches 90,000 rpm, system ready
│  6. Turbo vacuum improves from 10 Torr to 10^-5 Torr (takes 20 minutes)
│  7. Final vacuum: 10^-6 to 10^-7 Torr
│
├─ Shut-down sequence (CRITICAL - prevents damage):
│  1. Close turbo inlet isolation valve
│  2. Let turbo coast to stop (5-10 minutes, controlled deceleration)
│  3. Turn off turbo motor
│  4. Close turbo outlet isolation valve
│  5. Turn off backing pump
│  6. (Turbo running at speed while closing inlet would create backflow)
│
├─ Emergency ventilation (for maintenance):
│  1. Close both isolation valves
│  2. Open fine needle valve to atmosphere (slow bleed-in)
│  3. Wait until chamber reaches 1 Torr
│  4. Then open full vent (prevents sudden pressure spike)
│  5. Equalize to atmosphere before opening cell
└─ Typical cycle time: 20 minutes pumpdown, 5 minutes cool-down


Pressure Monitoring:
├─ Gauge 1 (coarse): Pirani gauge (0-1000 Torr, accuracy ~10%)
│  Used to monitor turbo inlet pressure
│  Controller: Leybold CERAVAC CTR 90
│
├─ Gauge 2 (fine): Baratron MKS 627D (0-10 Torr, accuracy ±1%)
│  Measures actual cell buffer gas pressure
│  Cold cathode ionization gauge (capacity ~10^-3 Torr)
│  Required for CPT lock-in (cell pressure critical to line shape)
│
└─ Pressure vs Performance:
   Cell pressure 5 Torr:   Weak absorption, poor signal/noise
   Cell pressure 10 Torr:  Optimal for CPT (design point)
   Cell pressure 15 Torr:  Increased collisional broadening

   → Must maintain 10 ± 1 Torr during operation

Vacuum Integrity:
├─ Leak rate goal: < 10^-7 Torr-L/s (ultra-high vacuum standard)
├─ Test method: He sniffer (helium leak detector)
│  1. Fill chamber with ~1 torr He
│  2. Scan all seals with probe
│  3. Detector sensitivity: 10^-9 Torr-L/s
│  4. Any peak indicates leak location
│
├─ Sealing materials:
│  - O-rings: Viton (FKM) or EPDM (not nitrile at high vacuum)
│  - Sealant: UHV epoxy or silver-filled epoxy
│  - Threads: Stainless steel with anti-seize compound
│  - Connections: Welded or brazed (preferred over threaded)
│
└─ Long-term outgassing:
   - Initial bake-out: 80°C for 24 hours (releases absorbed water)
   - Residual gas analysis (RGA): Check for H₂O, CO₂, N₂ peaks
   - Ultimate goal: All peaks < 10^-7 Torr (partial pressure)
```

---

## 4. ELECTRONIC CONTROL SYSTEM

### 4.1 Microcontroller Firmware Architecture

```c
// STM32H743 Real-Time Firmware Structure

#include "stm32h743xx.h"
#include "arm_math.h"  // DSP library

// HARDWARE CONFIGURATION
#define SERVO_LOOP_FREQ    100000  // 100 kHz servo control
#define TELEMETRY_FREQ     1000    // 1 kHz status reporting
#define CHARACTERIZATION_FREQ 1    // 1 Hz long-term analysis

// ADC Configuration (12-bit, 1 MSPS)
#define ADC_I_CHANNEL      ADC_CHANNEL_0  // I (in-phase) demodulation
#define ADC_Q_CHANNEL      ADC_CHANNEL_1  // Q (quadrature) demodulation
#define ADC_TEMP_CHANNEL   ADC_CHANNEL_2  // Cell temperature
#define ADC_PRESSURE_CHANNEL ADC_CHANNEL_3 // Cell pressure

// DAC Configuration (12-bit)
#define DAC1_OUTPUT        DAC_CHANNEL_1   // VCO tuning voltage
#define DAC2_OUTPUT        DAC_CHANNEL_2   // RF amplitude control

// SPI Configuration (10 MHz)
#define SPI_ADF4159_SPEED  10000000  // 10 MHz SPI clock

// CONTROL LOOP PARAMETERS
struct PID_Control {
    float Kp;           // Proportional gain
    float Ki;           // Integral gain
    float Kd;           // Derivative gain
    float integral;     // Running integral
    float prev_error;   // Previous error (for derivative)
    float max_output;   // Output saturation limit
    float min_output;
};

struct Lock_In_Amplifier {
    float I_filtered;   // I-channel (in-phase) 100 kHz low-pass
    float Q_filtered;   // Q-channel (quadrature) 100 kHz low-pass
    float magnitude;    // |I² + Q²|
    float phase;        // atan2(Q, I)
    float error_signal; // Discriminator output
};

struct System_State {
    uint64_t timestamp;  // Time since power-on (nanoseconds)
    uint32_t frequency;  // Locked frequency (Hz) from frequency counter
    float temperature;   // Cell temperature (°C)
    float pressure;      // Cell pressure (Torr)
    float vco_tune_voltage; // DAC output to VCO (0-3.3V)
    float rf_power_dbm;  // RF output power (dBm)
    struct PID_Control servo_loop;
    struct Lock_In_Amplifier lock_in;
    float stability_adev[5]; // Allan deviation @ 1s, 10s, 100s, 1000s, 10000s
};

// MAIN SERVO LOOP (Runs every 10 μs at 100 kHz)
void HAL_TIM_PeriodElapsedCallback(TIM_HandleTypeDef *htim) {
    // 1. Read ADC (I, Q channels)
    uint16_t adc_i_raw = ADC1->DR;  // 12-bit raw count
    uint16_t adc_q_raw = ADC2->DR;

    // 2. Convert to voltage (0-3.3V range)
    float V_i = (adc_i_raw / 4096.0) * 3.3;
    float V_q = (adc_q_raw / 4096.0) * 3.3;

    // 3. Low-pass filter (100 kHz cutoff)
    // First-order IIR filter: y[n] = α·x[n] + (1-α)·y[n-1]
    // α = 2πfc·Ts / (1 + 2πfc·Ts)
    // α ≈ 0.545 for fc=100kHz, Ts=10μs
    float alpha = 0.545;
    lock_in.I_filtered = alpha*V_i + (1-alpha)*lock_in.I_filtered;
    lock_in.Q_filtered = alpha*V_q + (1-alpha)*lock_in.Q_filtered;

    // 4. Compute error signal (discriminator)
    // Error_signal = I (in-phase component)
    // For Ramsey spectroscopy: Error ∝ sin(2πΔf·T_ramsey)
    // where Δf is frequency offset
    float error = lock_in.I_filtered;

    // 5. PID Control Loop
    PID_Control* pid = &system.servo_loop;

    // Proportional term
    float P_term = pid->Kp * error;

    // Integral term (with anti-windup)
    pid->integral += error * (1.0/SERVO_LOOP_FREQ);
    if (pid->integral > pid->max_output) pid->integral = pid->max_output;
    if (pid->integral < pid->min_output) pid->integral = pid->min_output;
    float I_term = pid->Ki * pid->integral;

    // Derivative term (with low-pass filtering)
    float derivative = (error - pid->prev_error) * SERVO_LOOP_FREQ;
    float D_term = pid->Kd * derivative;
    pid->prev_error = error;

    // Control voltage output
    float control_voltage = P_term + I_term + D_term;

    // Saturation (protect VCO)
    if (control_voltage > pid->max_output) control_voltage = pid->max_output;
    if (control_voltage < pid->min_output) control_voltage = pid->min_output;

    // 6. Output to DAC (VCO tuning)
    uint16_t dac_count = (control_voltage / 3.3) * 4096;  // Convert voltage to 12-bit count
    DAC1->DHR12R1 = dac_count;

    // 7. Store for diagnostics
    system.vco_tune_voltage = control_voltage;

    // 8. Every 100 servo loops, read temperature/pressure (slower sampling)
    static int counter = 0;
    if (counter++ >= 100) {
        counter = 0;

        // Read temperature ADC
        uint16_t temp_raw = ADC_Read_Channel(ADC_TEMP_CHANNEL);
        // Steinhart-Hart equation: 1/T = A + B*ln(R) + C*ln(R)³
        float resistance = 10000.0 * (4096.0 - temp_raw) / temp_raw;  // NTC divider
        float temp_kelvin = 1.0 / (1.009e-3 + 2.378e-4*log(resistance) + 2.019e-7*pow(log(resistance),3));
        system.temperature = temp_kelvin - 273.15;  // Convert to Celsius

        // Read pressure ADC
        uint16_t pressure_raw = ADC_Read_Channel(ADC_PRESSURE_CHANNEL);
        // Baratron: 0-10 Torr → 0-10V → ADC maps linearly
        system.pressure = (pressure_raw / 4096.0) * 10.0;

        // Health checks
        if (system.temperature > 65.0) { /* heater overheat alert */ }
        if (system.pressure > 12.0) { /* pump failure alert */ }
    }
}

// FREQUENCY COUNTER (1 kHz loop, updates every 1 ms)
void frequency_counter_update() {
    // Count zero-crossings of VCO output (after divider)
    // VCO @ 6.834 GHz, divide by 683.468 (SPI register)
    // Expected output: 10 MHz exactly

    // Frequency = (count × reference_freq) / measurement_interval
    static uint32_t last_count = 0;
    uint32_t current_count = TIMER_GET_COUNT(TIM5);  // 32-bit counter
    uint32_t delta = current_count - last_count;
    last_count = current_count;

    // Frequency (in Hz, relative to 10 MHz reference)
    float measured_freq = (delta * 1000.0) + 10e6;  // 1000 Hz resolution

    // Frequency error
    float freq_error_hz = measured_freq - 6834682610.0;
    float freq_error_ppm = freq_error_hz / 6834682610.0 * 1e6;

    system.frequency = (uint32_t)measured_freq;

    // Update PID gains based on lock status
    if (fabs(freq_error_ppm) > 1.0) {
        // Out of lock (> 1 ppm error)
        system.servo_loop.Kp = 0.001;  // Slower acquisition
        system.servo_loop.Ki = 0.00001;
    } else {
        // In lock (< 1 ppm)
        system.servo_loop.Kp = 0.0005;  // Tighter regulation
        system.servo_loop.Ki = 0.00005;
    }
}

// LONG-TERM STABILITY ANALYSIS (1 Hz loop, runs every 1 second)
void allan_deviation_update() {
    // Compute Allan deviation over multiple timescales
    // ADEV(τ) = sqrt(1/(2(n-1)) * Σ(y[i+1] - y[i])²)
    // where y[i] are fractional frequency measurements

    static float freq_history[10000];  // 10,000 seconds = 2.8 hours
    static int history_index = 0;

    float frac_freq = (float)system.frequency / 6834682610.0;  // Fractional frequency
    freq_history[history_index++] = frac_freq;

    if (history_index >= 10000) history_index = 0;  // Circular buffer

    // Compute ADEV at τ = 1s, 10s, 100s, 1000s, 10000s
    // ... (requires buffering and statistical computation)
}

// TELEMETRY OUTPUT (1 kHz loop)
void telemetry_send() {
    // Send metrics via UART or Ethernet
    // Format: JSON for easy parsing
    printf("{\"time_ns\": %llu, \"freq_hz\": %u, \"temp_c\": %.2f, \"pressure_torr\": %.2f, \"vco_v\": %.3f}\n",
           system.timestamp, system.frequency, system.temperature, system.pressure, system.vco_tune_voltage);
}

// INITIALIZATION
void system_init() {
    // 1. Clock configuration (480 MHz)
    SystemClock_Config();

    // 2. ADC setup (12-bit, 1 MSPS)
    ADC1_Init();
    ADC2_Init();

    // 3. DAC setup (12-bit)
    DAC1_Init();
    DAC2_Init();

    // 4. SPI (10 MHz for ADF4159)
    SPI1_Init(SPI_BAUDRATE_DIV_8);  // 480MHz / 8 = 60 MHz (still valid, ADF accepts 10-20 MHz)

    // 5. Timers
    TIM5_Init(100000);  // 100 kHz servo loop
    TIM6_Init(1000);    // 1 kHz telemetry
    TIM7_Init(1);       // 1 Hz analysis

    // 6. UART (serial output)
    UART4_Init(115200);  // Standard serial port

    // 7. PID Initial values
    system.servo_loop.Kp = 0.001;
    system.servo_loop.Ki = 0.00001;
    system.servo_loop.Kd = 0.0;
    system.servo_loop.max_output = 3.3;   // DAC max
    system.servo_loop.min_output = 0.0;

    // 8. Frequency counter
    TIM5_CounterMode_Init();  // Edge detection on VCO output

    // 9. ADF4159 Configuration via SPI
    adf4159_init();

    // 10. Enable interrupts
    NVIC_EnableIRQ(TIM5_IRQn);  // Servo loop
    NVIC_EnableIRQ(TIM6_IRQn);  // Telemetry
    HAL_TIM_Base_Start_IT(&htim5);
}

int main(void) {
    system_init();

    // Infinite loop (all work done in interrupts)
    while (1) {
        // Optional: Handle UART commands for diagnostics
        // Optional: Update display with metrics
        // Optional: Log data to SD card
    }

    return 0;
}
```

---

## 5. TESTING & CHARACTERIZATION PROCEDURES

### 5.1 Frequency Accuracy Verification

```
Equipment: Cesium clock reference + frequency counter

Test Procedure:
1. Power on atomic clock, wait 5 minutes warm-up
2. Connect 10 MHz output to Cesium reference
3. Measure frequency offset: f_measured - 6,834,682,610 Hz
4. Record for 24 hours minimum
5. Success: ±1 Hz accuracy (±0.146 ppb)

Alternative test (without Cesium):
- Use GPS receiver (accuracy ±100 ns → ±10 Hz)
- Sufficient for basic verification
```

### 5.2 Stability Measurement

```
Allan Deviation (ADEV) Test

Equipment: Counter with internal 10 MHz reference

Procedure:
1. Measure frequency every 1 second for 24 hours
2. Compute fractional frequency differences
3. Calculate ADEV(τ) for τ = 1s, 10s, 100s, 1000s, 10000s
4. Plot on log-log scale

Success criteria:
- ADEV(1s) < 5×10^-11
- ADEV(100s) < 1×10^-11
- ADEV(1000s) < 5×10^-12
```

---

## END OF CRITICAL DESIGN SPECS

This document provides the detailed engineering specifications needed to build the RF, optical, and control subsystems. Each section includes component selections, circuit details, and design equations.

**Next steps:**
1. Procure components and verify specifications
2. Design PCB layouts (RF layout critical)
3. Develop firmware on prototype hardware
4. Characterize performance at each phase
