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
    """
    This keeps the abstract routing meaning direction in points
    """

def create_connection(x0, y0, x1, y1):
    return Connection(None, [(x0, y0), (x1, y1)], KleElementOrigin(0, 0), True)

def get_path_between_connections(c0, c1):
    return c0.get_absolute_points() + c1.get_absolute_points()[::-1]


class Connector(KleLayoutElement):
    """
    Physical representaion of the connector
    """
    def __init__(self, connector_polygons, label, connection, width):
        super().__init__()
        self.connection, self.label = connection, label
        self.width = width
        self.add_elements([connector_polygons, label, connection])

    def add_prefix(self, prefix):
        if self.label.text == "":
            self.label.text = prefix
        else:
            self.label.text = f"{prefix}_{self.label.text}"

    def connect_to(self, other, trace_layer):
        radii = max(self.width, other.width) * 1.2
        trace = get_routed_trace(
            trace_layer, get_path_between_connections(
                self.connection, other.connection
            ),
            self.width, other.width,
            radii=radii
        )
        self.add_element(trace)
        
        return other

    def __str__(self):
        return f"{self.label}, {self.connection}"


def get_simple_connector(layer, annotation_layer, connection_name,
    connection_points, connection_width, connection_height):
    
    x0, y0, x1, y1 = connection_points

    conn_vec_dir = KleVector(x1-x0, y1-y0).get_unit()
    connection_x0, connection_y0 = (KlePoint(x0, y0) + conn_vec_dir * connection_height).get_tuple()
    connection = create_connection(
        connection_x0, connection_y0, x1, y1,
    )

    # This is not great
    con_perp = conn_vec_dir.get_perp() # Get perp
    px0 = x0 + con_perp.x_dir * connection_width/2
    px1 = x0 - con_perp.x_dir * connection_width/2
    px2 = x0 + con_perp.x_dir * connection_width/2 + conn_vec_dir.x_dir * connection_height
    px3 = x0 - con_perp.x_dir * connection_width/2 + conn_vec_dir.x_dir * connection_height

    py0 = y0 + con_perp.y_dir * connection_width/2
    py1 = y0 - con_perp.y_dir * connection_width/2
    py2 = y0 + con_perp.y_dir * connection_width/2 + conn_vec_dir.y_dir * connection_height
    py3 = y0 - con_perp.y_dir * connection_width/2 + conn_vec_dir.y_dir * connection_height

    poly = create_shape(layer, [
        (px0, py0), (px1, py1),
        (px3, py3), (px2, py2)
    ])
    label = create_annotation(
        annotation_layer, connection_name,  0, 0
    ).move(connection_x0, connection_y0)
    
    connector = Connector(poly, label, connection, connection_width)

    return connector

# Radii must be smaller than the extra dim


class ConnectedElement(KleLayoutElement):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.connector_map = dict()

    def add_prefix(self, prefix):
        for se in self.subelements:
            if type(se) in [ConnectedElement, Connector]:
                se.add_prefix(prefix)

    def add_connector_or_element(self, prefix_or_label, other):
        if type(other) in [ConnectedElement, Connector]:
            other.add_prefix(prefix_or_label)
        self.connector_map[prefix_or_label] = other
        self.add_element(other)

    def build_to_cell(self, target_cell):
        return super().build_to_cell(target_cell)

    def get_connector(self, label):
        _map = self
        for l in label.split("_"):
            _map = _map.connector_map[l]
        
        return _map

    def add_with_child_prefix(self, other):
        if type(other) is type(self):
            self.connector_map.update(other.connector_map)
        
        self.add_element(other)
        return self

def get_connector_extention(layer, annotation_layer, connector, relative_shift):
    width = connector.width

    e0 = get_simple_connector(
        layer, annotation_layer, f"{connector.label.text}_E0",
        [0, 0, 0, -1], width, 0.2
    ).move(*relative_shift)
    
    e1 = get_simple_connector(
        layer, annotation_layer, f"{connector.label.text}_E1",
        [0, 0, 0, 1], width, 0.2
    ).move(*relative_shift)
    

    return e0, e1