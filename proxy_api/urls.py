from django.urls import path
from proxy_api.views import home, api
urlpatterns = [
    path("api/", api),
    path('', home),
]
