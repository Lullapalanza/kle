"""
Ansys test file
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


layout = KleLayout(600, 5000, ["-sc"])
layers = layout.get_layers()

# ==== MAKE PL AND PORTS ====
PL_WIDTH = 3.5
PL_GAP = 2
pl = get_routed_cpw(
    layers["sc"],
    [
        (0, 0),
        (600, 0)
    ],
    PL_WIDTH,
    PL_GAP,
    radii=40
)


layout.add_element(pl.move(0, 4400))
# ==========

# ==== COUPLER DEFAULTS ====
COUPLER_DISTANCE = 2
COUPLER_HEIGHT = 15
COUPLER_GAP = 7
COUPLER_WIDTH = 30

RES_WIDTH = 2
RES_GAP = 10

COUPLING_WIDTH = 250
RES_LENGTH = 4400

# path = [
#     (COUPLING_WIDTH, 0), (0, 0), (0, -3000),
#     # (200, -3000), (200, -2800),  (200, -3000 + (RES_LENGTH - 3200))
#     (0, -RES_LENGTH + COUPLING_WIDTH)
# ]
# res = get_routed_cpw(
#     layers["sc"],
#     path,
#     RES_WIDTH,
#     RES_GAP,
#     radii=100,
#     phi_step=0.5
# )
# res.add_element(KleShape(
#     layers["sc"],
#     [
#         (0, 0), (RES_WIDTH + 2 * RES_GAP, 0),
#         (RES_WIDTH + 2 * RES_GAP, -RES_GAP), (0, -RES_GAP)
#     ]
# ).move(-RES_GAP - RES_WIDTH/2, -RES_LENGTH + COUPLING_WIDTH))

# layout.add_element(res.move(200, 4381))



RES_LENGTH = 3900
path = [(0, 0), (0, -300), (0, -RES_LENGTH)]
res = get_routed_cpw(
    layers["sc"],
    path,
    RES_WIDTH,
    RES_GAP
)
coupler = get_coupler(
    layers["sc"], RES_WIDTH, RES_GAP, PL_WIDTH, PL_GAP, COUPLER_WIDTH, COUPLER_HEIGHT, COUPLER_GAP, COUPLER_DISTANCE)
res.add_element(coupler)

layout.add_element(res.move(300, 4346.5))


layout.build()
layout.save_gds("C:/Users/nbr720/Documents/PhD/design/gds_files/A01_20240524.dxf")