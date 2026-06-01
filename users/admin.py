from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import EngUser


# 用户后台管理
@admin.register(EngUser)
class EngUserAdmin(UserAdmin):
    list_display = ['id', 'username', 'email', 'realname', 'role', 'is_staff']
    list_filter = ['role', 'is_staff', 'is_superuser', 'is_active']
    search_fields = ['username', 'email', 'realname']
    fieldsets = UserAdmin.fieldsets + (
        ('扩展信息', {'fields': ('realname', 'mobile', 'role')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('扩展信息', {'fields': ('realname', 'mobile', 'role')}),
    )