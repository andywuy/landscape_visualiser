from django.urls import path

from . import views

# Add namespace to your URLconf, because app1 and app2 can both have a index view.
# Specify using {% url 'app_name:view_name' %}
app_name = 'app'

urlpatterns = [
    path('', views.index, name='index'),
    path('upload_min_data', views.upload_min_data, name='upload_min_data'),
    path('upload_ts_data', views.upload_ts_data, name='upload_ts_data'),
    path('upload_colour', views.upload_colour, name='upload_colour'),
    path('upload_config', views.upload_config, name='upload_config'),
    path('display', views.display, name='display'),
]
