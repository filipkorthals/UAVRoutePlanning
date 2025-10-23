import numpy as np
import cv2
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.path import Path
from scipy.spatial import distance_matrix

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

    def run_path_finding(self):
        if self.algorithm is None:
            raise RuntimeError("PathPlanner No algorithm")
        if self.img_path is None or self.starting_direction is None or self.starting_point is None:
            raise RuntimeError("PathPlanner No algorithm params")
        self._path, self._directions, self._turns = self.algorithm.calculate_path(self.img_path, self.starting_point, self.starting_direction)

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


if __name__ == "__main__":
    path_planner = PathPlanner()
    path_planner.img_path = "rect.png"

    path_planner.algorithm = HeuristicKorean()
    path_planner.starting_point = [10, 10]
    path_planner.starting_direction = np.pi/4

    path_planner.run_path_finding()
    path_planner.draw_path()
