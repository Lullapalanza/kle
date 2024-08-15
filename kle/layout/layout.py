import copy
import klayout.db as pya

LAYOUT_DBU = 0.001 # 1 nm

class KleLayer:
    def __init__(self, name, polarity, layer, layer_base=None):
        self.name = name
        self.polarity = polarity
        self.layer = layer
        self.layer_base = layer_base


class KleShape:
    """
    Shape with layer
    """
    def __init__(self, layer, points):
        self.layer = layer
        self.points = points

    def build_to_cell(self, target_cell):
        if self.layer.polarity == 1:
            target_cell.shapes(self.layer.layer).insert(
                pya.Polygon([pya.Point(x / LAYOUT_DBU, y / LAYOUT_DBU) for x, y in self.points])
            )
        elif self.layer.polarity == -1:
            self.layer.layer_base.insert_hole(
                [pya.Point(x / LAYOUT_DBU, y / LAYOUT_DBU) for x, y in self.points]
            )

    def get_copy(self):
        return KleShape(self.layer, copy.deepcopy(self.points))

    def move(self, delta_x, delta_y):
        self.points = [(x+delta_x, y+delta_y) for x, y in self.points]
        return self

    def flip_vertically(self):
        self.points = [(x, -y) for x, y in self.points]
        return self

    def flip_horizontally(self):
        self.points = [(-x, y) for x, y in self.points]
        return self

    def rotate_left(self):
        self.points = [(y, x) for x, y in self.points]
        return self

    # def rotate_left(self):
    #     self._polygon.transform(pya.DTrans(1))
    #     return self

    # def rotate_right(self):
    #     self._polygon.transform(pya.DTrans(-1))
    #     return self

class KleLayoutElement:
    """
    Base element in layout
    """
    def __init__(self, name):
        self.name = name
        self.subelements = []

    def add_element(self, subelement):
        self.subelements.append(subelement)

    def build_to_cell(self, target_cell):
        for subelement in self.subelements:
            subelement.build_to_cell(target_cell)

    def move(self, x, y):
        [subelem.move(x, y) for subelem in self.subelements]
        return self

    def flip_horizontally(self):
        [subelem.flip_horizontally() for subelem in self.subelements]
        return self

    def get_copy(self):
        copy = KleLayoutElement(self.name)
        for e in self.subelements:
            copy.add_element(e.get_copy())
        return copy



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
        self.elements_to_build.append(element)

    def build(self):
        for element in self.elements_to_build:
            element.build_to_cell(self.main_cell)

        for kle_layer in self.layers.values():
            if kle_layer.polarity == -1:
                self.main_cell.shapes(
                    kle_layer.layer
                ).insert(kle_layer.layer_base)

    def save_gds(self, file_path):
        self.layout.write(file_path)