import klayout.db as pya


class Polygon:
    """
    Polygon (shape) with layer
    """
    def __init__(self, layer, points):
        self._layer = layer
        self._polygon = pya.DSimplePolygon(
            [pya.DPoint(x, y) for x, y in points]
        )

    def get_copy(self):
        copy = Polygon(self._layer, [])
        copy._polygon = self._polygon.dup()
        return copy

    def move(self, x, y):
        self._polygon.move(x, y)
        return self

    def rotate_left(self):
        self._polygon.transform(pya.DTrans(1))
        return self

    def rotate_right(self):
        self._polygon.transform(pya.DTrans(-1))
        return self

class LayoutElement:
    """
    Base element in layout
    """
    def __init__(self, name):
        self._name = name
        self._subelements = []

    def add_element(self, poly: Polygon):
        self._subelements.append(poly)

    def add_elements(self, list_of_poly: list[Polygon]):
        self._subelements.extend(list_of_poly)

    def move(self, x, y):
        [poly.move(x, y) for poly in self._subelements]
        return self

    def rotate_left(self):
        [poly.rotate_left() for poly in self._subelements]
        return self

    def rotate_right(self):
        [poly.rotate_right() for poly in self._subelements]
        return self

    def get_copy(self):
        copy = LayoutElement(self._name + "_copy")
        copy._subelements = [poly.get_copy() for poly in self._subelements]
        return copy

    def build_to_cell(self, main_cell):
        for poly in self._subelements:
            if type(poly) == LayoutElement:
                poly.build_to_cell(main_cell)
            elif type(poly) == Polygon:
                main_cell.shapes(poly._layer).insert(poly._polygon)


        
    