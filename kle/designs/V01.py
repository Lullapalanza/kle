"""
A transmission slot line resonator PL with N resonators, 4x4 chip size this time
"""
from kle.layout.layout import KleLayout, KleLayoutElement, KleShape
from kle.layout.layout_defaults import (
    get_cpw_probeline,
    get_straight_cpw_resonator,
    get_angle_cpw_resonator,
    get_cpw_port
)

from kle.layout.cpw_auto import (
    get_polygon_sides,
    get_routed_cpw,
    get_resonator,
    get_coupler,
    get_grid
)


# FAB STUFF
COMPENSATION = 0
#

layout = KleLayout(4000, 4000, ["border", "sc"])
layers = layout.get_layers()

# ==== MAKE PL AND PORTS ====
PL_WIDTH = 7 - COMPENSATION
PL_GAP = 4 + COMPENSATION
pl = get_routed_cpw(
    layers["sc"],
    [(0, 0),
    (100, 0), (500, 0),
    (1000, 0), (1500, 0),
    (2000, 0), (2500, 0),
    (3000, 0), (3480, 0)],
    PL_WIDTH,
    PL_GAP,
    radii=40
)

PORT_GAP = 47
pl.add_element(
    get_cpw_port(layers["sc"], PL_WIDTH, PL_GAP, port_gap=PORT_GAP, port_width=120)
)
pl.add_element(
    get_cpw_port(layers["sc"], PL_WIDTH, PL_GAP, port_gap=PORT_GAP, port_width=120).flip_horizontally().move(3480, 0)
)
layout.add_element(pl.move(260, 3500))
# ==========

# ==== COUPLER DEFAULTS ====
COUPLER_DISTANCE = 2 + COMPENSATION
COUPLER_HEIGHT = 10
COUPLER_GAP = 6

RES_WIDTH = 2 - COMPENSATION
RES_GAP = 10 + COMPENSATION
# =====


# ==== MAKE RESONATORS =====
COUPLER_WIDTHS = [
    12, 13, 14, 15,
    12, 13, 14, 15
]
# 5, 5.5, 6, 6.5, 7, 7.5 GHz
RESONATOR_LEN = [
    6150, 5850, 5364.11, 4900.93,
    4278.63, 3950.68, 3622.35, 3322.35
]
RESONATOR_POS = [
    (400, 3455.5), (850, 3455.5), (1300, 3455.5), (1750, 3455.5),
    (2200, 3460.5), (2650, 3460.5), (3100, 3460.5), (3550, 3460.5)]
RES_WIDTH_GAPS = [
    (7, 4), (7, 4), (7, 4), (7, 4),
    (2, 10), (2, 10), (2, 10), (2, 10)
]
MASK = [True, True, True, True, True, True, True, True]
# MASK = [False for _ in range(6)]
# MASK[1] = True

for c_w, l, pos, mask, wg in zip(COUPLER_WIDTHS, RESONATOR_LEN, RESONATOR_POS, MASK, RES_WIDTH_GAPS):
    if mask:
        res = get_resonator(layers["sc"], l, wg[0], wg[1], turn_length=150, y_lim=-2800)
        coupler = get_coupler(layers["sc"], wg[0], wg[1], PL_WIDTH, PL_GAP, c_w, COUPLER_HEIGHT, COUPLER_GAP, COUPLER_DISTANCE)
        res.add_element(coupler)
        pos = pos[0], pos[1] + 1
        layout.add_element(res.move(*pos))
# =====


# ==== ADD FLUX PINNING GRID ====
# layout.add_element(
#     get_grid(layers["sc"], [10, 20], [10, 20], 2)
# )
# ====

layout.build()
layout.save_gds("C:/Users/nbr720/Documents/PhD/design/gds_files/V01_20240430.gds")