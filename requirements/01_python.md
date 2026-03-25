# Python Environment Setup

## 1. Python Version

Requires Python 3.11 or 3.12.

Check your version:
```
python --version
```

If below 3.11, download from https://python.org/downloads

---

## 2. Create a Virtual Environment

```
cd C:\Users\DD\OneDrive\Programming\willAI\atomicclock-mems
python -m venv .venv
.venv\Scripts\activate
```

You should see `(.venv)` in your terminal prompt.

---

## 3. Install All Required Packages

```
pip install numpy scipy matplotlib qutip python-control allantools gdstk
```

### Package Breakdown

| Package | Version | Purpose | Used in |
|---|---|---|---|
| numpy | ≥1.26 | Array math, constants | all modules |
| scipy | ≥1.12 | Bessel functions, ODE solver, optimization | 01, 02, 05, 06, 07 |
| matplotlib | ≥3.8 | Plotting all simulation outputs | all modules |
| qutip | ≥5.0 | Quantum density matrix, Lindblad solver | 00_atomic_model |
| python-control | ≥0.9 | Bode plots, phase/gain margins, Nyquist | 07_servo_loop |
| allantools | ≥2019.9 | Allan deviation, ADEV, MDEV | 08_allan |
| gdstk | ≥0.9 | Generate GDS-II mask layout files | design/mask_layout |

---

## 4. Verify Installation

```python
# Run this in Python to verify
import numpy;       print(f"numpy      {numpy.__version__}       OK")
import scipy;       print(f"scipy      {scipy.__version__}       OK")
import matplotlib;  print(f"matplotlib {matplotlib.__version__}  OK")
import qutip;       print(f"qutip      {qutip.__version__}       OK")
import control;     print(f"control    {control.__version__}     OK")
import allantools;  print(f"allantools OK")
import gdstk;       print(f"gdstk      {gdstk.__version__}       OK")
```

---

## 5. QuTiP Note

QuTiP 5.x changed its API significantly from QuTiP 4.x. All simulations in
`00_atomic_model` are written for QuTiP 5. Do not install QuTiP 4.

If pip installs QuTiP 4 by default, force version 5:
```
pip install "qutip>=5.0"
```

---

## 6. Optional: Jupyter for Interactive Exploration

```
pip install jupyter
jupyter notebook
```

Useful for exploring simulation parameters interactively before committing
to final sim.py code.
