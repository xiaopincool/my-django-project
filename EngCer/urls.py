from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from .views import index

urlpatterns = [
    # 系统首页
    path('', index, name='index'),

    # 后台管理
    path('admin/', admin.site.urls),

    # 用户模块
    path('users/', include('users.urls')),

    # 认证模块
    path('accreditation/', include('accreditation.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)