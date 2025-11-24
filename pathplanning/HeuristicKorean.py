import cv2
import numpy as np
from matplotlib import pyplot as plt
from scipy.spatial import distance_matrix
from matplotlib.path import Path


class HeuristicKorean:
    def __init__(self, scan_radius: float = 20, scan_accuracy: float = 1,
                 distance_weight: float = 1, turn_weight: float = 1,
                 predator_weight: float = 1):
        self.scan_radius = scan_radius
        self.scan_accuracy = scan_accuracy
        self.distance_weight = distance_weight
        self.turn_weight = turn_weight
        self.predator_weight = predator_weight

    def get_contours(self, path: str) -> (np.array, list):
        rect = cv2.imread(path)
        gray = cv2.cvtColor(rect, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
        contours, hierarchy = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_TC89_KCOS)
        obstacles = list(contours[:-1])
        contours = contours[-1:]
        vertices_array = np.array(contours)
        vertices_array_shape = vertices_array.shape
        vertices_array = vertices_array.reshape((vertices_array_shape[1], vertices_array_shape[3]))
        for index, obstacle in enumerate(obstacles):
            obstacles[index] = np.array(obstacle)
            obstacle_shape = obstacles[index].shape
            print(obstacle_shape)
            obstacles[index] = obstacles[index].reshape((obstacle_shape[0], obstacle_shape[2]))
        print(obstacles)
        return vertices_array, obstacles

    def create_grid(self, vertices_array: np.array, obstacles: list, alpha: float = None) -> np.array:
        if alpha is None:
            alpha = np.arctan2(vertices_array[0][1] - vertices_array[1][1], vertices_array[0][0] - vertices_array[1][0])

        a = distance_matrix(vertices_array, vertices_array)

        max_vertex_distance = np.array(a).max()

        grid_param = max_vertex_distance * 2 * self.scan_radius / self.scan_accuracy

        set_points_x = np.arange(-grid_param / 2, grid_param / 2, self.scan_radius / self.scan_accuracy)
        set_points_y = np.arange(-grid_param / 2, grid_param / 2, self.scan_radius / self.scan_accuracy)

        set_points = np.array([[[x, y] for x in set_points_x] for y in set_points_y])
        set_points = set_points.reshape((set_points.shape[0] ** 2, 2))
        set_points = np.array(
            [[x * np.cos(alpha) - y * np.sin(alpha), x * np.sin(alpha) + y * np.cos(alpha)] for x, y in set_points])

        centre = np.array([np.average(set_points[:, 0]) - np.average(vertices_array[:, 0]),
                           np.average(set_points[:, 1]) - np.average(vertices_array[:, 1])])
        set_points = set_points - centre
        centre = np.mean(vertices_array, axis=0)
        vectors = vertices_array - centre

        norms = np.linalg.norm(vectors, axis=1).reshape(-1, 1)
        unit_vectors = vectors / norms

        moved_polygon = vertices_array - self.scan_radius / 4 * unit_vectors

        polygon = Path(moved_polygon)

        obstacle_shapes = []
        for obstacle in obstacles:
            obstacle_shapes.append(Path(obstacle))

        grid_points = np.array([point for point in set_points if polygon.contains_point(tuple([point[0], point[1]])) and sum([obstacle_shape.contains_point(tuple([point[0], point[1]])) for obstacle_shape in obstacle_shapes]) == 0])

        return grid_points

    def calculate_turn_cost(self, grid: np.array, current_point: np.array, current_direction: float):
        delta_vectors = grid - current_point
        target_angles = np.arctan2(delta_vectors[:, 1], delta_vectors[:, 0])
        angle_cost = target_angles - current_direction  # compensate for current direction
        angle_cost = (angle_cost + np.pi) % (2 * np.pi) - np.pi
        angle_cost = angle_cost.reshape(-1, 1)
        return angle_cost, target_angles

    def traverse_the_grid(self, grid_points: np.array, starting_point: np.array, starting_direction: float, priority_field: np.array) -> (np.array, np.array, np.array):
        visited = np.zeros(len(grid_points), dtype=bool)
        path, direction_history, turn_history = [], [], []

        current_point = starting_point
        current_direction = starting_direction

        predator = np.mean(grid_points, axis=0)
        predator_cost = distance_matrix(grid_points, [predator])
        predator_cost -= np.max(predator_cost)
        predator_cost *= -1

        priority_multiplier = 0.5
        if priority_field is not None:
            priority_factor = np.array([priority_multiplier if Path(priority_field).contains_point(point) else 1 for point in grid_points])
        else:
            priority_factor = np.array([1 for _ in grid_points])

        while not np.all(visited):
            unvisited_grid = grid_points[~visited]
            # calculate costs
            distance_cost = distance_matrix(unvisited_grid, [current_point])
            angle_cost, target_angles = self.calculate_turn_cost(unvisited_grid, current_point, current_direction)
            unvisited_predator_cost = predator_cost[~visited]

            cost_total = distance_cost * self.distance_weight + np.abs(angle_cost) * self.turn_weight \
                         + unvisited_predator_cost * self.predator_weight
            cost_total = np.multiply(cost_total, priority_factor)

            # choose the best next point
            best_next_idx = np.argmin(cost_total)
            current_point = unvisited_grid[best_next_idx]
            current_direction = target_angles[best_next_idx]

            # update output
            path.append(current_point)
            direction_history.append(current_direction)
            turn_history.append(angle_cost[best_next_idx])

            # remove from further calculations
            visited[np.where(~visited)[0][best_next_idx]] = True

        return np.array(path + [starting_point]), np.array(direction_history), np.array(turn_history)

    def calculate_path(self, img_path: str, starting_point: np.array, starting_direction: float, priority_field: np.array) -> (np.array, np.array, np.array):
        contour_vertices, obstacles = self.get_contours(img_path)
        grid_points = self.create_grid(contour_vertices, obstacles)
        plt.title("grid")
        plt.plot(contour_vertices[:, 0], contour_vertices[:, 1], "g*")
        plt.plot(grid_points[:, 0], grid_points[:, 1], "r*")
        # plt.quiver(path[:, 0], path[:, 1], np.cos(direction_history), np.sin(direction_history), color='r', angles='xy')


        # plt.plot(vertices_array[:, 0], vertices_array[:, 1], "g^")
        rect = cv2.imread(img_path)
        rect_rgb = cv2.cvtColor(rect, cv2.COLOR_BGR2RGB)
        plt.imshow(rect_rgb)
        plt.show()
        return self.traverse_the_grid(grid_points, starting_point, starting_direction, priority_field)

    def __str__(self):
        return "Heuristic("+str(self.scan_radius)+","+str(self.scan_accuracy)+","+str(self.distance_weight)+","\
            +str(self.turn_weight)+","+str(self.predator_weight)+")"
