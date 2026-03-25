"""
SIM: 00_atomic_model
====================
Wave 1 | Tool: QuTiP | ~2 days to implement and validate

Simulates:
  - Rb-87 energy level structure (hyperfine Hamiltonian)
  - CPT Lambda system (3-level density matrix)
  - CPT resonance curve vs Raman detuning
  - Contrast and linewidth extraction

After running, evaluator.py grades the results.

TODO: implement the simulation below.
      The RESULTS dict at the bottom is what evaluator.py reads.
"""

import numpy as np

# ─────────────────────────────────────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────────────────────────────────────

hbar   = 1.054571817e-34
h      = 6.62607015e-34
kB     = 1.380649e-23
c      = 299792458.0
mu_B   = 9.2740100783e-24

# Rb-87 fixed constants (from NIST)
RB87_HYPERFINE_HZ  = 6_834_682_610.904
RB87_D1_FREQ_HZ    = 377_107_463_380_000.0
RB87_D1_LAMBDA_NM  = 794.978851156
RB87_LIFETIME_5P_S = 27.70e-9
RB87_GAMMA_RAD     = 1.0 / RB87_LIFETIME_5P_S          # natural linewidth (rad/s)
RB87_GAMMA_HZ      = RB87_GAMMA_RAD / (2 * np.pi)      # natural linewidth (Hz)


# ─────────────────────────────────────────────────────────────────────────────
# SIMULATION — TODO: implement
# ─────────────────────────────────────────────────────────────────────────────

def simulate_energy_levels():
    """
    Build Rb-87 hyperfine Hamiltonian and compute energy levels.

    Returns:
        dict with keys: hyperfine_hz, d1_wavelength_nm, natural_linewidth_mhz
    """
    # TODO: use QuTiP to build H = A_hfs * I.J
    # Verify hyperfine splitting = RB87_HYPERFINE_HZ
    raise NotImplementedError("simulate_energy_levels not implemented yet")


def simulate_cpt_resonance(gamma_12_hz=1000.0, omega_rabi_ratio=0.3):
    """
    Solve 3-level Lambda density matrix at steady state.
    Sweep Raman detuning and extract CPT resonance curve.

    Args:
        gamma_12_hz:      ground state decoherence rate (Hz)
                          typical range: 300 Hz to 3000 Hz
        omega_rabi_ratio: Rabi frequency as fraction of natural linewidth Γ
                          typical range: 0.1 to 2.0

    Returns:
        dict with keys: delta_R_hz (array), absorption (array),
                        cpt_linewidth_khz, cpt_contrast_pct,
                        dark_state_verified, optimal_laser_power_uw
    """
    # TODO: implement using QuTiP or manual density matrix evolution
    #
    # Hamiltonian (rotating frame, RWA):
    #   H = -hbar * [delta_1 * |3><3| + delta_R * |2><2|
    #              - Omega_1/2 * |3><1| - Omega_2/2 * |3><2| + h.c.]
    #
    # Lindblad operators:
    #   L1 = sqrt(Gamma/2) * |1><3|    (decay to lower ground state)
    #   L2 = sqrt(Gamma/2) * |2><3|    (decay to upper ground state)
    #   L3 = sqrt(gamma_12) * |1><2|   (ground decoherence)
    #
    # Solve: d(rho)/dt = -i/hbar [H, rho] + sum_k (Lk rho Lk† - 0.5{Lk†Lk, rho})
    # At steady state: d(rho)/dt = 0
    #
    # Extract: absorption = Im(rho_31) proportional to absorbed light intensity
    raise NotImplementedError("simulate_cpt_resonance not implemented yet")


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("Running 00_atomic_model simulation...")

    # Part A: energy levels
    levels = simulate_energy_levels()
    print(f"Hyperfine splitting: {levels['hyperfine_hz']:.3f} Hz")
    print(f"D1 wavelength:       {levels['d1_wavelength_nm']:.6f} nm")

    # Part B: CPT resonance
    # Sweep over gamma_12 values to find optimal operating point
    cpt = simulate_cpt_resonance(gamma_12_hz=1000.0, omega_rabi_ratio=0.3)
    print(f"CPT linewidth:  {cpt['cpt_linewidth_khz']:.2f} kHz")
    print(f"CPT contrast:   {cpt['cpt_contrast_pct']:.2f} %")

    # Generate plots
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # TODO: plot energy levels
    # TODO: plot CPT resonance curve

    plt.tight_layout()
    plt.savefig("00_atomic_model/plots/cpt_resonance.png", dpi=150)
    print("Plots saved to 00_atomic_model/plots/")

    print("\nDone. Run evaluator.py to grade results.")


# ─────────────────────────────────────────────────────────────────────────────
# RESULTS — evaluator.py reads this dict
# Fill in after simulation runs successfully.
# ─────────────────────────────────────────────────────────────────────────────

RESULTS = {
    # Part A: atomic constants (validated against NIST)
    "hyperfine_hz":             None,   # fill: e.g. 6_834_682_610.904
    "d1_wavelength_nm":         None,   # fill: e.g. 794.978851
    "natural_linewidth_mhz":    None,   # fill: e.g. 5.746

    # Part B: CPT performance
    "cpt_linewidth_khz":        None,   # fill: e.g. 3.2
    "cpt_contrast_pct":         None,   # fill: e.g. 4.8
    "optimal_laser_power_uw":   None,   # fill: e.g. 120.0
    "discriminator_slope":      None,   # fill: normalized slope at lock point

    # Verification flags
    "dark_state_verified":      None,   # fill: True or False
    "clock_transition_verified": None,  # fill: True or False
}
