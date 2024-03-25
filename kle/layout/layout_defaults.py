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
        character_element.add_polygons([
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

    edges.add_polygon(b_edge_polygon)
    edges.add_polygon(t_edge_polygon)
    edges.add_polygon(l_edge_polygon)
    edges.add_polygon(r_edge_polygon)

    characters = get_character_element(virtual_layer, "0")
    characters.move(chip_size, edge_thickness)

    return edges, characters

def get_rf_port(superconducting_layer):
    """
    Get RF port
    """
    pass