from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('api', views.api, name='API'),
    path('signup', views.signup_view, name='Sign up'),
    path('login', views.login_view, name='Login'),
    path('logout', views.logout_view, name='Logout'),
    path('fetch_category_list_view', views.fetch_category_list_view, name='fetch_category_list_view'),
    path('get_category_map', views.get_category_map, name='get_category_map'),
    path('receive_api_request', views.receive_api_request, name='receive_api_request'),
]
