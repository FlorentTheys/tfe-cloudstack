from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('get_category_map', views.get_category_map, name='get_category_map'),
    path('receive_api_request', views.receive_api_request, name='receive_api_request'),
]
