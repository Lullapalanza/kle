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



LSHEET = 400e-12 # 63 ph/sq
EPS = 11.7

LAYER_NAMES = [
    "SC", "SC_FINE"#, "MARKER_0", "MARKER_1"
]
layout = KleLayout(10000, 10000, LAYER_NAMES)
layers = layout.get_layers()

# === START BORDER ===
border_shape = create_shape(layers["SC"], [
    [0, 0], [5000, 0], [5000, 100], [0, 100]
])
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
PL_WIDTH = 350
PL_GAP = 2
PL_LENGTH = 3500

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

PORT_GAP = 20 * PL_GAP
PORT_WIDTH = 2 * PL_WIDTH
PORT_LEN = 300

# ==== PL ====
pl.add_element(
    get_cpw_port(layers["SC"], PL_WIDTH, PL_GAP, port_gap=PORT_GAP, port_width=PORT_WIDTH, port_length=PORT_LEN, taper_length=200)
)
pl.add_element(
    get_cpw_port(layers["SC"], PL_WIDTH, PL_GAP, port_gap=PORT_GAP, port_width=PORT_WIDTH, port_length=PORT_LEN, taper_length=200).flip_horizontally().move(PL_LENGTH, 0)
)

# cut_step = PL_WIDTH/5
# pl_cut, _ = get_routed_trace(layers["SC"], [
#     (0, 0), (0, cut_step), (-500, cut_step), (-500, cut_step*2), (500, cut_step*2), (500, cut_step*3), (-500, cut_step*3),
#     (-500, cut_step*4), (0, cut_step*4), (0, cut_step*5)
# ], width_start=1, width_end=1, radii=5)
# pl.add_element(pl_cut.move(PL_LENGTH/2, -PL_WIDTH/2))

port_imp, _ = get_cpw_impedance(PORT_WIDTH, PORT_GAP, L_sheet=LSHEET, eps=EPS)
print("port imp", port_imp)

pl_imp, pl_freq = get_cpw_impedance(PL_WIDTH, PL_GAP, L_sheet=LSHEET, eps=EPS, l=pl_length + 2*PORT_LEN)
print("Probe line impedance:", pl_imp, "freq:", pl_freq/1e9)

# pl_co = KleCutOut(pl.move(460 + 500 + 220 + 620, 5000))

# layout.add_element(pl_co)
PL_CO.add_element(pl.move(750, 1000))
layout.add_element(PL_CO.move(500, 2000))

print("=== PL END ===")
# === END PL ===


layout.build_to_file(
    r"/home/jyrgen/Documents/PhD/design_files/MR00_400pH_11_7eps_20250829.gds"
)