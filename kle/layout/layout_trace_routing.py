from kle.layout.layout import KleLayoutElement, create_shape
from kle.layout.layout_path_routing import (
    KlePoint,
    smooth_path,
    get_distance,
    get_vector_between_points
)

def get_smoothed_path(path, radii, phi_step):
    path = smooth_path([
        KlePoint(x, y) for x, y in path
    ], radii, phi_step)
    trace_length = get_distance(path)
    return path, trace_length


def get_routed_trace(layer, path, width_start=0.7, width_end=1, radii=0.5, phi_step=0.5):
    trace = KleLayoutElement()

    # Make a smooth path
    path = smooth_path([
        KlePoint(x, y) for x, y in path
    ], radii, phi_step)
    trace_length = get_distance(path)

    print("Distance:", round(trace_length, 2), "um")

    hull = []
    curr_len = 0
    for i, klepoint in enumerate(path[:-1]):
        direction = get_vector_between_points(klepoint, path[i+1])
        perp = direction.get_unit().get_perp()

        _width = width_start + (width_end - width_start) * curr_len / trace_length
        hull.append(
            (klepoint + perp * _width/2).get_tuple()
        )
        hull.insert(0,
            (klepoint - perp * _width/2).get_tuple()
        )

        curr_len += direction.get_length()

    hull.append(
        (path[-1] + perp * width_end/2).get_tuple()
    )
    hull.insert(0,
        (path[-1] - perp * width_end/2).get_tuple()
    )

    trace.add_element(create_shape(
        layer, hull
    ))

    return trace, trace_length

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
    cpw = KleLayoutElement()

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

