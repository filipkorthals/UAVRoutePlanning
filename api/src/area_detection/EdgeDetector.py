import ee
import geemap
from .PointData import PointData

"""Class detecting edges in images using different bands from Sentinel-2"""


class EdgeDetector:
    def __init__(self, points: ee.FeatureCollection, map_center: PointData):
        self.__time_periods = [('2023-05-01', '2023-10-01'), ('2024-05-01', '2024-10-01'),
                               ('2025-05-01', '2025-10-01')]  # time period used to get satellite imagery
        self.__bands = ['B8', 'B4', 'B3', 'B2', 'B11']  # band used to calculate superpixels in SNIC
        # B8 and B4 bands need to be passed as NDVI is calculated using them
        self.__thresholds = [0.06,
                             0.1]  # low and high threshold used for canny detection algorithm [low_band, high_band]
        self.__sigma = 3  # sigma value used for image smoothing during edge detection
        self.__distance = 5  # max distance between edges to be connected
        self.__scale = 20  # scale that is used to show results on GEE Map
        self.__points = points
        self.__map_center = map_center
        self.__cloud_filter_threshold = 5
        self.__image = None

    # function used to mask clouds on Sentinel-2 images comes from: https://developers.google.com/earth-engine/datasets/catalog/COPERNICUS_S2_SR_HARMONIZED#colab-python
    def __mask_s2_clouds(self, image: ee.Image) -> ee.Image:
        """Masks clouds in a Sentinel-2 image using the QA band.

        Args:
            image (ee.Image): A Sentinel-2 image.

        Returns:
            ee.Image: A cloud-masked Sentinel-2 image.
        """
        qa = image.select('QA60')

        # Bits 10 and 11 are clouds and cirrus, respectively.
        cloud_bit_mask = 1 << 10
        cirrus_bit_mask = 1 << 11

        # Both flags should be set to zero, indicating clear conditions.
        mask = (
            qa.bitwiseAnd(cloud_bit_mask)
            .eq(0)
            .And(qa.bitwiseAnd(cirrus_bit_mask).eq(0))
        )

        return image.updateMask(mask).divide(10000)

    def __get_map(self, time_period: tuple[str]) -> ee.Image:
        """ Returns map image of selected bands for a GEE Map """
        return (ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
                .filterDate(time_period[0], time_period[1])
                .filterBounds(self.__map_center.get_gee_point())
                .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', self.__cloud_filter_threshold))
                .map(self.__mask_s2_clouds)
                .select(self.__bands)
                .mean())

    def __get_RGB_map(self, time_period: tuple[str]) -> ee.Image:
        """ Returns RGB image of map for presenting results """
        return (ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
                .filterDate(time_period[0], time_period[1])
                .filterBounds(self.__map_center.get_gee_point())
                .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', self.__cloud_filter_threshold))
                .map(self.__mask_s2_clouds)
                .select(['B2', 'B3', 'B4'])
                .first()
                )

    def __get_NDVI(self, map: ee.Image) -> ee.Image:
        """ Function that calculates NDVI """
        return map.normalizedDifference(['B8', 'B4']).rename('NDVI')

    def __segmentate_map(self, map: ee.Image) -> ee.Image:
        """ Function that segmentates map using SNIC algorithm """
        return ee.Algorithms.Image.Segmentation.SNIC(
            image=map,
            size=15,
            compactness=0.5
        )

    def __detect_edges(self, map: ee.Image) -> ee.Image:
        """ Detects edges on each of the bands from segmentation """
        low_threshold_detection = (
            ee.Algorithms.CannyEdgeDetector(
                image=map, threshold=self.__thresholds[0], sigma=self.__sigma
            )
        ).gt(0)
        high_threshold_detection = (
            ee.Algorithms.CannyEdgeDetector(
                image=map, threshold=self.__thresholds[1], sigma=self.__sigma
            )
        ).gt(0)
        hysteresis_threshold = low_threshold_detection.And(
            high_threshold_detection.focal_max(self.__distance, 'square', 'pixels'))

        return high_threshold_detection.Or(hysteresis_threshold)

    def __run_detection(self) -> ee.Image:
        """ Function that runs edge detection algorithm """
        self.__image = ee.Image.constant(0).updateMask(ee.Image(0))
        for time_period in self.__time_periods:
            result_image = self.__get_map(time_period)
            result_image = result_image.addBands(self.__get_NDVI(result_image))
            segmentated_image = self.__segmentate_map(result_image)
            result_image = result_image.addBands(self.__detect_edges(segmentated_image.select("NDVI_mean")))
            self.__image = self.__image.addBands(result_image)

        mean_band_image = self.__image.select([name for name in self.__image.bandNames().getInfo() if '_mean' in name])

        merged_band = (ee.ImageCollection(mean_band_image).toBands()).reduce(ee.Reducer.max())
        # merged_band = merged_band.selfMask().unmask(0).focalMax(10)  # applying dilation to make edges thicker
        merged_band = merged_band.focalMax(25, units="meters").focalMin(25, units="meters")  # applying opening to connect edges
        self.__image = self.__image.addBands(merged_band.rename("merged_band"))

    def __prepare_result_map(self, result_image: ee.Image) -> geemap.Map:
        """ Prepares result map that is ready to show to user """
        resultMap = geemap.Map()
        center_coords = self.__map_center.get_coordinates_degrees()
        resultMap.set_center(center_coords[0], center_coords[1], self.__scale)
        band_names = self.__image.bandNames().getInfo()
        visualization_RGB = {
            'min': 0.0,
            'max': 0.3,
            'bands': ['B4', 'B3', 'B2'],
        }
        resultMap.addLayer(self.__get_RGB_map(self.__time_periods[0]), visualization_RGB, 'RGB')
        for band in band_names:
            if '_mean' in band:
                resultMap.addLayer(self.__image.select(band).selfMask(), {"palette": ["ffffff"]}, band)
        resultMap.addLayer(self.__points, {'color': 'red'}, 'User input points')
        resultMap.addLayer(self.__image.select('merged_band').selfMask(), {"palette": ["ffffff"]}, 'Merged band')
        return resultMap

    def detect_and_show_on_map(self) -> geemap.Map:
        """ You can use this function to show results on GEE Map """
        self.__run_detection()

        return self.__prepare_result_map(self.__image)

    def detect_and_return_merged_bands(self) -> geemap.Map:
        """ Returns GEE Map that containes merged bands for all periods into one image """
        self.__run_detection()

        # Merging all the detected edges into one band
        return self.__image.select('merged_band')