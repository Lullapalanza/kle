import math
import copy
import abc
import klayout.db as pya
from typing import Optional, Any
from dataclasses import dataclass

LAYOUT_DBU = 0.001 # 1 nm


@dataclass
class KleElementOrigin:
    """
    Class instance of origin (x, y) - multiple shapes combined together should use the same origin for
    transformations
    """
    x: float
    y: float

    def get_copy(self):
        return KleElementOrigin(self.x, self.y)


@dataclass
class KleLayer:
    """
    Layer object to keep track of the polarity and optional base polygon when needed
    """
    name: str
    layer: int
    layer_base: Optional[pya.Polygon] = None

    def move_base(self, x, y):
        """
        Move base polygon by x, y if it exists
        """
        if self.layer_base:
            self.layer_base.move(x, y)


@dataclass
class KleLayerPoints:
    """
    A list of points and an origin tied to a layer
    """
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

    @abc.abstractmethod
    def build_to_cell(self) -> list[tuple[pya.Polygon, KleLayer]]:
        raise NotImplementedError

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
        # print(self.origin.x, self.origin.y)
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

    def get_copy(self):
        return KleLayerPoints(
            layer=self.layer,
            points=copy.deepcopy(self.points),
            origin=self.origin.get_copy(),
            holding_origin=False
        )

@dataclass(kw_only=True)
class KleReference(KleLayerPoints):
    def build_to_cell(self, target=None):
        return []

    def get_copy(self):
        return KleReference(
            layer=self.layer,
            points=copy.deepcopy(self.points),
            origin=self.origin.get_copy(),
            holding_origin=False,
        )

def create_ref(x, y):
    return KleReference(None, [(x, y)], KleElementOrigin(0, 0), True)


@dataclass(kw_only=True)
class KleAnnotation(KleLayerPoints):
    text: str

    def build_to_cell(self, target=None):
        x, y = self.points[0]
        return [
            (pya.DText(self.text, x + self.origin.x, y + self.origin.y), self.layer)
        ]

    def get_copy(self):
        return KleAnnotation(
            layer=self.layer,
            points=copy.deepcopy(self.points),
            origin=self.origin.get_copy(),
            holding_origin=False,
            text=self.text
        )

def create_annotation(layer, text, x, y):
    return KleAnnotation(layer, [(x, y)], KleElementOrigin(0, 0), True, text)



# Need to fix how everything gets inserted

@dataclass
class KleShape(KleLayerPoints):
    def build_to_cell(self, target=None):
        """
        Build shape to target_cell,
            if positive polarity add polygon (can overlap)
            if negative add hole
        """
        if target is not None:
            points = [
                pya.Point(
                    round((x+self.origin.x) / LAYOUT_DBU),
                    round((y+self.origin.y) / LAYOUT_DBU)
                ) for x, y in self.points
            ]
            if all([target.inside(p) for p in points]):
                target.insert_hole(
                    [
                        pya.Point(
                            round((x+self.origin.x) / LAYOUT_DBU),
                            round((y+self.origin.y) / LAYOUT_DBU)
                        ) for x, y in self.points
                    ]
                )
            return []

        else:
            polygon = pya.Polygon([
                pya.Point(
                    round((x+self.origin.x) / LAYOUT_DBU),
                    round((y+self.origin.y) / LAYOUT_DBU)
                ) for x, y in self.points
            ])

        return [(polygon, self.layer), ]

    def get_copy(self):
        return KleShape(
            layer=self.layer,
            points=copy.deepcopy(self.points),
            origin=self.origin.get_copy(),
            holding_origin=False,
        )

def create_shape(layer, points):
    return KleShape(layer, points, KleElementOrigin(0, 0), True)


class KleLayoutElement:
    """
    Base abstract element in layout - can hold shapes or other elements as subelements
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

    def build_to_cell(self, target=None):
        polygons_to_add = []
        for subelement in self.subelements:
            elems = subelement.build_to_cell(target)
            polygons_to_add.extend(elems)
        return polygons_to_add


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


class KleCutOut(KleLayoutElement):
    def __init__(self, positive_elem):
        super().__init__()
        self.add_element(positive_elem)
    
    def build_to_cell(self, target=None):
        if target is not None:
            print("WARNING, TARGET FOR CUTOUT")

        target_and_layers = self.subelements[0].build_to_cell()

        targets = pya.EdgeProcessor().simple_merge_p2p([target for target, layer in target_and_layers], True, True)
        # print(type(target[0]))
        # print(type(target_and_layers[0][0]))
        
        polygons_to_add = [(_t, target_and_layers[0][1]) for _t in targets]
        for subelement in self.subelements[1:]:
            for pol_target in polygons_to_add:
                elems = subelement.build_to_cell(pol_target[0])
                polygons_to_add.extend(elems)
        return polygons_to_add

    def get_copy(self):
        copy = KleCutOut(self.subelements[0].get_copy())
        for e in self.subelements[1:]:
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
            if layer[0] == "-":
                target = pya.Polygon(
                    [pya.Point(x, y) for x, y in [
                        (0, 0), (width / LAYOUT_DBU, 0),
                        (width/ LAYOUT_DBU, height / LAYOUT_DBU),
                        (0, height / LAYOUT_DBU)
                    ]]
                )
            else:
                target = None

            layer_name = layer.strip("-")

            self.layers[layer_name] = KleLayer(
                layer_name,
                self.layout.layer(i, 0, layer_name),
                layer_base=target
            )

        self.elements_to_build = []

    def get_layers(self):
        return self.layers

    def add_element(self, element):
        if not (issubclass(type(element), KleLayoutElement) or issubclass(type(element), KleLayerPoints)):
            raise NotElementError(element)
        self.elements_to_build.append(element)

    def build(self):
        for element in self.elements_to_build:
            for poly, layer in element.build_to_cell():
                self.main_cell.shapes(layer.layer).insert(poly)

        for kle_layer in self.layers.values():
            if kle_layer.layer_base is not None:
                self.main_cell.shapes(
                    kle_layer.layer
                ).insert(kle_layer.layer_base)

    def save(self, file_path):
        self.layout.write(file_path)

    def build_to_file(self, file_path):
        self.build()
        self.save(file_path)