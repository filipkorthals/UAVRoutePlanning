import ee
from AreaDetector import AreaDetector
from EdgeDetector import EdgeDetector

""" Class that controls detection of areas and returns results of it as a polygon points """


class AreaDetectionController:

    def __init__(self, points_list: list[ee.Geometry.Point]):
        self.__area_detector = None
        self.__projection = ee.Projection('EPSG:3035')  # projection that is accurate only to Europe!
        self.__points = ee.FeatureCollection([ee.Feature(point.transform(self.__projection)) for point in
                                              points_list])  # point is created as EPSG:4326 projection by default
        self.__map_center = self.__points.geometry().centroid()
        self.__edge_detector = EdgeDetector(self.__points, self.__map_center, self.__projection)

    def run_area_detection(self):
        """ Detects area for all points that were provided to class """
        detected_edges_map = self.__edge_detector.detect_and_return_merged_bands()
        self.__area_detector = AreaDetector(detected_edges_map, self.__map_center, self.__projection)

        coordinates_list = self.__points.toList(self.__points.size()).map(
            lambda f: (ee.Feature(f).geometry().coordinates())
        ).getInfo()  # creating list of coordinates to use for function on the client side

        coordinates_list = [tuple(coordinates) for coordinates in coordinates_list]

        self.__area_detector.detect_areas(coordinates_list)

        self.__area_detector.extract_points()

        # self.__area_detector.plot_result(coordinates_list)  # delete this later