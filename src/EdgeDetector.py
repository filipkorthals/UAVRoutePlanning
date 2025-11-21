import ee
import geemap
from PointData import PointData

"""Class detecting edges in images using different bands from Sentinel2"""


class EdgeDetector:
    def __init__(self, points: ee.FeatureCollection, map_center: PointData):
        self.__time_periods = [['2023-05-01', '2023-10-01'], ['2024-05-01', '2024-10-01'],
                               ['2025-05-01', '2025-10-01']]  # more time periods can provide more
        # accurate data, but also makes calculations slower
        self.__bands = ['B11']  # bands of satellite imagery that are used for edge detection
        self.__thresholds = [200, 210, 0.06,
                             0.1]  # low and high threshold that is used for each band [low_band1, high_band1, ... ]
        self.__sigmas = [7.5, 5]  # values of sigma that are used for each of the bands
        self.__distance = 5  # max distance between edges to be connected
        self.__scale = 16  # scale that is used to show results on GEE Map
        self.__points = points
        self.__map_center = map_center
        self.__cloud_filter_threshold = 5

    # Finding selected band in a selected place
    def __get_band_image(self, band: str, time_period: list) -> ee.Image:
        """ Function that finds particular band for selected image """
        return (ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
                .filterDate(time_period[0], time_period[1])
                .filterBounds(self.__map_center.get_gee_point())
                .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', self.__cloud_filter_threshold))
                .select(band)
                .mean())

    # Clouds masking is used only for comparison and visualization
    # TODO: change this function
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

    def __get_RGB_map(self) -> ee.Image:
        """ Function that returns map image for a GEE Map """
        return (ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
                .filterDate(self.__time_periods[0][0], self.__time_periods[-1][0])
                .filterBounds(self.__map_center.get_gee_point())
                # Pre-filter to get less cloudy granules.
                .filter(
            ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', self.__cloud_filter_threshold)
        )
                .map(self.__mask_s2_clouds)
                .first())

    def __get_NDVI(self, time_period: list) -> ee.Image:
        """ Function that calculates NDVI """
        bands = (ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
                 .filterDate(time_period[0], time_period[1])
                 .filterBounds(self.__map_center.get_gee_point())
                 .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', self.__cloud_filter_threshold))
                 .select(['B8', 'B4'])
                 .mean())
        return bands.normalizedDifference(['B8', 'B4']).rename('NDVI')

    def __run_canny_for_bands(self, bands_data: list) -> ee.Image:
        """ Function runs Canny edge detection algorithm for every provided band """
        bands_after_canny = []
        for i in range(len(bands_data)):
            low_threshold_detection = (
                ee.Algorithms.CannyEdgeDetector(
                    image=bands_data[i], threshold=self.__thresholds[i], sigma=self.__sigmas[i]
                )
            ).gt(0)
            high_threshold_detection = (
                ee.Algorithms.CannyEdgeDetector(
                    image=bands_data[i], threshold=self.__thresholds[i + 1], sigma=self.__sigmas[i]
                )
            ).gt(0)
            hysteresis_threshold = low_threshold_detection.And(
                high_threshold_detection.focal_max(self.__distance, 'square', 'pixels'))
            bands_after_canny.append(high_threshold_detection.Or(hysteresis_threshold))

        if len(bands_after_canny) > 1:
            aggregated_canny = bands_after_canny[0].Or(bands_after_canny[1])
            for i in range(2, len(bands_after_canny)):
                aggregated_canny = aggregated_canny.Or(bands_after_canny[i])
            return aggregated_canny.select([aggregated_canny.bandNames().get(0)])
        return bands_after_canny[0]

    def __prepare_result_map(self, results_list: ee.Image) -> geemap.Map:
        """ Prepares result map that is ready to show to user """
        resultMap = geemap.Map()
        center_coords = self.__map_center.get_coordinates_degrees()
        resultMap.set_center(center_coords[0], center_coords[1], self.__scale)
        visualization_RGB = {
            'min': 0.0,
            'max': 0.3,
            'bands': ['B4', 'B3', 'B2'],
        }
        visualization_NDVI = {
            'min': -1,
            'max': 1,
            'palette': [
                'blue',
                'white',
                'green'
            ],
        }
        resultMap.addLayer(self.__get_RGB_map(), visualization_RGB, "Source map")
        resultMap.addLayer(
            self.__get_NDVI([self.__time_periods[0][0], self.__time_periods[-1][0]]),
            visualization_NDVI,
            "NDVI"
        )
        for i in range(len(results_list)):
            resultMap.addLayer(results_list[i].selfMask(), {"palette": ["ffffff"]},
                               self.__time_periods[i][0] + " - " + self.__time_periods[i][1])
        resultMap.addLayer(self.__points, {'color': 'red'}, 'User input points')
        results = ee.ImageCollection(results_list).toBands().reduce(ee.Reducer.max())
        resultMap.addLayer(self.__apply_morphology(results).selfMask(), {'palette': ['ffffff']}, "Total result")
        return resultMap

    def __detect_edges(self) -> list[ee.Image]:
        """ Detects edged using Canny detector for selected periods """
        aggregated_canny_results = []
        for time_period in self.__time_periods:
            bands_data = []
            for band in self.__bands:
                bands_data.append(self.__get_band_image(band, time_period))
            bands_data.append(self.__get_NDVI(time_period))
            aggregated_canny_results.append(self.__run_canny_for_bands(bands_data))
        return aggregated_canny_results

    def __apply_morphology(self, image: ee.Image) -> ee.Image:
        """ Function that is used to apply morphological opening and closing on prepared result image """
        image = image.selfMask().unmask(0).focalMax(1)  # applying dilation to make edges thicker
        image = image.focalMin(1).focalMax(1)  # morphological opening
        image = image.focalMax(4).focalMin(4)  # morphological closing, radius is bigger to close bigger gaps
        return image.focalMin(1).selfMask()

    def detect_and_show_on_map(self) -> geemap.Map:
        """ You can use this function to show results on GEE Map """
        aggregated_canny_results = self.__detect_edges()

        return self.__prepare_result_map(aggregated_canny_results)

    def detect_and_return_merged_bands(self) -> geemap.Map:
        """ Returns GEE Map that containes merged bands for all periods into one image """
        aggregated_canny_results = self.__detect_edges()

        # Merging all the detected edges into one band
        results = ee.ImageCollection(aggregated_canny_results).toBands()
        return self.__apply_morphology(results.reduce(ee.Reducer.max()))
