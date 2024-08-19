import math
from kle.layout.layout import KleLayout, KleLayoutElement, KleShape, create_shape


def get_circle_points(r, n_pts=50):
    return [(math.cos(2*math.pi/n_pts*x)*r,math.sin(2*math.pi/n_pts*x)*r) for x in range(0,n_pts+1)]

def get_dot_with_leads(
    ohm_layer, gate_0_layer, gate_1_layer,
    bias_x=0, bias_y=0, dot_r=0.075,
    barrier_height=0.04, barrer_width=0.15,
    lead_height=0.1, lead_width=0.085 # This is not great, need to figure out how to reduce this
    # to managable amounds TODO
):
    dot = KleLayoutElement("dit")

    # Make a circle for the dot
    dot.add_element(create_shape(gate_0_layer, get_circle_points(dot_r)))

    # Add barrier up and below
    barrier_points = [
        (-barrer_width/2, dot_r),
        (barrer_width/2, dot_r),
        (barrer_width/2, dot_r + barrier_height),
        (-barrer_width/2, dot_r + barrier_height)
    ]
    barrier_s = create_shape(gate_1_layer, barrier_points)
    dot.add_element(barrier_s.move(0, 0).get_copy())
    dot.add_element(barrier_s.get_copy().move(
        0, -2 * dot_r - barrier_height
    ))

    # Add Leads
    lead_points = [
        (-lead_width/2, dot_r + barrier_height),
        (lead_width/2, dot_r + barrier_height),
        (lead_width/2, dot_r + barrier_height + lead_height),
        (-lead_width/2, dot_r + barrier_height + lead_height),
    ]
    lead = create_shape(ohm_layer, lead_points)
    dot.add_element(lead.get_copy())
    dot.add_element(lead.get_copy().move(
        0, -2 * dot_r - barrier_height * 2 - lead_height
    ))
    
    return dot


def get_andreev_dot_with_loop(
    ohm_layer, gate_0_layer, gate_1_layer,
    loop_width=0.8, loop_area=2,
    bias_x=0, bias_y=0, dot_r=0.075,
    barrier_height=0.04, barrer_width=0.15,
    lead_height=0.1, lead_width=0.085
    # TODO FIX ME
):
    dot = get_dot_with_leads(
        ohm_layer, gate_0_layer, gate_1_layer,
        bias_x, bias_y, dot_r,
        barrier_height, barrer_width,
        lead_height, lead_width
    )

    loop_height = loop_area / loop_width
    loop_top_offset = dot_r + barrier_height + lead_height
    loop_points = [
        (-lead_width/2, 0),
        (lead_width/2, 0),
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