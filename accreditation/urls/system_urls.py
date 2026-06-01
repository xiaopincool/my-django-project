from django.urls import path

from .. import views


urlpatterns = [
    path('system-manage/', views.system_manage, name='system_manage'),
]
