import math
from kle.layout.layout import KleLayout, KleLayer, KleLayoutElement, KleShape, create_shape
from kle.layout.layout_connections import get_simple_connector, ConnectedElement


def get_circle_points(r: float, n_pts: int = 50) -> list[tuple[float]]:
    """
    get [(x, y), ...] points for a circle originating at 0, 0 
    """
    return [(math.cos(2*math.pi/n_pts*x)*r,math.sin(2*math.pi/n_pts*x)*r) for x in range(0,n_pts+1)]


def get_Lazar_global_markers(global_marker_layer: KleLayer) -> KleLayoutElement:
    """
    Get marker layout based on Lazar 6x6 chip
    """
    global_markers = KleLayoutElement()

    marker_cross = KleLayoutElement()
    # Make large arm
    cross_arm_shape = create_shape(
        global_marker_layer, [(0, -2.5), (84, -2.5), (84, 2.5), (0, 2.5)]
    )
    marker_cross.add_element(cross_arm_shape.get_copy())
    marker_cross.add_element(cross_arm_shape.get_copy().move(96, 0))
    marker_cross.add_element(cross_arm_shape.get_copy().rotate_left().move(90, 6))
    marker_cross.add_element(cross_arm_shape.rotate_right().move(90, -6))


    # Add smaller center arm
    small_arm_shape = create_shape(global_marker_layer, [(-5, -0.25), (5, -0.25), (5, 0.25), (-5, 0.25)])
    marker_cross.add_element(small_arm_shape.get_copy().move(90, 0))
    marker_cross.add_element(small_arm_shape.rotate_left().move(90, 0))

    # Make one corner
    marker_quadrant = KleLayoutElement()
    for i in range(5):
        marker_quadrant.add_element(marker_cross.get_copy().move(200 * i, 0))

    for i in range(1, 5):
        marker_quadrant.add_element(marker_cross.get_copy().move(0, 200 * i))

    # marker_quadrant.shift_origin(90, 0).move(-90, 0)

    # Add 4 marker quadrants
    global_markers.add_element(marker_quadrant.get_copy().rotate_right().move(600, 5400))
    global_markers.add_element(marker_quadrant.get_copy().rotate_right().rotate_right().move(5400, 5400))
    global_markers.add_element(marker_quadrant.get_copy().rotate_left().move(5400, 600))
    global_markers.add_element(marker_quadrant.move(600, 600))

    return global_markers


def get_dot_with_leads(
    ohm_layer, gate_0_layer, gate_1_layer, annotation_layer,
    bias_x=0.0, bias_y=0.0, dot_r=0.075,
    barrier_height=0.04, barrer_width=0.15,
    lead_height=0.1, lead_width=0.085, # This is not great, need to figure out how to reduce this
    top_lead_rotation=0,
    plunger_rotation=0,
    # to managable amounts TODO
):  
    dot = ConnectedElement()

    plunger_height = 0.15
    plunger_width = 0.06
    
    # Make a circle for the dot
    dot.add_element(create_shape(gate_0_layer, get_circle_points(dot_r)))
    dot.add_connector_or_element("PL", get_simple_connector(
        gate_0_layer, annotation_layer, "", [0, 0, 0, plunger_height], 
        plunger_width, plunger_height
    ).rotate_by_angle(plunger_rotation - 90))
    dot.add_connector_or_element("PB", get_simple_connector(
        gate_1_layer, annotation_layer, "", [0, dot_r, 0, dot_r + 0.05], 
        plunger_width + 0.01, 0.05
    ).rotate_by_angle(plunger_rotation - 90))

    # Add barrier up and below
    barrier_points = [
        (-barrer_width/2 - bias_x, dot_r - bias_y),
        (barrer_width/2 + bias_x, dot_r - bias_y),
        (barrer_width/2 + bias_x, dot_r + barrier_height + bias_y),
        (-barrer_width/2 - bias_x, dot_r + barrier_height + bias_y)
    ]
    barrier_s = create_shape(gate_1_layer, barrier_points)
    dot.add_element(barrier_s.move(0, 0).get_copy().rotate_by_angle(top_lead_rotation))
    dot.add_element(barrier_s.get_copy().move(
        0, -2 * dot_r - barrier_height
    ))
    
    top_lead = get_simple_connector(
        ohm_layer, annotation_layer, "",
        [0, dot_r + barrier_height, 0, dot_r + barrier_height + lead_height + 5],
        connection_width=lead_width, connection_height=lead_height
    )
    bot_lead = get_simple_connector(
        ohm_layer, annotation_layer, "",
        [0, dot_r + barrier_height, 0, dot_r + barrier_height + lead_height + 5],
        connection_width=lead_width, connection_height=lead_height
    )
    
    dot.add_connector_or_element("TOPLEAD", top_lead.rotate_by_angle(top_lead_rotation))
    dot.add_connector_or_element("BOTLEAD", bot_lead.rotate_by_angle(180))
    
    return dot


def get_andreev_dot_with_loop(
    ohm_layer, gate_0_layer, gate_1_layer, annotation_layer,
    loop_width=0.8, loop_area=2,
    bias_x=0, bias_y=0, dot_r=0.075,
    barrier_height=0.04, barrer_width=0.15,
    lead_height=0.1, lead_width=0.085,
    top_lead_rotation=0,
    plunger_rotation=0
    # TODO FIX ME
):
    dot = get_dot_with_leads(
        ohm_layer, gate_0_layer, gate_1_layer, annotation_layer,
        bias_x, bias_y, dot_r,
        barrier_height, barrer_width,
        lead_height, lead_width,
        top_lead_rotation,
        plunger_rotation
    )

    loop_height = loop_area / loop_width
    loop_top_offset = dot_r + barrier_height + lead_height
    loop_points = [
        (-lead_width/2 - bias_x, 0),
        (lead_width/2 + bias_x, 0),
        (lead_width/2, loop_height/2 - loop_top_offset),
        (lead_width/2 + loop_width, loop_height/2 - loop_top_offset),
        (lead_width/2 + loop_width, -loop_top_offset),

        (lead_width/2 + loop_width + lead_width, -loop_top_offset),
        (lead_width/2 + loop_width + lead_width, loop_height/2 - loop_top_offset + lead_width),
        (-lead_width/2, loop_height/2 - loop_top_offset + lead_width)
    ]
    half_loop = create_shape(ohm_layer, loop_points)

    dot.add_element(half_loop.get_copy().move(0, dot_r + barrier_height + lead_height))
    dot.add_element(half_loop.get_copy().flip_vertically().move(0, -(dot_r + barrier_height + lead_height)))
    
    return dot