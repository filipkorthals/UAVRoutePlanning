from flask import Flask, request
from flask_cors import CORS
from api.src.UAVPathPlanner import UAVPathPlanner
from api.src.area_detection.PointData import PointData
import ee
import os
import matplotlib

matplotlib.use("Agg") 

app = Flask(__name__)

CORS(app, origins=["http://localhost:3000"])

os.makedirs('static', exist_ok=True)

uav_path_planner = UAVPathPlanner()

@app.route('/')
def siema():
    return 'siema'

@app.route('/area_detection', methods=['POST'])
def start_area_detection():
    data = request.get_json()
    waypoints = [marker['position'] for marker in data]

    # longitude, latitude = 53.324389, 18.455298
    # point = PointData(latitude, longitude, ee.Projection('EPSG:3035'))

    # longitude2, latitude2 = 53.325556, 18.443333
    # point2 = PointData(latitude2, longitude2, ee.Projection('EPSG:3035'))

    # longitude3, latitude3 = 53.328713, 18.447336
    # point3 = PointData(latitude3, longitude3, ee.Projection('EPSG:3035'))

    # longitude4, latitude4 = 53.324253, 18.450105
    # point4 = PointData(latitude4, longitude4, ee.Projection('EPSG:3035'))

    # longitude5, latitude5 = 53.318886, 18.426898
    # point5 = PointData(latitude5, longitude5, ee.Projection('EPSG:3035'))

    # longitude6, latitude6 = 53.318886, 18.426898
    # point6 = PointData(latitude6, longitude6, ee.Projection('EPSG:3035'))

    # points_list = [point3]

    points = []
    
    projection = ee.Projection('EPSG:3035')

    for waypoint in waypoints:
        points.append(PointData(waypoint['lng'], waypoint['lat'], projection))

    for point in points:
        print(point.get_coordinates_degrees())

    detected_area_boundary = uav_path_planner.detect_area(points)

    return detected_area_boundary

@app.route('/plan_path', methods=['POST'])
def plan_path():
    data = request.get_json()
    waypoints = [marker['position'] for marker in data]
    points = []

    projection = ee.Projection('EPSG:3035')

    for waypoint in waypoints:
        points.append(PointData(waypoint['lng'], waypoint['lat'], projection))

    for point in points:
        print(point.get_coordinates_degrees())

    uav_path_planner.plan_path(points)

    return {"url": "http://127.0.0.1:5001/static/Planned_path.jpg"}

if __name__ == '__main__':
    app.run(debug=True)