# CSAC MEMS — Process Traveler
**Version: 0.0 — Template, fill dimensions from Phase 1 simulation results**

Send this document to foundry together with GDS-II mask file.

---

## Wafer Stack

| Layer | Material | Thickness | Purpose |
|---|---|---|---|
| Bottom | Borofloat 33 glass | [from 03_mems_geometry] mm | Optical window |
| Middle | Si (100), >1kΩ·cm | [from 03_mems_geometry] mm | MEMS substrate |
| Top | Borofloat 33 glass | [from 03_mems_geometry] mm | Optical window |

---

## Step 1: DRIE Etch — Si Cavity

- Tool: Deep Reactive Ion Etcher (Bosch process)
- Target depth: **[from 03_mems_geometry/results.md]** mm ± 5%
- Target diameter: **[from 03_mems_geometry/results.md]** mm ± 2%
- Etch rate: ~3–5 µm/min (adjust to hit target depth)
- Sidewall angle: < 2° from vertical
- Inspection: profilometer after etch, measure 5 points per die

---

## Step 2: Pt Thin Film Deposition

- Tool: DC magnetron sputtering
- Stack: Ti 20nm (adhesion) / Pt 200nm
- Target Pt heater resistance: **[from 04_thermal/results.md]** Ω
- Target Pt RTD resistance @ 25°C: **[from 04_thermal/results.md]** Ω
- Sheet resistance of 200nm Pt: ~0.5 Ω/sq (verify by 4-point probe)

---

## Step 3: Photolithography — Pattern Pt

- Resist: AZ5214 or equivalent
- Develop, expose, etch Pt (aqua regia wet etch or RIE)
- Layer map: see mask_layout/layer_map.md
- Heater trace width: **[from 04_thermal/results.md]** µm
- RTD meander pitch: **[from 04_thermal/results.md]** µm

---

## Step 4: ALD Al2O3 Passivation

- Tool: Atomic Layer Deposition
- Material: Al2O3
- Thickness: 50 nm
- Temperature: 150°C
- Purpose: prevent Rb from attacking Si walls (anti-permeation barrier)
- Note: must coat all cavity interior surfaces including sidewalls

---

## Step 5: Anodic Bond — Bottom Glass to Si

- Tool: Suss SB6/8 or EVG 501 bonder
- Temperature: 350°C
- Voltage: 600V DC
- Duration: 30 min
- Atmosphere: N2 ambient (no O2 or H2O)
- Inspection: He leak test on bonded pair, target < 1×10⁻¹⁰ atm·cc/s
- Yield gate: > 70% good dies before proceeding

---

## Step 6: Rb Fill + N2 Backfill  ⚠ CRITICAL ⚠

- Environment: N2 glove box, O2 < 1 ppm, H2O < 1 ppm
- Rb quantity: ~50 ng per cavity (micropipette dispense)
- N2 backfill pressure: **[from 02_buffer_gas/results.md]** Torr ± 5 Torr
- Time limit: top glass bonding must begin within 30 minutes of Rb fill
- Visual inspection: Rb metal should appear as shiny silver droplet, no grey/white oxide

---

## Step 7: Anodic Bond — Top Glass (in glove box or loadlock)

- Same parameters as Step 5
- Must be done inside glove box or with N2 loadlock on bonder
- Temperature gradient: heat from bottom to keep Rb in cavity body, not windows
- Immediately inspect: no Rb visible on glass windows after bonding

---

## Step 8: Dicing

- Tool: dicing saw (blade) or laser dicing
- Kerf width: 200 µm (blade) or 50 µm (laser)
- Die size: **[from 03_mems_geometry/results.md]** × **[...]** mm
- Cutting medium: deionized water (no chemicals near Rb-filled dies)
- Post-dice: He leak test each individual die

---

## Inspection Gates

| Gate | Test | Pass criterion |
|---|---|---|
| After Step 1 | Profilometer depth measurement | Depth within ±5% of target |
| After Step 2 | 4-point probe sheet resistance | Within ±10% of target |
| After Step 5 | He leak test (bonded pair) | < 1×10⁻¹⁰ atm·cc/s |
| After Step 7 | Visual inspection of windows | No Rb visible on glass |
| After Step 8 | He leak test (individual die) | < 1×10⁻¹⁰ atm·cc/s |
| After Step 8 | Pt trace continuity (4-wire) | Heater and RTD resistance within ±10% |
