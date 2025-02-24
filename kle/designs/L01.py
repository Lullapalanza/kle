"""
Lumped element resonator samples for NbTiN
"""

from kle.layout.layout import KleLayout, KleLayoutElement, KleShape, create_shape, KleCutOut
from kle.layout.dot_elements import (
    get_Lazar_global_markers,
    get_dot_with_leads, DotWLeadsParams,
    get_andreev_dot_with_loop, ADParams,
)
from kle.layout.resonator_elements import get_cpw_port, get_interdigit_LC, get_L_length, LCParams, get_cpw_impedance
from kle.layout.layout_trace_routing import get_routed_cpw, get_routed_trace
from kle.layout.layout_connections import ConnectedElement


LSHEET = 111e-12
EPS = 11.7


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
PL_WIDTH = 120
PL_GAP = 2
pl, pl_length = get_routed_cpw(
    layers["SC"],
    [(0, 0),
    (100, 0), (500, 0),
    (1000, 0), (1500, 0),
    (2000, 0), (2500, 0),
    (3000, 0), (3580, 0)],
    PL_WIDTH,
    PL_GAP,
    radii=40
)

PORT_GAP = 5 * PL_GAP
PORT_WIDTH = 2 * PL_WIDTH
PORT_LEN = 120

pl.add_element(
    get_cpw_port(layers["SC"], PL_WIDTH, PL_GAP, port_gap=PORT_GAP, port_width=PORT_WIDTH, port_length=PORT_LEN)
)
pl.add_element(
    get_cpw_port(layers["SC"], PL_WIDTH, PL_GAP, port_gap=PORT_GAP, port_width=PORT_WIDTH, port_length=PORT_LEN).flip_horizontally().move(3580, 0)
)
# layout.add_element(pl.move(460 + 500 + 250, 3000))

port_imp, _ = get_cpw_impedance(PORT_WIDTH, PORT_GAP, L_sheet=LSHEET, eps=EPS)
print("port imp", port_imp)

pl_imp, pl_freq = get_cpw_impedance(PL_WIDTH, PL_GAP, L_sheet=LSHEET, eps=EPS, l=pl_length + 2*PORT_LEN)
print("Probe line impedance:", pl_imp, "freq:", pl_freq/1e9)

layout.add_element(pl.move(460 + 500 + 250, 3000))
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

Fs = [5e9, 5.5e9, 6e9, 6.5e9, 7e9]
top_Y, bot_Y = 3080 - 18, 2620 + 18
pos = [
    (1550, bot_Y), (2150, top_Y), (2750, bot_Y), (3350, top_Y),
    (3950, bot_Y)
]

for f, pos in zip(Fs, pos):
    mL, cL = get_L_length(f, 1000, width=2, L_sheet=LSHEET, N=11, eps=EPS)
    print(mL, cL)

    lcp = LCParams()
    lcp.interdigit_cap_L = cL
    lcp.interdigit_cap_N = 11
    lcp.interdigit_cap_G = 5
    lcp.interdigit_cap_W = 5

    lcp.meander_height = cL + 15
    lcp.meander_L = mL
    lcp.meander_N = 2
    lcp.cutout_width = 500

    cutout, resonator = get_interdigit_LC(layers["SC"], lcp)

    resonator.move(80, 25)
    
    if pos[1] == bot_Y:
        cutout.flip_vertically().move(0, 300)

    pl.add_element(
        cutout.move(*pos)
    )


def get_TS(layer, bond_pad_width, bond_pad_heigth, widths, length):
    extra = 80
    cutout = KleCutOut(create_shape(layer, [
        [0, 0], [2 * extra + 2 * bond_pad_width + length, 0],
        [2 * extra + 2 * bond_pad_width + length, (1 + len(widths)) * extra + len(widths) * bond_pad_heigth],
        [0, (1 + len(widths)) * extra + len(widths) * bond_pad_heigth]
    ]))
    
    bp = create_shape(layer, [
        [0, 0], [bond_pad_width, 0], [bond_pad_width, bond_pad_heigth], [0, bond_pad_heigth]
    ])
    for i, width in enumerate(widths):
        cutout.add_element(bp.get_copy().move(extra, extra + (extra + bond_pad_heigth) * i))
        cutout.add_element(bp.get_copy().move(extra + bond_pad_width + length, extra + (extra + bond_pad_heigth) * i))
        cutout.add_element(
            create_shape(layer, [
                [0,0], [length, 0], [length, width], [0, width]
            ]).move(extra + bond_pad_width, extra + (extra+bond_pad_heigth) * i + bond_pad_heigth/2)
        )
    # cutout.add_element(tss)

    return cutout


tss = get_TS(layers["SC"], 400, 200, [2, 1.5, 1], 50)

layout.add_element(tss.get_copy().move(1000, 500))
layout.add_element(tss.get_copy().flip_horizontally().move(5000, 500))
# layout.add_element(tss.get_copy().flip_vertically().move(1000, 5000))
# layout.add_element(tss.get_copy().flip_horizontally().flip_vertically().move(5000, 5000))

pl.move(0, -500)

layout.build_to_file(
    r"/home/jyrgen/Documents/PhD/design_files/L01_111pH_11_7eps_20250219_test.cif"
)
