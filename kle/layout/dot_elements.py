import math
from kle.layout.layout import KleLayout, KleLayoutElement, KleShape


def get_circle_points(r, n_pts=50):
    return [(math.cos(2*math.pi/n_pts*x)*r,math.sin(2*math.pi/n_pts*x)*r) for x in range(0,n_pts+1)]


def get_sensor_dot(ohm_layer, gate_0_layer, gate_1_layer, DOT_R=0.150/2, LEAD_WIDTH=0.1):
    # Make a generic 2 leads + QD + gates + screening element? How to connect the sides? Some kind of smart routing?
    sd = KleLayoutElement("sd")
    
    # DOT_R = 0.150/2
    sd.add_element(KleShape(gate_0_layer, get_circle_points(DOT_R))) # Make a circle for sensor dot

    BARRIER_WIDTH = 0.040
    BARRIER_OVERLAP = 0.000
    BARRIER_EXTRA = -0.01

    barrier_points = [
        (-DOT_R - BARRIER_EXTRA, DOT_R - BARRIER_OVERLAP),
        (DOT_R + BARRIER_EXTRA, DOT_R-BARRIER_OVERLAP),
        (DOT_R + BARRIER_EXTRA, DOT_R-BARRIER_OVERLAP + BARRIER_WIDTH),
        (-DOT_R - BARRIER_EXTRA, DOT_R-BARRIER_OVERLAP + BARRIER_WIDTH)
    ]
    barrier_s = KleShape(gate_1_layer, barrier_points)

    sd.add_element(barrier_s.get_copy())
    sd.add_element(barrier_s.get_copy().move(
        0, -2 * DOT_R - BARRIER_WIDTH + BARRIER_OVERLAP * 2
    ))

    LEAD_HEIGHT = 0.200
    # LEAD_WIDTH = 0.100
    LEAD_OVERLAP = 0.000

    lead_points = [
        (-LEAD_WIDTH/2, DOT_R-BARRIER_OVERLAP + BARRIER_WIDTH - LEAD_OVERLAP),
        (LEAD_WIDTH/2, DOT_R-BARRIER_OVERLAP + BARRIER_WIDTH - LEAD_OVERLAP),
        (LEAD_WIDTH/2, DOT_R-BARRIER_OVERLAP + BARRIER_WIDTH - LEAD_OVERLAP + LEAD_HEIGHT),
        (-LEAD_WIDTH/2, DOT_R-BARRIER_OVERLAP + BARRIER_WIDTH - LEAD_OVERLAP + LEAD_HEIGHT),
    ]

    load_s = KleShape(ohm_layer, lead_points)

    sd.add_element(load_s.get_copy())
    sd.add_element(load_s.get_copy().move(
        0, -2 * DOT_R - BARRIER_WIDTH * 2 + BARRIER_OVERLAP * 2 - LEAD_HEIGHT + LEAD_OVERLAP * 2 - 0.001
    ))
    
    return sd
