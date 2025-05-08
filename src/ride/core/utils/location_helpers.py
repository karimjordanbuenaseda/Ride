import math
from django.db.models import F, Func, ExpressionWrapper, FloatField


def calculate_distance_annotation(latitude, longitude):
    """
    
    Uses the Haversine formula for distance calculation directly in the database,
    which makes sorting by distance much more efficient than fetching all records
    and calculating in Python.
    """
    # Convert degrees to radians
    lat_rad = math.radians(float(latitude))
    lon_rad = math.radians(float(longitude))
    
    # Create an expression to calculate the distance using the Haversine formula
    # directly in the database
    R = 6371  # Earth radius in kilometers
    
    return ExpressionWrapper(
        # Haversine formula: 2 * R * asin(sqrt(sin²((lat2-lat1)/2) + cos(lat1) * cos(lat2) * sin²((lon2-lon1)/2)))
        2 * R * Func(
            Func(
                # sin²((lat2-lat1)/2)
                Func(
                    (Func(F('pickup_latitude'), function='RADIANS') - lat_rad) / 2,
                    function='SIN'
                ) ** 2 +
                # cos(lat1) * cos(lat2) * sin²((lon2-lon1)/2)
                Func(lat_rad, function='COS') *
                Func(Func(F('pickup_latitude'), function='RADIANS'), function='COS') *
                Func(
                    (Func(F('pickup_longitude'), function='RADIANS') - lon_rad) / 2,
                    function='SIN'
                ) ** 2,
                function='SQRT'
            ),
            function='ASIN'
        ),
        output_field=FloatField()
    )