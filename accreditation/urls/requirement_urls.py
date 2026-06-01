from django.urls import path
from .. import views

urlpatterns = [
    path('requirements/', views.requirement_list, name='requirement_list'),
    path('requirements/create/', views.requirement_create, name='requirement_create'),
    path('requirements/<int:requirement_id>/', views.requirement_detail, name='requirement_detail'),
    path('requirements/<int:requirement_id>/update/', views.requirement_update, name='requirement_update'),
    path('requirements/<int:requirement_id>/delete/', views.requirement_delete, name='requirement_delete'),

    path('requirements/<int:requirement_id>/indicators/create/', views.indicator_create, name='indicator_create'),
    path('indicators/<int:indicator_id>/update/', views.indicator_update, name='indicator_update'),
    path('indicators/<int:indicator_id>/delete/', views.indicator_delete, name='indicator_delete'),
]