from kle.layout.layout import KleLayoutElement, create_shape
from kle.layout.layout_path_routing import (
    KlePoint,
    smooth_path,
    get_distance,
    get_vector_between_points
)


def get_routed_trace(layer, path, width=0.7, radii=1, phi_step=0.5):
    trace = KleLayoutElement("routed_trace")

    path = smooth_path([
        KlePoint(x, y) for x, y in path
    ], radii, phi_step)

    hull = []
    for i, klepoint in enumerate(path[:-1]):
        direction = get_vector_between_points(klepoint, path[i+1])
        perp = direction.get_unit().get_perp()

        hull.append(
            (klepoint + perp * width/2).get_tuple()
        )
        hull.insert(0,
            (klepoint - perp * width/2).get_tuple()
        )

    hull.append(
        (path[-1] + perp * width/2).get_tuple()
    )
    hull.insert(0,
        (path[-1] - perp * width/2).get_tuple()
    )

    trace.add_element(create_shape(
        layer, hull
    ))

    return trace

def get_polygon_sides(path, width=10, gap=5):
    """
    path is a path of (x, y) points
    """
    left_hull = []
    right_hull = []

    for i, klepoint in enumerate(path[:-1]):
        direction = get_vector_between_points(klepoint, path[i+1])
        
        perp = direction.get_unit().get_perp()

        left_hull.append(
            (klepoint + perp * width/2).get_tuple()
        )
        left_hull.insert(0,
            (klepoint + perp * (width/2 + gap)).get_tuple()
        )

        right_hull.append(
            (klepoint - perp * width/2).get_tuple()
        )
        right_hull.insert(0,
            (klepoint - perp * (width/2 + gap)).get_tuple()
        )
    
    # Add last point
    left_hull.append(
        (path[-1] + perp * width/2).get_tuple()
    )
    left_hull.insert(0,
        (path[-1] + perp * (width/2 + gap)).get_tuple()
    )

    right_hull.append(
        (path[-1] - perp * width/2).get_tuple()
    )
    right_hull.insert(0,
        (path[-1] - perp * (width/2 + gap)).get_tuple()
    )


    return left_hull, right_hull


def get_routed_cpw(layer, path, width, gap, radii=40, phi_step=0.5):
    cpw = KleLayoutElement("routed_cpw")

    path = [
        KlePoint(x, y) for x, y in path
    ]

    smooth_data = smooth_path(path, radii, phi_step)

    distance = get_distance(smooth_data)
    print("Distance:", round(distance, 2), "um")

    left_side, right_side = get_polygon_sides(smooth_data, width, gap)
    
    cpw.add_element(create_shape(
        layer,
        left_side # all the points of the hole hull on one side
    ))

    cpw.add_element(create_shape(
        layer,
        right_side # all the points of the hole hull on other side
    ))

    return cpw


# def get_resonator(layer, length, width, gap, radii=40, turn_length=100, y_lim=-2200, y_offset=-200):
#     path = [(0, 0), (0, y_offset)]

#     move_down = 1
#     turn = False
#     remaining_length = length + y_offset
#     while remaining_length > 0:
#         if not turn:
#             length_to_add = y_lim if remaining_length + y_lim > 0 else -remaining_length
#             path.append((path[-1][0], path[-1][1] + length_to_add * move_down))
#             remaining_length += length_to_add
#             turn = True

#         else:
#             path.append(
#                 (path[-1][0] + turn_length, path[-1][1])
#             )
#             remaining_length -= turn_length
#             turn = False
#             move_down *= -1

#     resonator = get_routed_cpw(
#         layer, path, width, gap, radii
#     )

#     return resonator

# def get_coupler(layer, res_width, res_gap, pl_width, pl_gap, coupler_width, coupler_height, coupler_gap, coupler_distance):
#     coupler = KleLayoutElement("coupler")

#     temp0 = -coupler_width/2 + res_width/2 + res_gap
#     s1 = create_shape(layer,
#         [
#             (0, 0), (res_gap, 0), (res_gap, coupler_height),
#             (temp0, coupler_height),
#             (temp0, coupler_height + res_width),
#             (temp0 - coupler_gap, coupler_height + res_width),
#             (temp0 - coupler_gap, coupler_height - coupler_gap),
#             (0, coupler_height-coupler_gap)
#         ]
#     )
#     coupler.add_element(s1.get_copy().move(-res_gap -res_width/2, 0))
#     coupler.add_element(s1.get_copy().flip_horizontally().move(res_gap + res_width/2, 0))
    
#     coupler.add_element(create_shape(layer, [
#         (0, 0), (2*coupler_gap + coupler_width, 0),
#         (2*coupler_gap + coupler_width, coupler_distance),
#         (0, coupler_distance)
#     ]).move(-coupler_gap - coupler_width/2, coupler_height + res_width))

#     temp1 = -coupler_width/2 + pl_width/2 + pl_gap
#     s2 = create_shape(layer,
#         [
#             (0, 0), (pl_gap, 0), (pl_gap, coupler_height),
#             (temp1, coupler_height),
#             (temp1, coupler_height + pl_width),
#             (temp1 -coupler_gap, coupler_height + pl_width),
#             (temp1 -coupler_gap, coupler_height - coupler_gap),
#             (0, coupler_height-coupler_gap)
#         ]
#     )
#     s2.flip_vertically()

#     coupler.add_element(s2.get_copy().move(
#         -pl_gap - pl_width/2,
#         coupler_height*2 + coupler_distance + res_width + pl_width
#     ))
#     coupler.add_element(s2.get_copy().flip_horizontally().move(
#         pl_gap + pl_width/2,
#         coupler_height*2 + coupler_distance + res_width + pl_width
#     ))

#     coupler.add_element(create_shape(layer, [
#         (0, 0), (pl_width, 0), (pl_width, pl_gap), (0, pl_gap)
#     ]).move(-pl_width/2, 2*coupler_height + coupler_distance + res_width + pl_width))

#     return coupler


# def get_grid(layer, x_pos, y_pos, size):
#     grid = KleLayoutElement("grid")
#     hole = create_shape(layer, [(0, 0), (0, size), (size, size), (size, 0)])

#     for x in x_pos:
#         for y in y_pos:
#             grid.add_element(hole.get_copy().move(x, y))

#     return grid