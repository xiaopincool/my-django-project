from django.urls import path
from .. import views

urlpatterns = [
    path('attainments/', views.attainment_list, name='attainment_list'),
    path('attainments/new/', views.attainment_entry, name='attainment_entry'),
    path('courses/<int:course_id>/attainments/create/', views.attainment_create, name='attainment_create'),
    path('attainments/<int:record_id>/', views.attainment_detail, name='attainment_detail'),
    path('attainments/<int:record_id>/update/', views.attainment_update, name='attainment_update'),
    path('attainments/<int:record_id>/delete/', views.attainment_delete, name='attainment_delete'),
]