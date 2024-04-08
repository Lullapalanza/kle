from kle.layout.layout import KleLayoutElement, KleShape


def get_cpw_port(layer, connection_width, connection_gap, port_gap=10, port_width=80):
    port = KleLayoutElement("port")
    DIAG_LENGTH = 80
    top_gap = KleShape(
        layer, [(0, 0), (port_width, 0), (port_width + DIAG_LENGTH, DIAG_LENGTH),
        (port_width + DIAG_LENGTH, DIAG_LENGTH + connection_gap), (port_width, port_gap), (0, port_gap)]
    )
    port.add_element(top_gap.get_copy())
    port.add_element(top_gap.get_copy().flip_vertically().move(0, 2 * DIAG_LENGTH + 2 * connection_gap + connection_width))
    
    return port.move(-DIAG_LENGTH - port_width, -DIAG_LENGTH - connection_gap - connection_width/2)

def get_cpw_probeline(layer, length=1000, width=5, gap=5):
    """
    Get CPW probeline also with port
    """
    pl = KleLayoutElement("probeline")

    port_width = 60
    pl.add_element(get_cpw_port(
        layer,
        width,
        gap,
        port_gap=10,
        port_width=port_width
    ))

    side_gap = KleShape(
        layer, [(0, 0), (length, 0), (length, gap), (0, gap)]
    )
    EXTRA_LEN = 1500
    l_shape_outer = KleShape(
        layer, [(0, 0), (gap + width, 0), (gap + width, 300 + gap), (width - EXTRA_LEN- gap, 300 + gap),
        (width - EXTRA_LEN - gap, 300), (width, 300), (width, gap), (0, gap)]
    ).move(length, 0)
    l_shape_inner = KleShape(
        layer, [(0, 0), (gap, 0), (gap, 300 - 3*gap - width),
        (gap - EXTRA_LEN, 300 -3*gap - width), (gap - EXTRA_LEN, 300 - 4*gap - width), (0, 300 - 4*gap - width)]
    ).move(length-gap, 2*gap + width)

    X_MOVE = 60 + port_width
    Y_MOVE = 2500

    pl.add_element(side_gap.get_copy())
    pl.add_element(side_gap.get_copy().move(0, gap + width))
    
    pl.add_element(l_shape_outer.get_copy())
    pl.add_element(l_shape_inner.get_copy())

    pl.move(X_MOVE, Y_MOVE)

    return pl


def get_straight_cpw_resonator(layer, length=1000, width=5, gap=5, cap_width=5, grounded=True):
    cpw_resonator = KleLayoutElement("cpw_resonator")
    
    side_gap = KleShape(
        layer, [(0, 0), (gap, 0), (gap, -length), (0, -length)]
    )
    top_gap = KleShape(
        layer, [(0, 0), (2*gap + width, 0), (2*gap + width, cap_width), (0, cap_width)]
    )

    X_MOVE = 1000
    Y_MOVE = 2500 - gap# TODO: FIX ME!

    cpw_resonator.add_element(top_gap)
    cpw_resonator.add_element(side_gap.get_copy())
    cpw_resonator.add_element(side_gap.get_copy().move(gap + width, 0))
    cpw_resonator.move(X_MOVE, Y_MOVE)

    return cpw_resonator


def get_angle_cpw_resonator(layer, length=1000, width=5, gap=5, cap_width=5, grounded=True):
    cpw_resonator = KleLayoutElement("cpw_resonator")
    
    side_gap = KleShape(
        layer, [(0, 0), (gap, 0), (gap, -length), (0, -length)]
    )
    top_gap = KleShape(
        layer, [(0, 0), (2*gap + width, 0), (2*gap + width, cap_width), (0, cap_width)]
    )

    ANGLE_LENGTH = 100
    EXTRA_LENGTH = 1500
    outer_angle = KleShape(
        layer, [
            (0, 0), (0, -2*gap-width), (ANGLE_LENGTH, -2*gap-width),
            (ANGLE_LENGTH, -width + EXTRA_LENGTH), (ANGLE_LENGTH-gap, -width+EXTRA_LENGTH),
            (ANGLE_LENGTH-gap, -width -gap), (gap, -width -gap), (gap, 0)
        ]
    ).move(0, -length)
    inner_angle = KleShape(
        layer, [
            (0, 0), (0, -gap), (ANGLE_LENGTH - 2*width - 2*gap, -gap),
            (ANGLE_LENGTH-2*width-2*gap, -width + EXTRA_LENGTH), (ANGLE_LENGTH-2*width-3*gap, -width + EXTRA_LENGTH),
            (ANGLE_LENGTH-2*width-3*gap, 0), (ANGLE_LENGTH - 2*width -gap, 0)
        ]
    ).move(gap + width, -length)


    X_MOVE = 1000
    Y_MOVE = 2500 - gap# TODO: FIX ME!

    cpw_resonator.add_element(top_gap)
    cpw_resonator.add_element(side_gap.get_copy())
    cpw_resonator.add_element(side_gap.get_copy().move(gap + width, 0))

    cpw_resonator.add_element(outer_angle.get_copy())
    cpw_resonator.add_element(inner_angle.get_copy())

    cpw_resonator.move(X_MOVE, Y_MOVE)

    return cpw_resonator