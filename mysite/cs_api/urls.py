from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='home'),

    # cs api
    path('api', views.api, name='API'),
    path('api_history', views.api_history, name='API History'),
    path('api_history/<int:offset>', views.api_history, name='API History'),
    path('api_history/<int:offset>/<int:limit>', views.api_history, name='API History'),

    path('fetch_category_list_view', views.fetch_category_list_view, name='fetch_category_list_view'),
    path('get_category_map', views.get_category_map, name='get_category_map'),
    path('receive_api_request', views.receive_api_request, name='receive_api_request'),

    # cs user
    path('cs_user', views.cs_user, name='cs_user'),
    path('cs_user_add', views.cs_user_add, name='cs_user_add'),
    path('cs_user_delete/<int:cs_user_id>', views.cs_user_delete, name='cs_user_delete'),

    # cs event
    path('cs_event_history', views.cs_event_history, name='Event History'),
    path('cs_event_server', views.cs_event_server, name='cs_event_server'),
    path('cs_event_server_add', views.cs_event_server_add, name='cs_event_server_add'),
    path('cs_event_server_delete/<int:cs_event_server_id>', views.cs_event_server_delete, name='cs_event_server_delete'),

    # event triggers
    path('cs_event_trigger_list', views.cs_event_trigger_list, name='Event Trigger List'),
    path('cs_event_trigger_add', views.cs_event_trigger_add, name='Event Trigger Add'),
    path('cs_event_trigger_add/<int:event_trigger_id>', views.cs_event_trigger_add, name='Event Trigger Update'),
    path('cs_event_trigger_delete/<int:cs_event_trigger_id>', views.cs_event_trigger_delete, name='Event Trigger Delete'),
    path('get_data_for_trigger', views.get_data_for_trigger, name='get_data_for_trigger'),
    path('get_data_for_trigger/<int:cs_event_trigger_id>', views.get_data_for_trigger, name='get_data_for_trigger'),
    path('trigger_create', views.trigger_create, name='trigger_create'),

    # user
    path('signup', views.signup_view, name='Sign up'),
    path('login', views.login_view, name='Login'),
    path('logout', views.logout_view, name='Logout'),
]
