from __future__ import annotations
import ee

""" Class used to store information about points and operations on them """


class PointData:
    def __init__(self, latitude: float, longitude: float, projection: ee.Projection, gee_point: ee.Geometry.Point = None):
        self.__coordinates_degrees = (latitude, longitude)
        self.__gee_point = gee_point if gee_point is not None else ee.Geometry.Point(latitude, longitude)
        self.__coordinates_meters = None
        self.__projection = projection

    @classmethod
    def from_gee_point(cls, gee_point: ee.Geometry.Point, projection: ee.Projection):
        """ Construction of class object using Google Earth Engine Point """
        latitude, longitude = gee_point.coordinates().getInfo()
        return cls(latitude, longitude, projection, gee_point)

    @classmethod
    def from_coordinates_meters(cls, x: float, y: float, projection: ee.Projection):
        """ Construction of class object using coordinates in meters """
        point = ee.Geometry.Point([x, y], projection).transform("EPSG:4326")
        created_point = PointData.from_gee_point(point, projection)
        created_point.__coordinates_meters = x, y
        return created_point

    def get_gee_point(self):
        """ Returns representation of point on Google Earth Engine server side """
        return self.__gee_point

    def get_coordinates_degrees(self):
        """ Returns coordinates of point in degrees """
        return self.__coordinates_degrees

    def get_coordinates_meters(self):
        """ Returns coordinates of point in meters """
        if self.__coordinates_meters is None:
            self.__coordinates_meters = self.__gee_point.transform(self.__projection).coordinates().getInfo()
        return self.__coordinates_meters