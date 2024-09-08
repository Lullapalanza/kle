import math
import copy
import klayout.db as pya
from typing import Optional, Any
from dataclasses import dataclass

LAYOUT_DBU = 0.001 # 1 nm


@dataclass
class KleElementOrigin:
    x: float
    y: float

    def copy(self):
        return KleElementOrigin(self.x, self.y)


@dataclass
class KleLayer:
    name: str
    polarity: int
    layer: int
    layer_base: Optional[pya.Polygon] = None


@dataclass
class KleLayerPoints:
    layer: KleLayer
    points: list[tuple[float]]
    origin: KleElementOrigin
    holding_origin: bool

    def update_origin(self, new_origin):
        self.points = [
            (
                p[0] - new_origin.x + self.origin.x,
                p[1] - new_origin.y + self.origin.y,
            ) for p in self.points
        ]
        self.origin = new_origin
        self.holding_origin = False

    def build_to_cell(self, target_cell):
        pass

    def move(self, delta_x, delta_y):
        if self.holding_origin:
            self.origin.x += delta_x
            self.origin.y += delta_y
        else:
            self.points = [(x+delta_x, y+delta_y) for x, y in self.points]
        return self

    def flip_vertically(self):
        self.points = [(x, -y) for x, y in self.points]
        return self

    def flip_horizontally(self):
        self.points = [(-x, y) for x, y in self.points]
        return self

    def rotate_left(self):
        self.points = [(-y, x) for x, y in self.points]
        return self

    def rotate_right(self):
        self.points = [(y, -x) for x, y in self.points]
        return self

    def rotate_by_angle(self, angle):
        angle = angle * math.pi / 180 
        self.points = [(
            math.cos(angle) * x + math.sin(angle) * y,
            -math.sin(angle) * x + math.cos(angle) * y,
        ) for x, y in self.points]
        return self

    def get_absolute_points(self):
        return [
            (
                p[0] + self.origin.x,
                p[1] + self.origin.y
            ) for p in self.points
        ]

    def change_layer(self, new_layer):
        self.layer = new_layer

@dataclass
class KleAnnotation(KleLayerPoints):
    text: str

    def build_to_cell(self, target_cell):
        x, y = self.points[0]
        target_cell.shapes(self.layer.layer).insert(
            pya.DText(self.text, x + self.origin.x, y + self.origin.y)
        )

    def get_copy(self):
        return KleAnnotation(
            self.layer,
            copy.deepcopy(self.points),
            self.origin.copy(),
            False,
            self.text
        )

def create_annotation(layer, text, x, y):
    return KleAnnotation(layer, [(x, y)], KleElementOrigin(0, 0), True, text)


@dataclass
class KleShape(KleLayerPoints):
    def build_to_cell(self, target_cell):
        if self.layer.polarity == 1:
            target_cell.shapes(self.layer.layer).insert(
                pya.Polygon([
                    pya.Point((x+self.origin.x) / LAYOUT_DBU, (y+self.origin.y) / LAYOUT_DBU) for x, y in self.points
                ])
            )
        elif self.layer.polarity == -1:
            self.layer.layer_base.insert_hole(
                [pya.Point((x+self.origin.x) / LAYOUT_DBU, (y+self.origin.y) / LAYOUT_DBU) for x, y in self.points]
            )

    def get_copy(self):
        return KleShape(
            self.layer,
            copy.deepcopy(self.points),
            self.origin.copy(),
            False,
        )

def create_shape(layer, points):
    return KleShape(layer, points, KleElementOrigin(0, 0), True)


class KleLayoutElement:
    """
    Base element in layout
    """
    def __init__(self):
        self.subelements = []
        self.origin = None
        self.holding_origin = True

    def update_origin(self, new_origin):
        self.origin = new_origin
        self.holding_origin = False
        for se in self.subelements:
            se.update_origin(new_origin)
        return self

    def shift_origin(self, x, y):
        """
        Shift origin without moving the elements
        """
        self.origin.x += x
        self.origin.y += y
        for se in self.subelements:
            se.move(-x, -y)
        return self

    def add_element(self, subelement):
        self.origin = self.origin or subelement.origin
        subelement.update_origin(self.origin)
        self.subelements.append(subelement)

    def add_elements(self, subelements):
        for se in subelements:
            self.add_element(se)

    def build_to_cell(self, target_cell):
        for subelement in self.subelements:
            subelement.build_to_cell(target_cell)

    def move(self, x, y):
        if self.holding_origin:
            self.origin.x += x
            self.origin.y += y
        else:
            for se in self.subelements:
                se.move(x, y)
        return self

    def rotate_right(self):
        for se in self.subelements:
            se.rotate_right()
        return self

    def rotate_left(self):
        for se in self.subelements:
            se.rotate_left()
        return self

    def flip_horizontally(self):
        [subelem.flip_horizontally() for subelem in self.subelements]
        return self

    def flip_vertically(self):
        [subelem.flip_vertically() for subelem in self.subelements]
        return self

    def rotate_by_angle(self, angle):
        for se in self.subelements:
            se.rotate_by_angle(angle)
        return self

    def get_copy(self):
        copy = KleLayoutElement()
        for e in self.subelements:
            copy.add_element(e.get_copy())
        return copy

class NotElementError(BaseException):
    pass

class KleLayout:
    def __init__(self, width, height, layer_names):
        self.layout = pya.Layout()
        self.layout.dbu = LAYOUT_DBU
        self.main_cell = self.layout.create_cell("main")

        self.layers = {}
        for i, layer in enumerate(layer_names):
            polarity = -1 if layer[0] == "-" else 1
            layer_name = layer.strip("-")

            self.layers[layer_name] = KleLayer(
                layer_name,
                polarity,
                self.layout.layer(i, 0, layer_name)
            )

            # Make a base layer if polarity is negative
            if polarity == -1:
                layer_base = pya.Polygon(
                    [pya.Point(x, y) for x, y in [
                        (0, 0), (width / LAYOUT_DBU, 0),
                        (width/ LAYOUT_DBU, height / LAYOUT_DBU),
                        (0, height / LAYOUT_DBU)
                    ]]
                )
                self.layers[layer_name].layer_base = layer_base

        self.elements_to_build = []

    def get_layers(self):
        return self.layers

    def add_element(self, element):
        if not (issubclass(type(element), KleLayoutElement) or issubclass(type(element), KleLayerPoints)):
            raise NotElementError(element)
        self.elements_to_build.append(element)

    def build(self):
        for element in self.elements_to_build:
            element.build_to_cell(self.main_cell)

        for kle_layer in self.layers.values():
            if kle_layer.polarity == -1:
                self.main_cell.shapes(
                    kle_layer.layer
                ).insert(kle_layer.layer_base)

    def save(self, file_path):
        self.layout.write(file_path)

    def build_to_file(self, file_path):
        self.build()
        self.save(file_path)