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
    "MARKERS", "SC_FINE", "SC", "BORDER"
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

def get_small_marker():
    marker = KleLayoutElement()
    arm = create_shape(layers["MARKERS"], [
        (-10, -0.5), (-10, 0.5), (10, 0.5), (10, -0.5)
    ])
    marker.add_element(arm.get_copy())
    marker.add_element(arm.get_copy().rotate_right())
    return marker
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
shape, length = get_routed_trace(layers["SC_FINE"], path=path0, width_start=0.5, width_end=0.5, radii=1)
shape.add_element(create_shape(layers["SC_FINE"], [(0, 0), (3.25, 0), (3.25, 2), (0, 2)]).move(*start0).move(0, -1))
shape.add_element(create_shape(layers["SC_FINE"], [(0, 0), (3.25, 0), (3.25, 2), (0, 2)]).move(*end0).move(0, -1))

PL_CO.add_element(create_shape(layers["SC"], [(0, 0), (300, 0), (300, 300), (0, 300)]).move(1900, 2581))
layout.add_element(shape.move(2050, 2727))


from kle.layout.resonator_elements import get_C

filter_cap = get_interdigit_C(fk(5e-6, 5e-6), 70.5e-6, 15) * 2
filter_ind =  500 * LSHEET

print("filter cap target:", filter_cap, "filter ind target:", filter_ind)
print("filter f target", 1/(2e9*np.pi * (filter_cap * filter_ind)**0.5), "imp:", (filter_ind/filter_cap)**0.5)

lineZ, linef = get_cpw_impedance(center_width=30, gap=2, L_sheet=0, eps=EPS, l=1000)
print("line connections", lineZ, linef/(2*np.pi*1e9))


# === gate/lead connection ===

line_connection = KleLayoutElement()
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
filter_ind_path.append((filter_ind_path[-1][0], filter_ind_path[-1][1] + step_y-4))

filter_inductance, filter_ind_len = get_routed_trace(layers["SC"], filter_ind_path, width_start=2, width_end=2, radii=5)
print("filter inductance len", filter_ind_len, LSHEET * filter_ind_len/2)

# cap
interdigit_cap = KleLayoutElement()
N_finger, W, G, L = 15, 5, 5, 70
for n in range(N_finger):
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


line_connection.add_element(bondpad_hole)
line_connection.add_element(bondpad)
line_connection.add_element(filter_inductance)
line_connection.add_element(interdigit_cap.move(115, 420+145))
line_connection.add_element(other_side.move(115, 420+145))

interdigit_cap.add_element(create_shape(layers["SC"], [(25, 420), (0, 420), (0, 420 + 150), (25, 420+150)]))
other_side.add_element(create_shape(layers["SC"], [(25, 420), (0, 420), (0, 420 + 150), (25, 420+150)]).move(195, 0))
line_connection.move(1000, 1000)

PL_CO.add_element(bondpad_hole)

layout.add_element(interdigit_cap)
layout.add_element(other_side)


# ===

layout.build_to_file(
    r"/home/jyrgen/Documents/PhD/design_files/USC07_20260427.gds"
)