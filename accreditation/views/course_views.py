from decimal import Decimal, ROUND_HALF_UP

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.utils.http import url_has_allowed_host_and_scheme
from django.urls import reverse

from ..forms import (
    CourseForm,
    CourseGoalForm,
    CourseIndicatorRelationForm,
    GoalIndicatorRelationForm,
)
from ..models import (
    Course,
    CourseGoal,
    CourseIndicatorRelation,
    GoalIndicatorRelation,
)


WEIGHT_STEP = Decimal('0.01')
WEIGHT_TARGET = Decimal('1.00')


def get_safe_next_url(request, default_url=''):
    next_url = request.POST.get('next_url') or request.GET.get('next_url') or ''
    if next_url and url_has_allowed_host_and_scheme(
        url=next_url,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return next_url
    return default_url


def _q2(val):
    return Decimal(val or 0).quantize(WEIGHT_STEP, rounding=ROUND_HALF_UP)


def _fmt_weight(val):
    return format(_q2(val), 'f')


def _weight_pct(val):
    pct = _q2(val) * Decimal('100')
    return int(pct.quantize(Decimal('1'), rounding=ROUND_HALF_UP))


def _weight_bar_pct(val):
    pct = _weight_pct(val)
    if pct < 0:
        return 0
    if pct > 100:
        return 100
    return pct


def _weight_fill_cls(val):
    val = _q2(val)
    if val >= Decimal('0.75'):
        return 'rl-weight-red'
    if val >= Decimal('0.35'):
        return 'rl-weight-orange'
    return 'rl-weight-gray'


def _sum_state(total):
    total = _q2(total)
    diff = total - WEIGHT_TARGET

    if abs(diff) <= Decimal('0.01'):
        return {
            'sum_state': 'ok',
            'sum_badge': '权重闭合',
            'sum_tip': '当前指标点下课程权重和为 1.00，可以直接用于后续达成度计算。',
            'sum_bar_cls': 'rl-weight-green',
        }

    if diff < 0:
        gap = _fmt_weight(abs(diff))
        return {
            'sum_state': 'pending',
            'sum_badge': '还差 %s' % gap,
            'sum_tip': '当前指标点权重和为 %s，还差 %s 才到 1.00。' % (_fmt_weight(total), gap),
            'sum_bar_cls': 'rl-weight-orange',
        }

    over = _fmt_weight(diff)
    return {
        'sum_state': 'bad',
        'sum_badge': '超出 %s' % over,
        'sum_tip': '当前指标点权重和为 %s，已经超出 %s，请回收部分权重。' % (_fmt_weight(total), over),
        'sum_bar_cls': 'rl-weight-red',
    }


def _build_relation_groups(relations):
    req_list = []
    req_map = {}
    close_count = 0
    warn_count = 0

    for idx, rel in enumerate(relations, start=1):
        req = rel.indicator.graduation_requirement
        req_item = req_map.get(req.id)

        if req_item is None:
            req_item = {
                'id': req.id,
                'code': req.code or 'GR%s' % idx,
                'name': req.name or '毕业要求%s' % idx,
                'content': req.content,
                'relation_count': 0,
                'high_count': 0,
                'middle_count': 0,
                'low_count': 0,
                'indicators': [],
                '_indicator_map': {},
            }
            req_map[req.id] = req_item
            req_list.append(req_item)

        indicator = rel.indicator
        indicator_item = req_item['_indicator_map'].get(indicator.id)

        if indicator_item is None:
            indicator_item = {
                'id': indicator.id,
                'code': indicator.code,
                'content': indicator.content,
                'sort': indicator.sort,
                'relation_count': 0,
                'weight_sum_raw': Decimal('0'),
                'relations': [],
            }
            req_item['_indicator_map'][indicator.id] = indicator_item
            req_item['indicators'].append(indicator_item)

        weight_val = _q2(rel.weight)
        indicator_item['weight_sum_raw'] += weight_val
        indicator_item['relation_count'] += 1
        req_item['relation_count'] += 1
        req_item['%s_count' % rel.support_level] += 1

        indicator_item['relations'].append({
            'id': rel.id,
            'course_name': rel.course.name,
            'course_code': rel.course.code,
            'support_level': rel.support_level,
            'support_label': rel.get_support_level_display(),
            'weight_text': _fmt_weight(weight_val),
            'weight_pct': _weight_pct(weight_val),
            'weight_bar_pct': _weight_bar_pct(weight_val),
            'weight_fill_cls': _weight_fill_cls(weight_val),
        })

    for req_item in req_list:
        req_item['indicator_count'] = len(req_item['indicators'])

        for indicator_item in req_item['indicators']:
            weight_sum = _q2(indicator_item.pop('weight_sum_raw'))
            indicator_item['weight_sum_text'] = _fmt_weight(weight_sum)
            indicator_item['weight_sum_pct'] = _weight_pct(weight_sum)
            indicator_item['weight_sum_bar_pct'] = _weight_bar_pct(weight_sum)
            indicator_item.update(_sum_state(weight_sum))

            if indicator_item['sum_state'] == 'ok':
                close_count += 1
            else:
                warn_count += 1

        req_item.pop('_indicator_map', None)

    return req_list, close_count, warn_count


# 课程列表
@login_required
def course_list(request):
    courses = Course.objects.select_related('teacher').all().order_by('code', 'id')
    return render(
        request,
        'accreditation/course_list.html',
        context={'courses': courses}
    )


# 新增课程
@login_required
def course_create(request):
    if request.method == 'GET':
        form = CourseForm()
        return render(
            request,
            'accreditation/course_form.html',
            context={'form': form, 'page_title': '新增课程'}
        )

    form = CourseForm(request.POST)
    if form.is_valid():
        form.save()
        return redirect('accreditation:course_list')

    return render(
        request,
        'accreditation/course_form.html',
        context={'form': form, 'page_title': '新增课程'}
    )


# 课程详情
@login_required
def course_detail(request, course_id):
    course = get_object_or_404(
        Course.objects.select_related('teacher'),
        pk=course_id
    )

    relations = course.indicator_relations.select_related('indicator').all().order_by('indicator__code', 'id')
    attainment_records = course.attainment_records.all().order_by('-id')

    context = {
        'course': course,
        'relations': relations,
        'attainment_records': attainment_records,
    }
    return render(request, 'accreditation/course_detail.html', context=context)


# 编辑课程
@login_required
def course_update(request, course_id):
    course = get_object_or_404(Course, pk=course_id)

    if request.method == 'GET':
        form = CourseForm(instance=course)
        return render(
            request,
            'accreditation/course_form.html',
            context={'form': form, 'page_title': '编辑课程'}
        )

    form = CourseForm(request.POST, instance=course)
    if form.is_valid():
        form.save()
        return redirect('accreditation:course_detail', course_id=course.id)

    return render(
        request,
        'accreditation/course_form.html',
        context={'form': form, 'page_title': '编辑课程'}
    )


# 删除课程
@login_required
def course_delete(request, course_id):
    course = get_object_or_404(Course, pk=course_id)

    if request.method == 'POST':
        course.delete()
        return redirect('accreditation:course_list')

    return render(
        request,
        'accreditation/course_confirm_delete.html',
        context={'course': course}
    )


# 课程目标列表
@login_required
def goal_list(request):
    goals = CourseGoal.objects.select_related('course').all().order_by('course__code', 'sort', 'id')
    return render(
        request,
        'accreditation/goal_list.html',
        context={'goals': goals}
    )


# 课程目标新增入口，先选课程
@login_required
def goal_entry(request):
    course_rows = Course.objects.select_related('teacher').all().order_by('code', 'id')
    return render(
        request,
        'accreditation/goal_entry.html',
        context={'course_rows': course_rows}
    )


# 新增课程目标
@login_required
def goal_create(request, course_id):
    course = get_object_or_404(Course, pk=course_id)

    if request.method == 'GET':
        form = CourseGoalForm()
        return render(
            request,
            'accreditation/goal_form.html',
            context={'form': form, 'course': course, 'page_title': '新增课程目标'}
        )

    form = CourseGoalForm(request.POST)
    if form.is_valid():
        goal = form.save(commit=False)
        goal.course = course
        goal.save()
        return redirect('accreditation:course_detail', course_id=course.id)

    return render(
        request,
        'accreditation/goal_form.html',
        context={'form': form, 'course': course, 'page_title': '新增课程目标'}
    )


# 课程目标详情
@login_required
def goal_detail(request, goal_id):
    goal = get_object_or_404(
        CourseGoal.objects.select_related('course'),
        pk=goal_id
    )
    relations = goal.indicator_relations.select_related('indicator').all().order_by('indicator__code', 'id')
    return render(
        request,
        'accreditation/goal_detail.html',
        context={'goal': goal, 'relations': relations}
    )


# 编辑课程目标
@login_required
def goal_update(request, goal_id):
    goal = get_object_or_404(
        CourseGoal.objects.select_related('course'),
        pk=goal_id
    )
    course = goal.course

    if request.method == 'GET':
        form = CourseGoalForm(instance=goal)
        return render(
            request,
            'accreditation/goal_form.html',
            context={'form': form, 'course': course, 'page_title': '编辑课程目标'}
        )

    form = CourseGoalForm(request.POST, instance=goal)
    if form.is_valid():
        form.save()
        return redirect('accreditation:course_detail', course_id=course.id)

    return render(
        request,
        'accreditation/goal_form.html',
        context={'form': form, 'course': course, 'page_title': '编辑课程目标'}
    )


# 删除课程目标
@login_required
def goal_delete(request, goal_id):
    goal = get_object_or_404(
        CourseGoal.objects.select_related('course'),
        pk=goal_id
    )
    course = goal.course
    default_next_url = reverse('accreditation:course_detail', kwargs={'course_id': course.id})
    next_url = get_safe_next_url(request, default_next_url)

    if request.method == 'POST':
        goal.delete()
        return redirect(next_url)

    return render(
        request,
        'accreditation/goal_confirm_delete.html',
        context={
            'goal': goal,
            'course': course,
            'next_url': next_url,
        }
    )


# 课程支撑关系列表
@login_required
def relation_list(request):
    relation_qs = CourseIndicatorRelation.objects.select_related(
        'course',
        'indicator',
        'indicator__graduation_requirement',
    ).all()

    relations = list(relation_qs)
    relations.sort(
        key=lambda item: (
            item.indicator.graduation_requirement_id,
            item.indicator.sort,
            item.indicator_id,
            item.course.code,
            item.id,
        )
    )
    req_groups, close_indicator_count, warn_indicator_count = _build_relation_groups(relations)

    context = {
        'req_groups': req_groups,
        'relation_count': len(relations),
        'course_count': len({item.course_id for item in relations}),
        'indicator_count': len({item.indicator_id for item in relations}),
        'requirement_count': len(req_groups),
        'close_indicator_count': close_indicator_count,
        'warn_indicator_count': warn_indicator_count,
        'high_count': len([item for item in relations if item.support_level == 'high']),
        'middle_count': len([item for item in relations if item.support_level == 'middle']),
        'low_count': len([item for item in relations if item.support_level == 'low']),
    }
    return render(
        request,
        'accreditation/relation_list.html',
        context=context
    )


# 课程支撑关系新增入口，先选课程
@login_required
def relation_entry(request):
    course_rows = Course.objects.select_related('teacher').all().order_by('code', 'id')
    return render(
        request,
        'accreditation/relation_entry.html',
        context={'course_rows': course_rows}
    )


# 新增课程支撑关系
@login_required
def relation_create(request, course_id):
    course = get_object_or_404(Course, pk=course_id)

    if request.method == 'GET':
        form = CourseIndicatorRelationForm()
        return render(
            request,
            'accreditation/relation_form.html',
            context={'form': form, 'course': course, 'page_title': '新增课程支撑关系'}
        )

    form = CourseIndicatorRelationForm(request.POST)
    if form.is_valid():
        rel = form.save(commit=False)
        rel.course = course
        rel.save()
        return redirect('accreditation:course_detail', course_id=course.id)

    return render(
        request,
        'accreditation/relation_form.html',
        context={'form': form, 'course': course, 'page_title': '新增课程支撑关系'}
    )


# 课程支撑关系详情
@login_required
def relation_detail(request, relation_id):
    rel = get_object_or_404(
        CourseIndicatorRelation.objects.select_related('course', 'indicator'),
        pk=relation_id
    )
    return render(
        request,
        'accreditation/relation_detail.html',
        context={'relation': rel, 'course': rel.course}
    )


# 编辑课程支撑关系
@login_required
def relation_update(request, relation_id):
    rel = get_object_or_404(
        CourseIndicatorRelation.objects.select_related('course'),
        pk=relation_id
    )
    course = rel.course

    if request.method == 'GET':
        form = CourseIndicatorRelationForm(instance=rel)
        return render(
            request,
            'accreditation/relation_form.html',
            context={'form': form, 'course': course, 'relation': rel, 'page_title': '编辑课程支撑关系'}
        )

    form = CourseIndicatorRelationForm(request.POST, instance=rel)
    if form.is_valid():
        form.save()
        return redirect('accreditation:course_detail', course_id=course.id)

    return render(
        request,
        'accreditation/relation_form.html',
        context={'form': form, 'course': course, 'relation': rel, 'page_title': '编辑课程支撑关系'}
    )


# 删除课程支撑关系
@login_required
def relation_delete(request, relation_id):
    rel = get_object_or_404(
        CourseIndicatorRelation.objects.select_related('course'),
        pk=relation_id
    )
    course = rel.course

    if request.method == 'POST':
        rel.delete()
        return redirect('accreditation:course_detail', course_id=course.id)

    return render(
        request,
        'accreditation/relation_confirm_delete.html',
        context={'relation': rel, 'course': course}
    )


# 目标支撑关系列表
@login_required
def goal_relation_list(request):
    relations = GoalIndicatorRelation.objects.select_related(
        'goal',
        'goal__course',
        'indicator'
    ).all().order_by('goal__course__code', 'goal__sort', 'indicator__code', 'id')
    return render(
        request,
        'accreditation/goal_relation_list.html',
        context={'relations': relations}
    )


# 目标支撑关系新增入口，先选课程目标
@login_required
def goal_relation_entry(request):
    goal_rows = CourseGoal.objects.select_related('course').all().order_by('course__code', 'sort', 'id')
    return render(
        request,
        'accreditation/goal_relation_entry.html',
        context={'goal_rows': goal_rows}
    )


# 新增目标支撑关系
@login_required
def goal_relation_create(request, goal_id):
    goal = get_object_or_404(CourseGoal.objects.select_related('course'), pk=goal_id)

    if request.method == 'GET':
        form = GoalIndicatorRelationForm()
        return render(
            request,
            'accreditation/goal_relation_form.html',
            context={'form': form, 'goal': goal, 'page_title': '新增目标支撑关系'}
        )

    form = GoalIndicatorRelationForm(request.POST)
    if form.is_valid():
        rel = form.save(commit=False)
        rel.goal = goal
        rel.save()
        return redirect('accreditation:goal_detail', goal_id=goal.id)

    return render(
        request,
        'accreditation/goal_relation_form.html',
        context={'form': form, 'goal': goal, 'page_title': '新增目标支撑关系'}
    )


# 目标支撑关系详情
@login_required
def goal_relation_detail(request, relation_id):
    rel = get_object_or_404(
        GoalIndicatorRelation.objects.select_related('goal', 'goal__course', 'indicator'),
        pk=relation_id
    )
    return render(
        request,
        'accreditation/goal_relation_detail.html',
        context={'relation': rel}
    )


# 编辑目标支撑关系
@login_required
def goal_relation_update(request, relation_id):
    rel = get_object_or_404(
        GoalIndicatorRelation.objects.select_related('goal', 'goal__course', 'indicator'),
        pk=relation_id
    )
    goal = rel.goal

    if request.method == 'GET':
        form = GoalIndicatorRelationForm(instance=rel)
        return render(
            request,
            'accreditation/goal_relation_form.html',
            context={'form': form, 'goal': goal, 'page_title': '编辑目标支撑关系'}
        )

    form = GoalIndicatorRelationForm(request.POST, instance=rel)
    if form.is_valid():
        form.save()
        return redirect('accreditation:goal_relation_detail', relation_id=rel.id)

    return render(
        request,
        'accreditation/goal_relation_form.html',
        context={'form': form, 'goal': goal, 'page_title': '编辑目标支撑关系'}
    )


# 删除目标支撑关系
@login_required
def goal_relation_delete(request, relation_id):
    rel = get_object_or_404(
        GoalIndicatorRelation.objects.select_related('goal', 'goal__course', 'indicator'),
        pk=relation_id
    )
    goal = rel.goal

    if request.method == 'POST':
        rel.delete()
        return redirect('accreditation:goal_detail', goal_id=goal.id)

    return render(
        request,
        'accreditation/goal_relation_confirm_delete.html',
        context={'relation': rel, 'goal': goal}
    )
