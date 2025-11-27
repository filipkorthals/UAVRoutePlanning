import ee
from .AreaDetector import AreaDetector
from .EdgeDetector import EdgeDetector
from .PointData import PointData

""" Class that controls detection of areas and returns results of it as a polygon points """


class AreaDetectionController:

    def __init__(self):
        self.area_detector: AreaDetector = None
        self.__projection = ee.Projection('EPSG:3035')  # projection that is accurate only to Europe!
        self.__points_list = None
        self.__points_feature_collection = None
        self.__map_center = None
        self.__edge_detector = None

    def initialize_with_points(self, points_list: list[PointData]):
        """ Initializes area detection with passed points """
        self.__points_list = points_list
        self.__points_feature_collection = ee.FeatureCollection(
            [ee.Feature(point.get_gee_point().transform(self.__projection)) for point in
             points_list])  # point is created as EPSG:4326 projection by default
        self.__map_center = PointData.from_gee_point(self.__points_feature_collection.geometry().centroid(), self.__projection)
        self.__edge_detector = EdgeDetector(self.__points_feature_collection, self.__map_center)

    def detect_areas(self) -> tuple[list[int], list[int]]:
        """ Detects area for all points that were provided to class """
        print("Detection of edges is starting")
        detected_edges_map = self.__edge_detector.detect_and_return_merged_bands()
        data = detected_edges_map.getInfo()
        print("Detection of edges is finished")
        self.area_detector = AreaDetector(detected_edges_map, self.__map_center, self.__projection)

        print("Detection of areas is starting")
        self.area_detector.run_area_detection(self.__points_list)
        print("Detection of areas is finished")

        print("Point extraction is starting")
        self.area_detector.prepare_for_points_extraction()
        contours, hierarchy = self.area_detector.get_boundary_points()  # this function returns points for path planning
        print("Point extraction is finished")

        return contours, hierarchy

    def get_merged_map(self):
        """ Returns merged map of detected area """
        return self.area_detector.get_merged_map()
