from urllib.parse import urlencode

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme

from ..forms import ContinuousImprovementForm
from ..models import ContinuousImprovement, CourseAttainmentRecord


# 处理安全回跳地址
def get_safe_next_url(request, default_url=''):
    next_url = request.POST.get('next_url') or request.GET.get('next_url') or ''
    if next_url and url_has_allowed_host_and_scheme(
        url=next_url,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return next_url
    return default_url


# 持续改进列表，支持按关键词、状态、来源筛选
@login_required
def improvement_list(request):
    q = request.GET.get('q', '').strip()
    status = request.GET.get('status', '').strip()
    source = request.GET.get('source', '').strip()

    items = ContinuousImprovement.objects.select_related(
        'course',
        'responsible_person',
        'creator',
        'attainment_record',
    ).all()

    if q:
        items = items.filter(
            Q(title__icontains=q) |
            Q(problem_description__icontains=q) |
            Q(improvement_measure__icontains=q)
        )

    if status:
        items = items.filter(status=status)

    if source:
        items = items.filter(source=source)

    context = {
        'items': items,
        'q': q,
        'status': status,
        'source': source,
        'status_choices': ContinuousImprovement.STATUS_CHOICES,
        'source_choices': ContinuousImprovement.SOURCE_CHOICES,
    }
    return render(request, 'accreditation/improvement_list.html', context=context)


# 列表页新增入口
@login_required
def improvement_entry(request):
    next_url = get_safe_next_url(request, reverse('accreditation:improvement_list'))

    if request.method == 'GET':
        form = ContinuousImprovementForm()
        return render(
            request,
            'accreditation/improvement_form.html',
            context={
                'form': form,
                'page_title': '新增整改项',
                'next_url': next_url,
            }
        )

    return improvement_create(request)


# 新增整改项
@login_required
def improvement_create(request):
    next_url = get_safe_next_url(request, reverse('accreditation:improvement_list'))

    if request.method == 'GET':
        form = ContinuousImprovementForm()
        return render(
            request,
            'accreditation/improvement_form.html',
            context={
                'form': form,
                'page_title': '新增整改项',
                'next_url': next_url,
            }
        )

    form = ContinuousImprovementForm(request.POST)
    if form.is_valid():
        item = form.save(commit=False)
        item.creator = request.user
        item.save()
        messages.success(request, '整改项创建成功')
        return redirect(next_url or reverse('accreditation:improvement_detail', kwargs={'item_id': item.id}))

    return render(
        request,
        'accreditation/improvement_form.html',
        context={
            'form': form,
            'page_title': '新增整改项',
            'next_url': next_url,
        }
    )


# 根据达成度记录自动生成整改项
@login_required
def improvement_create_from_attainment(request, record_id):
    record = get_object_or_404(
        CourseAttainmentRecord.objects.select_related('course'),
        pk=record_id
    )

    # 已达成，不允许生成整改项
    if record.actual_value >= record.target_value:
        messages.info(request, '该达成度记录已达成，无需生成整改项')
        return redirect('accreditation:attainment_detail', record_id=record.id)

    # 从达成度生成整改项，保存后默认回达成度列表
    next_url = reverse('accreditation:attainment_list')

    # 已经生成过，则直接跳到编辑页，防止重复创建
    old_item = ContinuousImprovement.objects.filter(attainment_record=record).first()
    if old_item:
        messages.info(request, '该达成度记录已生成整改项，已为你跳转到编辑页')
        update_url = reverse('accreditation:improvement_update', kwargs={'item_id': old_item.id})
        return redirect('{}?{}'.format(update_url, urlencode({'next_url': next_url})))

    item = ContinuousImprovement.objects.create(
        title='【达成分析】{} {} {} 整改项'.format(
            record.course.name,
            record.academic_year,
            record.term
        ),
        source='attainment',
        course=record.course,
        attainment_record=record,
        problem_description=(
            '该整改项由达成度记录自动生成。\n'
            '课程：{}\n'
            '学年：{}\n'
            '学期：{}\n'
            '目标值：{}\n'
            '实际值：{}\n'
            '请结合本条达成度结果进一步补充具体问题描述。'
        ).format(
            record.course.name,
            record.academic_year,
            record.term,
            record.target_value,
            record.actual_value
        ),
        improvement_measure='请结合课程目标达成情况、考核方式、教学内容、支撑材料和学生反馈，完善整改措施。',
        responsible_person=request.user,
        status='pending',
        progress=0,
        creator=request.user,
        remark='由达成度记录 #{} 自动生成'.format(record.id)
    )
    messages.success(request, '整改项已自动生成，请继续完善内容')
    update_url = reverse('accreditation:improvement_update', kwargs={'item_id': item.id})
    return redirect('{}?{}'.format(update_url, urlencode({'next_url': next_url})))


# 整改项详情
@login_required
def improvement_detail(request, item_id):
    item = get_object_or_404(
        ContinuousImprovement.objects.select_related(
            'course',
            'responsible_person',
            'creator',
            'attainment_record',
        ),
        pk=item_id
    )
    return render(
        request,
        'accreditation/improvement_detail.html',
        context={'item': item}
    )


# 编辑整改项
@login_required
def improvement_update(request, item_id):
    item = get_object_or_404(ContinuousImprovement, pk=item_id)
    default_next_url = reverse('accreditation:improvement_detail', kwargs={'item_id': item.id})
    next_url = get_safe_next_url(request, default_next_url)

    if request.method == 'GET':
        form = ContinuousImprovementForm(instance=item)
        return render(
            request,
            'accreditation/improvement_form.html',
            context={
                'form': form,
                'page_title': '编辑整改项',
                'item': item,
                'next_url': next_url,
            }
        )

    form = ContinuousImprovementForm(request.POST, instance=item)
    if form.is_valid():
        form.save()
        messages.success(request, '整改项修改成功')
        return redirect(next_url)

    return render(
        request,
        'accreditation/improvement_form.html',
        context={
            'form': form,
            'page_title': '编辑整改项',
            'item': item,
            'next_url': next_url,
        }
    )


# 删除整改项
@login_required
def improvement_delete(request, item_id):
    item = get_object_or_404(
        ContinuousImprovement.objects.select_related(
            'course',
            'responsible_person',
            'creator',
            'attainment_record',
        ),
        pk=item_id
    )

    if request.method == 'POST':
        item.delete()
        messages.success(request, '整改项删除成功')
        return redirect('accreditation:improvement_list')

    return render(
        request,
        'accreditation/improvement_confirm_delete.html',
        context={'item': item}
    )