"""
USC design 2026/04/27
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


LSHEET = 200e-12 # 350e-12 # 260e-12 # pH/sq (matches material I thought was 200pH - need to figure out how to get the calc to put 2um meander at 5.5e9, 0.5um at 6e9 ish)
EPS = 11.7


LAYER_NAMES = [
    "MARKERS", "BORDER", "SC_FINE0", "SC_FINE1", "SC_FINE2", "SC_FINE3", "SC", "LARGE_AL"
]

layout = KleLayout(6000, 6000, LAYER_NAMES)
layers = layout.get_layers()


# === START BORDER ===
border_shape = create_shape(layers["BORDER"], [
    [0, 0], [5000, 0], [5000, 100], [0, 100]
])

border_square_0 = create_shape(layers["SC"], [
    [0, 0], [10, 0], [10, 10], [0, 10]
])
# border_square_1 = create_shape(layers["SC_FINE"], [
#     [0, 0], [10, 0], [10, 10], [0, 10]
# ])

layout.add_element(border_square_0.move(500, 500))
# layout.add_element(border_square_1.move(500, 500))

layout.add_element(border_square_0.get_copy().move(4990, 0))
# layout.add_element(border_square_1.get_copy().move(4990, 0))

layout.add_element(border_square_0.get_copy().move(4990, 4990))
# layout.add_element(border_square_1.get_copy().move(4990, 4990))

layout.add_element(border_square_0.get_copy().move(0, 4990))
# layout.add_element(border_square_1.get_copy().move(4990, 4990))


layout.add_element(border_shape.move(500, 500))
layout.add_element(border_shape.get_copy().move(0, 4900))
layout.add_element(border_shape.get_copy().rotate_right().move(0, 5000))
layout.add_element(border_shape.get_copy().rotate_right().move(5000-100, 5000))
# === END BORDER ===



# === DEF MARKER ===
def get_global_marker():
    marker = KleLayoutElement()
    small_arm = create_shape(layers["MARKERS"], [
        (-10, -1), (-10, 1), (10, 1), (10, -1)
    ])
    marker.add_element(small_arm.get_copy())
    marker.add_element(small_arm.get_copy().rotate_right())

    big_arm = create_shape(layers["MARKERS"], [
        (10, -5), (10, 5), (50, 5), (50, -5)
    ])
    marker.add_element(big_arm.get_copy())
    marker.add_element(big_arm.get_copy().rotate_by_angle(90))
    marker.add_element(big_arm.get_copy().rotate_by_angle(180))
    marker.add_element(big_arm.get_copy().rotate_by_angle(270))

    return marker

def get_wire_marker():
    marker = KleLayoutElement()
    arm = create_shape(layers["MARKERS"], [
        (-1, -0.1), (-1, 0.1), (1, 0.1), (1, -0.1)
    ])
    marker.add_element(arm.get_copy())
    marker.add_element(arm.get_copy().rotate_right())
    return marker


def get_small_marker():
    marker = KleLayoutElement()
    arm = create_shape(layers["MARKERS"], [
        (-10, -1), (-10, 1), (10, 1), (10, -1)
    ])
    marker.add_element(arm.get_copy())
    marker.add_element(arm.get_copy().rotate_right())
    return marker

def get_wire_marker_square():
    marker_square = KleLayoutElement()
    marker_square.add_element(get_wire_marker().move(-5, -5))
    marker_square.add_element(get_wire_marker().move(-5, 5))
    marker_square.add_element(get_wire_marker().move(5, 5))
    marker_square.add_element(get_wire_marker().move(5, -5))
    return marker_square
# === END MARKERS ===

# === MAKE MARKERS ===
for x in range(5):
    layout.add_element(get_global_marker().move(1000 + x * 250, 1000))
    layout.add_element(get_global_marker().move(5000 - x * 250, 1000))
    layout.add_element(get_global_marker().move(1000 + x * 250, 5000))
    layout.add_element(get_global_marker().move(5000 - x * 250, 5000))

for y in range(4):
    layout.add_element(get_global_marker().move(1000, 1250 + y * 250))
    layout.add_element(get_global_marker().move(5000, 1250 + y * 250))
    layout.add_element(get_global_marker().move(1000, 4750 - y * 250))
    layout.add_element(get_global_marker().move(5000, 4750 - y * 250))

layout.add_element(create_shape(layers["MARKERS"], [(-250, -50), (250, -50), (250, 50), (-250, 50)]).move(3000, 1000))
# === END MAKE MARKERS ===


# === START PROBE LINE ===
print("=== PL ===")
PL_WIDTH = 230 # 115 # 80 # 350
PL_GAP = 4
PL_LENGTH = 3400

PL_CO = KleCutOut(create_shape(layers["SC"], [
    (500, 500), (5500, 500), (5500, 5500), (500, 5500)
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

PL_CO.add_element(pl.move(1000 + 560/2, 3000))
layout.add_element(PL_CO)

print("=== PL END ===")
# === END PROBE LINE ===


# === START RESONATORS ===
def get_resonator_path(w, N, gap, arm_len, end_len=15):
    path = [(-3-gap-w, end_len-3), (-gap -w, end_len-3), (-gap -w, 0), (0, 0), (arm_len, 0)]
    lp = path[-1]
    for i in range(N-1):
        dir = -1 if i%2 == 0 else 1
        path += [(lp[0], lp[1] + gap + w), (lp[0] + dir * arm_len, lp[1] + gap + w)]
        lp = path[-1]

    path += [(-gap -w, lp[1]), (-gap -w, lp[1]-end_len+3), (-gap-w-3, lp[1]-end_len+3)]

    return path, path[0], path[-1]


def Kbrim(k):
    return sp.ellipk((1-k**2)**0.5)

def K(k):
    return sp.ellipk(k)

def fk(w, gap):
    a = w/2
    b = (w+gap)/2
    return np.tan(a * np.pi/(4 * b))**2

def get_interdigit_C(k, L, n):
    return (L*(n-1)/1e6)*(K(k)/Kbrim(k)) * 0.5 * (EPS + 1) * 1e-3 / (18 * np.pi)



# === RESONATOR 0 (left bottom) ===
path0, start0, end0 = get_resonator_path(0.5, 16, 2.7, 29.86+0.5)
shape, length = get_routed_trace(layers["SC_FINE0"], path=path0, width_start=0.5, width_end=0.5, radii=1)
shape.add_element(create_shape(layers["SC_FINE0"], [(0, 0), (3.25, 0), (3.25, 2), (0, 2)]).move(*start0).move(0, -1))
shape.add_element(create_shape(layers["SC_FINE0"], [(0, 0), (3.25, 0), (3.25, 2), (0, 2)]).move(*end0).move(0, -1))

# Resonator 0
PL_CO.add_element(create_shape(layers["SC"], [(0, 0), (300, 0), (300, 300), (0, 300)]).move(1900 + 300, 2581))
layout.add_element(shape.move(2050 + 300, 2727+50))
layout.add_element(get_wire_marker_square().move(2310+18, 2790+5))

# Resonator 1
PL_CO.add_element(create_shape(layers["SC"], [(0, 0), (300, 0), (300, 300), (0, 300)]).move(1900 + 20-300, 2581+538))
path0, start0, end0 = get_resonator_path(0.5, 16, 2.7, 29.86+0.5+3.5)
shape, length = get_routed_trace(layers["SC_FINE1"], path=path0, width_start=0.5, width_end=0.5, radii=1)
shape.add_element(create_shape(layers["SC_FINE1"], [(0, 0), (3.25, 0), (3.25, 2), (0, 2)]).move(*start0).move(0, -1))
shape.add_element(create_shape(layers["SC_FINE1"], [(0, 0), (3.25, 0), (3.25, 2), (0, 2)]).move(*end0).move(0, -1))
layout.add_element(shape.flip_horizontally().move(2050 - 270, 2727+450))
layout.add_element(get_wire_marker_square().move(2050 - 270+22, 2727+450+32))


# Resonator 2
PL_CO.add_element(create_shape(layers["SC"], [(0, 0), (300, 0), (300, 300), (0, 300)]).move(1900 + 1900-300, 2581+538))
path0, start0, end0 = get_resonator_path(0.35, 22, 1.221, 22.765-0.273, end_len=11.4)
shape, length = get_routed_trace(layers["SC_FINE2"], path=path0, width_start=0.350, width_end=0.350, radii=0.5)
shape.add_element(create_shape(layers["SC_FINE2"], [(0, 0), (3.25, 0), (3.25, 2), (0, 2)]).move(*start0).move(0, -1))
shape.add_element(create_shape(layers["SC_FINE2"], [(0, 0), (3.25, 0), (3.25, 2), (0, 2)]).move(*end0).move(0, -1))
layout.add_element(shape.move(4000+237, 2727+70))
layout.add_element(get_wire_marker_square().move(4000+237+22-42.6, 2727+70+32-18.6))


# Resonator 3
PL_CO.add_element(create_shape(layers["SC"], [(0, 0), (300, 0), (300, 300), (0, 300)]).move(1900 + 1900 + 280, 2581))
path0, start0, end0 = get_resonator_path(0.35, 24, 1.221, 22.765-0.273+0.7, end_len=11.4)
shape, length = get_routed_trace(layers["SC_FINE3"], path=path0, width_start=0.350, width_end=0.350, radii=0.5)
shape.add_element(create_shape(layers["SC_FINE3"], [(0, 0), (3.25, 0), (3.25, 2), (0, 2)]).move(*start0).move(0, -1))
shape.add_element(create_shape(layers["SC_FINE3"], [(0, 0), (3.25, 0), (3.25, 2), (0, 2)]).move(*end0).move(0, -1))
layout.add_element(shape.flip_horizontally().move(4000-350, 2727+450-10))
layout.add_element(get_wire_marker_square().move(4000-350+20, 2727+450+12))


# === gate/lead connection ===
from kle.layout.resonator_elements import get_C

def get_pad_filter_line(end_path=None, add_extra=False):
    end_path = end_path or []
    line_connection = KleLayoutElement()
    
    filter_cap = get_interdigit_C(fk(5e-6, 5e-6), 70.5e-6, 15) * 2
    filter_ind =  500 * LSHEET

    print("filter cap target:", filter_cap, "filter ind target:", filter_ind)
    print("filter f target", 1/(2e9*np.pi * (filter_cap * filter_ind)**0.5), "imp:", (filter_ind/filter_cap)**0.5)

    bondpad_hole = create_shape(layers["SC"], [(0, 0), (0, 220+200+150), (220, 220+200+150), (220, 0)])
    
    bondpad = create_shape(layers["SC"], [(10, 10), (10, 210), (210, 210), (210, 10)])
    filter_ind_path = [(110, 210), (110, 240), (170, 240)]
    step_x, step_y = 120, 23
    for _ in range(3):
        filter_ind_path.append((filter_ind_path[-1][0], filter_ind_path[-1][1] + step_y))
        filter_ind_path.append((filter_ind_path[-1][0]-step_x, filter_ind_path[-1][1]))
        filter_ind_path.append((filter_ind_path[-1][0], filter_ind_path[-1][1] + step_y))
        filter_ind_path.append((filter_ind_path[-1][0]+step_x, filter_ind_path[-1][1]))

    filter_ind_path.append((filter_ind_path[-1][0], filter_ind_path[-1][1] + step_y))
    filter_ind_path.append((filter_ind_path[-1][0]-step_x/2, filter_ind_path[-1][1]))
    filter_ind_path.append((filter_ind_path[-1][0], filter_ind_path[-1][1] + step_y-4+10))

    filter_inductance, filter_ind_len = get_routed_trace(layers["SC"], filter_ind_path, width_start=2, width_end=2, radii=5)
    print("filter inductance len", filter_ind_len, LSHEET * filter_ind_len/2)

    # cap
    interdigit_cap = KleLayoutElement()
    N_finger, W, G, L = 15, 5, 5, 70
    for n in range(N_finger):
        interdigit_cap.add_element(
            create_shape(layers["LARGE_AL"], [
                [0, 0],
                [W, 0],
                [W, L],
                [0, L]
            ]).move(n * (W + G), (n%2)*G)
        )
    end_conn = create_shape(layers["LARGE_AL"], [
        [-0, 0],
        [-0, -W],
        [(W + G) * N_finger - G, -W],
        [(W + G) * N_finger - G, 0]
    ])
    interdigit_cap.add_element(end_conn)
    interdigit_cap.add_element(end_conn.get_copy().move(0, L + G + W))

    # ===
    interdigit_cap.rotate_right()


    other_side = interdigit_cap.get_copy()
    other_side.flip_horizontally().move(-2*W, 0)


    layout.add_element(bondpad)
    layout.add_element(filter_inductance)


    
    PL_CO.add_element(bondpad_hole, update_origin=False)
    line_connection.add_element(bondpad_hole)
    line_connection.add_element(bondpad)
    line_connection.add_element(filter_inductance)
    line_connection.add_element(interdigit_cap.move(115, 420+145))
    line_connection.add_element(other_side.move(115, 420+145))

    interdigit_cap.add_element(create_shape(layers["LARGE_AL"], [(25, 420), (-10, 420), (-10, 420 + 150), (25, 420+150)]))
    other_side.add_element(create_shape(layers["LARGE_AL"], [(35, 420), (0, 420), (0, 420 + 150), (35, 420+150)]).move(195, 0))
    filter_endpoint = create_ref(110, 570)
    line_connection.add_element(filter_endpoint)


    line_start_x, line_start_y = filter_endpoint.get_absolute_points()[0]
    line_path = [
        (line_start_x, line_start_y),
        (line_start_x, line_start_y + 200),
        (line_start_x, line_start_y + 400) 
    ]
    line_path.extend([(ep[0] + line_path[-1][0], ep[1] + line_path[-1][1]) for ep in end_path])
    line_elem, line_len = get_routed_trace(layers["SC"], path=line_path, width_end=34, width_start=34, radii=60)
    line_elem_al, _ = get_routed_trace(layers["LARGE_AL"], path=line_path, width_end=26, width_start=26, radii=60)

    PL_CO.add_element(line_elem)
    line_connection.add_element(line_elem)
    line_connection.add_element(line_elem_al)

    lineZ, linef = get_cpw_impedance(center_width=26, gap=4, L_sheet=0, eps=EPS, l=line_len)
    print("line connections", lineZ, linef/(2*np.pi*1e9))

    layout.add_element(line_elem_al)

    layout.add_element(interdigit_cap)
    layout.add_element(other_side)

    if add_extra is True:
        x0, y0 = line_path[-1][0], line_path[-1][1]
        shape = create_shape(layers["SC"], [(x0 - 10, y0 - 10), (x0 - 10, y0 + 10), (x0 + 10, y0 + 10), (x0 + 10, y0 - 10)])
        layout.add_element(shape)
        line_connection.add_element(shape)

    return line_connection


def make_lines():
    lines_0 = KleLayoutElement()
    lines_0.add_element(
        get_pad_filter_line(end_path=[(0, 200), (400, 550), (500, 550), (590 + 300, 550)], add_extra=True).move(1200, 1200)
    )
    lines_0.add_element(
        get_pad_filter_line(end_path=[(0, 200), (150 + 150, 500), (450, 500), (290 + 300, 500)]).move(1200 + 1 * 300, 1200)
    )
    lines_0.add_element(
        get_pad_filter_line(end_path=[(0, 300), (100, 450), (120, 450), (290, 450)]).move(1200 + 2 * 300, 1200)
    )
    lines_0.add_element(
        get_pad_filter_line(end_path=[(-250+300, 250), (-250+300, 350), (-250+300, 411)]).move(1200 + 3 * 300, 1200)
    )
    lines_0.add_element(
        get_pad_filter_line(end_path=[(-500+300, 300), (-500+300, 380), (-500+300, 411)]).move(1200 + 4 * 300, 1200)
    )
    lines_0.add_element(
        get_pad_filter_line(end_path=[(0, 121), (-750+300, 340), (-750+300, 380), (-750+300, 411)], add_extra=True).move(1200 + 5 * 300, 1200)
    )
    return lines_0

# 0
make_lines()

# 3
make_lines().move(2000-120, 0)

# 1
from kle.layout.layout import KleElementOrigin
make_lines().move(2000-120, 0).update_origin(new_origin=KleElementOrigin(3000, 3000)).flip_vertically().flip_horizontally()

# 2
make_lines().update_origin(new_origin=KleElementOrigin(3000, 3000)).flip_vertically().flip_horizontally()



# === LOCAL MARKERS ===
# 0
marker_positions = [
    (2180, 2820), (2520, 2820), (2180, 2580), (2520, 2580),
    (2180-30, 2820-30), (2520+30, 2820-30), (2180-30, 2580-30), (2520+30, 2580-30),
    (2180-60, 2820-00), (2520+60, 2820-00), (2180-60, 2580-00), (2520+60, 2580-00),
    (2180-90, 2820-30), (2520+90, 2820-30), (2180-90, 2580-30), (2520+90, 2580-30),
]
m0, m1 = 0, 0
for m in marker_positions:
    layout.add_element(get_small_marker().move(m[0]+m0, m[1]+m1))



# 1
marker_positions = [
    (2180, 2820), (2520, 2820), (2180, 2580), (2520, 2580),
    (2180-30, 2820-30), (2520+30, 2820-30), (2180-30, 2580-30), (2520+30, 2580-30),
    (2180-60, 2820-00), (2520+60, 2820-00), (2180-60, 2580-00), (2520+60, 2580-00),
    (2180-90, 2820-30), (2520+90, 2820-30), (2180-90, 2580-30), (2520+90, 2580-30),
]
m0, m1 = -580, 630
for m in marker_positions:
    layout.add_element(get_small_marker().move(m[0]+m0, m[1]+m1))



# 2
marker_positions = [
    (2180, 2820), (2520, 2820), (2180, 2580), (2520, 2580),
    (2180-30, 2820-30), (2520+30, 2820-30), (2180-30, 2580-30), (2520+30, 2580-30),
    (2180-60, 2820-00), (2520+60, 2820-00), (2180-60, 2580-00), (2520+60, 2580-00),
    (2180-90, 2820-30), (2520+90, 2820-30), (2180-90, 2580-30), (2520+90, 2580-30),
]
m0, m1 = 1880, 0
for m in marker_positions:
    layout.add_element(get_small_marker().move(m[0]+m0, m[1]+m1))


# 3
marker_positions = [
    (2180, 2820), (2520, 2820), (2180, 2580), (2520, 2580),
    (2180-30, 2820-30), (2520+30, 2820-30), (2180-30, 2580-30), (2520+30, 2580-30),
    (2180-60, 2820-00), (2520+60, 2820-00), (2180-60, 2580-00), (2520+60, 2580-00),
    (2180-90, 2820-30), (2520+90, 2820-30), (2180-90, 2580-30), (2520+90, 2580-30),
]
m0, m1 = -580+1880, 630
for m in marker_positions:
    layout.add_element(get_small_marker().move(m[0]+m0, m[1]+m1))
# ====


layout.build_to_file(
    r"/home/jyrgen/Documents/PhD/design_files/USC07_20260427.dxf"
)