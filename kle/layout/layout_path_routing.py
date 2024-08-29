"""
I want to autoroute a CPW with parameters and have it make some nice turns or something like that

Also to have connection points (ports)?
"""
import numpy as np


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
    
    def __rmul__(self, other):
        if type(other) in [float, int]:
            return KleVector(self.x_dir * other, self.y_dir * other)

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


def smooth_path(course_path, radii=20, phi_step=0.5):
    """
    course path is collection of x, y points that I want to split into smaller sizes and then
    round 

    return smoothed path from the course 
    """
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
        if dir_1.x_dir < 0:
            phi = -np.arccos(round(prev_c_point.x - center_r.x, 6)/radii)
        else:
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

