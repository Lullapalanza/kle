"""
Test dot design TD00 - design used for testing the generation of some elements

I uess with this one I want to try and implement automatic routing for the fanout?
Maybe also bounding boxes? That way I can have margins without having to move things myself and autocentering?
"""

from kle.layout.layout import KleLayout, KleLayoutElement, KleShape, create_shape
from kle.layout.dot_elements import (
    get_Lazar_global_markers,
    get_dot_with_leads,
    get_andreev_dot_with_loop,
)
from kle.layout.layout_trace_routing import get_routed_trace

LAYER_NAMES = [
    "-CHIP",
    "MARKERS",
    "LM0",
    "LM1",
    "LM2",
    "LM3",
    "OHMICS_0",
    "GATES0_0",
    "GATES1_0",
]

layout = KleLayout(6000, 6000, LAYER_NAMES)
layers = layout.get_layers()

layout.add_element(get_Lazar_global_markers(layers["MARKERS"]))


# ==== START BOND PADS ====
def create_bond_pads_for_quadrant(layer):
    bond_pads = KleLayoutElement("bp")

    width = 160
    height = 160
    spacing = 160 + 50

    pad = create_shape(layer, [
        (-width/2, -height/2),
        (width/2, -height/2),
        (width/2, height/2),
        (-width/2, height/2)
    ])

    for i in range(1, 8):
        bond_pads.add_element(pad.get_copy().move(i*spacing, 0))
        bond_pads.add_element(pad.get_copy().move(i*spacing, -1680))
        
    for i in range(7):
        bond_pads.add_element(pad.get_copy().move(0, -(i+1) * spacing))
        bond_pads.add_element(pad.get_copy().move(1680, -(i+1) * spacing))
        
    bond_pads.move(-1680/2, 1680/2)

    return bond_pads
# ==== END BOND PADS ====



# ==== LOCAL MARKERS FOR 4 QUADRANTS ====
lm_l_pos = [
    ("LM0", 1775, 4175),
    ("LM1", 3925, 4175),
    ("LM2", 1775, 2025),
    ("LM3", 3925, 2025),
]

for l, x, y in lm_l_pos:
    lm = KleLayoutElement(f"Local markers {l}")
    lms = create_shape(
        layers[l], [
            (-11, -1.25), (-1.25, -1.25), (-1.25, -11), (1.25, -11), (1.25, -1.25),
            (11, -1.25), (11, 1.25), (1.25, 1.25), (1.25, 11), (-1.25, 11),
            (-1.25, 1.25), (-11, 1.25)
        ]
    )
    positions = [
        (0, 0), (20, -20), (40, -40),
        (300, 0), (280, -20), (260, -40),
        (0, -300), (20, -280), (40, -260),
        (300, -300), (280, -280), (260, -260)
    ]
    for p in positions:
        lm.add_element(lms.get_copy().move(*p))
    layout.add_element(lm.move(x, y))
    
    layout.add_element(create_bond_pads_for_quadrant(layers["MARKERS"]).move(x+150, y-150))
# ==== END LOCAL MARKERS ====

bias_x=-0.00
bias_y=-0.00
barrier_points = [
    (0 - bias_x, -0.060 - bias_y),
    (0.05 + bias_x, -0.060 - bias_y),
    (0.05 + bias_x, 0.060 + bias_y), 
    (0 - bias_x, 0.060 + bias_y)
]
dot_shift = 0.065
barrier_shift = (dot_shift - 0.05)/2

def get_charge_sensed_ad(r_cs, r_ad):
    CS_AD = KleLayoutElement("charge sensed Andreev Dot")
    CS_AD.add_element(get_dot_with_leads(
        layers["OHMICS_0"],
        layers["GATES0_0"],
        layers["GATES1_0"],
        dot_r=r_cs,
        bias_x=-0.00,
        bias_y=-0.00,
        barrier_height=0.05
    ))
    CS_AD.add_element(get_andreev_dot_with_loop(
        layers["OHMICS_0"],
        layers["GATES0_0"],
        layers["GATES1_0"],
        dot_r=r_ad,
        top_lead_rotation=45,
        loop_area=200,
        loop_width=20,
        bias_x=-0.00,
        bias_y=-0.00,
        plunger_rotation=73,
        barrier_height=0.05
    ).move(r_cs + r_ad + dot_shift, 0))
    barrier = create_shape(layers["GATES0_0"], barrier_points)
    CS_AD.add_element(barrier.move(r_cs + barrier_shift, 0))
    return CS_AD


first_quadrant = KleLayoutElement("first quadrant")

SL_WIDTH = 0.5
mirror_shift = 20 + 0.5
up_shift = 10 + 0.17 + SL_WIDTH + 0.2

right_side = get_charge_sensed_ad(0.175/2, 0.175/2)
first_quadrant.add_element(right_side.move(0, up_shift))

left_side = get_charge_sensed_ad(0.175/2, 0.2/2)
first_quadrant.add_element(
    left_side.move(mirror_shift, -up_shift).flip_horizontally().flip_vertically()
)

first_quadrant.move(-mirror_shift/2, up_shift/2)
first_quadrant.move(1775 + 150, 4175 - 150)

layout.add_element(first_quadrant)


from klayout.db import DText, DTrans

txt = DText("Hello", 0, 0)
layout.main_cell.shapes(1).insert(txt)


layout.build_to_file("C:/Users/nbr720/Documents/PhD/design/design_files/TD00.dxf")
