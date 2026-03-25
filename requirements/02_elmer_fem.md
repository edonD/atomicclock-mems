# Elmer FEM + FreeCAD Setup

Used for: 03_mems_geometry (structural stress) and 04_thermal (heat distribution).
These are the two modules where Python alone is not sufficient.

---

## Why FEM is Required Here

Python can solve equations. FEM solves geometry.

When you heat a glass-Si-glass sandwich from 20°C to 85°C, the stress at the
bond interface depends on the exact 3D geometry — cavity shape, wall thickness,
corner radii. You cannot get this from an equation. You need FEM.

If you skip FEM and guess cavity dimensions, you risk:
- Bond cracking during thermal cycling (-40 to +85°C)
- Hot spots causing Rb condensation on windows
- Mechanical resonances in the vibration band

FEM is what makes the mask layout dimensions credible to a foundry.

---

## Tool 1: Elmer FEM

Free, open-source finite element solver. Handles structural mechanics + thermal.
Developed by CSC Finland. Used in academic MEMS research.

### Install on Windows

1. Download installer from: https://www.elmerfem.org/blog/binaries/
   - Get: `ElmerFEM-gui-mpi-Windows-AMD64.exe` (latest release)

2. Run installer, default settings, install to `C:\ElmerFEM`

3. Add to PATH:
   ```
   C:\ElmerFEM\bin
   ```
   (Control Panel → System → Advanced → Environment Variables → PATH)

4. Verify:
   ```
   elmersolver --version
   ElmerGrid --version
   ```

### What Elmer Does in This Project

| Module | Elmer analysis type | What you get |
|---|---|---|
| 03_mems_geometry | Linear elasticity (structural) | Stress map, safety factor at bond interface |
| 04_thermal | Heat equation (thermal) | Temperature distribution, hot spots, thermal resistance |

---

## Tool 2: FreeCAD

Free 3D CAD tool. Used to draw the MEMS cell geometry before exporting to Elmer.

### Install on Windows

1. Download from: https://www.freecad.org/downloads.php
   - Get: `FreeCAD_1.0.0-conda-Windows-x86_64.7z` (or latest stable)

2. Install to `C:\FreeCAD`

3. No PATH setup needed — you use the GUI

### What FreeCAD Does in This Project

You draw the glass-Si-glass stack in FreeCAD:
- Si wafer with DRIE-etched cavity
- Bottom and top glass wafers
- Pt heater traces (as thin rectangles)

Then export the mesh to Elmer using FreeCAD's FEM workbench.

---

## Workflow: FreeCAD → Elmer

```
1. Draw geometry in FreeCAD (FEM workbench)
2. Define materials (Si, Borofloat 33 glass, Pt)
3. Apply boundary conditions (fixed base, temperature loads)
4. Export mesh as .unv file
5. Convert: ElmerGrid -format unv -out mesh/ input.unv
6. Write Elmer .sif file (provided in each module folder)
7. Run: elmersolver sim.sif
8. View results in ParaView or ElmerPost
```

---

## Tool 3: ParaView (for viewing FEM results)

Free scientific visualization tool. Needed to view Elmer output.

Download: https://www.paraview.org/download/

---

## Material Properties Used in Simulations

These are hardcoded into the Elmer .sif files:

### Silicon (Si)
```
Youngs Modulus = 170e9      ! Pa
Poisson Ratio = 0.28
Density = 2330              ! kg/m^3
Heat Conductivity = 148     ! W/m/K
Heat Capacity = 700         ! J/kg/K
CTE = 2.6e-6                ! 1/K (thermal expansion)
```

### Borofloat 33 Glass
```
Youngs Modulus = 63e9       ! Pa
Poisson Ratio = 0.20
Density = 2230              ! kg/m^3
Heat Conductivity = 1.2     ! W/m/K
Heat Capacity = 830         ! J/kg/K
CTE = 3.25e-6               ! 1/K
```

### Platinum (Pt heater traces)
```
Youngs Modulus = 168e9      ! Pa
Poisson Ratio = 0.38
Density = 21450             ! kg/m^3
Heat Conductivity = 71.6    ! W/m/K
Electrical Conductivity = 9.43e6  ! S/m
TCR = 3850e-6               ! 1/K (resistance temperature coefficient)
```

---

## Verify Elmer Install

```
elmersolver --version
```
Should print version number. If not found, check PATH.
