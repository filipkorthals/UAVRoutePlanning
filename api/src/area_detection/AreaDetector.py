import ee
import geemap

from .MapFragment import MapFragment
from .Direction import Direction
from .PointData import PointData
import matplotlib.pyplot as plt
import math
import numpy as np
import cv2 as cv
import os

""" Class that is responsible of detecting areas in images that contain results of edge detection """


class AreaDetector:

    def __init__(self, edge_map: geemap.Image, map_center: ee.Geometry.Point, projection: ee.Projection):
        self.__edge_map = edge_map
        self.__projection = projection
        self.__map_center = map_center
        self.__detected_areas_map_fragments = [[]]  # MapFragments objects stored in array
        self.__detected_area_merged_image = []
        self.__patch_size = 255
        self.__img_resolution = 10
        self.__buffer_radius = ((self.__patch_size - 1) / 2) * self.__img_resolution
        self.__points_distance = 100 # distance of generated points in meters
        # we subtract center point from the patch size
        self.__map_fragments_counter = 0
        self.__BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        os.makedirs(self.__BASE_DIR + '/results', exist_ok=True)
        os.makedirs(self.__BASE_DIR + '/results/thresholding', exist_ok=True)
        os.makedirs(self.__BASE_DIR + '/results/morphology', exist_ok=True)
        os.makedirs(self.__BASE_DIR + '/results/contour_detection', exist_ok=True)
        os.makedirs(self.__BASE_DIR + '/results/edges', exist_ok=True)
        self.__load_map_fragment(self.__map_center, 0, 0)

    def __load_map_fragment(self, center_point: PointData, x_pos_to_insert: int, y_pos_to_insert: int):
        """ Initiates a map around center point of image """
        print("Loading map fragment")
        new_map_fragment = MapFragment(center_point, self.__projection, self.__buffer_radius, self.__edge_map,
                                       self.__img_resolution, self.__patch_size, self.__img_resolution)
        self.__detected_areas_map_fragments[y_pos_to_insert].insert(x_pos_to_insert, new_map_fragment)

        self.__map_fragments_counter += 1

        fig, ax = plt.subplots()

        ax.axis("off")
        ax.imshow(new_map_fragment.get_image(), cmap='gray')
        fig.savefig(self.__BASE_DIR + '/results/edges/Contours' + str(self.__map_fragments_counter) + '.jpg', dpi=500, bbox_inches='tight')

        plt.close(fig)

        print("Loading map fragment finished")
        print("\nStructure of loaded map: ")
        for row_id, row in enumerate(self.__detected_areas_map_fragments):
            print(str(row_id + 1) + ". row length:", int(len(row)))
        print('\n')

    def __search_row_for_the_map_fragment(self, map_fragment_center: PointData, point: PointData,
                                          row_num: int) -> tuple[int, int]:
        """ Searches for map fragment in row and returns coordinates of map fragment as [row_num, col_num] """
        print("Searching in row", row_num)
        direction_x = 0
        point_coordinates = point.get_coordinates_meters()
        map_fragment_center_coordinates = map_fragment_center.get_coordinates_meters()
        if (point_coordinates[0] - map_fragment_center_coordinates[0]) <= -self.__buffer_radius:
            direction_x = -1
        elif (point_coordinates[0] - map_fragment_center_coordinates[0]) >= self.__buffer_radius:
            direction_x = 1

        if direction_x >= 0:
            for col_num in range(len(self.__detected_areas_map_fragments[row_num])):
                if self.__detected_areas_map_fragments[row_num][col_num].contains_point(point):
                    print("Point is found on current map fragment - row", row_num, "col", col_num, "\n")
                    return row_num, col_num
            # if there is no buffer that contains searched point, we have to add next one
            while True:
                current_map_fragment = self.__detected_areas_map_fragments[row_num][-1]
                print("Loading map to the right")
                self.__load_map_fragment(current_map_fragment.find_near_map_fragment_center(direction_x, 0),
                                         len(self.__detected_areas_map_fragments[row_num]), row_num)
                if self.__detected_areas_map_fragments[row_num][-1].contains_point(point):
                    print("Point is found on current map fragment - row", row_num, "col",
                          len(self.__detected_areas_map_fragments[row_num]) - 1, "\n")
                    return row_num, len(self.__detected_areas_map_fragments[row_num]) - 1

        else:
            while True:
                current_map_fragment = self.__detected_areas_map_fragments[row_num][0]
                print("Loading map to the left")
                self.__load_map_fragment(current_map_fragment.find_near_map_fragment_center(direction_x, 0), 0, row_num)
                if self.__detected_areas_map_fragments[row_num][0].contains_point(point):
                    print("Point is found on current map fragment - row", row_num, "col", 0, "\n")
                    return row_num, 0

    def __search_for_the_map_fragment(self, row_num: int, point: PointData) -> tuple[int, int]:
        """ Searches self.__detected_areas_map for row where point is located and returns map fragment coordinates as
        [row_num, col_num]"""
        if row_num < 0:
            self.__detected_areas_map_fragments.insert(0, [])  # new row at the top is added
            current_map_fragment = self.__detected_areas_map_fragments[1][0]  # we start looking from the lower row
            print("Loading map up")
            self.__load_map_fragment(current_map_fragment.find_near_map_fragment_center(0, -1), 0, 0)
            return self.__search_for_the_map_fragment(row_num + 1, point)

        if row_num >= len(self.__detected_areas_map_fragments):
            current_map_fragment = self.__detected_areas_map_fragments[-1][0]  # we start from the last row
            self.__detected_areas_map_fragments.append([])
            print("Loading map down")
            self.__load_map_fragment(current_map_fragment.find_near_map_fragment_center(0, 1), 0,
                                     len(self.__detected_areas_map_fragments) - 1)
            return self.__search_for_the_map_fragment(row_num, point)

        map_fragment_center = self.__detected_areas_map_fragments[row_num][0].get_center_point()
        direction_y = 0
        point_coordinates = point.get_coordinates_meters()

        if (map_fragment_center.get_coordinates_meters()[1] - point_coordinates[1]) <= -self.__buffer_radius:
            direction_y = -1
        elif (map_fragment_center.get_coordinates_meters()[1] - point_coordinates[
            1]) >= self.__buffer_radius:
            direction_y = 1

        if direction_y == -1:
            if row_num - 1 < 0:
                current_map_fragment = self.__detected_areas_map_fragments[0][0]
                self.__detected_areas_map_fragments.insert(0, [])  # new row at the top is added
                print("Loading map up")
                self.__load_map_fragment(current_map_fragment.find_near_map_fragment_center(0, -1), 0,
                                         row_num)
                return self.__search_for_the_map_fragment(row_num + 1, point)
            else:
                return self.__search_for_the_map_fragment(row_num - 1, point)

        elif direction_y == 1:
            if row_num + 1 >= len(self.__detected_areas_map_fragments):
                current_map_fragment = self.__detected_areas_map_fragments[row_num][0]
                self.__detected_areas_map_fragments.append([])
                print("Loading map down")
                self.__load_map_fragment(current_map_fragment.find_near_map_fragment_center(0, direction_y), 0,
                                         row_num + 1)
            # we are moving searching to the next row
            return self.__search_for_the_map_fragment(row_num + 1, point)

        # if current row is correct, we start searching inside it
        return self.__search_row_for_the_map_fragment(map_fragment_center, point, row_num)

    def run_area_detection(self, points: list[PointData]) -> None:
        """ Detects area that contains provided point """
        points = self.__sort_points(points, self.__map_center)

        if len(points) > 2:
            points = self.__generate_points_grid(points)

        for number, point in enumerate(points):
            print("Detecting area for point", str(number + 1))
            # searching for corresponding map fragment for the point
            row_num, col_num = self.__search_for_the_map_fragment(0, point)

            found_map_fragment = self.__detected_areas_map_fragments[row_num][col_num]
            x, y = found_map_fragment.convert_point_to_img_coordinates(point)
            found_map_fragment.run_flood_fill(x, y)

            self.detect_in_adjacent_map_fragments(found_map_fragment, row_num)

    def __sort_points(self, points: list[PointData], center_point: PointData) -> list[PointData]:
        """ Sorts points that they are in counter-clockwise order """

        def get_angle(point: PointData) -> float:
            """ Returns the angle in between two points """
            center_x, center_y = center_point.get_coordinates_meters()
            point_x, point_y = point.get_coordinates_meters()
            return math.atan2(point_y - center_y, point_x - center_x)

        return sorted(points, key=get_angle)

    def detect_in_adjacent_map_fragments(self, found_map_fragment: MapFragment, row_num: int) -> None:
        """ Runs area detection in adjacent map fragments if this is necessary - when area detected previously is
        beyond current map fragment"""
        points_to_check = found_map_fragment.check_bounds()
        for direction in Direction:
            if len(points_to_check[direction.value]) == 0:
                # we don't have to check map fragment in this direction as there aren't any areas detected in this
                # direction
                continue

            new_row_num, new_col_num = (0, 0)
            if direction == Direction.TOP:
                print("Detecting adjacent area top")
                center_point = found_map_fragment.find_near_map_fragment_center(0, -1)
                new_row_num, new_col_num = self.__search_for_the_map_fragment(row_num - 1, center_point)
            elif direction == Direction.BOTTOM:
                print("Detecting adjacent area bottom")
                center_point = found_map_fragment.find_near_map_fragment_center(0, 1)
                new_row_num, new_col_num = self.__search_for_the_map_fragment(row_num + 1, center_point)
            elif direction == Direction.LEFT:
                print("Detecting adjacent area left")
                center_point = found_map_fragment.find_near_map_fragment_center(-1, 0)
                new_row_num, new_col_num = self.__search_for_the_map_fragment(row_num, center_point)
            else:
                print("Detecting adjacent area right")
                center_point = found_map_fragment.find_near_map_fragment_center(1, 0)
                new_row_num, new_col_num = self.__search_for_the_map_fragment(row_num, center_point)

            was_flood_fill_run = False
            for coordinates in points_to_check[direction.value]:
                # here we run flood fill for all fragments
                adjacent_fragment = self.__detected_areas_map_fragments[new_row_num][new_col_num]
                if adjacent_fragment.get_pixel_value(coordinates[0], coordinates[1]) == 0:
                    adjacent_fragment.run_flood_fill(coordinates[0], coordinates[1])
                    was_flood_fill_run = True

            if was_flood_fill_run:
                # we check if we have to detect anything in adjacent map fragments
                self.detect_in_adjacent_map_fragments(adjacent_fragment, new_row_num)

    def __merge_map(self) -> None:
        print("Merging map is starting")

        leftmost_map_fragment = None
        rightmost_map_fragment = None

        # searching for most left and most right map fragment
        for row in self.__detected_areas_map_fragments:
            if leftmost_map_fragment is None:
                leftmost_map_fragment = row[0]
            else:
                leftmost_map_fragment_center_x = leftmost_map_fragment.get_center_point().get_coordinates_meters()[0]
                current_map_fragment_center_x = row[0].get_center_point().get_coordinates_meters()[0]
                if current_map_fragment_center_x < leftmost_map_fragment_center_x:
                    leftmost_map_fragment = row[0]

            if rightmost_map_fragment is None:
                rightmost_map_fragment = row[-1]
            else:
                rightmost_map_fragment_center_x = rightmost_map_fragment.get_center_point().get_coordinates_meters()[0]
                current_map_fragment_center_x = row[-1].get_center_point().get_coordinates_meters()[0]
                if current_map_fragment_center_x > rightmost_map_fragment_center_x:
                    rightmost_map_fragment = row[-1]

        distance = (rightmost_map_fragment.get_center_point().get_coordinates_meters()[0] -
                    leftmost_map_fragment.get_center_point().get_coordinates_meters()[0])

        total_map_fragments_row = round(distance / self.__patch_size / self.__img_resolution) + 1

        merged_rows = []

        for row_num, row in enumerate(self.__detected_areas_map_fragments):
            distance_from_row_start = (row[0].get_center_point().get_coordinates_meters()[0] -
                    leftmost_map_fragment.get_center_point().get_coordinates_meters()[0])

            elements_from_start = int(round(distance_from_row_start / self.__patch_size / self.__img_resolution))

            # we add missing fragments to the map fragments (empty images are loaded for them)

            elements_to_end = total_map_fragments_row - elements_from_start - len(row)

            for i in range(elements_from_start):
                center_point = row[0].find_near_map_fragment_center(-1, 0)
                row.insert(0, MapFragment(center_point, self.__projection, self.__buffer_radius, None, self.__img_resolution, self.__patch_size, self.__img_resolution))

            for i in range(elements_to_end):
                center_point = row[0].find_near_map_fragment_center(1, 0)
                row.append(MapFragment(center_point, self.__projection, self.__buffer_radius, None,
                                          self.__img_resolution, self.__patch_size, self.__img_resolution))

            merged_row = np.concatenate([fragment.get_image() for fragment in row], axis=1)
            merged_rows.append(merged_row)

        self.__detected_area_merged_image = np.concatenate(merged_rows, axis=0).astype(np.uint8)
        print("Merging map finished")

        fig = plt.figure()

        plt.axis("off")
        plt.imshow(self.__detected_area_merged_image, cmap='gray')
        plt.savefig(self.__BASE_DIR + '/results/Edge_map.jpg', dpi=500, bbox_inches='tight')


    def prepare_for_points_extraction(self) -> None:
        """ Prepares detected areas on MapFragments for points extraction. Applies threshold and merges all fragments into one image """
        counter = 1
        for row in range(len(self.__detected_areas_map_fragments)):
            for column in range(len(self.__detected_areas_map_fragments[row])):
                self.__detected_areas_map_fragments[row][column].apply_two_thresholds()

                plt.figure()
                plt.imshow(self.__detected_areas_map_fragments[row][column].get_image(), cmap='gray')
                plt.axis("off")
                plt.savefig(self.__BASE_DIR + f'/results/thresholding/Thresholding{str(counter)}.jpg', dpi=500, bbox_inches='tight')
                plt.close()

                self.__detected_areas_map_fragments[row][column].apply_morphology_close(7)

                plt.figure()
                plt.imshow(self.__detected_areas_map_fragments[row][column].get_image(), cmap='gray')
                plt.axis("off")
                plt.savefig(self.__BASE_DIR + f'/results/morphology/Morphology{str(counter)}.jpg', dpi=500, bbox_inches='tight')
                plt.close()

                self.__detected_areas_map_fragments[row][column].apply_one_threshold()

                counter += 1

        self.__merge_map()

    def get_map_fragment(self, row_num: int, col_num: int):
        """ Returns map fragment at the provided position, function created for testing purposes """
        return self.__detected_areas_map_fragments[row_num][col_num]


    def get_boundary_points(self) -> tuple[list[int], list[int]]:
        """ Returns points of the detected areas boundaries """
        contours, hierarchy = cv.findContours(self.__detected_area_merged_image, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_TC89_KCOS)
        # saving result as the image
        image_contour = cv.cvtColor(self.__detected_area_merged_image, cv.COLOR_GRAY2BGR)  # Image for contours
        image_points = cv.cvtColor(self.__detected_area_merged_image, cv.COLOR_GRAY2BGR)  # Image for points

        for contour in contours:
            cv.drawContours(image_contour, [contour], -1, (255, 0, 255), 2)

        for contour in contours:
            for point in contour:
                cv.circle(image_points, tuple(point[0]), 1, (128, 0, 128), -1)

        image_contour_rgb = cv.cvtColor(image_contour, cv.COLOR_BGR2RGB)
        image_points_rgb = cv.cvtColor(image_points, cv.COLOR_BGR2RGB)

        # Plot side by side
        plt.figure(figsize=(12, 6))

        # Contours
        plt.subplot(1, 2, 1)
        plt.imshow(image_contour_rgb, cmap='gray')
        plt.title("Contours")
        plt.axis('off')

        # Points
        plt.subplot(1, 2, 2)
        plt.imshow(image_points_rgb, cmap='gray')
        plt.title("Contour Points")
        plt.axis('off')
        plt.savefig(self.__BASE_DIR + '/results/contour_detection/Contour.jpg', dpi=500, bbox_inches='tight')
        plt.close()

        return contours, hierarchy

    def get_coordinates_img_merged_map(self, point: PointData) -> tuple[int, int]:
        """ Returns coordinates of the point on the merged area map image """
        row_num, col_num = self.__search_for_the_map_fragment(0, point)
        x, y = self.__detected_areas_map_fragments[row_num][col_num].convert_point_to_img_coordinates(point)
        return x + (self.__patch_size * col_num), y + (self.__patch_size * row_num)

    def calculate_coordinates_meters(self, img_coordinates: tuple[int, int]) -> tuple[float, float]:
        """ Calculates img coordinates of point on the map in meters """
        row_num, col_num = img_coordinates[1] // self.__patch_size, img_coordinates[0] // self.__patch_size
        x, y = img_coordinates[0] % self.__patch_size, img_coordinates[1] % self.__patch_size
        x_meters, y_meters = self.__detected_areas_map_fragments[row_num][col_num].convert_img_coordinates_to_map_coordinates(x, y)
        return x_meters, y_meters

    def get_merged_map(self):
        """ Returns merged map of detected area """
        return self.__detected_area_merged_image

    def convert_boundary_points_to_degrees(self, contours: list[int]):
        """ Converts boundary points into degree coordinates """
        points = []

        for contour in contours:
            for point in contour:
                point_tmp = tuple(point[0])
                point = ee.Geometry.Point(self.calculate_coordinates_meters(point_tmp), self.__projection)
                points.append(point)

        points_collection = ee.FeatureCollection(points).map(
            lambda element: element.setGeometry(element.geometry().transform('EPSG:4326'))
        )

        # If there will be more than 65 536 points, the function will fail
        data = points_collection.getInfo()['features']
        points = [{'lng': point['geometry']['coordinates'][0], 'lat': point['geometry']['coordinates'][1]} for point in data]

        return points

    def convert_path_points_to_degrees(self, path: list[int]):
        """ Converts boundary points into degree coordinates """
        points = []

        for point in path:
            point_tmp = tuple(point.tolist())
            point = ee.Geometry.Point(self.calculate_coordinates_meters(point_tmp), self.__projection)
            points.append(point)

        points_collection = ee.FeatureCollection(points).map(
            lambda element: element.setGeometry(element.geometry().transform('EPSG:4326'))
        )

        # If there will be more than 65 536 points, the function will fail
        data = points_collection.getInfo()['features']
        points = [{'lng': point['geometry']['coordinates'][0], 'lat': point['geometry']['coordinates'][1]} for point in data]

        return points

    def __generate_points_grid(self, points: list[PointData]) -> list[PointData]:
        """ Generates grid of points in the selected area of interest """
        polygon_outline = points[:]
        polygon_outline.append(points[0])
        area_of_interest = ee.Geometry.Polygon([point.get_coordinates_degrees() for point in polygon_outline])

        scaled_projection = self.__projection.atScale(self.__points_distance)
        dummy_image = ee.Image(0).rename('dummy')

        grid_image = dummy_image.reproject(
            crs=scaled_projection,
            scale=self.__points_distance
        )

        point_grid = grid_image.sample(
            region=area_of_interest,
            scale=self.__points_distance,
            projection=scaled_projection,
            geometries=True  # Returns points instead of just sampled values
        )

        point_grid = point_grid.map(
            lambda element: element.setGeometry(element.geometry().transform('EPSG:4326'))
        )

        data = point_grid.getInfo()['features']
        points_coordinates = [(point['geometry']['coordinates'][0], point['geometry']['coordinates'][1]) for point in
                  data]

        for coordinates in points_coordinates:
            points.append(PointData(coordinates[0], coordinates[1], self.__projection))
            print(str(coordinates[1]) + ',' + str(coordinates[0]))

        return points