import math
from kle.layout.layout import KleLayout, KleLayoutElement, KleShape, create_shape


def get_circle_points(r, n_pts=50):
    return [(math.cos(2*math.pi/n_pts*x)*r,math.sin(2*math.pi/n_pts*x)*r) for x in range(0,n_pts+1)]

def get_dot_with_leads(
    ohm_layer, gate_0_layer, gate_1_layer,
    bias_x=0.0, bias_y=0.0, dot_r=0.075,
    barrier_height=0.04, barrer_width=0.15,
    lead_height=0.1, lead_width=0.085, # This is not great, need to figure out how to reduce this
    top_lead_rotation=0,
    plunger_rotation=0,
    # to managable amounds TODO
):
    dot = KleLayoutElement("dit")

    plunger_height = 0.05
    plnger_width = 0.2
    
    # Make a circle for the dot
    dot.add_element(create_shape(gate_0_layer, get_circle_points(dot_r)))
    dot.add_element(create_shape(gate_0_layer, [
        (0, -plunger_height/2 -bias_y), (0, plunger_height/2 +bias_y),
        (-plnger_width -bias_x, plunger_height/2 +bias_y), (-plnger_width -bias_x, -plunger_height/2 -bias_y)
    ]).rotate_by_angle(plunger_rotation))

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

    # Add Leads
    lead_points = [
        (-lead_width/2 - bias_x, dot_r + barrier_height - bias_y),
        (lead_width/2 + bias_x, dot_r + barrier_height - bias_y),
        (lead_width/2 + bias_x, dot_r + barrier_height + lead_height),
        (-lead_width/2 - bias_x, dot_r + barrier_height + lead_height),
    ]
    lead = create_shape(ohm_layer, lead_points)
    top_lead = lead.get_copy()
    bot_lead = lead.get_copy()

    dot.add_element(top_lead)
    top_lead.rotate_by_angle(top_lead_rotation)
    
    dot.add_element(bot_lead)
    bot_lead.flip_vertically()
    
    return dot


def get_andreev_dot_with_loop(
    ohm_layer, gate_0_layer, gate_1_layer,
    loop_width=0.8, loop_area=2,
    bias_x=0, bias_y=0, dot_r=0.075,
    barrier_height=0.04, barrer_width=0.15,
    lead_height=0.1, lead_width=0.085,
    top_lead_rotation=0,
    plunger_rotation=0
    # TODO FIX ME
):
    dot = get_dot_with_leads(
        ohm_layer, gate_0_layer, gate_1_layer,
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