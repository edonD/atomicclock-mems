# VCO Design Program — SKY130 6.835 GHz Oscillator

## Objective
Design and validate a voltage-controlled oscillator that oscillates at 6.835 GHz
(Rb-87 hyperfine frequency) using the SKY130 130nm CMOS open-source PDK with
**real transistor models** — not simplified Level 1 placeholders.

## Working Directory
`/home/ubuntu/atomicclock-mems/09_circuit_design`

## Critical Context
- SKY130 transistor fT is ~60 GHz. A 6.835 GHz VCO is near the process limit.
- The existing `vco_sky130.sp` uses fake Level 1 MOSFET models — it has NEVER been validated with real SKY130 models.
- If 6.835 GHz is not achievable, design a **prescaler architecture**: VCO at a lower harmonic + frequency multiplier, or VCO at 6.835 GHz with relaxed specs.
- This is the single most critical design risk in the entire CSAC project.

## SKY130 PDK Locations

```
PDK_ROOT = /home/ubuntu/.volare/volare/sky130/versions/6d4d11780c40b20ee63cc98e645307a9bf2b2ab8/sky130A

RF NFET models (L=0.15um, best fT):
  libs.ref/sky130_fd_pr/spice/sky130_fd_pr__rf_nfet_01v8_aM04W5p00L0p15.spice
  libs.ref/sky130_fd_pr/spice/sky130_fd_pr__rf_nfet_01v8_lvt_aM04W5p00L0p15.spice
  (LVT variants have higher fT — prefer these)

Varactor models:
  libs.ref/sky130_fd_pr/spice/sky130_fd_pr__cap_var_lvt.model.spice
  libs.ref/sky130_fd_pr/spice/sky130_fd_pr__cap_var_hvt.model.spice

Inductor models:
  libs.ref/sky130_fd_pr/spice/sky130_fd_pr__ind_05_125.model.spice  (1.25 nH)
  libs.ref/sky130_fd_pr/spice/sky130_fd_pr__ind_05_220.model.spice  (2.20 nH)
  libs.ref/sky130_fd_pr/spice/sky130_fd_pr__ind_03_90.model.spice   (0.90 nH)

Test coil SPICE:
  libs.ref/sky130_fd_pr/spice/sky130_fd_pr__rf_test_coil1.spice
  libs.ref/sky130_fd_pr/spice/sky130_fd_pr__rf_test_coil2.spice
  libs.ref/sky130_fd_pr/spice/sky130_fd_pr__rf_test_coil3.spice

Corner models:
  libs.ref/sky130_fd_pr/spice/sky130_fd_pr__nfet_01v8__tt_leak.corner.spice
```

## Tool
- **ngspice 42** at `/usr/bin/ngspice`
- Run in batch mode: `ngspice -b -o output.log script.sp`
- Use `.control ... .endc` blocks for automation
- Save waveforms with `wrdata` for post-processing with Python + matplotlib

---

## Task List

### Phase 1: Understand SKY130 RF Transistor Capabilities
- [x] Read the RF NFET SPICE model files to understand subcircuit pin order and parameters
- [x] Read the inductor model files to understand available L values and Q factors
- [x] Read the varactor model files to understand C(V) tuning range
- [x] Create `vco_design/01_fT_characterization.sp`:
  - Instantiate `sky130_fd_pr__rf_nfet_01v8_lvt` (LVT, best speed) at L=0.15u, W=5u
  - DC sweep and AC analysis to extract fT vs Vgs, gm, Cgs, Cgd
  - Calculate max oscillation frequency fmax = fT / (2 * sqrt(Rg * gds / gm))
  - Run with ngspice, save results
- [x] Create `vco_design/01_fT_results.py` — parse ngspice output and plot fT vs Vgs
- [x] **Decision gate**: If fT < 20 GHz at operating point, 6.835 GHz VCO is infeasible → go to Phase 6 (prescaler fallback)

### Phase 2: Inductor Characterization
- [x] Create `vco_design/02_inductor_char.sp`:
  - Include each SKY130 inductor model (ind_03_90, ind_05_125, ind_05_220)
  - S-parameter / AC analysis to extract L, Q, self-resonance frequency (SRF) at 6.835 GHz
  - For LC tank: need L such that f = 1/(2*pi*sqrt(L*C)) = 6.835 GHz
  - With C_total ~0.5-2 pF, need L ~0.27-1.1 nH
- [x] Run and extract Q factor at 6.835 GHz for each inductor
- [x] Select best inductor (highest Q at target frequency, below SRF)
- [x] If no PDK inductor works at 6.835 GHz (SRF too low), design a custom spiral model

### Phase 3: Varactor Characterization
- [x] Create `vco_design/03_varactor_char.sp`:
  - Include `sky130_fd_pr__cap_var_lvt` model
  - DC sweep Vtune 0.0V to 1.8V
  - Extract C(V) curve, Cmin, Cmax, tuning ratio
  - Calculate achievable tuning range at 6.835 GHz: Δf = f0 * (1 - sqrt(Cmin/Cmax)) / 2
- [x] Run and plot C(V) curve
- [x] Verify tuning range covers ±500 MHz (or at minimum ±100 MHz for servo lock)

### Phase 4: VCO Design with Real Models
- [x] Create `vco_design/04_vco_real.sp` — the main VCO circuit:
  - Use real `sky130_fd_pr__rf_nfet_01v8_lvt` for cross-coupled pair
  - Use real `sky130_fd_pr__cap_var_lvt` for varactors
  - Use real `sky130_fd_pr__ind_*` for tank inductor (or custom model from Phase 2)
  - Properly biased: Vdd=1.8V, tail current source using current mirror
  - Calculate required negative resistance: -Gm > 1/Rtank for startup
  - Size transistors: W/L for sufficient gm while minimizing Cgs parasitic
  - Include output buffer (source follower or common-source)
- [x] **Transient simulation**: 20 ns with 0.1 ps timestep
  - Verify oscillation starts
  - Measure steady-state frequency (FFT or zero-crossing)
  - Measure amplitude
  - Measure startup time
- [x] **Frequency tuning**: sweep Vtune 0.4V to 1.4V in DC steps
  - Run transient at each Vtune, measure frequency
  - Plot f(Vtune) curve — must pass through 6.835 GHz
  - Calculate Kvco (MHz/V)
- [x] **Power measurement**: measure total supply current * Vdd
  - Must be < 30 mW (budget from spec)
- [x] Save all simulation results and waveforms

### Phase 5: VCO Validation and Optimization
- [x] **Phase noise estimation** (Leeson's equation):
  - L(Δf) = 10*log10[(2*F*k*T/Psig) * (f0/(2*Q*Δf))^2 * (1 + Δf_1/f3/Δf)]
  - Use measured Q from inductor, oscillation amplitude, noise figure
  - Target: < -80 dBc/Hz at 1 MHz offset (relaxed from original -90 dBc/Hz)
- [x] **Corner simulations**: run at SS, TT, FF corners
  - VCO must oscillate across all corners
  - Frequency shift must stay within tuning range
- [x] **Temperature sweep**: -40°C to 85°C
  - Check frequency drift vs temperature
- [x] **Monte Carlo** (if time permits): 20 runs with mismatch
  - Check frequency spread, startup reliability
- [x] Create `vco_design/05_vco_summary.py`:
  - Parse all ngspice outputs
  - Generate comprehensive plot PNG with: oscillation waveform, FFT spectrum,
    f(Vtune) tuning curve, power consumption, phase noise estimate
  - Save as `vco_design/vco_validation_results.png`

### Phase 6: Prescaler Fallback (only if Phase 1 shows fT is insufficient)
- [x] If 6.835 GHz direct oscillation fails, design alternative:
  - **Option A**: VCO at 3.4175 GHz (half frequency) + frequency doubler
  - **Option B**: VCO at 1.709 GHz (quarter frequency) + 4x multiplier
  - **Option C**: Ring oscillator at 6.835 GHz (worse phase noise but simpler)
- [x] Design the chosen architecture and validate with ngspice
- [x] Document the trade-offs vs direct 6.835 GHz

### Phase 7: Documentation and Visualization
- [x] Write `vco_design/README.md` with:
  - Final VCO topology and schematic description
  - All key parameters (frequency, power, phase noise, tuning range)
  - SKY130 component selection rationale
  - Simulation results with plots
  - Known limitations and next steps
- [x] Generate professional VCO schematic PNG showing the circuit with component values
- [x] Update `09_circuit_design/README.md` with VCO validation results

### Phase 8: Commit & Push
- [x] Stage all files under `09_circuit_design/vco_design/` and updated READMEs
- [x] Commit with descriptive message
- [x] Push to remote repository

---

## Key Design Equations

```
Tank frequency:     f0 = 1 / (2*pi*sqrt(L * C_total))
Startup condition:  gm > 2 / Rtank  (negative resistance must exceed loss)
Tank Q:             Q = 2*pi*f0*L / Rseries = Rparallel / (2*pi*f0*L)
Phase noise:        L(Δf) ≈ (2*F*kT/Psig) * (f0/(2*Q*Δf))^2  [Leeson]
Tuning range:       Δf ≈ f0 * (Cmax - Cmin) / (2 * C_total)
Power:              P = Vdd * I_tail + buffer power
fT:                 fT = gm / (2*pi*(Cgs+Cgd))
```

## Design Space

| Parameter | Target | Acceptable Range |
|-----------|--------|-----------------|
| Frequency | 6.835 GHz | 6.335 - 7.335 GHz (±500 MHz tuning) |
| Phase noise @ 1 MHz | -90 dBc/Hz | -80 dBc/Hz minimum |
| Power | < 27 mW | < 35 mW |
| Supply | 1.8 V | 1.62 - 1.98 V (±10%) |
| Tuning range | ±500 MHz | ±100 MHz minimum (servo lock) |
| Startup time | < 100 ns | < 500 ns |
| Output amplitude | > 0.3 Vpp | > 0.2 Vpp |

## Constraints
- Use only components available in the SKY130 PDK — no external/custom models
- All simulations must use real BSIM4/PSP models, NOT Level 1 approximations
- ngspice batch mode (`-b` flag) for unattended execution
- Python matplotlib for all plots (no GUI required)
- If a simulation fails or doesn't converge, adjust parameters and retry (don't skip)
- Document every design decision and trade-off

## Success Criteria
- VCO oscillates at or near 6.835 GHz with real SKY130 models, OR
- A feasible prescaler architecture is designed with clear path to 6.835 GHz
- Professional visualization PNG generated with simulation results
- Everything committed and pushed
