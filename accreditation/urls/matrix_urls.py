from django.urls import path
from .. import views

urlpatterns = [
    path('support-matrix/', views.support_matrix, name='support_matrix'),
]