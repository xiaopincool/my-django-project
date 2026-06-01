from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from ..forms import StudentForm
from ..models import Student


@login_required
def student_list(request):
    q = (request.GET.get('q') or '').strip()
    college = (request.GET.get('college') or '').strip()
    major = (request.GET.get('major') or '').strip()
    grade = (request.GET.get('grade') or '').strip()
    class_name = (request.GET.get('class_name') or '').strip()
    status = (request.GET.get('status') or '').strip()

    student_qs = Student.objects.all().order_by('student_no', 'id')

    if q:
        student_qs = student_qs.filter(
            Q(name__icontains=q) | Q(student_no__icontains=q)
        )

    if college:
        student_qs = student_qs.filter(college_name=college)

    if major:
        student_qs = student_qs.filter(major_name=major)

    if grade:
        student_qs = student_qs.filter(grade_name=grade)

    if class_name:
        student_qs = student_qs.filter(class_name=class_name)

    if status:
        student_qs = student_qs.filter(status=status)

    students = list(student_qs)

    all_qs = Student.objects.all()
    college_list = list(all_qs.order_by('college_name').values_list('college_name', flat=True).distinct())
    major_list = list(all_qs.order_by('major_name').values_list('major_name', flat=True).distinct())
    grade_list = list(all_qs.order_by('grade_name').values_list('grade_name', flat=True).distinct())
    class_list = list(all_qs.order_by('class_name').values_list('class_name', flat=True).distinct())

    stats = {
        'student_total': all_qs.count(),
        'studying_total': all_qs.filter(status='studying').count(),
        'grade_total': all_qs.values('grade_name').exclude(grade_name='').distinct().count(),
        'class_total': all_qs.values('class_name').exclude(class_name='').distinct().count(),
    }

    context = {
        'students': students,
        'college_list': college_list,
        'major_list': major_list,
        'grade_list': grade_list,
        'class_list': class_list,
        'status_choices': Student.STATUS_CHOICES,
        'q': q,
        'college': college,
        'major': major,
        'grade': grade,
        'class_name': class_name,
        'status': status,
        'stats': stats,
    }
    return render(request, 'accreditation/student_list.html', context=context)


@login_required
def student_create(request):
    if request.method == 'GET':
        form = StudentForm()
        return render(
            request,
            'accreditation/student_form.html',
            context={'form': form, 'page_title': '新增学生'}
        )

    form = StudentForm(request.POST)
    if form.is_valid():
        obj = form.save(commit=False)
        obj.creator = request.user
        obj.save()
        messages.success(request, '学生信息已新增。')
        return redirect('accreditation:student_list')

    return render(
        request,
        'accreditation/student_form.html',
        context={'form': form, 'page_title': '新增学生'}
    )


@login_required
def student_detail(request, student_id):
    student = get_object_or_404(Student, pk=student_id)
    return render(
        request,
        'accreditation/student_detail.html',
        context={'student': student}
    )


@login_required
def student_update(request, student_id):
    student = get_object_or_404(Student, pk=student_id)

    if request.method == 'GET':
        form = StudentForm(instance=student)
        return render(
            request,
            'accreditation/student_form.html',
            context={
                'form': form,
                'page_title': '编辑学生',
                'student': student,
            }
        )

    form = StudentForm(request.POST, instance=student)
    if form.is_valid():
        form.save()
        messages.success(request, '学生信息已更新。')
        return redirect('accreditation:student_detail', student_id=student.id)

    return render(
        request,
        'accreditation/student_form.html',
        context={
            'form': form,
            'page_title': '编辑学生',
            'student': student,
        }
    )


@login_required
def student_delete(request, student_id):
    student = get_object_or_404(Student, pk=student_id)

    if request.method == 'POST':
        student.delete()
        messages.success(request, '学生信息已删除。')
        return redirect('accreditation:student_list')

    return render(
        request,
        'accreditation/student_confirm_delete.html',
        context={'student': student}
    )
