# Freedom to Operate — Technical Brief
## MEMS Rb-87 CPT Chip-Scale Atomic Clock with Integrated Pt Heater/RTD

**Prepared by:** Engineering Team, CSAC MEMS Project
**Date:** 2026-03-29
**Intended recipient:** Patent counsel
**Purpose:** Pre-filing FTO scoping — identify prior art landscape, define novel aspects, and outline potential claim directions for attorney review.

---

> **DISCLAIMER:** This document is a technical engineering brief prepared to assist patent counsel.
> It is **not legal advice** and does not constitute a freedom-to-operate opinion. Only a licensed
> patent attorney or agent can provide an FTO opinion. This brief does not identify all potentially
> relevant patents and has not been prepared with the rigor of a formal legal search.

---

## 1. Description of the Invention

### 1.1 Overview

This invention is a **chip-scale atomic clock (CSAC)** based on **Coherent Population Trapping (CPT)**
in a microfabricated Rb-87 vapor cell. The complete system consists of:

1. **MEMS vapor cell** — a silicon wafer with a DRIE-etched cylindrical cavity (1.5 mm diameter,
   1.0 mm depth) anodically bonded between two Borofloat 33 glass wafers. The cavity contains
   Rb-87 metal and N2 buffer gas at a specific fill pressure (76.6 Torr at room temperature,
   designed for operation at 85°C).

2. **Integrated thermal oven** — a platinum thin-film serpentine heater (100 Ω, 200 nm thick,
   sputtered on the Si die) and a collocated Pt100 RTD on the same Si substrate, forming an
   on-chip closed-loop thermal oven. The heater and RTD are patterned in the same sputtered Pt
   layer as a single lithographic step.

3. **CPT optical excitation** — a 795 nm VCSEL (Rb-87 D1 line) modulated at 3,417,341,305 Hz
   (half the Rb-87 hyperfine splitting of 6,834,682,611 Hz) with modulation index β = 1.84.
   The first-order sidebands form the two-photon CPT field. A quarter-wave plate provides
   lin-perp-lin or σ+/σ− polarization.

4. **RF frequency synthesizer** — an ADF4351 fractional-N PLL with integer divider N=341,
   fractional numerator F=798, modulus M=1087, and 10 MHz TCXO reference, synthesizing
   3,417,341,306 Hz with < 1 Hz error. The specific N, F, M values were found by an
   exhaustive search over all ADF4351-legal modulus values (M = 2…4095).

5. **Servo electronics** — photodetector monitoring transmitted light through the cell; a lock-in
   demodulated error signal drives the PLL frequency offset DAC to lock to the CPT dark resonance;
   a PID thermal controller maintains cell at 85°C ± 0.01°C.

### 1.2 Operating Principle

When the VCSEL modulation frequency equals exactly half the Rb-87 hyperfine splitting (corrected
for the N2 buffer gas pressure shift of approximately −513 kHz at 76.6 Torr), the Rb atoms are
driven into a dark state (CPT resonance) and transmitted power through the cell increases sharply.
The servo locks the PLL to this dark resonance. The 10 MHz TCXO output, disciplined by the PLL
lock, constitutes the frequency reference output.

### 1.3 Key Numerical Parameters

| Parameter | Value | Source |
|-----------|-------|--------|
| Rb-87 D1 wavelength | 794.978851 nm | NIST ASD |
| Rb-87 hyperfine splitting | 6,834,682,611 Hz | NIST |
| CPT modulation frequency | 3,417,341,305 Hz (= hyperfine/2) | Derived |
| N2 fill pressure (room temp) | 76.6 Torr | 02_buffer_gas |
| N2 pressure shift | −6.7 kHz/Torr → −513 kHz at 76.6 Torr | Vanier & Audoin |
| Cavity diameter | 1.5 mm | 03_mems_geometry |
| Cavity depth | 1.0 mm | 03_mems_geometry |
| Cell operating temperature | 85°C | 04_thermal |
| Heater resistance | 100 Ω (Pt thin film) | 04_thermal |
| RTD resistance @ 85°C | 132.8 Ω | 04_thermal |
| RTD sensitivity | 0.381 Ω/°C | 04_thermal |
| PLL: N, F, M | 341, 798, 1087 | 06_rf_synthesis |
| PLL frequency error | 0.896 Hz | 06_rf_synthesis |
| VCSEL modulation index β | 1.84 | 01_vcsel_sideband |
| RF drive at VCSEL | ~1.0 mW (0 dBm) | 01_vcsel_sideband |

---

## 2. Key Novel Aspects — Technical Summary for Patent Counsel

The following four aspects are candidates for novelty. Each is described technically to allow
the attorney to structure a prior art search and evaluate claim viability.

### 2.1 Specific N2 Pressure for Given Cavity Geometry (Analytical Dicke Narrowing Model)

**What it is:** A closed-form analytical method for determining the optimal N2 buffer gas pressure
that minimizes CPT linewidth for a given cavity diameter, without requiring FEM simulation.

**Technical detail:** The method minimizes the total CPT linewidth as a function of N2 pressure P:

```
γ_total(P) = γ_Dicke(P) + γ_pressure(P) + γ_ground

where:
  γ_Dicke(P)    = γ_transit² / (γ_transit + k_broad × P)     [Dicke narrowing term]
  γ_pressure(P) = k_broad × P                                 [pressure broadening]
  γ_transit     = 1 / (π × d / v_thermal)                     [transit-time linewidth]
  k_broad       = 10.8 kHz/Torr                               (Rb-N2, Vanier & Audoin)
  d             = cavity diameter
```

The minimum is found analytically by setting dγ_total/dP = 0. For d = 1.5 mm at 85°C,
the result is P_opt = 76.6 Torr.

**Why it may be novel:** Prior art describes Dicke narrowing qualitatively and experiments at
various pressures, but the explicit closed-form minimization applied to a specific (1.5 mm, 1.0 mm)
cavity geometry with the exact pressure result of 76.6 Torr for production specification purposes
may not have been published or claimed.

**Distinguishing from prior art:** Perez et al. (2014) optimize buffer gas mixtures (Ne+N2, Ar+N2)
for minimum temperature coefficient, not for minimum CPT linewidth in the Dicke narrowing regime.
Knappe et al. use empirical pressure optimization, not the analytical model.

### 2.2 Integrated On-Chip Pt Heater + Pt100 RTD on Same Si Die as Vapor Cell

**What it is:** Co-fabrication of the CPT vapor cell cavity, the Pt serpentine heater (100 Ω),
and the Pt100 RTD as a single sputtered thin-film lithographic step on the same Si substrate,
forming a monolithic thermal oven.

**Technical detail:**
- Single 200 nm Pt / 20 nm Ti stack deposited by sputtering
- Heater trace: 50 µm wide, 9.4 mm total length serpentine → 100 Ω
- RTD trace: standard Pt100 geometry, four-wire (Kelvin) contact pads on same die
- Both patterned in one lithographic mask layer
- Enables < 0.01°C temperature stability with on-chip measurement and MOSFET-driven PID control

**Why it may be novel:** The specific combination of (a) co-patterning heater and RTD from a single
sputtered Pt layer on the Si MEMS die with (b) the Si/glass vapor cell cavity, in a single process
flow, with (c) four-wire Pt100 RTD geometry achieving 0.381 Ω/°C sensitivity sufficient for
± 0.01°C control, may constitute a novel integrated oven architecture.

**Distinguishing from prior art:** NIST CSAC cells (Knappe 2004, Lutwak 2004) use off-chip
resistance heaters or ITO heaters on the glass window. The Microchip SA65 uses a separate
ceramic heater substrate bonded to the cell. On-chip co-integration of heater and RTD from
a single Pt layer with Pt100 accuracy is believed to be distinct from these approaches.

### 2.3 ADF4351 Fractional-N PLL Frequency Search Algorithm for CPT Excitation

**What it is:** A method for selecting the optimal fractional-N PLL register values (N, F, M)
that minimizes frequency error from a target CPT excitation frequency (HYPERFINE/2), given
integer constraints on N, F, M inherent to the ADF4351 architecture.

**Technical detail:** The algorithm exhaustively searches all valid modulus values M ∈ [2, 4095]
(the ADF4351 architectural constraint), computes F = round(frac_part × M) for each M, and
evaluates the resulting frequency error |f_actual − f_target|. The global minimum is selected.
For the Rb-87 CPT case (f_target = 3,417,341,305.452 Hz, f_ref = 10 MHz):

```
f_target / f_ref = 341.73413054...
N = 341
Best M found: 1087  (F = 798)
Frequency error: 0.896 Hz  (below 1 Hz threshold)
```

The 1 Hz threshold is set by the requirement that initial lock acquisition can occur without
prior knowledge of the buffer gas pressure shift.

**Why it may be novel:** The application of this specific search algorithm to the CPT excitation
problem — including the derivation of the 1 Hz error tolerance from the CPT linewidth and servo
pull-in range — as a systematic method for PLL chip selection and configuration in chip-scale
atomic clocks may constitute a novel method claim.

**Distinguishing from prior art:** General fractional-N PLL synthesizer patents (Analog Devices,
Silicon Laboratories, Fractus/Qualcomm) cover the PLL circuit itself, not the application-specific
search methodology for atomic clock use. CSL/NIST CSAC designs use custom ASICs, not commercial
fractional-N PLL chips.

### 2.4 Analytical (Non-FEM) Thermal Model for MEMS Oven Design

**What it is:** A closed-form first-principles thermal model that predicts steady-state heater
power and startup behavior for the MEMS cell oven, using only lumped-element heat balance
(conduction through substrate + natural convection + radiation), enabling oven design without
requiring finite-element simulation.

**Technical detail:** The model uses:
```
P_heater = h × A_surface × ΔT + k_eff × A_cross × ΔT / L + ε × σ × A × (T_hot⁴ − T_amb⁴)
```
with convection coefficient h = 10 W/m²K for natural convection around a 2 mm die,
yielding a < 80 mW heater power estimate that guided Pt trace geometry sizing before
FEM validation. The model is parameterized by cavity surface area and ambient temperature range
(−40°C to +85°C). Combined with the Callendar-Van Dusen RTD model (R₀ = 100 Ω, A = 3.9083×10⁻³ °C⁻¹,
B = −5.775×10⁻⁷ °C⁻²) it gives a complete oven specification without FEM.

**Why it may be novel:** The specific parameterization of this thermal model for a Si/glass MEMS
vapor cell geometry, including the derivation of Pt trace geometry constraints (length, width,
thickness) from resistance and power requirements in a single design procedure, may have not been
formally claimed as a method for CSAC oven design.

---

## 3. Key Prior Art to Distinguish

Attorney should obtain and review the following references in full. This list is not exhaustive.

### 3.1 Knappe et al., APL 85, 1460 (2004) — "A microfabricated atomic clock"
- **What it discloses:** First MEMS Rb CPT atomic clock with Si/Pyrex anodically bonded vapor
  cell, VCSEL excitation, off-chip heater resistor. Cell geometry ~1×1×2 mm. CPT linewidth ~10 kHz.
- **Distinguishing our work:** No integrated on-chip Pt heater/RTD. No analytical buffer gas
  optimization. No fractional-N PLL; used off-the-shelf signal generator. No production-specification
  N2 pressure derivation.
- **Assignee:** NIST (US Government). Patents likely available for license or may be expired.

### 3.2 Lutwak et al., PTTI Proceedings (2004) — NIST/Symmetricom CSAC
- **What it discloses:** Full CSAC system architecture including MEMS cell, integrated physics
  package, ASIC control electronics. Foundation for what became the Microchip SA65.
- **Distinguishing our work:** Uses ASIC control electronics (proprietary), not ADF4351-based
  fractional-N PLL. Heater is a separate ceramic element, not co-patterned Pt on Si die.
  Buffer gas pressure not analytically derived in published work.
- **Assignee:** Symmetricom / Microchip Technology. **Active patents almost certain — search required.**

### 3.3 Microchip SA65 / Microsemi CSAC Patent Portfolio
- **What to search:** Microchip Technology and predecessor Symmetricom/Microsemi hold patents
  on MEMS vapor cell geometry, CPT physics package integration, and thermal control for CSAC.
  Key patents may include US7,852,163 (Lutwak et al., "Miniature atomic clock"), US7,468,637,
  and related continuation/CIP family.
- **Attorney action:** Full portfolio search required. Determine whether on-chip co-integrated
  Pt heater + RTD is claimed. Determine whether specific buffer gas pressure optimization
  methodology is claimed.
- **Note:** Many Symmetricom CSAC patents filed ~2004–2012 will be expiring or expired by 2026.
  Confirm expiry dates.

### 3.4 Perez et al., Sensors 14, 5571 (2014) — "High-contrast coherent population trapping resonances..."
- **What it discloses:** Systematic study of buffer gas composition (N2, Ne, Ar mixtures) and
  pressure effects on CPT resonance contrast and temperature coefficient. Identifies optimal
  gas pressures empirically for minimum temperature coefficient in various cell sizes.
- **Distinguishing our work:** Perez focuses on temperature coefficient minimization and gas
  mixture optimization. Does not disclose the Dicke narrowing analytical model for pressure
  selection, the specific 76.6 Torr result for 1.5 mm geometry, or integrated Pt heater/RTD.
  Publication (not patent), so relevant as 102(a) prior art under AIA.

### 3.5 Additional Prior Art to Search (attorney to identify)
- Beverini et al. (2004–2010) — Italian CSAC development, buffer gas cells
- Stanford / Lam group — MEMS atomic clock publications ~2006–2015
- DARPA CSAC program patents (BAA 04-18 participants: Symmetricom, Draper, Stanford, NIST)
- European Patent Office (EPO): Syrlinks, iXblue, Orolia — European CSAC patents
- Pendulum Instruments / Spectratime CSAC patents (now part of Orolia/SAFRAN)
- Texas Instruments / Freescale — MEMS heater integration patents (may have relevant thermal claims)

---

## 4. Claims to Consider

The following are draft claim directions for attorney review. These are engineering characterizations,
not formal patent claims.

### Claim 1 — Method: Optimal Buffer Gas Pressure Determination

A method for determining the nitrogen buffer gas fill pressure for a microfabricated alkali-metal
vapor cell in a chip-scale atomic clock, the method comprising:

(a) computing the transit-time CPT linewidth for a cavity of specified diameter d and temperature T;

(b) computing the Dicke-narrowed linewidth as a function of N2 pressure P using the quadratic
    relationship γ_Dicke = γ_transit² / (γ_transit + k_broad × P);

(c) computing total CPT linewidth as the sum of Dicke-narrowed, pressure-broadened, and residual
    ground-state decoherence terms;

(d) selecting the N2 fill pressure that minimizes said total linewidth;

(e) wherein the method produces a fill pressure specification for use in a wafer-level vapor cell
    sealing process.

**Possible embodiment:** For cavity diameter 1.5 mm at 85°C, the method yields 76.6 Torr.

### Claim 2 — Apparatus: Integrated Pt Heater and RTD on MEMS Vapor Cell Die

A microfabricated vapor cell assembly comprising:

(a) a silicon substrate defining a cylindrical cavity;

(b) alkali-metal vapor and buffer gas sealed within said cavity;

(c) a first platinum thin-film trace patterned on the silicon substrate in a serpentine geometry,
    forming a resistive heater;

(d) a second platinum thin-film trace patterned on the same silicon substrate in a Pt100-compliant
    geometry, forming a resistance temperature detector;

(e) wherein the first and second platinum traces are fabricated from the same sputtered Pt layer
    in a single lithographic patterning step;

(f) and wherein the resistance temperature detector is connected in a four-wire Kelvin configuration
    enabling temperature measurement with resolution of ≤ 0.01°C.

**Possible embodiment:** Heater 100 Ω, RTD 100 Ω at 0°C (132.8 Ω at 85°C), Ti adhesion layer,
200 nm Pt, on Si die with Borofloat 33 anodically bonded windows.

### Claim 3 — Method: Fractional-N PLL Register Search for CPT Frequency Synthesis

A method for configuring a fractional-N phase-locked loop for coherent population trapping
excitation in an alkali-metal chip-scale atomic clock, the method comprising:

(a) receiving as input a target CPT excitation frequency f_target = f_hyperfine / 2 for a
    specified alkali isotope;

(b) for each valid modulus value M in the range [M_min, M_max] defined by the PLL chip architecture:
    (i) computing the fractional numerator F = round((f_target/f_ref − N) × M);
    (ii) computing the resulting synthesized frequency and its error Δf = |f_synthesized − f_target|;

(c) selecting the modulus M and numerator F that minimize Δf;

(d) storing the selected N, F, M values as PLL configuration registers;

(e) wherein the method produces a frequency error below a threshold determined by the servo
    loop pull-in range of the atomic resonance.

**Possible embodiment:** For Rb-87 CPT with ADF4351 (M ∈ [2, 4095]), f_ref = 10 MHz:
N=341, F=798, M=1087, error = 0.896 Hz.

---

## 5. Attorney Action Items

| # | Action | Priority |
|---|--------|----------|
| 1 | Full text search of USPTO and EPO for Symmetricom/Microchip CSAC patent portfolio; identify expiry dates and live claims covering vapor cell geometry, thermal control, and buffer gas composition | **High — blocker** |
| 2 | Search for "integrated heater RTD vapor cell" and "Pt thin film MEMS atomic clock" to identify any claims covering the co-patterned Pt heater + RTD architecture | High |
| 3 | Search for "buffer gas pressure optimization CPT" and "Dicke narrowing chip-scale clock" claims | High |
| 4 | Search for "fractional-N PLL atomic clock" and "ADF4351 atomic clock" — note ADF4351 is a commodity part; the claims here are on the search method, not the chip | Medium |
| 5 | Determine whether DARPA CSAC program produced government-owned patents with march-in rights or license requirements | Medium |
| 6 | Assess patentability of Claims 1–3 in view of prior art found; recommend which to pursue | Medium |
| 7 | Confirm whether Knappe 2004 (NIST, APL 85, 1460) resulted in issued patents assigned to NIST, and whether US government license applies | Low |
| 8 | Review expiry dates on Microchip/Symmetricom patents filed 2004–2012 (20-year term); many will expire 2024–2032 | Low |

---

## 6. Technical Background for Attorney Reference

### Coherent Population Trapping (CPT)
A quantum interference effect in a 3-level Λ system (two ground hyperfine states + excited state)
in which atoms driven by two coherent optical fields at frequency difference equal to the hyperfine
splitting are trapped in a dark superposition state, producing a sharp increase in transmitted light
(EIT/CPT resonance). The resonance frequency is the primary frequency reference in a CPT CSAC.

### MEMS Vapor Cell
A silicon microchip with a hermetically sealed cavity containing alkali metal vapor (Rb or Cs)
and buffer gas (N2, Ar, or mixtures), fabricated using semiconductor microfabrication processes
(DRIE etching, anodic bonding). The buffer gas reduces transit-time linewidth via Dicke narrowing
and enables sub-5 kHz CPT linewidths in mm-scale cells.

### Rb-87 Hyperfine Splitting
The clock transition in Rb-87 is between the |F=1⟩ and |F=2⟩ ground hyperfine states, with
frequency 6,834,682,610.904 Hz (NIST ASD). The CPT modulation frequency is exactly half this
value: 3,417,341,305.452 Hz. Buffer gas shifts this resonance by approximately −6.7 kHz/Torr
of N2, which must be compensated by tuning the PLL output.

### Why ADF4351?
The ADF4351 (Analog Devices) is the only broadly available fractional-N synthesizer that spans
DC to 4.4 GHz with a SPI-programmable modulus and published register architecture, enabling
the software search algorithm in Claim 3. Alternative chips (e.g., HMC830, MAX2871) have
different modulus ranges; the algorithm is applicable to any fractional-N PLL with documented
integer constraints.

---

*End of FTO Technical Brief*
*Version 1.0 | 2026-03-29 | CSAC MEMS Engineering Team*
*This document is confidential and prepared in anticipation of attorney-client engagement.*
