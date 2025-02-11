"""
Lumped element resonator samples for NbTiN
"""

from kle.layout.layout import KleLayout, KleLayoutElement, KleShape, create_shape
from kle.layout.dot_elements import (
    get_Lazar_global_markers,
    get_dot_with_leads, DotWLeadsParams,
    get_andreev_dot_with_loop, ADParams,
)
from kle.layout.resonator_elements import get_cpw_port, get_interdigit_LC, get_L_length, LCParams
from kle.layout.layout_trace_routing import get_routed_cpw, get_routed_trace
from kle.layout.layout_connections import ConnectedElement


LAYER_NAMES = [
    "SC",
]

layout = KleLayout(6000, 6000, LAYER_NAMES)
layers = layout.get_layers()

# Border
border_shape = create_shape(layers["SC"], [
    [200, 200], [5800, 200], [5800, 300], [200, 300]
])
layout.add_element(border_shape)
layout.add_element(border_shape.get_copy().move(0, 5500))
layout.add_element(border_shape.get_copy().rotate_right().move(0, 6000))
layout.add_element(border_shape.get_copy().rotate_right().move(5500, 6000))
# layout.add_element(border_shape.get_copy().move(0, 5500))

# ==== PL ===
PL_WIDTH = 7
PL_GAP = 4
pl = get_routed_cpw(
    layers["SC"],
    [(0, 0),
    (100, 0), (500, 0),
    (1000, 0), (1500, 0),
    (2000, 0), (2500, 0),
    (3000, 0), (5080, 0)],
    PL_WIDTH,
    PL_GAP,
    radii=40
)

PORT_GAP = 47
pl.add_element(
    get_cpw_port(layers["SC"], PL_WIDTH, PL_GAP, port_gap=PORT_GAP, port_width=120)
)
pl.add_element(
    get_cpw_port(layers["SC"], PL_WIDTH, PL_GAP, port_gap=PORT_GAP, port_width=120).flip_horizontally().move(5080, 0)
)
layout.add_element(pl.move(460, 4500))
# ====


# Magic
# layout.add_element(create_shape(layers["SC_0"], [
#     [0, 0], [0, 6000], [6000, 6000], [6000, 0]
# ]))



# CAP
def get_LC(N, L=200, W=2, G=2):
    resonator = KleLayoutElement()
    interdigit_cap = KleLayoutElement()
    # N = 6
    # L = 200
    # W = 2
    # G = 2

    CON_EXTRA = 5

    for n in range(N):
        interdigit_cap.add_element(
            create_shape(layers["SC_0"], [
                [0, 0],
                [W, 0],
                [W, L],
                [0, L]
            ]).move(n * (W + G), (n%2)*G)
        )
    interdigit_cap.add_element(
        create_shape(layers["SC_0"], [
            [-CON_EXTRA, 0],
            [-CON_EXTRA, -W],
            [(W + G) * N - G, -W],
            [(W + G) * N - G, 0]
        ])
    )
    interdigit_cap.add_element(
        create_shape(layers["SC_0"], [
            [-CON_EXTRA, 0],
            [-CON_EXTRA, -W],
            [(W + G) * N - G, -W],
            [(W + G) * N - G, 0]
        ]).move(0, L + G + W)
    )

    path = [[0, 0], [-300, 0], [-300, 66], [-50, 66], [-50, 132], [-300, 132], [-300, 200 + 2 * G], [0, 200 + 2 * G]]
    meander = get_routed_trace(layers["SC_0"], path, width_start=W, width_end=W, radii=3)

    resonator.add_element(interdigit_cap)
    resonator.add_element(meander.move(-5, -W/2))

    return resonator

# layout.add_element(get_LC(4).move(1200, 4700))
# layout.add_element(get_LC(5).move(2200, 4700))
# layout.add_element(get_LC(6).move(3200, 4700))
# layout.add_element(get_LC(7).move(4200, 4700))
# layout.add_element(get_LC(8).move(5200, 4700))


# layout.add_element(get_LC(4, W=1.5, G=1.5).move(1200, 4100))
# layout.add_element(get_LC(5, W=1.5, G=1.5).move(2200, 4100))
# layout.add_element(get_LC(6, W=1.5, G=1.5).move(3200, 4100))
# layout.add_element(get_LC(7, W=1.5, G=1.5).move(4200, 4100))
# layout.add_element(get_LC(8, W=1.5, G=1.5).move(5200, 4100))

# layout.add_element(create_shape(layers["SC_0"], []))

mL, cL = get_L_length(5e9, 1000, width=2, L_sheet=26e-12, N=5)
print(mL, cL)


lcp = LCParams()
lcp.interdigit_cap_L = cL
lcp.meander_height = cL + 15
lcp.meander_L = mL
lcp.meander_N = 6
lcp.cutout_width = 500
cutout, resonator = get_interdigit_LC(layers["SC"], lcp)

resonator.move(200, -25)

layout.add_element(
    cutout.move(750, 3900)
)

layout.build_to_file(
    r"/home/jyrgen/Documents/PhD/design_files/L01_20250210.gds"
)
