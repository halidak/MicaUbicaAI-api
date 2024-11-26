from django.urls import path
from .views import your_view_function
from .views import reset_game
from .compViews import compVScomp, reset_gameComp


urlpatterns = [
    path('stones', your_view_function, name='your_view_function'),
    path('comp', compVScomp, name="compVscomp"),
    path('resetC', reset_gameComp, name='reset_gameC'),
    path('reset', reset_game, name='reset_game')
]
