from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),  # Home page
    path('calculate/', views.calculate_rank, name='calculate_rank'),  # POST handler
]
