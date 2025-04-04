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




def get_cap(C):
    L, W, G, N = 80, 5, 5, 12
    L = C / ((EPS + 1) * ((N-3) * 4.409e-18 + 9.92e-18))
    
    interdigit_cap = KleLayoutElement()
    for n in range(N):
        interdigit_cap.add_element(
            create_shape(layers["SC"], [
                [0, 0],
                [W, 0],
                [W, L],
                [0, L]
            ]).move(n * (W + G), (n%2)*G)
        )
    end_conn = create_shape(layers["SC"], [
        [-0, 0],
        [-0, -W],
        [(W + G) * N - G, -W],
        [(W + G) * N - G, 0]
    ])
    interdigit_cap.add_element(end_conn)
    interdigit_cap.add_element(end_conn.get_copy().move(0, L + G + W))

    from kle.layout.resonator_elements import get_C

    # print("Cap:", get_C(EPS, L, N)*1e12, "pF")

    return interdigit_cap, L


# ==== LC resonators with bias "taps" ====
Fs = [5e9, 5.5e9, 6e9, 6.5e9]
bot_Y = 2220 + 18 - 700
delta_x = 800
pos = [
    (1300 + i * delta_x, bot_Y) for i in range(len(Fs))
]

# for i, [f, pos] in enumerate(zip(Fs, pos)):
#     # Get L and C
#     Z0 = 1000
#     C = 1/(2 * 3.14 * f * Z0)
#     L = C * Z0**2

#     Cgnd = C*2
#     meander_len = L * 2 / LSHEET
#     print("L:", L, "C:", C, "len:", meander_len)
    
#     cutout = KleCutOut(create_shape(layers["SC"], [(0, 0), (500, 0), (500, -2000), (0, -2000)]).move(-5, 30))

#     cap_to_gnd, capL = get_cap(Cgnd)
#     cap_to_gnd.rotate_right()

#     cutout.add_element(cap_to_gnd)
#     cutout.add_element(cap_to_gnd.get_copy().move(0, -300))

#     meander_changed_len = (meander_len - 185 - 115)/2
#     meander_path = [
#         (0, 0), (10, 0), (meander_changed_len, 0), (meander_changed_len, 185 + 115), (0, 185 + 115)
#     ]
#     routed_meander, _len = get_routed_trace(layers["SC"], meander_path, width_start=2, width_end=2, radii=4)
#     cutout.add_element(routed_meander.move(capL + 10, -185-115*1.5))

#     symmetry_offset = 320 - L - meander_changed_len
#     symmetry_path = [
#         (0, 0), (10, 0), (symmetry_offset, 0), (symmetry_offset, -250)
#     ]
#     def temp(blah):
#         if blah == 0:
#             return symmetry_offset
#         if blah == 1:
#             return symmetry_offset-120
#         if blah == 2:
#             return symmetry_offset-120
#         else:
#             return symmetry_offset

#     for i in range(59):
#         symmetry_path.append([temp(i%4), -260 -50 * (1 + i//2)])
#     symmetry_path.append([temp(i%4), -260 -50 * (1 + i//2) - 2.5])
    
#     symmetry_connection, _len = get_routed_trace(layers["SC"], symmetry_path, width_start=2, width_end=2, radii=4)
#     cutout.add_element(symmetry_connection.move(meander_changed_len + capL + 10.999, -115 - 185/2))
#     print("Gate len:", _len)

#     gnd_path = [(-25, 0), (-25, -10)]
#     def temp(blah):
#         if blah == 0:
#             return 0
#         if blah == 1:
#             return 0 + 120
#         if blah == 2:
#             return 0 + 120
#         else:
#             return 0

#     for i in range(59):
#         gnd_path.append([temp(i%4), -50 -50 * (1 + i//2)])
#     gnd_path.append([temp(i%4), -50 -50 * (1 + i//2)-5])

#     gnd_conn, _len = get_routed_trace(layers["SC"], gnd_path, width_start=2, width_end=2, radii=4)
#     cutout.add_element(gnd_conn.move(90, -185 - 115*2))

#     cutout.move(*pos)
#     layout.add_element(cutout)

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
    lcp.meander_N = 0
    lcp.cutout_width = 400
    lcp.cutout_height = 1400

    cutout, resonator = get_interdigit_LC(layers["SC"], lcp)

    # resonator.move(80, 25)
    # if i in [0, 1]:
    resonator.rotate_by_angle(-90)
    resonator.add_element(create_shape(layers["SC"], [
        (0, 0), (cL + 5, 0), (cL + 5, 15), (0, 15)
    ]).move(-cL - 107.5, 305))
    resonator.move(335, 350 + 700 + i + 25)
    if i in [2, 3]:
        resonator.move(0, - 50*i)
    path_left = [
        [0, 35], [-120, 35]
    ]
    path_rigth = [
        [0, 35], [120, 35]
    ]
    # else:
    #     resonator.move(50, 520)

    #     if i == 3:
    #         _start = -65.717
    #     else:
    #         _start = -59.807
    #     path_left = [
    #         [_start, 150], [-120, 150]
    #     ]
    #     if i == 4:
    #         __start = -8.959
    #     else:
    #         __start = 0
    #     path_rigth = [
    #        [-160 + 27.60030 - __start, 100], [-160, 100], [-160, 35], [-10, 35], [120, 35]
    #     ]
    def temp(blah):
        if blah == 0:
            return -120
        if blah == 1:
            return -50
        if blah == 2:
            return -50
        else:
            return -120

    for j in range(66):
        path_left.append([temp(j%4), -35 * (1 + j//2)])
    
    path_left.append([-50, -35 * (1 + j//2) - 10])
    path_left.append([-50, -35 * (1 + j//2) - 14 - 55])

    # Left side trace
    trace, length = get_routed_trace(layers["SC"], path_left, radii=10, width_start=2, width_end=2, phi_step=0.1)
    # print("bias len:", length)
    if i in [0, 1, 4]:
        cutout.add_element(trace.move(213 - cL + 0.001, 524 + 700))
    # left_connector, pl_length = get_routed_cpw(
    #     layers["SC"],
    #     [
    #         (0, 0),
    #         (0, -600),
    #         (-100, -600),
    #         (-100, -800)
    #     ],
    #     width=20,
    #     gap=3,
    #     radii=40
    # )
    # left_connector.add_element(
    #     get_cpw_port(layers["SC"], 20, 3, port_gap=20, port_width=150, port_length=200).rotate_by_angle(-90).move(-100, -800)
    # )
    # layout.add_element(left_connector.move(pos[0] - cL + 163, 2238))

    # Right side trace
    if i == 0:
        extra_y = -2.622
        extra_x = -6.5
    elif i == 1:
        extra_y = -4.144
        extra_x = -4.5
    elif i == 3:
        extra_y = -6.024
        extra_x = 0
    elif i == 4:
        extra_y = -6.549
        extra_x = 1.5

    path_rigth = [
        [-33.3 + extra_x, 795 - mL/2 + extra_y], [-33.3 + extra_x, 380], [120, 380]
    ]
    def temp(blah):
        if blah == 0:
            return 120
        if blah == 1:
            return 50
        if blah == 2:
            return 50
        else:
            return 120

    for j in range(50):
        path_rigth.append([temp(j%4), 380 -35 * (1 + j//2)])
    
    path_rigth.append([50, 380-35 * (1 + j//2) - 10])
    path_rigth.append([50, 380-35 * (1 + j//2) - 29])

    trace, length = get_routed_trace(layers["SC"], path_rigth, radii=10, width_start=2, width_end=2, phi_step=0.1)
    
    if i in [0, 1, 4]:
        cutout.add_element(trace.move(237, 524))
        
        rigth_connector, pl_length = get_routed_cpw(
            layers["SC"],
            [
                (0, 0),
                (0, -600),
                (0, -800)
            ],
            width=4,
            gap=80,
            radii=40
        )
        imp, freq = get_cpw_impedance(30, 3, LSHEET, EPS, pl_length)
        print("BLah blah:", imp, freq/1e9, freq/2e9)
        rigth_connector.add_element(
            get_cpw_port(layers["SC"], 4, 80, port_gap=80, port_width=250, port_length=200).rotate_by_angle(-90).move(0, -800)
        )
        layout.add_element(rigth_connector.move(pos[0] + 287, 2238-700))


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

Lengths = [1150, 1040, 900, 790, 700]
bot_Y = 2220 + 840
delta_x = 800
pos = [
    (1200 + i * delta_x, bot_Y) for i in range(len(Lengths))
]

GAP = 50
WIRE_WIDTH = 2
CENTER_GAP = 2
BOT_GAP = 40
bot_gaps = [50+3, 40 + 3, 100 + 3, 30+3, 20+3]
CPW_GAPS = [100, 90, 80, 60, 50]
LLENGTH = 200
extra_W = 180 + 19
extra_H = 70

for length, pos, bgap, cgap in zip(Lengths, pos, bot_gaps, CPW_GAPS):

    GAP = cgap

    width = 2 * (GAP + WIRE_WIDTH) + CENTER_GAP
    tot_length = length + bgap

    cpw_path = [
        (0, tot_length), (0, tot_length-length), (LLENGTH-20, tot_length-length), (LLENGTH, tot_length-length)
    ]

    hole_path = cpw_path[:-2] + [(LLENGTH + GAP, tot_length-length)]
    cpw_hole, _ = get_routed_trace(layers["SC"], hole_path, width_start=width, width_end=width, radii=180, phi_step=0.1)

    cutout = KleCutOut(cpw_hole)

    # trace, _ = get_routed_trace(
    #     layers["SC"],
    #     [
    #         (-2, tot_length), (-2, tot_length-length), (-2 + LLENGTH, tot_length-length),
    #         (-2 + LLENGTH, tot_length-length + 4), (2, tot_length-length + 4), (2, tot_length)],
    #     width_start=2,
    #     width_end=2,
    #     radii=1.99
    # )
    trace, cpw_len_ = get_routed_cpw(
        layers["SC"], path=[
            (0, tot_length), (0, tot_length-length), (LLENGTH-20, tot_length-length), (LLENGTH, tot_length-length)
        ], width=2, gap=2, radii=180, phi_step=0.1
    )
    port_imp, freq = get_split_cpw_impedance(4, 2, cgap, L_sheet=LSHEET, eps=EPS, l=cpw_len_)
    print("imp:", port_imp, "freq:", freq/2e9, "len:", cpw_len_)

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
        (-2, 0), (-2, 7), (-2, 20), (-40, 20), (-GAP - WIRE_WIDTH - CENTER_GAP/2, 20)
    ], width_start=2, width_end=2, radii=4)
    cutout_1.add_element(t0)
    cutout_1.add_element(t0.get_copy().flip_horizontally())

    bond_trace_length = 500
    bond, trace_len = get_routed_cpw(layers["SC"], [
        (-53, 20), (-200, 20),
        (-200, 200), (-200, taper_length + bond_trace_length)
    ], 50, 3, radii=50)

    imp, freq = get_cpw_impedance(50, 3, LSHEET, EPS, trace_len)
    # print("KEKW:", imp, freq/1e9, freq/2e9)
    
    bondpad = get_cpw_port(layers["SC"], 250, 3, 3, 250, 1000)
    
    # bondpad.add_element(create_shape(layers["SC"], [
    #     (), (), (), 
    # ]))
    # bond.add_element(bondpad.rotate_by_angle(90).move(-200, taper_length + bond_trace_length))
    cutout_1.add_element(bondpad.rotate_by_angle(90).move(-width/2 - 250/2, taper_length))
    cutout_1.add_element(bondpad.get_copy().flip_horizontally())
    
    
    layout.add_element(cutout_1.move(pos[0], pos[1] + tot_length))
    layout.add_element(cutout.move(*pos))

# ==== END CPW with "RF ground" ====


def get_tapped_cpw():
    GAP = 200
    WIDTH = 3
    radii=300
    straight_len = 1500

    cpw_path = [(0, 0), (500, 0), (500, -straight_len), (10, -straight_len), (0, -straight_len)]
    cpw_hole, _ = get_routed_trace(layers["SC"], cpw_path, width_start=2*GAP + WIDTH, width_end=2*GAP + WIDTH, radii=radii, phi_step=0.1)
    

    cpw = KleCutOut(cpw_hole)
    cpw_center, center_len = get_routed_trace(layers["SC"], cpw_path, width_start=WIDTH, width_end=WIDTH, radii=radii, phi_step=0.1)
    
    cpw.add_element(cpw_center)

    imp, f = get_cpw_impedance(WIDTH, GAP, LSHEET, EPS, l=center_len, lambda_frac=1)
    print("0.5 lambda", get_cpw_impedance(WIDTH, GAP, LSHEET, EPS, l=center_len, lambda_frac=0.5))
    print(center_len, imp, f/1e9)

    one_sixth = center_len/6

    cpw.add_element(
        create_shape(layers["SC"], [(0, 0), [GAP, 0], [GAP, WIDTH], [0, WIDTH]]).move(500 + WIDTH/2, -straight_len/2 + one_sixth - WIDTH/2)
    )
    cpw.add_element(
        get_cpw_port(layers["SC"], 3, 3, 10, 250, 250, 250).flip_horizontally().move(500 + WIDTH/2 + GAP, -straight_len/2 + one_sixth)
    )
    cpw.add_element(
        create_shape(layers["SC"], [(0, 0), [GAP, 0], [GAP, WIDTH], [0, WIDTH]]).move(500 + WIDTH/2, -straight_len/2 - one_sixth - WIDTH/2)
    )
    cpw.add_element(
        get_cpw_port(layers["SC"], 3, 3, 10, 250, 250, 250).flip_horizontally().move(500 + WIDTH/2 + GAP, -straight_len/2 - one_sixth)
    )
    cpw.add_element(create_shape(layers["SC"], [
        (-GAP, -WIDTH/2 - GAP), (0, -WIDTH/2 - GAP), (0, WIDTH/2 + GAP),
        (-GAP, WIDTH/2 + GAP)]
    ))
    cpw.add_element(create_shape(layers["SC"], [
        (-GAP, -WIDTH/2 - GAP), (0, -WIDTH/2 - GAP), (0, WIDTH/2 + GAP),
        (-GAP, WIDTH/2 + GAP)]
    ).move(0, -straight_len))

    return cpw

layout.add_element(get_tapped_cpw().move(4400, 2800))


layout.build_to_file(
    r"/home/jyrgen/Documents/PhD/design_files/CC00_90pH_11_7eps_20250324.gds"
)
