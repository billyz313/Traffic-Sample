from django.db import models
from django.contrib.gis.db import models as gis_models  # Optional, for GeoDjango if you set it up


class TrafficSegmentData(models.Model):
    # Data from your CSV file
    segment_id = models.IntegerField(db_index=True)  # Index for faster lookup
    street = models.CharField(max_length=255)
    direction = models.CharField(max_length=10)
    from_street = models.CharField(max_length=255)
    to_street = models.CharField(max_length=255)
    length = models.FloatField()
    street_heading = models.CharField(max_length=100, blank=True, null=True)  # Some fields might be optional
    comments = models.TextField(blank=True, null=True)

    # Coordinates - standard way if not using GeoDjango
    start_longitude = models.FloatField()
    start_latitude = models.FloatField()
    end_longitude = models.FloatField()
    end_latitude = models.FloatField()

    current_speed = models.IntegerField(default=-1)  # Use -1 or null=True, blank=True if speed can be missing

    # Crucial field for storing the timestamp of the data point
    # Use DateTimeField to store date and time
    # This will be derived from your 'LAST_UPDATED' and potentially the date in the filename
    recorded_at = models.DateTimeField(db_index=True)  # Index for faster time-based queries

    # Optional: GeoDjango LineString field for spatial queries if you configure PostGIS
    # geometry = gis_models.LineStringField(srid=4326, blank=True, null=True)

    class Meta:
        verbose_name = "Traffic Segment Data"
        verbose_name_plural = "Traffic Segment Data"
        # If segment_id + recorded_at is unique, you can add a unique_together constraint
        # unique_together = (('segment_id', 'recorded_at'),)

    def __str__(self):
        return f"Segment {self.segment_id} on {self.street} ({self.recorded_at.strftime('%Y-%m-%d %H:%M')})"