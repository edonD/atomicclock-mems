#!/usr/bin/env python3
"""
Generate the CSAC cross-section and floorplan sheets with a restrained, shared
visual system.
"""

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyArrowPatch, FancyBboxPatch, Rectangle

BASE = Path(__file__).parent

BG = "#050812"
PANEL = "#0b1321"
PANEL_ALT = "#0f1a2c"
OUTLINE = "#21334d"
TEXT = "#e8effb"
MUTED = "#93a6c3"
ACCENT = "#62d5ff"
OPTICAL = "#73e3ff"
THERMAL = "#ffbd62"
RF = "#8b72f6"
STACK_GLASS = "#6ed4ff"
STACK_GAS = "#5b284f"
STACK_BOND = "#7b6756"
STACK_SI = "#1f2a3d"
STACK_VOID = "#08111d"
PAD = "#b6925f"
GOOD = "#8be6b8"


def setup_ax(ax, xlim, ylim):
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.set_facecolor(BG)
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)


def add_badge(ax, x, y, text, edge=ACCENT, fill=PANEL_ALT, color=TEXT):
    ax.text(
        x,
        y,
        text,
        ha="left",
        va="center",
        fontsize=8,
        color=color,
        fontweight="bold",
        bbox=dict(
            boxstyle="round,pad=0.35,rounding_size=0.18",
            facecolor=fill,
            edgecolor=edge,
            linewidth=1.0,
        ),
    )


def add_title(ax, title, subtitle):
    ax.text(8, 96, title, fontsize=19, fontweight="bold", color=TEXT, ha="left")
    ax.text(8, 91.5, subtitle, fontsize=10, color=MUTED, ha="left")


def add_dim_arrow(ax, x0, y0, x1, y1, label, color):
    ax.annotate(
        "",
        xy=(x1, y1),
        xytext=(x0, y0),
        arrowprops=dict(arrowstyle="<->", color=color, lw=1.6),
    )
    ax.text(
        (x0 + x1) * 0.5,
        (y0 + y1) * 0.5,
        label,
        ha="center",
        va="center",
        fontsize=9,
        color=color,
        fontweight="bold",
        bbox=dict(
            boxstyle="round,pad=0.2,rounding_size=0.12",
            facecolor=BG,
            edgecolor="none",
            alpha=0.9,
        ),
    )


def block(ax, xy, wh, label, sublabel, edge, face=PANEL_ALT):
    x, y = xy
    w, h = wh
    ax.add_patch(
        FancyBboxPatch(
            (x, y),
            w,
            h,
            boxstyle="round,pad=0.3,rounding_size=0.65",
            facecolor=face,
            edgecolor=edge,
            linewidth=1.4,
        )
    )
    ax.text(x + w * 0.5, y + h * 0.62, label, ha="center", va="center",
            fontsize=9, color=TEXT, fontweight="bold")
    ax.text(x + w * 0.5, y + h * 0.28, sublabel, ha="center", va="center",
            fontsize=7, color=MUTED)


def generate_cross_section():
    fig, ax = plt.subplots(figsize=(16, 10), dpi=150)
    fig.patch.set_facecolor(BG)
    setup_ax(ax, (0, 100), (0, 100))

    ax.add_patch(
        FancyBboxPatch(
            (4, 6),
            92,
            86,
            boxstyle="round,pad=0.6,rounding_size=1.4",
            facecolor=PANEL,
            edgecolor=OUTLINE,
            linewidth=1.2,
        )
    )

    add_title(
        ax,
        "CSAC Internal Cross-Section",
        "One sheet, one palette: optical path, thermal control, and mixed-signal stack.",
    )
    add_badge(ax, 69, 96.5, "SIMULATED INTERNAL ARCHITECTURE")

    x0 = 12
    w = 64
    layers = [
        ("Glass lid", 82, 9, STACK_GLASS),
        ("Rb-87 + N2 cavity", 68, 14, STACK_GAS),
        ("Anodic bond", 64.7, 3.3, STACK_BOND),
        ("Silicon substrate", 20, 44.7, STACK_SI),
        ("Pad ring / bulk", 10, 10, "#101a28"),
    ]

    for name, y, h, color in layers:
        ax.add_patch(Rectangle((x0, y), w, h, facecolor=color, edgecolor=OUTLINE, linewidth=1.1))
        ax.text(x0 + w + 3.2, y + h * 0.5, name, ha="left", va="center",
                fontsize=9, color=TEXT if color != STACK_BOND else "#e3d6c5", fontweight="bold")

    ax.text(x0 + w * 0.5, 86.3, "Borosilicate lid / optical entry window",
            ha="center", va="center", fontsize=10, color=TEXT, fontweight="bold")
    ax.text(x0 + w * 0.5, 74.2, "Atomic vapor cavity", ha="center", va="center",
            fontsize=11, color="#f2d9ff", fontweight="bold")
    ax.text(x0 + w * 0.5, 70.4, "Rb-87 vapor, N2 buffer gas, 1 mm class cavity depth",
            ha="center", va="center", fontsize=8.4, color="#d6afd8")
    ax.text(x0 + w * 0.5, 42.2, "Thinned silicon platform with heater, photodiode, and control electronics",
            ha="center", va="center", fontsize=10, color="#bdd2ef", fontweight="bold")

    cavity = Rectangle((26, 43), 36, 11.5, facecolor=STACK_VOID, edgecolor="#ab89d1",
                       linewidth=1.3, linestyle=(0, (2, 2)))
    ax.add_patch(cavity)
    ax.text(44, 48.7, "Back-etched cavity volume", ha="center", va="center",
            fontsize=8.5, color="#c9afeb", style="italic")

    for cx in [20, 32, 44, 56, 68]:
        ax.add_patch(Circle((cx, 75), 1.2, facecolor="#f4b1c8", edgecolor="none", alpha=0.65))

    heater_color = "#ff9e52"
    ax.add_patch(Rectangle((14.4, 32), 6.8, 5.8, facecolor="#3a2417", edgecolor=heater_color, linewidth=1.2))
    ax.add_patch(Rectangle((66.8, 32), 6.8, 5.8, facecolor="#3a2417", edgecolor=heater_color, linewidth=1.2))
    ax.text(17.8, 34.9, "Heater", ha="center", va="center", fontsize=7.8, color=THERMAL, fontweight="bold")
    ax.text(70.2, 34.9, "Heater", ha="center", va="center", fontsize=7.8, color=THERMAL, fontweight="bold")

    block(ax, (17, 17.5), (11, 8.2), "VCO", "6.835 GHz", RF)
    block(ax, (31, 17.5), (11, 8.2), "TIA", "photodiode readout", ACCENT)
    block(ax, (45, 17.5), (11, 8.2), "Divider", "1 Hz / servo clocks", GOOD)
    block(ax, (59, 17.5), (11, 8.2), "PID", "lock + heater control", THERMAL)
    block(ax, (38.3, 28), (7.4, 5.5), "PD", "780 nm sense", ACCENT)

    beam = FancyArrowPatch((10, 75), (26, 75), arrowstyle="-|>", mutation_scale=22,
                           linewidth=2.4, color=OPTICAL)
    ax.add_patch(beam)
    ax.text(8.2, 79.4, "Laser input", ha="right", va="center", fontsize=9,
            color=OPTICAL, fontweight="bold")

    through = FancyArrowPatch((44, 84.5), (44, 55), arrowstyle="-|>", mutation_scale=18,
                              linewidth=2.2, color=OPTICAL)
    ax.add_patch(through)
    ax.text(46.2, 69.6, "Optical path", ha="left", va="center", fontsize=8.5,
            color=OPTICAL, fontweight="bold")

    sense = FancyArrowPatch((42, 30.6), (42, 25.7), arrowstyle="-|>", mutation_scale=14,
                            linewidth=1.8, color=ACCENT)
    ax.add_patch(sense)
    ax.text(44.1, 28.4, "Absorption signal", ha="left", va="center", fontsize=7.8, color=ACCENT)

    ax.add_patch(FancyArrowPatch((42, 21.6), (59, 21.6), arrowstyle="-|>", mutation_scale=14,
                                 linewidth=1.7, color=ACCENT))
    ax.add_patch(FancyArrowPatch((64.5, 21.6), (28.2, 20.6), arrowstyle="-|>", mutation_scale=14,
                                 linewidth=1.7, color=THERMAL, linestyle="--"))
    ax.text(52.3, 15.3, "Frequency correction loop", ha="center", va="center",
            fontsize=7.8, color=THERMAL)

    ax.add_patch(FancyArrowPatch((64.5, 22.8), (70.2, 37), arrowstyle="-|>", mutation_scale=14,
                                 linewidth=1.6, color=THERMAL))
    ax.text(67.5, 30.6, "Heater drive", ha="center", va="center", fontsize=7.6, color=THERMAL)

    add_dim_arrow(ax, 8, 10, 8, 82, "3.0 mm die span", ACCENT)
    add_dim_arrow(ax, 12, 8, 76, 8, "3.0 mm", ACCENT)
    add_dim_arrow(ax, 84, 68, 84, 82, "1.0 mm cavity", THERMAL)

    pad_positions = [15, 22, 29, 36, 43, 50, 57, 64, 71]
    for px in pad_positions:
        ax.add_patch(Rectangle((px - 0.9, 12.3), 1.8, 3.5, facecolor=PAD, edgecolor="#d2af78", linewidth=0.8))

    ax.text(44, 8.8,
            "Phase 1 values are simulated. Package dimensions and subsystem placement are concept-level.",
            ha="center", va="center", fontsize=8.5, color=MUTED, style="italic")

    outfile = BASE / "chip_cross_section.png"
    fig.savefig(outfile, dpi=150, facecolor=BG, edgecolor="none", bbox_inches="tight")
    plt.close(fig)
    print(f"Cross-section diagram saved: {outfile}")


def generate_floorplan():
    fig, ax = plt.subplots(figsize=(14, 14), dpi=150)
    fig.patch.set_facecolor(BG)
    setup_ax(ax, (0, 100), (0, 100))

    ax.add_patch(
        FancyBboxPatch(
            (4, 4),
            92,
            92,
            boxstyle="round,pad=0.8,rounding_size=1.4",
            facecolor=PANEL,
            edgecolor=OUTLINE,
            linewidth=1.2,
        )
    )

    add_title(
        ax,
        "CSAC Top-Down Floorplan",
        "Reduced color entropy: neutral blocks, one optical accent, one thermal accent, one RF accent.",
    )
    add_badge(ax, 72, 96.5, "PLACEMENT STUDY / CONCEPT")

    die = Rectangle((8, 8), 84, 84, facecolor="#08111c", edgecolor=ACCENT, linewidth=1.8)
    ax.add_patch(die)

    cavity = FancyBboxPatch((24, 24), 52, 52, boxstyle="round,pad=0.5,rounding_size=1.2",
                            facecolor=STACK_GAS, edgecolor="#b38ce2", linewidth=1.4, alpha=0.95)
    ax.add_patch(cavity)
    ax.text(50, 52, "Optical cavity", ha="center", va="center", fontsize=14, color=TEXT, fontweight="bold")
    ax.text(50, 46.8, "Rb-87 vapor + N2", ha="center", va="center", fontsize=10, color="#d8bce9")
    ax.text(50, 42.2, "1.8 x 1.8 mm class envelope", ha="center", va="center", fontsize=8.6, color=MUTED)

    heater_edge = "#ff9e52"
    heaters = [
        Rectangle((24, 77), 52, 6.5, facecolor="#312114", edgecolor=heater_edge, linewidth=1.3),
        Rectangle((24, 16.5), 52, 6.5, facecolor="#312114", edgecolor=heater_edge, linewidth=1.3),
        Rectangle((16.5, 24), 6.5, 52, facecolor="#312114", edgecolor=heater_edge, linewidth=1.3),
        Rectangle((77, 24), 6.5, 52, facecolor="#312114", edgecolor=heater_edge, linewidth=1.3),
    ]
    for rect in heaters:
        ax.add_patch(rect)
    ax.text(50, 80.2, "Heater ring", ha="center", va="center", fontsize=9, color=THERMAL, fontweight="bold")

    block(ax, (71.5, 60), (12, 10), "VCO", "isolated RF island", RF)
    block(ax, (66, 44), (10.5, 8.5), "DAC", "varactor tune", THERMAL)
    block(ax, (71.5, 76.5), (10, 8), "TIA", "close to photodiode", ACCENT)
    block(ax, (84, 76.5), (8, 8), "PD", "optical sense", ACCENT)
    block(ax, (12, 76.5), (12, 8), "Divider", "timebase outputs", GOOD)
    block(ax, (12, 60), (12, 8), "PID", "servo + heater", THERMAL)
    block(ax, (8.8, 43), (8.7, 10), "SPI", "edge I/O", ACCENT)

    for cx, cy in [(22, 22), (36, 86), (80, 22), (84, 37), (18, 37)]:
        ax.add_patch(Rectangle((cx, cy), 3.4, 3.4, facecolor="#151f2d", edgecolor="#405068", linewidth=0.8))
        ax.text(cx + 1.7, cy + 1.7, "C", ha="center", va="center", fontsize=7, color=MUTED)

    for x in range(10, 90, 8):
        ax.add_patch(Rectangle((x, 92), 3.8, 3, facecolor=PAD, edgecolor="#d2af78", linewidth=0.7))
        ax.add_patch(Rectangle((x, 5), 3.8, 3, facecolor=PAD, edgecolor="#d2af78", linewidth=0.7))
    for y in range(10, 90, 8):
        ax.add_patch(Rectangle((5, y), 3, 3.8, facecolor=PAD, edgecolor="#d2af78", linewidth=0.7))
        ax.add_patch(Rectangle((92, y), 3, 3.8, facecolor=PAD, edgecolor="#d2af78", linewidth=0.7))

    ax.add_patch(FancyArrowPatch((88, 80), (80, 80), arrowstyle="-|>", mutation_scale=16,
                                 linewidth=1.9, color=ACCENT))
    ax.add_patch(FancyArrowPatch((71.5, 80), (24, 64), arrowstyle="-|>", mutation_scale=14,
                                 linewidth=1.5, color=ACCENT, linestyle="--"))
    ax.add_patch(FancyArrowPatch((24, 64), (66, 48), arrowstyle="-|>", mutation_scale=14,
                                 linewidth=1.5, color=THERMAL, linestyle="--"))
    ax.add_patch(FancyArrowPatch((71.2, 48), (77.5, 60), arrowstyle="-|>", mutation_scale=14,
                                 linewidth=1.4, color=RF))
    ax.text(57, 33.5, "Optical sense path", fontsize=8.4, color=ACCENT)
    ax.text(50.5, 28.5, "Servo and heater feedback", fontsize=8.4, color=THERMAL)

    add_dim_arrow(ax, 8, 6, 92, 6, "3 mm die", ACCENT)
    add_dim_arrow(ax, 6, 8, 6, 92, "3 mm", ACCENT)

    legend_x = 72
    ax.add_patch(
        FancyBboxPatch(
            (70.5, 10),
            22,
            16,
            boxstyle="round,pad=0.5,rounding_size=1.1",
            facecolor=PANEL_ALT,
            edgecolor=OUTLINE,
            linewidth=1.0,
        )
    )
    ax.text(72.5, 22.7, "Legend", fontsize=9.5, color=TEXT, fontweight="bold")
    ax.text(72.5, 19.0, "Cyan  = optical / readout", fontsize=8, color=ACCENT)
    ax.text(72.5, 15.7, "Amber = thermal / control", fontsize=8, color=THERMAL)
    ax.text(72.5, 12.4, "Violet = RF island", fontsize=8, color=RF)

    ax.text(50, 2.5,
            "Placement and routing remain conceptual; shown here to communicate hierarchy, not final routing density.",
            ha="center", va="center", fontsize=8.3, color=MUTED, style="italic")

    outfile = BASE / "chip_floorplan.png"
    fig.savefig(outfile, dpi=150, facecolor=BG, edgecolor="none", bbox_inches="tight")
    plt.close(fig)
    print(f"Floorplan diagram saved: {outfile}")


if __name__ == "__main__":
    generate_cross_section()
    generate_floorplan()
    print("\n[OK] Both diagrams created:")
    print("   - chip_cross_section.png")
    print("   - chip_floorplan.png")
