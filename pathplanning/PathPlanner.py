import numpy as np
import cv2
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.path import Path
from scipy.spatial import distance_matrix
from scipy import interpolate

from HeuristicKorean import HeuristicKorean


class PathPlanner:

    def __init__(self):
        self.algorithm = None
        self._path: np.array = None
        self._directions: np.array = None
        self._turns: np.array = None
        self.img_path: str = None
        self.starting_point: np.array = None
        self.starting_direction: float = None
        self.priority_field: np.array = None

    def run_path_finding(self):
        if self.algorithm is None:
            raise RuntimeError("PathPlanner No algorithm")
        if self.img_path is None or self.starting_direction is None or self.starting_point is None:
            raise RuntimeError("PathPlanner No algorithm params")
        self._path, self._directions, self._turns = self.algorithm.calculate_path(self.img_path, self.starting_point, self.starting_direction, self.priority_field)

    def draw_path(self):
        plt.title(self.img_path + str(self.algorithm))
        plt.plot(self._path[:, 0], self._path[:, 1], "r")
        # plt.quiver(path[:, 0], path[:, 1], np.cos(direction_history), np.sin(direction_history), color='r', angles='xy')
        plt.plot(self.starting_point[0], self.starting_point[1], 'bo')

        plt.quiver(self.starting_point[0], self.starting_point[1], np.cos(self.starting_direction), np.sin(self.starting_direction),
                   color='b', angles='xy')

        # plt.plot(vertices_array[:, 0], vertices_array[:, 1], "g^")
        rect = cv2.imread(self.img_path)
        rect_rgb = cv2.cvtColor(rect, cv2.COLOR_BGR2RGB)
        plt.imshow(rect_rgb)
        plt.show()

    def calculate_path_score(self) -> (float, float):
        lengths = np.sqrt(np.sum(np.diff(self._path, axis=0)**2, axis=1))
        total_length = np.sum(lengths)

        number_of_no_turns = np.count_nonzero((self._turns > -0.1) & (self._turns < 0.1))
        number_of_small_turns = np.count_nonzero((self._turns > -np.pi/3) & (self._turns < np.pi/3)) - number_of_no_turns
        number_of_big_turns = np.count_nonzero(self._turns) - number_of_small_turns - number_of_small_turns

        turn_score = number_of_small_turns * 0.5 + number_of_big_turns
        return total_length, turn_score

    def smoothen_path(self):
        q_points = self._path * 0.75 + np.r_[[self.starting_point], self._path[:-1]] * 0.25
        r_points = self._path * 0.25 + np.r_[[self.starting_point], self._path[:-1]] * 0.75
        self._path = np.empty((2 * len(self._path), 2))
        self._path[1::2] = q_points
        self._path[0::2] = r_points


