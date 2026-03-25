# KLayout + gdstk Setup

Used for: design/mask_layout — generating and verifying the GDS-II chip layout.

---

## The Two Tools and Why Both

| Tool | Role | When used |
|---|---|---|
| gdstk (Python) | GENERATE the GDS-II file from simulation dimensions | After all sims complete |
| KLayout | VIEW, verify, and DRC-check the GDS-II file | Before sending to foundry |

gdstk creates the file programmatically from your simulation results.
KLayout is the industry-standard viewer that foundries use to inspect your layout.

---

## Tool 1: gdstk

Python library. Installed via pip (already in requirements/01_python.md).

```
pip install gdstk
```

### What gdstk does

Takes simulation output numbers (cavity diameter, heater trace width, etc.)
and generates a `.gds` file — the actual chip layout in the industry-standard format.

```python
import gdstk

lib = gdstk.Library()
cell = gdstk.Cell("CSAC_CELL")

# Cavity — dimensions from 03_mems_geometry/results.md
cavity = gdstk.ellipse((0, 0), radius=0.75)      # 1.5mm diameter cavity
cell.add(cavity)

# Heater trace — geometry from 04_thermal/results.md
heater = gdstk.FlexPath([(-0.6, 0.3), (0.6, 0.3), (0.6, -0.3), (-0.6, -0.3)],
                         width=0.05, layer=2)
cell.add(heater)

lib.add(cell)
lib.write_gds("csac_cell_v1.gds")
```

---

## Tool 2: KLayout

Free, open-source. Industry standard for GDS-II layout editing and verification.

### Install on Windows

1. Download from: https://www.klayout.de/build.html
   - Get: `klayout-0.29.x-win64-install.exe` (latest stable)

2. Run installer, default settings

3. Open any .gds file: `klayout csac_cell_v1.gds`

### What you do in KLayout

After gdstk generates the .gds file:
1. Open in KLayout
2. Visual check: does the layout look correct?
3. Check layer assignments
4. Measure dimensions (ruler tool): do they match simulation outputs?
5. Design Rule Check (DRC): run foundry DRC rules if available
6. Export screenshots for documentation

---

## Mask Layout Layers (used in csac_cell_v1.py)

| Layer | Name | What it represents |
|---|---|---|
| 1 | CAVITY | DRIE etch boundary — the main vapor cell cavity |
| 2 | PT_HEATER | Platinum heater trace |
| 3 | PT_RTD | Platinum RTD (temperature sensor) meander |
| 4 | BOND_RING | Anodic bonding frame — must be continuous |
| 5 | DICING | Dicing lane boundary |
| 6 | OPTICAL_WIN | Optical window (where VCSEL beam passes through) |

---

## GDS-II File → Foundry

When the layout is complete and KLayout check passes:

1. Zip the .gds file
2. Write an accompanying process traveler (design/process_traveler.md)
3. Email both to foundry contact

Foundries that accept this format directly:
- MEMSCAP: info@memscap.com
- EPFL CMi: cmi@epfl.ch
- CMC Microsystems: mems@cmc.ca
