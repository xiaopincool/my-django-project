from django.urls import path
from . import views

app_name = 'accreditation'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),

    path('requirements/', views.requirement_list, name='requirement_list'),
    path('requirements/create/', views.requirement_create, name='requirement_create'),
    path('requirements/<int:requirement_id>/', views.requirement_detail, name='requirement_detail'),
    path('requirements/<int:requirement_id>/update/', views.requirement_update, name='requirement_update'),
    path('requirements/<int:requirement_id>/delete/', views.requirement_delete, name='requirement_delete'),

    path('requirements/<int:requirement_id>/indicators/create/', views.indicator_create, name='indicator_create'),
    path('indicators/<int:indicator_id>/update/', views.indicator_update, name='indicator_update'),
    path('indicators/<int:indicator_id>/delete/', views.indicator_delete, name='indicator_delete'),

    path('courses/', views.course_list, name='course_list'),
    path('courses/create/', views.course_create, name='course_create'),
    path('courses/<int:course_id>/', views.course_detail, name='course_detail'),
    path('courses/<int:course_id>/update/', views.course_update, name='course_update'),
    path('courses/<int:course_id>/delete/', views.course_delete, name='course_delete'),

    path('goals/', views.goal_list, name='goal_list'),
path('goals/new/', views.goal_entry, name='goal_entry'),
    path('courses/<int:course_id>/goals/create/', views.goal_create, name='goal_create'),
    path('goals/<int:goal_id>/', views.goal_detail, name='goal_detail'),
    path('goals/<int:goal_id>/update/', views.goal_update, name='goal_update'),
    path('goals/<int:goal_id>/delete/', views.goal_delete, name='goal_delete'),

    path('relations/', views.relation_list, name='relation_list'),
path('relations/new/', views.relation_entry, name='relation_entry'),
    path('courses/<int:course_id>/relations/create/', views.relation_create, name='relation_create'),
    path('relations/<int:relation_id>/', views.relation_detail, name='relation_detail'),
    path('relations/<int:relation_id>/update/', views.relation_update, name='relation_update'),
    path('relations/<int:relation_id>/delete/', views.relation_delete, name='relation_delete'),

    path('goals/<int:goal_id>/relations/create/', views.goal_relation_create, name='goal_relation_create'),
    path('goal-relations/', views.goal_relation_list, name='goal_relation_list'),
path('goal-relations/new/', views.goal_relation_entry, name='goal_relation_entry'),
    path('goal-relations/<int:relation_id>/update/', views.goal_relation_update, name='goal_relation_update'),
    path('goal-relations/<int:relation_id>/delete/', views.goal_relation_delete, name='goal_relation_delete'),
    path('goal-relations/<int:relation_id>/', views.goal_relation_detail, name='goal_relation_detail'),

    path('materials/', views.material_list, name='material_list'),
    path('materials/upload/', views.material_upload, name='material_upload'),
    path('materials/<int:material_id>/', views.material_detail, name='material_detail'),
    path('materials/<int:material_id>/update/', views.material_update, name='material_update'),
    path('materials/<int:material_id>/delete/', views.material_delete, name='material_delete'),

    path('attainments/', views.attainment_list, name='attainment_list'),
path('attainments/new/', views.attainment_entry, name='attainment_entry'),
    path('courses/<int:course_id>/attainments/create/', views.attainment_create, name='attainment_create'),
    path('attainments/<int:record_id>/', views.attainment_detail, name='attainment_detail'),
    path('attainments/<int:record_id>/update/', views.attainment_update, name='attainment_update'),
path('attainments/<int:record_id>/delete/', views.attainment_delete, name='attainment_delete'),
path('support-matrix/', views.support_matrix, name='support_matrix'),
]