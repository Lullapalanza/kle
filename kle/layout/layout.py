import klayout.db as pya

class Layout:
    def __init__(self, design_id, layer_names, dbu=0.001):
        self.dbu = dbu
        self.layout = pya.Layout()
        self.main_cell = self.layout.create_cell("main")

        self.layers = {
            l_name: self.layout.layer(i, 0, l_name) for i, l_name in enumerate(layer_names)
        }

        self.elements_to_build = []

    def add_element(self, element):
        self.elements_to_build.append(element)

    def get_layers(self):
        return self.layers

    def build(self):
        for element in self.elements_to_build:
            element.build_to_cell(self.main_cell)

    def save_gds(self, file_path):
        self.layout.write(file_path)
