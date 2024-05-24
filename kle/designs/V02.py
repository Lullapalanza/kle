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


layout = KleLayout(7000, 7000, ["border", "sc", "grid"])
layers = layout.get_layers()

# ==== MAKE PL AND PORTS ====
PL_WIDTH = 7
PL_GAP = 4
pl = get_routed_cpw(
    layers["sc"],
    [(0, 0),
    (100, 0), (500, 0),
    (1000, 0), (1500, 0),
    (2000, 0), (2500, 0),
    (3000, 0), (6480, 0)],
    PL_WIDTH,
    PL_GAP,
    radii=40
)

PORT_GAP = 47
pl.add_element(
    get_cpw_port(layers["sc"], PL_WIDTH, PL_GAP, port_gap=PORT_GAP, port_width=120)
)
pl.add_element(
    get_cpw_port(layers["sc"], PL_WIDTH, PL_GAP, port_gap=PORT_GAP, port_width=120).flip_horizontally().move(6480, 0)
)
layout.add_element(pl.move(260, 6500))
# ==========

# ==== COUPLER DEFAULTS ====
COUPLER_DISTANCE = 2
COUPLER_HEIGHT = 10
COUPLER_GAP = 6

RES_WIDTH = 2
RES_GAP = 10
# =====


# ==== MAKE RESONATORS =====
COUPLER_WIDTHS = [
    12, 13, 14, 15,
    12, 13, 14, 15, 15
]
# 5, 5.5, 6, 6.5, 7, 7.5 GHz
RESONATOR_LEN = [
    7475, 6649, 5953, 5411, 4960, 4579,
    4252, 3968, 3720
]
RESONATOR_POS = [
    (800, 6455.5), (1475, 6455.5), (2150, 6455.5), (2825, 6455.5),
    (3500, 6460.5), (4175, 6460.5), (4850, 6460.5), (5525, 6460.5), (6200, 6460.5)]
RES_WIDTH_GAPS = [
    (7, 4), (7, 4), (7, 4), (7, 4),
    (2, 10), (2, 10), (2, 10), (2, 10), (2, 10)
]
MASK = [True, True, True, True, True, True, True, True, True]
# MASK = [False for _ in range(6)]
# MASK[1] = True

for c_w, l, pos, mask, wg in zip(COUPLER_WIDTHS, RESONATOR_LEN, RESONATOR_POS, MASK, RES_WIDTH_GAPS):
    if mask:
        res = get_resonator(layers["sc"], l, wg[0], wg[1], turn_length=150, y_lim=-5800)
        coupler = get_coupler(layers["sc"], wg[0], wg[1], PL_WIDTH, PL_GAP, c_w, COUPLER_HEIGHT, COUPLER_GAP, COUPLER_DISTANCE)
        res.add_element(coupler)
        pos = pos[0], pos[1] + 1
        layout.add_element(res.move(*pos))
# =====


# ==== ADD FLUX PINNING GRID ====
layout.add_element(
    get_grid(layers["grid"], [10 * (i+1) for i in range(699)], [10 * (i+1) for i in range(699)], 2)
)
# ====

layout.build()
layout.save_gds("C:/Users/nbr720/Documents/PhD/design/gds_files/V02_20240503_grid.gds")