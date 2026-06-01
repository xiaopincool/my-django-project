from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import OperationalError, ProgrammingError
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from ..forms import TrainingPlanForm
from ..models import TrainingPlan


@login_required
def training_plan_list(request):
    sel_college = (request.GET.get('college') or '').strip()
    sel_major = (request.GET.get('major') or '').strip()
    sel_year = (request.GET.get('year') or '').strip()

    college_list = []
    major_list = []
    year_list = []
    plan_list = []
    now_plan = None
    show_plan = None
    total_count = 0

    try:
        base_qs = TrainingPlan.objects.all().order_by('-plan_year', 'college_name', 'major_name', 'id')
        active_qs = base_qs.filter(is_active=True)
        total_count = base_qs.count()

        now_plan_id = request.session.get('current_training_plan_id')
        if now_plan_id:
            now_plan = active_qs.filter(pk=now_plan_id).first()
        if now_plan is None:
            now_plan = active_qs.first()
        if now_plan is None:
            now_plan = base_qs.first()

        current_plan_id = (request.GET.get('current_plan') or '').strip()
        if current_plan_id and current_plan_id.isdigit():
            change_plan = base_qs.filter(pk=current_plan_id).first()
            if change_plan:
                if change_plan.is_active:
                    request.session['current_training_plan_id'] = change_plan.id
                    messages.success(request, '当前培养方案已切换。')
                else:
                    messages.warning(request, '当前方案未启用，不能设为当前专业。')

            jump_url = reverse('accreditation:training_plan_list')
            query_data = request.GET.copy()
            if 'current_plan' in query_data:
                del query_data['current_plan']
            if query_data.urlencode():
                jump_url = '%s?%s' % (jump_url, query_data.urlencode())
            return redirect(jump_url)

        college_list = list(base_qs.order_by('college_name').values_list('college_name', flat=True).distinct())
        major_list = list(base_qs.order_by('major_name').values_list('major_name', flat=True).distinct())
        year_list = list(base_qs.order_by('-plan_year').values_list('plan_year', flat=True).distinct())

        data_qs = base_qs
        if sel_college:
            data_qs = data_qs.filter(college_name=sel_college)
        if sel_major:
            data_qs = data_qs.filter(major_name=sel_major)
        if sel_year:
            try:
                data_qs = data_qs.filter(plan_year=int(sel_year))
            except ValueError:
                data_qs = data_qs.none()

        plan_list = list(data_qs)

        if sel_college and sel_major and sel_year and len(plan_list) == 1:
            only_plan = plan_list[0]
            if only_plan.is_active and request.session.get('current_training_plan_id') != only_plan.id:
                request.session['current_training_plan_id'] = only_plan.id
                now_plan = only_plan

        show_plan = now_plan
        if plan_list:
            show_plan = plan_list[0]
            if now_plan:
                for item in plan_list:
                    if item.id == now_plan.id:
                        show_plan = item
                        break

        if now_plan is None and plan_list:
            now_plan = plan_list[0]
    except (OperationalError, ProgrammingError, ValueError):
        pass

    context = {
        'college_list': college_list,
        'major_list': major_list,
        'year_list': year_list,
        'plan_list': plan_list,
        'now_plan': now_plan,
        'show_plan': show_plan,
        'sel_college': sel_college,
        'sel_major': sel_major,
        'sel_year': sel_year,
        'total_count': total_count,
    }
    return render(request, 'accreditation/training_plan_list.html', context=context)


@login_required
def training_plan_create(request):
    if request.method == 'GET':
        form = TrainingPlanForm()
        return render(
            request,
            'accreditation/training_plan_form.html',
            context={'form': form, 'page_title': '新增培养方案'}
        )

    form = TrainingPlanForm(request.POST, request.FILES)
    if form.is_valid():
        obj = form.save(commit=False)
        obj.creator = request.user
        obj.save()
        if obj.is_active and not request.session.get('current_training_plan_id'):
            request.session['current_training_plan_id'] = obj.id
        messages.success(request, '培养方案已新增。')
        return redirect('accreditation:training_plan_list')

    return render(
        request,
        'accreditation/training_plan_form.html',
        context={'form': form, 'page_title': '新增培养方案'}
    )


@login_required
def training_plan_update(request, plan_id):
    plan = get_object_or_404(TrainingPlan, pk=plan_id)

    if request.method == 'GET':
        form = TrainingPlanForm(instance=plan)
        return render(
            request,
            'accreditation/training_plan_form.html',
            context={
                'form': form,
                'page_title': '编辑培养方案',
                'plan': plan,
            }
        )

    form = TrainingPlanForm(request.POST, request.FILES, instance=plan)
    if form.is_valid():
        obj = form.save()
        if not obj.is_active and request.session.get('current_training_plan_id') == obj.id:
            next_plan = TrainingPlan.objects.filter(is_active=True).exclude(pk=obj.id).order_by('-plan_year', 'college_name', 'major_name', 'id').first()
            if next_plan:
                request.session['current_training_plan_id'] = next_plan.id
            else:
                request.session.pop('current_training_plan_id', None)
        messages.success(request, '培养方案已更新。')
        return redirect('accreditation:training_plan_list')

    return render(
        request,
        'accreditation/training_plan_form.html',
        context={
            'form': form,
            'page_title': '编辑培养方案',
            'plan': plan,
        }
    )
