"""
Meander resonators for MAN etching - negative resist
"""
from kle.layout.layout import KleLayout, KleLayoutElement, KleShape, create_shape, KleCutOut, create_ref
from kle.layout.dot_elements import (
    get_Lazar_global_markers,
    get_dot_with_leads, DotWLeadsParams,
    get_andreev_dot_with_loop, ADParams,
)
from kle.layout.resonator_elements import get_resonator_LC, get_coplanar_C, get_cpw_port, get_interdigit_LC, get_L_length, LCParams, get_cpw_impedance
from kle.layout.layout_trace_routing import get_routed_cpw, get_routed_trace
from kle.layout.layout_connections import ConnectedElement
from kle.layout.resonator_elements import get_cpw_LC



import scipy.special as sp
import numpy as np

eps_0 = 8.8542e-12
mu_0 = np.pi * 4e-7


LSHEET = 300e-12 # 300 ph/sq
EPS = 11.7

LAYER_NAMES = [
    "SC", "SC_FINE", "BORDER" #, "MARKER_0", "MARKER_1"
]

layout = KleLayout(10000, 10000, LAYER_NAMES)
layers = layout.get_layers()

# === START BORDER ===
border_shape = create_shape(layers["BORDER"], [
    [0, 0], [5000, 0], [5000, 100], [0, 100]
])

border_square_0 = create_shape(layers["SC"], [
    [0, 0], [10, 0], [10, 10], [0, 10]
])
border_square_1 = create_shape(layers["SC_FINE"], [
    [0, 0], [10, 0], [10, 10], [0, 10]
])

layout.add_element(border_square_0.move(500, 500))
layout.add_element(border_square_1.move(500, 500))

layout.add_element(border_square_0.get_copy().move(4990, 0))
layout.add_element(border_square_1.get_copy().move(4990, 0))

layout.add_element(border_square_0.get_copy().move(4990, 4990))
layout.add_element(border_square_1.get_copy().move(4990, 4990))

layout.add_element(border_square_0.get_copy().move(0, 4990))
layout.add_element(border_square_1.get_copy().move(4990, 4990))


layout.add_element(border_shape.move(500, 500))
layout.add_element(border_shape.get_copy().move(0, 4900))
layout.add_element(border_shape.get_copy().rotate_right().move(0, 5000))
layout.add_element(border_shape.get_copy().rotate_right().move(5000-100, 5000))
# === END BORDER ===

# === DEF MARKER ===
def get_optical_marker():
    op_marker = KleLayoutElement()
    small_arm = create_shape(layers["MARKER_0"], [
        (-10, -1), (-10, 1), (10, 1), (10, -1)
    ])
    op_marker.add_element(small_arm.get_copy())
    op_marker.add_element(small_arm.get_copy().rotate_right())
    
    big_arm = create_shape(layers["MARKER_0"], [
        (10, -5), (10, 5), (100, 5), (100, -5)
    ])
    op_marker.add_element(big_arm.get_copy())
    op_marker.add_element(big_arm.get_copy().rotate_by_angle(90))
    op_marker.add_element(big_arm.get_copy().rotate_by_angle(180))
    op_marker.add_element(big_arm.get_copy().rotate_by_angle(270))
    return op_marker

def get_global_EBL():
    marker = KleLayoutElement()
    small_arm = create_shape(layers["MARKER_1"], [
        (-6, -0.25), (-6, 0.25), (6, 0.25), (6, -0.25)
    ])
    marker.add_element(small_arm.get_copy())
    marker.add_element(small_arm.get_copy().rotate_right())

    big_arm = create_shape(layers["MARKER_1"], [
        (6, -2.5), (6, 2.5), (90, 2.5), (90, -2.5)
    ])
    marker.add_element(big_arm.get_copy())
    marker.add_element(big_arm.get_copy().rotate_by_angle(90))
    marker.add_element(big_arm.get_copy().rotate_by_angle(180))
    marker.add_element(big_arm.get_copy().rotate_by_angle(270))

    return marker

def get_local_EBL():
    marker = KleLayoutElement()
    arm = create_shape(layers["MARKER_1"], [
        (-10, -0.5), (-10, 0.5), (10, 0.5), (10, -0.5)
    ])
    marker.add_element(arm.get_copy())
    marker.add_element(arm.get_copy().rotate_right())
    return marker

def get_local_square():
    markers = KleLayoutElement()

    markers.add_element(get_local_EBL().move(-75, 20))
    markers.add_element(get_local_EBL().move(-75, -25))
    markers.add_element(get_local_EBL().move(75, 20))
    markers.add_element(get_local_EBL().move(75, -25))

    return markers

# === END MARKER ===

# layout.add_element(get_optical_marker().move(1000, 1000))
# layout.add_element(get_optical_marker().move(1000, 9000))
# layout.add_element(get_optical_marker().move(9000, 1000))
# layout.add_element(get_optical_marker().move(9000, 9000))

# layout.add_element(get_global_EBL().move(1000 + 300, 1000))
# layout.add_element(get_global_EBL().move(1000 + 300, 9000))
# layout.add_element(get_global_EBL().move(9000 - 300, 1000))
# layout.add_element(get_global_EBL().move(9000 - 300, 9000))

# layout.add_element(get_local_square().move(3580, 4794.))

# === START PL ===
print("=== PL ===")
PL_WIDTH = 280 # 115 # 80 # 350
PL_GAP = 2
PL_LENGTH = 2800

PL_CO = KleCutOut(create_shape(layers["SC"], [
    (0, 0), (5000, 0), (5000, 2000), (0, 2000)
]))

pl, pl_length = get_routed_cpw(
    layers["SC"],
    [(0, 0),
    (100, 0), (500, 0),
    (1000, 0), (1500, 0),
    (2000, 0), (2500, 0),
    (PL_LENGTH-100, 0), (PL_LENGTH, 0)],
    PL_WIDTH,
    PL_GAP,
    radii=40
)

PORT_GAP = 10 * PL_GAP
PORT_WIDTH = 1.6 * PL_WIDTH
PORT_LEN = 300

# ==== PL ====
pl.add_element(
    get_cpw_port(layers["SC"], PL_WIDTH, PL_GAP, port_gap=PORT_GAP, port_width=PORT_WIDTH, port_length=PORT_LEN, taper_length=200)
)
pl.add_element(
    get_cpw_port(layers["SC"], PL_WIDTH, PL_GAP, port_gap=PORT_GAP, port_width=PORT_WIDTH, port_length=PORT_LEN, taper_length=200).flip_horizontally().move(PL_LENGTH, 0)
)

port_imp, _ = get_cpw_impedance(PORT_WIDTH, PORT_GAP, L_sheet=LSHEET, eps=EPS)
print("port imp", port_imp)

pl_imp, pl_freq = get_cpw_impedance(PL_WIDTH, PL_GAP, L_sheet=LSHEET, eps=EPS, l=pl_length + 2*PORT_LEN, lambda_frac=0.5)
print("Probe line impedance:", pl_imp, "freq:", pl_freq/1e9)

PL_CO.add_element(pl.move(750 + (930-230)*0.5, 1000))
layout.add_element(PL_CO.move(500, 2000))

print("=== PL END ===")
# === END PL ===





# === START RESONATORS ===
def get_resonator_path(w, N, gap, arm_len, end_len=15):
    path = [(-gap -w, end_len), (-gap -w, 0), (0, 0), (arm_len, 0)]
    lp = path[-1]
    for i in range(N-1):
        dir = -1 if i%2 == 0 else 1
        path += [(lp[0], lp[1] + gap + w), (lp[0] + dir * arm_len, lp[1] + gap + w)]
        lp = path[-1]

    path += [(-gap -w, lp[1]), (-gap -w, lp[1]-end_len)]

    return path


def get_Cl_traces(w, gap, eps):
    # F/m
    return 0.09 * (1 + eps) * np.log10(1 + 2 * w/gap + w**2/gap**2) * 1e-10

def get_meander_res_imp(w, N, gap, arm_len, gnd_cap, L_sheet, eps, lambda_frac=0.5, end_len=15):
    eps_r = (1+eps)/2
    cap_between_arms = get_Cl_traces(w, gap, eps)
    print("Cl between arms: ", cap_between_arms)
    
    
    
    k_meander = w / (w + 2 * gap)
    k_gnd = w / (w + 2 * gnd_cap)

    k_m_brim = (1-k_meander**2)**0.5
    k_gnd_brim = (1-k_gnd**2)**0.5

    K_m = sp.ellipk(k_meander)
    K_g = sp.ellipk(k_gnd)

    K_m_brim = sp.ellipk(k_m_brim)
    K_g_brim = sp.ellipk(k_gnd_brim)

    C = eps_0 * (1+eps) * K_m/K_m_brim # cap per meander len
    Cg = eps_0 * (1+eps) * K_g/K_g_brim # cap per gnd len

    center_width = w * 1e-6

    tot_cap = 0
    tot_ind = 0

    # ===
    ind_per_len = 0 # 0.125 * mu_0 * K_m_brim/K_m
    # ===

    for n in range(N):
        tot_cap += 1e-6 * (arm_len) * C * Cg * ( 1/(C + Cg * n) + 1/(C + Cg * (N-n-1)))
        tot_ind += 1e-6 * (arm_len + gap) * (L_sheet / center_width - ind_per_len)

    tot_ind += 1e-6 * (end_len * 2) * L_sheet / center_width # Add eends
    tot_cap += 1e-6 * (end_len * 2) * Cg * 2 # Add ends

    imp = (tot_ind/tot_cap)**0.5
    freq = 1 / (tot_cap * tot_ind)**0.5
    
    return imp, freq * lambda_frac

# === START RESONATORS ===

res_poss = [
    (-600, 523+135-17.5-42.5),
    (-100, 523+135-17.5-42.5),
    (400, 523+135-17.5-42.5),

    (1100, 523+135-17.5-42.5),
    (1600, 523+135-17.5-42.5),
    (2100, 523+135-17.5-42.5),
]
paramss = [
    (2, 22, 3, 72),
    (2, 22, 3, 70),
    (2, 22, 3, 68),

    (0.5, 20, 2.4, 38),
    (0.5, 20, 2.2, 36),
    (0.5, 20, 2, 35.1),
]


for i, (res_pos, param) in enumerate(zip(res_poss, paramss)):
    res_hole = create_shape(layers["SC"], [
        (0, -100), (300, -100), (300, 300), (0, 300)
    ])
    PL_CO.add_element(res_hole.move(2100 + res_pos[0], 2000 + res_pos[1]))

    smaller_end = [3, 6, 7, 8, 9, 10]

    meander_path = get_resonator_path(*param, end_len=15)
    meander_res, res_len = get_routed_trace(
        layers["SC_FINE"],
        meander_path,
        width_start=param[0],
        width_end=param[0],
        radii=1 if param[0] < 1 else 2
    )
    if i in [3, 4, 5]:
        meander_res.move(0, 90)

    meander_res.move(0, -50)

    test_imp, test_freq = get_meander_res_imp(*param, 120, L_sheet=LSHEET, eps=EPS, end_len=15 if i not in smaller_end else 10)
    print(f"{i} - len (um):", res_len, "imp:", test_imp*1.425, "freq:", test_freq/1.425e9)
    print("ratio:", (param[2] + param[0]) * param[1] / param[3])
    
    cpw_Z, cpw_freq = get_cpw_impedance(
        param[0], 100, L_sheet=LSHEET, eps=EPS, l=res_len
    )
    print("CPW:", cpw_Z, cpw_freq)
    print("CPW calc:", 2 * cpw_freq * res_len/param[0] * LSHEET)

    layout.add_element(meander_res.move(2250 - param[3]/2 + res_pos[0], 2100 + res_pos[1]))




# Fs = [5.1e9, 5.2e9, 5.3e9, 5.4e9, 5.5e9]
# top_Y = 3080 - 18 + 50
# pos = [
#     (1550, top_Y + 50), (2150, top_Y + 60), (2750, top_Y + 70), (3350, top_Y + 80),
#     (3950, top_Y + 90)
# ]
# params = [
#     (2, 5), (2, 6), (1.5, 7), (1, 9), (0.5, 9)
# ]

# for f, pos, prms in zip(Fs, pos, params):
#     res_hole = create_shape(layers["SC"], [
#         (0, 0), (500, 0), (500, 500), (0, 500)
#     ])
#     PL_CO.add_element(res_hole.move(1575 + pos[0] - 1080 - 400, 3500-458 + 17.5 + 42.5))

#     z0 = 1000 if f < 4.45e9 else 2000
#     mL, cL = get_L_length(f, z0, width=prms[0], L_sheet=LSHEET, N=prms[1], eps=EPS)
#     # print("mL, cL", mL, cL)

#     lcp = LCParams()
#     lcp.interdigit_cap_L = cL
#     lcp.interdigit_cap_N = prms[1]
#     lcp.interdigit_cap_G = 5
#     lcp.interdigit_cap_W = 5

#     lcp.meander_height = cL + 15
#     lcp.meander_L = mL
#     lcp.meander_N = 4
#     lcp.cutout_width = 500
#     lcp.meander_W = prms[0]
#     lcp.meander_offset = 20

#     resonator = get_interdigit_LC(layers["SC_FINE"], lcp)

#     # resonator.move(80, 25)
#     resonator.rotate_by_angle(90).move(80 + 30, -30)

#     layout.add_element(
#         resonator.move(*pos)
#     )

# === END RESONATORS ===


# TEST 
def get_TS(layer0, layer1, bond_pad_width, bond_pad_heigth, widths, length):
    extra = 80
    cutout = KleLayoutElement()
    
    bp = create_shape(layer0, [
        [0, 0], [bond_pad_width, 0], [bond_pad_width, bond_pad_heigth], [0, bond_pad_heigth]
    ])
    for i, width in enumerate(widths):
        cutout.add_element(bp.get_copy().move(extra, extra + (extra + bond_pad_heigth) * i))
        cutout.add_element(bp.get_copy().move(extra + bond_pad_width + length, extra + (extra + bond_pad_heigth) * i))
        cutout.add_element(
            create_shape(layer1, [
                [-3,0], [length+3, 0], [length+3, width], [-3, width]
            ]).move(extra + bond_pad_width, extra + (extra+bond_pad_heigth) * i + bond_pad_heigth/2)
        )
    # cutout.add_element(tss)

    return cutout


tss0 = get_TS(layers["SC_FINE"], layers["SC_FINE"], 200, 100, [2, 1, 0.5], 10)
layout.add_element(tss0.get_copy().move(2000, 1200))
layout.add_element(tss0.get_copy().move(2000, 4500-320))


# layout.build()
layout.build_to_file(
    r"/home/jyrgen/Documents/PhD/design_files/MR01_300pH_20251022.gds"
)