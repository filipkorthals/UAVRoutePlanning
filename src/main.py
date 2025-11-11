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

    longitude = 53.324389
    latitude = 18.455298
    point = PointData(latitude, longitude, ee.Projection('EPSG:3035'))

    longitude2 = 53.325556
    latitude2 = 18.443333
    point2 = PointData(latitude2, longitude2, ee.Projection('EPSG:3035'))

    longitude3 = 53.328713
    latitude3 = 18.447336
    point3 = PointData(latitude3, longitude3, ee.Projection('EPSG:3035'))

    longitude4 = 53.324253
    latitude4 = 18.450105
    point4 = PointData(latitude4, longitude4, ee.Projection('EPSG:3035'))

    points_list = [point, point2, point3, point4]

    areaDetectionController = AreaDetectionController(points_list)
    areaDetectionController.run_area_detection()

    print("Total time:", str(time.time() - start), "seconds")
