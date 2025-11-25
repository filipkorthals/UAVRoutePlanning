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
        self.__path_planner.algorithm = HeuristicKorean()
        self.__path_planner.run_path_finding_detected_area(contours, hierarchy,
                                                           self.__area_detection_controller.get_merged_map(),
                                                           np.pi / 4)
        self.__path_planner.draw_path(self.__area_detection_controller.get_merged_map())
        print("Path planning time:", str(time.time() - start), "seconds")


# code to execute
""" Detection using multiple points """
uav_path_planner = UAVPathPlanner() # module initializes GEE - IMPORTANT

longitude, latitude = 53.324389, 18.455298
point = PointData(latitude, longitude, ee.Projection('EPSG:3035'))

longitude2, latitude2 = 53.325556, 18.443333
point2 = PointData(latitude2, longitude2, ee.Projection('EPSG:3035'))

longitude3, latitude3 = 53.328713, 18.447336
point3 = PointData(latitude3, longitude3, ee.Projection('EPSG:3035'))

longitude4, latitude4 = 53.324253, 18.450105
point4 = PointData(latitude4, longitude4, ee.Projection('EPSG:3035'))

longitude5, latitude5 = 53.318886, 18.426898
point5 = PointData(latitude5, longitude5, ee.Projection('EPSG:3035'))

longitude6, latitude6 = 53.318886, 18.426898
point6 = PointData(latitude6, longitude6, ee.Projection('EPSG:3035'))

points_list = [point, point3, point4, point5, point6]

uav_path_planner.plan_path(points_list)

