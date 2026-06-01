import re

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect

from ..forms import GraduationRequirementForm, RequirementIndicatorForm
from ..models import GraduationRequirement, RequirementIndicator


# 毕业要求列表
def _code_sort_key(code):
    text = (code or '').strip()
    nums = [int(item) for item in re.findall(r'\d+', text)]
    prefix = re.sub(r'\d+', '', text).lower()
    return prefix, nums, text.lower()


@login_required
def requirement_list(request):
    requirements = list(
        GraduationRequirement.objects.prefetch_related('indicators').all()
    )
    requirements.sort(key=lambda item: _code_sort_key(item.code))

    for item in requirements:
        item.sorted_indicators = sorted(
            item.indicators.all(),
            key=lambda row: _code_sort_key(row.code)
        )

    return render(
        request,
        'accreditation/requirement_list.html',
        context={'requirements': requirements}
    )


# 新增毕业要求
@login_required
def requirement_create(request):
    if request.method == 'GET':
        form = GraduationRequirementForm()
        return render(
            request,
            'accreditation/requirement_form.html',
            context={'form': form, 'page_title': '新增毕业要求'}
        )

    form = GraduationRequirementForm(request.POST)
    if form.is_valid():
        requirement = form.save(commit=False)
        requirement.creator = request.user
        requirement.save()
        return redirect('accreditation:requirement_list')

    return render(
        request,
        'accreditation/requirement_form.html',
        context={'form': form, 'page_title': '新增毕业要求'}
    )


# 毕业要求详情
@login_required
def requirement_detail(request, requirement_id):
    requirement = get_object_or_404(
        GraduationRequirement.objects.prefetch_related('indicators'),
        pk=requirement_id
    )
    return render(
        request,
        'accreditation/requirement_detail.html',
        context={'requirement': requirement}
    )


# 编辑毕业要求
@login_required
def requirement_update(request, requirement_id):
    requirement = get_object_or_404(GraduationRequirement, pk=requirement_id)

    if request.method == 'GET':
        form = GraduationRequirementForm(instance=requirement)
        return render(
            request,
            'accreditation/requirement_form.html',
            context={'form': form, 'page_title': '编辑毕业要求'}
        )

    form = GraduationRequirementForm(request.POST, instance=requirement)
    if form.is_valid():
        form.save()
        return redirect('accreditation:requirement_detail', requirement_id=requirement.id)

    return render(
        request,
        'accreditation/requirement_form.html',
        context={'form': form, 'page_title': '编辑毕业要求'}
    )


# 删除毕业要求
@login_required
def requirement_delete(request, requirement_id):
    requirement = get_object_or_404(GraduationRequirement, pk=requirement_id)

    if request.method == 'POST':
        requirement.delete()
        return redirect('accreditation:requirement_list')

    return render(
        request,
        'accreditation/requirement_confirm_delete.html',
        context={'requirement': requirement}
    )


# 新增指标点
@login_required
def indicator_create(request, requirement_id):
    requirement = get_object_or_404(GraduationRequirement, pk=requirement_id)

    if request.method == 'GET':
        form = RequirementIndicatorForm()
        return render(
            request,
            'accreditation/indicator_form.html',
            context={
                'form': form,
                'requirement': requirement,
                'page_title': '新增指标点',
            }
        )

    form = RequirementIndicatorForm(request.POST)
    if form.is_valid():
        indicator = form.save(commit=False)
        indicator.graduation_requirement = requirement
        indicator.save()
        return redirect('accreditation:requirement_detail', requirement_id=requirement.id)

    return render(
        request,
        'accreditation/indicator_form.html',
        context={
            'form': form,
            'requirement': requirement,
            'page_title': '新增指标点',
        }
    )


# 编辑指标点
@login_required
def indicator_update(request, indicator_id):
    indicator = get_object_or_404(
        RequirementIndicator.objects.select_related('graduation_requirement'),
        pk=indicator_id
    )
    requirement = indicator.graduation_requirement

    if request.method == 'GET':
        form = RequirementIndicatorForm(instance=indicator)
        return render(
            request,
            'accreditation/indicator_form.html',
            context={
                'form': form,
                'requirement': requirement,
                'page_title': '编辑指标点',
            }
        )

    form = RequirementIndicatorForm(request.POST, instance=indicator)
    if form.is_valid():
        form.save()
        return redirect('accreditation:requirement_detail', requirement_id=requirement.id)

    return render(
        request,
        'accreditation/indicator_form.html',
        context={
            'form': form,
            'requirement': requirement,
            'page_title': '编辑指标点',
        }
    )


# 删除指标点
@login_required
def indicator_delete(request, indicator_id):
    indicator = get_object_or_404(
        RequirementIndicator.objects.select_related('graduation_requirement'),
        pk=indicator_id
    )
    requirement = indicator.graduation_requirement

    if request.method == 'POST':
        indicator.delete()
        return redirect('accreditation:requirement_detail', requirement_id=requirement.id)

    return render(
        request,
        'accreditation/indicator_confirm_delete.html',
        context={'indicator': indicator, 'requirement': requirement}
    )
