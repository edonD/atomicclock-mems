# Results

## Status: PASS

## Numbers Extracted

| Parameter                     | Value                              | Spec / Threshold        |
|-------------------------------|-------------------------------------|-------------------------|
| PLL chip                      | ADF4351 (Analog Devices, ~$15)     |                         |
| Reference frequency           | 10 MHz TCXO                        |                         |
| Target frequency              | 3 417 341 305.452 Hz               | HYPERFINE / 2           |
| **PLL N**                     | **341**                            | ADF4351 range 23–65535  |
| **PLL F**                     | **798**                            | 0 ≤ F < M               |
| **PLL M (modulus)**           | **1087**                           | 2–4095                  |
| Actual synthesised freq       | 3 417 341 306.348 Hz               |                         |
| **Frequency error**           | **0.896 Hz**                       | < 1 Hz ✓               |
| Achievable freq step (f/M)    | 9 199.6 Hz                         |                         |
| N₂ pressure shift (02_bg)     | −513.1 kHz                         |                         |
| Tuning range (3× margin)      | 1 539 kHz                          | covers pressure shift ✓ |
| Required tuning voltage       | 154 mV                             | << 1 V ✓               |
| VCO phase noise               | −90 dBc/Hz @ 10 kHz               | ≤ −90 dBc/Hz ✓         |
| **ADEV from VCO (τ=1 s)**     | **9.25 × 10⁻¹⁵**                  | < 1 × 10⁻¹⁰ ✓         |
| Margin vs ADEV target         | 10 807×                            |                         |

## Notes

- Searched all ADF4351 modulus values M = 2 … 4095. Best resolution achieved at
  M = 1087 (F = 798) giving 0.896 Hz error — just below the 1 Hz threshold.
- The 100 MHz reference alternative (N=34, F=377, M=2174) gives an identical
  0.90 Hz error but requires an extra ×10 multiplier; 10 MHz direct is preferred.
- VCO phase noise of −90 dBc/Hz at 10 kHz offset is 10 000× better than needed;
  the CPT servo easily suppresses it inside the 30 Hz bandwidth.
- Full tuning range of ±1.54 MHz is achieved with only ±154 mV on the VCO
  varactor (K_VCO = 10 MHz/V), well within DAC range.

## Evaluator Verdict

PASS — python evaluator.py exits 0
