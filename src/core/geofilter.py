from core.abstracts.pipeline import StreamFilter
import fiona
from shapely.geometry import shape, Point
import json
import os

class GeoFilter(StreamFilter):

    def __init__(self, input_stream):
        self.input_stream = input_stream
        super().__init__(input_stream)
        os.environ['SHAPE_RESTORE_SHX'] = 'YES'

    async def filter(self):
        # Correct the path to point to the shapefile location
        shape_file_path = os.path.join(os.path.dirname(__file__), '../data/shapes/bg_airspace_polygon.shp')

        if not os.path.exists(shape_file_path):
            raise FileNotFoundError(f"Shapefile not found: {shape_file_path}")

        try:
            # Open the shapefile
            with fiona.open(shape_file_path) as fiona_collection:
                async for item in self.input_stream:

                    item_decode = json.loads(item)
                    lat = item_decode.get('lat')
                    lon = item_decode.get('lon')

                    if lat is not None and lon is not None:
                        point = Point(lon, lat)  # longitude, latitude

                        shapefile_record = next(iter(fiona_collection))

                        # Convert the record's geometry to a Shapely shape
                        geom_shape = shape(shapefile_record['geometry'])
                        if geom_shape.contains(point):
                            # If the point is within the feature's geometry, yield the item
                            yield item
        except fiona.errors.DriverError as e:
            print(f"Fiona failed to open the shapefile: {e}")
