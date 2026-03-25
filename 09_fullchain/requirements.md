# 09_fullchain — Requirements

**WAVE 4 | Tool: Python | Depends on: ALL modules**

---

## Questions This Simulation Must Answer

1. When all modules are connected together, does the system still meet ADEV < 5×10⁻¹⁰?
2. Are there unexpected interactions between modules that degrade performance?
3. Does the total power budget stay under 150 mW?
4. What is the end-to-end sensitivity to each parameter? (which is the weakest link?)

---

## What to Simulate

Import RESULTS from all 9 modules. Build a unified model:
- Feed CPT linewidth (00) + N2 pressure (02) + optical SNR (05) into ADEV formula
- Add thermal noise contribution (04) to ADEV
- Add VCO phase noise contribution (06) to ADEV
- Apply servo loop filter (07) to combined noise
- Compute final ADEV vs averaging time τ

Run sensitivity analysis:
- For each input parameter, perturb ±10% and measure ADEV change
- Identify which parameter has the most impact on ADEV
- That parameter is the manufacturing control priority

Power budget:
- Heater: from 04_thermal
- VCSEL: optical power / efficiency
- RF electronics: VCO + PLL
- Digital: PID + ADC
- Total must be < 150 mW

---

## Output to Extract into results.md

```
Final ADEV @ 1s         : _____   must match 08_allan within 20%
Final ADEV @ 1hr        : _____
Total power budget      : _____ mW   must be < 150 mW
Weakest link parameter  : _____   (most sensitive to ±10% perturbation)
System-level SNR        : _____
Go/No-Go for Phase 2    : YES / NO
```

---

## Evaluation Gate

09_fullchain PASS = Phase 1 complete. Proceed to Phase 2 design package.
