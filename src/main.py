import ee
import time
from AreaDetectionController import AreaDetectionController
from PointData import PointData

if __name__ == "__main__":
    start = time.time()
    ee.Authenticate()
    ee.Initialize(project="uav-route-planning")

    # code to execute
    """ Detection using multiple points """

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

    points_list = [point, point2, point3, point4, point5, point6]

    areaDetectionController = AreaDetectionController(points_list)
    areaDetectionController.run_area_detection()

    print("Total time:", str(time.time() - start), "seconds")
