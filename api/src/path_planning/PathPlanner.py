import numpy as np
import cv2
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.path import Path
from numpy import tan
from numpy.ma.core import arctan
from scipy.spatial import distance_matrix
import os


def calculate_tangent_points(point: np.array, radius: float):
    distance_sq = np.sum(point ** 2)
    offset_from_centre = (radius ** 2) / distance_sq * point
    inverse_vector = np.array([-point[1], point[0]])
    delta = radius / distance_sq * np.sqrt(distance_sq - radius ** 2) * inverse_vector

    point1, point2 = offset_from_centre + delta, offset_from_centre - delta
    return point1, point2


class PathPlanner:

    def __init__(self):
        self.algorithm = None
        self.resolution = 10
        self._path: np.array = None
        self._directions: np.array = None
        self._turns: np.array = None
        self.time_travelled = 0
        self.img_path: str = None
        self.starting_point: np.array = None
        self.starting_direction: float = None
        self.priority_field: np.array = np.array([])
        # os.makedirs('src/path_planning/results', exist_ok=True)

    def run_path_finding(self):
        if self.algorithm is None:
            raise RuntimeError("PathPlanner No algorithm")
        if self.img_path is None or self.starting_direction is None or self.starting_point is None:
            raise RuntimeError("PathPlanner No algorithm params")
        self._path, self._directions, self._turns = self.algorithm.calculate_path(self.img_path, self.starting_point,
                                                                                  self.starting_direction,
                                                                                  self.priority_field)

    def draw_path(self, merged_area: np.array):
        plt.clf()
        if self.img_path is not None:
            plt.title(self.img_path + str(self.algorithm))
        else:
            plt.title("Path planning result")
        rect_rgb = cv2.cvtColor(merged_area, cv2.COLOR_BGR2RGB)
        plt.imshow(rect_rgb)
        plt.fill(self.priority_field[:, 0], self.priority_field[:, 1], "g",  alpha=0.3)
        if self._path is not None:
            plt.plot(self._path[:, 0], self._path[:, 1], "r")
        plt.plot(self.starting_point[0], self.starting_point[1], 'bo')
        start = self.starting_point
        dx = np.cos(self.starting_direction)
        dy = np.sin(self.starting_direction)

        plt.quiver(start[0], start[1], dx, dy, color='b', angles='xy', scale_units='xy', scale=1)
        # plt.savefig('src/path_planning/results/Planned_path.jpg')
        # zapisywanie w miejscu dostepnym z frontendu
        static_path = os.path.join(os.path.dirname(__file__), '../../static/Planned_path.jpg')
        static_path = os.path.abspath(static_path)

        plt.savefig(static_path)

    def run_path_finding_detected_area(self, contours: list[int], hierarchy: list[int], merged_map: np.array,
                                       starting_direction: float):

        self.starting_point = self.priority_field[0, :]
        self.starting_direction = starting_direction
        self._path, self._directions, self._turns, self.time_travelled = self.algorithm.calculate_path(contours,
                                                                                                       hierarchy,
                                                                                                       self.starting_point,
                                                                                                       self.starting_direction,
                                                                                                       self.priority_field)

    def validate_turns(self, velocity: float) -> float:
        maximal_turn = 0
        for i in range(0, len(self._path) - 2):
            (x1, y1), (x2, y2) = self._path[i], self._path[i + 2]
            x0, y0 = self._path[i + 1]

            distance = abs((y2 - y1) * x0 - (x2 - x1) * y0 + x2 * y1 - y2 * x1) / np.sqrt(
                (y2 - y1) ** 2 + (x2 - x1) ** 2)

            distance_in_m = distance * self.resolution
            velocity_in_m = velocity * 1000 / 3600

            turn = arctan((velocity_in_m ** 2) / (9.81 * distance_in_m))

            if turn > maximal_turn:
                maximal_turn = turn

        return maximal_turn

    def smoothen_path(self, velocity: float, bank_angle: float, margin: float):
        velocity_in_m = velocity * 1000 / 3600
        turn_radius = velocity_in_m ** 2 / (9.81 * tan(bank_angle))
        turn_radius_in_px = turn_radius / self.resolution
        margin_in_px = margin / self.resolution

        tangent_points_distance = turn_radius_in_px * np.abs(np.tan(self._turns / 2))
        tangent_arc_distance = turn_radius_in_px * (1 / np.cos(self._turns / 2) - 1)

        points_to_arc = (tangent_points_distance > 0.001) & (tangent_arc_distance <= margin_in_px)

        points_to_expand = tangent_arc_distance > margin_in_px

        smoothed_path = [self._path[0]]

        for index in range(1, self._turns.size):
            leg1_point = self._path[index - 1]
            corner_point = self._path[index]
            leg2_point = self._path[index + 1]

            if np.linalg.norm(leg1_point - corner_point) < turn_radius_in_px or np.linalg.norm(leg2_point - corner_point) < turn_radius_in_px:
                smoothed_path += [corner_point]
                print("Warning: dangerous maneouvers: (bank angle > "+ str(bank_angle*180/np.pi)+"deg) may be required")
                continue

            if points_to_arc[index]:

                vector21 = (leg1_point - corner_point)
                vector23 = (leg2_point - corner_point)

                point12 = corner_point + tangent_points_distance[index] * vector21 / np.linalg.norm(vector21)
                point23 = corner_point + tangent_points_distance[index] * vector23 / np.linalg.norm(vector23)

                smoothed_path += [point12, point23]

            elif points_to_expand[index]:

                middle = (leg2_point + leg1_point) / 2
                vector2m = middle - corner_point

                centre = corner_point + turn_radius_in_px * vector2m/np.linalg.norm(vector2m)

                # first point
                moved_point = leg1_point - centre
                point1, point2 = calculate_tangent_points(moved_point, turn_radius_in_px)

                chosen_point = None
                if self._turns[index] < 0:
                    chosen_point = point2
                else:
                    chosen_point = point1

                moved_point = leg2_point - centre
                point1, point2 = calculate_tangent_points(moved_point, turn_radius_in_px)

                chosen_point2 = None
                if self._turns[index] > 0:
                    chosen_point2 = point2
                else:
                    chosen_point2 = point1

                smoothed_path += [chosen_point + centre, corner_point, chosen_point2 + centre]

            else:
                smoothed_path += [corner_point]

        smoothed_path += [self._path[-1]]

        self._path = np.array(smoothed_path)

    def calculate_length(self):
        diffs = np.diff(self._path, axis=0)
        segment_lengths = np.linalg.norm(diffs, axis=1)
        return segment_lengths.sum()
