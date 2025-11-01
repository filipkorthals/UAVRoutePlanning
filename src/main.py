import ee
from AreaDetectionController import AreaDetectionController

if __name__ == "__main__":
    ee.Authenticate()
    ee.Initialize(project="uav-route-planning")

    # code to execute
    """ Trying detection using two points """

    longitude = 53.324167
    latitude = 18.448611
    point = ee.Geometry.Point([latitude, longitude])

    longitude2 = 53.325556
    latitude2 = 18.443333
    point2 = ee.Geometry.Point([latitude2, longitude2])

    points_list = [point, point2]

    areaDetectionController = AreaDetectionController(points_list)
    areaDetectionController.run_area_detection()
