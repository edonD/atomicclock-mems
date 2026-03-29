# Bill of Materials — CSAC MEMS
**Version: 1.0 — Updated from Phase 1 simulation results**
**Date: 2026-03-29**

All values derived from Phase 1 simulation modules (00–06). See individual `results.md` files
for derivations.

---

## 1. MEMS Cell

Fabricated as a Si-glass-Si sandwich stack at a MEMS foundry. The Si wafer is DRIE-etched
to form the vapor cell cavity (1.5 mm diameter × 1.0 mm depth). Two Borofloat 33 glass
wafers are anodically bonded to seal the cavity. Rb-87 and N2 gas are dispensed in a glove
box environment before final bonding.

| # | Item | Specification | Vendor / Part | Proto Cost (1–10 u) | Prod Cost (1k u) | Lead Time |
|---|------|---------------|---------------|---------------------|------------------|-----------|
| 1.1 | Si wafer, (100), FZ | >1 kΩ·cm, 4", 1.0–1.5 mm thick | Siegert Wafer / UniversityWafer | $50/wafer | $25/wafer | 2–4 weeks |
| 1.2 | Borofloat 33 glass wafer, 4" | 0.3 mm thick, anodic-bond grade | Schott / Präzisions Glas & Optik | $30/wafer | $15/wafer | 4–6 weeks |
| 1.3 | Rb-87 metal | ≥97% isotopic purity, 1 g sealed ampule | Sigma-Aldrich cat. 276332 | $200/g | $120/g | 4–8 weeks |
| 1.4 | N2 gas, ultra-high purity | 99.9999% (6N), fill pressure 76.6 Torr at room temp | Air Liquide / Linde | $200/cylinder | $100/cylinder | 1–2 weeks |
| 1.5 | MEMS foundry processing (wafer-level) | DRIE etch (1.5 mm dia, 1.0 mm deep), anodic bond 400°C/800V, dicing | IMT (Buchs), MEMSCAP, or equivalent | $5,000–15,000 NRE + ~$50/die | ~$10/die | **12–20 weeks** |

**Notes on N2 fill pressure:** The 76.6 Torr room-temperature fill pressure (from module 02\_buffer\_gas)
is the analytically derived optimum for a 1.5 mm cavity diameter. At 85°C operating temperature,
this scales to approximately 98 Torr by ideal gas law (P × T_op/T_fill). This achieves Dicke
narrowing limited CPT linewidth below 5 kHz.

**Key long-lead item:** MEMS foundry slot requires 12–20 weeks from design freeze. Submit GDS-II
mask and process traveler at least 4 months before first evaluation date.

---

## 2. Optics

One optical path per unit. VCSEL driven at D1 wavelength; quarter-wave plate converts linear to
circular polarization for CPT σ+/σ− excitation. Photodetector monitors transmitted power.
Optical isolator is optional for bench prototypes but recommended for production to prevent
back-reflection into VCSEL.

| # | Item | Specification | Vendor / Part | Proto Cost (1–10 u) | Prod Cost (1k u) | Lead Time |
|---|------|---------------|---------------|---------------------|------------------|-----------|
| 2.1 | VCSEL, 795 nm | D1 line Rb-87, λ = 795.0 nm (±0.2 nm at 85°C), SM, modulation BW > 5 GHz, threshold < 1 mA | RayCan RC25-795, Bandwidth10, or Vertilite | $300–800 | $50–100 (qty contract) | **8–16 weeks** |
| 2.2 | Quarter-wave plate | 795 nm, zero-order, 5 mm dia, AR-coated | Thorlabs WPQ05M-780 | $120 | $40 | 1–2 weeks |
| 2.3 | Photodetector, Si PIN | 795 nm, bandwidth > 1 MHz (−3 dB), responsivity > 0.5 A/W, active area ≥ 0.5 mm² | Thorlabs FDS1010 or Hamamatsu S5971 | $30–60 | $5–10 | 2–4 weeks |
| 2.4 | Optical isolator (optional) | 795 nm, isolation > 35 dB, aperture ≥ 1 mm | Thorlabs IO-5-780-VLP | $300 | $80 (custom pkg) | 2–4 weeks |
| 2.5 | VCSEL collimation lens | f = 4.5 mm, NA 0.55, AR @ 795 nm | Thorlabs A110TM-B | $50 | $10 | 1–2 weeks |

**VCSEL operational parameters (from 01\_vcsel\_sideband):**
- Operating wavelength: 795 nm (D1 line)
- Optical output power at operating point: ~50 µW at cell face
- Modulation frequency: 3,417,341,305 Hz (≈3.417 GHz, half-hyperfine)
- Modulation index: β = 1.84 (optimizes first-order sideband power)
- RF drive level required at VCSEL: ~1.0 mW (+0 dBm)
- Expected photocurrent: 85 µA at 169 µW incident power (after cell absorption)

**VCSEL is the longest-lead optics item** and has the tightest wavelength tolerance.
Order early; negotiate wafer-level screening for λ and modulation bandwidth.

---

## 3. RF Electronics

The RF synthesizer generates the 3.417 GHz CPT modulation signal from the 10 MHz TCXO.
The ADF4351 fractional-N PLL was selected in module 06\_rf\_synthesis as the only commercial
chip meeting all constraints: N=341, F=798, M=1087 with f_ref=10 MHz gives a synthesized
frequency error of only 0.896 Hz.

| # | Item | Specification | Vendor / Part | Proto Cost (1–10 u) | Prod Cost (1k u) | Lead Time |
|---|------|---------------|---------------|---------------------|------------------|-----------|
| 3.1 | Fractional-N PLL synthesizer | ADF4351, 35 MHz–4.4 GHz, SPI control, integrated VCO | Analog Devices ADF4351BCPZ | $15 | $6 | 2–4 weeks |
| 3.2 | VCO (external loop filter / reference board) | 3.4–3.5 GHz, phase noise ≤ −90 dBc/Hz @ 10 kHz, K_VCO ≈ 10 MHz/V | Crystek CVCO55CL-3400-3500 or ADF4351 internal VCO | $30 | $8 | 2–4 weeks |
| 3.3 | TCXO, 10 MHz | ±0.5 ppm, phase noise < −130 dBc/Hz @ 1 kHz offset, 3.3 V supply | Epson TG2520SMN or TXCO2016A | $5–20 | $2–5 | 2–4 weeks |
| 3.4 | RF amplifier / VCSEL modulation driver | 3.4 GHz, gain ≥ 10 dB, P_out > +3 dBm, NF < 4 dB | Mini-Circuits PGA-103+ or RFMD RF2878 | $5–15 | $2–4 | 1–2 weeks |
| 3.5 | RF bandpass filter, 3.4 GHz | BPF, center 3.417 GHz, BW 200 MHz, IL < 2 dB | TDK / Murata ceramic BPF | $3–8 | $0.50 | 2–3 weeks |
| 3.6 | ADF4351 loop filter passives | R1–R3, C1–C4 per ADIsimPLL design | Standard 0402 SMT | $1 | $0.10 | 1 week |
| 3.7 | RF power attenuator, 0–10 dB | SMA/microstrip, 3.4 GHz, set drive level to VCSEL | Mini-Circuits VAT series | $5 | $1 | 1 week |

**PLL synthesis result (from 06\_rf\_synthesis):**
- N = 341, F = 798, M = 1087, f_ref = 10 MHz
- Synthesized: 3,417,341,306.35 Hz (error = 0.896 Hz from target)
- N2 pressure shift compensation: ±1.54 MHz tuning range with ±154 mV DAC → adequate
- VCO phase noise: −90 dBc/Hz @ 10 kHz → ADEV contribution 9.25×10⁻¹⁵ at τ=1s (negligible)

**TCXO phase noise requirement:** The 10 MHz reference must have phase noise
< −130 dBc/Hz @ 1 kHz to avoid the reference spurs upconverting to the 3.417 GHz output
at a level that would degrade clock ADEV. Standard TCXO parts from Epson/Vectron meet this.

---

## 4. Thermal Control

The Pt serpentine heater and Pt100 RTD are fabricated on-chip as sputtered thin-film traces
(200 nm Pt on 20 nm Ti adhesion layer) during MEMS processing. The off-chip electronics
consist of a MOSFET heater driver, an RTD bridge amplifier, and the MCU running the PID loop.

### 4a. On-chip (fabricated at MEMS foundry, included in cell cost line 1.5)

| # | Item | Specification | Notes |
|---|------|---------------|-------|
| 4a.1 | Pt sputtering target | 99.95% purity, 4" dia | Kurt J. Lesker EJTPTXX403A2 |
| 4a.2 | Ti sputtering target (adhesion) | 99.99% purity | Kurt J. Lesker EJTTITXX403A2 |
| 4a.3 | Heater trace geometry | 100 Ω nominal, serpentine, 9.4 mm total length, 50 µm wide, 200 nm thick | Derived from thermal module 04 |
| 4a.4 | RTD trace geometry | Pt100 (100 Ω at 0°C), 132.8 Ω at 85°C, 4-wire Kelvin contact | 0.381 Ω/°C sensitivity at 85°C |

**Heater parameters (from 04\_thermal):**
- Heater resistance: 100 Ω (Pt thin film)
- Maximum heater power: 74 mW (worst case: ambient −40°C)
- Supply voltage for heater driver: 3.0 V (derived: V = √(P×R) = √(74mW×100Ω) = 2.72 V → 3.0 V rail)
- Max heater current: 55 mA → low-side N-channel MOSFET gate driver required

**RTD parameters:**
- R₀ = 100 Ω (Pt100 standard)
- R at 85°C = 132.8 Ω (Callendar-Van Dusen, A = 3.9083×10⁻³ °C⁻¹)
- Sensitivity: 0.381 Ω/°C at 85°C
- Required resolution for ΔT = 0.01°C: ΔR = 3.81 mΩ → 4-wire measurement mandatory
- Excitation current: 1 mA (limits self-heating to P = I²R = 0.133 mW < 0.1 mW target; use 0.5 mA if self-heating is problematic)

### 4b. Off-chip electronics

| # | Item | Specification | Vendor / Part | Proto Cost (1–10 u) | Prod Cost (1k u) | Lead Time |
|---|------|---------------|---------------|---------------------|------------------|-----------|
| 4b.1 | Heater driver MOSFET (low-side N-ch) | V_DS > 5 V, I_D > 100 mA, R_DS(on) < 500 mΩ, SOT-23 | Vishay SI2302 or IRLML2502 | $0.50 | $0.08 | 1 week |
| 4b.2 | Gate drive resistor | 10–100 Ω, 0402 | Standard SMT | $0.05 | $0.01 | stock |
| 4b.3 | RTD excitation current source | 1 mA precision, < 10 ppm/°C drift | Texas Instruments REF200 or op-amp + R | $3 | $0.50 | 1–2 weeks |
| 4b.4 | Instrumentation amplifier (RTD bridge) | Gain 100–1000, CMRR > 100 dB, input noise < 10 nV/√Hz | AD8221 (Analog Devices) or INA128 | $5 | $1 | 1–2 weeks |
| 4b.5 | MCU | ARM Cortex-M0+/M4, SPI (ADF4351), 12-bit ADC (RTD + photodetector), PWM (heater), < 5 mW, QFN-32 | STM32L412 or STM32G0 | $3–8 | $1.50 | 2–4 weeks |
| 4b.6 | 12-bit ADC (optional external, if MCU ADC insufficient) | SAR ADC, 12–16 bit, SPI, < 1 mW | AD7685 (Analog Devices) | $5 | $1 | 2 weeks |
| 4b.7 | 3.3 V LDO regulator | I_out > 200 mA, noise < 10 µV_rms, SOT-223 | TPS7A3301 or ADP151 | $1 | $0.20 | 1 week |
| 4b.8 | Decoupling capacitors, 100 nF / 10 µF | 0402 / 0805, X5R/X7R | Standard SMT | $0.20 | $0.02 | stock |

---

## 5. PCB and Packaging

The prototype uses a 4-layer FR4 PCB with the MEMS cell and optics mounted on the top surface.
Production packaging would integrate into a ceramic LCC or metal-lid module, but that is a
Phase 3 activity. Estimated prototype PCB size: 25 mm × 25 mm.

| # | Item | Specification | Vendor / Part | Proto Cost (1–10 u) | Prod Cost (1k u) | Lead Time |
|---|------|---------------|---------------|---------------------|------------------|-----------|
| 5.1 | PCB, 4-layer FR4 | 25×25 mm, 4-layer, 50 Ω CPW on outer layers for RF traces, ENIG finish | OSH Park / PCBWay | $10–30 | $3–8 | 1–2 weeks |
| 5.2 | SMA connectors (RF in/out) | Edge-launch, SMA-F, 50 Ω, usable to 6 GHz | Samtec / Amphenol | $3 | $0.50 | 1 week |
| 5.3 | Passive SMT components (R, C, L) | 0402/0603 package, standard values | Yageo / Vishay / Murata | $5–10 | $1 | stock |
| 5.4 | Prototype enclosure / shielding can | Cu or tin-plated steel RF shield, snap-on, PCB footprint | Würth Elektronik WE-SHC | $2–5 | $0.30 | 1–2 weeks |
| 5.5 | PCB assembly (SMT, prototype) | Stencil paste + reflow, hand-placed MEMS cell | In-house or small-batch CM | $50–200 | — | 1–2 weeks |
| 5.6 | Thermal isolation spacers | Macor or PEEK standoffs, 2 mm, low thermal conductivity | McMaster-Carr | $5 | $0.50 | 1 week |

---

## 6. Cost Summary

### 6a. Prototype (1–10 units) — Approximate Total per Unit

| Category | Estimated Cost |
|----------|---------------|
| MEMS cell (materials + foundry NRE amortized over 10 units) | $600–1,600 |
| Optics (VCSEL + QWP + PD + lens) | $500–1,000 |
| RF electronics (PLL, VCO, TCXO, amp, filter) | $60–100 |
| Thermal electronics (MOSFET, InAmp, MCU, passives) | $20–30 |
| PCB and packaging | $100–250 |
| **Total per prototype unit** | **~$1,300–3,000** |

NRE dominates at prototype scale. The foundry process development and mask set
($5k–15k one-time) must be amortized. Budget $10k–20k for first functional prototype run.

### 6b. Production (1,000 units) — Approximate Total per Unit

| Category | Estimated Cost |
|----------|---------------|
| MEMS cell (wafer-level, fully amortized NRE) | $15–25 |
| Optics (volume pricing, VCSEL negotiated) | $60–120 |
| RF electronics | $15–25 |
| Thermal electronics | $5–8 |
| PCB and packaging (custom ceramic module) | $10–20 |
| Assembly and test | $15–30 |
| **Total per production unit** | **~$120–230** |

Comparable commercial CSACs (Microchip SA65) retail for $1,500–3,500 at low volume.
At 1k units and ~$200 COGS, a 5–10× margin is achievable at a $1,000–2,000 selling price.

---

## 7. Long-Lead Item Summary

| Item | Lead Time | Action Required |
|------|-----------|-----------------|
| MEMS foundry slot (cell fab) | **12–20 weeks** | Submit GDS-II + process traveler at design freeze; contact IMT/MEMSCAP immediately |
| VCSEL, 795 nm | **8–16 weeks** | Source from RayCan or Bandwidth10; request datasheet screening for λ and mod BW |
| Rb-87 metal (Sigma-Aldrich) | **4–8 weeks** | Export license may be required depending on jurisdiction; verify with supplier |
| Borofloat glass wafers | **4–6 weeks** | Order with foundry submission |
| ADF4351 PLL (possible allocation risk) | 2–4 weeks normally, up to 12 weeks if allocation | Check distributor stock (Mouser/Digi-Key); order immediately |

**Critical path:** MEMS foundry → VCSEL → integration and test.
Estimated time from design freeze to first functional prototype: **6–9 months**.

---

## 8. Test Equipment (One-Time, Not per Unit)

| Item | Purpose | Vendor / Part | Est. Cost |
|------|---------|---------------|-----------|
| He leak detector | MEMS cell hermeticity check | Pfeiffer SmartTest HLT560 | $15k–30k |
| N2 glove box | Rb/N2 dispense environment | Inert Technology / MBraun | $15k–30k |
| RF signal generator, to 4.4 GHz | PLL characterization, RF chain debug | Windfreak SynthHD Pro | $500 |
| Lock-in amplifier | CPT error signal demodulation, servo characterization | Stanford Research SR810 | $3k (used) |
| SMU / temperature controller | RTD calibration, heater characterization | Keithley 2400 | $2k (used) |
| Optical power meter | VCSEL output, cell transmission | Thorlabs PM100D + S120C | $600 |
| Spectrum analyzer, to 4.4 GHz | Phase noise, spurious check | Rigol DSA815 (or used HP E4404B) | $1.5k–5k |
| Oscilloscope, 500 MHz | Servo loop, digital debug | Rigol DS1054Z or similar | $400 |
| Frequency counter, 10-digit | ADEV measurement | Keysight 53230A or Pendulum CNT-90 | $5k–10k |

**Total one-time test equipment budget (approximate):** $40k–80k.
Many items are available used at 30–50% of list price on eBay/Surplus.

---

*Document version 1.0. Update with actual quotes and delivery confirmations before purchase order release.*
*All prices in USD, approximate, 2026. Verify current pricing with distributors.*
