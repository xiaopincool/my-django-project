from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from accreditation.forms import CourseMaterialForm
from accreditation.models import Course, CourseMaterial

from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
def get_safe_next_url(request, default_url=''):
    next_url = request.POST.get('next_url') or request.GET.get('next_url') or ''
    if next_url and url_has_allowed_host_and_scheme(
        url=next_url,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return next_url
    return default_url
# 材料列表
@login_required
def material_list(request):
    q = request.GET.get('q', '').strip()
    course_id = request.GET.get('course_id', '').strip()
    status = request.GET.get('status', '').strip()

    materials = CourseMaterial.objects.select_related('course', 'category', 'uploader').all()

    if q:
        materials = materials.filter(title__icontains=q)

    if course_id:
        materials = materials.filter(course_id=course_id)

    if status:
        materials = materials.filter(status=status)

    materials = materials.order_by('-id')
    courses = Course.objects.all().order_by('code')
    status_choices = getattr(CourseMaterial, 'STATUS_CHOICES', [])

    context = {
        'materials': materials,
        'courses': courses,
        'status_choices': status_choices,
        'q': q,
        'course_id': course_id,
        'status': status,
    }
    return render(request, 'accreditation/material_list.html', context)


# 上传材料
# @login_required
# def material_upload(request):
#     next_course_id = request.GET.get('course_id', '').strip()
#
#     if request.method == 'GET':
#         form = CourseMaterialForm()
#
#         if next_course_id:
#             course = get_object_or_404(Course, pk=next_course_id)
#             form = CourseMaterialForm(initial={'course': course})
#         else:
#             course = None
#
#         return render(
#             request,
#             'accreditation/material_form.html',
#             {
#                 'form': form,
#                 'page_title': '上传材料',
#                 'course': course,
#                 'next_course_id': next_course_id,
#             }
#         )
#
#     next_course_id = request.POST.get('next_course_id', '').strip()
#     form = CourseMaterialForm(request.POST, request.FILES)
#
#     if form.is_valid():
#         obj = form.save(commit=False)
#         obj.uploader = request.user
#         obj.status = 'submitted'
#         obj.save()
#
#         if next_course_id:
#             return redirect('accreditation:course_detail', course_id=next_course_id)
#
#         return redirect('accreditation:material_list')
#
#     course = None
#     if next_course_id:
#         course = get_object_or_404(Course, pk=next_course_id)
#
#     return render(
#         request,
#         'accreditation/material_form.html',
#         {
#             'form': form,
#             'page_title': '上传材料',
#             'course': course,
#             'next_course_id': next_course_id,
#         }
#     )
@login_required
def material_upload(request):
    next_course_id = request.GET.get('course_id', '').strip() or request.POST.get('next_course_id', '').strip()

    if next_course_id:
        default_next_url = reverse('accreditation:course_detail', kwargs={'course_id': next_course_id})
    else:
        default_next_url = reverse('accreditation:material_list')

    next_url = get_safe_next_url(request, default_next_url)

    if request.method == 'GET':
        form = CourseMaterialForm()

        if next_course_id:
            course = get_object_or_404(Course, pk=next_course_id)
            form = CourseMaterialForm(initial={'course': course})
        else:
            course = None

        return render(
            request,
            'accreditation/material_form.html',
            {
                'form': form,
                'page_title': '上传材料',
                'course': course,
                'next_course_id': next_course_id,
                'next_url': next_url,
            }
        )

    form = CourseMaterialForm(request.POST, request.FILES)

    if form.is_valid():
        obj = form.save(commit=False)
        obj.uploader = request.user
        obj.status = 'submitted'
        obj.save()
        return redirect(next_url)

    course = None
    if next_course_id:
        course = get_object_or_404(Course, pk=next_course_id)

    return render(
        request,
        'accreditation/material_form.html',
        {
            'form': form,
            'page_title': '上传材料',
            'course': course,
            'next_course_id': next_course_id,
            'next_url': next_url,
        }
    )

# 材料详情
@login_required
def material_detail(request, material_id):
    stuff = get_object_or_404(
        CourseMaterial.objects.select_related('course', 'category', 'uploader'),
        pk=material_id
    )
    return render(
        request,
        'accreditation/material_detail.html',
        {
            'material': stuff,
            'course': stuff.course,
        }
    )


# # 编辑材料
# @login_required
# def material_update(request, material_id):
#     stuff = get_object_or_404(CourseMaterial.objects.select_related('course'), pk=material_id)
#     course = stuff.course
#
#     if request.method == 'GET':
#         form = CourseMaterialForm(instance=stuff)
#         return render(
#             request,
#             'accreditation/material_form.html',
#             {
#                 'form': form,
#                 'material': stuff,
#                 'course': course,
#                 'page_title': '编辑材料',
#                 'next_course_id': course.id,
#             }
#         )
#
#     form = CourseMaterialForm(request.POST, request.FILES, instance=stuff)
#     if form.is_valid():
#         obj = form.save(commit=False)
#
#         if not obj.uploader_id:
#             obj.uploader = request.user
#
#         if not obj.status:
#             obj.status = 'submitted'
#
#         obj.save()
#         return redirect('accreditation:course_detail', course_id=course.id)
#
#     return render(
#         request,
#         'accreditation/material_form.html',
#         {
#             'form': form,
#             'material': stuff,
#             'course': course,
#             'page_title': '编辑材料',
#             'next_course_id': course.id,
#         }
#     )

@login_required
def material_update(request, material_id):
    stuff = get_object_or_404(CourseMaterial.objects.select_related('course'), pk=material_id)
    course = stuff.course

    default_next_url = reverse('accreditation:course_detail', kwargs={'course_id': course.id})
    next_url = get_safe_next_url(request, default_next_url)

    if request.method == 'GET':
        form = CourseMaterialForm(instance=stuff)
        return render(
            request,
            'accreditation/material_form.html',
            {
                'form': form,
                'material': stuff,
                'course': course,
                'page_title': '编辑材料',
                'next_course_id': course.id,
                'next_url': next_url,
            }
        )

    form = CourseMaterialForm(request.POST, request.FILES, instance=stuff)
    if form.is_valid():
        obj = form.save(commit=False)

        if not obj.uploader_id:
            obj.uploader = request.user

        if not obj.status:
            obj.status = 'submitted'

        obj.save()
        return redirect(next_url)

    return render(
        request,
        'accreditation/material_form.html',
        {
            'form': form,
            'material': stuff,
            'course': course,
            'page_title': '编辑材料',
            'next_course_id': course.id,
            'next_url': next_url,
        }
    )
# # 删除材料
# @login_required
# def material_delete(request, material_id):
#     stuff = get_object_or_404(CourseMaterial.objects.select_related('course'), pk=material_id)
#     course = stuff.course
#
#     if request.method == 'POST':
#         stuff.delete()
#         return redirect('accreditation:course_detail', course_id=course.id)
#
#     return render(
#         request,
#         'accreditation/material_confirm_delete.html',
#         {
#             'material': stuff,
#             'course': course,
#             'page_title': '删除材料',
#         }
#     )
@login_required
def material_delete(request, material_id):
    stuff = get_object_or_404(CourseMaterial.objects.select_related('course'), pk=material_id)
    course = stuff.course

    default_next_url = reverse('accreditation:course_detail', kwargs={'course_id': course.id})
    next_url = get_safe_next_url(request, default_next_url)

    if request.method == 'POST':
        stuff.delete()
        return redirect(next_url)

    return render(
        request,
        'accreditation/material_confirm_delete.html',
        {
            'material': stuff,
            'course': course,
            'page_title': '删除材料',
            'next_url': next_url,
        }
    )