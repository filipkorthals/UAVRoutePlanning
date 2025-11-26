import ee
import time
from src.area_detection.AreaDetectionController import AreaDetectionController
from src.area_detection.PointData import PointData
import numpy as np
from src.path_planning.HeuristicKorean import HeuristicKorean
from src.path_planning.PathPlanner import PathPlanner

""" Class that is responsible of handling path planning for UAV """


class UAVPathPlanner:
    def __init__(self):
        ee.Authenticate()
        ee.Initialize(project="uav-route-planning")
        self.__area_detection_controller = AreaDetectionController()
        self.__path_planner = PathPlanner()

    def plan_path(self, points: list[PointData]):
        """ Function that handles path planning for UAV """
        start = time.time()
        self.__area_detection_controller.initialize_with_points(points)
        contours, hierarchy = self.__area_detection_controller.detect_areas()
        print("Area detection time:", str(time.time() - start), "seconds")

        start = time.time()
        self.__path_planner.algorithm = HeuristicKorean(predator_weight=0)
        self.__path_planner.starting_point
        self.__path_planner.priority_field = np.array([self.__area_detection_controller.area_detector.
                                                      get_coordinates_merged_map(point) for point in points])
        self.__path_planner.run_path_finding_detected_area(contours, hierarchy,
                                                           self.__area_detection_controller.get_merged_map(),
                                                           np.pi / 4)
        self.__path_planner.smoothen_path()
        self.__path_planner.draw_path(self.__area_detection_controller.get_merged_map())
        print("Path planning time:", str(time.time() - start), "seconds")


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

