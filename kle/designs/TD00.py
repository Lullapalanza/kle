"""
Test dot design TD00 - design used for testing the generation of some elements

I uess with this one I want to try and implement automatic routing for the fanout?
Maybe also bounding boxes? That way I can have margins without having to move things myself and autocentering?
"""

from kle.layout.layout import KleLayout, KleLayoutElement, KleShape, create_shape, create_annotation
from kle.layout.dot_elements import (
    get_Lazar_global_markers,
    get_dot_with_leads, DotWLeadsParams,
    get_andreev_dot_with_loop, ADParams,
)
from kle.layout.layout_trace_routing import get_routed_trace
from kle.layout.layout_connections import get_simple_connector, ConnectedElement, get_connector_extention


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
def create_bond_pads_for_quadrant():
    layer = layers["ANNOTATIONS"]
    port_gen = (i for i in range(8*4))

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
        bond_pads = ConnectedElement()
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
            
            port = get_simple_connector(layers["ANNOTATIONS"], layers["ANNOTATIONS"], "", [0, 0, 0, 10],
                connection_width=4, connection_height=4).move(
                1890/2 - tot_small_width/2 + i*spacing_small, -930 + height/2
            ).rotate_by_angle(180)
            bond_pads.add_connector_or_element(f"P{c_id}", port)

        bond_pads.shift_origin(1890/2, -1890/2)
        bond_pads.move(-1890/2, 1890/2)
        return bond_pads

    all_sides = ConnectedElement()
    all_sides.add_with_child_prefix(get_pads())
    all_sides.add_with_child_prefix(get_pads().rotate_right())
    all_sides.add_with_child_prefix(get_pads().rotate_by_angle(180))
    all_sides.add_with_child_prefix(get_pads().rotate_left())

    return all_sides
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

    bpads = create_bond_pads_for_quadrant()

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
    CS_params = DotWLeadsParams(dot_r=r_cs, barrier_width=0.05)
    
    CS_AD = ConnectedElement()
    dot = get_dot_with_leads(
        layers["OHMICS_0"],
        layers["GATES0_0"],
        layers["GATES1_0"],
        layers["ANNOTATIONS"],
        CS_params
    )
    CS_AD.add_connector_or_element("CS", dot)

    AD_params = ADParams(
        dot_r=r_ad,
        top_lead_rotation=45,
        loop_area=200,
        loop_width=20,
        plunger_rotation=90-17,
        barrier_width=0.05,
        barrier_offset=-0.02,
        barrier_height=0.05,
        plunger_barrier_offset=0.05,
        flip_loop=False
    )
    CS_AD.add_connector_or_element("AD", get_andreev_dot_with_loop(
        layers["OHMICS_0"],
        layers["GATES0_0"],
        layers["GATES1_0"],
        layers["ANNOTATIONS"],
        AD_params
    ).move(r_cs + r_ad + dot_shift, 0))
    barrier = create_shape(layers["GATES1_0"], barrier_points)
    CS_AD.add_element(barrier.move(r_cs + barrier_shift, 0))
    return CS_AD


first_quadrant = ConnectedElement()

SL_WIDTH = 0.5
mirror_shift = 20 + 0.5
up_shift = 10 + 0.17 + SL_WIDTH + 0.2

right_side = get_charge_sensed_ad(0.175/2, 0.175/2)
first_quadrant.add_connector_or_element("N", right_side.move(0, up_shift))

left_side = get_charge_sensed_ad(0.175/2, 0.2/2)
first_quadrant.add_connector_or_element("S",
    left_side.move(mirror_shift, -up_shift).flip_horizontally().flip_vertically()
)

first_quadrant.move(-mirror_shift/2, up_shift/2)
first_quadrant.move(1775 + 150, 4175 - 150)

layout.add_element(first_quadrant)


def connect_with_ext(c0l, c1l, layer, rotation, position):
    c0 = first_quadrant.get_connector(c0l)
    c1 = bpads.get_connector(c1l)

    e0, e1 = get_connector_extention(
        layer,
        layers["ANNOTATIONS"],
        c0,
        position
    )

    c0.connect_to(e0.rotate_by_angle(rotation), layer)
    c1.connect_to(e1.rotate_by_angle(rotation), layer)
    layout.add_element(e0)
    layout.add_element(e1)

ol = layers["OHMICS_0"]
g0 = layers["GATES0_0"]
g1 = layers["GATES1_0"]

connect_with_ext("N_AD_TB", "P3", g1, 0, (1915, 4050))

connect_with_ext("N_CS_TOPLEAD", "P28", ol, -90, (1900, 4042))
connect_with_ext("N_CS_TB", "P27", g1, -90, (1910, 4041.6))
connect_with_ext("N_CS_PB", "P26", g1, -90, (1910.2, 4041.2))
connect_with_ext("N_CS_PL", "P25", g0, -135, (1908, 4038))
connect_with_ext("N_CS_BB", "P24", g1, -135, (1908, 4037))
connect_with_ext("N_CS_BOTLEAD", "P23", ol, -135, (1909, 4035))



layout.build_to_file("C:/Users/nbr720/Documents/PhD/design/design_files/TD00.dxf")
# layout.build_to_file("C:/Users/jyrgen/Documents/PhD/design/gds_files/TD00.dxf")
