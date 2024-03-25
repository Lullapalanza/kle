import klayout.db as pya

from kle.layout.layout_defaults import get_chip_edges


def get_new_layout():
    layout = pya.Layout()
    layout.dbu = 0.001

    # Make layers
    main_cell = layout.create_cell("main")

    l0 = layout.layer(0, 0, "base")

    edges, d_id = get_chip_edges(l0, 2500, 10, design_id="000")

    edges.build_to_cell(main_cell)
    d_id.build_to_cell(main_cell)

    return layout

if __name__ == "__main__":
    get_new_layout().write("C:/Users/nbr720/Documents/PhD/design/gds_files/test.gds")