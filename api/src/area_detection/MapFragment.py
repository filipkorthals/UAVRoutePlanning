import ee
import geemap
import numpy as np
from skimage.segmentation import flood_fill
import cv2 as cv
import matplotlib.pyplot as plt
from .Direction import Direction
from .PointData import PointData

FLOOD_FILL_COLOR = 0.5
BLACK = 0
WHITE = 255

""" Class that represents map fragments that are stored in AreaDetector class, makes map operations easier """


class MapFragment:
    def __init__(self, center_point: PointData, projection: ee.Projection, buffer_radius: float,
                 edge_map: geemap.Map, img_resolution: int, patch_size: int):
        self.__buffer_radius = buffer_radius
        self.__img_resolution = img_resolution
        self.__projection = ee.Projection(projection)
        self.__center_point = center_point
        self.__scale = 5
        self.__patch_size = patch_size
        if edge_map is not None:
            self.__map_representation = self.__move_rectangle_to_numpy(edge_map)
        else:
            self.__map_representation = np.zeros((self.__patch_size, self.__patch_size))


    def __move_rectangle_to_numpy(self, edge_map: geemap.Map) -> np.array:
        """ Converts map rectangle to NumPy array """
        # select buffer around center point
        buffer = self.__get_buffer_around_point(self.__center_point)
        img = edge_map.reproject(self.__projection, None, self.__scale)
        img = img.sampleRectangle(region=buffer, defaultValue=0).getInfo()

        # selecting band of the image
        img = np.array(img['properties']['merged_band'], dtype=float)
        return img

    def contains_point(self, point: PointData) -> bool:
        """ Function that checks whether a point is inside the map fragment """
        coordinates = self.convert_point_to_img_coordinates(point)
        print("Calculated coordinates in image:", str(coordinates[0]), str(coordinates[1]))
        if 0 <= coordinates[0] < self.__patch_size and 0 <= coordinates[1] < self.__patch_size:
            print("Point is inside current map fragment")
            return True
        print('Point isn\'t inside current map fragment')
        return False

    def __get_buffer_around_point(self, point: PointData) -> ee.Geometry:
        """ Returns buffer around point """
        return point.get_gee_point().buffer(self.__buffer_radius, proj=self.__projection)

    def find_near_map_fragment_center(self, x_direction: int, y_direction: int) -> PointData:
        """ Returns center point of map fragment next to the current one """
        x, y = self.__center_point.get_coordinates_meters()
        latitude = x + x_direction * self.__buffer_radius * 2
        longitude = y - y_direction * self.__buffer_radius * 2
        return PointData.from_coordinates_meters(latitude, longitude, self.__projection)

    def run_flood_fill(self, x: int, y: int):
        """ Runs flood fill on map fragment - detected areas have value of FLOOD_FILL_COLOR to differentiate them from the edges """
        if self.__map_representation[y][x] == BLACK:
            self.__map_representation[:] = flood_fill(self.__map_representation, (y, x), FLOOD_FILL_COLOR)

    def apply_two_thresholds(self, threshold1: float = 0.0, threshold2: float = 1.0):
        """ Applies thresholding with two thresholds on map fragment to extract detected areas from image """
        for y in range(len(self.__map_representation)):
            for x in range(len(self.__map_representation[y])):
                if threshold1 < self.__map_representation[y][x] < threshold2:
                    self.__map_representation[y][x] = WHITE
                else:
                    self.__map_representation[y][x] = BLACK
        self.__map_representation = self.__map_representation.astype(np.uint8)

    def apply_one_threshold(self, threshold: float = 0):
        for y in range(len(self.__map_representation)):
            for x in range(len(self.__map_representation[y])):
                if self.__map_representation[y][x] > threshold:
                    self.__map_representation[y][x] = WHITE
                else:
                    self.__map_representation[y][x] = BLACK
        self.__map_representation = self.__map_representation.astype(np.uint8)

    def apply_morphology_close(self, kernel_size: int = 5):
        """ Applies morphological close with selected kernel size to reduce discontinuity in image, mask size needs
        to be odd number"""
        kernel = np.ones((kernel_size, kernel_size), np.uint8)
        self.__map_representation = cv.morphologyEx(self.__map_representation, cv.MORPH_CLOSE, kernel)


    def check_bounds(self) -> tuple[
        list[tuple[int, int]], list[tuple[int, int]], list[tuple[int, int]], list[tuple[int, int]]]:
        """ Checks if any detected area is at the bounds of the map fragment and returns points for flood fill each
        adjacent map fragments"""
        points_for_flood_fill = ([], [], [], [])
        # tuple that contains list of the points that will be used for flood fill to the adjacent map fragments

        for i in range(len(self.__map_representation)):
            self.__check_bound(i, 0, points_for_flood_fill[0], Direction.TOP)
            self.__check_bound(i, -1, points_for_flood_fill[1], Direction.BOTTOM)
            self.__check_bound(0, i, points_for_flood_fill[2], Direction.LEFT)
            self.__check_bound(-1, i, points_for_flood_fill[3], Direction.RIGHT)

        return points_for_flood_fill

    def __check_bound(self, x: int, y: int, points_for_flood_fill: list[tuple[int, int]],
                      direction: Direction) -> None:
        """ Checks if an edge point is considered as a searched area and adds it to the list if that is true,
        returns boolean that informs if previous area was closed, possible values for direction is vertical and
        horizontal"""
        if self.__map_representation[y][x] == FLOOD_FILL_COLOR:
            if direction == Direction.TOP:
                points_for_flood_fill.append((x, self.__patch_size - 1))
            elif direction == Direction.BOTTOM:
                points_for_flood_fill.append((x, 0))
            elif direction == Direction.LEFT:
                points_for_flood_fill.append((self.__patch_size - 1, y))
            elif direction == Direction.RIGHT:
                points_for_flood_fill.append((0, y))

    def get_image(self) -> np.array:
        """ Returns representation of map fragment as a np.array """
        return self.__map_representation

    def get_pixel_value(self, x: int, y: int) -> float:
        return self.__map_representation[y][x]

    def get_center_point(self):
        return self.__center_point

    def get_buffer_origin_coordinates(self) -> tuple[float, float]:
        buffer_origin_x, buffer_origin_y = self.__center_point.get_coordinates_meters()

        buffer_origin_x -= self.__buffer_radius
        buffer_origin_y += self.__buffer_radius

        return buffer_origin_x, buffer_origin_y

    def convert_point_to_img_coordinates(self, point: PointData) -> tuple[int, int]:
        """ Function that returns point ready to plot using matplotlib """

        buffer_origin_x, buffer_origin_y = self.get_buffer_origin_coordinates()
        point_coordinates_x, point_coordinates_y = point.get_coordinates_meters()

        y = int(round((buffer_origin_y - point_coordinates_y) / self.__img_resolution))
        x = int(round((point_coordinates_x - buffer_origin_x) / self.__img_resolution))

        return x, y

    def convert_img_coordinates_to_map_coordinates(self, x_img: int, y_img: int) -> tuple[float, float]:
        """ Converts point from map representation into the point coordinates that correspond to the real coordinates
        that are used by the map (in meters) """
        buffer_origin_coordinates = self.get_buffer_origin_coordinates()
        x_map = buffer_origin_coordinates[0] + x_img * self.__img_resolution
        y_map = buffer_origin_coordinates[1] - y_img * self.__img_resolution
        return x_map, y_map
