"""
Test dot design TD00 - design used for testing the generation of some elements

I uess with this one I want to try and implement automatic routing for the fanout?
Maybe also bounding boxes? That way I can have margins without having to move things myself and autocentering?
"""

from kle.layout.layout import KleLayout, KleLayoutElement, KleShape, create_shape, create_annotation
from kle.layout.dot_elements import (
    get_Lazar_global_markers,
    get_dot_with_leads,
    get_andreev_dot_with_loop,
)
from kle.layout.layout_trace_routing import get_routed_trace
from kle.layout.layout_connections import get_polygon_with_connection, get_trace_between_connections


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
    "ANNOTATIONS"
]

layout = KleLayout(6000, 6000, LAYER_NAMES)
layers = layout.get_layers()

layout.add_element(get_Lazar_global_markers(layers["MARKERS"]))




# ==== START BOND PADS ====
def create_bond_pads_for_quadrant(layer):
    port_gen = (i for i in range(8*4))
    pad_map = dict()

    width = 160
    height = 160
    spacing = 160 + 50

    pad = create_shape(layer, [
        (-width/2, -height/2),
        (width/2, -height/2),
        (width/2, height/2),
        (-width/2, height/2)
    ])

    connection_larger_width = 30
    connection_smaller_width = 4
    spacing_small = 16
    tot_small_width = 176 - 32

    def get_pads():
        bond_pads = KleLayoutElement()
        for i in range(1, 9):
            bond_pads.add_element(pad.get_copy().move(i*spacing, 0))
            bond_pads.add_element(
                create_shape(layer, [
                    (i*spacing - connection_larger_width/2, -height/2),
                    (i*spacing + connection_larger_width/2, -height/2),
                    (1890/2 - tot_small_width/2 + i*spacing_small + connection_smaller_width/2, -930 + height/2),
                    (1890/2 - tot_small_width/2 + i*spacing_small - connection_smaller_width/2, -930 + height/2),
                ])
            )
            # Add port
            c_id = next(port_gen)
            
            port = get_polygon_with_connection(layers["ANNOTATIONS"], layers["ANNOTATIONS"], f"P{c_id}", [0, 0, 0, -1]).move(
                1890/2 - tot_small_width/2 + i*spacing_small, -930 + height/2
            )
            pad_map[c_id] = port.connection
            bond_pads.add_element(port)

        bond_pads.shift_origin(1890/2, -1890/2)
        bond_pads.move(-1890/2, 1890/2)
        return bond_pads, pad_map

    all_sides = KleLayoutElement()
    pads0, map0 = get_pads()
    pads1, map1 = get_pads()
    pads2, map2 = get_pads()
    pads3, map3 = get_pads()
    all_sides.add_elements([pads0, pads1.rotate_right(), pads2.rotate_right().rotate_right(), pads3.rotate_left()])
    bp_map = map0 | map1 | map2 | map3
    return all_sides, bp_map
# ==== END BOND PADS ====



# ==== LOCAL MARKERS FOR 4 QUADRANTS ====
lm_l_pos = [
    ("LM0", 1775, 4175),
    # ("LM1", 3925, 4175),
    # ("LM2", 1775, 2025),
    # ("LM3", 3925, 2025),
]

for l, x, y in lm_l_pos:
    lm = KleLayoutElement()
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

    bpads, ports = create_bond_pads_for_quadrant(layers["MARKERS"])

    layout.add_element(bpads.move(x+150, y-150))
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
    CS_AD = KleLayoutElement()
    dot, con = get_dot_with_leads(
        layers["OHMICS_0"],
        layers["GATES0_0"],
        layers["GATES1_0"],
        layers["ANNOTATIONS"],
        dot_r=r_cs,
        bias_x=-0.00,
        bias_y=-0.00,
        barrier_height=0.05
    )
    CS_AD.add_element(dot)
    CS_AD.add_element(get_andreev_dot_with_loop(
        layers["OHMICS_0"],
        layers["GATES0_0"],
        layers["GATES1_0"],
        layers["ANNOTATIONS"],
        dot_r=r_ad,
        top_lead_rotation=45,
        loop_area=200,
        loop_width=20,
        bias_x=-0.00,
        bias_y=-0.00,
        plunger_rotation=73,
        barrier_height=0.05
    )[0].move(r_cs + r_ad + dot_shift, 0))
    barrier = create_shape(layers["GATES0_0"], barrier_points)
    CS_AD.add_element(barrier.move(r_cs + barrier_shift, 0))
    return CS_AD, con


first_quadrant = KleLayoutElement()

SL_WIDTH = 0.5
mirror_shift = 20 + 0.5
up_shift = 10 + 0.17 + SL_WIDTH + 0.2

right_side, con = get_charge_sensed_ad(0.175/2, 0.175/2)
first_quadrant.add_element(right_side.move(0, up_shift))

left_side, _ = get_charge_sensed_ad(0.175/2, 0.2/2)
first_quadrant.add_element(
    left_side.move(mirror_shift, -up_shift).flip_horizontally().flip_vertically()
)

first_quadrant.move(-mirror_shift/2, up_shift/2)
first_quadrant.move(1775 + 150, 4175 - 150)

layout.add_element(first_quadrant)


p = get_trace_between_connections(layers["OHMICS_0"], con, ports[24], 0.085)
layout.add_element(p)


# BALADASD
c0 = get_polygon_with_connection(layers["LM0"], layers["ANNOTATIONS"], "P0", [0, 0, 0, -1])
c1 = get_polygon_with_connection(layers["LM0"], layers["ANNOTATIONS"], "P1", [0, 0, 0, -1])
layout.add_element(c0)
layout.add_element(c1.move(5, -10).flip_vertically())
p = get_trace_between_connections(layers["LM0"], c0.connection, c1.connection, 1)
layout.add_element(p)


c0 = get_polygon_with_connection(layers["LM0"], layers["ANNOTATIONS"], "P0", [0, 0, 0, -1])
c1 = get_polygon_with_connection(layers["LM0"], layers["ANNOTATIONS"], "P1", [0, 0, 0, -1])
layout.add_element(c0)
layout.add_element(c1.move(-10, -100).flip_vertically())
p = get_trace_between_connections(layers["LM0"], c0.connection, c1.connection, 1)
layout.add_element(p)

layout.build_to_file("C:/Users/nbr720/Documents/PhD/design/design_files/TD00.dxf")
