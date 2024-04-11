"""
A transmission slot line resonator PL with N resonators
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
COMPENSATION = 0.1
#

layout = KleLayout(3000, 3000, ["border", "-sc"])
layers = layout.get_layers()


# ==== MAKE PL AND PORTS ====
PL_WIDTH = 7 - COMPENSATION
PL_GAP = 4 + COMPENSATION
pl = get_routed_cpw(
    layers["sc"],
    [(0, 0),
    (100, 0), (500, 0),
    (1000, 0), (1500, 0),
    (2000, 0), (2680, 0)],
    PL_WIDTH,
    PL_GAP,
    radii=40
)

PORT_GAP = 47
pl.add_element(
    get_cpw_port(layers["sc"], PL_WIDTH, PL_GAP, port_gap=PORT_GAP, port_width=80)
)
pl.add_element(
    get_cpw_port(layers["sc"], PL_WIDTH, PL_GAP, port_gap=PORT_GAP, port_width=80).flip_horizontally().move(2680, 0)
)
layout.add_element(pl.move(160, 2700))
# ==========

# ==== COUPLER DEFAULTS ====
COUPLER_DISTANCE = 2 + COMPENSATION
COUPLER_HEIGHT = 10
COUPLER_GAP = 6

RES_WIDTH = 2 - COMPENSATION
RES_GAP = 10 + COMPENSATION
# =====


# ==== MAKE RESONATORS =====
COUPLER_WIDTHS = [10, 11, 12, 13, 14, 15]
# 5, 5.5, 6, 6.5, 7, 7.5 GHz
RESONATOR_LEN = [5850, 5364.11, 4900.93, 4278.63, 4000.68, 3722.35]
RESONATOR_POS = [
    (380, 2661.5), (800, 2661.5), (1220, 2661.5), (1640, 2661.5),
    (2060, 2661.5), (2600, 2661.5)]
MASK = [True, True, True, True, True, True]
# MASK = [False for _ in range(6)]
# MASK[1] = True

for c_w, l, pos, mask in zip(COUPLER_WIDTHS, RESONATOR_LEN, RESONATOR_POS, MASK):
    if mask:
        res = get_resonator(layers["sc"], l, RES_WIDTH, RES_GAP)
        coupler = get_coupler(layers["sc"], RES_WIDTH, RES_GAP, PL_WIDTH, PL_GAP, c_w, COUPLER_HEIGHT, COUPLER_GAP, COUPLER_DISTANCE)
        res.add_element(coupler)
        pos = pos[0], pos[1] + 0.049
        layout.add_element(res.move(*pos))
# =====


# ==== ADD FLUX PINNING GRID ====
# layout.add_element(
#     get_grid(layers["sc"], [10, 20], [10, 20], 2)
# )
# ====


layout.build()
layout.save_gds("C:/Users/nbr720/Documents/PhD/design/gds_files/R00_20240411.gds")