"""
A transmission slot line resonator FL with different things attached
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

COUPLING_WIDTH = 150
# =====


# ==== MAKE RESONATORS =====
COUPLER_WIDTHS = [
    12, 13, 14, 15,
    12, 13, 14, 15, 15
]
# 5, 5.5, 6, 6.5, 7, 7.5 GHz
RESONATOR_LEN = [
    4744, 4561, 4391, 4223, 4087, 3950
]
RESONATOR_POS = [
    (1000, 6500-11), (2000, 6500-11), (3000, 6500-11), (4000, 6500-11),
    (5000, 6500-11), (6000, 6500-11)]
RES_WIDTH_GAPS = [
    (7, 4), (7, 4), (7, 4), (7, 4), (7, 4), (7, 4)
]
# MASK = [False, False, False, False, False, False, True, True, True]
# MASK = [False for _ in range(6)]
# MASK[1] = True

for c_w, l, pos, wg in zip(COUPLER_WIDTHS, RESONATOR_LEN, RESONATOR_POS, RES_WIDTH_GAPS):
    path = [(COUPLING_WIDTH, 0), (0, 0), (0, -2000), (0, -l + COUPLING_WIDTH - 43)]
    res = get_routed_cpw(layers["sc"], path, wg[0], wg[1], radii=100, phi_step=0.5)
    res.add_element(KleShape(
        layers["sc"],
        [
            (0, 0), (wg[1], 0),
            (wg[1], -wg[0] - 2 * wg[1]), (0, -wg[0] - 2 * wg[1])
        ]
    ).move(COUPLING_WIDTH, wg[1] + wg[0]/2))
    layout.add_element(res.move(*pos))
# =====


# ==== ADD FLUX PINNING GRID ====
# layout.add_element(
#     get_grid(layers["grid"], [10 * (i+1) for i in range(699)], [10 * (i+1) for i in range(699)], 2)
# )
# ====

layout.build()
layout.save_gds("C:/Users/nbr720/Documents/PhD/design/gds_files/V03_20240524.gds")