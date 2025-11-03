import ee
import time
from AreaDetectionController import AreaDetectionController
from PointData import PointData

if __name__ == "__main__":
    start = time.time()
    ee.Authenticate()
    ee.Initialize(project="uav-route-planning")

    # code to execute
    """ Trying detection using two points """

    longitude = 53.324167
    latitude = 18.448611
    point = PointData(latitude, longitude, ee.Projection('EPSG:3035'))

    longitude2 = 53.325556
    latitude2 = 18.443333
    point2 = PointData(latitude2, longitude2, ee.Projection('EPSG:3035'))

    points_list = [point, point2]

    areaDetectionController = AreaDetectionController(points_list)
    areaDetectionController.run_area_detection()
    print("Total time:", str(time.time() - start), "seconds")
