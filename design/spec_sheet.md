# CSAC MEMS — Design Specification Sheet
**Version: 0.0 — Awaiting Phase 1 simulation results**

---

## Status

| Module | Status | Key output |
|---|---|---|
| 00_atomic_model | NOT RUN | CPT linewidth, contrast |
| 01_vcsel_sideband | NOT RUN | β modulation index |
| 02_buffer_gas | NOT RUN | N2 pressure |
| 03_mems_geometry | NOT RUN | Cavity dimensions |
| 04_thermal | NOT RUN | Heater power, PID |
| 05_optical | NOT RUN | SNR, beam size |
| 06_rf_synthesis | NOT RUN | VCO tuning, phase noise |
| 07_servo_loop | NOT RUN | PID gains, bandwidth |
| 08_allan | NOT RUN | ADEV prediction |
| 09_fullchain | NOT RUN | System go/no-go |

---

## Performance Specification (fill after Phase 1)

| Parameter | Simulated | Target | SA65 Benchmark |
|---|---|---|---|
| ADEV @ τ=1s | — | < 5×10⁻¹⁰ | 2.5×10⁻¹⁰ |
| ADEV @ τ=1hr | — | < 1×10⁻¹¹ | — |
| Power consumption | — | < 150 mW | 120 mW |
| CPT linewidth | — | < 5 kHz | 3–5 kHz |
| CPT contrast | — | > 3% | 3–8% |
| Cell temperature | — | 85°C ±0.01°C | 80–90°C |
| Output frequency | 10 MHz | 10 MHz | 10 MHz |
| Cell footprint | — | < 4×4 mm | 1.5×1.5×1.5 mm |

---

## Operating Parameters (for foundry — fill after Phase 1)

| Parameter | Value | Source module |
|---|---|---|
| N2 fill pressure | — Torr | 02_buffer_gas |
| Cavity diameter | — mm | 03_mems_geometry |
| Cavity depth | — mm | 03_mems_geometry |
| Glass thickness | — mm | 03_mems_geometry |
| Pt heater resistance | — Ω | 04_thermal |
| Heater power budget | — mW | 04_thermal |
| Pt RTD resistance @ 25°C | — Ω | 04_thermal |
| VCSEL modulation index β | — | 01_vcsel_sideband |
| RF drive power | — dBm | 01_vcsel_sideband |
| VCO tuning range | — MHz | 06_rf_synthesis |
