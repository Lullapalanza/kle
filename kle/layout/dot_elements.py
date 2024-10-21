import math
from dataclasses import dataclass
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


@dataclass
class DotWLeadsParams:
    dot_r: float = 0.075
    
    barrier_width: float = 0.04
    barrier_height: float = 0.15
    barrier_offset: float = 0.025

    lead_height: float = 0.1
    lead_width: float = 0.085
    top_lead_rotation: float = 0.0

    plunger_height: float = 0.15
    plunger_width: float = 0.05
    plunger_rotation: float = 0.0

    plunger_barrier_height: float = 0.05
    plunger_barrier_width_offset: float = 0.01
    plunger_barrier_offset: float = 0.02


def get_dot_with_leads(ohm_layer, gate_0_layer, gate_1_layer, annotation_layer, params=DotWLeadsParams()):  
    dot = ConnectedElement()

    # Make a circle for the dot and plunger + plunger barrier connectors
    dot.add_element(create_shape(gate_0_layer, get_circle_points(params.dot_r)))
    dot.add_connector_or_element("PL", get_simple_connector(
        gate_0_layer, annotation_layer, "", [0, 0, 0, params.plunger_height * 2], 
        params.plunger_width, params.plunger_height
    ).rotate_by_angle(params.plunger_rotation - 90))
    
    plunger_barrier = get_simple_connector(
        gate_1_layer, annotation_layer, "", [0, 0, 0, 0.1], 
        params.plunger_width + 0.01, 0.05
    ).rotate_by_angle(17).move(0, params.dot_r + params.plunger_barrier_offset + 0.015)
    dot.add_connector_or_element("PB", plunger_barrier)
    pwidth = (params.plunger_width + params.plunger_barrier_width_offset)/2
    plunger_barrier.add_element(create_shape(gate_1_layer,
        [
            (-pwidth, params.dot_r + params.plunger_barrier_offset),
            (pwidth, params.dot_r + params.plunger_barrier_offset),
            (pwidth, params.dot_r + params.plunger_barrier_offset + params.plunger_barrier_height),
            (-pwidth, params.dot_r + params.plunger_barrier_offset + params.plunger_barrier_height)
        ]
    ))
    plunger_barrier.rotate_by_angle(params.plunger_rotation - 90)

    # Add barrier connectors
    barrier_top = get_simple_connector(
        gate_1_layer, annotation_layer, "", [0, 0, -params.barrier_height * 2, 0], 
        params.barrier_width, params.barrier_height
    ).move(params.barrier_height/2 - params.barrier_offset, params.dot_r + params.barrier_width/2)
    dot.add_connector_or_element("TB", barrier_top)
    barrier_top.rotate_by_angle(params.top_lead_rotation)

    barrier_bot = get_simple_connector(
        gate_1_layer, annotation_layer, "", [0, 0, -params.barrier_height * 2, 0], 
        params.barrier_width, params.barrier_height
    ).move(params.barrier_height/2 - params.barrier_offset, -params.dot_r -params.barrier_width/2)
    dot.add_connector_or_element("BB", barrier_bot)

    top_lead = get_simple_connector(
        ohm_layer, annotation_layer, "",
        [0, params.dot_r + params.barrier_width, 0, params.dot_r + params.barrier_width + params.lead_height + 0.1],
        connection_width=params.lead_width, connection_height=params.lead_height
    )
    bot_lead = get_simple_connector(
        ohm_layer, annotation_layer, "",
        [0, params.dot_r + params.barrier_width, 0, params.dot_r + params.barrier_width + params.lead_height + 0.1],
        connection_width=params.lead_width, connection_height=params.lead_height
    )
    
    dot.add_connector_or_element("TOPLEAD", top_lead.rotate_by_angle(params.top_lead_rotation))
    dot.add_connector_or_element("BOTLEAD", bot_lead.rotate_by_angle(180))
    
    return dot


@dataclass
class ADParams(DotWLeadsParams):
    loop_width: float = 0.08
    loop_area: float = 2
    flip_loop: bool = False

def get_andreev_dot_with_loop(ohm_layer, gate_0_layer, gate_1_layer, annotation_layer, params=ADParams()):
    dot = get_dot_with_leads(
        ohm_layer, gate_0_layer, gate_1_layer, annotation_layer, params
    )

    loop_height = params.loop_area / params.loop_width
    loop_top_offset = params.dot_r + params.barrier_height + params.lead_height
    loop_points = [
        (-params.lead_width/2, 0),
        (params.lead_width/2, 0),
        (params.lead_width/2, loop_height/2 - loop_top_offset),
        (params.lead_width/2 + params.loop_width, loop_height/2 - loop_top_offset),
        (params.lead_width/2 + params.loop_width, -loop_top_offset),

        (params.lead_width/2 + params.loop_width + params.lead_width, -loop_top_offset),
        (params.lead_width/2 + params.loop_width + params.lead_width, loop_height/2 - loop_top_offset + params.lead_width),
        (-params.lead_width/2, loop_height/2 - loop_top_offset + params.lead_width)
    ]
    half_loop = create_shape(ohm_layer, loop_points)

    hl0 = half_loop.get_copy().move(0, params.dot_r + params.barrier_height + params.lead_height)
    hl1 = half_loop.get_copy().flip_vertically().move(0, -(params.dot_r + params.barrier_height + params.lead_height))

    dot.add_elements([hl0, hl1])

    if params.flip_loop:
        hl0.flip_horizontally()
        hl1.flip_horizontally()

    return dot