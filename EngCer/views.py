from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.db import OperationalError, ProgrammingError
from django.shortcuts import render


# 首页门户，放常用入口和几个关键数字
@login_required
def index(request):
    User = get_user_model()
    from accreditation.models import (
        GraduationRequirement,
        RequirementIndicator,
        Course,
        CourseIndicatorRelation,
        CourseAttainmentRecord,
        TrainingPlan,
        Student,
    )

    gr_num = GraduationRequirement.objects.count()
    indicator_num = RequirementIndicator.objects.count()
    course_num = Course.objects.count()
    relation_num = CourseIndicatorRelation.objects.count()
    attain_num = CourseAttainmentRecord.objects.count()
    try:
        plan_num = TrainingPlan.objects.count()
    except (OperationalError, ProgrammingError):
        plan_num = 0
    try:
        student_num = Student.objects.count()
    except (OperationalError, ProgrammingError):
        student_num = 0

    teacher_num = User.objects.filter(role='teacher').count()
    account_num = User.objects.count()
    role = getattr(request.user, 'role', '')
    is_admin_role = role == 'admin'

    if role == 'admin':
        entry_num = 8
    elif role == 'program':
        entry_num = 7
    else:
        entry_num = 5

    ctx = {
        'gr_num': gr_num,
        'indicator_num': indicator_num,
        'course_num': course_num,
        'relation_num': relation_num,
        'attain_num': attain_num,
        'plan_num': plan_num,
        'student_num': student_num,
        'teacher_num': teacher_num,
        'account_num': account_num,
        'entry_num': entry_num,
    }
    return render(request, 'index.html', context=ctx)
