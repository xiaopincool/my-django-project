from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render

from users.permissions import is_admin, is_program

from ..forms import TeacherForm
from ..models import Course


User = get_user_model()


def ensure_admin(user):
    if is_admin(user) or is_program(user):
        return None
    return HttpResponseForbidden('当前角色无权限')


def attach_teacher_course_info(teacher_list):
    for item in teacher_list:
        course_list = list(item.course_set.all().order_by('code'))
        item.course_total = len(course_list)
        item.course_name_text = '、'.join([course.name for course in course_list[:3]]) or '暂未分配课程'
        item.role_text = '任课教师'
        item.status_text = '启用' if item.is_active else '停用'


@login_required
def teacher_list(request):
    deny = ensure_admin(request.user)
    if deny:
        return deny

    keyword = (request.GET.get('keyword') or '').strip()
    status = (request.GET.get('status') or '').strip()

    teacher_qs = User.objects.filter(role='teacher').prefetch_related('course_set').order_by('username', 'id')

    if keyword:
        teacher_qs = teacher_qs.filter(
            Q(username__icontains=keyword) |
            Q(realname__icontains=keyword) |
            Q(mobile__icontains=keyword)
        )

    if status == 'active':
        teacher_qs = teacher_qs.filter(is_active=True)
    elif status == 'inactive':
        teacher_qs = teacher_qs.filter(is_active=False)

    teacher_list_data = list(teacher_qs)
    attach_teacher_course_info(teacher_list_data)

    all_teacher_qs = User.objects.filter(role='teacher')
    course_teacher_ids = Course.objects.filter(teacher__role='teacher').values_list('teacher_id', flat=True).distinct()

    context = {
        'teacher_list': teacher_list_data,
        'keyword': keyword,
        'status': status,
        'stats': {
            'teacher_total': all_teacher_qs.count(),
            'active_total': all_teacher_qs.filter(is_active=True).count(),
            'course_total': Course.objects.filter(teacher__role='teacher').count(),
            'linked_total': all_teacher_qs.filter(id__in=course_teacher_ids).count(),
        }
    }
    return render(request, 'accreditation/teacher_list.html', context=context)


@login_required
def teacher_create(request):
    deny = ensure_admin(request.user)
    if deny:
        return deny

    if request.method == 'GET':
        form = TeacherForm()
        return render(
            request,
            'accreditation/teacher_form.html',
            context={'form': form, 'page_title': '新增教师'}
        )

    form = TeacherForm(request.POST)
    if form.is_valid():
        teacher = form.save(commit=False)
        teacher.is_staff = False
        teacher.is_superuser = False
        teacher.save()
        messages.success(request, '教师账号已新增。')
        return redirect('accreditation:teacher_list')

    return render(
        request,
        'accreditation/teacher_form.html',
        context={'form': form, 'page_title': '新增教师'}
    )


@login_required
def teacher_detail(request, teacher_id):
    deny = ensure_admin(request.user)
    if deny:
        return deny

    teacher = get_object_or_404(User.objects.filter(role='teacher').prefetch_related('course_set'), pk=teacher_id)
    attach_teacher_course_info([teacher])
    return render(
        request,
        'accreditation/teacher_detail.html',
        context={'teacher_obj': teacher}
    )


@login_required
def teacher_update(request, teacher_id):
    deny = ensure_admin(request.user)
    if deny:
        return deny

    teacher = get_object_or_404(User.objects.filter(role='teacher'), pk=teacher_id)

    if request.method == 'GET':
        form = TeacherForm(instance=teacher)
        return render(
            request,
            'accreditation/teacher_form.html',
            context={
                'form': form,
                'page_title': '编辑教师',
                'teacher_obj': teacher,
            }
        )

    form = TeacherForm(request.POST, instance=teacher)
    if form.is_valid():
        form.save()
        messages.success(request, '教师信息已更新。')
        return redirect('accreditation:teacher_detail', teacher_id=teacher.id)

    return render(
        request,
        'accreditation/teacher_form.html',
        context={
            'form': form,
            'page_title': '编辑教师',
            'teacher_obj': teacher,
        }
    )


@login_required
def teacher_delete(request, teacher_id):
    deny = ensure_admin(request.user)
    if deny:
        return deny

    teacher = get_object_or_404(User.objects.filter(role='teacher'), pk=teacher_id)

    if request.method == 'POST':
        teacher.delete()
        messages.success(request, '教师账号已删除。')
        return redirect('accreditation:teacher_list')

    return render(
        request,
        'accreditation/teacher_confirm_delete.html',
        context={'teacher_obj': teacher}
    )
