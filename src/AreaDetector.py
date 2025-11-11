import ee
import geemap
from MapFragment import MapFragment
from Direction import Direction
import matplotlib.pyplot as plt
from PointData import PointData

""" Class that is responsible of detecting areas in images that contain results of Canny Edge Detection """


class AreaDetector:

    def __init__(self, edge_map: geemap.Image, map_center: ee.Geometry.Point, projection: ee.Projection):
        self.__edge_map = edge_map
        self.__projection = projection
        self.__map_center = map_center  # nie wiem czy to jest jeszcze potrzebne, na razie zostaje
        self.__detected_areas_map = [[]]  # MapFragments objects stored in array
        self.__patch_size = 255
        self.__img_resolution = 5  # to chyba może być przerzucone w całości do klasy map fragment :)
        self.__buffer_radius = ((self.__patch_size - 1) / 2) * self.__img_resolution
        # we subtract center point from the patch size
        self.__load_map_fragment(self.__map_center, 0, 0)

    def __load_map_fragment(self, center_point: PointData, x_pos_to_insert: int, y_pos_to_insert: int):
        """ Initiates a map around center point of image """
        print("Loading map fragment")
        new_map_fragment = MapFragment(center_point, self.__projection, self.__buffer_radius, self.__edge_map,
                                       self.__img_resolution)
        self.__detected_areas_map[y_pos_to_insert].insert(x_pos_to_insert, new_map_fragment)
        print("Loading map fragment finished")
        print("\nStructure of loaded map: ")
        for row_id, row in enumerate(self.__detected_areas_map):
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
            for col_num in range(len(self.__detected_areas_map[row_num])):
                if self.__detected_areas_map[row_num][col_num].contains_point(point):
                    print("Point is found on current map fragment - row", row_num, "col", col_num, "\n")
                    return row_num, col_num
            # if there is no buffer that contains searched point, we have to add next one
            while True:
                current_map_fragment = self.__detected_areas_map[row_num][-1]
                print("Loading map to the right")
                self.__load_map_fragment(current_map_fragment.find_near_map_fragment_center(direction_x, 0),
                                         len(self.__detected_areas_map[row_num]), row_num)
                if self.__detected_areas_map[row_num][-1].contains_point(point):
                    print("Point is found on current map fragment - row", row_num, "col",
                          len(self.__detected_areas_map[row_num]) - 1, "\n")
                    return row_num, len(self.__detected_areas_map[row_num]) - 1

        else:
            while True:
                current_map_fragment = self.__detected_areas_map[row_num][0]
                print("Loading map to the left")
                self.__load_map_fragment(current_map_fragment.find_near_map_fragment_center(direction_x, 0), 0, row_num)
                if self.__detected_areas_map[row_num][0].contains_point(point):
                    print("Point is found on current map fragment - row", row_num, "col", 0, "\n")
                    return row_num, 0

    def __search_for_the_map_fragment(self, row_num: int, point: PointData) -> tuple[int, int]:
        # UWAGA - JEŻELI PUNKTY BĘDĄ W BARDZO DUŻYCH ODLEGŁOŚCIACH OD SIEBIE - WIĘCEJ NIŻ JEDEN SEGMENT TO SIĘ WYWALI
        # BO NIE ZNAJDZIE FRAGMENTU I NIE BĘDZIE WIEDZIAŁ JAK DODAĆ
        """ Searches self.__detected_areas_map for row where point is located and returns map fragment coordinates as
        [row_num, col_num]"""
        if row_num < 0:
            self.__detected_areas_map.insert(0, [])  # new row at the top is added
            current_map_fragment = self.__detected_areas_map[1][0]  # we start looking from the lower row
            print("Loading map up")
            self.__load_map_fragment(current_map_fragment.find_near_map_fragment_center(0, -1), 0, 0)
            return self.__search_for_the_map_fragment(row_num + 1, point)

        if row_num >= len(self.__detected_areas_map):
            current_map_fragment = self.__detected_areas_map[-1][0]  # we start from the last row
            self.__detected_areas_map.append([])
            print("Loading map down")
            self.__load_map_fragment(current_map_fragment.find_near_map_fragment_center(0, 1), 0,
                                     len(self.__detected_areas_map) - 1)
            return self.__search_for_the_map_fragment(row_num, point)

        map_fragment_center = self.__detected_areas_map[row_num][0].get_center_point()
        direction_y = 0
        point_coordinates = point.get_coordinates_meters()

        if (map_fragment_center.get_coordinates_meters()[1] - point_coordinates[1]) <= -self.__buffer_radius:
            direction_y = -1
        elif (map_fragment_center.get_coordinates_meters()[1] - point_coordinates[
            1]) >= self.__buffer_radius:
            direction_y = 1

        if direction_y == -1:
            if row_num - 1 < 0:
                current_map_fragment = self.__detected_areas_map[0][0]
                self.__detected_areas_map.insert(0, [])  # new row at the top is added
                print("Loading map up")
                self.__load_map_fragment(current_map_fragment.find_near_map_fragment_center(0, -1), 0,
                                         row_num)
                return self.__search_for_the_map_fragment(row_num + 1, point)
            else:
                return self.__search_for_the_map_fragment(row_num - 1, point)

        elif direction_y == 1:
            if row_num + 1 >= len(self.__detected_areas_map):
                current_map_fragment = self.__detected_areas_map[row_num][0]
                self.__detected_areas_map.append([])
                print("Loading map down")
                self.__load_map_fragment(current_map_fragment.find_near_map_fragment_center(0, direction_y), 0,
                                         row_num + 1)
            # we are moving searching to the next row
            return self.__search_for_the_map_fragment(row_num + 1, point)

        # if current row is correct, we start searching inside it
        return self.__search_row_for_the_map_fragment(map_fragment_center, point, row_num)

    def detect_areas(self, points: list[PointData]) -> None:
        """ Detects area that contains provided point """
        # TODO: try to paralelize detecting areas

        for number, point in enumerate(points):
            print("Detecting area for point", str(number + 1))
            # searching for corresponding map fragment for the point
            row_num, col_num = self.__search_for_the_map_fragment(0, point)

            found_map_fragment = self.__detected_areas_map[row_num][col_num]
            x, y = found_map_fragment.convert_point_to_img_coordinates(point)
            found_map_fragment.run_flood_fill(x, y)

            self.detect_in_adjacent_map_fragments(found_map_fragment, row_num)

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
                adjacent_fragment = self.__detected_areas_map[new_row_num][new_col_num]
                if adjacent_fragment.get_pixel_value(coordinates[0], coordinates[1]) == 0:
                    adjacent_fragment.run_flood_fill(coordinates[0], coordinates[1])
                    was_flood_fill_run = True

            if was_flood_fill_run:
                # we check if we have to detect anything in adjacent map fragments
                self.detect_in_adjacent_map_fragments(adjacent_fragment, new_row_num)

    def extract_points(self) -> list[tuple[float, float]]:
        """ Returns outline points from detected area """
        # dla filtrów liniowych jest też wersja, która działa na CUDA -
        # nie wiem czy jest sens ją implementować
        counter = 1
        for row in range(len(self.__detected_areas_map)):
            for column in range(len(self.__detected_areas_map[row])):
                self.__detected_areas_map[row][column].apply_two_thresholds()

                plt.figure()
                plt.imshow(self.__detected_areas_map[row][column].get_image(), cmap='gray', vmin=0, vmax=1)
                plt.axis("off")
                plt.savefig('Thresholding.jpg', dpi=500, bbox_inches='tight')
                plt.close()

                self.__detected_areas_map[row][column].apply_morphology_close(7)

                plt.figure()
                plt.imshow(self.__detected_areas_map[row][column].get_image(), cmap='gray', vmin=0, vmax=1)
                plt.axis("off")
                plt.savefig('Morhphology.jpg', dpi=500, bbox_inches='tight')
                plt.close()

                self.__detected_areas_map[row][column].apply_one_threshold()
                self.__detected_areas_map[row][column].get_boundary_points()
        return []

    def plot_result(self, points: list[PointData]) -> None:
        """ Plots result of area detection """
        # to też trzeba zmienić żeby plotowało więcej fragmentów niż tylko jeden
        counter = 1
        for row_index in range(len(self.__detected_areas_map)):
            for map_fragment in self.__detected_areas_map[row_index]:
                plt.figure()
                plt.imshow(map_fragment.get_image(), cmap='gray', vmin=0, vmax=1)
                for point in points:
                    prepared_coordinates = map_fragment.convert_point_to_img_coordinates(point)
                    plt.plot(prepared_coordinates[0], prepared_coordinates[1], 'ro', markersize=5)
                plt.axis("off")
                plt.savefig('Area_part_' + str(counter) + '.jpg', dpi=500, bbox_inches='tight')
                counter += 1

    def get_map_fragment(self, row_num: int, col_num: int):
        """ Returns map fragment at the provided position, function created for testing purposes """
        return self.__detected_areas_map[row_num][col_num]
