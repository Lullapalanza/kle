"""
Design for Bertram and rasmus for dots coupled to Bertram designed current control

heidelberg
marks_RestoRas08.gds reference for markers
notebook there as well
1 and 2 gates/dots
1Ghz BiasT like filter (2pads)

10x10 chip
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



LSHEET = 63e-12 # 63 ph/sq
EPS = 11.7

LAYER_NAMES = [
    "SC", "SC_FINE", "REF_DOT"
]
layout = KleLayout(10000, 10000, LAYER_NAMES)
layers = layout.get_layers()

# === START BORDER ===
border_shape = create_shape(layers["SC"], [
    [0, 0], [9000, 0], [9000, 100], [0, 100]
])
layout.add_element(border_shape.move(500, 500))
layout.add_element(border_shape.get_copy().move(0, 8900))
layout.add_element(border_shape.get_copy().rotate_right().move(0, 9000))
layout.add_element(border_shape.get_copy().rotate_right().move(9000, 9000))
# === END BORDER ===

# === START PL ===
print("=== PL ===")
PL_WIDTH = 240
PL_GAP = 50
PL_LENGTH = 6500
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

PORT_GAP = 4 * PL_GAP
PORT_WIDTH = 2 * PL_WIDTH
PORT_LEN = 300

# ==== PL ====
pl.add_element(
    get_cpw_port(layers["SC"], PL_WIDTH, PL_GAP, port_gap=PORT_GAP, port_width=PORT_WIDTH, port_length=PORT_LEN)
)
pl.add_element(
    get_cpw_port(layers["SC"], PL_WIDTH, PL_GAP, port_gap=PORT_GAP, port_width=PORT_WIDTH, port_length=PORT_LEN).flip_horizontally().move(PL_LENGTH, 0)
)
pl_cut, _ = get_routed_trace(layers["SC"], [
    (0, 0), (0, PL_WIDTH/2), (0, PL_WIDTH)
], width_start=1, width_end=1)
pl.add_element(pl_cut.move(PL_LENGTH/2, -PL_WIDTH/2))

port_imp, _ = get_cpw_impedance(PORT_WIDTH, PORT_GAP, L_sheet=LSHEET, eps=EPS)
print("port imp", port_imp)

pl_imp, pl_freq = get_cpw_impedance(PL_WIDTH, PL_GAP, L_sheet=LSHEET, eps=EPS, l=pl_length + 2*PORT_LEN)
print("Probe line impedance:", pl_imp, "freq:", pl_freq/1e9)

pl_co = KleCutOut(pl.move(460 + 500 + 220 + 620, 5000))

layout.add_element(pl_co)

print("=== PL END ===")
# === END PL ===


# === FILTER DEF ===
def get_interdigit_cap(layer, W, G, L, N, extra_end=True):
    # Interdigit Cap
    extra_end = 15 if extra_end is True else 0
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


def get_one_stage_of_bowtie(skip_mean=False, existing_ind=0):
    cutout_width, cutout_height = 465, 226 + 20 - 2
    bowtie = KleCutOut(create_shape(layers["SC"], [
        (100-1-18, 20), (100-1-18, -cutout_height), (-cutout_width, -cutout_height), (-cutout_width, 20)
    ]))

    intercap, cap = get_interdigit_cap(layers["SC"], 4, 4, 120, 25)
    bowtie.add_element(intercap.move(-138-7 + 15, -107*2 - 4 - 20 - 2))
    bowtie.add_element(intercap.get_copy().flip_vertically().move(0, -224))

    if skip_mean is False:
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
    
    else:
        ind_f_path = [(0, 0), (-10, 0), (-320, 0)]

    inductor, len = get_routed_trace(layers["SC"], ind_f_path, width_start=2.5, width_end=2.5, radii=8)
    tot_inductance = len * LSHEET/2.5 + existing_ind
    bowtie.add_element(inductor.move(-138-7, -5 - 107))
    connection_ref = create_ref(0, -112)

    bowtie.add_element(connection_ref)
    print("bowtiecap", cap*2e12, "pF, bowtie Ind", tot_inductance*1e9, "nH")
    def cutoff(L, C):
        return 1/(2*3.14 * (L * C)**0.5)
    print("cutoff (GHz)", cutoff(cap*2, tot_inductance)/1e9)

    return bowtie, connection_ref

def get_tpiece(layer, connection_width=8, connection_gap=4, height=200, straight_extra=400, tlen=200, tside=None):
    tpiece_tot = KleLayoutElement()
    straight_piece, _ = get_routed_cpw(layer, [(0, 0), (0, -height/2), (0, -height-straight_extra)], width=connection_width, gap=connection_gap)
    tpiece = KleCutOut(straight_piece)
    tpiece_tot.add_element(tpiece)

    if tside is None:
        return tpiece_tot
    
    elif tside == "left":
        extra_piece, _ = get_routed_cpw(layer, [(-connection_gap-connection_width/2, -height/2), (-tlen/2, -height/2), (-tlen, -height/2), (-tlen, -height)], width=connection_width, gap=connection_gap)
        tpiece_tot.add_element(extra_piece)
        tpiece.add_element(create_shape(layers["SC"], [
            (-connection_gap-connection_width/2, -height/2 - connection_width/2), (-connection_width/2, -height/2 - connection_width/2),
            (-connection_width/2, -height/2 + connection_width/2), (-connection_gap-connection_width/2, -height/2 + connection_width/2),
        ]))
        return tpiece_tot
    
    elif tside == "right":
        extra_piece, _ = get_routed_cpw(layer, [(connection_gap+connection_width/2, -height/2), (+tlen/2, -height/2), (+tlen, -height/2), (+tlen, -height)], width=connection_width, gap=connection_gap)
        tpiece_tot.add_element(extra_piece)
        tpiece.add_element(create_shape(layers["SC"], [
            (connection_gap+connection_width/2, -height/2 - connection_width/2), (connection_width/2, -height/2 - connection_width/2),
            (connection_width/2, -height/2 + connection_width/2), (+connection_gap+connection_width/2, -height/2 + connection_width/2),
        ]))
        return tpiece_tot
# === FILTER DEF ===




def get_one_sample_cell(res_len, mid_cap_hwidth, mid_cap_len, Nconn=4):
    # === START RES ===
    PL_CUTOUT_WIDTH = 1000
    EXTRA = 1

    # pl_co is the probe line cutout where to attach everything else
    res_reference = KleLayoutElement() # Keep everything packaged without building
    remove_from_pl = create_shape(layers["SC"], [
        (0, 0), (PL_CUTOUT_WIDTH, 0), (PL_CUTOUT_WIDTH, PL_GAP), (0, PL_GAP)
    ])
    res_reference.add_element(remove_from_pl)

    RES_LEN = res_len
    X0 = PL_CUTOUT_WIDTH/2
    Y0 = PL_GAP/2

    SPACE_FOR_DOT_HW = PL_GAP/2
    SPACE_FOR_DOT_LENGTH = 50

    # EXTRA_HW = 20
    # EXTRA_LEN = 60
    # FANOUT_HW = 1000-140.5
    # FANOUT_LEN = 100 # 100

    fine_res = KleCutOut(
        create_shape(layers["SC_FINE"], [
            (-EXTRA, 0),
            (-SPACE_FOR_DOT_HW + X0, 0), (-SPACE_FOR_DOT_HW + X0, -SPACE_FOR_DOT_LENGTH), # EXTRA FOR ROUTING
            (SPACE_FOR_DOT_HW + X0, -SPACE_FOR_DOT_LENGTH), (SPACE_FOR_DOT_HW + X0, 0), # EXTRA FOR ROUTING
            (PL_CUTOUT_WIDTH + EXTRA, 0), (PL_CUTOUT_WIDTH + EXTRA, PL_GAP), (-EXTRA, PL_GAP)
        ])
    )
    

    trace, _len = get_routed_trace(layers["SC_FINE"], [
        (-RES_LEN/2 + X0, 0), (-RES_LEN/2 + X0, Y0), (RES_LEN/2 + X0, Y0), (RES_LEN/2 + X0, Y0*2)
    ], radii=2, width_start=0.5, width_end=0.5)
    
    fine_res.add_element(trace)
    
    _Z, _f = get_cpw_impedance(0.5, 24.5, LSHEET, EPS, _len)
    print(f"RES Z: {_Z}, freq: {_f/1e9}, len: {_len}")

    # === DOT RESONATOR CONN ===
    fine_res.add_element(create_shape(layers["SC_FINE"], [
        (-mid_cap_hwidth, 0), (mid_cap_hwidth, 0), (mid_cap_hwidth, -SPACE_FOR_DOT_LENGTH), (-mid_cap_hwidth, -SPACE_FOR_DOT_LENGTH)
    ]).move(X0, Y0-0.25))

    res_reference.add_element(fine_res)

    # === GATES AND LEADS ===
    line_ends = []
    existing_ind = []
    N_and_path = {
        0: [(0, -0.25), (-2.5, -0.25), (-10, -0.25)],
        1: [(0, 0), (0, -2.5), (0, -4.5)],
        2: [(0, 0), (0, -2.5), (0, -4.5)],
        3: [(0, -0.25), (2.5, -0.25), (5, -0.25)]
    }

    for n in range(Nconn):
        fout_trace, _ = get_routed_trace(layers["SC_FINE"], N_and_path[n], width_end=0.5, width_start=0.5)
        fine_res.add_element(fout_trace.move(X0 -15 + n * 10, Y0 - 0.25 - SPACE_FOR_DOT_LENGTH - 20))
        # res_reference.add_element(fout_trace)
    #     fout_trace = [
    #         (0, -CAP_WIDTH-mid_cap_len+3), (0, -CAP_WIDTH-14-EXTRA_LEN) # Connection to pad
    #     ]
    #     fout_trace.extend(N4_and_path[n])
    #     conn, fanout_len = get_routed_trace(layers["SC_FINE"], fout_trace, width_end=0.5, width_start=0.5, radii=5)
    #     print("fanout ind", fanout_len * LSHEET/0.5)
    #     existing_ind.append(fanout_len * LSHEET/0.5)
    #     trace.add_element(conn)
    #     endpoint = create_ref(*fout_trace[-1])
    #     trace.add_element(endpoint)

    #     fine_res.add_element(trace.move(n * 5 + X0 - 5 * (Nconn-1)/2, Y0 - 10 - 15))
        
    #     line_ends.append(endpoint)

    # # === END RES ===


    # for i, ep in enumerate(line_ends):
    #     bt, r = get_one_stage_of_bowtie(True if i in [0, 3] else False, existing_ind=existing_ind[i])
    #     x, y = ep.get_absolute_points()[0]
    #     layout.add_element(bt.rotate_right().move(x+112, y-465 + 1)) # 1 um of overlap
    #     res_reference.add_element(bt)
        
    #     _tside="left"

    #     t_piece = get_tpiece(
    #         layers["SC"], connection_width=8, connection_gap=4, height=200, tside=_tside
    #     )
    #     layout.add_element(t_piece.move(x, y-465-80))
    #     res_reference.add_element(t_piece)

    #     port = get_cpw_port(
    #         layers["SC"], connection_width=8,
    #         connection_gap=4, port_gap=10,
    #         port_length=160, port_width=160, taper_length=80
    #     )

    #     port0 = port.get_copy().rotate_left().move(x, y-465-80-200-400)
    #     layout.add_element(port0)
    #     res_reference.add_element(port0)
        
    #     if _tside=="left":
    #         port_co = KleCutOut(create_shape(layers["SC"], [
    #             (-20, -25), (115, -25), (115, 70), (-20, 70)
    #         ]))
    #         port_cap, cval = get_interdigit_cap(layers["SC"], 5, 5, 40, 10, extra_end=False)
    #         port_co.add_element(port_cap)
    #         port_co.add_element(create_shape(
    #             layers["SC"], [
    #                 (0, 0), (8, 0), (8, 20), (0, 20)
    #             ]
    #         ).move(45-1.5, 50))
    #         port_co.add_element(create_shape(
    #             layers["SC"], [
    #                 (0, 0), (8, 0), (8, 20), (0, 20)
    #             ]
    #         ).move(45-1.5, -25))

    #         port1 = port.get_copy().rotate_left().move(x - 200, y-465-80-200-95)
    #         port1.add_element(port_co.move(x-200-47.55, y-465-280-70))
            
    #         layout.add_element(port1)
    #         res_reference.add_element(port1)
    #         _tside="left"
    #     elif _tside=="right":
    #         port1 = port.get_copy()
    #         layout.add_element(port1.flip_horizontally().move(x+200, y-465-180))
    #         res_reference.add_element(port1)
    
    return res_reference, remove_from_pl, fine_res #, ref_dot


res_0, rpl_0, fr_0 = get_one_sample_cell(800, 0.5, 50, Nconn=4)
# === ADD ===
res_0.move(3000, 4830)
pl_co.add_element(rpl_0)
layout.add_element(fr_0)



res_2, rpl_2, fr_2 = get_one_sample_cell(900, 0.5, 50, Nconn=3)
# === ADD ===
res_2.move(6000, 4830).flip_vertically().move(0, 340)
pl_co.add_element(rpl_2)
layout.add_element(fr_2)


# === TEMP ==== FOR DOSE TEST
def get_meander_path(height, step, N):
    path = [
        (-20, 0)
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

    path = path[:-1] + [(height * ((i+1)%2), -step * (i + 0.5)), (path[-1][0], path[-1][1]-20)]

    return path


# poss = [
#     (50, 300), (250, 300), (50, 140), (250, 140)
# ]
# H, S = 100, 2
# DT_cutout = KleCutOut(create_shape(layers["SC"], [
#     (0, 0), (400, 0), (400, 400), (0, 400)
# ]))
# for W, pos in zip([0.1, 0.25, 0.5, 1], poss):
# # W = 0.5
#     S = W * 2.5
#     DT_trace, _ = get_routed_trace(layers["SC"], get_meander_path(H, S, 30), width_start=W, width_end=W, radii=W*1.2)
#     DT_cutout.add_element(DT_trace.move(*pos))

# layout.add_element(DT_cutout)

layout.build_to_file(
    # r"/home/jyrgen/Documents/PhD/design_files/B00_63pH_11_7eps_20250613.gds"
    r"C:\Users\jyrgen\Documents\PhD\design\gds_files\B00_63pH_11_7eps_20250616.gds"
)