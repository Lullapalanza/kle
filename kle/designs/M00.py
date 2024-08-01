"""
Material 00
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


layout = KleLayout(3000, 5000, ["border", "sc"])
layers = layout.get_layers()

border = KleLayoutElement("border")
# LEFT
border.add_element(KleShape(layers["sc"], [
    (0, 0), (-100, 0), (-100, 5200), (0, 5200)
]))
# TOP
border.add_element(KleShape(layers["sc"], [
    (0, 5100), (0, 5200), (3000, 5200), (3000, 5100)
]))
# RIGHT
border.add_element(KleShape(layers["sc"], [
    (0, 0), (-100, 0), (-100, 5200), (0, 5200)
]).move(3100, 0))
# BOTTOM
border.add_element(KleShape(layers["sc"], [
    (0, 5100), (0, 5200), (3000, 5200), (3000, 5100)
]).move(0, -5100))
layout.add_element(border)

# ==== MAKE PL AND PORTS ====
PL_WIDTH = 7
PL_GAP = 4
pl = get_routed_cpw(
    layers["sc"],
    [
        (0, 0), (100, 0), (500, 0),
        (1000, 0), (1500, 0), (2000, 0), (2480, 0)
    ],
    PL_WIDTH,
    PL_GAP,
    radii=40
)

PORT_GAP = 47
pl.add_element(
    get_cpw_port(layers["sc"], PL_WIDTH, PL_GAP, port_gap=PORT_GAP, port_width=120)
)
pl.add_element(
    get_cpw_port(layers["sc"], PL_WIDTH, PL_GAP, port_gap=PORT_GAP, port_width=120).flip_horizontally().move(2480, 0)
)
layout.add_element(pl.move(260, 4500))
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
    10, 10, 10, 10
]
# 5, 5.5, 6, 6.5, 7, 7.5 GHz
RESONATOR_LEN = [
    4744, 4561, 4391, 4223
]
RESONATOR_POS = [
    (600, 4500-11), (1200, 4500-11), (1800, 4500-11), (2400, 4500-11)
]
RES_WIDTH_GAPS = [
    (7, 4), (7, 4), (7, 4), (7, 4)
]
MASK = [True, True, True, True]
# MASK = [False for _ in range(6)]
# MASK[1] = True

for c_w, l, pos, wg in zip(COUPLER_WIDTHS, RESONATOR_LEN, RESONATOR_POS, RES_WIDTH_GAPS):
    l = l + 130
    path = [
        (COUPLING_WIDTH, 0), (0, 0), (0, -3000), (200, -3000), (200, -3000 + (l - 3200 - COUPLING_WIDTH))
    ]
    res = get_routed_cpw(layers["sc"], path, wg[0], wg[1], radii=100, phi_step=0.5)
    # res = get_resonator(layers["sc"], l, wg[0], wg[1], turn_length=150, y_lim=-2800)

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
#     get_grid(layers["sc"], [10, 20], [10, 20], 2)
# )
# ====

layout.build()
layout.save_gds("C:/Users/nbr720/Documents/PhD/design/gds_files/M00_20240604.gds")