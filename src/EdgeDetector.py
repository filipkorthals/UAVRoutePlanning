import ee
import geemap
from PointData import PointData

"""Class detecting edges in images using different bands from Sentinel2"""


class EdgeDetector:
    def __init__(self, points: ee.FeatureCollection, map_center: PointData):
        self.__time_periods = [['2017-06-01', '2017-09-01'], ['2018-06-01', '2018-09-01'], ['2019-06-01', '2019-09-01'],
                               ['2020-06-01', '2020-09-01'], ['2021-06-01', '2021-09-01'], ['2022-06-01', '2022-09-01'],
                               ['2023-06-01', '2023-09-01'], ['2024-06-01',
                                                              '2024-09-01']]  # more time periods can provide more
        # accurate data, but also makes calculations slower
        self.__bands = ['B4', 'B3', 'B2']  # bands of satellite imagery that are used for edge detection
        self.__thresholds = [110 if i % 2 == 0 else 120 for i in range(
            6)]  # low and high threshold that is used for each band [low_band1, high_band1, ... ]
        self.__sigmas = [5, 11, 4]  # values of sigma that are used for each of the bands
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
                .mean())

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
        visualization = {
            'min': 0.0,
            'max': 0.3,
            'bands': self.__bands,
        }
        resultMap.addLayer(self.__get_RGB_map(), visualization, "Source map")
        for i in range(len(results_list)):
            resultMap.addLayer(results_list[i].updateMask(results_list[i]), {"palette": ["ffffff"]},
                               self.__time_periods[i][0] + " - " + self.__time_periods[i][1])
        resultMap.addLayer(self.__points, {'color': 'red'}, 'User input points')
        return resultMap

    def __detect_edges(self) -> list[ee.Image]:
        """ Detects edged using Canny detector for selected periods """
        aggregated_canny_results = []
        for time_period in self.__time_periods:
            bands_data = []
            for band in self.__bands:
                bands_data.append(self.__get_band_image(band, time_period))
            aggregated_canny_results.append(self.__run_canny_for_bands(bands_data))
        return aggregated_canny_results

    def detect_and_show_on_map(self) -> geemap.Map:
        """ You can use this function to show results on GEE Map """
        aggregated_canny_results = self.__detect_edges()

        return self.__prepare_result_map(aggregated_canny_results)

    def detect_and_return_merged_bands(self) -> geemap.Map:
        """ Returns GEE Map that containes merged bands for all periods into one image """
        aggregated_canny_results = self.__detect_edges()

        # Merging all the detected edges into one band
        results = ee.ImageCollection(aggregated_canny_results).toBands()
        return results.reduce(ee.Reducer.max())
