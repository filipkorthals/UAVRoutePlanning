from __future__ import annotations
import ee

""" Class used to store information about points and operations on them """


class PointData:
    def __init__(self, latitude: float, longitude: float, projection: ee.Projection, gee_point: ee.Geometry.Point = None):
        self.__coordinates_degrees = (latitude, longitude)
        self.__gee_point = gee_point if gee_point is not None else ee.Geometry.Point(latitude, longitude)
        self.__coordinates_meters = None
        self.__img_coordinates = None
        self.__projection = projection

    @classmethod
    def from_gee_point(cls, gee_point: ee.Geometry.Point, projection: ee.Projection):
        """ Construction of class object using Google Earth Engine Point """
        latitude, longitude = gee_point.coordinates().getInfo()
        return cls(latitude, longitude, projection, gee_point)

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

    def get_image_coordinates(self):
        """ Returns coordinates of point on MapFragment """
        return self.__img_coordinates

    def set_image_coordinates(self, latitude: int, longitude: int):
        """ Sets coordinates of point on MapFragment """
        self.__img_coordinates = (latitude, longitude)

    def convert_point_to_map_coordinates(self, x: int, y: int) -> tuple[float, float]:
        """ Converts point from map representation into the point coordinates that correspond to the real coordinates
        that are used by the map"""
        # TODO: musisz się dowiedzieć jak konkretnie ma to być wykorzystane wyświetlane - w jakim formacie będą
        #  docelowe współrzędne do wyświetlania oraz do planowania trasy
        return ()