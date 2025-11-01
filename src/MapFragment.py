import ee
import geemap
import numpy as np
from skimage.segmentation import flood_fill
import cv2 as cv
import matplotlib.pyplot as plt
from Direction import Direction
from PointData import PointData

""" Class that represents map fragments that are stored in AreaDetector class, makes map operations easier """


class MapFragment:
    def __init__(self, center_point: PointData, projection: ee.Projection, buffer_radius: float,
                 edge_map: geemap.Map, img_resolution: int):
        self.__buffer_radius = buffer_radius
        self.__img_resolution = img_resolution
        self.__projection = ee.Projection(projection)
        self.__center_point = center_point
        self.__scale = 5
        self.__map_representation = self.__move_rectangle_to_numpy(edge_map)

    def __move_rectangle_to_numpy(self, edge_map: geemap.Map) -> np.array:
        """ Converts map rectangle to NumPy array """
        # select buffer around center point
        buffer = self.__get_buffer_around_point(self.__center_point)
        img = edge_map.reproject(self.__projection, None, self.__scale)
        img = img.sampleRectangle(region=buffer, defaultValue=0).getInfo()

        # selecting band of the image
        img = np.array(img['properties']['max'], dtype=float)
        return img

    def contains_point(self, point: PointData) -> bool:
        """ Function that checks whether a point is inside the map fragment """
        if self.__get_buffer_around_point(self.__center_point).bounds(proj=self.__projection).intersects(
                point.get_gee_point()).getInfo():
            return True
        return False

    def __get_buffer_around_point(self, point: PointData) -> ee.Geometry:
        """ Returns buffer around point """
        return point.get_gee_point().buffer(self.__buffer_radius, proj=self.__projection)

    def find_near_map_fragment_center(self, x_direction: int, y_direction: int) -> PointData:
        """ Returns center point of map fragment next to the current one """
        x, y = self.__center_point.get_coordinates_degrees()
        latitude = x + x_direction * self.__buffer_radius * 2
        longitude = y - y_direction * self.__buffer_radius * 2
        return PointData(latitude, longitude, self.__projection)

    def run_flood_fill(self, x: int, y: int):
        """ Runs flood fill on map fragment - detected areas have value of 0.5 to differentiate them from the edges """
        self.__map_representation[:] = flood_fill(self.__map_representation, (y, x), 0.5)

    def apply_two_thresholds(self, threshold1: float = 0.0, threshold2: float = 1.0):
        """ Applies thresholding with two thresholds on map fragment to extract detected areas from image """
        for y in range(len(self.__map_representation)):
            for x in range(len(self.__map_representation[y])):
                if threshold1 < self.__map_representation[y][x] < threshold2:
                    self.__map_representation[y][x] = 255
                else:
                    self.__map_representation[y][x] = 0
        self.__map_representation = self.__map_representation.astype(np.uint8)

    def apply_one_threshold(self, threshold: float = 0):
        for y in range(len(self.__map_representation)):
            for x in range(len(self.__map_representation[y])):
                if self.__map_representation[y][x] > threshold:
                    self.__map_representation[y][x] = 255
                else:
                    self.__map_representation[y][x] = 0
        self.__map_representation = self.__map_representation.astype(np.uint8)

    def apply_morphology_close(self, kernel_size: int = 5):
        """ Applies morphological close with selected kernel size to reduce discontinuity in image, mask size needs
        to be odd number"""
        kernel = np.ones((kernel_size, kernel_size), np.uint8)
        self.__map_representation = cv.morphologyEx(self.__map_representation, cv.MORPH_CLOSE, kernel)

    def get_boundary_points(self) -> list[int]:
        """ Returns points of the detected areas boundaries """
        contours, hierarchy = cv.findContours(self.__map_representation, cv.RETR_CCOMP, cv.CHAIN_APPROX_TC89_KCOS)
        # tymczasowo -  rysowanie rezultatu
        image_contour = cv.cvtColor(self.__map_representation, cv.COLOR_GRAY2BGR)  # Image for contours
        image_points = cv.cvtColor(self.__map_representation, cv.COLOR_GRAY2BGR)  # Image for points

        # Draw the contours on the contour image
        for contour in contours:
            cv.drawContours(image_contour, [contour], -1, (255, 0, 255), 2)

            # Draw the points on the points image
        for contour in contours:
            for point in contour:
                cv.circle(image_points, tuple(point[0]), 1, (128, 0, 128), -1)

        image_contour_rgb = cv.cvtColor(image_contour, cv.COLOR_BGR2RGB)
        image_points_rgb = cv.cvtColor(image_points, cv.COLOR_BGR2RGB)

        # Plot side by side
        plt.figure(figsize=(12, 6))

        # Contours
        plt.subplot(1, 2, 1)
        plt.imshow(image_contour_rgb)
        plt.title("Contours")
        plt.axis('off')

        # Points
        plt.subplot(1, 2, 2)
        plt.imshow(image_points_rgb)
        plt.title("Contour Points")
        plt.axis('off')
        plt.savefig('Contour.jpg', dpi=500, bbox_inches='tight')
        plt.close()

        plt.show()

        return

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
        if self.__map_representation[y][x] == 0.5:
            if direction == Direction.TOP:
                points_for_flood_fill.append((x, 255))
            elif direction == Direction.BOTTOM:
                points_for_flood_fill.append((x, 0))
            elif direction == Direction.LEFT:
                points_for_flood_fill.append((255, y))
            elif direction == Direction.RIGHT:
                points_for_flood_fill.append((0, y))

    def get_image(self) -> np.array:
        """ Returns representation of map fragment as a np.array """
        return self.__map_representation

    def get_pixel_value(self, x: int, y: int) -> float:
        return self.__map_representation[y][x]

    def get_center_point(self):
        return self.__center_point

    def convert_point_to_img_coordinates(self, point: PointData) -> list[int]:
        """ Function that returns point ready to plot using matplotlib """
        if point.get_image_coordinates() is None:
            buffer = self.__center_point.get_gee_point().buffer(self.__buffer_radius, proj=self.__projection)

            # ????????? co to był za kod
            # buffer_origin = buffer.bounds(proj=projection).coordinates().getInfo()[0][3]
            # buffer_origin = ee.Geometry.Point(buffer_origin, proj=projection)
            # base = buffer_origin.coordinates().getInfo()  # base -> [y, x]
            # point_coordinates = point.get_coordinates_degrees()  # coordinates of point -> [y, x]

            buffer_origin = buffer.bounds(proj=self.__projection).coordinates().getInfo()[0][3]  # buffer_origin -> [y, x]
            point_coordinates = point.get_coordinates_meters()  # coordinates of point -> [y, x]

            y = int(round((buffer_origin[1] - point_coordinates[1]) / self.__img_resolution))
            x = int(round((point_coordinates[0] - buffer_origin[0]) / self.__img_resolution))

            point.set_image_coordinates(x, y)  # nie wiem czy współrzędne są w dobrej kolejności :)

        return point.get_image_coordinates()
