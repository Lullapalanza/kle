"""
Current controlled resonators tests (planar, no ald like things)
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


LSHEET = 90e-12
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

# ==== PL and ports ====
PL_WIDTH = 120
PL_GAP = 2.5
pl, pl_length = get_routed_cpw(
    layers["SC"],
    [(0, 0),
    (100, 0), (500, 0),
    (1000, 0), (1500, 0),
    (2000, 0), (2500, 0),
    (3000, 0), (3980, 0)],
    PL_WIDTH,
    PL_GAP,
    radii=40
)

PORT_GAP = 6 * PL_GAP
PORT_WIDTH = 2 * PL_WIDTH
PORT_LEN = 200

pl.add_element(
    get_cpw_port(layers["SC"], PL_WIDTH, PL_GAP, port_gap=PORT_GAP, port_width=PORT_WIDTH, port_length=PORT_LEN)
)
pl.add_element(
    get_cpw_port(layers["SC"], PL_WIDTH, PL_GAP, port_gap=PORT_GAP, port_width=PORT_WIDTH, port_length=PORT_LEN).flip_horizontally().move(3980, 0)
)

port_imp, _ = get_cpw_impedance(PORT_WIDTH, PORT_GAP, L_sheet=LSHEET, eps=EPS)
print("port imp", port_imp)

pl_imp, pl_freq = get_cpw_impedance(PL_WIDTH, PL_GAP, L_sheet=LSHEET, eps=EPS, l=pl_length + 2*PORT_LEN)
print("Probe line impedance:", pl_imp, "freq:", pl_freq/1e9)

layout.add_element(pl.move(460 + 500 + 50, 3000))
# ==== PL ====


# ==== LC resonators with bias "taps" ====
Fs = [5e9, 5.5e9, 6e9, 6.5e9, 7e9]
bot_Y = 2220 + 18
delta_x = 800
pos = [
    (1300 + i * delta_x, bot_Y) for i in range(len(Fs))
]

for i, [f, pos] in enumerate(zip(Fs, pos)):
    mL, cL = get_L_length(f, 1000, width=2, L_sheet=LSHEET, N=11, eps=EPS)
    mL, cL = round(mL, 3), round(cL, 3)
    print(mL, cL)

    lcp = LCParams()
    lcp.interdigit_cap_L = cL
    lcp.interdigit_cap_N = 11
    lcp.interdigit_cap_G = 5
    lcp.interdigit_cap_W = 5

    lcp.meander_height = cL + 15
    lcp.meander_L = mL
    lcp.meander_N = 2
    lcp.cutout_width = 400
    lcp.cutout_height = 700

    cutout, resonator = get_interdigit_LC(layers["SC"], lcp)

    # resonator.move(80, 25)
    if i in [0, 1]:
        resonator.rotate_by_angle(-90)
        resonator.add_element(create_shape(layers["SC"], [
            (0, 0), (cL + 5, 0), (cL + 5, 15), (0, 15)
        ]).move(-cL - 107.5, 305))
        resonator.move(335, 350 + i + 25)
        path_left = [
            [0, 35], [-120, 35]
        ]
        path_rigth = [
           [0, 35], [120, 35]
        ]
    else:
        resonator.move(50, 520)

        if i == 3:
            _start = -65.717
        else:
            _start = -59.807
        path_left = [
            [_start, 150], [-120, 150]
        ]
        if i == 4:
            __start = -8.959
        else:
            __start = 0
        path_rigth = [
           [-160 + 27.60030 - __start, 100], [-160, 100], [-160, 35], [-10, 35], [120, 35]
        ]
    def temp(blah):
        if blah == 0:
            return -120
        if blah == 1:
            return -50
        if blah == 2:
            return -50
        else:
            return -120

    for i in range(102):
        path_left.append([temp(i%4), -10 * (1 + i//2)])
    
    path_left.append([-50, -10 * (1 + i//2) - 10])
    path_left.append([-50, -10 * (1 + i//2) - 14])

    # Left side trace
    trace, length = get_routed_trace(layers["SC"], path_left, radii=4, width_start=2, width_end=2)
    print("bias len:", length)
    cutout.add_element(trace.move(213 - cL + 0.001, 524))
    left_connector, pl_length = get_routed_cpw(
        layers["SC"],
        [
            (0, 0),
            (0, -600),
            (-100, -600),
            (-100, -800)
        ],
        width=20,
        gap=3,
        radii=40
    )
    left_connector.add_element(
        get_cpw_port(layers["SC"], 20, 3, port_gap=20, port_width=150, port_length=200).rotate_by_angle(-90).move(-100, -800)
    )
    layout.add_element(left_connector.move(pos[0] - cL + 163, 2238))

    # Right side trace
    # path_rigth = [
    #     [0, 35], [120, 35]
    # ]
    def temp(blah):
        if blah == 0:
            return 120
        if blah == 1:
            return 50
        if blah == 2:
            return 50
        else:
            return 120

    for i in range(102):
        path_rigth.append([temp(i%4), -10 * (1 + i//2)])
    
    path_rigth.append([50, -10 * (1 + i//2) - 10])
    path_rigth.append([50, -10 * (1 + i//2) - 14])

    trace, length = get_routed_trace(layers["SC"], path_rigth, radii=4, width_start=2, width_end=2)
    cutout.add_element(trace.move(237, 524))
    rigth_connector, pl_length = get_routed_cpw(
        layers["SC"],
        [
            (0, 0),
            (0, -600),
            (100, -600),
            (100, -800)
        ],
        width=20,
        gap=3,
        radii=40
    )
    imp, freq = get_cpw_impedance(30, 3, LSHEET, EPS, pl_length)
    print("BLah blah:", imp, freq/1e9, freq/2e9)
    rigth_connector.add_element(
        get_cpw_port(layers["SC"], 20, 3, port_gap=20, port_width=150, port_length=200).rotate_by_angle(-90).move(100, -800)
    )
    layout.add_element(rigth_connector.move(pos[0] + 287, 2238))


    pl.add_element(
        cutout.move(*pos)
    )
# ==== END LC resonators with bias "taps" ====


# ==== CPW with "RF ground" ====
import scipy.special as sp
import numpy as np

eps_0 = 8.8542e-12
def get_split_cpw_impedance(eq_center_width, kin_ind_width, gap, L_sheet, eps, l=100):
    kc = eq_center_width / (eq_center_width + 2 * gap)
    kbrimc = (1-kc**2)**0.5
    mu_0 = np.pi * 4e-7

    Kc = sp.ellipk(kc)
    Kbrimc = sp.ellipk(kbrimc)

    cap_per_len = 2 * eps_0 * (1+eps) * Kc/Kbrimc
    
    kl = kin_ind_width * 2 / (2 * kin_ind_width + 2 * gap)
    kbriml = (1-kl**2)**0.5
    Kl = sp.ellipk(kl)
    Kbriml = sp.ellipk(kbriml)
    ind_per_len = 0.25 * mu_0 * Kbriml/Kl

    kin_ind_width = kin_ind_width * 1e-6

    ll = ind_per_len + L_sheet/(kin_ind_width * 2)
    cl = cap_per_len
    
    imp = (ll/cl)**0.5
    freq = 1/(ll * cl)**0.5 * (1/(2e-6 * l)) 

    return imp, freq

# port_imp, freq = get_split_cpw_impedance(6, 2, 50, L_sheet=LSHEET, eps=EPS, l=1000)

Lengths = [1610, 1510, 930, 870, 800]
bot_Y = 2220 + 840
delta_x = 800
pos = [
    (1200 + i * delta_x, bot_Y) for i in range(len(Fs))
]

GAP = 50
WIRE_WIDTH = 2
CENTER_GAP = 2
BOT_GAP = 40
bot_gaps = [15, 14, 13, 12, 11]
LLENGTH = 200
extra_W = 180 + 19
extra_H = 70

for length, pos, bgap in zip(Lengths, pos, bot_gaps):
    port_imp, freq = get_split_cpw_impedance(4, 2, 50, L_sheet=LSHEET, eps=EPS, l=length)
    print("imp:", port_imp, "freq:", freq/2e9)

    width = 2 * (GAP + WIRE_WIDTH) + CENTER_GAP
    tot_length = length + bgap
    cutout = KleCutOut(create_shape(layers["SC"], [
        [-width/2, 0], [width/2 + extra_W, 0], [width/2 + extra_W, extra_H], [width/2, extra_H], [width/2, tot_length], [-width/2, tot_length]
    ]))

    # trace, _ = get_routed_trace(
    #     layers["SC"],
    #     [
    #         (-2, tot_length), (-2, tot_length-length), (-2 + LLENGTH, tot_length-length),
    #         (-2 + LLENGTH, tot_length-length + 4), (2, tot_length-length + 4), (2, tot_length)],
    #     width_start=2,
    #     width_end=2,
    #     radii=1.99
    # )
    trace, _ = get_routed_cpw(
        layers["SC"], path=[
            (0, tot_length), (0, tot_length-length), (LLENGTH-20, tot_length-length), (LLENGTH, tot_length-length)
        ], width=2, gap=2, radii=60
    )
    cutout.add_element(trace)
    cutout.add_element(create_shape(layers["SC"], [
        (0, 0), (2, 0), (2, 6), (0, 6)
    ]).move(200, bgap-3))

    
    taper_length = 48
    width = width
    cutout_1 = KleCutOut(create_shape(layers["SC"], [
        [-width/2, 0], [width/2, 0], [width/2, taper_length], [-width/2, taper_length]
    ]))

    t0, _ = get_routed_trace(layers["SC"], [
        (-2, 0), (-2, 7), (-2, 20), (-40, 20), (-53, 20)
    ], width_start=2, width_end=2, radii=4)
    # t01, _ = get_routed_trace(layers["SC"], [
    #     (-50, 30), (-50, 40), (-50, 70)
    # ], width_start=2, width_end=50, radii=4)
    # t02, _ = get_routed_trace(layers["SC"], [
    #     (-50, 10), (-50, taper_length/2), (-50, taper_length)
    # ], width_start=50, width_end=50, radii=4)
    # t0.add_element(t01)
    # t0.add_element(t02)
    # cutout_1.add_element(create_shape(layers["SC"], [
    #     (-22, 70), (-22, taper_length), (22, taper_length), (22, 70)
    # ]))
    cutout_1.add_element(t0)
    cutout_1.add_element(t0.get_copy().flip_horizontally())

    bond_trace_length = 500
    bond, trace_len = get_routed_cpw(layers["SC"], [
        (-53, 20), (-200, 20),
        (-200, 200), (-200, taper_length + bond_trace_length)
    ], 50, 3, radii=50)

    imp, freq = get_cpw_impedance(50, 3, LSHEET, EPS, trace_len)
    print("KEKW:", imp, freq/1e9, freq/2e9)
    
    bondpad = get_cpw_port(layers["SC"], 50, 3, 10, 200, 200)
    bond.add_element(bondpad.rotate_by_angle(90).move(-200, taper_length + bond_trace_length))
    cutout_1.add_element(bond)
    cutout_1.add_element(bond.get_copy().flip_horizontally())
    
    
    layout.add_element(cutout_1.move(pos[0], pos[1] + tot_length))
    layout.add_element(cutout.move(*pos))
# ==== END CPW with "RF ground" ====


layout.build_to_file(
    r"/home/jyrgen/Documents/PhD/design_files/CC00_90pH_11_7eps_20250311.gds"
)
