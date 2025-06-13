"""
Current controlled resonator array
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

# ==== PL and ports ====
print("=== PL ===")
PL_WIDTH = 280
PL_GAP = 3
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

PORT_GAP = 4 * PL_GAP
PORT_WIDTH = 1.2 * PL_WIDTH
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

layout.add_element(pl.move(460 + 500 + 50, 3500))

print("=== PL END ===")
# ==== PL ====


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

N3_and_path = {
    0: [(0, 0), (-70, 0), (-70, -270 + 19.25 - 200)],
    1: [(0, 0), (-100, 0), (-250, -400), (-340 + 65.241, -400), (-350 + 65.241, -400)],
    2: [(0, 0), (-100, 0), (-350 + 65.241, 0)],
    3: [(0, 0), (-100, 0), (-250, 400), (-340 + 65.241, 400), (-350 + 65.241, 400)],
    4: [(0, 0), (-70, 0), (-70, 270 - 19.274 + 200)]
}
N5_and_path = {
    0: [(0, 0), (-70, 0), (-70, -270 + 19.25 - 200)],
    1: [(0, 0), (-100, 0), (-170, -400), (-300 + 65.241 + 50.291, -400), (-350 + 65.241 + 50.291, -400)],
    2: [(0, 0), (-100, 0), (-350 + 65.241 + 50.291, 0)],
    3: [(0, 0), (-100, 0), (-170, 400), (-340 + 65.241 + 50.291, 400), (-350 + 65.241 + 50.291, 400)],
    4: [(0, 0), (-70, 0), (-70, 270 - 19.274 + 200 - 22.304)]
}

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
    lcp.cutout_width = 610 - 30 + distance_from_PL
    lcp.cutout_height = 673 + 400

    
    dc_endpoints = []

    cutout, resonators = get_interdigit_LC(layers["SC"], lcp)
    if N == 5:
        DC_connect_zero = (-73.579 + 45 + 59.26 - 35.922 - 50.291, 200 + 114.5 + 142.5 + 3.75 - 10)
        resonators.move(45, 200 + (383.51 - 95 - 20) / 2)
    elif N == 3:
        DC_connect_zero = (-73.579 + 45 + 59.26 - 35.922, 200 + 114.5 + 142.5 + 3.75 - 10 + 35)
        resonators.move(45, 200 + (383.51 - 95 - 20 + 70) / 2)
    
    cutout.add_element(create_shape(layers["SC"], [
        (0, 0), (0, lcp.interdigit_cap_W * 3), (45, lcp.interdigit_cap_W * 3), (45, 0)
    ]).move(45 + 501.543 - 11.543, 90 - 10 + 200 + (383.51 - 95 - 20) / 2 + (35 if N == 3 else 0)))

    cutout.add_element(create_shape(layers["SC"], [
        (0, 0), (0, lcp.interdigit_cap_W * 3), (45, lcp.interdigit_cap_W * 3), (45, 0)
    ]).move(45 + 501.543 - 11.543, 90 + 200 + 5 + (cL + 15) * N + (383.51 - 95 - 20) / 2 + (35 if N == 3 else 0)))

    resonator_0 = resonators.get_copy()

    if N == 5:
        trace = get_trace_end(N5_and_path[0]).move(*DC_connect_zero)
        resonators.add_element(trace)
        dc_endpoints.append(trace.subelements[0])

    if N == 5:
        for i in range(1, N):
            resonators.add_element(resonator_0.get_copy().move(0, (5 * 3 + cL) * i))
            trace = get_trace_end(N5_and_path[i]).move(*DC_connect_zero).move(0, (5 * 3 + cL) * i)
            resonators.add_element(trace)
            dc_endpoints.append(trace.subelements[0])

            if i in [1, 2, 3]:
                for n in range(3):
                    bt_elem, bt_ref = get_one_stage_of_bowtie()
                    bt_elem.flip_horizontally()
                    bt_points = bt_ref.get_absolute_points()[0]
                    dc_trace_points = trace.subelements[0].get_absolute_points()[0]
                    bt_elem.move(dc_trace_points[0] - bt_points[0] - 465 - n * (465 + 99), dc_trace_points[1] - bt_points[1])
                    
                    resonators.add_element(bt_elem)
                
                port_connect = (dc_trace_points[0] - bt_points[0] - (n+1) * (465 + 99), dc_trace_points[1] - bt_points[1]-112)

                resonators.add_element(get_cpw_port(
                    layers["SC"], connection_width=12,
                    connection_gap=2, port_gap=10,
                    port_length=160, port_width=160, taper_length=80
                ).move(*port_connect))

            if i in [4]:
                extra_parts = KleLayoutElement()

                extra_conn = KleCutOut(create_shape(layers["SC"], [(0, 0), (400, 0), (400, 454), (0, 454)]))
                extra_parts.add_element(extra_conn.move(-290, 1073))
                start_point = dc_endpoints[i].get_absolute_points()[0]
                extra_path = [start_point, (start_point[0], start_point[1] + 320), (start_point[0] - 214.911 + 70, start_point[1] + 320), (start_point[0] - 214.911 + 0.152 + 50.291, start_point[1] + 320)]
                extra_trace, _ = get_routed_trace(layers["SC"], extra_path, width_start=2.5, width_end=2.5, radii=10)
                extra_conn.add_element(extra_trace)

                endpoint = (start_point[0] - 214.911 + 0.152 + 50.291, start_point[1] + 320)
                for n in range(3):
                    bt_elem, bt_ref = get_one_stage_of_bowtie()
                    bt_elem.flip_horizontally()
                    bt_points = bt_ref.get_absolute_points()[0]
                    dc_trace_points = endpoint
                    bt_elem.move(dc_trace_points[0] - bt_points[0] - 465 - n * (465 + 99), dc_trace_points[1] - bt_points[1])
                    
                    extra_parts.add_element(bt_elem)
                
                resonators.add_element(extra_parts)
                port_connect = (dc_trace_points[0] - bt_points[0] - (n+1) * (465 + 99), dc_trace_points[1] - bt_points[1]-112)
                
                extra_parts.add_element(get_cpw_port(
                    layers["SC"], connection_width=12,
                    connection_gap=2, port_gap=10,
                    port_length=160, port_width=160, taper_length=80
                ).move(*port_connect))

                
            
        # add for 0
        resonators.add_element(extra_parts.get_copy().flip_vertically().move(0, 1073))
            
        resonators.move(290, 0)


        return cutout
    
    else:
        for i in range(0, N):
            if i != 0:
                resonators.add_element(resonator_0.get_copy().move(0, (5 * 3 + cL) * i))
            trace = get_trace_end(N3_and_path[i + 1]).move(*DC_connect_zero).move(0, (5 * 3 + cL) * i)
            resonators.add_element(trace)
            dc_endpoints.append(trace.subelements[0])

            if i in [0, 1, 2]:
                for n in range(3):
                    bt_elem, bt_ref = get_one_stage_of_bowtie()
                    bt_elem.flip_horizontally()
                    bt_points = bt_ref.get_absolute_points()[0]
                    dc_trace_points = trace.subelements[0].get_absolute_points()[0]
                    bt_elem.move(dc_trace_points[0] - bt_points[0] - 465 - n * (465 + 99), dc_trace_points[1] - bt_points[1])
                    
                    resonators.add_element(bt_elem)
                
                port_connect = (dc_trace_points[0] - bt_points[0] - (n+1) * (465 + 99), dc_trace_points[1] - bt_points[1]-112)

                resonators.add_element(get_cpw_port(
                    layers["SC"], connection_width=12,
                    connection_gap=2, port_gap=10,
                    port_length=160, port_width=160, taper_length=80
                ).move(*port_connect))

            # if i in [2]:
            #     extra_parts = KleLayoutElement()

            #     extra_conn = KleCutOut(create_shape(layers["SC"], [(0, 0), (400, 0), (400, 454), (0, 454)]))
            #     extra_parts.add_element(extra_conn.move(-290, 1073))
            #     start_point = dc_endpoints[i].get_absolute_points()[0]
            #     extra_path = [start_point, (start_point[0], start_point[1] + 320), (start_point[0] - 214.911 + 30, start_point[1] + 320), (start_point[0] - 214.911 + 0.152, start_point[1] + 320)]
            #     extra_trace, _ = get_routed_trace(layers["SC"], extra_path, width_start=2.5, width_end=2.5, radii=10)
            #     extra_conn.add_element(extra_trace)

            #     endpoint = (start_point[0] - 214.911 + 0.152, start_point[1] + 320)
            #     for n in range(3):
            #         bt_elem, bt_ref = get_one_stage_of_bowtie()
            #         bt_elem.flip_horizontally()
            #         bt_points = bt_ref.get_absolute_points()[0]
            #         dc_trace_points = endpoint
            #         bt_elem.move(dc_trace_points[0] - bt_points[0] - 465 - n * (465 + 99), dc_trace_points[1] - bt_points[1])
                    
            #         extra_parts.add_element(bt_elem)
                
            #     resonators.add_element(extra_parts)
            #     port_connect = (dc_trace_points[0] - bt_points[0] - (n+1) * (465 + 99), dc_trace_points[1] - bt_points[1]-112)
                
            #     extra_parts.add_element(get_cpw_port(
            #         layers["SC"], connection_width=12,
            #         connection_gap=2, port_gap=10,
            #         port_length=160, port_width=160, taper_length=80
            #     ).move(*port_connect))

        # add for 0
        # resonators.add_element(extra_parts.get_copy().flip_vertically().move(0, 1073))
            

        resonators.move(290, 0)
        # print(dc_endpoints)

        return cutout



# cap_elem, _ = get_interdigit_cap(layers["SC"], 6, 2, 120, 27)
# layout.add_element(cap_elem.move(-200, -200))

# def get_cascaded_square_LC(f, Z0, N):
#     # mL, cL = get_L_length(f, Z0, width=2, L_sheet=LSHEET, N=11, eps=EPS)
#     L, C = get_resonator_LC(f, Z0)
#     plate_W, plate_G, plate_L = 70, 2, 130
#     print("C vs plate", C, get_coplanar_C(plate_W, plate_G, eps=EPS) * plate_L/1e6)

#     cutout = KleCutOut(create_shape(layers["SC"], [
#         (0, 0), (0, 673), (600, 673), (600, 0)
#     ]))

#     base_cap_square = create_shape(layers["SC"], [
#         (0, 0), (plate_L, 0), (plate_L, plate_W), (0, plate_W)
#     ]).move(455/2, 100)

#     path = [
#         [0, -7.5],
#         [-10, -7.5],
#         [-10, -1.0],
#         [-126.08683333333333, -1.0],
#         [-126.08683333333333, 7.0],
#         [-50.0, 7.0],
#         [-50.0, 15.0],
#         [-126.08683333333333, 15.0],
#         [-126.08683333333333, 23.0],
#         [-50.0, 23.0],
#         [-50.0, 31.0],
#         [-126.08683333333333, 31.0],
#         [-126.08683333333333, 39.0],
#         [-20, 39.0],
#         [-10, 39.241],
#         [-10, 45.741],
#         [-1, 45.741],
#         [0, 45.741]
#     ]
#     base_inductor, len = get_routed_trace(layers["SC"], path, width_start=2, width_end=2, radii=3)
#     base_inductor.move(227.5, 110 + 35 + 7)
    
#     # print(type(base_inductor))
#     print("Llen vs L", len * 90e-12 / 2, L)

#     cutout.add_element(base_cap_square.get_copy())


#     for i in range(N):
#         cutout.add_element(base_cap_square.get_copy().move(0, (plate_W + plate_G) * (i+1)))
#         cutout.add_element(base_inductor.get_copy().move(0, i * (70 + 2)))

#     return cutout


distance_from_PL = 50
# for i in range(2, 7):

layout.add_element(
    get_cascaded_LC(5e9, 4000, 5, distance_from_PL).rotate_left().move(2478, 2760 - 80 + distance_from_PL)
)

layout.add_element(
    get_cascaded_LC(6e9, 4000, 3, distance_from_PL).rotate_left().move(4618, 2760 - 80 + distance_from_PL)
)

# Add ref resonator
NCAP = 5
mL, cL = get_L_length(6.5e9, 4000, width=2, L_sheet=LSHEET, N=NCAP, eps=EPS)

lcp = LCParams()
lcp.interdigit_cap_L = cL
lcp.interdigit_cap_N = 5
lcp.interdigit_cap_G = 5
lcp.interdigit_cap_W = 5

lcp.meander_height = cL + 15
lcp.meander_L = mL
lcp.meander_N = 0
lcp.cutout_width = 800
lcp.cutout_height = 400

cutout, resonator = get_interdigit_LC(layers["SC"], lcp)

resonator.move(80 + 375, -30 + 70 + (216.764 - 142.75)/2)
layout.add_element(cutout.rotate_right().move(2500, 4440))




# Add regular CC resonator
FREQ = [4.5e9]
POS = [(0, 0)]
RES_GAP = [40, ]
BOWTIES = [
    [2, 2]
]


def get_fishbone_cap():
    cutout_width, cutout_height = 145, 224
    bowtie = KleCutOut(create_shape(layers["SC"], [
        (0, 0), (0, -cutout_height), (-cutout_width, -cutout_height), (-cutout_width, 0)
    ]))

    intercap, cap = get_interdigit_cap(layers["SC"], 5, 2, 100, 21)
    bowtie.add_element(intercap.move(-138-7, -107*2 - 5))
    bowtie.add_element(intercap.get_copy().flip_vertically().move(0, -232 + 8))

    return bowtie

for f, pos, res_gap, bowties in zip(FREQ, POS, RES_GAP, BOWTIES):
    mL, cL = get_L_length(f, 4000, width=2, L_sheet=LSHEET, N=NCAP, eps=EPS)
    mL, cL = round(mL, 3), round(cL, 3)
    print(mL, cL)

    lcp = LCParams()
    lcp.interdigit_cap_L = cL
    lcp.interdigit_cap_N = NCAP
    lcp.interdigit_cap_G = 5
    lcp.interdigit_cap_W = 5

    lcp.meander_height = cL + 15
    lcp.meander_L = mL
    lcp.meander_N = 0
    lcp.cutout_width = 600
    lcp.cutout_height = 673 - 100

    cutout, resonator = get_interdigit_LC(layers["SC"], lcp)
    resonator.rotate_right().move(165, 305 + 20)

    meander_path = get_meander_path(100, 50, 7)
    meander_path = [(0, 23 + 89 - 30.25), (0, 15 + 30 - 0.25)] + meander_path[:-3] + [
        (meander_path[-1][0] - 100, meander_path[-1][1]),
        (meander_path[-1][0] + 80, meander_path[-1][1])
    ]
    meander, meander_len = get_routed_trace(
        layers["SC"], meander_path, width_start=2.5,
        width_end=2.5, radii=10
    )
    
    meander_right = meander.get_copy().flip_horizontally().move(245 + 167.5 + 50 + cL, 650 + 31 - 190 + 0.25)
    cutout.add_element(meander_right)
    meander_left = meander.move(147.5 - 60, 530 + 120 + 31 -190 + 0.25)
    cutout.add_element(meander_left)
    print("meander_ind", meander_len * LSHEET/2)
    resonator.move(0, -22.5)
    resonator.move(0, res_gap)
    layout.add_element(cutout.move(*pos))

    if bowties[0] > 0:
        bt_elem, ref = get_one_stage_of_bowtie()
        bt_elem.rotate_left()

        meander_end = meander_left.subelements[-2].get_absolute_points()[0]
        bowtie_end = ref.get_absolute_points()[0]

        for i in range(bowties[0]):
            cutout.add_element(bt_elem.get_copy().move(
                meander_end[0] - bowtie_end[0], meander_end[1] - bowtie_end[1] + i * (465 + 99) + 465
            ))

        cutout.add_element(get_cpw_port(
            layers["SC"], connection_width=12,
            connection_gap=2, port_gap=10,
            port_length=160, port_width=160, taper_length=80
        ).move(-145, -112).rotate_left().flip_vertically().move(
            meander_end[0] - bowtie_end[0] + 257, meander_end[1] - bowtie_end[1] + (i+1) * (465 + 99) + 112
        ))

    if bowties[1] > 0:
        bt_elem, ref = get_one_stage_of_bowtie()
        bt_elem.rotate_left()

        meander_end = meander_right.subelements[-2].get_absolute_points()[0]
        bowtie_end = ref.get_absolute_points()[0]

        for i in range(bowties[1]):
            cutout.add_element(bt_elem.get_copy().move(
                meander_end[0] - bowtie_end[0], meander_end[1] - bowtie_end[1] + i * (465 + 99) + 465
            ))
        cutout.add_element(get_cpw_port(
            layers["SC"], connection_width=12,
            connection_gap=2, port_gap=10,
            port_length=160, port_width=160, taper_length=80
        ).move(-145, -112).rotate_left().flip_vertically().move(
            meander_end[0] - bowtie_end[0] + 257, meander_end[1] - bowtie_end[1] + (i+1) * (465 + 99) + 112
        ))

    cutout.move(3300, 3640)



# === End top

layout.build_to_file(
    r"/home/jyrgen/Documents/PhD/design_files/RA00_400pH_11_7eps_20250505.gds"
)