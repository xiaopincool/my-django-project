from django.urls import path

from .. import views

urlpatterns = [
    # 持续改进列表
    path('improvements/', views.improvement_list, name='improvement_list'),

    # 新增整改项入口
    path('improvements/new/', views.improvement_entry, name='improvement_entry'),

    # 新增整改项
    path('improvements/create/', views.improvement_create, name='improvement_create'),

    # 根据达成度记录自动生成整改项
    path(
        'attainments/<int:record_id>/generate-improvement/',
        views.improvement_create_from_attainment,
        name='improvement_create_from_attainment'
    ),

    # 整改项详情
    path('improvements/<int:item_id>/', views.improvement_detail, name='improvement_detail'),

    # 编辑整改项
    path('improvements/<int:item_id>/update/', views.improvement_update, name='improvement_update'),

    # 删除整改项
    path('improvements/<int:item_id>/delete/', views.improvement_delete, name='improvement_delete'),
]