import pytest
import asyncio
import json
import pytest_asyncio
from src.core.geofilter import GeoFilter

# New async method to generate coordinates
async def random_coordinate():
    coordinates = [
        (23.8, 90.2),  # Example point inside the polygon
        (25.845, 94.279),  # Example point outside the polygon
        (23.9, 90.3),  # Another point inside the polygon
        (27.367, 92.417)  # Another point outside the polygon
    ]

    for lat, lon in coordinates:
        yield json.dumps({"lat": lat, "lon": lon})
        await asyncio.sleep(0.1)  # Simulate delay between data points

@pytest.mark.asyncio
async def test_is_inside():
    # Use the new async coordinate generator
    input_stream = random_coordinate()

    geo_filter = GeoFilter(input_stream)
    result = [item async for item in geo_filter.filter()]
    assert len(result) == 2

