# Bill of Materials — CSAC MEMS
**Version: 0.0 — Fill RF parameters from Phase 1 results**

---

## MEMS Cell

| Item | Spec | Vendor | Est. Cost |
|---|---|---|---|
| Si wafer (100), >1kΩ·cm, 4" | 1.0–1.5mm thick | Siegert Wafer, UniversityWafer | $50/wafer |
| Borofloat 33 glass wafer, 4" | 0.3mm thick | Schott, Präzisions Glas | $30/wafer |
| Rb-87 metal | 1g ampule | Sigma-Aldrich (276332) | $200/g |
| N2 gas (99.9999% pure) | cylinder | Air Liquide, Linde | $200/cylinder |

---

## Optics (per module)

| Item | Spec | Vendor | Est. Cost |
|---|---|---|---|
| VCSEL 795nm | D1 line Rb-87, SM fiber or free-space | Bandwidth10, Vertilite, RayCan | $300–800 |
| Quarter-wave plate | 795nm, 5mm dia | Thorlabs WPQ05M-780 | $120 |
| Photodetector | Si, 795nm, BW > 1 MHz | Thorlabs PDA36A2 | $500 |
| Optical isolator | 795nm | Thorlabs IO-5-780-VLP | $300 |

---

## RF Electronics (per module)

| Item | Spec | Vendor | Est. Cost |
|---|---|---|---|
| PLL synthesizer | 3.4 GHz, frac-N | ADF4351 (Analog Devices) | $15 |
| VCO | [from 06_rf_synthesis] GHz | Crystek CVCO55CL-XXXX | $30 |
| TCXO 10 MHz reference | ±1 ppm, low phase noise | Epson TXC | $5–20 |
| RF power amp (VCSEL driver) | 3.4 GHz, [from 01_vcsel_sideband] dBm | Mini-Circuits | $10–30 |

---

## Thermal (per module)

| Item | Spec | Vendor | Est. Cost |
|---|---|---|---|
| Pt sputtering target | 99.95% purity | Kurt J. Lesker | $400 |
| Ti sputtering target (adhesion) | 99.99% purity | Kurt J. Lesker | $200 |
| ALD precursor (TMA for Al2O3) | Standard ALD | Sigma-Aldrich | $300 |

---

## Test Equipment (one-time, not per unit)

| Item | Vendor | Est. Cost |
|---|---|---|
| He leak detector | Pfeiffer SmartTest HLT560 | $15k–30k |
| N2 glove box | Inert Technology, MBraun | $15k–30k |
| RF signal generator (3.4 GHz) | Windfreak SynthHD Pro | $500 |
| Lock-in amplifier | Stanford Research SR810 | $3k (used) |
| Temperature controller + SMU | Keithley 2400 | $2k (used) |
| Optical power meter | Thorlabs PM100D | $500 |
