"""
I want to autoroute a CPW with parameters and have it make some nice turns or something like that

Also to have connection points (ports)?
"""
import numpy as np

from kle.layout.layout import KleLayoutElement, KleShape



class KleVector:
    def __init__(self, x_dir, y_dir):
        self.x_dir = x_dir
        self.y_dir = y_dir

    def get_length(self):
        return (self.x_dir**2 + self.y_dir**2)**0.5

    def get_unit(self):
        l = self.get_length()
        return KleVector(self.x_dir/l, self.y_dir/l)

    def get_perp(self):
        return KleVector(-self.y_dir, self.x_dir)

    def __mul__(self, other):
        if type(other) in [float, int]:
            return KleVector(self.x_dir * other, self.y_dir * other)
        elif type(other) == KleVector:
            return self.x_dir * other.x_dir + self.y_dir * other.y_dir

    def __truediv__(self, other):
        if type(other) in [float, int]:
            return KleVector(self.x_dir / other, self.y_dir / other)

    def __add__(self, other):
        if type(other) == KleVector:
            return KleVector(self.x_dir + other.x_dir, self.y_dir + other.y_dir)

    def __str__(self):
        return f"x_dir: {self.x_dir}, y_dir {self.y_dir}"

class KlePoint:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __add__(self, other):
        if type(other) == KlePoint:
            return KlePoint(self.x + other.x, self.y + other.y)
        elif type(other) == KleVector:
            return KlePoint(self.x + other.x_dir, self.y + other.y_dir)

    def __sub__(self, other):
        if type(other) == KlePoint:
            return KlePoint(self.x - other.x, self.y - other.y)
        elif type(other) == KleVector:
            return KlePoint(self.x - other.x_dir, self.y - other.y_dir)

    def get_tuple(self):
        return (self.x, self.y)

    def __str__(self):
        return f"x: {self.x}, y {self.y}"


def get_vector_between_points(p0, p1):
    return KleVector(*(p1-p0).get_tuple())

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

def smooth_path(course_path, radii=20, phi_step=0.5):
    """
    course path is collection of x, y points that I want to split into smaller sizes and then
    round 
    """
    # First add 2 new path nodes around every node with distance radii
    smooth_path = [course_path[0], ]
    for i, point in enumerate(course_path[1:-1]):
        dir_1 = get_vector_between_points(
            course_path[i], point
        ).get_unit()
        
        dir_2 = get_vector_between_points(
            point, course_path[i+2]
        ).get_unit()

        perp_1, perp_2 = dir_1.get_perp(), dir_2.get_perp()

        alpha = np.arccos(dir_1 * (dir_2 * -1))
        d = float(radii / np.tan(alpha/2))

        # Distinguish left and right turns
        if perp_1 * dir_2 > 0:
            sign = +1
        else:
            sign = -1
        
        center_r = point + dir_2 * d + perp_2 * radii * sign

        prev_c_point = point - dir_1 * d
        next_c_point = point + dir_2 * d
        # print(prev_c_point, center_r, (prev_c_point.x - center_r.x)/radii)
        phi = np.arccos(round(prev_c_point.x - center_r.x, 6)/radii)

        curr_point = KlePoint(
            center_r.x + radii * np.cos(phi),
            center_r.y - sign * radii * np.sin(phi)
        )
        smooth_path.append(curr_point) 

        while np.sqrt((curr_point - next_c_point).x**2 + (curr_point - next_c_point).y**2) > (radii * phi_step / (2 * np.pi)):
            phi = phi - phi_step/(2*np.pi)
            curr_point = KlePoint(
                center_r.x + radii * np.cos(phi),
                center_r.y - sign * radii * np.sin(phi)
            )
            smooth_path.append(curr_point)

    smooth_path.append(course_path[-1])

    return smooth_path

def get_distance(path):
    distance = 0
    p0 = path[0]
    for p in path[1:]:
        diff = p - p0
        distance += np.sqrt(diff.x**2 + diff.y**2)
        p0 = p
    return distance

def get_routed_cpw(layer, path, width, gap, radii=20, phi_step=0.5):
    cpw = KleLayoutElement("routed_cpw")

    path = [
        KlePoint(x, y) for x, y in path
    ]

    smooth_data = smooth_path(path, radii, phi_step)

    distance = get_distance(smooth_data)
    print("Distance:", round(distance, 2), "um")

    left_side, right_side = get_polygon_sides(smooth_data, width, gap)
    
    cpw.add_element(KleShape(
        layer,
        left_side # all the points of the hole hull on one side
    ))

    cpw.add_element(KleShape(
        layer,
        right_side # all the points of the hole hull on other side
    ))

    return cpw


def get_resonator(layer, length, width, gap, radii=40, turn_length=100, y_lim=-2200, y_offset=-200):
    path = [(0, 0), (0, y_offset)]

    move_down = 1
    turn = False
    remaining_length = length + y_offset
    while remaining_length > 0:
        if not turn:
            length_to_add = y_lim if remaining_length + y_lim > 0 else -remaining_length
            path.append((path[-1][0], path[-1][1] + length_to_add * move_down))
            remaining_length += length_to_add
            turn = True

        else:
            path.append(
                (path[-1][0] + turn_length, path[-1][1])
            )
            remaining_length -= turn_length
            turn = False
            move_down *= -1

    resonator = get_routed_cpw(
        layer, path, width, gap, radii
    )

    return resonator

def get_coupler(layer, res_width, res_gap, pl_width, pl_gap, coupler_width, coupler_height, coupler_gap, coupler_distance):
    coupler = KleLayoutElement("coupler")

    temp0 = -coupler_width/2 + res_width/2 + res_gap
    s1 = KleShape(layer,
        [
            (0, 0), (res_gap, 0), (res_gap, coupler_height),
            (temp0, coupler_height),
            (temp0, coupler_height + res_width),
            (temp0 - coupler_gap, coupler_height + res_width),
            (temp0 - coupler_gap, coupler_height - coupler_gap),
            (0, coupler_height-coupler_gap)
        ]
    )
    coupler.add_element(s1.get_copy().move(-res_gap -res_width/2, 0))
    coupler.add_element(s1.get_copy().flip_horizontally().move(res_gap + res_width/2, 0))
    
    coupler.add_element(KleShape(layer, [
        (0, 0), (2*coupler_gap + coupler_width, 0),
        (2*coupler_gap + coupler_width, coupler_distance),
        (0, coupler_distance)
    ]).move(-coupler_gap - coupler_width/2, coupler_height + res_width))

    temp1 = -coupler_width/2 + pl_width/2 + pl_gap
    s2 = KleShape(layer,
        [
            (0, 0), (pl_gap, 0), (pl_gap, coupler_height),
            (temp1, coupler_height),
            (temp1, coupler_height + pl_width),
            (temp1 -coupler_gap, coupler_height + pl_width),
            (temp1 -coupler_gap, coupler_height - coupler_gap),
            (0, coupler_height-coupler_gap)
        ]
    )
    s2.flip_vertically()

    coupler.add_element(s2.get_copy().move(
        -pl_gap - pl_width/2,
        coupler_height*2 + coupler_distance + res_width + pl_width
    ))
    coupler.add_element(s2.get_copy().flip_horizontally().move(
        pl_gap + pl_width/2,
        coupler_height*2 + coupler_distance + res_width + pl_width
    ))

    coupler.add_element(KleShape(layer, [
        (0, 0), (pl_width, 0), (pl_width, pl_gap), (0, pl_gap)
    ]).move(-pl_width/2, 2*coupler_height + coupler_distance + res_width + pl_width))

    return coupler

def get_grid(layer, x_pos, y_pos, size):
    grid = KleLayoutElement("grid")
    hole = KleShape(layer, [(0, 0), (0, size), (size, size), (size, 0)])

    for x in x_pos:
        for y in y_pos:
            grid.add_element(hole.get_copy().move(x, y))

    return grid