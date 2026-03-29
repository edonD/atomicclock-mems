# Neuromorphic & Photonic AI Accelerators: Strategic Entry Plan

**Document Created:** 2026-03-30
**Target Market Entry:** Q2 2026 (NSF SBIR Phase I)
**First Product Timeline:** 2027-2028
**Total Funding Target:** $2-10M over 3 years

---

## EXECUTIVE SUMMARY

You have **unique positioning** to enter the neuromorphic/photonic AI space:

1. **Analog expertise:** MEMS atomic clocks require extreme precision analog circuits, low-noise design, frequency stabilization
2. **Photonics integration:** VCSELs, frequency combs, optical cavity design from CSAC work
3. **Manufacturing:** Anodic bonding, CMOS integration, hermetic packaging at wafer scale
4. **SKY130 experience:** Open-source CMOS+photonics co-design capability

**Unmet market needs you can address:**
- Integrated photonic-analog neuromorphic chips (not just interconnects or pure analog)
- Frequency-stable optical neural network synchronization
- Edge AI chips combining VCSEL photonics + analog compute cores
- Low-cost, open-source design methodology

**Recommended strategy:** Build an **integrated photonic-analog neuromorphic accelerator** leveraging SKY130 photonics + your precision analog expertise. This bridges:
- Your MEMS atomic clock know-how → neuromorphic oscillators & synchronization
- Your VCSEL expertise → on-chip photonic neurons
- Your CMOS integration → analog compute cores
- Your characterization skills → noise/precision benchmarking

---

## PART 1: HOW YOUR MEMS EXPERTISE MAPS TO NEUROMORPHIC AI

### Your Core Competencies → Neuromorphic Applications

| Your Expertise | CSAC Application | Neuromorphic Application | Value Proposition |
|---|---|---|---|
| **Precision oscillators** | VCO locked to Rb-87 CPT | Photonic neural network clock distribution | Frequency-stable synchronization for multi-ns operations |
| **Frequency combs** | Optical atomic clock reference | Dual frequency comb neurons (WDM encoding) | Parallel computation via wavelength division |
| **VCSEL design/integration** | Pump laser in CSAC | Spiking photonic neurons (GHz rate) | Fast, ultra-low-power spiking elements |
| **Analog noise floors** | Photodetector signal processing | Lock-in detection in neural circuits | Sensitivity improvement to femtojoule scale |
| **Anodic bonding** | Hermetic cavity sealing | Integrated photonic package | 3D stacking of photonic + electronic layers |
| **MEMS resonators** | Mechanical frequency reference | Integrated oscillators for neural clocks | On-chip distributed timing in neuromorphic array |
| **PID/servo control** | Frequency lock mechanism | Adaptive learning in spiking networks | Feedback control of neuromorphic dynamics |
| **Precision measurement** | Allan variance, phase noise | Characterizing photonic neural network reliability | System-level noise budgeting |

**Key insight:** Your atomic clock is a **neuromorphic prototype** — it uses feedback, oscillation, and precision analog synchronization. The neuromorphic chip you build will use similar principles at much higher speeds and scales.

---

## PART 2: THE NEUROMORPHIC AI MARKET (2025-2030)

### Market Size & Growth

| Segment | 2025 | 2030 | CAGR | Notes |
|---------|------|------|------|-------|
| **Neuromorphic chips (SNN)** | $89.7M | $7.05B | 87.8% | BrainChip, Intel Loihi dominant |
| **Edge AI accelerators** | $4.44B | $11.54B | 21.0% | Growing due to privacy + latency needs |
| **Photonic AI accelerators** | ~$50M (nascent) | $3B (2034) | Unknown | Optalysys, Lightmatter, academic labs |
| **Analog in-memory compute** | ~$100M (research) | $2B+ (2032) | 50%+ | IBM, EnCharge AI, emerging startups |
| **Total addressable** | $4.5B+ | $15B+ | 25-30% | Compound across categories |

### Why This Matters for You

1. **First-mover advantage:** Photonic-analog hybrid chips are **underexplored** (most teams pursue pure photonic OR pure analog, not both)
2. **Complementary strengths:** Your photonics + their analog computing = differentiation
3. **Funding ready:** DARPA OPTIMA, NSF SBIR, EU Quantum Flagship all active
4. **Commercial path:** Edge AI market desperate for <100 mW inference chips

---

## PART 3: COMPETITIVE GAP ANALYSIS

### What Exists Today (2024-2026)

**Pure Neuromorphic (SNNs):**
- BrainChip Akida 2.0 (commercial, shipping)
- Intel Loihi 3 (Jan 2026, research)
- Advantage: Mature, proven, commercial deployments
- Disadvantage: No photonic elements, limited to digital spiking

**Pure Analog In-Memory:**
- IBM Analog AI (research)
- EnCharge AI EN100 (2025 launch)
- Advantage: Ultra-low power, competitive accuracy
- Disadvantage: Limited scaling (billions of parameters hard), no photonics

**Pure Photonic:**
- Lightmatter Passage (2025, interconnects only)
- Optalysys FT:X (2025+, special-purpose image processing)
- MIT prototype (2024, lab only)
- Advantage: Nanosecond latency, massive bandwidth
- Disadvantage: Nonlinearity hard, scaling immature, cost high

### The Gap You Can Fill

**Missing:** Integrated photonic-analog neuromorphic chip that:
- Uses **VCSEL photonic neurons** for ultrafast spiking
- Integrates **analog MAC cores** for weight computation
- Synchronizes via **frequency-stable on-chip oscillators** (your expertise)
- Designed in **open-source SKY130** (no NDA, academic collaboration)
- Targets **edge AI inference** (realistic first market)
- Power budget: **10-100 mW**
- Cost: **$1-5K** (vs. millions for Lightmatter)

**Why no one else built this yet:**
- Photonic teams lack analog expertise
- Analog teams avoid photonics (integration complexity)
- Most startups chase VC funding (want "photonic" or "neuromorphic" as single narrative)
- Academic teams rarely productionize

**Why you can:**
- You've already integrated CMOS + cavity + photonics (CSAC proof-of-concept)
- You understand precision analog better than photonic startups
- You have manufacturing pipeline ready
- You can leverage open-source tools (SKY130 photonics PDK exists)

---

## PART 4: TECHNICAL APPROACH - YOUR FIRST PRODUCT

### Project: **NeuroPhoton Accelerator v1** (2026-2028)

#### **High-Level Concept**

A **hybrid photonic-analog neuromorphic accelerator** on a single die:

```
┌─────────────────────────────────────────────┐
│        NeuroPhoton Accelerator v1            │
├─────────────────────────────────────────────┤
│                                              │
│  [VCSEL Array] ──┐  Photonic neurons (GHz)  │
│     (4×4 grid)   │  - Fast spiking          │
│                  │  - Event-driven          │
│                  ↓                           │
│  ┌────────────────────────────┐             │
│  │ Integrated Oscillator Bank │ Clock dist. │
│  │  (microring resonators)    │             │
│  └────────────────────────────┘             │
│           ↓                                 │
│  ┌────────────────────────────┐             │
│  │  Analog MAC Array (16×16)  │ Weights    │
│  │  - Switched-capacitor      │ Computation│
│  │  - 8-bit precision         │            │
│  └────────────────────────────┘             │
│           ↓                                 │
│  ┌────────────────────────────┐             │
│  │   Digital Sequencer        │ Control    │
│  │  - Neuron readout          │            │
│  │  - Weight programming      │            │
│  │  - Spike routing           │            │
│  └────────────────────────────┘             │
│           ↓                                 │
│      [Output Driver]                        │
│                                              │
└─────────────────────────────────────────────┘

Die size: ~5×5 mm (comparable to your CSAC)
Process: SKY130 (130 nm CMOS + photonics)
Power: 50-100 mW @ 1 GHz clock
Latency: 100-500 ns per inference
```

#### **Component Breakdown**

**1. VCSEL Photonic Neuron Array (4×4 grid)**

Your expertise applies directly here.

- **16 VCSELs** (780 nm, Rb-87 resonant wavelength—you know this!)
- **Design constraints:**
  - Modulation bandwidth: > 1 GHz (for spiking)
  - Output power: 1-10 mW per neuron
  - Temperature stability: ±0.1 nm (use your thermal management from CSAC)
  - Array spacing: > 50 µm (avoid crosstalk)

- **Why 780 nm?**
  - You already have VCSEL expertise from CSAC pump laser
  - 780 nm silicon photonics waveguides are mature
  - Photodetectors for 780 nm are efficient and low-noise

**2. Integrated Microring Resonator Clock Distribution**

This is where your frequency expertise shines.

- **One master oscillator** (microring laser) @ 1 GHz
- **Clock distribution** via silicon waveguides to all 16 neurons
- **Frequency stability:**
  - Allan deviation: < 10⁻¹¹ @ 1 sec (20× better than quartz)
  - Phase noise: < –80 dBc/Hz @ 100 kHz offset
  - Self-injection locking to high-Q resonator (your technique from CSAC)

**Why critical:** Photonic neural networks lose synchronization without stable clock. Your precision oscillator experience directly addresses this.

**3. Analog MAC (Multiply-Accumulate) Core**

16×16 switched-capacitor array for weight computation.

- **Architecture:** Programmable capacitor network
- **Precision:** 8-bit weights, 8-bit activations (reduces power vs. 16-bit)
- **Power:** < 1 mW per MAC (similar to IBM Analog AI spec)
- **Integration:** Shares substrate with photonic components
- **Your role:** Analog noise budgeting, precision measurement

**4. Digital Sequencer**

Lightweight digital controller (< 1 mm² die area).

- SRAM for weight storage (16×16 @ 8-bit = 2 KB)
- Spike event routing (which neuron fires → address decoder)
- Photodetector output multiplexing
- Temperature/PVT monitoring (you'll have sensors from CSAC experience)

---

#### **Die Layout Concept**

```
┌──────────────────────────────────┐
│   (2.5 mm)                       │ (2.5 mm)
│                                  │
│  ┌──────────────┐                │
│  │  VCSEL Array │ Photonics      │
│  │  (4×4, 0.5mm)│ Layer          │
│  └──────────────┘                │
│       ↓                          │
│  ┌──────────────────────────┐   │
│  │  Microring oscillator    │    │
│  │  + waveguide clock dist  │    │
│  │  (1.0 × 1.5 mm)         │    │
│  └──────────────────────────┘   │
│       ↓                          │
│  ┌──────────────────────────┐   │
│  │  Analog MAC Array        │    │
│  │  16×16 (1.2 × 1.2 mm)   │    │
│  │  + photodetectors        │    │
│  └──────────────────────────┘   │
│       ↓                          │
│  ┌──────────────────────────┐   │
│  │  Digital Sequencer       │    │
│  │  + I/O drivers (0.8 mm²) │    │
│  └──────────────────────────┘   │
│                                  │
└──────────────────────────────────┘

Total: 5×5 mm die (400 µm² per neuron)
Packaging: Wirebond LCC-40 or flip-chip BGA
```

---

#### **Performance Target (MVP)**

| Metric | Target | Comparison |
|--------|--------|------------|
| **Power consumption** | 75 mW @ 1 GHz | 100× less than Jetson Nano |
| **Inference latency** | 200-500 ns | 1000× faster than GPU |
| **Energy/inference** | 50-100 pJ | Competitive with photonic approaches |
| **Model capacity** | ResNet-18 equivalent | ~250K weights (fits in on-chip SRAM) |
| **Accuracy** | 92-95% on MNIST/CIFAR-10 | Competitive with quantized digital |
| **Die size** | 25 mm² | Fits in LCC-40 package |
| **Cost (1K volume)** | ~$2-5K/unit | 100× cheaper than Lightmatter |

---

### Implementation Roadmap (18-month timeline)

#### **Phase 0: Feasibility Study (Q2 2026, 3 months)**
- **Goal:** Validate SKY130 photonics + analog co-design
- **Deliverables:**
  - Microring oscillator simulation + layout (frequency stability model)
  - 4×4 VCSEL array design (thermal, optical, electrical modeling)
  - 16×16 switched-capacitor MAC array design (noise analysis)
  - Preliminary die layout and power budget
- **Funding:** NSF SBIR Phase I ($305K)
- **Team:** 2 analog designers, 1 photonics engineer, 1 ML engineer (part-time)

#### **Phase 1: Design & Simulation (Q3 2026 - Q4 2026, 6 months)**
- **Goal:** Complete design and tape-out ready
- **Deliverables:**
  - Full schematic + layout
  - Parasitic extraction and post-layout simulation
  - Thermal & mechanical FEA (temperature cycling, stress)
  - Test plan and bench characterization methodology
  - Design kit integration with SKY130 PDK
- **Funding:** NSF SBIR Phase II ($1.75M) or DARPA OPTIMA subcontract
- **Team:** 3-4 engineers (full-time IC design, photonics, test)

#### **Phase 2: Tape-Out & Fab (Q1 2027 - Q2 2027, 4-6 months)**
- **Goal:** Silicon in hand, initial characterization
- **Deliverables:**
  - Mask set generation
  - Multi-project wafer (MPW) run through Efabless/GlobalFoundries
  - First silicon parts received & binned
  - Bench testing setup (optical, electrical, thermal)
  - Initial performance metrics
- **Funding:** Government contract or venture funding ($500K-$1M)
- **Partners:** Efabless (MPW run coordination), GlobalFoundries (process support)

#### **Phase 3: Characterization & Demo (Q3 2027 - Q4 2027, 6 months)**
- **Goal:** Prove neuromorphic inference capability
- **Deliverables:**
  - Full electrical characterization (power, speed, noise)
  - Optical alignment and photodetector signal quality
  - Clock distribution jitter measurement
  - Running CNN inference on ResNet-18
  - Comparison benchmarks vs. Akida/Loihi/Jetson
  - Technical paper (IEEE, Nature Electronics, or topical conference)
- **Funding:** None required (use government funding from Phase II)
- **Demos:** DARPA PI meeting, academic conferences

#### **Phase 4: Second-Gen Design (2028, 12 months)**
- **Goal:** Production-ready chip with improved specs
- **Improvements:**
  - Larger array (8×8 neurons = 64 elements)
  - Full-network training (vs. inference-only)
  - Integration with external analog input (sensor fusion)
  - Commercial package (BGA instead of wirebond)
  - Cost reduction (volume manufacturing path)
- **Funding:** DARPA OPTIMA Phase 2 or corporate R&D contract ($2-5M)
- **Target:** First customer trials by end of 2028

---

## PART 5: FUNDING STRATEGY (2026-2028)

### Recommended Funding Path

```
Q2 2026          Q3 2026-Q4 2026       Q1 2027-Q2 2027      Q3 2027-Q4 2027
  ↓                   ↓                      ↓                    ↓

NSF SBIR Phase I   NSF SBIR Phase II      Tape-out via        Product Release
$305K              $1.75M                 Govt Contract        + Licensing
(6 months)         (24 months)            $500K-$1M            ($2-5M/year)
   +                                      + Venture: $1-2M      recurring

Total 2026-2027: ~$2.5M
Total 2028-2030: $5-10M (production, licensing, follow-on products)
```

### Specific Funding Sources

#### **1. NSF SBIR Phase I (Q2 2026 submission, $305K)**

**Program:** Advanced Computing Systems
**Deadline:** June 2026
**Topics matching you:**
- "Ultra-low-power AI accelerators for edge computing"
- "Photonic neural network integration"
- "Neuromorphic computing hardware"

**Your proposal should emphasize:**
- Photonic-analog hybrid approach (novel)
- SKY130 open-source design (reproducible)
- Commercial path (edge AI market)
- Your MEMS photonics expertise (differentiator)
- Team qualifications (emphasize atomic clock project as proof-of-complexity)

**Suggested narrative:**
> "We leverage our expertise in precision photonic oscillators and analog signal processing (demonstrated in chip-scale atomic clocks) to create the first integrated photonic-analog neuromorphic accelerator. This hybrid approach achieves nanosecond latency (photonic) with ultra-low power (analog) for edge AI inference."

---

#### **2. DARPA OPTIMA (Q3 2026 submission)**

**Program:** Optimum Processing Technology Inside Memory Arrays
**Budget:** ~$78M total, multiple awards
**Focus:** Compute-in-memory, not explicitly photonic, but analog approaches welcomed

**Your angle:**
- Analog in-memory compute core (MAC array)
- Integration with precision clock distribution (unique)
- SKY130 design (academic-friendly, transparent)
- Edge AI focus (meets program goals)

**Contact:** DARPA MTO program manager
**Expected award:** $1-2M over 24-36 months

---

#### **3. NSF Directorate for Engineering - ECCS (2026-2027)**

**Program:** Electronics, Photonics, and Magnetic Devices
**Budget:** $300M+ annually
**Topics:**
- Integrated photonic-electronic systems
- Neuromorphic computing hardware
- Emerging computing paradigms

**Your proposal:**
- Full design kit + tape-out plan
- Open-source methodology (SKY130)
- Academic partnerships (collaborate with MIT, UC Berkeley, or Stanford)

**Expected award:** $500K-$1.5M

---

#### **4. EU Quantum Flagship (2026-2027)**

**Program:** Photonics-specific initiatives
**Budget:** €400M+ 2025-2030
**Relevant calls:**
- Neuromorphic photonics (PROMETHEUS project direction)
- Integrated photonic systems for AI
- SKY130/open-source photonics (EU priority)

**Expected award:** €500K-€2M

---

#### **5. Venture Funding (2027-2028)**

Once you have Phase II results (working silicon), venture capital becomes available:

**Target:** $5-10M Series A
**Investors:**
- Semiconductor-focused: Sapphire Ventures, Intel Capital
- Photonics-focused: Applied Ventures, Tec Ventures
- AI hardware: Dell Technologies Capital, other corporate VC

**Pitch:** "Photonic-analog neuromorphic chip for edge AI. 100× smaller, 100× lower power than Loihi. $2-5K cost vs. millions for Lightmatter. Market: every robot, drone, autonomous vehicle edge AI by 2030."

---

## PART 6: TEAM & PARTNERSHIPS

### Core Team (5-7 people, $2-3M/year cost)

| Role | Skills | Availability | Notes |
|------|--------|--------------|-------|
| **IC Design Lead** | Analog circuits, SKY130 | 1 FTE | You or hire |
| **Photonics Engineer** | Silicon photonics, VCSEL, optical design | 1 FTE | Hire or partner with university |
| **Analog Circuit Designer** | Switched-capacitor, MAC, precision | 1 FTE | Hire or grow from CSAC team |
| **Test/Characterization Engineer** | Lab setup, measurement, benchmarking | 1 FTE | Hire or partner with fab |
| **ML Engineer** (part-time) | SNN training, quantization, benchmarks | 0.5 FTE | Contractor or university partner |
| **Project Manager** | Schedules, budgets, milestones | 0.5 FTE | You or hire |
| **Administrative** | Finance, HR, grant management | 0.25 FTE | Shared services |

**Total cost:** $2-2.5M/year (salaries + overhead)
**Funded by:** NSF SBIR Phase II ($1.75M) + DARPA ($1-2M) = match fully

### Strategic Partnerships

**1. Academic (for credibility & talent)**
- **MIT** (photonic AI, neuromorphic systems) — Marin Soljačić's lab
- **UC Berkeley** (neuromorphic photonics) — Laura Waller's lab
- **Stanford** (analog neuromorphic) — Boris Murmann's group
- **Caltech** (photonic quantum/neural networks) — Belkin/Marandi labs

**Joint paper publications, grad student interns, facility access**

**2. Manufacturing & Tools**
- **Efabless** (MPW coordination) — Already has SKY130 design flow
- **GlobalFoundries** (foundry) — 130nm photonics capability
- **KLayout** (design tool) — Open-source GDS editor, SKY130 compatible

**3. Commercial (for market validation)**
- **BrainChip** (Akida maker) — Benchmark comparison, potential licensing
- **Intel Neuromorphic** (Loihi) — Reference benchmark, potential partnership
- **System integrators** (Qualcomm, Nvidia, Apple) — Early customer feedback

**4. Funding/Venture**
- **Y Combinator/Plug and Play** (startup acceleration)
- **SBIR accelerators** (like Battelle) — Guidance on Phase I/II applications

---

## PART 7: RISK MITIGATION

### Technical Risks

| Risk | Impact | Mitigation |
|------|--------|-----------|
| **SKY130 photonics immaturity** | 6+ months delay | Start with discrete VCSEL + simulation; validate on 2-3 chip variants |
| **Microring frequency drift** | Synchronization loss | Use temperature sensors + closed-loop tuning (analog PID); design for ±5 nm tolerance |
| **VCSEL wavelength mismatch** | Photodetector coupling loss | Over-design detector bandwidth; use array of detectors (redundancy) |
| **Analog computation noise** | Inference accuracy drop | Use 12-bit simulations during design; characterize noise in Phase 2 |
| **Heat dissipation** | Thermal runaway | Simulate thermal mapping early; use floorplan optimization & thermal vias |

### Commercial Risks

| Risk | Impact | Mitigation |
|------|--------|-----------|
| **Market preemption** (Lightmatter scales down) | Product obsolescence | Differentiate on cost/integration; target edge market (vs. datacenter) |
| **Loihi 4 released at lower cost** | Pricing pressure | Use photonics as moat (nanosecond latency unique to you) |
| **Foundry capacity** | Tape-out delays | Secure MPW slot early (2026 Q1); have backup with Samsung or TSMC |
| **Venture funding tightens** | Capital shortage | Rely on government funding (SBIR, DARPA guaranteed if qualified) |

### Regulatory/IP Risks

| Risk | Mitigation |
|------|-----------|
| **Patent landscape (photonics heavily patented)** | Design around existing patents; use university partnerships for freedom-to-operate |
| **Open-source licensing (SKY130 is open)** | Your contributions are proprietary; only design methodology is public |
| **Export control (photonics can be restricted)** | Focus on commercial 780nm (Rb-87, non-classified); avoid military frequencies until needed |

---

## PART 8: REALISTIC SUCCESS METRICS (2026-2030)

### Phase 1 Success (end 2026)
- ✅ NSF SBIR Phase I awarded ($305K)
- ✅ Complete architecture design & feasibility study published
- ✅ SKY130 photonics design kit integrated into your flow
- ✅ 2-3 hired: photonics engineer, analog designer

### Phase 2 Success (end 2027)
- ✅ NSF SBIR Phase II awarded ($1.75M)
- ✅ First silicon fabricated (MPW run, 10-20 dies)
- ✅ Core functionality demonstrated (photonic neurons spiking, analog MACs computing, synchronization locked)
- ✅ Published results showing competitive power/latency benchmarks
- ✅ Team expanded to 5-6 FTE

### Phase 3 Success (end 2028)
- ✅ Second-gen chip taped out (improved specs)
- ✅ Licensing agreement with major chip company (Qualcomm, Apple, or AI startup)
- ✅ Academic spinout or acquisition offer ($10-100M range)
- ✅ 5-10 papers published in top venues (Nature, IEEE, ISSCC)
- ✅ Team of 7-10, $500K-$1M annual revenue from licensing/partnerships

### Phase 4 Success (2029-2030)
- ✅ Commercial product available ($1-5K/unit)
- ✅ First deployment in autonomous vehicle edge AI, medical imaging, or robotics
- ✅ Recurring government contracts ($5-10M/year)
- ✅ Potential acquisition or IPO (if venture-backed)

---

## PART 9: IMMEDIATE NEXT STEPS (April-June 2026)

### This Week
1. ✅ **Read this document** — Understand the landscape
2. ✅ **Assess team gaps** — Identify who you need to hire
3. ✅ **SKY130 photonics tutorial** — Download PDK, run example designs

### April 2026
4. **Form advisory board** — 2-3 experts (photonics, analog AI, manufacturing)
5. **Draft NSF SBIR Phase I proposal** (due June 2026)
   - Emphasize photonic-analog hybrid novelty
   - Reference your CSAC work as proof-of-complexity
   - Identify team members
   - Outline 6-month feasibility study

6. **Secure initial funding** ($50K-$100K) for:
   - SKY130 design tools & licenses
   - Consultant photonics engineer (6 months)
   - Prototype equipment (optical bench, characterization)

### May-June 2026
7. **Submit NSF SBIR Phase I** (June deadline)
8. **Begin preliminary design** (microring oscillator, VCSEL array modeling)
9. **Establish academic partnership** (MIT, Berkeley, or Stanford)
10. **Scout for co-investors** (venture or strategic corporate)

---

## FINANCIAL SUMMARY

### 3-Year Budget (2026-2028)

| Category | 2026 | 2027 | 2028 | Total |
|----------|------|------|------|-------|
| **Personnel** | $400K | $1.2M | $1.5M | $3.1M |
| **Equipment/Tools** | $150K | $100K | $50K | $300K |
| **Fabrication** | $0 | $400K | $300K | $700K |
| **Testing/Characterization** | $50K | $200K | $150K | $400K |
| **Publications/Conferences** | $20K | $40K | $40K | $100K |
| **Contingency (15%)** | $90K | $220K | $240K | $550K |
| **TOTAL** | **$710K** | **$2.16M** | **$2.28M** | **$5.15M** |

### Funding Sources

| Source | 2026 | 2027 | 2028 | Total |
|--------|------|------|------|-------|
| **NSF SBIR Phase I** | $305K | — | — | $305K |
| **NSF SBIR Phase II** | — | $1.75M | — | $1.75M |
| **DARPA/Gov Contract** | — | $1.0M | $1.5M | $2.5M |
| **Venture Capital** | $100K (seed) | — | $1.0M | $1.1M |
| **Internal/Other** | $205K | ($590K match) | — | ($385K) |
| **TOTAL** | **$610K** | **$2.16M** | **$2.5M** | **$5.27M** |

**Bottom line:** Government funding (SBIR + DARPA) covers ~60% of Phase 1-2. Venture covers growth from 2027 onward.

---

## APPENDIX: COMPETITIVE COMPARISON

### You vs. Competitors (2026 vs. 2028)

| Metric | BrainChip Akida | Intel Loihi 3 | EnCharge AI | **You (Projected)** | Lightmatter |
|--------|---|---|---|---|---|
| **Market availability** | Now | Jan 2026 | 2025 | 2028 | Summer 2025 |
| **Primary approach** | Digital SNN | Digital SNN | Analog CIM | **Photonic+Analog** | Photonic I/O only |
| **Die size** | ~3×3 mm | Unknown | Unknown | **5×5 mm** | ~4×4 mm |
| **Power (@ full speed)** | 50-100 mW | <100 mW | 50-200 mW | **75 mW** | N/A (I/O only) |
| **Latency** | 1-10 µs | <1 µs | 1-10 µs | **200-500 ns** | <1 ns |
| **Cost per unit** | $1-5K | Research | $5-20K | **$1-5K** | $1M+ |
| **Model capacity** | 1.2M neurons | 8M neurons | Unknown | **~250K weights** | Not applicable |
| **Training support** | Limited | Yes | No | **No (inference only)** | Not applicable |
| **Photonic elements** | None | None | None | **Yes (VCSELs)** | Yes (interconnect) |
| **Integration** | Digital only | Digital only | Analog only | **Analog+Photonic** | Photonic only |
| **Differentiation** | Mature product | Scale | Low power | **Speed+Cost+Integration** | Bandwidth |

**Your edge:** Only company bridging photonic speed + analog power + neuromorphic algorithms at realistic cost/complexity.

---

## SUMMARY

You have **18-24 months** to go from concept to first silicon. You have:

✅ **Expertise** (atomic clock = precision oscillators, photonic integration, CMOS analog)
✅ **Market** (neuromorphic AI explosive growth, edge AI desperate for low-power chips)
✅ **Technology** (SKY130 photonics is open + mature, VCSEL design proven in CSAC)
✅ **Funding** (SBIR Phase I awarded on merit, DARPA continuously open, venture ready by 2028)
✅ **Differentiation** (photonic-analog hybrid nobody else is building)

**Next action:** Submit NSF SBIR Phase I proposal by June 2026 for Feasibility Study. Use that $305K to validate architecture and hire core team. By end of 2027, you'll have first silicon and publications. By 2028-2029, you'll be shipping commercial units or licensing to larger players.

**This is a $5-20M opportunity over the next 4 years.**

---

**Document prepared:** 2026-03-30
**For questions:** Reference FUNDABLE_RESEARCH_2026.md for detailed source citations
**Next milestone:** Meet with SKY130 design community (early April) → Draft SBIR Phase I (April-May) → Submit June 2026
