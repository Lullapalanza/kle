"""
I want to be able to define some points as connection points and then automatically route some paths or
traces between them.

This should define some way to get connections, add them to the annotations layer
and if requested move them to a different layer and autoroute between 2 connections
"""
import copy
from kle.layout.layout import (
    create_shape, create_annotation, KleLayoutElement, KleLayerPoints,
    KleElementOrigin
)
from kle.layout.layout_path_routing import KleVector, KlePoint
from kle.layout.layout_trace_routing import get_routed_trace
from dataclasses import dataclass


@dataclass
class Connection(KleLayerPoints):
    name: str

    def build_to_cell(self, target_cell):
        pass

    def get_copy(self):
        return Connection(
            self.layer,
            copy.deepcopy(self.points),
            self.origin.copy(),
            False,
            self.name,
        )


class Connector(KleLayoutElement):
    def __init__(self, connection):
        super().__init__()
        self.connection = connection
        self.add_element(connection)


def create_connection(name, x0, y0, x1, y1):
    return Connection(
        None, [(x0, y0), (x1, y1)], KleElementOrigin(0, 0), True, name
    )

def get_path_between_connections(c0, c1):
    return c0.get_absolute_points() + c1.get_absolute_points()[::-1]

def get_trace_between_connections(layer, c0, c1, width):
    return get_routed_trace(layer, get_path_between_connections(c0, c1), width_start=width, width_end=4, radii=1)

def get_polygon_with_connection(layer, annotation_layer, connection_name, connection_points, connection_width=1, connection_height=0.2):
    x0, y0, x1, y1 = connection_points

    conn_vec = KleVector(x1-x0, y1-y0)
    conn_unit = conn_vec.get_unit()
    _x0, _y0 = (KlePoint(x0, y0) + conn_unit * connection_height).get_tuple()

    connection = create_connection(
        connection_name,
        _x0, _y0, x1, y1
    )
    connector = Connector(connection)

    con_perp = conn_unit.get_perp() # Get perp
    px0 = x0 + con_perp.x_dir * connection_width/2
    px1 = x0 - con_perp.x_dir * connection_width/2
    px2 = x0 + con_perp.x_dir * connection_width/2 + conn_unit.x_dir * connection_height
    px3 = x0 - con_perp.x_dir * connection_width/2 + conn_unit.x_dir * connection_height

    py0 = y0 + con_perp.y_dir * connection_width/2
    py1 = y0 - con_perp.y_dir * connection_width/2
    py2 = y0 + con_perp.y_dir * connection_width/2 + conn_unit.y_dir * connection_height
    py3 = y0 - con_perp.y_dir * connection_width/2 + conn_unit.y_dir * connection_height

    poly = create_shape(layer, [
        (px0, py0), (px1, py1),
        (px3, py3), (px2, py2)
    ])
    label = create_annotation(annotation_layer, connection_name,  0, 0).move(connection_points[0], connection_points[1] + connection_height)
    
    connector.add_element(poly)
    connector.add_element(label)

    return connector

# Radii must be smaller than the extra dim