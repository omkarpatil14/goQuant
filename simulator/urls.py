from django.urls import path
from .views import calculate_metrics

urlpatterns = [
    path('calculate/', calculate_metrics),
]
