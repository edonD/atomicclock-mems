# 05_optical — Requirements

**WAVE 2 | Tool: Python (ABCD matrices + absorption) | Depends on: 03_mems_geometry**

---

## Questions This Simulation Must Answer

1. Does the VCSEL beam fit through the cavity without clipping at the walls?
2. What is the optical power at the photodetector after passing through the cell?
3. What SNR is achievable at the photodetector? (drives ADEV directly)
4. What window thickness causes acceptable beam divergence and birefringence?
5. What is the required VCSEL beam divergence specification?

---

## Inputs Required

| Parameter | Source |
|---|---|
| Cavity diameter | 03_mems_geometry/results.md |
| Cavity depth | 03_mems_geometry/results.md |
| Glass window thickness | 03_mems_geometry/results.md |
| Rb vapor density at 85°C | 02_buffer_gas/results.md (or calculate internally) |

---

## What to Simulate

ABCD beam propagation:
```
[r']   [A B] [r]
[θ'] = [C D] [θ]

For free space (length L):  M = [[1, L], [0, 1]]
For thin lens (focal f):    M = [[1, 0], [-1/f, 1]]
For glass (n, thickness t): M = [[1, t/n], [0, 1]]
```

Beer-Lambert absorption:
```
I_out = I_in × exp(-α × L)
α = n_Rb × σ_D1
σ_D1 = (λ² / 8π) × (1/τ_sp) × g(ν)  (D1 cross section)
```

Shot noise SNR:
```
SNR = I_pd / sqrt(2e × I_pd × BW)
where I_pd = photodiode current, BW = detection bandwidth
```

---

## Output to Extract into results.md

```
Optical power at detector    : _____ µW
Beam diameter at cell exit   : _____ mm    must be < cavity diameter
SNR at photodetector         : _____       drives ADEV
Required VCSEL divergence    : _____ degrees (half-angle)
Absorption at 85°C           : _____ %     = (1 - exp(-αL)) × 100
Window transmission loss     : _____ %
```
