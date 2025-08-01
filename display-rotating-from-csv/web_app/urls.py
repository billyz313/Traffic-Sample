from django.urls import path

from web_app import views

urlpatterns = [
    path('', views.index, name='index'),
    path('api/traffic-segments/', views.traffic_segments_api, name='traffic_segments_api'),
]
