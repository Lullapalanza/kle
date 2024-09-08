"""
Some kind of conditional bond pad
"""
from kle.layout.layout import KleLayoutElement, create_shape
from kle.layout.layout_connections import get_trace_between_connections, get_connector

BP_WIDTH = 160
BP_HEIGTH = 160
BP_CONNECTION_HEIGHT = 10
BP_CONNECTION_WIDTH = 4

def get_rectangle(layer, width, height):
    return create_shape(layer, [
        (-width/2, -height/2),
        (width/2, -height/2),
        (width/2, height/2),
        (-width/2, height/2)
    ])

def get_simple_pad(layer, annotation_layer, pad_id):
    """
    Bond pad that is just the same layer as asked for
    """
    pad_polygon = get_rectangle(layer, BP_WIDTH, BP_HEIGTH)
    connection = get_connector(
        layer, annotation_layer, pad_id,
        [0, -BP_HEIGTH, 0, -BP_HEIGTH -BP_CONNECTION_HEIGHT], BP_CONNECTION_WIDTH
    )

    return pad_polygon, connection

def get_pad_for_gates():
    pass


class BondPad(KleLayoutElement):
    def __init__(self, ohm_layer, annotation_layer, pad_id):
        super().__init__()
        self.pad, self.connection = get_simple_pad(annotation_layer, annotation_layer, pad_id)
        self.add_elements([self.pad, self.connection])

    def connect_to(self, other_connector):
        self.pad.change_layer(other_connection.layer)
        p = get_trace_between_connections(other_connection.layer, self.connection, othe_connection, 1)

        pass