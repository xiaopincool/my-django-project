from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from ..models import (
    GraduationRequirement,
    RequirementIndicator,
    Course,
    CourseIndicatorRelation,
    CourseAttainmentRecord,
)


# 工作台首页，展示系统各模块统计信息
@login_required
def dashboard(request):
    context = {
        'requirement_count': GraduationRequirement.objects.count(),
        'indicator_count': RequirementIndicator.objects.count(),
        'course_count': Course.objects.count(),
        'relation_count': CourseIndicatorRelation.objects.count(),
        'attainment_count': CourseAttainmentRecord.objects.count(),
    }
    return render(request, 'accreditation/dashboard.html', context=context)
