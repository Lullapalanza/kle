from kle.layout.layout_element import LayoutElement, Polygon


BLOCK_HEIGHT = 400
def get_number_unit_element(layer, scale=0.1):
    return Polygon(
        layer, [
            (0, 0),
            (100*scale, 100*scale),
            (100*scale, (100+BLOCK_HEIGHT)*scale),
            (0, (200+BLOCK_HEIGHT)*scale),
            (-100*scale, (100+BLOCK_HEIGHT)*scale),
            (-100*scale, 100*scale),
        ]
    )


def get_character_element(layer, character):
    character_element = LayoutElement(character)
    number_unit = get_number_unit_element(layer)
    if character == "0":
        character_element.add_elements([
            number_unit.get_copy(),
            number_unit.get_copy().move(60, 0),
            number_unit.get_copy().rotate_right(),
        ])

    return character_element


def get_chip_edges(virtual_layer, chip_size=3000, edge_thickness=10, design_id="000"):
    """
    Get edges as a visual marker 
    """
    edges = LayoutElement("chip_edges")
    b_edge_polygon = Polygon(
        virtual_layer,
        [
            (0, 0),
            (chip_size, 0),
            (chip_size, edge_thickness),
            (0, edge_thickness)
        ]
    )
    t_edge_polygon = b_edge_polygon.get_copy().move(0, chip_size - edge_thickness)
    l_edge_polygon = b_edge_polygon.get_copy().rotate_left().move(edge_thickness, 0)
    r_edge_polygon = l_edge_polygon.get_copy().move(chip_size - edge_thickness, 0)

    edges.add_element(b_edge_polygon)
    edges.add_element(t_edge_polygon)
    edges.add_element(l_edge_polygon)
    edges.add_element(r_edge_polygon)

    # characters = get_character_element(virtual_layer, "0")
    # characters.move(chip_size, 0)
    # edges.add_element(characters)

    return edges

def get_rf_slot_port(superconducting_layer, transmission_line_width=10):
    """
    Get RF port for a slot line
    """
    port = LayoutElement("port")

    port_center_conductor = Polygon(
        superconducting_layer,
        [
            (0, 0),
            (100, 0),
            (200, 50 - transmission_line_width/2),
            (200, 50 + transmission_line_width/2),
            (100, 100),
            (0, 100)
        ]
    )
    port.add_element(port_center_conductor)

    return port

def get_rf_port(superconducting_layer):
    """
    Get RF port
    """
    port = LayoutElement("port")

    port_bondpad = Polygon(
        superconducting_layer,
        [
            (0, 0),
            (100, 0),
            (200, 50 - 1),
            (200, 50 + 1),
            (100, 100),
            (0, 100)
        ]
    )

    port.add_subelement(port_bondpad)

    return port


def get_simple_interdigit_cap(layer, capacitor_gap=2, finger_width=3, length=10, number_of_fingers=5):
    cap = LayoutElement("capacitor")

    single_digit = Polygon(
        layer,
        [
            (0, 0), (0, length), (finger_width, length), (finger_width, finger_width),
            (2 * (finger_width+capacitor_gap), finger_width),
            (2 * (finger_width+capacitor_gap), 0), 
        ]
    )
    end_digit = Polygon(
        layer,
        [(0, 0), (0, length + finger_width + capacitor_gap), (finger_width, length + finger_width + capacitor_gap), (finger_width, 0)]
    )
    
    lower_half = LayoutElement("lower_half")
    lower_half.add_elements([
        single_digit.get_copy().move(i * 2 * (finger_width+capacitor_gap), 0) for i in range(number_of_fingers-1)
    ])
    lower_half.add_element(
        Polygon(
            layer,
            [(0, 0), (0, -finger_width), (2 * (number_of_fingers-1) * (capacitor_gap + finger_width), -finger_width), (2 * (number_of_fingers-1) * (capacitor_gap + finger_width), 0)]
        )
    )

    upper_half = lower_half.get_copy().rotate_left().rotate_left().move(
        (finger_width + capacitor_gap) * 2 * (number_of_fingers-1) - capacitor_gap,
        finger_width + capacitor_gap + length
    )

    cap.add_elements([
        lower_half, upper_half,
        end_digit.get_copy().move((finger_width + capacitor_gap) * 2 * (number_of_fingers-1), 0), # Finish last digit
        end_digit.get_copy().move(-(finger_width + capacitor_gap), 0) # Finish first digit
    ])

    return cap