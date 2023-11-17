from django.urls import path
from .views import your_view_function
from .views import reset_game


urlpatterns = [
    path('stones', your_view_function, name='your_view_function'),
    path('reset', reset_game, name='reset_game'),
]