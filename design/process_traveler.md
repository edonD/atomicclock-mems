# MEMS CSAC Process Traveler — Version 1.0 — 2026-03-29

**Project:** Chip-Scale Atomic Clock (CSAC) — MEMS Rb-87 CPT Cell
**Revision:** 1.0 — Phase 1 simulation complete, Phase 2 layout in progress
**Destination:** Foundry traveler + MEMS fabrication partner

> Send this document with the GDS-II mask file set (see `design/mask_layout/`).
> All dimensions are derived from Phase 1 simulation results unless noted.

---

## Wafer Stack

| Layer | Material | Thickness | Role |
|---|---|---|---|
| Bottom window | Borofloat 33 glass (AF 32 or equivalent) | **0.3 mm** | Optical transmission window (bottom) |
| MEMS substrate | Si (100), p-type, > 1 kΩ·cm resistivity | **0.5 mm** | Structural substrate, Pt heater / RTD surface |
| Top window | Borofloat 33 glass (AF 32 or equivalent) | **0.3 mm** | Optical transmission window (top) |
| **Total stack** | — | **1.1 mm** | — |

**Wafer format:** 4″ diameter recommended (100 mm), single-side polished Si, double-side polished glass.
**Die layout:** 3.0 mm × 3.0 mm die, 200 µm dicing lanes → ~700 dies per 4″ wafer (estimated).

---

## Step 1: DRIE Etch — Si Cavity

**Purpose:** Etch the cylindrical Rb vapor cell cavity through the Si wafer.

| Parameter | Value | Tolerance |
|---|---|---|
| Etch tool | Deep Reactive Ion Etcher (Bosch process) | — |
| Cavity shape | Cylindrical | — |
| Cavity diameter | **1.5 mm** | ±5% (±75 µm) |
| Cavity depth | **1.0 mm** (through 0.5 mm Si, into sacrificial floor etch-stop) | ±5% (±50 µm) |
| Etch profile | **Through-etch** — cavity opens fully through Si wafer | — |
| Sidewall angle | < 2° from vertical (Bosch scallop < 0.5 µm peak-to-valley) | — |
| Etch rate | 3–5 µm/min (adjust recipe to hit target depth) | — |
| Mask material | SiO₂ (1 µm PECVD) or photoresist hard baked | — |
| Etch chemistry | SF₆ / C₄F₈ alternating (Bosch ICP) | — |

**Inspection criteria:**
- Profilometer depth measurement: 5 points per die (center + quadrant midpoints), all within ±5% of 1.0 mm.
- SEM cross-section on witness die: verify sidewall angle and scallop.
- Visual inspection: no grass, no trenching at etch stop.

**Yield gate:** ≥ 95% of measured points within tolerance before proceeding.

---

## Step 2: Pt Thin Film Deposition — Heater

**Purpose:** Deposit Pt heater serpentine on Si surface for cell temperature control at 85°C.

| Parameter | Value | Notes |
|---|---|---|
| Deposition tool | DC magnetron sputtering | Ion beam also acceptable |
| Adhesion layer | Ti, **20 nm** | Prevents Pt delamination from Si/SiO₂ |
| Pt layer thickness | **200 nm** | Target sheet resistance ~0.5 Ω/sq |
| Heater trace width | **50 µm** | Lithography / wet-etch defined |
| Heater trace length | **6.289 mm** | Serpentine pattern wrapping cell perimeter |
| Heater trace pattern | Serpentine on Si surface adjacent to cavity | See mask layer HEAT |
| Target heater resistance | **100 Ω** at room temperature | Verify with 4-wire probe |
| Target heater resistance @ 85°C | ~120 Ω (estimated TCR correction) | — |
| Heater voltage (design point) | 2.72 V DC (for 73.8 mW into 100 Ω) | From 04_thermal |
| Deposition temperature | ≤ 300°C substrate temp | Prevent interdiffusion |

**Inspection criteria:**
- 4-point probe sheet resistance on witness coupon: within ±10% of 0.50 Ω/sq.
- Adhesion tape test (ASTM D3359) on witness coupon: ≥ 4B rating.
- Step height profilometer: Ti+Pt stack = 220 ±20 nm.

---

## Step 3: Pt RTD — Resistance Temperature Detector

**Purpose:** Deposit and pattern a separate Pt meander RTD for precision temperature sensing of the cell.

| Parameter | Value | Notes |
|---|---|---|
| Deposition | Same Pt run as Step 2 (co-deposited) | Pattern separately with Step 4 lithography |
| RTD trace thickness | **200 nm Pt / 20 nm Ti** | Same stack as heater |
| RTD trace width | **20 µm** | Finer than heater for better resistance matching |
| RTD pattern | Meander adjacent to cell cavity | See mask layer RTD |
| Target resistance @ 0°C | **100 Ω** | Platinum α₀ = 3.851×10⁻³ /°C (IEC 60751 Class B) |
| Resistance @ 85°C | **132.80 Ω** | From 04_thermal: RTD sensitivity 0.381 Ω/°C |
| RTD sensitivity | **0.381 Ω/°C** | Over 25–85°C operating range |
| RTD thermal noise | **1.35×10⁻⁵ °C rms** | 04_thermal — sufficient for 4.2×10⁻⁵ °C stability |
| Measurement current | ≤ 100 µA | Keep self-heating < 0.01°C |
| Calibration | 2-point cal at 25°C and 85°C (in oven) | After dicing, per die |

**Inspection criteria:**
- 4-wire resistance measurement: within ±5 Ω of 100 Ω at 25°C after pattern etch.
- Trace continuity check: no open circuits or shorts between heater and RTD layers.
- Optical inspection: no line-width deviation > ±2 µm on RTD meander (CD-SEM if available).

---

## Step 4: Photolithography — Pattern Pt (Heater + RTD)

**Purpose:** Pattern the co-deposited Pt/Ti stack into heater serpentine and RTD meander geometries.

| Parameter | Value |
|---|---|
| Resist | AZ5214E (image reversal) or AZ1512 |
| Exposure | I-line (365 nm), contact or 1× projection |
| Develop | AZ 726 MIF or equivalent |
| Etch (Pt) | Aqua regia wet etch (3:1 HCl:HNO₃ at 60°C), or Ar⁺ ion mill |
| Etch (Ti) | 1% HF:H₂O after Pt removal |
| Critical dimension | 20 µm (RTD trace) — 50 µm (heater) |
| Layer alignment | RTD layer aligned to heater layer within ±5 µm |

**Note:** Both heater and RTD can be patterned in a single lithography step using a two-feature mask layer if the trace pitches permit (verify with mask DRC).

**Inspection criteria:**
- Optical microscope CD measurement: heater 50 ±3 µm, RTD 20 ±2 µm.
- Resistance spot-check (5 dies per wafer): within ±10% of target values.

---

## Step 5: Rb Fill — Alkali Metal Dispense

**Purpose:** Deposit a controlled quantity of Rb-87 metal into each cell cavity before final sealing.

**Environment: N₂ glove box, O₂ < 1 ppm, H₂O < 1 ppm.  This step is CRITICAL — Rb oxidizes in seconds in air.**

| Parameter | Value | Notes |
|---|---|---|
| Rb isotope | **Rb-87** (natural abundance or enriched) | Natural Rb is 27.8% Rb-87; enriched preferred |
| Rb quantity per cell | ~50–100 ng | Micropipette dispense from SAES Rb dispenser, or Rb-87 ampule |
| Dispense method option A | **SAES Rb getter/dispenser** (model RB/NF/7/25 FT10+10) | Thermally activated — preferred for production |
| Dispense method option B | Rb-87 glass ampule, break in glove box, micropipette aliquot | Lab / prototype use |
| Cell state at fill | Bottom glass bonded (Step 6 already done), Si cavity open | Fill into open cavity |
| Visual inspection | Rb appears as **shiny silver droplet** — reject if grey or white (oxide) | — |
| Time limit | Top glass bonding must begin within **30 minutes** of Rb dispense | Minimize surface oxidation |
| Wafer temperature | Room temperature (20–25°C) during fill | Keep Rb solid |

**Inspection criteria:**
- Visual check under microscope (0.5× to 2× magnification): metallic sheen, no oxide.
- No Rb contamination outside cavity (check under UV lamp — Rb fluoresces faintly).
- Glove box atmosphere: verify O₂ < 1 ppm immediately before and after fill step.

---

## Step 6: N₂ Buffer Gas Fill — Pressure-Controlled Backfill

**Purpose:** Backfill cavities with N₂ to the precise pressure required to minimize clock frequency sensitivity to temperature while maintaining CPT linewidth.

**Environment: must be performed inside glove box or N₂ loadlock attached to bonding tool.**

| Parameter | Value | Tolerance | Source |
|---|---|---|---|
| Fill gas | **N₂, ≥ 99.9999% (6N purity)** | — | 02_buffer_gas |
| Fill pressure | **76.6 Torr (76.58 Torr nominal)** | **±2 Torr (±2.6%)** | 02_buffer_gas |
| Pressure measurement | Capacitance manometer (MKS Baratron) in fill chamber | ±0.1 Torr accuracy | — |
| Pressure shift absorbed | −513.1 kHz from N₂ at 76.6 Torr (offset into PLL) | — | 02_buffer_gas |
| Temperature during fill | 25°C (room temp) — specify pressure at 25°C | Correct for 85°C op. temp if needed | — |
| Seal method | **Anodic bonding** (see Step 7) within 10 minutes of pressurization | — | — |

**Pressure sensitivity:** From 02_buffer_gas, the clock frequency shifts −6.7 kHz/Torr with N₂. A ±2 Torr tolerance → ±13.4 kHz frequency error, well within PLL capture range of ±1.6 MHz.

**Inspection criteria:**
- Pressure gauge log: record fill pressure to 0.1 Torr resolution for every wafer lot.
- Reject any wafer where fill pressure deviates > ±2 Torr from 76.6 Torr target.

---

## Step 7: Anodic Bond — Si to Borofloat 33 (Top Glass Seal)

**Purpose:** Permanently seal the Rb-filled cavity with the top Borofloat 33 glass window using anodic bonding. This is the hermetic seal step — failure here means the die is lost.

**This step seals the Rb and N₂ permanently. Perform inside glove box or N₂ loadlock.**

| Parameter | Value | Notes |
|---|---|---|
| Bond tool | Suss SB6/8, EVG 501, or equivalent | Must have N₂ loadlock |
| Bond temperature | **350°C** | Si and Borofloat 33 CTE compatible |
| Bond voltage | **800 V DC** (range 500–1000 V) | Si positive, glass negative |
| Bond duration | **15 min** at temperature and voltage | Ramp up voltage slowly: 0 → 800 V in 2 min |
| Atmosphere | **N₂ (process gas), no O₂ or H₂O** | O₂ ≤ 10 ppm in bond chamber |
| Bond ring width | **≥ 0.5 mm** (target 0.8 mm) | Simulated bond stress 2.59 MPa (safety factor 3.86×) |
| Glass type | **Borofloat 33 (SCHOTT)** or equivalent alkali-containing glass | Required for anodic bonding |
| Bond stress (FEM) | **2.59 MPa** | < 10 MPa tensile strength → 3.86× margin |
| Bottom glass bond | Identical parameters, performed **before** Rb fill (wafer is Si + bottom glass at Step 5) | — |

**Bottom glass bond (pre-Rb fill):**
- Bond bottom Borofloat 33 to Si **before** Steps 5–6 (Rb fill).
- Same parameters: 350°C, 800 V, 15 min, N₂ atmosphere.
- He leak test before proceeding to Rb fill: < 1×10⁻¹⁰ atm·cc/s.

**Top glass bond (post-Rb fill, hermetic seal):**
- Wafer loaded into glove box / loadlock immediately after N₂ backfill (Step 6).
- Temperature gradient preferred: heat from **bottom** to keep Rb in cavity body, not windows.
- Post-bond visual: **no Rb visible on glass windows** — reject immediately if Rb migrates to window.

**Inspection criteria:**
- He leak test (bonded wafer): < 1×10⁻¹⁰ atm·cc/s per IPC standard.
- Bond ring continuity: IR transmission imaging of bond interface — no unbonded voids > 0.2 mm.
- Window cleanliness: no Rb condensation on optical path (window center ±0.5 mm from axis).
- Yield gate: ≥ 80% die yield on He leak test before dicing.

---

## Step 8: Dicing

**Purpose:** Singulate the wafer into individual 3×3 mm dies.

| Parameter | Value | Notes |
|---|---|---|
| Tool | Dicing saw (blade) or laser dicing | Blade preferred for cleaner glass edge |
| Die size | **3.0 mm × 3.0 mm** | From 03_mems_geometry (die area 9.0 mm²) |
| Dicing lane width | **200 µm** | Allows 170 µm blade kerf + 30 µm alignment margin |
| Blade kerf | 170–200 µm | Diamond blade, silicon / glass compatible |
| Cutting medium | **Deionized water only — NO chemical additives** | Protect Rb in cells |
| Water purity | ≥ 18 MΩ·cm resistivity | Prevent ionic contamination of Pt traces |
| Feed rate | ≤ 5 mm/s (glass layers) | Prevent chipping |
| Spindle speed | 20 000–25 000 RPM | Adjust for blade spec |
| Post-dice rinse | DI water rinse, N₂ blow-dry | No IPA (may enter cell via capillary if seal is marginal) |

**Inspection criteria:**
- He leak test on each individual die: < 1×10⁻¹⁰ atm·cc/s.
- 4-wire Pt resistance measurement: heater 100 ±10 Ω, RTD 100 ±5 Ω at 25°C.
- Edge chip inspection: glass chipping < 50 µm depth from die edge.
- Window cleanliness: no particles > 10 µm on optical window surface.

---

## Inspection Gates Summary

| Gate | After Step | Test | Pass Criterion | Action on Fail |
|---|---|---|---|---|
| G1 | Step 1 (DRIE) | Profilometer depth (5 pts/die) | 1.0 mm ±5% | Re-etch or scrap die |
| G2 | Step 1 (DRIE) | Sidewall angle (SEM witness die) | < 2° from vertical | Re-optimize Bosch recipe |
| G3 | Step 2 (Pt dep.) | Sheet resistance 4-point probe | 0.5 ±0.05 Ω/sq | Re-deposit |
| G4 | Step 3 (RTD) | 4-wire RTD resistance | 100 ±5 Ω at 25°C | Rework trace length |
| G5 | Step 4 (litho) | CD measurement (optical) | 50 ±3 µm heater, 20 ±2 µm RTD | Re-expose |
| G6 | Bottom bond (pre-Step 5) | He leak test | < 1×10⁻¹⁰ atm·cc/s | Scrap wafer |
| G7 | Step 5 (Rb fill) | Visual inspection of Rb | Metallic silver, no oxide | Repeat fill |
| G8 | Step 6 (N₂ fill) | Pressure log | 76.6 ±2.0 Torr | Re-purge and refill |
| G9 | Step 7 (top bond) | He leak test (wafer) | < 1×10⁻¹⁰ atm·cc/s | Scrap affected dies |
| G9 | Step 7 (top bond) | IR bond void imaging | No void > 0.2 mm | Accept/scrap per map |
| G10 | Step 8 (dicing) | He leak test (individual die) | < 1×10⁻¹⁰ atm·cc/s | Scrap die |
| G11 | Step 8 (dicing) | 4-wire Pt resistance | Heater 100 ±10 Ω, RTD 100 ±5 Ω | Scrap die |
| G12 | Step 8 (dicing) | Window cleanliness | No particles > 10 µm in beam path | Clean or scrap |

**Wafer-level yield gate:** Proceed to Rb fill only if G1–G5 yield ≥ 95% of dies.
**Die-level yield gate:** Ship only dies passing G10 + G11 + G12.

---

## Known Yield Limiters and Mitigation

| Risk | Severity | Root Cause | Mitigation |
|---|---|---|---|
| Rb oxidation during fill | **Critical** | O₂/H₂O exposure > 1 ppm | Certify glove box atmosphere before each fill session; use SAES dispensers to minimize open Rb exposure time |
| He leak failure (bond) | **High** | Particle contamination at bond interface | Clean glass surfaces with SC1 + SC2 immediately before bonding; inspect for particles > 0.5 µm |
| N₂ pressure out-of-spec | **High** | Pressure gauge drift or leak in fill chamber | Calibrate Baratron monthly; perform fill chamber leak-up rate test < 0.01 Torr/min before each run |
| Pt trace resistance spread | **Medium** | Sputtering non-uniformity across wafer | Use rotating substrate holder; measure 9-point sheet resistance across wafer, accept if uniformity < ±5% |
| Glass chipping during dicing | **Medium** | Blade wear, excessive feed rate | Change blade every 50 mm cut length; use slow feed (≤ 5 mm/s) through glass layers |
| Rb migration to windows | **Medium** | Excess Rb quantity + top-down heating during bond | Limit Rb to 50–100 ng per cell; heat from bottom during top glass bond step |
| Pt delamination | **Low** | Poor Ti adhesion layer | Verify Ti deposition immediately before Pt in same pump-down; roughen Si surface with 10 s O₂ plasma before deposition |
| DRIE micromasking (grass) | **Low** | Contamination or mask erosion | Clean wafer and chuck with O₂ plasma before DRIE; use fresh photoresist mask |

---

## Reference Dimensions Summary

| Dimension | Value | Module Source |
|---|---|---|
| Cavity diameter | 1.5 mm | 03_mems_geometry |
| Cavity depth | 1.0 mm | 03_mems_geometry |
| Si substrate thickness | 0.5 mm | Design spec |
| Glass thickness (top + bottom) | 0.3 mm each | 03_mems_geometry |
| Die size | 3.0 × 3.0 mm | 03_mems_geometry |
| Dicing lane width | 200 µm | Process design |
| Heater trace width | 50 µm | 04_thermal |
| Heater trace length | 6.289 mm | 04_thermal |
| Heater trace thickness | 200 nm Pt + 20 nm Ti | 04_thermal |
| Heater resistance | 100 Ω | 04_thermal |
| RTD trace width | 20 µm | 04_thermal |
| RTD resistance @ 0°C | 100 Ω | 04_thermal |
| RTD resistance @ 85°C | 132.80 Ω | 04_thermal |
| N₂ fill pressure | 76.6 Torr | 02_buffer_gas |
| Bond ring width | ≥ 0.5 mm | 03_mems_geometry |
| Bond stress (FEM) | 2.59 MPa | 03_mems_geometry |
| Bond safety factor | 3.86× | 03_mems_geometry |

---

*Process Traveler Version 1.0 — generated 2026-03-29 from Phase 1 simulation results.*
*Dimensions subject to Phase 2 layout DRC verification before release to foundry.*
