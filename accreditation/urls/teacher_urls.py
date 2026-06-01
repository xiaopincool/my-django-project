from django.urls import path

from .. import views


urlpatterns = [
    path('teachers/', views.teacher_list, name='teacher_list'),
    path('teachers/create/', views.teacher_create, name='teacher_create'),
    path('teachers/<int:teacher_id>/', views.teacher_detail, name='teacher_detail'),
    path('teachers/<int:teacher_id>/update/', views.teacher_update, name='teacher_update'),
    path('teachers/<int:teacher_id>/delete/', views.teacher_delete, name='teacher_delete'),
]
