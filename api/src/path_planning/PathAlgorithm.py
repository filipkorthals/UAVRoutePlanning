import cv2
import numpy as np
from matplotlib import pyplot as plt
from scipy.spatial import distance_matrix
from matplotlib.path import Path


class PathAlgorithm:
    def __init__(self, scan_radius: float = 200, scan_accuracy: float = 1,
                 distance_weight: float = 1, turn_weight: float = 1,
                 predator_weight: float = 0.5, resolution: float = 20, travel_time: float = 30, velocity: float = 20):
        self.scan_radius = scan_radius
        self.scan_accuracy = scan_accuracy
        self.distance_weight = distance_weight
        self.turn_weight = turn_weight
        self.predator_weight = predator_weight
        self.resolution = resolution
        self.travel_time= travel_time
        self.velocity = velocity

    def get_contours(self, path: str) -> np.array:
        rect = cv2.imread(path)
        gray = cv2.cvtColor(rect, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
        contours, hierarchy = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_TC89_KCOS)
        return self.process_contours(contours, hierarchy)

    def process_contours(self, contours: list[int], hierarchy: list[int]):
        contours = contours[:1]
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

        grid_param = max_vertex_distance + self.scan_radius * 2
        print(grid_param)

        set_points_x = np.arange(-grid_param / 2, grid_param / 2, self.scan_radius / self.scan_accuracy)
        set_points_y = np.arange(-grid_param / 2, grid_param / 2, self.scan_radius / self.scan_accuracy)

        set_points = np.array([[[x, y] for x in set_points_x] for y in set_points_y])
        set_points = set_points.reshape((set_points.shape[0] ** 2, 2))
        set_points = np.array(
            [[x * np.cos(alpha) - y * np.sin(alpha), x * np.sin(alpha) + y * np.cos(alpha)] for x, y in set_points])
        print(set_points.size)
        centre = np.array([np.average(set_points[:, 0]) - np.average(vertices_array[:, 0]),
                           np.average(set_points[:, 1]) - np.average(vertices_array[:, 1])])
        set_points = set_points - centre

        polygon = Path(vertices_array)
        mask = polygon.contains_points(set_points)
        obstacle_mask = [False for _ in range(mask.size)]
        for obstacle in obstacles:
            obstacle_shape = Path(obstacle)
            obstacle_mask = obstacle_mask | obstacle_shape.contains_points(set_points)

        grid_points = set_points[mask ^ obstacle_mask]

        return grid_points

    def calculate_turn_cost(self, grid: np.array, current_point: np.array, current_direction: float):
        delta_vectors = grid - current_point
        target_angles = np.arctan2(delta_vectors[:, 1], delta_vectors[:, 0])
        angle_cost = target_angles - current_direction  # compensate for current direction
        angle_cost = (angle_cost + np.pi) % (2 * np.pi) - np.pi
        angle_cost = angle_cost.reshape(-1, 1)
        return angle_cost, target_angles

    def traverse_the_grid(self, grid_points: np.array, starting_point: np.array, starting_direction: float, priority_field: np.array) -> (np.array, np.array, np.array, float):
        visited = np.zeros(len(grid_points), dtype=bool)
        path, direction_history, turn_history = [starting_point], [], []

        current_point = starting_point
        current_direction = starting_direction

        predator = np.mean(grid_points, axis=0)
        predator_cost = distance_matrix(grid_points, [predator])
        predator_cost -= np.max(predator_cost)
        predator_cost *= -1

        priority_multiplier = 0.5
        if priority_field is not None:
            priority_factor = np.array([priority_multiplier if Path(priority_field).contains_point(point) else 1 for point in grid_points])
            priority_factor = priority_factor.reshape((priority_factor.size, 1))
        else:
            priority_factor = np.array([1 for _ in grid_points])
            priority_factor = priority_factor.reshape((priority_factor.size, 1))

        time_travelled = 0
        time_required_to_get_back = 0

        while not np.all(visited):
            print("Visited " + str(sum(visited)) + " out of " + str(grid_points.size / 2) + " waypoints")
            unvisited_grid = grid_points[~visited]
            # calculate costs
            distance_cost = distance_matrix(unvisited_grid, [current_point]) / self.scan_radius
            angle_cost, target_angles = self.calculate_turn_cost(unvisited_grid, current_point, current_direction)
            unvisited_predator_cost = predator_cost[~visited]

            cost_total = distance_cost * self.distance_weight + np.abs(angle_cost) * self.turn_weight \
                         + unvisited_predator_cost * self.predator_weight
            cost_total = np.multiply(cost_total, priority_factor[~visited])

            # choose the best next point
            best_next_idx = np.argmin(cost_total)
            current_point = unvisited_grid[best_next_idx]
            current_direction = target_angles[best_next_idx]

            # add time travelled to sum
            time_required = np.linalg.norm(current_point - path[-1]) * self.resolution / self.velocity / 60
            time_travelled += time_required
            time_required_to_get_back = np.linalg.norm(current_point - starting_point) * self.resolution / self.velocity / 60

            # update output
            path.append(current_point)
            direction_history.append(current_direction)
            turn_history.append(angle_cost[best_next_idx])

            # remove from further calculations
            visited[np.where(~visited)[0][best_next_idx]] = True

            if time_travelled + time_required_to_get_back >= self.travel_time * 0.99:
                print("Path planning stopping because of time")
                break

        time_travelled += time_required_to_get_back
        delta_vector = starting_point - current_point
        target_angles = np.arctan2(delta_vector[1], delta_vector[0])
        angle_cost = target_angles - current_direction  # compensate for current direction
        angle_cost = (angle_cost + np.pi) % (2 * np.pi) - np.pi

        return np.array(path + [starting_point]), np.array(direction_history+[target_angles]), np.array(turn_history+[angle_cost]), time_travelled

    def calculate_path(self, contours: list[int], hierarchy: list[int], starting_point: np.array, starting_direction: float, priority_field: np.array) -> (np.array, np.array, np.array):
        contour_vertices, obstacles = self.process_contours(contours, hierarchy)
        grid_points = self.create_grid(contour_vertices, obstacles)
        if grid_points.size == 0:
            return None, None, None
        return self.traverse_the_grid(grid_points, starting_point, starting_direction, priority_field)

    def __str__(self):
        return "Heuristic("+str(self.scan_radius)+","+str(self.scan_accuracy)+","+str(self.distance_weight)+","\
            +str(self.turn_weight)+","+str(self.predator_weight)+")"
