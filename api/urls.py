from django.urls import path
from .views import your_view_function

urlpatterns = [
    path('stones', your_view_function, name='your_view_function'),
]