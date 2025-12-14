from flask import Flask, request, Response
from flask_cors import CORS
from api.src.UAVPathPlanner import UAVPathPlanner
from api.src.area_detection.PointData import PointData
import ee
import os
import matplotlib
import json

matplotlib.use("Agg") 

app = Flask(__name__)

CORS(app, origins=["http://localhost:3000"])

os.makedirs('static', exist_ok=True)

uav_path_planner = UAVPathPlanner()

@app.route('/')
def hello_world():
    return 'Hello world!'

@app.route('/waypoints', methods=['POST'])
def start_area_detection():
    data = request.get_json()
    waypoints = [marker['position'] for marker in data['waypoints']]

    points = []
    
    projection = ee.Projection('EPSG:3035')

    for waypoint in waypoints:
        points.append(PointData(waypoint['lng'], waypoint['lat'], projection))

    for point in points:
        print(point.get_coordinates_degrees())

    detected_area_boundary = uav_path_planner.detect_area(points)
    planned_path = uav_path_planner.plan_path(points, data['velocity'], data['time'])

    return_data = {
        "area": detected_area_boundary,
        "path": planned_path,
    }

    return Response(json.dumps(return_data), mimetype='application/json')

if __name__ == '__main__':
    app.run(debug=True)