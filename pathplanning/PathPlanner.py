import numpy as np
import cv2
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.path import Path
from scipy.spatial import distance_matrix


class PathPlanner:

    def __int__(self):
        self.scan_radius = 1
        self.accuracy = 100

        self.field_points = np.array([])
        self.grid_param = 1

    def get_field_vertices(self, image : np.ndarray):
        pass

    def create_grid_points(self) -> np.array :
        pass

if __name__ == "__main__":
    rect = cv2.imread("rect.png")
    oval = cv2.imread("oval.png")
    blob = cv2.imread("blob.png")

    # Convert to grayscale
    gray = cv2.cvtColor(rect, cv2.COLOR_BGR2GRAY)

    # Threshold to get binary image
    _, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)

    # Find contours
    contours, hierarchy = cv2.findContours(thresh, cv2.RETR_LIST    , cv2.CHAIN_APPROX_TC89_KCOS     )

    contours = contours[:1]
    vertices_array = np.array(contours)
    vertices_array_shape = vertices_array.shape
    vertices_array = vertices_array.reshape((vertices_array_shape[1], vertices_array_shape[3]))
    print(vertices_array)
    alpha = np.arctan2(vertices_array[0][1] - vertices_array[1][1], vertices_array[0][0] - vertices_array[1][0])
    print("alpha = ", alpha)

    a = distance_matrix(vertices_array, vertices_array)
    print(a)
    print(np.array(a).max())

    scan_radius = 20
    accuracy = 2

    max_vertex_distance = np.array(a).max()

    grid_param = max_vertex_distance * 2 * scan_radius / accuracy
    print(grid_param)

    set_points_x = np.arange(-grid_param/2, grid_param/2, scan_radius/accuracy)
    set_points_y = np.arange(-grid_param/2, grid_param/2, scan_radius/accuracy)
    print(set_points_x)
    set_points = np.array([[[x,y] for x in set_points_x] for y in set_points_y])
    set_points = set_points.reshape((set_points.shape[0]**2, 2))
    set_points = np.array([[x * np.cos(alpha) - y*np.sin(alpha), x*np.sin(alpha)+y*np.cos(alpha)] for x, y in set_points])
    print(set_points)

    print(set_points)
    centre = np.array([np.average(set_points[:, 0]) - np.average(vertices_array[:, 0]), np.average(set_points[:, 1]) - np.average(vertices_array[:, 1])])
    set_points = set_points - centre

    #thetas = np.array([np.atan2((vertices_array[i+1][1] - vertices_array[i][1]), (vertices_array[i+1][0] - vertices_array[i][0])) for i in range(vertices_array.shape[0] - 2)])
    #print(vertices_array)
    #print(thetas)

    """
    final_points = set_points.copy()
    for i in range(thetas.shape[0]):
        set_points_prim = np.array([[x, y, x * np.cos(thetas[i]) + np.sin(thetas[i]) * y , y * np.cos(thetas[i]) -  x * np.sin(thetas[i])] for x, y in set_points])
        print(set_points_prim)
        set_points_final = np.array([[x, y] for x, y, x1, y1 in set_points_prim if x1 > -scan_radius/2 and y1 > -scan_radius/2  ] )

        # View rows as structured arrays for fast comparison
        a_view = set_points_final.view([('', set_points_final.dtype)] * set_points_final.shape[1])
        b_view = final_points.view([('',final_points.dtype)] * final_points.shape[1])

        common_rows = np.intersect1d(a_view, b_view).view(set_points_final.dtype).reshape(-1, set_points_final.shape[1])
        print(common_rows)
        final_points = common_rows
        # Draw contours on the original image

    print(final_points)"""

    centre = np.mean(vertices_array, axis=0)
    vectors = vertices_array - centre

    norms = np.linalg.norm(vectors, axis=1).reshape(-1, 1)
    unit_vectors = vectors / norms

    moved_polygon = vertices_array - scan_radius/4 * unit_vectors

    polygon = Path(moved_polygon)
    final_points = [point for point in set_points if polygon.contains_point(tuple([point[0], point[1]]))]

    looking_for_route = True
    path_points = final_points[:2]
    points_to_consider = np.array(final_points[2:])
    current_point = final_points[1]
    i = 2
    direction_angle = (final_points[1][1] - final_points[0][1]) / (final_points[1][0] - final_points[0][0])
    while looking_for_route:
        distances = distance_matrix(points_to_consider, [current_point])
        print(distances)
        condition = distances <= scan_radius/2
        print(condition)
        points_close_enough = points_to_consider[condition]
        next_point_index = np.array([x/y - direction_angle for x,y in points_close_enough - current_point]).argmin()
        current_point = points_close_enough[next_point_index]
        path_points.append(current_point)
        points_to_consider.remove(current_point)

    # Display the image

    plt.title("Contours on rect.png")
    # for contour in contours:
    #     for point in contour:
    #         x, y = point[0]
    #         plt.plot(x, y, 'ro')  # 'ro' means red circles
    plt.plot(final_points[0][0], final_points[0][1], 'bo')
    plt.plot(final_points[1][0], final_points[1][1], 'go')
    """for point in final_points[2:]:
        x, y = point
        plt.plot(x, y, 'ro')"""
    plt.plot(path_points[:, 0], path_points[:, 1], color="red")

    cv2.drawContours(rect, contours, -1, (0, 255, 0), 1)

    # Convert BGR to RGB for matplotlib
    rect_rgb = cv2.cvtColor(rect, cv2.COLOR_BGR2RGB)
    plt.imshow(rect_rgb)
    plt.show()





