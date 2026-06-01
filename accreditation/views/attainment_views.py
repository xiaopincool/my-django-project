from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from ..forms import CourseAttainmentRecordForm
from ..models import CourseAttainmentRecord, Course


def _get_result_text(target_value, actual_value):
    if actual_value >= target_value:
        return '已达成'
    return '未达成'

def get_safe_next_url(request, default_url=''):
    next_url = request.POST.get('next_url') or request.GET.get('next_url') or ''
    if next_url and url_has_allowed_host_and_scheme(
        url=next_url,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return next_url
    return default_url

# 达成度记录列表
@login_required
def attainment_list(request):
    course_id = request.GET.get('course_id', '').strip()
    academic_year = request.GET.get('academic_year', '').strip()

    records = CourseAttainmentRecord.objects.select_related('course', 'creator').all()

    if course_id:
        records = records.filter(course_id=course_id)

    if academic_year:
        records = records.filter(academic_year__icontains=academic_year)

    records = records.order_by('-id')
    courses = Course.objects.all().order_by('code', 'id')

    context = {
        'records': records,
        'courses': courses,
        'course_id': course_id,
        'academic_year': academic_year,
    }
    return render(request, 'accreditation/attainment_list.html', context)


# 达成度记录新增入口，先选课程
@login_required
def attainment_entry(request):
    course_rows = Course.objects.select_related('teacher').all().order_by('code', 'id')
    return render(
        request,
        'accreditation/attainment_entry.html',
        context={'course_rows': course_rows}
    )


# # 新增达成度记录
# @login_required
# def attainment_create(request, course_id):
#     course = get_object_or_404(Course, pk=course_id)
#
#     if request.method == 'GET':
#         form = CourseAttainmentRecordForm()
#         return render(
#             request,
#             'accreditation/attainment_form.html',
#             context={
#                 'form': form,
#                 'course': course,
#                 'page_title': '新增达成度记录',
#             }
#         )
#
#     form = CourseAttainmentRecordForm(request.POST)
#     if form.is_valid():
#         rec = form.save(commit=False)
#         rec.course = course
#         rec.creator = request.user
#
#         if not rec.conclusion:
#             rec.conclusion = _get_result_text(rec.target_value, rec.actual_value)
#
#         rec.save()
#         return redirect('accreditation:course_detail', course_id=course.id)
#
#     return render(
#         request,
#         'accreditation/attainment_form.html',
#         context={
#             'form': form,
#             'course': course,
#             'page_title': '新增达成度记录',
#         }
#     )
@login_required
def attainment_create(request, course_id):
    course = get_object_or_404(Course, pk=course_id)

    default_next_url = reverse('accreditation:course_detail', kwargs={'course_id': course.id})
    next_url = get_safe_next_url(request, default_next_url)

    if request.method == 'GET':
        form = CourseAttainmentRecordForm()
        return render(
            request,
            'accreditation/attainment_form.html',
            context={
                'form': form,
                'course': course,
                'page_title': '新增达成度记录',
                'next_url': next_url,
            }
        )

    form = CourseAttainmentRecordForm(request.POST)
    if form.is_valid():
        rec = form.save(commit=False)
        rec.course = course
        rec.creator = request.user

        if not rec.conclusion:
            rec.conclusion = _get_result_text(rec.target_value, rec.actual_value)

        rec.save()
        return redirect(next_url)

    return render(
        request,
        'accreditation/attainment_form.html',
        context={
            'form': form,
            'course': course,
            'page_title': '新增达成度记录',
            'next_url': next_url,
        }
    )

# 达成度记录详情
@login_required
def attainment_detail(request, record_id):
    rec = get_object_or_404(
        CourseAttainmentRecord.objects.select_related('course', 'creator'),
        pk=record_id
    )
    is_reached = rec.actual_value >= rec.target_value

    context = {
        'record': rec,
        'course': rec.course,
        'is_reached': is_reached,
    }
    return render(request, 'accreditation/attainment_detail.html', context)


# # 编辑达成度记录
# @login_required
# def attainment_update(request, record_id):
#     rec = get_object_or_404(
#         CourseAttainmentRecord.objects.select_related('course'),
#         pk=record_id
#     )
#     course = rec.course
#
#     if request.method == 'GET':
#         form = CourseAttainmentRecordForm(instance=rec)
#         return render(
#             request,
#             'accreditation/attainment_form.html',
#             context={
#                 'form': form,
#                 'course': course,
#                 'record': rec,
#                 'page_title': '编辑达成度记录',
#             }
#         )
#
#     form = CourseAttainmentRecordForm(request.POST, instance=rec)
#     if form.is_valid():
#         obj = form.save(commit=False)
#
#         if not obj.conclusion:
#             obj.conclusion = _get_result_text(obj.target_value, obj.actual_value)
#
#         obj.save()
#         return redirect('accreditation:course_detail', course_id=course.id)
#
#     return render(
#         request,
#         'accreditation/attainment_form.html',
#         context={
#             'form': form,
#             'course': course,
#             'record': rec,
#             'page_title': '编辑达成度记录',
#         }
#     )
@login_required
def attainment_update(request, record_id):
    rec = get_object_or_404(
        CourseAttainmentRecord.objects.select_related('course'),
        pk=record_id
    )
    course = rec.course

    default_next_url = reverse('accreditation:course_detail', kwargs={'course_id': course.id})
    next_url = get_safe_next_url(request, default_next_url)

    if request.method == 'GET':
        form = CourseAttainmentRecordForm(instance=rec)
        return render(
            request,
            'accreditation/attainment_form.html',
            context={
                'form': form,
                'course': course,
                'record': rec,
                'page_title': '编辑达成度记录',
                'next_url': next_url,
            }
        )

    form = CourseAttainmentRecordForm(request.POST, instance=rec)
    if form.is_valid():
        obj = form.save(commit=False)

        if not obj.conclusion:
            obj.conclusion = _get_result_text(obj.target_value, obj.actual_value)

        obj.save()
        return redirect(next_url)

    return render(
        request,
        'accreditation/attainment_form.html',
        context={
            'form': form,
            'course': course,
            'record': rec,
            'page_title': '编辑达成度记录',
            'next_url': next_url,
        }
    )

# # 删除达成度记录
# @login_required
# def attainment_delete(request, record_id):
#     rec = get_object_or_404(
#         CourseAttainmentRecord.objects.select_related('course'),
#         pk=record_id
#     )
#     course = rec.course
#
#     if request.method == 'POST':
#         rec.delete()
#         return redirect('accreditation:course_detail', course_id=course.id)
#
#     return render(
#         request,
#         'accreditation/attainment_confirm_delete.html',
#         context={
#             'record': rec,
#             'course': course,
#         }
#     )
@login_required
def attainment_delete(request, record_id):
    rec = get_object_or_404(
        CourseAttainmentRecord.objects.select_related('course'),
        pk=record_id
    )
    course = rec.course

    default_next_url = reverse('accreditation:course_detail', kwargs={'course_id': course.id})
    next_url = get_safe_next_url(request, default_next_url)

    if request.method == 'POST':
        rec.delete()
        return redirect(next_url)

    return render(
        request,
        'accreditation/attainment_confirm_delete.html',
        context={
            'record': rec,
            'course': course,
            'next_url': next_url,
        }
    )