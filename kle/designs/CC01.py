"""
Current controlled resonators tests (planar, no ald like things)
"""
from kle.layout.layout import KleLayout, KleLayoutElement, KleShape, create_shape, KleCutOut, create_ref
from kle.layout.dot_elements import (
    get_Lazar_global_markers,
    get_dot_with_leads, DotWLeadsParams,
    get_andreev_dot_with_loop, ADParams,
)
from kle.layout.resonator_elements import get_cpw_port, get_interdigit_LC, get_L_length, LCParams, get_cpw_impedance
from kle.layout.layout_trace_routing import get_routed_cpw, get_routed_trace
from kle.layout.layout_connections import ConnectedElement


def parall(X0, X1):
    return (X0 * X1) / (X0 + X1)

def calculate_filter_react(CF, LF, omega, n=3):
    XL = omega * LF
    XF = 1/(omega * CF)
    print("ZL, CF", XL, XF)

    stage_0 = XL + XF
    # stage_1 = parall(CF, stage_0) + ZL
    
    for i in range(1, n):
        print(stage_0)
        stage_0 = parall(stage_0, XF) + XL
        print(stage_0)

    return stage_0


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
print("=== PL ===")
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

print("=== PL END ===")
# ==== PL ====

def get_interdigit_cap(layer, W, G, L, N):
    # Interdigit Cap
    interdigit_cap = KleLayoutElement()
    for n in range(N):
        interdigit_cap.add_element(
            create_shape(layer, [
                [0, 0],
                [W, 0],
                [W, L],
                [0, L]
            ]).move(n * (W + G), (n%2)*G)
        )
    end_conn = create_shape(layer, [
        [-0, 0],
        [-0, -W],
        [(W + G) * N - G, -W],
        [(W + G) * N - G, 0]
    ])
    interdigit_cap.add_element(end_conn)
    interdigit_cap.add_element(end_conn.get_copy().move(0, L + G + W))

    cap = (EPS + 1) * ((N-3) * (W/G) * 4.409e-6 + 9.92e-6) * L * 1e-12


    return interdigit_cap, cap

def get_meander_path(height, step, N):
    path = [
        (0, 0)
    ]
    for i in range(N):
        if i%2 == 0:
            path.extend([
                (height, -step * i),
                (height, -step * (i + 1))
            ])
        else:
            path.extend([
                (0, -step * i),
                (0, -step * (i + 1))
            ])

    path = path[:-1] + [(height * ((i+1)%2), -step * (i + 0.5)), path[-1]]

    return path


def get_fishbone_cap():
    cutout_width, cutout_height = 145, 224
    bowtie = KleCutOut(create_shape(layers["SC"], [
        (0, 0), (0, -cutout_height), (-cutout_width, -cutout_height), (-cutout_width, 0)
    ]))

    intercap, cap = get_interdigit_cap(layers["SC"], 5, 2, 100, 21)
    bowtie.add_element(intercap.move(-138-7, -107*2 - 5))
    bowtie.add_element(intercap.get_copy().flip_vertically().move(0, -232 + 8))

    return bowtie


def get_one_stage_of_bowtie():
    cutout_width, cutout_height = 465, 224
    bowtie = KleCutOut(create_shape(layers["SC"], [
        (0, 0), (0, -cutout_height), (-cutout_width, -cutout_height), (-cutout_width, 0)
    ]))

    intercap, cap = get_interdigit_cap(layers["SC"], 5, 2, 100, 21)
    bowtie.add_element(intercap.move(-138-7, -107*2 - 5))
    bowtie.add_element(intercap.get_copy().flip_vertically().move(0, -232 + 8))

    N_step = 28
    gap_step = 20
    gap_heigth = 80

    ind_f_path = [(0, 0), (-gap_step, 0)]

    def temp(blah):
        if blah == 0:
            return -gap_heigth
        if blah == 1:
            return -gap_heigth
        if blah == 2:
            return gap_heigth
        else:
            return gap_heigth

    for i in range(N_step):
        ind_f_path.append(
            (-gap_step * (1 + (i+1)//2), temp(i%4)),
        )

    ind_f_path.append((-gap_step * (1 + (i+2)//2), 0))
    ind_f_path.append((-310, 0))
    ind_f_path.append((-320, 0))

    inductor, len = get_routed_trace(layers["SC"], ind_f_path, width_start=2, width_end=2, radii=8)
    tot_inductance = len * LSHEET/2
    bowtie.add_element(inductor.move(-138-7, -5 - 107))
    connection_ref = create_ref(0, -112)

    bowtie.add_element(connection_ref)
    print("bowtiecap", cap*2e12, "pF, bowtie Ind", tot_inductance*1e9, "nH")

    return bowtie, connection_ref


def get_grounded_LC_with_split_L(freq_target, meander_offset=10):
    interdigit_W = 6
    mL, cL = get_L_length(freq_target, 1000, 2, LSHEET, EPS)
    mL, cL = round(mL, 3), round(cL, 3)

    res_cap_elem, res_cap_val = get_interdigit_cap(layers["SC"], interdigit_W, interdigit_W, cL, 11)

    # Make 2 meanders,
    double_mL = 2 * mL
    path_height = 100

    N_meander = 13
    meander_path = get_meander_path(path_height, 23, N_meander)
    res_meander_elem, res_meander_len = get_routed_trace(
        layers["SC"],
        [(-meander_offset, 0)]+meander_path,
        width_start=2,
        width_end=2,
        radii=8
    )
    heigth_diff = (res_meander_len - double_mL) / N_meander
    meander_path = get_meander_path(path_height - heigth_diff, 23, N_meander)
    res_meander_elem, res_meander_len = get_routed_trace(
        layers["SC"],
        [(-meander_offset, 0)]+meander_path,
        width_start=2,
        width_end=2,
        radii=8
    )
    print(res_meander_len, double_mL)

    resonator = KleCutOut(create_shape(layers["SC"], [
        (-200, 0), (200 + 105, 0), (305, -23 * N_meander - cL - interdigit_W - 10),
        (-200, -23 * N_meander - cL - interdigit_W - 10)
    ]))

    resonator.add_element(res_cap_elem.move(0, -cL -interdigit_W*2))
    res_meander_elem.move(0, -cL - 10)
    meander_left = res_meander_elem.get_copy().flip_horizontally().move(-meander_offset, -interdigit_W)
    meander_right = res_meander_elem.move(21 * interdigit_W + meander_offset, -interdigit_W)

    resonator.add_elements([meander_left, meander_right])

    return resonator, meander_left.subelements[-1], meander_right.subelements[-1]


FREQ = [5e9, 5.5e9, 6e9, 6.5e9, 7e9]
OFFSETS = [10, 70, 10, 70, 10]
BOWTIES = [
    [2, 0], [2, 2], [0, 0], [2, 2], [0, 2]
]
POS = [
    (1400 + i*775, 2937.5 - 20) for i in range(len(FREQ))
]

for f, pos, offset, bowties in zip(FREQ, POS, OFFSETS, BOWTIES):
    split_L_LC, meander_left_end_ref, meander_right_end_ref = get_grounded_LC_with_split_L(f, meander_offset=offset)
    layout.add_element(split_L_LC.move(*pos))

    if bowties[0] > 0:
        bt_elem, ref = get_one_stage_of_bowtie()
        bt_elem.rotate_left()

        meander_end = meander_left_end_ref.get_absolute_points()[0]
        bowtie_end = ref.get_absolute_points()[0]

        for i in range(bowties[0]):
            layout.add_element(bt_elem.get_copy().move(
                meander_end[0] - bowtie_end[0], meander_end[1] - bowtie_end[1] - i * 465
            ))

        endcap = get_fishbone_cap()
        endcap.add_element(get_cpw_port(
            layers["SC"], connection_width=10,
            connection_gap=2, port_gap=10,
            port_length=160, port_width=160, taper_length=80
        ).move(-145, -112))
        endcap.rotate_left()
        layout.add_element(endcap.move(
            meander_end[0] - bowtie_end[0], meander_end[1] - bowtie_end[1] - (i+1) * 465
        ))
        


    if bowties[1] > 0:
        bt_elem, ref = get_one_stage_of_bowtie()
        bt_elem.rotate_left()

        meander_end = meander_right_end_ref.get_absolute_points()[0]
        bowtie_end = ref.get_absolute_points()[0]

        for i in range(bowties[1]):
            layout.add_element(bt_elem.get_copy().move(
                meander_end[0] - bowtie_end[0], meander_end[1] - bowtie_end[1] - i * 465
            ))
        endcap = get_fishbone_cap()
        endcap.add_element(get_cpw_port(
            layers["SC"], connection_width=10,
            connection_gap=2, port_gap=10,
            port_length=160, port_width=160, taper_length=80
        ).move(-145, -112))
        endcap.rotate_left()
        layout.add_element(endcap.move(
            meander_end[0] - bowtie_end[0], meander_end[1] - bowtie_end[1] - (i+1) * 465
        ))



# Top Side (floating LC and fishbone filters)====
# FREQ = [5.25e9, 5.75e9, 6.25e9, 6.75e9, 7.25e9]
# POS = [
#     (1400 + i*775, 3060) for i in range(len(FREQ))
# ]

FREQ = [5.25e9]
POS = [(0, 0)]

for f, pos in zip(FREQ, POS):
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
    resonator.rotate_right().move(65, 305 + 20)

    meander_path = get_meander_path(100, 23, 23)
    meander_path = meander_path + [
        (meander_path[-1][0] + 10, meander_path[-1][1]),
        (meander_path[-1][0] + 20, meander_path[-1][1])
    ]
    meander, meander_len = get_routed_trace(
        layers["SC"], meander_path, width_start=2,
        width_end=2, radii=5
    )
    cutout.add_element(meander.move(47.5, 530 + 120))
    print("meander_ind", meander_len * LSHEET/2)

    layout.add_element(cutout.move(*pos))

# === End top


layout.build_to_file(
    r"/home/jyrgen/Documents/PhD/design_files/CC01_90pH_11_7eps_20250407.gds"
)
