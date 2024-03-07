import klayout.db as pya

from inspect import signature 


def get_new_layout():
    layout = pya.Layout()
    layout.dbu = 0.001

    # Make layers
    main_cell = layout.create_cell("main")

    l0 = layout.layer(0, 0, "base")
    l1 = layout.layer(1, 0, "alignment")
    l2 = layout.layer(2, 0, "plunger")
    l3 = layout.layer(3, 0, "kek")


    main_cell.shapes(l0).insert(pya.Box(0, 0, 1000, 2000))
    main_cell.shapes(l1).insert(pya.Box(500, 500, 1500, 2500).moved(500, 1500))
    main_cell.shapes(l2).insert(pya.Box(0, 0, 1000, 2000))
    main_cell.shapes(l3).insert(pya.Box(500, 500, 1500, 2500).moved(500, 1500))

    return layout

if __name__ == "__main__":
    get_new_layout().write("C:/Users/jyrgen/Desktop/test.oas")