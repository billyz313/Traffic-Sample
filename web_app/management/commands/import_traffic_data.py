import os
import csv
from datetime import datetime
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from web_app.models import TrafficSegmentData  # Make sure to replace 'web_app' with your actual app name


class Command(BaseCommand):
    help = 'Imports traffic segment data from dated CSV files into the database.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--data_dir',
            type=str,
            help='Directory containing the CSV files (default: web_app/data)',
            default=os.path.join(settings.BASE_DIR, 'web_app', 'data')
        )
        parser.add_argument(
            '--clear_existing',
            action='store_true',
            help='Clear all existing TrafficSegmentData before importing new data.',
        )

    def handle(self, *args, **options):
        data_dir = options['data_dir']
        clear_existing = options['clear_existing']

        if not os.path.isdir(data_dir):
            raise CommandError(f"Data directory does not exist: {data_dir}")

        if clear_existing:
            self.stdout.write(self.style.WARNING("Clearing all existing TrafficSegmentData..."))
            TrafficSegmentData.objects.all().delete()
            self.stdout.write(self.style.SUCCESS("Existing data cleared."))

        self.stdout.write(f"Starting data import from: {data_dir}")

        total_files = 0
        processed_files = 0
        total_rows = 0
        inserted_rows = 0
        skipped_rows_overall = 0

        # Regex to match the expected filename pattern for easy parsing
        # Matches "Chicago_Traffic_Tracker_-_Congestion_Estimates_by_Segments_"
        # followed by YYYY-MM-DD-HH-MM-SS and then ".csv"
        filename_pattern = r'Chicago_Traffic_Tracker_-_Congestion_Estimates_by_Segments_(\d{4}-\d{2}-\d{2}-\d{2}-\d{2}-\d{2})\.csv'
        import re

        for filename in os.listdir(data_dir):
            match = re.match(filename_pattern, filename)
            if match:
                total_files += 1
                csv_path = os.path.join(data_dir, filename)
                datetime_str = match.group(1)  # Extract the YYYY-MM-DD-HH-MM-SS part
                self.stdout.write(f"Processing {filename}...")

                try:
                    # Parse the datetime string from the filename
                    # Format: YYYY-MM-DD-HH-MM-SS
                    recorded_at = datetime.strptime(datetime_str, '%Y-%m-%d-%H-%M-%S')
                except ValueError as e:
                    self.stderr.write(self.style.ERROR(
                        f"Skipping {filename}: Invalid datetime format in filename '{datetime_str}'. Error: {e}"))
                    skipped_rows_overall += 1  # Count this file's rows as skipped for overall count
                    continue

                rows_in_file = 0
                rows_inserted_from_file = 0
                rows_skipped_in_file = 0

                try:
                    with open(csv_path, mode='r', encoding='utf-8') as file:
                        reader = csv.DictReader(file)

                        # Get a list of expected clean column names to map incoming data
                        # These should match your TrafficSegmentData model fields
                        expected_columns = [
                            'SEGMENTID', 'STREET', 'DIRECTION', 'FROM_STREET', 'TO_STREET',
                            'LENGTH', 'STREET_HEADING', 'COMMENTS', 'START_LONGITUDE',
                            'START_LATITUDE', 'END_LONGITUDE', 'END_LATITUDE', 'CURRENT_SPEED',
                            'LAST_UPDATED'  # Though LAST_UPDATED from CSV is less relevant now as we use recorded_at
                        ]

                        # Mapping for potentially messy CSV headers to clean model fields
                        # This handles cases where CSV headers have leading/trailing spaces
                        header_map = {col.strip().upper(): col for col in reader.fieldnames}

                        for row_num, row_data in enumerate(reader):
                            rows_in_file += 1
                            total_rows += 1
                            try:
                                # Clean data: Strip whitespace from values and map keys
                                cleaned_row = {k.strip(): v.strip() if isinstance(v, str) else v for k, v in
                                               row_data.items()}
                                # If your CSV has headers like " CURRENT_SPEED", this ensures you map it
                                # to "CURRENT_SPEED" for access below.

                                # Basic validation for required fields
                                if not all(cleaned_row.get(col_name.strip(), '') for col_name in
                                           ['SEGMENTID', 'STREET', 'START_LONGITUDE', 'START_LATITUDE', 'END_LONGITUDE',
                                            'END_LATITUDE']):
                                    self.stderr.write(self.style.WARNING(
                                        f"Skipping row {row_num + 1} in {filename}: Missing essential data."))
                                    rows_skipped_in_file += 1
                                    skipped_rows_overall += 1
                                    continue

                                # Create TrafficSegmentData instance
                                TrafficSegmentData.objects.create(
                                    segment_id=int(cleaned_row.get(header_map.get('SEGMENTID'), '-1')),
                                    street=cleaned_row.get(header_map.get('STREET'), ''),
                                    direction=cleaned_row.get(header_map.get('DIRECTION'), ''),
                                    from_street=cleaned_row.get(header_map.get('FROM_STREET'), ''),
                                    to_street=cleaned_row.get(header_map.get('TO_STREET'), ''),
                                    length=float(cleaned_row.get(header_map.get('LENGTH'), 0.0)),
                                    street_heading=cleaned_row.get(header_map.get('STREET_HEADING'), ''),
                                    comments=cleaned_row.get(header_map.get('COMMENTS'), ''),
                                    start_longitude=float(cleaned_row.get(header_map.get('START_LONGITUDE'), 0.0)),
                                    start_latitude=float(cleaned_row.get(header_map.get('START_LATITUDE'), 0.0)),
                                    end_longitude=float(cleaned_row.get(header_map.get('END_LONGITUDE'), 0.0)),
                                    end_latitude=float(cleaned_row.get(header_map.get('END_LATITUDE'), 0.0)),
                                    current_speed=int(float(cleaned_row.get(header_map.get('CURRENT_SPEED'), -1))),
                                    recorded_at=recorded_at  # Use the datetime parsed from the filename
                                )
                                rows_inserted_from_file += 1
                                inserted_rows += 1

                            except ValueError as ve:
                                self.stderr.write(self.style.ERROR(
                                    f"Data type error in row {row_num + 1} of {filename}: {ve} - Row: {row_data}"))
                                rows_skipped_in_file += 1
                                skipped_rows_overall += 1
                            except Exception as e:
                                self.stderr.write(self.style.ERROR(
                                    f"Error inserting row {row_num + 1} from {filename}: {e} - Row: {row_data}"))
                                rows_skipped_in_file += 1
                                skipped_rows_overall += 1
                except Exception as e:
                    self.stderr.write(self.style.ERROR(f"Failed to read or process file {filename}: {e}"))
                    skipped_rows_overall += rows_in_file - rows_inserted_from_file  # Account for rows in partially read files
                    continue

                self.stdout.write(self.style.SUCCESS(
                    f"Finished {filename}: {rows_inserted_from_file}/{rows_in_file} rows inserted, {rows_skipped_in_file} skipped."))
                processed_files += 1
            else:
                self.stdout.write(self.style.WARNING(f"Skipping non-matching file: {filename}"))

        self.stdout.write(self.style.SUCCESS("\n--- Import Summary ---"))
        self.stdout.write(self.style.SUCCESS(f"Total files found matching pattern: {total_files}"))
        self.stdout.write(self.style.SUCCESS(f"Files successfully processed: {processed_files}"))
        self.stdout.write(self.style.SUCCESS(f"Total rows attempted: {total_rows}"))
        self.stdout.write(self.style.SUCCESS(f"Total rows inserted: {inserted_rows}"))
        self.stdout.write(
            self.style.WARNING(f"Total rows skipped (due to errors or missing data): {skipped_rows_overall}"))
        self.stdout.write(self.style.SUCCESS("----------------------"))
        if total_files > processed_files or skipped_rows_overall > 0:
            self.stdout.write(self.style.WARNING("Please review the logs above for skipped files or rows with errors."))