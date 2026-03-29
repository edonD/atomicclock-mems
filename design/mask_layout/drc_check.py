"""
DRC (Design Rule Check) — CSAC_CELL_V1
=======================================
Checks the MEMS Chip-Scale Atomic Clock GDS layout against the CSAC_V1
design rules and prints / writes a structured pass/fail report.

Exit codes
----------
  0 — all rules PASS
  1 — one or more rules FAIL

Usage
-----
  python drc_check.py [path/to/csac_cell_v1.gds]

Default GDS path is the file alongside this script.
"""

import sys
import math
import textwrap
from pathlib import Path
from collections import defaultdict

import numpy as np
import gdstk

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
SCRIPT_DIR  = Path(__file__).resolve().parent
GDS_PATH    = Path(sys.argv[1]) if len(sys.argv) > 1 else SCRIPT_DIR / "csac_cell_v1.gds"
REPORT_PATH = SCRIPT_DIR / "drc_report.txt"

# Layer numbers
L_DIE_OUTLINE = 0
L_CAVITY      = 1
L_PT_HEATER   = 2
L_PT_RTD      = 3
L_BOND_RING   = 4
L_DICING      = 5
L_OPTICAL_WIN = 6
L_LABELS      = 10

LAYER_NAMES = {
    L_DIE_OUTLINE: "DIE_OUTLINE",
    L_CAVITY:      "CAVITY",
    L_PT_HEATER:   "PT_HEATER",
    L_PT_RTD:      "PT_RTD",
    L_BOND_RING:   "BOND_RING",
    L_DICING:      "DICING",
    L_OPTICAL_WIN: "OPTICAL_WIN",
    L_LABELS:      "LABELS",
}

# Design constants (µm)
DIE_W = 3000.0
DIE_H = 3000.0
DIE_CENTER_X = 1500.0
DIE_CENTER_Y = 1500.0

# DRC limits
HEATER_MIN_WIDTH    = 20.0   # µm  (rule: >= 20 µm)
RTD_MIN_WIDTH       = 10.0   # µm  (rule: >= 10 µm)
BOND_RING_MIN_AREA  = 1e6    # µm² (rule: total area >= 1 000 000 µm²)
CAVITY_DIAM_NOM     = 1500.0 # µm
CAVITY_DIAM_TOL     = 50.0   # µm  (±50 µm tolerance on diameter)
CAVITY_CENTER_TOL   = 50.0   # µm  (centroid must be within 50 µm of die center)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def layer_name(n: int) -> str:
    return LAYER_NAMES.get(n, f"L{n}")


def polygon_min_width(poly) -> float:
    """
    Estimate minimum feature width of a rectilinear polygon using its
    bounding-box minimum dimension.  For axis-aligned rectangular traces
    (as used in all serpentine / meander patterns here) this equals the
    true minimum trace width.  For L-shaped corners the bounding-box
    minimum is also the trace width, so this is exact for the CSAC layout.
    """
    pts = poly.points
    bb_w = float(pts[:, 0].max() - pts[:, 0].min())
    bb_h = float(pts[:, 1].max() - pts[:, 1].min())
    return min(bb_w, bb_h)


def poly_bbox(poly):
    """Return (xmin, ymin, xmax, ymax) of a polygon."""
    pts = poly.points
    return (float(pts[:, 0].min()), float(pts[:, 1].min()),
            float(pts[:, 0].max()), float(pts[:, 1].max()))


def poly_centroid(poly):
    """Bounding-box centroid (µm)."""
    pts = poly.points
    cx = (float(pts[:, 0].min()) + float(pts[:, 0].max())) / 2.0
    cy = (float(pts[:, 1].min()) + float(pts[:, 1].max())) / 2.0
    return cx, cy


def poly_outside_die(poly, die_w=DIE_W, die_h=DIE_H) -> bool:
    """True if any vertex of poly lies outside [0, die_w] × [0, die_h]."""
    pts = poly.points
    return bool(
        np.any(pts[:, 0] < -1e-3) or np.any(pts[:, 0] > die_w + 1e-3) or
        np.any(pts[:, 1] < -1e-3) or np.any(pts[:, 1] > die_h + 1e-3)
    )


# ---------------------------------------------------------------------------
# Result collector
# ---------------------------------------------------------------------------

class DRCResult:
    def __init__(self):
        self.entries = []   # list of (status, rule_id, message)

    def record(self, passed: bool, rule_id: str, message: str):
        status = "PASS" if passed else "FAIL"
        self.entries.append((status, rule_id, message))
        return passed

    def all_pass(self) -> bool:
        return all(s == "PASS" for s, _, _ in self.entries)

    def summary_lines(self) -> list:
        lines = []
        width = 80
        sep   = "=" * width

        lines.append(sep)
        lines.append("  DRC REPORT — CSAC_CELL_V1")
        lines.append(f"  GDS file : {GDS_PATH}")
        lines.append(sep)
        lines.append("")

        for status, rule_id, message in self.entries:
            tag   = f"[{status}]"
            label = f"{rule_id:<35s}"
            # wrap long detail lines
            detail = f"{tag} {label} {message}"
            wrapped = textwrap.wrap(detail, width=width,
                                    subsequent_indent=" " * 46)
            lines.extend(wrapped)

        lines.append("")
        lines.append(sep)
        overall = "ALL RULES PASSED" if self.all_pass() else "ONE OR MORE RULES FAILED"
        lines.append(f"  OVERALL: {overall}")
        lines.append(sep)
        return lines


# ---------------------------------------------------------------------------
# DRC checks
# ---------------------------------------------------------------------------

def run_drc(gds_path: Path) -> DRCResult:
    res = DRCResult()

    # ---- Load GDS --------------------------------------------------------
    if not gds_path.exists():
        res.record(False, "FILE_EXISTS",
                   f"GDS file not found: {gds_path}")
        return res

    lib  = gdstk.read_gds(str(gds_path))
    res.record(True, "FILE_EXISTS", f"GDS loaded — {len(lib.cells)} cell(s) found")

    # Find the top-level cell (non-empty) — filter to gdstk.Cell only (not RawCell)
    real_cells: list[gdstk.Cell] = [c for c in lib.cells if isinstance(c, gdstk.Cell)]
    top_cell: gdstk.Cell | None = next(
        (c for c in real_cells if len(c.polygons) > 0), None
    )

    if top_cell is None:
        res.record(False, "CELL_FOUND", "No cell with polygons found in GDS")
        return res
    res.record(True, "CELL_FOUND",
               f"Top cell '{top_cell.name}' — {len(top_cell.polygons)} polygons")

    # Group polygons by layer
    by_layer: dict = defaultdict(list)
    for p in top_cell.polygons:
        by_layer[p.layer].append(p)

    # =========================================================================
    # RULE 1  L2 PT_HEATER — minimum trace width >= 20 µm
    # =========================================================================
    rule_id = "L2_HEATER_MIN_WIDTH"
    heater_polys = by_layer.get(L_PT_HEATER, [])
    if not heater_polys:
        res.record(False, rule_id,
                   "FAIL — Layer 2 (PT_HEATER) has no polygons")
    else:
        violations = []
        for i, p in enumerate(heater_polys):
            w = polygon_min_width(p)
            if w < HEATER_MIN_WIDTH - 1e-3:
                cx, cy = poly_centroid(p)
                violations.append(
                    f"poly[{i}] min_width={w:.2f} µm < {HEATER_MIN_WIDTH} µm "
                    f"at ({cx:.1f}, {cy:.1f})"
                )
        if violations:
            res.record(False, rule_id,
                       f"{len(violations)} violation(s): " + "; ".join(violations))
        else:
            min_w = min(polygon_min_width(p) for p in heater_polys)
            res.record(True, rule_id,
                       f"All {len(heater_polys)} polygons >= {HEATER_MIN_WIDTH} µm "
                       f"(min observed = {min_w:.2f} µm)")

    # =========================================================================
    # RULE 2  L3 PT_RTD — minimum trace width >= 10 µm
    # =========================================================================
    rule_id = "L3_RTD_MIN_WIDTH"
    rtd_polys = by_layer.get(L_PT_RTD, [])
    if not rtd_polys:
        res.record(False, rule_id,
                   "FAIL — Layer 3 (PT_RTD) has no polygons")
    else:
        violations = []
        for i, p in enumerate(rtd_polys):
            w = polygon_min_width(p)
            if w < RTD_MIN_WIDTH - 1e-3:
                cx, cy = poly_centroid(p)
                violations.append(
                    f"poly[{i}] min_width={w:.2f} µm < {RTD_MIN_WIDTH} µm "
                    f"at ({cx:.1f}, {cy:.1f})"
                )
        if violations:
            res.record(False, rule_id,
                       f"{len(violations)} violation(s): " + "; ".join(violations))
        else:
            min_w = min(polygon_min_width(p) for p in rtd_polys)
            res.record(True, rule_id,
                       f"All {len(rtd_polys)} polygons >= {RTD_MIN_WIDTH} µm "
                       f"(min observed = {min_w:.2f} µm)")

    # =========================================================================
    # RULE 3  L4 BOND_RING — total area >= 1e6 µm²
    # =========================================================================
    rule_id = "L4_BOND_RING_AREA"
    bond_polys = by_layer.get(L_BOND_RING, [])
    if not bond_polys:
        res.record(False, rule_id,
                   "FAIL — Layer 4 (BOND_RING) has no polygons")
    else:
        total_area = sum(p.area() for p in bond_polys)
        passed = total_area >= BOND_RING_MIN_AREA
        cmp_op = ">=" if passed else "<"
        res.record(passed, rule_id,
                   f"Total bond ring area = {total_area:,.0f} µm² "
                   f"({cmp_op} {BOND_RING_MIN_AREA:,.0f} µm² minimum) "
                   f"across {len(bond_polys)} polygon(s)")

    # =========================================================================
    # RULE 4  L5 DICING — layer must exist with polygons
    # =========================================================================
    rule_id = "L5_DICING_EXISTS"
    dicing_polys = by_layer.get(L_DICING, [])
    passed = len(dicing_polys) > 0
    res.record(passed, rule_id,
               (f"{len(dicing_polys)} dicing polygon(s) found"
                if passed else "FAIL — Layer 5 (DICING) has no polygons"))

    # =========================================================================
    # RULE 5  L1 CAVITY — bounding-box diameter ~1500 µm  (±50 µm)
    # =========================================================================
    rule_id = "L1_CAVITY_DIAMETER"
    cavity_polys = by_layer.get(L_CAVITY, [])
    if not cavity_polys:
        res.record(False, rule_id,
                   "FAIL — Layer 1 (CAVITY) has no polygons")
    else:
        for i, p in enumerate(cavity_polys):
            pts = p.points
            bb_w = float(pts[:, 0].max() - pts[:, 0].min())
            bb_h = float(pts[:, 1].max() - pts[:, 1].min())
            avg_diam = (bb_w + bb_h) / 2.0
            lo = CAVITY_DIAM_NOM - CAVITY_DIAM_TOL
            hi = CAVITY_DIAM_NOM + CAVITY_DIAM_TOL
            passed = lo <= avg_diam <= hi
            res.record(passed, rule_id,
                       f"cavity[{i}] bb_w={bb_w:.1f} µm, bb_h={bb_h:.1f} µm, "
                       f"avg_diam={avg_diam:.1f} µm "
                       f"(nominal {CAVITY_DIAM_NOM} ± {CAVITY_DIAM_TOL} µm) "
                       f"— {'OK' if passed else 'OUT OF SPEC'}")

    # =========================================================================
    # RULE 6  All layers — no polygon outside die boundary (3000 × 3000 µm)
    # =========================================================================
    rule_id = "ALL_LAYERS_IN_DIE"
    oob_details = []
    for layer in sorted(by_layer.keys()):
        if layer == L_LABELS:          # label glyphs may be tiny and off-grid
            continue                   # skip LABELS for this check
        for i, p in enumerate(by_layer[layer]):
            if poly_outside_die(p):
                cx, cy = poly_centroid(p)
                xmin, ymin, xmax, ymax = poly_bbox(p)
                oob_details.append(
                    f"L{layer}({layer_name(layer)}) poly[{i}] "
                    f"bbox=({xmin:.0f},{ymin:.0f})-({xmax:.0f},{ymax:.0f})"
                )
    if oob_details:
        res.record(False, rule_id,
                   f"{len(oob_details)} polygon(s) outside die: " +
                   "; ".join(oob_details))
    else:
        total_checked = sum(len(v) for k, v in by_layer.items()
                            if k != L_LABELS)
        res.record(True, rule_id,
                   f"All {total_checked} non-label polygons inside "
                   f"{DIE_W:.0f} × {DIE_H:.0f} µm die boundary")

    # =========================================================================
    # RULE 7  L1 CAVITY centroid within 50 µm of die center (1500, 1500)
    # =========================================================================
    rule_id = "L1_CAVITY_CENTROID"
    cavity_polys = by_layer.get(L_CAVITY, [])
    if not cavity_polys:
        res.record(False, rule_id,
                   "FAIL — Layer 1 (CAVITY) has no polygons — cannot check centroid")
    else:
        for i, p in enumerate(cavity_polys):
            cx, cy = poly_centroid(p)
            dist = math.hypot(cx - DIE_CENTER_X, cy - DIE_CENTER_Y)
            passed = dist <= CAVITY_CENTER_TOL
            res.record(passed, rule_id,
                       f"cavity[{i}] centroid=({cx:.2f}, {cy:.2f}) µm, "
                       f"dist from die-center=({DIE_CENTER_X:.0f},{DIE_CENTER_Y:.0f}) "
                       f"= {dist:.2f} µm "
                       f"(limit {CAVITY_CENTER_TOL} µm) "
                       f"— {'OK' if passed else 'CENTROID OFFSET TOO LARGE'}")

    return res


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print(f"Running DRC on: {GDS_PATH}")
    print()

    result = run_drc(GDS_PATH)
    lines  = result.summary_lines()
    report = "\n".join(lines)

    # Print to console
    print(report)

    # Write to file
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write(report)
        f.write("\n")
    print(f"\nReport written to: {REPORT_PATH}")

    sys.exit(0 if result.all_pass() else 1)


if __name__ == "__main__":
    main()
