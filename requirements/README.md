# Software Requirements

Install in this order. All tools are free.

---

## Install Order

```
1. Python environment        → 01_python.md        (30 min)
2. Elmer FEM + FreeCAD       → 02_elmer_fem.md      (1-2 hrs)
3. KLayout + gdstk           → 03_klayout_gdstk.md  (30 min)
```

---

## Tool → Module Map

| Tool | Used in | Purpose |
|---|---|---|
| Python 3.11+ | All modules | Simulation language |
| QuTiP | 00_atomic_model | Quantum density matrix solver |
| SciPy / NumPy | 01, 02, 05, 06, 07, 08, 09 | Math, signal processing |
| python-control | 07_servo_loop | Control system analysis (Bode, margins) |
| allantools | 08_allan | Allan deviation computation |
| matplotlib | All | Plotting |
| gdstk | design/mask_layout | GDS-II mask file generation |
| Elmer FEM | 03_mems_geometry, 04_thermal | Structural + thermal FEM |
| FreeCAD | 03_mems_geometry, 04_thermal | 3D geometry for FEM mesh |
| KLayout | design/mask_layout | GDS-II viewer, DRC check |

---

## Verification Test

After installing everything, run:
```
python requirements/verify_install.py
```

Expected output:
```
[OK] Python 3.11+
[OK] numpy
[OK] scipy
[OK] matplotlib
[OK] qutip
[OK] control
[OK] allantools
[OK] gdstk
[OK] Elmer FEM (elmersolver found in PATH)
[OK] KLayout (klayout found in PATH)
```
