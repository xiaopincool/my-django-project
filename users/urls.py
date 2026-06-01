# from django.urls import path
# from . import views
#
# app_name = 'users'
#
# urlpatterns = [
#     # 登录
#     path('login/', views.login_view, name='login'),
#
#     # 退出登录
#     path('logout/', views.logout_view, name='logout'),
# ]
from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
]