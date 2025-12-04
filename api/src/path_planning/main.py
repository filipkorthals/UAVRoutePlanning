import numpy as np

from PathAlgorithm import PathAlgorithm
from PathPlanner import PathPlanner

if __name__ == "__main__":
    path_planner = PathPlanner()
    path_planner.img_path = "test1.png"

    #starting_points = [[x, 10] for x in range(0, 350, 50)] \
    #                    + [[10, x] for x in range(0, 250, 50)]
    starting_points = [[10, 10]]
    for x, y in starting_points:
        path_planner.algorithm = PathAlgorithm(scan_radius=10, scan_accuracy=0.5, turn_weight=0, predator_weight=0, distance_weight=0)
        path_planner.priority_field = []
        path_planner.starting_point = [x, y]
        path_planner.starting_direction = np.arctan2(100 - y, 200 - x )

        path_planner.run_path_finding()
        print(path_planner.calculate_path_score())
        path_planner.draw_path()
        print(path_planner.calculate_path_score())
        path_planner.draw_path()