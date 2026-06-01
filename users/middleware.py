from django.http import HttpResponseForbidden
from django.urls import resolve

from accreditation.models import (
    Course,
    CourseGoal,
    CourseIndicatorRelation,
    GoalIndicatorRelation,
    CourseAttainmentRecord,
    ContinuousImprovement,
    GraduationRequirement,
    RequirementIndicator,
)
from .permissions import is_admin, is_teacher, is_program, can_manage_course_obj, can_view_course_obj


class RolePermissionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_view(self, request, view_func, view_args, view_kwargs):
        if not request.user.is_authenticated:
            return None

        match = resolve(request.path_info)
        view_name = match.view_name or ''

        if not view_name.startswith('accreditation:'):
            return None

        if is_admin(request.user):
            return None

        if is_program(request.user):
            return self._check_program(view_name)

        if is_teacher(request.user):
            return self._check_teacher(request, view_name, view_kwargs)

        return HttpResponseForbidden('无权限')

    def _check_program(self, view_name):
        if view_name == 'accreditation:system_manage':
            return HttpResponseForbidden('专业负责人不能进入系统管理')
        return None

    def _check_teacher(self, request, view_name, kwargs):
        # 教师可看的列表
        list_allow_views = {
            'accreditation:dashboard',
            'accreditation:training_plan_list',
            'accreditation:student_list',
            'accreditation:student_detail',
            'accreditation:course_list',
            'accreditation:goal_list',
            'accreditation:relation_list',
            'accreditation:goal_relation_list',
            'accreditation:attainment_list',
            'accreditation:improvement_list',
            'accreditation:requirement_list',
            'accreditation:requirement_detail',
            'accreditation:support_matrix',
        }

        # 教师绝对不能动
        admin_only_views = {
            'accreditation:training_plan_create',
            'accreditation:training_plan_update',
            'accreditation:student_create',
            'accreditation:student_update',
            'accreditation:student_delete',
            'accreditation:requirement_create',
            'accreditation:requirement_update',
            'accreditation:requirement_delete',
            'accreditation:indicator_create',
            'accreditation:indicator_update',
            'accreditation:indicator_delete',
            'accreditation:course_create',
            'accreditation:course_delete',
            'accreditation:course_update',
        }

        if view_name in admin_only_views:
            return HttpResponseForbidden('当前角色无权限')

        if view_name in list_allow_views:
            return None

        course = self._get_course_from_kwargs(view_name, kwargs)
        if course is None:
            return HttpResponseForbidden('当前角色无权限')

        if request.method == 'GET':
            if can_view_course_obj(request.user, course):
                return None
            return HttpResponseForbidden('只能查看自己负责课程的数据')

        if can_manage_course_obj(request.user, course):
            return None

        return HttpResponseForbidden('只能维护自己负责课程的数据')

    def _get_course_from_kwargs(self, view_name, kwargs):
        if 'course_id' in kwargs:
            try:
                return Course.objects.select_related('teacher').get(pk=kwargs['course_id'])
            except Course.DoesNotExist:
                return None

        if 'goal_id' in kwargs:
            try:
                goal = CourseGoal.objects.select_related('course__teacher').get(pk=kwargs['goal_id'])
                return goal.course
            except CourseGoal.DoesNotExist:
                return None

        if 'relation_id' in kwargs:
            if 'goal_relation' in view_name:
                try:
                    rel = GoalIndicatorRelation.objects.select_related('goal__course__teacher').get(pk=kwargs['relation_id'])
                    return rel.goal.course
                except GoalIndicatorRelation.DoesNotExist:
                    return None
            try:
                rel = CourseIndicatorRelation.objects.select_related('course__teacher').get(pk=kwargs['relation_id'])
                return rel.course
            except CourseIndicatorRelation.DoesNotExist:
                return None

        if 'record_id' in kwargs:
            try:
                obj = CourseAttainmentRecord.objects.select_related('course__teacher').get(pk=kwargs['record_id'])
                return obj.course
            except CourseAttainmentRecord.DoesNotExist:
                return None

        if 'item_id' in kwargs:
            try:
                obj = ContinuousImprovement.objects.select_related('course__teacher').get(pk=kwargs['item_id'])
                return obj.course
            except ContinuousImprovement.DoesNotExist:
                return None

        return None
