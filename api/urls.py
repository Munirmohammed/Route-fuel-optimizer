from django.urls import path
from .views import RouteOptimizerView

urlpatterns = [
    path('route-optimizer/', RouteOptimizerView.as_view(), name='route-optimizer'),
]
