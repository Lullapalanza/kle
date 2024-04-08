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
layout = KleLayout(3000, 3000, ["border", "-sc"])
layers = layout.get_layers()


# ==== MAKE PL AND PORTS ====
PL_WIDTH = 7
PL_GAP = 4
pl = get_routed_cpw(
    layers["sc"],
    [(0, 0),
    (400, 0), (500, 0),
    (2220, 0), (2320, 0),
    (2660, 0), (2680, 0)],
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
COUPLER_DISTANCE = 3
COUPLER_HEIGHT = 10
COUPLER_GAP = 6

RES_WIDTH = 2
RES_GAP = 10
# =====


# ==== MAKE RESONATORS =====
COUPLER_WIDTHS = [10, 11, 12, 13, 14, 15]
RESONATOR_LEN = [5850, 5364.11, 4920.93, 4509.63, 4180.68, 3922.35]
RESONATOR_POS = [
    (380, 2660.5), (800, 2660.5), (1220, 2660.5), (1640, 2660.5),
    (2060, 2660.5), (2480, 2660.5)]
MASK = [True, True, True, True, True, True]
# MASK = [False for _ in range(6)]
# MASK[5] = True

for c_w, l, pos, mask in zip(COUPLER_WIDTHS, RESONATOR_LEN, RESONATOR_POS, MASK):
    if mask:
        res = get_resonator(layers["sc"], l, RES_WIDTH, RES_GAP)
        coupler = get_coupler(layers["sc"], RES_WIDTH, RES_GAP, PL_WIDTH, PL_GAP, c_w, COUPLER_HEIGHT, COUPLER_GAP, COUPLER_DISTANCE)
        res.add_element(coupler)
        layout.add_element(res.move(*pos))
# =====


# ==== ADD FLUX PINNING GRID ====
# layout.add_element(
#     get_grid(layers["sc"], [10 * (i+2) for i in range(297)], [10 * (i+2) for i in range(21)], 2)
# )
# ====


layout.build()
layout.save_gds("C:/Users/nbr720/Documents/PhD/design/gds_files/R01_20240408.gds")