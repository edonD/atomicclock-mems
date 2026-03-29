# CSAC MEMS Design Specification — Version 1.0 — Phase 1 Complete — 2026-03-29

> **Status:** Phase 1 simulation complete. All 10 modules simulated. Phase 2 (layout & tape-out prep) authorized.

---

## 1. Module Status

| # | Module | Status | Key Output |
|---|---|---|---|
| 00 | Atomic model (QuTiP CPT) | **PASS** | CPT linewidth 3.01 kHz, contrast 34.78% |
| 01 | VCSEL sideband | **PASS** | β = 1.84, sideband power 67.7%, RF drive 5.97 dBm |
| 02 | Buffer gas | **PASS** | N₂ optimal 76.6 Torr, pressure shift −513 kHz |
| 03 | MEMS geometry (FEM) | **PASS** | 1.5 mm × 1.0 mm cavity, safety factor 3.86 |
| 04 | Thermal (FEM) | **PASS** | 73.8 mW heater, 4.2×10⁻⁵ °C stability |
| 05 | Optical | **PASS** | SNR 1.62×10⁶, beam Ø 152.6 µm at cell exit |
| 06 | RF synthesis | **PASS** | ADF4351 PLL, freq error 0.90 Hz, VCO ADEV 9.25×10⁻¹⁵ |
| 07 | Servo loop | **PASS** | 30 Hz lock BW, PM 84.9°, GM 60 dB |
| 08 | Allan deviation | **PASS** | ADEV(1s) = 1.07×10⁻¹¹ |
| 09 | Full-chain integration | **GO** | ADEV(1s) = 8.84×10⁻¹², power 123.8 mW, Phase 2 ready |

---

## 2. Top-Level Performance vs. Targets vs. SA65 Benchmark

| Parameter | Simulated | Target | SA65 Benchmark | Margin |
|---|---|---|---|---|
| ADEV @ τ = 1 s | **8.84×10⁻¹²** | < 5×10⁻¹⁰ | 2.5×10⁻¹⁰ | 28× better than target |
| ADEV @ τ = 10 s | **3.37×10⁻¹²** | — | — | — |
| ADEV @ τ = 100 s | **1.07×10⁻¹²** | — | — | — |
| ADEV @ τ = 1 hr | **1.78×10⁻¹³** | < 1×10⁻¹¹ | — | 56× better than target |
| Total power | **123.8 mW** | < 150 mW | 120 mW | 17.5% headroom vs target |
| CPT linewidth | **3.01 kHz** (physics) / **3.2 kHz** (servo) | < 5 kHz | 3–5 kHz | PASS |
| CPT contrast | **34.78%** (physics) / **4.8%** used in ADEV | > 3% | 3–8% | PASS |
| Cell temperature | **85°C ± 4.2×10⁻⁵ °C** | 85°C ± 0.01°C | 80–90°C | 238× better than target |
| Output frequency | **10 MHz** (divided from 3.4 GHz PLL) | 10 MHz | 10 MHz | PASS |
| Cell footprint | **3×3 mm die** | < 4×4 mm | 1.5×1.5 mm | PASS |
| Startup time | **78.5 s** | < 120 s | ~180 s | PASS |
| Weakest link | **Thermal stability** | — | — | Sensitivity 9.93/°C |

---

## 3. Atomic Physics Specifications

| Parameter | Value | Source | Notes |
|---|---|---|---|
| Rb-87 ground-state hyperfine | **6 834 682 610.904 Hz** | 00_atomic_model | SI definition; used as clock transition |
| D1 line wavelength | **794.978851 nm** (vacuum) | 00_atomic_model | Rb-87 5S₁/₂ → 5P₁/₂ |
| Natural linewidth (D1) | ~5.75 MHz | Literature | Doppler-free |
| CPT linewidth (QuTiP sim) | **3.01 kHz** | 00_atomic_model | Buffer-gas broadened, 76.6 Torr N₂ |
| CPT contrast | **34.78%** | 00_atomic_model | Peak absorption ratio |
| Rb density in cell | **2.58×10¹⁸ m⁻³** | 02_buffer_gas | At 85°C operating temperature |
| Pressure shift coefficient | **−6.7 kHz/Torr** (N₂) | 02_buffer_gas | Rb-87 clock transition |
| Pressure broadening coefficient | **10.8 kHz/Torr** (N₂) | 02_buffer_gas | Lorentzian broadening |
| Pressure shift (at 76.6 Torr) | **−513.1 kHz** | 02_buffer_gas | Absorbed into PLL offset |
| Temperature coefficient | **−1432.65 Hz/°C** | 02_buffer_gas | Clock freq sensitivity to cell T |
| Optimal N₂ pressure | **76.58 Torr** | 02_buffer_gas | Linewidth–shift tradeoff optimum |
| CPT linewidth at optimum | **1.95 kHz** | 02_buffer_gas | Pressure-broadened estimate |

---

## 4. MEMS Cell Specifications

| Parameter | Value | Tolerance | Source |
|---|---|---|---|
| Cavity diameter | **1.5 mm** | ±5% (±75 µm) | 03_mems_geometry |
| Cavity depth | **1.0 mm** | ±5% (±50 µm) | 03_mems_geometry |
| Si substrate thickness | **0.5 mm** | ±25 µm | Design spec |
| Borofloat 33 glass (top) | **0.3 mm** | ±15 µm | 03_mems_geometry |
| Borofloat 33 glass (bottom) | **0.3 mm** | ±15 µm | 03_mems_geometry |
| Total stack height | **1.1 mm** | — | Si 0.5 mm + 2× glass 0.3 mm |
| Die area | **9.0 mm²** (3×3 mm) | — | 03_mems_geometry |
| Bond ring stress (anodic) | **2.59 MPa** | — | 03_mems_geometry FEM |
| Borofloat 33 tensile strength | **~10 MPa** | — | Literature |
| Bond safety factor | **3.86×** | ≥ 2.0× required | 03_mems_geometry — PASS |
| Lowest resonance mode | **448 293 Hz** (~448 kHz) | — | 03_mems_geometry FEM |
| Optical path length (αL) | **1.2016** | — | 05_optical, base |
| Effective αL (pressure-broadened) | **0.00611** | — | 05_optical |
| N₂ fill pressure | **76.58 Torr** | ±2 Torr | 02_buffer_gas |

---

## 5. Optical Specifications

| Parameter | Value | Source |
|---|---|---|
| VCSEL input power | **200 µW** | 05_optical (assumed) |
| VCSEL wavelength | **794.979 nm** | 00_atomic_model |
| Beam diameter at cell exit | **152.6 µm** | 05_optical |
| Rayleigh range | **63.2 µm** | 05_optical |
| Beam waist at photodetector | **120.8 µm** | 05_optical |
| Beam clipping margin (vs 1.5 mm cavity) | **× 9.8 clearance** | 05_optical — no clipping |
| Pressure broadening factor | **196.8×** | 05_optical |
| Effective absorption (αL) | **0.611%** | 05_optical |
| Window transmission (both surfaces) | **84.93%** | 05_optical (Borofloat R-loss) |
| Cell transmission | **99.39%** | 05_optical |
| Total optical transmission | **84.42%** | 05_optical |
| Optical power at photodetector | **168.8 µW** | 05_optical |
| Photodiode current | **84.4 µA** | 05_optical (@ 0.5 A/W resp.) |
| Optical SNR | **1.62×10⁶ (62.2 dB)** | 05_optical |
| Dominant noise source | Shot noise | 05_optical |

---

## 6. RF / Electronics Specifications

| Parameter | Value | Source |
|---|---|---|
| Target frequency (×2 to Rb clock) | **3 417 341 305.452 Hz** | 06_rf_synthesis |
| PLL actual frequency | **3 417 341 306.348 Hz** | 06_rf_synthesis |
| Frequency quantization error | **0.896 Hz** | 06_rf_synthesis |
| PLL dividers (N / F / M) | **341 / 798 / 1087** | 06_rf_synthesis |
| PLL reference | **10 MHz TCXO** | 06_rf_synthesis |
| Recommended PLL chip | **ADF4351** (AD, 35 MHz–4.4 GHz, ~$15) | 06_rf_synthesis |
| Tuning range | **±1.539 MHz** | 06_rf_synthesis |
| Required tuning voltage | **0.154 V** | 06_rf_synthesis |
| Achievable frequency step | **9.2 kHz** | 06_rf_synthesis |
| VCO phase noise | **−90 dBc/Hz @ 1 Hz offset** | 06_rf_synthesis |
| VCO ADEV contribution @ 1 s | **9.25×10⁻¹⁵** | 06_rf_synthesis — negligible |
| VCSEL modulation index β | **1.841** | 01_vcsel_sideband |
| J₀(β) carrier suppression | **0.316** | 01_vcsel_sideband |
| J₁(β) first sideband amplitude | **0.582** | 01_vcsel_sideband |
| Sideband power fraction | **67.7%** | 01_vcsel_sideband |
| RF drive power to VCSEL | **5.97 dBm** | 01_vcsel_sideband |
| Sideband spacing | **6.834682610904 GHz** | 01_vcsel_sideband (= hyperfine) |

---

## 7. Thermal Specifications

| Parameter | Value | Source |
|---|---|---|
| Cell operating temperature | **85°C** | Design requirement |
| Heater power (steady-state) | **73.84 mW** | 04_thermal FEM |
| Heater resistance | **100 Ω** | 04_thermal |
| Heater trace material | **Pt (200 nm / Ti 20 nm adhesion)** | 04_thermal |
| Heater trace width | **50 µm** | 04_thermal |
| Heater trace length | **6.289 mm** | 04_thermal |
| Heater trace pattern | Serpentine on Si surface | 04_thermal |
| Temperature stability (PID closed-loop) | **4.2×10⁻⁵ °C** | 04_thermal |
| Thermal gradient across cell | **0.052 °C/mm** | 04_thermal |
| Startup time (25°C → 85°C) | **78.5 s** | 04_thermal |
| RTD material | **Pt (200 nm)** | 04_thermal |
| RTD trace width | **20 µm** | 04_thermal |
| RTD resistance @ 0°C | **100 Ω** (target) | 04_thermal |
| RTD resistance @ 85°C | **132.80 Ω** | 04_thermal |
| RTD sensitivity | **0.381 Ω/°C** | 04_thermal |
| RTD thermal noise (RMS) | **1.35×10⁻⁵ °C** | 04_thermal |
| PID Kp | **0.003** | 04_thermal |
| PID Ki | **0.0003** | 04_thermal |
| PID Kd | **0.005** | 04_thermal |
| Plant gain (K) | **1692.77 °C/W** | 04_thermal |
| Plant time constant (τ) | **20.0 s** | 04_thermal |
| Convection heat loss | **37.2 mW** | 04_thermal |
| Conduction heat loss | **10.0 mW** | 04_thermal |
| Radiation heat loss | **19.93 mW** | 04_thermal |

---

## 8. Servo Loop Specifications

| Parameter | Value | Source |
|---|---|---|
| Loop type | Frequency-modulation / phase-sensitive detection | 07_servo_loop |
| Lock bandwidth | **30 Hz** | 07_servo_loop |
| Phase margin | **84.9°** | 07_servo_loop |
| Gain margin | **60 dB** | 07_servo_loop |
| Capture range | **±1.6 kHz** | 07_servo_loop |
| Servo Kp | **0.2413** | 07_servo_loop |
| Servo Ki | **4.548** | 07_servo_loop |
| Servo Kd | **1.28×10⁻⁵** | 07_servo_loop |
| CPT linewidth used in servo model | **3.2 kHz** | 07_servo_loop |

---

## 9. System-Level Specifications

| Parameter | Value | Notes |
|---|---|---|
| Total ADEV @ τ = 1 s | **8.84×10⁻¹²** | Full-chain integration (09_fullchain) |
| Allan deviation breakdown @ 1 s | | |
| — Shot noise contribution | **6.01×10⁻¹²** | 08_allan |
| — Thermal noise contribution | **8.81×10⁻¹²** | 08_allan (dominant) |
| — VCO noise contribution | **9.25×10⁻¹⁵** | 08_allan (negligible) |
| Dominant noise source @ 1 s | **Thermal stability** | 09_fullchain sensitivity analysis |
| Thermal sensitivity | **9.93 / °C** (fractional freq / °C) | 09_fullchain |
| Total power consumption | **123.8 mW** | 09_fullchain |
| — Heater | **73.84 mW** | 04_thermal |
| — VCSEL + driver | **5.0 mW** | 09_fullchain |
| — RF synthesizer (ADF4351) | **30.0 mW** | 09_fullchain |
| — Digital / µC | **15.0 mW** | 09_fullchain |
| Phase 2 authorization | **GO** | 09_fullchain evaluator |

---

## 10. Manufacturing Tolerances and Safety Factors

| Parameter | Simulated Value | Limit / Requirement | Margin |
|---|---|---|---|
| Bond ring stress | 2.59 MPa | < 5 MPa (glass fracture / 2) | **1.93× under limit** |
| Bond safety factor | **3.86×** | ≥ 2.0× | **93% margin** |
| Beam clipping: beam Ø at exit | 152.6 µm | Cavity Ø 1500 µm | **9.8× clearance** |
| Cavity depth tolerance | ±50 µm (±5%) | < ±10% per optical path | PASS |
| Cavity diameter tolerance | ±75 µm (±5%) | Beam clearance maintained | PASS |
| N₂ pressure tolerance | ±2 Torr (±2.6%) | ±5 Torr spec | **50% margin** |
| Heater resistance tolerance | ±10 Ω (target 100 Ω) | ±20% of design | PASS |
| RTD resistance tolerance | ±5 Ω (target 100 Ω) | ±10% of design | PASS |
| Lowest structural resonance | 448 kHz | > 1 kHz (vibration immunity) | PASS |
| Dicing lane width | 200 µm | ≥ 100 µm (blade kerf) | **2× margin** |
| Die size | 3×3 mm | ≤ 4×4 mm target | PASS |

---

## 11. SA65 Comparison Table

| Parameter | This Design (Simulated) | SA65 (Datasheet) | Notes |
|---|---|---|---|
| ADEV @ τ = 1 s | **8.84×10⁻¹²** | 2.5×10⁻¹⁰ | **28× better** |
| ADEV @ τ = 100 s | **1.07×10⁻¹²** | ~5×10⁻¹¹ | **47× better** |
| Total power | **123.8 mW** | 120 mW | Comparable (+3%) |
| Cell footprint | **3×3 mm** | ~5×5 mm physics pkg | Smaller |
| CPT linewidth | **3.01 kHz** | 3–5 kHz | Within range |
| CPT contrast | **34.78%** (physics) | 3–8% (measured) | Physics sim vs operated |
| Operating temperature | **85°C** | 80–90°C | Compatible |
| Startup time | **78.5 s** | ~180 s (typ.) | **Faster** |
| N₂ buffer gas pressure | **76.6 Torr** | 60–80 Torr (typ.) | Compatible |
| RF sideband architecture | EOM / VCSEL FM | VCSEL FM | Same approach |

> **Note:** The SA65 ADEV figures are for a production-grade, long-aged device. The simulated ADEV here is a pre-layout physics estimate. Phase 2 will refine with parasitic extraction and noise margin analysis.

---

*Document generated from Phase 1 simulation results — 2026-03-29.*
*Modules: 00_atomic_model, 01_vcsel_sideband, 02_buffer_gas, 03_mems_geometry, 04_thermal, 05_optical, 06_rf_synthesis, 07_servo_loop, 08_allan, 09_fullchain.*
