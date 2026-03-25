# Mask Layout

GDS-II chip layout for the CSAC vapor cell.

## Status: AWAITING PHASE 1

The mask layout script `csac_cell_v1.py` is ready to run after Phase 1 simulations
complete and all dimensions are filled into `design/spec_sheet.md`.

## How to Generate the GDS-II File

1. Complete all Phase 1 simulations
2. Fill all dimensions into `design/spec_sheet.md`
3. Update the parameters at the top of `csac_cell_v1.py`
4. Run: `python design/mask_layout/csac_cell_v1.py`
5. Output: `csac_cell_v1.gds`
6. Open in KLayout to verify: `klayout csac_cell_v1.gds`
7. Check all dimensions against spec_sheet.md

## Layer Map

| Layer | Name | Color in KLayout | What it is |
|---|---|---|---|
| 1 | CAVITY | Blue | DRIE etch boundary |
| 2 | PT_HEATER | Red | Platinum heater trace |
| 3 | PT_RTD | Orange | Platinum RTD meander |
| 4 | BOND_RING | Green | Anodic bonding frame |
| 5 | DICING | Grey dashed | Dicing lane |
| 6 | OPTICAL_WIN | Yellow | Optical window area |

## Files

- `csac_cell_v1.py` — Python script using gdstk, generates .gds
- `csac_cell_v1.gds` — generated GDS-II file (send this to foundry)
- `layer_map.md` — layer definitions
- `screenshots/` — layout images for documentation and investor deck
