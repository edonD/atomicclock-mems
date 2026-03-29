# NeuroPhoton Accelerator: Immediate Action Plan (April-June 2026)

**Status:** Ready for Execution
**Timeline:** 90 days to NSF SBIR Phase I submission (June 2026 deadline)
**Budget Required:** $50-100K (initial feasibility work)
**Team Size:** 2-3 people starting now

---

## WEEK 1-2: Foundational Setup (April 1-15)

### [ ] Technical Foundation
- [ ] Download SKY130 PDK + documentation (free, open-source)
  - Link: https://github.com/google/skywater-pdk
  - Install: `pip install skywater-pdk`
  - Estimated time: 2 hours setup

- [ ] Set up EDA tools (all open-source/free for academic)
  - [ ] **Magic** (VLSI layout tool) — SKY130 design
  - [ ] **Xschem** (schematic capture) — circuit design
  - [ ] **ngspice** (SPICE simulator) — analog circuits
  - [ ] **KLayout** (GDS viewer) — mask visualization
  - [ ] Total installation time: 4-6 hours

- [ ] Complete SKY130 photonics tutorial
  - Link: https://openaccess.sky130.com/
  - Read: "Photonics PDK Overview"
  - Goal: Understand silicon nitride waveguide design
  - Time: 4-6 hours

- [ ] Review existing microring resonator designs (SKY130 example)
  - Find: `sky130_pdk/docs/photonics/microring_tutorial.md`
  - Run simulations locally
  - Understand: resonance tuning, Q-factor, free spectral range
  - Time: 6-8 hours

### [ ] Literature Review
- [ ] Download 5-10 key papers on:
  - [ ] "Photonic-integrated neural networks" (MIT 2024)
  - [ ] "VCSEL-based photonic neurons" (Nature 2023-2024)
  - [ ] "Switched-capacitor analog neural networks" (IBM, Princeton)
  - [ ] "Neuromorphic photonics survey" (Optical Society review)
  - [ ] "Silicon photonics for AI" (Nature Photonics 2024)
  - Time: 4 hours reading

- [ ] Create comparison table: photonic AI vs. analog AI vs. digital neuromorphic
  - Reference: FUNDABLE_RESEARCH_2026.md already has this
  - Update with latest 2026 products
  - Time: 2 hours

### [ ] Team & Advisors
- [ ] Identify 3 potential advisors/collaborators:
  - [ ] Photonics expert (MIT Soljačić lab, UC Berkeley Waller, Stanford Majumdar)
  - [ ] Analog IC designer (with neuromorphic experience)
  - [ ] Manufacturing expert (foundry liaison)
  - Action: Send intro emails with NeuroPhoton project overview
  - Time: 2-3 hours

- [ ] Post job listings (if hiring):
  - [ ] Senior analog IC designer (1 FTE, $150-200K/yr)
  - [ ] Photonics engineer (1 FTE, $140-180K/yr)
  - [ ] Platforms: LinkedIn, AngelList, IEEE Jobs, university boards
  - Time: 3-4 hours

### [ ] Project Infrastructure
- [ ] Create GitHub repo: `neurophyton-accelerator` (private)
  - Organize: `/designs`, `/docs`, `/simulations`, `/papers`
  - Initialize README with project overview
  - Add NEUROMORPHIC_AI_STRATEGY.md and NEUROPHYTON_ARCHITECTURE.md

- [ ] Set up design notebook (Jupyter or OneNote)
  - Daily log of design decisions + simulations
  - Reference for NSF SBIR proposal writing

- [ ] Create project budget spreadsheet
  - Detailed line-item costs for:
    - Team salaries (3 people × 6 months)
    - EDA tool licenses (if any commercial tools needed)
    - Fabrication: MPW cost estimate
    - Testing equipment
    - Travel (to conferences, fab visits)
  - Ensure alignment with NSF SBIR Phase I limits ($305K)

**End of Week 1-2 Checklist:**
- [ ] All EDA tools installed & tested (run one example design)
- [ ] SKY130 photonics tutorial completed
- [ ] 5-10 key papers read & summarized
- [ ] 3+ advisor contacts made
- [ ] GitHub repo created with initial documentation
- [ ] Initial budget drafted

---

## WEEK 3-4: Architecture Refinement (April 15-30)

### [ ] Photonics Subsystem Design

#### Microring Oscillator
- [ ] **Simulation task:** Model 1 GHz microring resonator in SKY130 photonics
  - Parameters: radius, waveguide width, gap to ring
  - Use optical mode solver (e.g., Lumerical MODE, or free COMSOL)
  - Goal: Achieve Q > 10,000 (determines frequency stability)
  - Output: Plot resonance peak, extract resonance frequency
  - Time: 8-10 hours

- [ ] **Frequency stability model:** Predict Allan deviation given PID loop parameters
  - SPICE simulation of feedback circuit
  - Thermal tuning: dn/dT = 1.8×10⁻⁴ (silicon nitride)
  - Loop bandwidth tuning: 10 MHz → 100 MHz trade-off
  - Output: Bode plot of closed-loop stability
  - Time: 4-6 hours

- [ ] **Design trade-study:** Compare different microring designs
  - Option A: 50 µm radius (small, easy to integrate)
  - Option B: 100 µm radius (higher Q, better stability)
  - Option C: Racetrack resonator (different geometry)
  - Choose: Based on power budget + footprint
  - Time: 4 hours

#### VCSEL Array
- [ ] **Research VCSEL specifications** for SKY130 integration
  - Identify commercial VCSEL vendors (Lumentum, Broadcom, RealD)
  - Spec sheet review: wavelength stability, modulation bandwidth
  - Contact vendors: Can they provide 780 nm @ 3×5 mm footprint?
  - Time: 4-6 hours

- [ ] **Waveguide coupling design** (VCSEL → silicon photonics waveguide)
  - Simulate mode-matching between VCSEL beam and waveguide
  - Calculate coupling efficiency (target: > 60%)
  - Design grating coupler if needed
  - Output: Coupling efficiency map (waveguide width vs. VCSEL position)
  - Time: 6-8 hours

- [ ] **Thermal management analysis**
  - Each VCSEL dissipates ~5 mW
  - 16 VCSELs = 80 mW total
  - Simulate temperature rise using thermal FEA (ANSYS, or simplified analytic)
  - Goal: Keep ΔT < 5°C (wavelength shift < 0.3 nm)
  - Output: Thermal map, identify hot spots
  - Time: 6 hours

#### Waveguide Clock Distribution
- [ ] **Route optimization:** Design waveguide layout for minimal skew
  - Use symmetric branching (binary tree layout)
  - Simulate path length differences → clock jitter
  - Add phase shifters for fine-tuning
  - Output: Layout diagram, jitter budget summary
  - Time: 6-8 hours

- [ ] **Power loss budget:** Calculate optical power at each neuron
  - Starting power: 100 mW (from microring)
  - Splitter loss: 0.5 dB per stage
  - Waveguide loss: 0.1 dB/mm
  - Final power available per neuron: > 10 µW
  - Output: Power flow diagram
  - Time: 2 hours

### [ ] Analog Subsystem Design

#### MAC Array
- [ ] **Design single MAC cell** (multiply-accumulate)
  - SPICE schematic: input sampling, weight storage, charge sharing
  - Transient analysis: settling time, precision loss due to parasitic
  - Output: AC response, noise figure
  - Time: 10-12 hours

- [ ] **Layout single MAC cell** (physical implementation)
  - Use SKY130 design kit in Magic
  - Size transistors for balanced performance
  - Minimize capacitive parasitics
  - Output: GDS layout, design rules check (DRC) pass
  - Time: 8-10 hours

- [ ] **Array scaling:** Replicate to 16×16 grid
  - Floorplan: arrange cells in matrix
  - Power routing: separate analog power from digital
  - Ground distribution: minimize ground bounce
  - Output: Full 16×16 layout
  - Time: 6-8 hours

#### Non-linear Activation & Comparators
- [ ] **Design 16 × comparators** (for ReLU: y = max(0, x))
  - SPICE circuit: inverter-based latch comparator
  - Threshold tuning: variable reference
  - Speed: < 1 ns decision time
  - Output: Schematic + simulation
  - Time: 4-6 hours

- [ ] **Output buffers** (impedance matching to digital)
  - Drive digital input capacitance (10-20 pF)
  - Output: Drive strength (5 mA minimum)
  - CMOS inverter size optimization
  - Time: 2-3 hours

### [ ] Digital Control Subsystem

#### FSM & Sequencer
- [ ] **Design finite state machine**
  - States: IDLE → INFER → WAIT → ROUTE_SPIKES → IDLE
  - Transitions on 1 GHz clock
  - Verilog RTL implementation
  - Time: 6-8 hours

- [ ] **Spike router logic**
  - 16 priority encoders (which neuron spikes first?)
  - Multiplexer for output (SPI serialization)
  - Time: 4 hours

#### SPI Slave Interface
- [ ] **Design SPI controller** (load weights via SPI)
  - Clock: up to 10 MHz
  - Data: 8 bits per word
  - Write sequence: address (4 bits) + data (8 bits)
  - Time: 4-6 hours

#### Test Circuitry
- [ ] **Design built-in self-test (BIST)**
  - Internal oscillator test (frequency measurement)
  - Analog loopback (MAC functionality check)
  - Temperature sensor readout
  - Output: Test strategy document
  - Time: 4 hours

### [ ] System Integration
- [ ] **Create top-level block diagram** (update NEUROPHYTON_ARCHITECTURE.md)
  - Show all subsystems interconnected
  - Power distribution network (PDN) plan
  - Clock distribution tree
  - I/O pad placement
  - Time: 4 hours

- [ ] **Conduct design review** (with your team/advisors)
  - Present architecture
  - Review trade-offs (power vs. performance vs. area)
  - Get feedback on manufacturability
  - Time: 2 hours

**End of Week 3-4 Checklist:**
- [ ] Microring resonator simulated, Q-factor verified
- [ ] VCSEL coupling efficiency analyzed
- [ ] Thermal management budget acceptable
- [ ] Single MAC cell designed + laid out
- [ ] 16×16 MAC array floorplan complete
- [ ] FSM Verilog written
- [ ] SPI interface designed
- [ ] System integration review completed

---

## WEEK 5-8: Detailed Design & NSF Proposal Writing (May 1-31)

### [ ] Complete IC Design
- [ ] **Finalize all subcircuits** (bring designs to "design review ready" state)
  - Microring oscillator with feedback circuit
  - 16 VCSEL drivers (current sources, modulation control)
  - Full 16×16 MAC array
  - 16 comparators + output buffers
  - FSM + SPI interface + internal test logic

- [ ] **System-level SPICE simulation**
  - Simulate one layer inference (16 inputs → 16 outputs)
  - Measure total latency (should be 100-500 ns)
  - Verify power consumption (target: < 100 mW)
  - Output: Performance summary table
  - Time: 12-16 hours

- [ ] **Layout all subsystems** (in SKY130 Magic)
  - Place-and-route using open-source tools (OpenROAD)
  - Or manual P&R if preferred (more control)
  - Design rule checks (DRC): must pass 100%
  - Layout versus schematic (LVS): must pass 100%
  - Time: 20-30 hours

- [ ] **Create design kit documentation**
  - Schematic symbols for top-level blocks
  - Layout design rules (spacing, minimum features)
  - Simulation models for tape-out
  - Post-layout simulation (with parasitics)

### [ ] Preliminary Manufacturing Analysis
- [ ] **Contact potential foundries**
  - GlobalFoundries (SKY130 process, has photonics)
  - TSMC (130 nm, might support photonics via partnership)
  - Samsung (also has 130 nm photonics)
  - Get: Preliminary quotes for MPW run (10-20 die per run)
  - Time: 3-4 hours

- [ ] **Design for testability (DFT) plan**
  - Test pads for probe testing (microring power, frequency)
  - Internal oscillators for clock/frequency measurement
  - Analog test points (MAC intermediate nodes)
  - Output: Test pad map, probe sequence
  - Time: 4 hours

- [ ] **Estimate manufacturing schedule**
  - Design completion: May 31
  - Mask set generation: June (2-4 weeks)
  - Wafer fabrication: July-September (12-16 weeks typical)
  - Packaging: October-November (6-8 weeks)
  - First results: December 2026 (realistic timeline)

### [ ] NSF SBIR Phase I Proposal Writing (Due June 2026)

**Proposal Structure (6-page limit for Phase I):**

#### Page 1: Project Summary (1 page)
- Title: "Photonic-Analog Neuromorphic Accelerator on a Chip"
- Impact: "Enable energy-efficient AI inference for edge devices (robotics, drones, medical) by combining photonic speed with analog power efficiency"
- Technical approach: "Integrate VCSEL photonic neurons + switched-capacitor analog MACs + digital control on single SKY130 die"
- Key innovation: "First hybrid photonic-analog neuromorphic chip; leverages atomic clock expertise in precision oscillators + photonics integration"
- Anticipated benefits: 100× faster, 10× lower power than digital alternatives; commercial path via edge AI market ($4.5B+ 2025-2030)

#### Page 2: Technical Approach (2 pages)
- Detailed explanation of each subsystem:
  1. Photonic subsystem: microring oscillator (frequency stability), VCSEL neurons (GHz spiking), waveguide clock distribution
  2. Analog subsystem: switched-capacitor MACs (multiply-accumulate), nonlinear activation (ReLU)
  3. Digital control: FSM, SPI weight loading, spike routing
- Design specifications: 16 neurons, 16×16 weights, 100 ns latency, 100 mW power, 5×5 mm die
- Use diagrams from NEUROPHYTON_ARCHITECTURE.md
- Performance projections: Compare vs. BrainChip Akida, Intel Loihi, Jetson

#### Page 3: Feasibility & Preliminary Results (1 page)
- Show: SPICE simulations of MAC, microring resonator frequency stability
- Include plots: Power consumption vs. frequency, latency vs. array size, thermal analysis
- Demonstrate your team's expertise: Reference atomic clock project ("We have designed precision oscillators and photonic-electronic integrated circuits at mm-scale...")

#### Page 4: Work Plan & Timeline (1 page)
- Phase I (6 months, $305K):
  - Months 1-2: Finalize architecture, complete design review
  - Months 2-4: Detailed IC design (all cells simulated & laid out)
  - Months 4-5: System integration, foundry engagement, manufacturing planning
  - Month 6: Phase II proposal preparation, IP disclosure
  - Deliverables: Complete design kit (schematics, layouts, models), foundry quotes, tape-out readiness

#### Page 5: Commercial Potential & Broader Impact (1 page)
- Market: Edge AI accelerators for autonomous vehicles, robots, medical devices
- Competitive advantage: Only photonic-analog neuromorphic chip; 100× faster than BrainChip; 100× cheaper than Lightmatter
- Path to commercialization: Phase II (build silicon, demo), then licensing to Qualcomm/Apple/Nvidia or spinout company
- Broader impacts: Enable privacy-preserving AI inference (no cloud needed); reduce energy consumption in datacenters; create jobs in photonics + neuromorphic fields

#### Page 6: Team & Facilities (1 page)
- Key personnel:
  - PI: You (list your credentials: atomic clock, MEMS, CMOS integration experience)
  - Co-I 1: Photonics expert (from advisory board)
  - Co-I 2: Analog IC designer
  - Student researchers (graduate assistants for simulation/layout)
- Facilities:
  - EDA tools: SKY130 (free), OpenROAD (free), Xschem/Magic (free)
  - Computing: Your existing infrastructure (no new hardware needed)
  - Collaborations: Academic advisors (MIT, UC Berkeley, Stanford)

**Proposal Writing Timeline:**
- Week 5 (May 1-5): Outline + gather figures
- Week 6 (May 6-12): Draft Sections 1-3 (impact + approach)
- Week 7 (May 13-19): Draft Sections 4-6 (work plan + team)
- Week 8 (May 20-26): Revisions + advisor feedback
- Week 9 (May 27-June 2): Final polish + submit

**Pro tips for NSF SBIR proposals:**
1. Emphasize novelty: "First hybrid photonic-analog neuromorphic chip" (true!)
2. Show team expertise: Use atomic clock project as proof that you can execute complex MEMS+photonics integration
3. Be realistic: Don't promise production chips in 6 months (you won't deliver); promise "design kit + foundry engagement"
4. Address risks: Acknowledge VCSEL integration challenges, mitigation via multiple design variants
5. Include budget justification: $305K Phase I should cover ~$200K salaries, $50K simulation tools, $30K travel/communications, $25K contingency

---

## WEEK 9-12: Submission & Transition to Phase II (June-July)

### [ ] NSF SBIR Phase I Submission (Due June 2026)
- [ ] Finalize proposal (get NSF format correct: margins, fonts, page limits)
- [ ] Submit via Grants.gov (register organization first)
- [ ] Confirmation: NSF acknowledges receipt within 48 hours

### [ ] Continuation Planning
- [ ] **Draft Phase II proposal outline** (parallel to Phase I)
  - Phase II (24 months, $1.75M): Build silicon, demonstrate system
  - Includes detailed test plan, benchmarking, licensing strategy
  - Keep as backup if Phase I approved early

- [ ] **Engage with other funding sources** (DARPA, NSF, EU)
  - DARPA OPTIMA: Submit competing proposal (different angle than Phase II)
  - EU Quantum Flagship: Explore photonics-specific calls
  - NSF ECCS: Electronics, photonics, magnetic devices

- [ ] **Accelerate team hiring**
  - Once Phase I approved: Hire analog IC designer + photonics engineer
  - Ramp up design timeline

---

## BUDGET SUMMARY (Phase I: $305K)

| Category | Amount | Notes |
|----------|--------|-------|
| **Personnel** | $180K | PI (0.5 FTE) + Co-I (0.5 FTE) + 1 grad student (1 FTE) × 6 months |
| **Equipment** | $10K | EDA licenses (if needed), simulation workstation |
| **Consulting** | $30K | Photonics expert advice, foundry liaison, manufacturing guidance |
| **Travel** | $15K | Trip to foundry (GlobalFoundries), NSF PI meeting, conference |
| **Materials & Services** | $20K | Design documentation, IP protection, communication |
| **Indirect Costs (F&A)** | $50K | University overhead (~20% of direct costs) |
| **TOTAL** | **$305K** | Exactly NSF Phase I limit |

---

## SUCCESS METRICS (End of Phase I, December 2026)

✅ **Deliverables:**
- [ ] Complete IC design (schematics + layouts in Magic/GDS)
- [ ] SPICE simulation of full system (latency, power verified)
- [ ] Design kit (symbols, libraries, simulation models)
- [ ] Design review presentation (technical depth)
- [ ] Manufacturing plan + foundry quotes (realistic timeline)
- [ ] NSF Phase II proposal (ready to submit if Phase I approved)

✅ **Technical Achievements:**
- [ ] Microring resonator Q > 10,000 (frequency stability 5×10⁻¹³)
- [ ] 16×16 MAC array latency < 100 ns (per layer)
- [ ] Total system power < 100 mW @ 1 GHz
- [ ] Die area 5×5 mm (achievable in SKY130)
- [ ] All DRC/LVS checks pass (manufacturing-ready)

✅ **Publications:**
- [ ] Submit technical paper to IEEE (design overview, performance projections)
- [ ] Post design kit on GitHub (open-source, reproducible)

---

## LONG-TERM VISION (2026-2029)

```
2026: NSF SBIR Phase I ($305K)
  → Complete design kit

2027: NSF SBIR Phase II ($1.75M) + DARPA ($1-2M)
  → Fabricate silicon, characterize, publish

2028: Second-gen design + licensing discussions
  → Partner with Qualcomm, Apple, or startup
  → Potential Series A funding ($5-10M venture)

2029: Commercial availability
  → First customers (edge AI, autonomous vehicles, robotics)
  → Annual revenue: $1-5M (licensing fees)

2030-2035: Scale to full product family
  → 4×4 array (64 neurons), 8×8 (256 neurons)
  → Integration with other functions (sensor interfaces, power management)
  → Potential IPO or acquisition by major chip company ($100M+)
```

---

## FINAL CHECKLIST (Ready to Launch)

- [ ] **Documents completed:**
  - [ ] NEUROMORPHIC_AI_STRATEGY.md (market analysis, funding)
  - [ ] NEUROPHYTON_ARCHITECTURE.md (technical design)
  - [ ] NEUROPHYTON_KICKOFF.md (this document)

- [ ] **Team assembled:**
  - [ ] Core team identified (you + 1-2 initial hires/advisors)
  - [ ] Advisors on board (photonics, analog IC, manufacturing)
  - [ ] GitHub + infrastructure ready

- [ ] **Funding plan activated:**
  - [ ] NSF SBIR Phase I outlined + timeline set
  - [ ] DARPA OPTIMA tracked (next BAA cycle)
  - [ ] EU/other sources identified as backup

- [ ] **Technical foundation strong:**
  - [ ] SKY130 PDK installed + tutorials completed
  - [ ] EDA tools set up (Magic, Xschem, ngspice)
  - [ ] Key papers read + competitive landscape understood

**You are ready to start design work immediately.**

---

## CONTACTS & RESOURCES

### Funding Programs
- **NSF SBIR:** https://www.sba.gov/sbir/
  - Contact: NSF grants.gov
  - Program officer (Compute Systems): [look up when applying]
  - Deadline: June 2026 (annually in June)

- **DARPA OPTIMA:** https://www.darpa.mil/research/programs/optimum-processing-technology-inside-memory-arrays
  - Contact: DARPA MTO program manager
  - BAA cycle: Check DARPA website for open solicitations

- **EU Quantum Flagship:** https://quantumflagship.eu/
  - Photonics-specific calls opening 2026-2027
  - EU grants up to €2M

### Technical Resources
- **SKY130 PDK:** https://github.com/google/skywater-pdk
- **OpenROAD:** https://openroad.readthedocs.io/ (place & route)
- **Xschem:** https://xschem.sourceforge.io/ (schematic editor)
- **Magic:** http://opencircuitdesign.com/magic/ (layout tool)

### Manufacturing
- **GlobalFoundries SKY130:** Contact through Efabless
  - Efabless: https://efabless.com/ (MPW coordination)
  - Typical cost: $1-2K per die @ 1K die per project

- **Design Support:** OpenLane (open-source design flow)

### Academic Collaboration
- **MIT:** Marin Soljačić (photonic neural networks)
- **UC Berkeley:** Laura Waller (computational photonics)
- **Stanford:** Shanhui Fan (integrated photonics)
- **Caltech:** Alireza Marandi (frequency combs, photonics)

---

## CONCLUSION

You have a **clear, executable plan** to build the first photonic-analog neuromorphic accelerator. You have:

✅ Technology (SKY130 photonics + your MEMS expertise)
✅ Market (neuromorphic AI $7.05B market by 2032)
✅ Funding path (NSF SBIR Phase I ready in June)
✅ Team (hiring plan for Phase I, advisors identified)
✅ Technical roadmap (18 months to first silicon)

**Next step:** Start with Week 1-2 checklist. Download SKY130 PDK, set up EDA tools, read papers, contact advisors. By mid-May, begin detailed design. By June, submit NSF proposal.

**This is a $5-20M opportunity over 4 years.**

Good luck. You've got this.

---

**Document Created:** 2026-03-30
**Last Updated:** 2026-03-30
**Status:** Ready for Execution
