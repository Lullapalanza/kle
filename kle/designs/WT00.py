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
from kle.layout.resonator_elements import get_cpw_LC, get_C



import scipy.special as sp
import numpy as np

eps_0 = 8.8542e-12
mu_0 = np.pi * 4e-7


LSHEET = 200e-12 # 350e-12 # 260e-12 # pH/sq (matches material I thought was 200pH - need to figure out how to get the calc to put 2um meander at 5.5e9, 0.5um at 6e9 ish)
EPS = 11.7

N_wires = 25

LAYER_NAMES = [
    "MARKERS", "GUIDE", "AU0", "AU1", #, "MARKER_0", "MARKER_1"
]

layout = KleLayout(6000, 6000, LAYER_NAMES)
layers = layout.get_layers()

# === START BORDER ===
border_shape = create_shape(layers["GUIDE"], [
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
    small_arm = create_shape(layers["MARKERS"], [
        (-10, -1), (-10, 1), (10, 1), (10, -1)
    ])
    op_marker.add_element(small_arm.get_copy())
    op_marker.add_element(small_arm.get_copy().rotate_right())
    
    big_arm = create_shape(layers["MARKERS"], [
        (10, -5), (10, 5), (100, 5), (100, -5)
    ])
    op_marker.add_element(big_arm.get_copy())
    op_marker.add_element(big_arm.get_copy().rotate_by_angle(90))
    op_marker.add_element(big_arm.get_copy().rotate_by_angle(180))
    op_marker.add_element(big_arm.get_copy().rotate_by_angle(270))
    return op_marker

def get_global_EBL():
    marker = KleLayoutElement()
    # small_arm = create_shape(layers["MARKERS"], [
    #     (-6, -0.25), (-6, 0.25), (6, 0.25), (6, -0.25)
    # ])
    # marker.add_element(small_arm.get_copy())
    # marker.add_element(small_arm.get_copy().rotate_right())

    big_arm = create_shape(layers["MARKERS"], [
        (0, -2.5), (0, 2.5), (90, 2.5), (90, -2.5)
    ])
    marker.add_element(big_arm.get_copy())
    marker.add_element(big_arm.get_copy().rotate_by_angle(90))
    marker.add_element(big_arm.get_copy().rotate_by_angle(180))
    marker.add_element(big_arm.get_copy().rotate_by_angle(270))

    return marker

def get_local_EBL():
    marker = KleLayoutElement()
    arm = create_shape(layers["MARKERS"], [
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

# layout.add_element(get_global_EBL().move(1000, 1000))
# layout.add_element(get_global_EBL().move(1000, 5000))
# layout.add_element(get_global_EBL().move(5000, 5000))
# layout.add_element(get_global_EBL().move(5000, 1000))


layout.add_element(get_global_EBL().move(750, 750))
layout.add_element(get_global_EBL().move(750, 5250))
layout.add_element(get_global_EBL().move(5250, 5250))
layout.add_element(get_global_EBL().move(5250, 750))

layout.add_element(create_shape(layers["MARKERS"], [(-200, -20), (200, -20), (200, 20), (-200, 20)]).move(3000, 800))



def get_contact_test(width, gap, overlap, goldlayer, nbtin_under):
    _all = KleLayoutElement()

    pads = KleCutOut(create_shape(layers["MARKERS"], (
        (-500, -250), (-500, 250), (500, 250), (500, -250)
    )))

    bondpad = create_shape(layers["MARKERS"], (
        (-200, -200), (-200, 200), (200, 200), (200, -200)
    ))

    pads.add_element(bondpad.get_copy().move(-200 - gap/2, 0))
    pads.add_element(bondpad.get_copy().move(200 + gap/2, 0))
    _all.add_element(pads)
    

    _all.add_element(create_shape(layers[goldlayer], [
        (-gap/2 - overlap, -width/2), (-gap/2 - overlap, width/2), (+gap/2 + overlap, width/2), (+gap/2 + overlap, -width/2)
    ]))
    if nbtin_under is True:
        pads.add_element(create_shape(layers[goldlayer], [
            (-gap/2, -width/2 +0.5), (-gap/2, width/2-0.5), (+gap/2, width/2 -0.5), (+gap/2, -width/2 + 0.5)
        ]))
    return _all



# layout.add_element(get_contact_test(10, 10, 10))

gaps = [50, 100, 50, 100]
overlaps = [5, 10, 20, 40, 10, 20, 40]

for x, gap in enumerate(gaps):
    for y, overlap in enumerate(overlaps):
        layout.add_element(get_contact_test(
            5, gap, overlap,
            "AU0" if y in [0, 1, 2, 3] else "AU1",
            True if x in [0, 1] else False
        ).move(1500 + x * 1000, 1200 + y * 600))


layout.build_to_file(
    r"/home/jyrgen/Documents/PhD/design_files/CT00_20260331.gds"
)

# layout.add_element(get_optical_marker().move(1000, 1000))
# layout.add_element(get_optical_marker().move(1000, 9000))
# layout.add_element(get_optical_marker().move(9000, 1000))
# layout.add_element(get_optical_marker().move(9000, 9000))


# layout.add_element(get_local_square().move(3580, 4794.))
