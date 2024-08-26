from kle.layout.layout import KleLayout, KleLayoutElement, KleShape, create_shape
from kle.layout.dot_elements import (
    get_circle_points,
    get_dot_with_leads,
    get_andreev_dot_with_loop
)


LA_LAYERS = ["M", "G0", "G1", "O", "SL"] # Local alignment layers, gate, ohmics
def get_layers_for_la(id):
    """
    layer names for local alignment
    """
    return [
        f"{la_layer}_{id}" for la_layer in LA_LAYERS
    ]

LAYER_NAMES = [
    "-CHIP",
    "MARKERS",
    "OC",
    "B0C", # Barriers Corse
    "B1C", # Barriers Corse
    "TS_B", # Test structure barrier
    "TS_G", # TS gate
    "TS_O", # TS ohmics
]

for lid in [0, 1, 2, 3]:
    LAYER_NAMES.extend(get_layers_for_la(lid))

layout = KleLayout(6000, 6000, LAYER_NAMES)
layers = layout.get_layers()

# ==== GLOBAL MARKERS ====
marker_quadrant = KleLayoutElement("marker quadrant")
g_marker = KleLayoutElement("Global marker")

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

marker_quadrant.update_origin((90, 0)).move(-90, 0)

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

    for i in range(9):
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
    ("M_0", 1775, 4175),
    ("M_1", 3925, 4175),
    ("M_2", 1775, 2025),
    ("M_3", 3925, 2025),
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
    
    layout.add_element(create_bond_pads_for_quadrant(layers["OC"]).move(x+150, y-150))
# ==== END LOCAL MARKERS ====


# The device is split into 4
# 1st and second are double devices with different dot size with and without loop

# ==== FIRST QUADRANT ====
def get_charge_sensed_ad(r_cs, r_ad):
    CS_AD = KleLayoutElement("charge sensed Andreev Dot")
    CS_AD.add_element(get_dot_with_leads(
        layers["O_0"],
        layers["G0_0"],
        layers["G1_0"],
        dot_r=r_cs,
        bias_x=-0.005,
        bias_y=-0.005,
    ))
    CS_AD.add_element(get_andreev_dot_with_loop(
        layers["O_0"],
        layers["G0_0"],
        layers["G1_0"],
        dot_r=r_ad,
        top_lead_rotation=45,
        loop_area=100,
        loop_width=8,
        bias_x=-0.005,
        bias_y=-0.005,
        plunger_rotation=73
    ).move(r_cs + r_ad + 0.055, 0))
    barrier = create_shape(layers["G1_0"], [(0, -0.060), (0.04, -0.060), (0.04, 0.060), (0, 0.060)])
    CS_AD.add_element(barrier.move(r_cs + 0.0075, 0))
    return CS_AD


first_quadrant = KleLayoutElement("first quadrant")

right_side = get_charge_sensed_ad(0.175/2, 0.2/2)
first_quadrant.add_element(right_side)

left_side = get_charge_sensed_ad(0.175/2, 0.25/2)
first_quadrant.add_element(
    left_side.move(9*2 + 0.025 - 0.56, 0).flip_horizontally()
)

first_quadrant.update_origin((9 - 0.28, 0))
first_quadrant.move(-9 + 0.28, 0)

# Add stripline
SL_HEIGHT = 50
SL_WIDTH = 0.5
stripline = create_shape(layers["SL_0"], [
    (-SL_WIDTH/2, -SL_HEIGHT/2),
    (SL_WIDTH/2, -SL_HEIGHT/2),
    (SL_WIDTH/2, SL_HEIGHT/2),
    (-SL_WIDTH/2, SL_HEIGHT/2),
])
first_quadrant.add_element(stripline)

first_quadrant.move(1775 + 150, 4175 - 150)
layout.add_element(first_quadrant)
# ===== END FIRST QUADRANT ====



# ===== SECOND QUADRANT ======
def get_double_junction(r_cs, r_ad):
    double_junction = KleLayoutElement("double junction")
    double_junction.add_element(get_dot_with_leads(
        layers["O_1"],
        layers["G0_1"],
        layers["G1_1"],
        dot_r=r_cs,
        bias_x=-0.005,
        bias_y=-0.005,
    ))
    AD_R = 0.2/2
    double_junction.add_element(get_dot_with_leads(
        layers["O_1"],
        layers["G0_1"],
        layers["G1_1"],
        bias_x=-0.005,
        bias_y=-0.005,
        dot_r=r_ad,
        plunger_rotation=180
    ).move(r_cs + r_ad + 0.055, 0))
    barrier = create_shape(layers["G1_1"], [(0, -0.060), (0.04, -0.060), (0.04, 0.060), (0, 0.060)])
    double_junction.add_element(barrier.get_copy().move(r_cs + 0.0075, 0))

    return double_junction

second_quadrant = KleLayoutElement("second quadrant")

left_side = get_double_junction(0.175/2, 0.2/2)
second_quadrant.add_element(left_side)

right_side = get_double_junction(0.175/2, 0.25/2)
second_quadrant.add_element(right_side.flip_horizontally().move(2, 0))

second_quadrant.update_origin((1, 0))
second_quadrant.move(-1, 0)
second_quadrant.move(3925 + 150, 4175 - 150)
layout.add_element(second_quadrant)
# ===== END SECOND QUADRANT ====




# ==== THIRD AND FOURTH QUADRANT
def get_charge_sensed_dad(ohm_layer, gate_0_layer, gate_1_layer, r_cs, r_ad, dot_r=0.100/2):
    """
    dad - double andreev dot
    """
    # Make Charge sensor
    CS_AD = KleLayoutElement("charge sensed Andreev Dot")
    CS_AD.add_element(get_dot_with_leads(
        ohm_layer, gate_0_layer, gate_1_layer,
        dot_r=r_cs,
        bias_x=-0.005,
        bias_y=-0.005,
    ))

    # Make dot
    CS_AD.add_element(create_shape(
        gate_0_layer, get_circle_points(dot_r)
    ).move(r_cs + dot_r + 0.055, 0))
    barrier = create_shape(gate_1_layer, [(0, -0.060), (0.04, -0.060), (0.04, 0.060), (0, 0.060)])
    CS_AD.add_element(barrier.get_copy().move(r_cs + 0.0075, 0))

    CS_AD.add_element(get_andreev_dot_with_loop(
        ohm_layer, gate_0_layer, gate_1_layer,
        dot_r=r_ad,
        top_lead_rotation=45,
        loop_area=100,
        loop_width=8,
        bias_x=-0.005,
        bias_y=-0.005,
        plunger_rotation=73
    ).move(r_cs + dot_r * 2 + r_ad + 0.055 * 2, 0))

    barrier = create_shape(gate_1_layer, [(0, -0.060), (0.04, -0.060), (0.04, 0.060), (0, 0.060)])
    CS_AD.add_element(barrier.get_copy().move(r_cs + 0.063 + dot_r * 2, 0))
    return CS_AD

def get_dad_quadrant(ohm_layer, gate_0_layer, gate_1_layer, stripline_layer, position):
    quadrant = KleLayoutElement("quadrant")
    
    quadrant.add_element(get_charge_sensed_dad(
        ohm_layer, gate_0_layer, gate_1_layer, 0.175/2, 0.2/2
    ))

    right_side = get_charge_sensed_dad(
        ohm_layer, gate_0_layer, gate_1_layer, 0.175/2, 0.2/2
    )

    quadrant.add_element(
        right_side.move(9.2*2 + 0.025 - 0.56, 0).flip_horizontally()
    )

    quadrant.update_origin((9.2 - 0.28, 0))
    quadrant.move(-9.2 + 0.28, 0)

    # Add stripline
    SL_HEIGHT = 50
    SL_WIDTH = 0.5
    stripline = create_shape(layers["SL_0"], [
        (-SL_WIDTH/2, -SL_HEIGHT/2),
        (SL_WIDTH/2, -SL_HEIGHT/2),
        (SL_WIDTH/2, SL_HEIGHT/2),
        (-SL_WIDTH/2, SL_HEIGHT/2),
    ])
    quadrant.add_element(stripline)
    quadrant.move(position[0] + 150, position[1] - 150)

    return quadrant

layout.add_element(
    get_dad_quadrant(layers["O_2"], layers["G0_2"], layers["G1_2"], layers["SL_2"], (1775, 2025))
)
layout.add_element(
    get_dad_quadrant(layers["O_3"], layers["G0_3"], layers["G1_3"], layers["SL_3"], (3925, 2025))
)

layout.build_to_file("C:/Users/nbr720/Documents/PhD/design/design_files/AQ00_test_20240826.dxf")