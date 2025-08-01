from django.shortcuts import render
import csv
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import os
from django.conf import settings

version = 1.16  # versioning for js and css

def index(request):

    return render(request, 'index.html', {'version':version})


@require_http_methods(["GET"])
def traffic_segments_api(request):
    """
    API endpoint to return traffic segment data as GeoJSON
    """
    debug_info = {
        'file_exists': False,
        'total_rows': 0,
        'processed_rows': 0,
        'skipped_rows': 0,
        'error_count': 0,
        'first_few_errors': [],
        'sample_rows': [],
        'column_names': None
    }
    try:
        # Path to your CSV file
        csv_path = os.path.join(settings.BASE_DIR,
                                'web_app\data\Chicago_Traffic_Tracker_-_Congestion_Estimates_by_Segments.csv')

        # Check if file exists
        debug_info['file_exists'] = os.path.exists(csv_path)
        if not debug_info['file_exists']:
            return JsonResponse({
                'error': 'CSV file not found',
                'debug_info': debug_info,
                'checked_path': csv_path
            }, status=404)

        features = []

        with open(csv_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            debug_info['column_names'] = reader.fieldnames

            # Get total row count first
            total_rows = sum(1 for row in csv.reader(open(csv_path, 'r', encoding='utf-8'))) - 1  # subtract header
            debug_info['total_rows'] = total_rows

            # Reset file pointer and skip header
            file.seek(0)
            next(file)

            for row_num, row in enumerate(reader, 1):
                # Store sample rows for debugging
                if row_num <= 3:
                    debug_info['sample_rows'].append(dict(row))

                try:
                    # Try to extract coordinates - adjust column names to match your CSV
                    # If you're unsure of column names, print row.keys() here
                    all_columns = list(row.keys())

                    # Look for column names containing latitude/longitude keywords
                    start_lat_col = next(
                        (col for col in all_columns if 'start' in col.lower() and 'lat' in col.lower()), None)
                    start_lon_col = next((col for col in all_columns if
                                          'start' in col.lower() and ('lon' in col.lower() or 'lng' in col.lower())),
                                         None)
                    end_lat_col = next((col for col in all_columns if 'end' in col.lower() and 'lat' in col.lower()),
                                       None)
                    end_lon_col = next((col for col in all_columns if
                                        'end' in col.lower() and ('lon' in col.lower() or 'lng' in col.lower())), None)
                    speed_col = next((col for col in all_columns if 'speed' in col.lower() or 'current' in col.lower()),
                                     None)

                    if not all([start_lat_col, start_lon_col, end_lat_col, end_lon_col]):
                        if len(debug_info['first_few_errors']) < 5:
                            debug_info['first_few_errors'].append(
                                f"Couldn't find required coordinate columns in row {row_num}")
                        debug_info['error_count'] += 1
                        debug_info['skipped_rows'] += 1
                        continue

                    start_lat = float(row[start_lat_col])
                    start_lon = float(row[start_lon_col])
                    end_lat = float(row[end_lat_col])
                    end_lon = float(row[end_lon_col])

                    # Get speed if available
                    current_speed = None
                    if speed_col:
                        speed_val = row[speed_col]
                        if speed_val and speed_val != '-1':
                            try:
                                current_speed = int(speed_val)
                            except (ValueError, TypeError):
                                current_speed = None

                    # Create feature with all available properties
                    properties = {'row_number': row_num}
                    for key, value in row.items():
                        properties[key.lower().replace(' ', '_')] = value

                    feature = {
                        "type": "Feature",
                        "geometry": {
                            "type": "LineString",
                            "coordinates": [[start_lon, start_lat], [end_lon, end_lat]]
                        },
                        "properties": properties
                    }

                    features.append(feature)
                    debug_info['processed_rows'] += 1

                except Exception as e:
                    if len(debug_info['first_few_errors']) < 5:
                        debug_info['first_few_errors'].append(f"Row {row_num}: {str(e)}")
                    debug_info['error_count'] += 1
                    debug_info['skipped_rows'] += 1

        geojson = {
            "type": "FeatureCollection",
            "features": features
        }

        # If no features were created but we had rows, return debug info
        if not features and debug_info['total_rows'] > 0:
            return JsonResponse({
                'type': 'FeatureCollection',
                'features': [],
                'debug_info': debug_info,
                'message': 'No valid features could be created from the data'
            })

        return JsonResponse(geojson)

    except Exception as e:
        debug_info['error'] = str(e)
        return JsonResponse({
            'error': str(e),
            'debug_info': debug_info
        }, status=500)
