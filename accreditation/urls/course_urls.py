from django.urls import path
from .. import views

urlpatterns = [
    path('courses/', views.course_list, name='course_list'),
    path('courses/create/', views.course_create, name='course_create'),
    path('courses/<int:course_id>/', views.course_detail, name='course_detail'),
    path('courses/<int:course_id>/update/', views.course_update, name='course_update'),
    path('courses/<int:course_id>/delete/', views.course_delete, name='course_delete'),

    path('relations/', views.relation_list, name='relation_list'),
    path('relations/new/', views.relation_entry, name='relation_entry'),
    path('courses/<int:course_id>/relations/create/', views.relation_create, name='relation_create'),
    path('relations/<int:relation_id>/', views.relation_detail, name='relation_detail'),
    path('relations/<int:relation_id>/update/', views.relation_update, name='relation_update'),
    path('relations/<int:relation_id>/delete/', views.relation_delete, name='relation_delete'),
]
