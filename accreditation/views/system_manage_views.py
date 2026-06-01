from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import render

from users.permissions import is_admin

from ..models import Course


User = get_user_model()


@login_required
def system_manage(request):
    if not is_admin(request.user):
        return HttpResponseForbidden('当前角色无权限')

    user_qs = User.objects.all().order_by('-date_joined')

    context = {
        'stats': {
            'account_total': user_qs.count(),
            'admin_total': user_qs.filter(role='admin').count(),
            'teacher_total': user_qs.filter(role='teacher').count(),
            'program_total': user_qs.filter(role='program').count(),
        },
        'course_link_total': Course.objects.filter(teacher__role='teacher').count(),
        'active_total': user_qs.filter(is_active=True).count(),
        'recent_user_list': user_qs[:6],
    }
    return render(request, 'accreditation/system_manage.html', context=context)
