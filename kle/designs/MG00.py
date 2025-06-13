"""
"MetaMaterial Porbe Line" from resonator arrays
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


LSHEET = 400e-12 # Based on new deposition
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

# Make line out of resonators


def get_interdigit_cap(layer, W, G, L, N):
    # Interdigit Cap
    extra_end = 15
    interdigit_cap = KleLayoutElement()
    for n in range(N):
        if n == 0:
            _extra0 = -extra_end
            _extra1 = 0
        elif n == N-1:
            _extra0 = 0
            _extra1 = extra_end
        else:
            _extra0 = 0
            _extra1 = 0
        interdigit_cap.add_element(
            create_shape(layer, [
                [_extra0, 0],
                [W + _extra1, 0],
                [W + _extra1, L],
                [_extra0, L]
            ]).move(n * (W + G), (n%2)*G)
        )
    end_conn = create_shape(layer, [
        [-extra_end, 0],
        [-extra_end, -W],
        [extra_end + (W + G) * N - G, -W],
        [extra_end + (W + G) * N - G, 0]
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


def get_one_stage_of_bowtie():
    cutout_width, cutout_height = 465, 226 + 20
    bowtie = KleCutOut(create_shape(layers["SC"], [
        (100-1, 22), (100-1, -cutout_height), (-cutout_width, -cutout_height), (-cutout_width, 22)
    ]))

    intercap, cap = get_interdigit_cap(layers["SC"], 6, 2, 120, 27)
    bowtie.add_element(intercap.move(-138-7 + 15, -107*2 - 4 - 20 - 2))
    bowtie.add_element(intercap.get_copy().flip_vertically().move(0, -224))

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

    inductor, len = get_routed_trace(layers["SC"], ind_f_path, width_start=2.5, width_end=2.5, radii=8)
    tot_inductance = len * LSHEET/2.5
    bowtie.add_element(inductor.move(-138-7, -5 - 107))
    connection_ref = create_ref(0, -112)

    bowtie.add_element(connection_ref)
    print("bowtiecap", cap*2e12, "pF, bowtie Ind", tot_inductance*1e9, "nH")

    return bowtie, connection_ref

def get_trace_end(path):
    trace, _ = get_routed_trace(layers["SC"], path, width_start=2.5, width_end=2.5, radii=10)
    trace_and_endpoint = KleLayoutElement()
    trace_and_endpoint.add_elements([
        create_ref(*path[-1]), trace
    ])

    return trace_and_endpoint


def get_cascaded_LC(f, Z0, N, distance_from_PL):
    cap_N = 5
    mL, cL = get_L_length(f, Z0, width=2, L_sheet=LSHEET, N=cap_N, eps=EPS)
    mL, cL = round(mL, 3), round(cL, 3)
    print(mL, cL)

    lcp = LCParams()
    lcp.interdigit_cap_L = cL
    lcp.interdigit_cap_N = cap_N
    lcp.interdigit_cap_G = 5
    lcp.interdigit_cap_W = 5

    lcp.meander_height = cL
    lcp.meander_L = mL
    lcp.meander_N = 0
    lcp.cutout_width = 1000
    lcp.cutout_height = 673 + 400 + 4000

    
    dc_endpoints = []

    cutout, resonators = get_interdigit_LC(layers["SC"], lcp)
    resonators.move(300, 0)
    resonator_0 = resonators.get_copy()

    for i in range(1, N):
        if i%2 == 0:
            resonators.add_element(resonator_0.get_copy().move(0, (5 * 3 + cL) * i))
        else:
            resonators.add_element(resonator_0.get_copy().flip_horizontally().move(1045, (5 * 3 + cL) * i))

    return cutout


layout.add_element(
    get_cascaded_LC(5e9, 4000, 100, 0).rotate_left().move(2478, 2760 - 80)
)

layout.build_to_file(
    r"/home/jyrgen/Documents/PhD/design_files/MG00_400pH_11_7eps_20250509.gds"
)