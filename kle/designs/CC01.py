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
        (0, 0),
        (step, 0)
    ]
    for i in range(N):
        if i%2 == 0:
            path.extend([
                [step * (i + 1), height/2],
                [step * (i + 2), height/2]
            ])
        else:
            path.extend([
                [step * (i + 1), -height/2],
                [step * (i + 2), -height/2]
            ])

    return path

def get_one_stage_of_bowtie():
    cutout_width, cutout_height = 458+7, 224
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

    print("bowtiecap", cap*2e12, "pF, bowtie Ind", tot_inductance*1e9, "nH")

    return bowtie, cap*2, tot_inductance

bowtie, bt_cap, bt_ind = get_one_stage_of_bowtie()
bt_cap = 0.5e-12
filter_ind = calculate_filter_react(bt_cap, bt_ind, 5.11e9 * 6.28)/(6.28 * 5.11e9)
print("filter_ind", filter_ind)
print("freq", 1/(3.5385704175513093e-14 * parall(3.5385704175513096e-08, filter_ind))**0.5/(2e9 * 3.14))

filter = KleLayoutElement()

filter.add_element(bowtie)
filter.add_element(bowtie.get_copy().move(-465, 0))
filter.add_element(bowtie.get_copy().move(-465 * 2, 0))
filter.add_element(get_cpw_port(
    layers["SC"], connection_width=10, connection_gap=2, port_gap=10, port_length=160, port_width=160, taper_length=80
).flip_horizontally().move(0, -112))


# Resonator 0 - 2 bowtie filters
cutoutHeigh, cutoutWidth = 400, 400
res0 = KleCutOut(create_shape(layers["SC"], [
    (0, 0), (cutoutWidth, 0), (cutoutWidth, -cutoutHeigh), (0, -cutoutHeigh)
]))

freq = 4.5e9
mL, cL = get_L_length(freq, 1000, width=2, L_sheet=LSHEET, N=11, eps=EPS)
print(mL)
capacitor, res_cap = get_interdigit_cap(layers["SC"], 5, 5, cL, 11)

res0.add_element(capacitor.rotate_by_angle(90).move(5, -50))

path_height = 107
meand_path = get_meander_path(path_height, 23, 13)
meand_path.append((400-cL-15, path_height/2))
gnd_to_cap_trace, gndClen = get_routed_trace(
    layers["SC"],
    meand_path,
    width_start=2,
    width_end=2,
    radii=8
)
print(mL * 2, gndClen)
print(gndClen * LSHEET/2)


res0.add_element(gnd_to_cap_trace.move(cL + 15, -50 - 105/2))
res0.add_element(filter.rotate_by_angle(90).move(400-112+32, -1795))
layout.add_element(res0.move(1000, 2937.5))



layout.build_to_file(
    r"/home/jyrgen/Documents/PhD/design_files/CC01_90pH_11_7eps_20250407.gds"
)
