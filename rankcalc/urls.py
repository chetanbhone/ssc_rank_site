from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),  # Home page
    path('calculate/', views.calculate_rank, name='calculate_rank'),  # POST handler
    path('results/', views.all_results, name='all_results'),
    path('export/', views.export_candidates_csv, name='export_csv'),


]

