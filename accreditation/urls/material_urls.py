from django.urls import path
from .. import views

urlpatterns = [
    path('materials/', views.material_list, name='material_list'),
    path('materials/upload/', views.material_upload, name='material_upload'),
    path('materials/<int:material_id>/', views.material_detail, name='material_detail'),
    path('materials/<int:material_id>/update/', views.material_update, name='material_update'),
    path('materials/<int:material_id>/delete/', views.material_delete, name='material_delete'),
]