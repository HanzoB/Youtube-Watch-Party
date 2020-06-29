

from django.urls import path, include
from . import views
from django.utils.crypto import get_random_string

app_name = "main"

urlpatterns = [

    path("", views.index, name="index"),
]



