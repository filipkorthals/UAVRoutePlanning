import numpy as np
import cv2
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.path import Path
from scipy.spatial import distance_matrix
import os


class PathPlanner:

    def __init__(self):
        self.algorithm = None
        self._path: np.array = None
        self._directions: np.array = None
        self._turns: np.array = None
        self.img_path: str = None
        self.starting_point: np.array = None
        self.starting_direction: float = None
        os.makedirs('src/path_planning/results', exist_ok=True)

    def run_path_finding(self):
        if self.algorithm is None:
            raise RuntimeError("PathPlanner No algorithm")
        if self.img_path is None or self.starting_direction is None or self.starting_point is None:
            raise RuntimeError("PathPlanner No algorithm params")
        self._path, self._directions, self._turns = self.algorithm.calculate_path(self.img_path, self.starting_point, self.starting_direction)

    def draw_path(self, merged_area: np.array):
        if self.img_path is not None:
            plt.title(self.img_path + str(self.algorithm))
        else:
            plt.title("Path planning result")
        rect_rgb = cv2.cvtColor(merged_area, cv2.COLOR_BGR2RGB)
        plt.imshow(rect_rgb)
        plt.plot(self._path[:, 0], self._path[:, 1], "r")
        plt.plot(self.starting_point[0], self.starting_point[1], 'bo')

        start = self._path[-1]
        next_point = self._path[-2]
        dx = next_point[0] - start[0]
        dy = next_point[1] - start[1]

        plt.quiver(start[0], start[1], dx, dy, color='b', angles='xy', scale_units='xy', scale=1)
        plt.savefig('src/path_planning/results/Planned_path.jpg')

    def run_path_finding_detected_area(self, contours: list[int], hierarchy: list[int], merged_map: np.array, starting_direction: float):
        M = cv2.moments(merged_map)
        if M["m00"] != 0:
            centroid_x = int(M["m10"] / M["m00"])
            centroid_y = int(M["m01"] / M["m00"])
        else:
            print("No detected area")
            return
        self.starting_point = [centroid_x, centroid_y]
        self.starting_direction = starting_direction
        self._path, self._directions, self._turns = self.algorithm.calculate_path_detected_area(contours, hierarchy, self.starting_point, self.starting_direction)
