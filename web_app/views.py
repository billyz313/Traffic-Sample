import os
import csv
from datetime import datetime, time, date, timedelta
from django.http import JsonResponse
from django.conf import settings
from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from web_app.models import TrafficSegmentData # Import your new model
from django.db.models import Min, Max # For finding min/max dates

version = 1.16  # versioning for js and css

def index(request):

    return render(request, 'index.html', {'version':version})


@require_http_methods(["GET"])
def traffic_segments_api(request):
    """
    API endpoint to return traffic segment data as GeoJSON from the database.

    Query Parameters:
    - datetime (optional): An ISO-formatted datetime string (e.g., "2025-07-31T12:31:00")
                          to request data for a specific timestamp.
                          If not provided, the oldest available data is returned.

    Returns:
    - GeoJSON FeatureCollection of traffic segments.
    - Metadata including current_timestamp, next_timestamp, oldest_timestamp, latest_timestamp.
    """
    debug_info = {
        'query_filters': {},
        'returned_features': 0,
        'current_data_timestamp': None,
        'next_data_timestamp_calculated': None,
        'oldest_data_timestamp': None,
        'latest_data_timestamp': None,
        'error_messages': []
    }

    # --- 1. Get overall oldest and latest timestamps from the database ---
    min_max_dates = TrafficSegmentData.objects.aggregate(min_date=Min('recorded_at'), max_date=Max('recorded_at'))

    oldest_data_datetime = min_max_dates['min_date']
    latest_data_datetime = min_max_dates['max_date']

    if not oldest_data_datetime:
        debug_info['error_messages'].append("No traffic data found in the database.")
        return JsonResponse({'error': 'No traffic data available', 'debug': debug_info}, status=404)

    debug_info['oldest_data_timestamp'] = oldest_data_datetime.isoformat()
    debug_info['latest_data_timestamp'] = latest_data_datetime.isoformat()

    # --- 2. Determine the target datetime for the current request ---
    target_datetime = None

    datetime_param = request.GET.get('datetime', None)

    if datetime_param:
        try:
            # Parse the ISO-formatted datetime string from the request
            # fromisoformat handles various ISO formats, including with/without Z or timezone offsets
            target_datetime = datetime.fromisoformat(datetime_param)
            # Ensure timezone awareness if your DB is timezone-aware
            # if settings.USE_TZ:
            #     from django.utils import timezone
            #     target_datetime = timezone.make_aware(target_datetime)
            debug_info['query_filters']['requested_datetime_param'] = datetime_param
        except ValueError as e:
            debug_info['error_messages'].append(
                f"Invalid 'datetime' format: '{datetime_param}'. Error: {e}. Returning oldest data.")
            # Fallback to oldest data if parsing fails
            target_datetime = oldest_data_datetime
    else:
        # If no specific datetime is sent, default to the oldest data available
        debug_info['error_messages'].append("No 'datetime' parameter provided. Returning oldest data.")
        target_datetime = oldest_data_datetime

    # Ensure target_datetime exists in the database. If not, use the closest available.
    # We want to find the closest *existing* recorded_at timestamp in the database
    # that is less than or equal to the requested target_datetime.
    # This ensures we always return data for an actual timestamp we have.

    # Query for exact match or the nearest earlier timestamp
    closest_data_query = TrafficSegmentData.objects.filter(recorded_at__lte=target_datetime).order_by(
        '-recorded_at').first()

    if closest_data_query:
        # Use the actual timestamp found in the DB
        actual_data_timestamp = closest_data_query.recorded_at
    else:
        # If no data is found <= requested, it means the request was for something older than our oldest.
        # So, just use the absolute oldest data.
        actual_data_timestamp = oldest_data_datetime
        debug_info['error_messages'].append("Requested datetime was before earliest data. Using absolute oldest data.")

    debug_info['current_data_timestamp'] = actual_data_timestamp.isoformat()

    # --- 3. Fetch data for the determined actual_data_timestamp ---
    # Filter for all segments recorded at this exact timestamp
    current_data_segments = TrafficSegmentData.objects.filter(recorded_at=actual_data_timestamp).order_by('segment_id')

    features = []
    for segment_data in current_data_segments:
        feature = {
            "type": "Feature",
            "properties": {
                "segment_id": segment_data.segment_id,
                "street": segment_data.street,
                "direction": segment_data.direction,
                "from_street": segment_data.from_street,
                "to_street": segment_data.to_street,
                "length": segment_data.length,
                "street_heading": segment_data.street_heading,
                "comments": segment_data.comments,
                "_current_speed": segment_data.current_speed,
                "_last_updated": segment_data.recorded_at.isoformat()  # ISO format for consistency
            },
            "geometry": {
                "type": "LineString",
                "coordinates": [
                    [segment_data.start_longitude, segment_data.start_latitude],
                    [segment_data.end_longitude, segment_data.end_latitude]
                ]
            }
        }
        features.append(feature)

    debug_info['returned_features'] = len(features)

    # --- 4. Determine the next available timestamp ---
    next_data_datetime = None

    # Find the first timestamp strictly greater than the current actual_data_timestamp
    next_query = TrafficSegmentData.objects.filter(recorded_at__gt=actual_data_timestamp).order_by(
        'recorded_at').first()

    if next_query:
        next_data_datetime = next_query.recorded_at
    else:
        # If no next timestamp exists, loop back to the oldest data
        next_data_datetime = oldest_data_datetime
        debug_info['error_messages'].append("No data after current timestamp found. Looping back to oldest.")

    debug_info['next_data_timestamp_calculated'] = next_data_datetime.isoformat() if next_data_datetime else None

    geojson_data = {
        "type": "FeatureCollection",
        "features": features,
        "metadata": {  # Include metadata for frontend to manage state
            "current_timestamp": actual_data_timestamp.isoformat(),
            "next_timestamp": next_data_datetime.isoformat(),  # This will be used by the frontend for the next request
            "oldest_timestamp": oldest_data_datetime.isoformat(),
            "latest_timestamp": latest_data_datetime.isoformat(),
        },
        "debug": debug_info  # Include debug info in response for development
    }

    return JsonResponse(geojson_data)
