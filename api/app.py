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
    # planned_path = uav_path_planner.plan_path(points, data['velocity'], data['time'])
    planned_path = [
        {"lat": 53.32596434311779, "lng": 18.44977865505595},
        {"lat": 53.325337263130294, "lng": 18.448954881612252},
        {"lat": 53.324896859836585, "lng": 18.44806740570445},
        {"lat": 53.32445825428925, "lng": 18.446702580411028},
        {"lat": 53.324395624593734, "lng": 18.445319566387724},
        {"lat": 53.32432944027524, "lng": 18.4442536397614},
        {"lat": 53.32426295547066, "lng": 18.4431259385087},
        {"lat": 53.32405539004529, "lng": 18.44255186196048},
        {"lat": 53.32370433884174, "lng": 18.442402412626933},
        {"lat": 53.32351249104231, "lng": 18.442765684310388},
        {"lat": 53.32350573229667, "lng": 18.443488372001838},
        {"lat": 53.32355820016046, "lng": 18.44441549431164},
        {"lat": 53.32368766734227, "lng": 18.44568635847051},
        {"lat": 53.323856034168536, "lng": 18.447034587595653},
        {"lat": 53.324168234470775, "lng": 18.448883132521104},
        {"lat": 53.32446906804034, "lng": 18.450292381901335}
    ]

    return_data = {
        "area": detected_area_boundary,
        "path": planned_path,
    }

    return Response(json.dumps(return_data), mimetype='application/json')

if __name__ == '__main__':
    app.run(debug=True)