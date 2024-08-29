from kle.layout.layout import KleLayoutElement, create_shape


def get_cpw_port(layer, connection_width, connection_gap, port_gap=10, port_width=80, port_length=80, taper_length=80):
    port = KleLayoutElement("port")

    top_gap = create_shape(layer, [
        (0, connection_width/2),
        (0, connection_width/2 + connection_gap),
        (-taper_length, port_width/2 + port_gap),
        (-taper_length -port_length, port_width/2 + port_gap),
        (-taper_length -port_length, port_width/2),
        (-taper_length, port_width/2)
        
    ])
    port.add_element(top_gap.get_copy())
    port.add_element(top_gap.get_copy().flip_vertically())
    
    return port

