import ee
import time
from .area_detection.AreaDetectionController import AreaDetectionController
from .area_detection.PointData import PointData
import numpy as np
from .path_planning.PathAlgorithm import PathAlgorithm
from .path_planning.PathPlanner import PathPlanner

""" Class that is responsible of handling path planning for UAV """


class UAVPathPlanner:
    def __init__(self):
        ee.Authenticate()
        ee.Initialize(project="uav-route-planning")
        self.__area_detection_controller = AreaDetectionController()
        self.__path_planner = PathPlanner()

    def detect_area(self, points: list[PointData]) -> list[tuple[float, float]]:
        start = time.time()
        self.__area_detection_controller.initialize_with_points(points)
        self.__area_detection_controller.detect_areas()
        points_coordinates = self.__area_detection_controller.get_boundary_coordinates()  # points of detected area
        # now coordinates need to be reversed before using them on map
        print("Area detection time:", str(time.time() - start), "seconds")
        return points_coordinates

    def plan_path(self, points: list[PointData], velocity: float, travel_time: float):
        """ Function that handles path planning for UAV """
        start = time.time()
        self.__path_planner.resolution = 10
        scan_radius = 2000 / self.__path_planner.resolution

        # velocity needs to be converted from kmph to mps:
        velocity_in_m = velocity * 1000 / 3600

        self.__path_planner.algorithm = PathAlgorithm(scan_radius=scan_radius, scan_accuracy=2, predator_weight=1.5, distance_weight=1.5, turn_weight=0, resolution=self.__path_planner.resolution, velocity=velocity_in_m, travel_time=travel_time)
        self.__path_planner.priority_field = np.array([self.__area_detection_controller.area_detector.
                                                      get_coordinates_img_merged_map(point) for point in points])
        self.__path_planner.run_path_finding_detected_area(self.__area_detection_controller.get_contours(), self.__area_detection_controller.get_hierarchy(),
                                                           self.__area_detection_controller.get_merged_map(),
                                                           np.pi / 4)
        if self.__path_planner._path is None:
            return []
        self.__path_planner.smoothen_path(velocity, np.pi/6, 100)
        self.__path_planner.draw_path(self.__area_detection_controller.get_merged_map(), 0)
        print("Path planning time:", str(time.time() - start), "seconds")
        return self.__area_detection_controller.area_detector.convert_path_points_to_degrees(self.__path_planner._path), self.__path_planner.time_travelled



# code to execute
""" Detection using multiple points """
# uav_path_planner = UAVPathPlanner() # module initializes GEE - IMPORTANT

# longitude, latitude = 54.14392009809102, 18.644358525823773
# point = PointData(latitude, longitude, ee.Projection('EPSG:3035'))

# longitude, latitude = 54.1377860411294, 18.641354451774795
# point2 = PointData(latitude, longitude, ee.Projection('EPSG:3035'))

# longitude, latitude = 54.1407023454407, 18.636118779860862
# point3 = PointData(latitude, longitude, ee.Projection('EPSG:3035'))

# longitude, latitude = 54.14188645070116, 18.632651723670833
# point4 = PointData(latitude, longitude, ee.Projection('EPSG:3035'))

# longitude, latitude = 54.14502614281903, 18.63560379573818
# point5 = PointData(latitude, longitude, ee.Projection('EPSG:3035'))

# points_list = [point, point2, point3, point4, point5]

# uav_path_planner.plan_path(points_list)

