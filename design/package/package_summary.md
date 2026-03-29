# CSAC-1 Package Design Summary

## Package Specification

| Parameter | Value |
|-----------|-------|
| Package type | LCC-20 (Leadless Chip Carrier, 20 pads) |
| Body dimensions | 7.0 mm × 7.0 mm × 4.35 mm (H) |
| Die cavity | 3.5 mm × 3.5 mm × 1.1 mm deep |
| Pad pitch | 1.2 mm |
| Pad size | 0.8 mm × 0.6 mm (W × D) |
| Pads per side | 5 (4 sides) |
| Die size | 3.0 mm × 3.0 mm × 0.5 mm |
| Cavity window | Ø 1.5 mm borosilicate glass |
| Cavity atmosphere | Ar/N₂ (inert, <1 ppm O₂/H₂O) |
| Hermetic seal | Metal lid, seam-weld or solder-seal |
| Thermal resistance junction-to-case | θ_jc ≈ 15 °C/W |
| Thermal resistance junction-to-ambient | θ_ja ≈ 45 °C/W |
| Operating temperature | −40 °C to +85 °C |
| Storage temperature | −55 °C to +125 °C |
| Package material | 96% Al₂O₃ multilayer ceramic |
| Lid material | Kovar (Fe-Ni-Co), gold-plated |
| Marking | `CSAC-1 / YYXX` (YY = year, XX = lot) |

---

## Pin Assignment (LCC-20, CCW from Pin 1)

| Pin | Signal | Description |
|-----|--------|-------------|
| 1   | NC     | No connect (left side, pin 1 marker) |
| 2   | NC     | No connect |
| 3   | NC     | No connect |
| 4   | NC     | No connect |
| 5   | NC     | No connect |
| 6   | VCC    | +3.3 V supply |
| 7   | GND    | Ground |
| 8   | HTR+   | Heater positive drive |
| 9   | HTR−   | Heater negative / return |
| 10  | RTD+   | RTD sense positive |
| 11  | RTD−   | RTD sense negative |
| 12  | CLK    | SPI clock input |
| 13  | DATA   | SPI data (MOSI/MISO) |
| 14  | NC     | No connect |
| 15  | NC     | No connect |
| 16  | NC     | No connect |
| 17  | NC     | No connect |
| 18  | NC     | No connect |
| 19  | NC     | No connect |
| 20  | NC     | No connect |

> **Note:** NC pads should be left floating on the PCB (do not connect to GND plane —
> prevents thermal shorts from affecting heater control accuracy).

---

## Layer Stack (bottom to top)

| Layer | Material | Thickness |
|-------|----------|-----------|
| PCB substrate | FR-4 or AlN (preferred for thermal) | 1.50 mm |
| Solder paste | SAC305 (Sn-Ag-Cu lead-free) | 0.15 mm |
| LCC ceramic body | Al₂O₃ multilayer | 1.50 mm |
| Die attach epoxy | Low-outgassing Ag-filled epoxy (≤50 ppm TML) | 0.10 mm |
| Si die | CSAC physics/ASIC die | 0.50 mm |
| Cavity atmosphere | Ar/N₂ fill | 0.60 mm |
| Glass window | Borosilicate, AR-coated (795 nm) | 0.30 mm |
| Metal lid | Kovar hermetic seal lid | 0.30 mm |
| **Total** | | **4.35 mm** |

---

## Key Assembly Notes

### Die Attach
- Use **low-outgassing silver-filled epoxy** (e.g., Loctite Ablestik 8175 or equivalent).
- TML (Total Mass Loss) spec: **≤ 50 ppm** at 125 °C / 24 h per ASTM E595.
- CVCM (Collected Volatile Condensable Material): **≤ 10 ppm**.
- Cure: 150 °C / 60 min in N₂ atmosphere (prevent oxidation of Ag filler).
- Die attach fillet: ≤ 50 µm climb on die sidewall.

### Cavity Seal / Lid Atmosphere
- Purge cavity with **Ar/N₂ (99.999%)** immediately before seam-welding.
- Residual O₂: **< 100 ppm**; H₂O: **< 50 ppm** (dew point ≤ −60 °C).
- Perform lid seal in glove-box or vacuum chamber with controlled backfill.
- Seal integrity: fine-leak test per MIL-STD-883 Method 1014 (He leak rate < 5×10⁻⁹ atm·cc/s).

### Reflow Profile (PCB Assembly)
| Phase | Temperature | Duration |
|-------|-------------|----------|
| Preheat | 25 → 150 °C | 60–90 s |
| Soak | 150–180 °C | 60–120 s |
| Reflow peak | 245–260 °C | ≤ 30 s above 217 °C |
| Cool-down | 260 → 25 °C | ≥ 2 °C/s |
- Max package body temperature: **260 °C** (do not exceed — glass window AR coating risk).
- Use **no-clean flux** (halide-free); aqueous wash not recommended (hermetic risk).

### Handling
- ESD class: HBM 2000 V (Class 2).
- Moisture sensitivity: MSL-1 (unlimited floor life at ≤ 30 °C/85% RH) — hermetic package.
- Storage: dry-pack not required; recommend sealed bag with desiccant for long-term (>12 mo).

### PCB Footprint Recommendation
- Land pattern: IPC-7351 LCC20 (7.0 × 7.0 mm body), pad 0.8 × 0.6 mm, pitch 1.2 mm.
- Courtyard: 9.0 × 9.0 mm minimum.
- Thermal relief: **avoid** on HTR± and RTD± pads — use solid fill for accurate RTD readings.

---

## Marking

Top-side laser mark (white):

```
CSAC-1
YYXX
```

- `YY` = 2-digit year (e.g., `26` for 2026)
- `XX` = 2-digit lot code (00–99)

Pin 1 indicator: bevelled corner + silkscreen dot on PCB.
