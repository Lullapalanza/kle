from kle.layout.layout import KleLayout, KleLayoutElement, KleShape, create_shape
from kle.layout.dot_elements import (
    get_Lazar_global_markers,
    get_dot_with_leads, DotWLeadsParams,
    get_andreev_dot_with_loop, ADParams,
)

LA_LAYERS = [
    "LM", "OHMICS", "BARRIERS", "PLUNGERS", "SL"
] # Local alignment layers, gate, ohmics
def get_layers_for_la(id):
    """
    layer names for local alignment
    """
    return [
        f"{la_layer}{id}" for la_layer in LA_LAYERS
    ]

LAYER_NAMES = [
    "-CHIP",
    "MARKERS",
    "OHMICS_COURSE",
    "BARRIERS_COURSE", # Barriers Corse
    "PLUNGERS_COURSE", # PLungers Corse
    "TS_B", # Test structure barrier
    "TS_G", # TS gate
    "TS_O", # TS ohmics
    "ANNOTATIONS",
]

for lid in [0, 1, 2, 3]:
    LAYER_NAMES.extend(get_layers_for_la(lid))

layout = KleLayout(6000, 6000, LAYER_NAMES)
layers = layout.get_layers()

# ==== GLOBAL MARKERS ====
marker_quadrant = KleLayoutElement()
g_marker = KleLayoutElement()

m_largearm_shape = create_shape(
    layers["MARKERS"],
    [(0, -2.5), (84, -2.5), (84, 2.5), (0, 2.5)],
)
g_marker.add_element(m_largearm_shape.get_copy())
g_marker.add_element(m_largearm_shape.get_copy().move(84 + 12, 0))
g_marker.add_element(m_largearm_shape.get_copy().rotate_left().move(84 + 6, 6))
g_marker.add_element(m_largearm_shape.get_copy().rotate_left().move(84 + 6, -84 - 6))

m_smallarm_shape = create_shape(layers["MARKERS"], [(-5, -0.25), (5, -0.25), (5, 0.25), (-5, 0.25)])
g_marker.add_element(m_smallarm_shape.get_copy().move(90, 0))
g_marker.add_element(m_smallarm_shape.get_copy().rotate_left().move(90, 0))


for i in range(5):
    marker_quadrant.add_element(g_marker.get_copy().move(200 * i, 0))

for i in range(1, 5):
    marker_quadrant.add_element(g_marker.get_copy().move(0, 200 * i))

marker_quadrant.shift_origin(90, 0).move(-90, 0)

mk_NW = marker_quadrant.get_copy().rotate_right().move(600, 5400)
mk_NE = marker_quadrant.get_copy().rotate_right().rotate_right().move(5400, 5400)
mk_SE = marker_quadrant.get_copy().rotate_left().move(5400, 600)
mk_SW = marker_quadrant.move(600, 600)

layout.add_element(mk_NW)
layout.add_element(mk_NE)
layout.add_element(mk_SE)
layout.add_element(mk_SW)
# ==== END GLOBAL MARKERS ====



# ==== START BOND PADS ====
def create_bond_pads_for_quadrant(layer):
    bond_pads = KleLayoutElement()

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

    for i in range(1, 9):
        bond_pads.add_element(pad.get_copy().move(i*spacing, 0))
        bond_pads.add_element(
            create_shape(layer, [
                (i*spacing - connection_larger_width/2, -height/2),
                (i*spacing + connection_larger_width/2, -height/2),
                (1890/2 - tot_small_width/2 + i*spacing_small + connection_smaller_width/2, -930 + height/2),
                (1890/2 - tot_small_width/2 +  i*spacing_small, -930 + height/2 - 2),
                (1890/2 - tot_small_width/2 + i*spacing_small - connection_smaller_width/2, -930 + height/2),
            ])
        )
    bond_pads.shift_origin(1890/2, -1890/2)
    bond_pads.move(-1890/2, 1890/2)

    all_sides = KleLayoutElement()
    all_sides.add_element(bond_pads.get_copy())
    all_sides.add_element(bond_pads.get_copy().rotate_right())
    all_sides.add_element(bond_pads.get_copy().rotate_left())
    all_sides.add_element(bond_pads.get_copy().rotate_right().rotate_right())

    return all_sides
# ==== END BOND PADS ====



# ==== LOCAL MARKERS FOR 4 QUADRANTS ====
lm_l_pos = [
    ("LM0", 1775, 4175),
    ("LM1", 3925, 4175),
    ("LM2", 1775, 2025),
    ("LM3", 3925, 2025),
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
    
    layout.add_element(create_bond_pads_for_quadrant(layers["OHMICS_COURSE"]).move(x+150, y-150))
# ==== END LOCAL MARKERS ====



bias_x=0
bias_y=0
barrier_points = [
    (0 - bias_x, -0.060 - bias_y),
    (0.05 + bias_x, -0.060 - bias_y),
    (0.05 + bias_x, 0.060 + bias_y), 
    (0 - bias_x, 0.060 + bias_y)
]
dot_shift = 0.065
barrier_shift = (dot_shift - 0.05)/2

# The device is split into 4
# 1st and second are double devices with different dot size with and without loop

# ==== FIRST QUADRANT ====

def get_charge_sensed_ad(r_cs, r_ad):
    CS_AD = KleLayoutElement()
    
    charge_sensor_params = DotWLeadsParams(dot_r=r_cs, barrier_width=0.05)
    CS_AD.add_element(get_dot_with_leads(
        layers["OHMICS0"],
        layers["PLUNGERS0"],
        layers["BARRIERS0"],
        layers["ANNOTATIONS"],
        charge_sensor_params,
    ))

    andreev_params = ADParams(
        dot_r=r_ad,
        top_lead_rotation=45,
        loop_area=200,
        loop_width=20,
        plunger_rotation=73,
        barrier_width=0.05,
        barrier_height=0.1,
        barrier_offset=0,
        plunger_barrier_offset=0.05
    )
    CS_AD.add_element(get_andreev_dot_with_loop(
        layers["OHMICS0"],
        layers["PLUNGERS0"],
        layers["BARRIERS0"],
        layers["ANNOTATIONS"],
        andreev_params,
    ).move(r_cs + r_ad + dot_shift, 0))
    barrier = create_shape(layers["BARRIERS0"], barrier_points)
    CS_AD.add_element(barrier.move(r_cs + barrier_shift, 0))
    return CS_AD


first_quadrant = KleLayoutElement()

SL_WIDTH = 0.5
mirror_shift = 20 + 0.5
up_shift = 10 + 0.17 + SL_WIDTH + 0.2

right_side = get_charge_sensed_ad(0.175/2, 0.175/2)
first_quadrant.add_element(right_side)
first_quadrant.move(0, up_shift)

left_side = get_charge_sensed_ad(0.175/2, 0.2/2)
first_quadrant.add_element(
    left_side.move(mirror_shift, -up_shift).flip_horizontally().flip_vertically()
)

first_quadrant.move(-mirror_shift/2, up_shift/2)

# Add stripline
SL_HEIGHT = 20 + 0.43 + SL_WIDTH*2
stripline_middle = create_shape(layers["SL0"], [
    (-SL_HEIGHT/2, -SL_WIDTH/2),
    (SL_HEIGHT/2, -SL_WIDTH/2),
    (SL_HEIGHT/2, SL_WIDTH/2),
    (-SL_HEIGHT/2, SL_WIDTH/2),
])

first_quadrant.add_element(stripline_middle.get_copy())
first_quadrant.add_element(stripline_middle.get_copy().move(0, up_shift))
first_quadrant.add_element(stripline_middle.move(0, -up_shift))

stripline_side = create_shape(layers["SL0"], [
    (-SL_WIDTH/2, -SL_WIDTH/2),
    (SL_WIDTH/2, -SL_WIDTH/2),
    (SL_WIDTH/2, SL_WIDTH/2 + up_shift),
    (-SL_WIDTH/2, SL_WIDTH/2 + up_shift),
])
first_quadrant.add_element(stripline_side.get_copy().move(SL_HEIGHT/2 - SL_WIDTH/2, 0))
first_quadrant.add_element(stripline_side.flip_vertically().move(-SL_HEIGHT/2 + SL_WIDTH/2, 0))

first_quadrant.move(1775 + 150, 4175 - 150)
layout.add_element(first_quadrant)
# ===== END FIRST QUADRANT ====



# # ===== SECOND QUADRANT ======
# def get_double_junction(r_cs, r_ad):
#     double_junction = KleLayoutElement()
#     double_junction.add_element(get_dot_with_leads(
#         layers["OHMICS2"],
#         layers["GATES2"],
#         layers["CG2"],
#         dot_r=r_cs,
#         bias_x=-0.005,
#         bias_y=-0.005,
#         barrier_height=0.05
#     ))
#     AD_R = 0.2/2
#     double_junction.add_element(get_dot_with_leads(
#         layers["OHMICS2"],
#         layers["GATES2"],
#         layers["CG2"],
#         bias_x=-0.005,
#         bias_y=-0.005,
#         dot_r=r_ad,
#         plunger_rotation=180,
#         barrier_height=0.05
#     ).move(r_cs + r_ad + dot_shift, 0))
#     barrier = create_shape(layers["CG2"], barrier_points)
#     double_junction.add_element(barrier.get_copy().move(r_cs + barrier_shift, 0))

#     return double_junction

# second_quadrant = KleLayoutElement()

# left_side = get_double_junction(0.175/2, 0.175/2)
# second_quadrant.add_element(left_side)

# right_side = get_double_junction(0.175/2, 0.2/2)
# second_quadrant.add_element(right_side.flip_horizontally().move(2, 0))

# second_quadrant.shift_origin(1, 0)
# second_quadrant.move(-1, 0)
# second_quadrant.move(3925 + 150, 4175 - 150)
# layout.add_element(second_quadrant)
# # ===== END SECOND QUADRANT ====




# # ==== THIRD AND FOURTH QUADRANT
# def get_charge_sensed_dad(ohm_layer, gate_0_layer, gate_1_layer, r_cs, r_ad, dot_r=0.100/2):
#     """
#     dad - double andreev dot
#     """
#     # Make Charge sensor
#     CS_AD = KleLayoutElement()
#     CS_AD.add_element(get_dot_with_leads(
#         ohm_layer, gate_0_layer, gate_1_layer,
#         dot_r=r_cs,
#         bias_x=-0.005,
#         bias_y=-0.005,
#         barrier_height=0.05
#     ))

#     # Make dot
#     CS_AD.add_element(create_shape(
#         gate_0_layer, get_circle_points(dot_r)
#     ).move(r_cs + dot_r + dot_shift, 0))
#     barrier = create_shape(gate_1_layer, barrier_points)
#     CS_AD.add_element(barrier.get_copy().move(r_cs + barrier_shift, 0))

#     CS_AD.add_element(get_andreev_dot_with_loop(
#         ohm_layer, gate_0_layer, gate_1_layer,
#         dot_r=r_ad,
#         top_lead_rotation=45,
#         loop_area=200,
#         loop_width=20,
#         bias_x=-0.005,
#         bias_y=-0.005,
#         plunger_rotation=73,
#         barrier_height=0.05
#     ).move(r_cs + dot_r * 2 + r_ad + dot_shift * 2, 0))

#     barrier = create_shape(gate_1_layer, barrier_points)
#     CS_AD.add_element(barrier.get_copy().move(r_cs + dot_shift + barrier_shift + dot_r * 2, 0))
#     return CS_AD

# def get_dad_quadrant(ohm_layer, gate_0_layer, gate_1_layer, stripline_layer, position):
#     quadrant = KleLayoutElement()

    
#     SL_WIDTH = 0.5
#     mirror_shift = 20 + 0.5
#     up_shift = 10 + 0.17 + SL_WIDTH + 0.2

    
#     quadrant.add_element(get_charge_sensed_dad(
#         ohm_layer, gate_0_layer, gate_1_layer, 0.175/2, 0.175/2
#     ))

#     right_side = get_charge_sensed_dad(
#         ohm_layer, gate_0_layer, gate_1_layer, 0.175/2, 0.2/2
#     )

#     quadrant.add_element(
#         right_side.move(mirror_shift, -up_shift).flip_horizontally().flip_vertically()
#     )

#     quadrant.move(-mirror_shift/2, up_shift/2)

#     # Add stripline
#     SL_HEIGHT = 20 + SL_WIDTH*2 + 0.632 + 0.132
#     stripline_middle = create_shape(layers["SL"], [
#         (-SL_HEIGHT/2, -SL_WIDTH/2),
#         (SL_HEIGHT/2, -SL_WIDTH/2),
#         (SL_HEIGHT/2, SL_WIDTH/2),
#         (-SL_HEIGHT/2, SL_WIDTH/2),
#     ])

#     quadrant.add_element(stripline_middle.get_copy())
#     quadrant.add_element(stripline_middle.get_copy().move(0, up_shift))
#     quadrant.add_element(stripline_middle.move(0, -up_shift))

#     stripline_side = create_shape(layers["SL"], [
#         (-SL_WIDTH/2, -SL_WIDTH/2),
#         (SL_WIDTH/2, -SL_WIDTH/2),
#         (SL_WIDTH/2, SL_WIDTH/2 + up_shift),
#         (-SL_WIDTH/2, SL_WIDTH/2 + up_shift),
#     ])
#     quadrant.add_element(stripline_side.get_copy().move(SL_HEIGHT/2 - SL_WIDTH/2, 0))
#     quadrant.add_element(stripline_side.flip_vertically().move(-SL_HEIGHT/2 + SL_WIDTH/2, 0))

#     quadrant.move(position[0] + 150, position[1] - 150)

#     return quadrant

# layout.add_element(
#     get_dad_quadrant(layers["OHMICS3"], layers["GATES3"], layers["CG3"], layers["SL3"], (1775, 2025))
# )
# layout.add_element(
#     get_dad_quadrant(layers["OHMICS4"], layers["GATES4"], layers["CG4"], layers["SL4"], (3925, 2025))
# )

layout.build_to_file("/home/jyrgen/Downloads/PhD/design/design_files/AQ01_20241213.dxf")
