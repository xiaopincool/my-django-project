from django.contrib.auth.models import AbstractUser
from django.db import models


# 系统用户
class EngUser(AbstractUser):
    # 三种角色
    ROLE_CHOICES = (
        ('admin', '管理员'),
        ('teacher', '任课教师'),
        ('program', '专业负责人'),
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='teacher',
        verbose_name='角色'
    )
    realname = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='真实姓名'
    )
    mobile = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name='手机号'
    )

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = '用户'
        verbose_name_plural = verbose_name
