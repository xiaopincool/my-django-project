from .permissions import is_admin, is_teacher, is_program, role_label, can_manage_requirement


def role_flags(request):
    user = request.user
    sidebar_plan = None
    sidebar_plan_college = ''
    sidebar_plan_major = '计算机科学与技术'
    sidebar_plan_year = '2024'

    try:
        from django.db import OperationalError, ProgrammingError
        from accreditation.models import TrainingPlan

        plan_qs = TrainingPlan.objects.filter(is_active=True).order_by('-plan_year', 'college_name', 'major_name', 'id')
        plan_id = request.session.get('current_training_plan_id')

        if plan_id:
            sidebar_plan = plan_qs.filter(pk=plan_id).first()
        if sidebar_plan is None:
            sidebar_plan = plan_qs.first()

        if sidebar_plan:
            sidebar_plan_college = sidebar_plan.college_name
            sidebar_plan_major = sidebar_plan.major_name
            sidebar_plan_year = str(sidebar_plan.plan_year)
    except (OperationalError, ProgrammingError, ValueError):
        pass

    return {
        'is_admin_role': is_admin(user),
        'is_teacher_role': is_teacher(user),
        'is_program_role': is_program(user),
        'current_role_label': role_label(user),
        'can_manage_requirement': can_manage_requirement(user),
        'is_readonly_role': False,
        'sidebar_plan': sidebar_plan,
        'sidebar_plan_college': sidebar_plan_college,
        'sidebar_plan_major': sidebar_plan_major,
        'sidebar_plan_year': sidebar_plan_year,
    }
