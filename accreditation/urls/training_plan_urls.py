from django.urls import path
from .. import views

urlpatterns = [
    path('training-plans/', views.training_plan_list, name='training_plan_list'),
    path('training-plans/create/', views.training_plan_create, name='training_plan_create'),
    path('training-plans/<int:plan_id>/update/', views.training_plan_update, name='training_plan_update'),
]
