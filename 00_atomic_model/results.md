# Results: 00_atomic_model

## Status: NOT RUN

## Numbers Extracted

| Parameter | Value | Unit | Notes |
|---|---|---|---|
| hyperfine_hz | — | Hz | must match 6,834,682,610.904 |
| d1_wavelength_nm | — | nm | must match 794.978851156 |
| natural_linewidth_mhz | — | MHz | must match 5.746 |
| cpt_linewidth_khz | — | kHz | target < 5 kHz |
| cpt_contrast_pct | — | % | target > 3% |
| optimal_laser_power_uw | — | µW | |
| discriminator_slope | — | — | |

## Evaluator Verdict
NOT RUN

## Feeds Into
- `design/spec_sheet.md` → performance section
- `01_vcsel_sideband/requirements.md` → hyperfine frequency
- `02_buffer_gas/requirements.md` → CPT linewidth sensitivity
- `06_rf_synthesis/requirements.md` → modulation frequency target
- `07_servo_loop/requirements.md` → discriminator slope
- `08_allan/requirements.md` → linewidth + contrast → ADEV estimate
