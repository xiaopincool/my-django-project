from collections import defaultdict
from datetime import datetime
from datetime import date
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from io import BytesIO
import re
from urllib.parse import urlencode, quote
from xml.sax.saxutils import escape
import zipfile

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import OperationalError, ProgrammingError, transaction
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse

from ..models import (
    Course,
    CourseAttainmentRecord,
    CourseIndicatorRelation,
    GraduationRequirement,
    Student,
    TrainingPlan,
)


PASS_LINE = Decimal('0.70')
DEFAULT_TOTAL_SCORE = Decimal('100')
DISPLAY_STEP = Decimal('0.01')


def _quantize(value):
    return Decimal(value).quantize(DISPLAY_STEP, rounding=ROUND_HALF_UP)


def _format_decimal(value):
    if value is None:
        return '--'
    return format(_quantize(value), 'f')


def _format_input_decimal(value):
    if value is None:
        return ''
    text = format(_quantize(value), 'f')
    if text.endswith('.00'):
        return text[:-3]
    if text.endswith('0'):
        return text[:-1]
    return text


def _get_attainment_status(value):
    if value is None:
        return 'pending'
    if value >= PASS_LINE:
        return 'ok'
    return 'bad'


def _to_decimal(raw_value, default=None):
    text = str(raw_value or '').strip()
    if not text:
        return default
    try:
        return Decimal(text)
    except (InvalidOperation, TypeError, ValueError):
        return default


def _append_unique(target, values):
    for item in values:
        if item and item not in target:
            target.append(item)


def _ensure_selected(options, selected_value):
    if selected_value and selected_value not in options:
        options.append(selected_value)


def _code_sort_key(code):
    text = (code or '').strip()
    nums = [int(item) for item in re.findall(r'\d+', text)]
    prefix = re.sub(r'\d+', '', text).lower()
    return prefix, nums, text.lower()


def _get_default_cycle():
    latest_record = CourseAttainmentRecord.objects.order_by('-id').first()
    if latest_record:
        return latest_record.academic_year, latest_record.term

    today = date.today()
    start_year = today.year if today.month >= 9 else today.year - 1
    return '%s-%s' % (start_year, start_year + 1), '第一学期'


def _build_record_qs(selected):
    record_qs = CourseAttainmentRecord.objects.all()

    if selected['academic_year']:
        record_qs = record_qs.filter(academic_year=selected['academic_year'])
    if selected['college_name']:
        record_qs = record_qs.filter(college_name=selected['college_name'])
    if selected['major_name']:
        record_qs = record_qs.filter(major_name=selected['major_name'])
    if selected['grade_name']:
        record_qs = record_qs.filter(grade_name=selected['grade_name'])
    if selected['class_name']:
        record_qs = record_qs.filter(class_name=selected['class_name'])

    return record_qs


def _build_exact_record_qs(selected):
    return CourseAttainmentRecord.objects.filter(
        college_name=selected['college_name'],
        major_name=selected['major_name'],
        grade_name=selected['grade_name'],
        class_name=selected['class_name'],
        academic_year=selected['academic_year'],
    )


def _pick_course_record(record_qs, course, selected):
    course_qs = record_qs.filter(course_id=course.id).order_by('-id')
    if not course_qs.exists():
        return None

    if selected['term']:
        row = course_qs.filter(term=selected['term']).first()
        if row:
            return row

    if course.term:
        row = course_qs.filter(term=course.term).first()
        if row:
            return row

    return course_qs.first()


def _get_result_text(target_value, actual_value):
    if actual_value >= target_value:
        return '已达成'
    return '未达成'


def _build_return_url(selected):
    base_url = reverse('accreditation:attainment_list')
    query_data = {}

    for key in [
        'college_name',
        'major_name',
        'grade_name',
        'class_name',
        'academic_year',
        'term',
    ]:
        if selected.get(key):
            query_data[key] = selected[key]

    if not query_data:
        return base_url

    return '%s?%s' % (base_url, urlencode(query_data))


def _xlsx_col_name(col_num):
    result = []

    while col_num > 0:
        col_num, rem = divmod(col_num - 1, 26)
        result.append(chr(65 + rem))

    return ''.join(reversed(result))


def _xlsx_cell_xml(row_num, col_num, value):
    cell_ref = '%s%s' % (_xlsx_col_name(col_num), row_num)

    if value is None or value == '':
        return '<c r="%s"/>' % cell_ref

    if isinstance(value, Decimal):
        return '<c r="%s"><v>%s</v></c>' % (cell_ref, format(value, 'f'))

    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return '<c r="%s"><v>%s</v></c>' % (cell_ref, value)

    return '<c r="%s" t="inlineStr"><is><t>%s</t></is></c>' % (
        cell_ref,
        escape(str(value)),
    )


def _xlsx_sheet_xml(rows):
    parts = [
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
        '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">',
        '<sheetData>',
    ]

    for row_num, row in enumerate(rows, start=1):
        parts.append('<row r="%s">' % row_num)
        for col_num, value in enumerate(row, start=1):
            parts.append(_xlsx_cell_xml(row_num, col_num, value))
        parts.append('</row>')

    parts.extend([
        '</sheetData>',
        '</worksheet>',
    ])
    return ''.join(parts)


def _build_export_sheets(selected, selected_label, course_rows, result_cards):
    export_cards = [item for item in result_cards if not item['is_placeholder']]

    overview_rows = [
        ['达成分析导出'],
        ['导出范围', selected_label or '未指定'],
        ['学院', selected['college_name'] or '全部'],
        ['专业', selected['major_name'] or '全部'],
        ['年级', selected['grade_name'] or '全部'],
        ['班级', selected['class_name'] or '全部'],
        ['学年', selected['academic_year'] or '未指定'],
        ['学期', selected['term'] or '未指定'],
        ['达成判定线', _format_decimal(PASS_LINE)],
        [],
        ['毕业要求编号', '毕业要求名称', '综合达成值', '最低指标点值', '最终结果', '指标点数量', '提示数量', '判定规则'],
    ]

    for card in export_cards:
        overview_rows.append([
            card['code'],
            card['name'],
            card['comprehensive_text'],
            card['min_text'],
            card['status_text'],
            card['indicator_count'],
            card['warning_count'],
            card['status_rule_text'],
        ])

    course_rows_data = [
        ['课程名称', '课程编号', '支撑指标点数', '平均分', '总分', '课程达成值', '来源', '说明'],
    ]
    for row in course_rows:
        course_rows_data.append([
            row['course_name'],
            row['course_code'],
            row['support_count'],
            row['average_score_raw'] or '',
            row['total_score_raw'] or '',
            row['attainment_text'],
            row['source_text'],
            row['source_note'],
        ])

    indicator_rows = [
        ['毕业要求编号', '毕业要求名称', '指标点编号', '指标点内容', '指标点达成值', '权重和', '详细计算过程', '指标点提示'],
    ]
    course_detail_rows = [
        ['毕业要求编号', '指标点编号', '支撑课程', '课程编号', '平均分', '总分', '课程达成值', '权重', '计算结果', '支撑强度'],
    ]

    for card in export_cards:
        for indicator in card['indicator_results']:
            indicator_rows.append([
                card['code'],
                card['name'],
                indicator['code'],
                indicator['content'],
                indicator['value_text'],
                indicator['weight_sum_text'],
                indicator['formula_text'],
                '；'.join(indicator['warning_list']) if indicator['warning_list'] else '',
            ])

            for item in indicator['line_items']:
                course_detail_rows.append([
                    card['code'],
                    indicator['code'],
                    item['course_name'],
                    item['course_code'],
                    item['average_score_text'],
                    item['total_score_text'],
                    item['course_value_text'],
                    item['weight_text'],
                    item['product_text'],
                    item['support_level_text'],
                ])

    return [
        ('分析概览', overview_rows),
        ('课程成绩', course_rows_data),
        ('指标点明细', indicator_rows),
        ('课程支撑明细', course_detail_rows),
    ]


def _build_xlsx_file(sheet_rows):
    buf = BytesIO()

    workbook_xml = [
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
        '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
        'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">',
        '<sheets>',
    ]

    workbook_rels = [
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">',
    ]

    content_types = [
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">',
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>',
        '<Default Extension="xml" ContentType="application/xml"/>',
        '<Override PartName="/xl/workbook.xml" '
        'ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>',
        '<Override PartName="/docProps/core.xml" '
        'ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>',
        '<Override PartName="/docProps/app.xml" '
        'ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>',
    ]

    with zipfile.ZipFile(buf, 'w', zipfile.ZIP_DEFLATED) as zf:
        for idx, (sheet_name, rows) in enumerate(sheet_rows, start=1):
            workbook_xml.append(
                '<sheet name="%s" sheetId="%s" r:id="rId%s"/>'
                % (escape(sheet_name), idx, idx)
            )
            workbook_rels.append(
                '<Relationship Id="rId%s" '
                'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" '
                'Target="worksheets/sheet%s.xml"/>'
                % (idx, idx)
            )
            content_types.append(
                '<Override PartName="/xl/worksheets/sheet%s.xml" '
                'ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
                % idx
            )
            zf.writestr('xl/worksheets/sheet%s.xml' % idx, _xlsx_sheet_xml(rows))

        workbook_xml.extend(['</sheets>', '</workbook>'])
        workbook_rels.append('</Relationships>')
        content_types.append('</Types>')

        now_text = datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')

        zf.writestr(
            '[Content_Types].xml',
            ''.join(content_types),
        )
        zf.writestr(
            '_rels/.rels',
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>'
            '<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>'
            '<Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" Target="docProps/app.xml"/>'
            '</Relationships>',
        )
        zf.writestr('xl/workbook.xml', ''.join(workbook_xml))
        zf.writestr('xl/_rels/workbook.xml.rels', ''.join(workbook_rels))
        zf.writestr(
            'docProps/app.xml',
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties" '
            'xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes">'
            '<Application>EngCer</Application>'
            '</Properties>',
        )
        zf.writestr(
            'docProps/core.xml',
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" '
            'xmlns:dc="http://purl.org/dc/elements/1.1/" '
            'xmlns:dcterms="http://purl.org/dc/terms/" '
            'xmlns:dcmitype="http://purl.org/dc/dcmitype/" '
            'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">'
            '<dc:creator>EngCer</dc:creator>'
            '<cp:lastModifiedBy>EngCer</cp:lastModifiedBy>'
            '<dcterms:created xsi:type="dcterms:W3CDTF">%s</dcterms:created>'
            '<dcterms:modified xsi:type="dcterms:W3CDTF">%s</dcterms:modified>'
            '</cp:coreProperties>'
            % (now_text, now_text),
        )

    return buf.getvalue()


def _export_analysis_file(selected, selected_label, course_rows, result_cards):
    sheet_rows = _build_export_sheets(selected, selected_label, course_rows, result_cards)
    file_bytes = _build_xlsx_file(sheet_rows)

    name_parts = ['达成分析结果']
    for item in [
        selected.get('major_name'),
        selected.get('grade_name'),
        selected.get('class_name'),
        selected.get('academic_year'),
        selected.get('term'),
    ]:
        if item:
            name_parts.append(item)

    file_name = '%s.xlsx' % '_'.join(name_parts)

    response = HttpResponse(
        file_bytes,
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )
    response['Content-Disposition'] = "attachment; filename*=UTF-8''%s" % quote(file_name)
    return response


def _build_filter_options(selected):
    college_options = []
    major_options = []
    grade_options = []
    class_options = []

    try:
        plan_base = TrainingPlan.objects.filter(is_active=True)
        _append_unique(
            college_options,
            plan_base.order_by('college_name').values_list('college_name', flat=True).distinct(),
        )

        plan_major_qs = plan_base
        if selected['college_name']:
            plan_major_qs = plan_major_qs.filter(college_name=selected['college_name'])
        _append_unique(
            major_options,
            plan_major_qs.order_by('major_name').values_list('major_name', flat=True).distinct(),
        )
    except (OperationalError, ProgrammingError):
        pass

    try:
        student_base = Student.objects.all()
        _append_unique(
            college_options,
            student_base.order_by('college_name').values_list('college_name', flat=True).distinct(),
        )

        student_major_qs = student_base
        if selected['college_name']:
            student_major_qs = student_major_qs.filter(college_name=selected['college_name'])
        _append_unique(
            major_options,
            student_major_qs.order_by('major_name').values_list('major_name', flat=True).distinct(),
        )

        student_grade_qs = student_base
        if selected['college_name']:
            student_grade_qs = student_grade_qs.filter(college_name=selected['college_name'])
        if selected['major_name']:
            student_grade_qs = student_grade_qs.filter(major_name=selected['major_name'])
        _append_unique(
            grade_options,
            student_grade_qs.order_by('grade_name').values_list('grade_name', flat=True).distinct(),
        )

        student_class_qs = student_grade_qs
        if selected['grade_name']:
            student_class_qs = student_class_qs.filter(grade_name=selected['grade_name'])
        _append_unique(
            class_options,
            student_class_qs.order_by('class_name').values_list('class_name', flat=True).distinct(),
        )
    except (OperationalError, ProgrammingError):
        pass

    _ensure_selected(college_options, selected['college_name'])
    _ensure_selected(major_options, selected['major_name'])
    _ensure_selected(grade_options, selected['grade_name'])
    _ensure_selected(class_options, selected['class_name'])

    college_options.sort()
    major_options.sort()
    grade_options.sort()
    class_options.sort()

    academic_year_options = list(
        CourseAttainmentRecord.objects.order_by('-academic_year')
        .values_list('academic_year', flat=True)
        .distinct()
    )

    today = date.today()
    start_year = today.year if today.month >= 9 else today.year - 1
    _append_unique(academic_year_options, [
        '%s-%s' % (start_year, start_year + 1),
        '%s-%s' % (start_year - 1, start_year),
        '%s-%s' % (start_year - 2, start_year - 1),
    ])
    _ensure_selected(academic_year_options, selected['academic_year'])

    term_options = []
    _append_unique(term_options, ['第一学期', '第二学期', '第三学期'])
    _append_unique(
        term_options,
        CourseAttainmentRecord.objects.order_by('term').values_list('term', flat=True).distinct(),
    )
    _ensure_selected(term_options, selected['term'])

    return {
        'college_options': academic_year_options and college_options or college_options,
        'major_options': major_options,
        'grade_options': grade_options,
        'class_options': class_options,
        'academic_year_options': academic_year_options,
        'term_options': term_options,
    }


def _get_analysis_courses():
    course_ids = list(
        CourseIndicatorRelation.objects.values_list('course_id', flat=True).distinct()
    )
    relation_rows = CourseIndicatorRelation.objects.select_related(
        'course',
        'indicator',
        'indicator__graduation_requirement',
    ).order_by(
        'indicator__graduation_requirement__code',
        'indicator__sort',
        'course__code',
        'id',
    )

    relation_map = defaultdict(list)
    support_count_map = defaultdict(int)
    for row in relation_rows:
        relation_map[row.indicator_id].append(row)
        support_count_map[row.course_id] += 1

    course_qs = Course.objects.filter(is_active=True).order_by('code', 'id')
    if course_ids:
        course_qs = course_qs.filter(id__in=course_ids)

    return list(course_qs), relation_map, support_count_map


def _get_record_prefill_map(selected):
    if not selected['academic_year']:
        return {}

    return _build_record_qs(selected)


def _build_prefill_rows(courses, support_count_map, selected):
    record_qs = _get_record_prefill_map(selected)
    rows = []

    for course in courses:
        record = _pick_course_record(record_qs, course, selected)
        average_score = None
        total_score = DEFAULT_TOTAL_SCORE
        source_text = '手工录入'
        source_note = '当前页面支持直接录入班级平均分。'

        if record:
            if record.average_score is not None:
                average_score = _quantize(record.average_score)
            else:
                average_score = _quantize(record.actual_value * DEFAULT_TOTAL_SCORE)

            if record.total_score:
                total_score = _quantize(record.total_score)

            source_text = '系统已保存'
            source_note = '已按当前筛选范围下的系统记录自动回填。'

        attainment_value = None
        has_score = average_score is not None
        if has_score and total_score > 0:
            attainment_value = _quantize(average_score / total_score)

        rows.append({
            'course': course,
            'course_id': course.id,
            'course_code': course.code,
            'course_name': course.name,
            'average_score': average_score,
            'average_score_raw': _format_input_decimal(average_score),
            'total_score': total_score,
            'total_score_raw': _format_input_decimal(total_score),
            'attainment_value': attainment_value,
            'attainment_text': _format_decimal(attainment_value),
            'attainment_status': _get_attainment_status(attainment_value),
            'has_score': has_score,
            'source_text': source_text,
            'source_note': source_note,
            'support_count': support_count_map.get(course.id, 0),
            'row_warnings': [],
        })
    return rows


def _build_rows_from_post(request, courses, support_count_map):
    course_map = {}
    for course in courses:
        course_map[str(course.id)] = course

    rows = []
    course_ids = request.POST.getlist('course_id')
    average_scores = request.POST.getlist('average_score')
    total_scores = request.POST.getlist('total_score')

    for index, course_id in enumerate(course_ids):
        course = course_map.get(course_id)
        if course is None:
            continue

        average_score_raw = ''
        total_score_raw = ''
        if index < len(average_scores):
            average_score_raw = average_scores[index].strip()
        if index < len(total_scores):
            total_score_raw = total_scores[index].strip()

        average_score = _to_decimal(average_score_raw, None)
        total_score = _to_decimal(total_score_raw, DEFAULT_TOTAL_SCORE)
        row_warnings = []

        if total_score is None or total_score <= 0:
            row_warnings.append('总分必须大于 0，当前已按 100 处理。')
            total_score = DEFAULT_TOTAL_SCORE

        if average_score is not None and average_score < 0:
            row_warnings.append('平均分不能小于 0，当前按 0 处理。')
            average_score = Decimal('0')

        if average_score is not None and total_score and average_score > total_score:
            row_warnings.append('平均分大于总分，请再核对一下成绩。')

        attainment_value = None
        has_score = average_score is not None
        if has_score and total_score > 0:
            attainment_value = _quantize(average_score / total_score)

        rows.append({
            'course': course,
            'course_id': course.id,
            'course_code': course.code,
            'course_name': course.name,
            'average_score': average_score,
            'average_score_raw': average_score_raw,
            'total_score': total_score,
            'total_score_raw': _format_input_decimal(total_score),
            'attainment_value': attainment_value,
            'attainment_text': _format_decimal(attainment_value),
            'attainment_status': _get_attainment_status(attainment_value),
            'has_score': has_score,
            'source_text': '手工录入',
            'source_note': '当前结果按页面录入的平均分即时换算。',
            'support_count': support_count_map.get(course.id, 0),
            'row_warnings': row_warnings,
        })

    return rows


def _save_course_rows(selected, course_rows, user):
    save_rows = [row for row in course_rows if row['has_score']]

    if not save_rows:
        return {
            'saved_count': 0,
            'created_count': 0,
            'updated_count': 0,
        }

    created_count = 0
    updated_count = 0

    with transaction.atomic():
        for row in save_rows:
            record_qs = _build_exact_record_qs(selected)
            record = _pick_course_record(record_qs, row['course'], selected)

            if record is None:
                record = CourseAttainmentRecord(course=row['course'])
                created_count += 1
            else:
                updated_count += 1

            record.college_name = selected['college_name']
            record.major_name = selected['major_name']
            record.grade_name = selected['grade_name']
            record.class_name = selected['class_name']
            record.academic_year = selected['academic_year']
            record.term = row['course'].term or selected['term']
            record.average_score = row['average_score']
            record.total_score = row['total_score']
            record.target_value = PASS_LINE
            record.actual_value = row['attainment_value'] or Decimal('0')
            record.conclusion = _get_result_text(record.target_value, record.actual_value)
            if not record.remark:
                record.remark = '由达成情况分析页录入的班级课程平均分。'
            record.creator = user
            record.save()

    return {
        'saved_count': len(save_rows),
        'created_count': created_count,
        'updated_count': updated_count,
    }


def _unique_messages(message_list):
    result = []
    for item in message_list:
        if item and item not in result:
            result.append(item)
    return result


def _build_requirement_results(course_rows, relation_map):
    requirements = list(
        GraduationRequirement.objects.filter(is_active=True)
        .prefetch_related('indicators')
        .order_by('id')
    )
    requirements.sort(key=lambda item: _code_sort_key(item.code))

    row_map = {}
    for row in course_rows:
        row_map[row['course_id']] = row

    has_score_data = any(row['has_score'] for row in course_rows)
    result_cards = []

    for index, requirement in enumerate(requirements, start=1):
        indicator_rows = list(requirement.indicators.filter(is_active=True).order_by('sort', 'id'))
        requirement_warnings = []
        indicator_results = []

        for indicator in indicator_rows:
            indicator_relations = relation_map.get(indicator.id, [])
            indicator_warnings = []
            line_items = []
            weight_sum = Decimal('0')

            for relation in indicator_relations:
                course_row = row_map.get(relation.course_id)
                weight_value = _quantize(relation.weight or Decimal('0'))
                weight_sum += weight_value

                is_missing_score = True
                course_value_for_calc = Decimal('0')
                course_value_text = '待录入'
                average_score_text = '--'
                total_score_text = _format_decimal(DEFAULT_TOTAL_SCORE)
                product_value = Decimal('0')
                product_text = '待计算'

                if course_row:
                    total_score_text = _format_decimal(course_row['total_score'])
                    if course_row['has_score']:
                        is_missing_score = False
                        course_value_for_calc = course_row['attainment_value'] or Decimal('0')
                        course_value_text = _format_decimal(course_value_for_calc)
                        average_score_text = _format_decimal(course_row['average_score'])
                        product_value = _quantize(course_value_for_calc * weight_value)
                        product_text = _format_decimal(product_value)
                    else:
                        indicator_warnings.append(
                            '%s 还没有录入平均分，当前按 0.00 计入。' % relation.course.name
                        )
                        product_text = '0.00'

                    indicator_warnings.extend(course_row['row_warnings'])
                else:
                    indicator_warnings.append(
                        '%s 没有出现在当前成绩录入区，当前按 0.00 计入。' % relation.course.name
                    )
                    product_text = '0.00'

                line_items.append({
                    'course_name': relation.course.name,
                    'course_code': relation.course.code,
                    'average_score_text': average_score_text,
                    'total_score_text': total_score_text,
                    'course_value_text': course_value_text,
                    'weight_text': _format_decimal(weight_value),
                    'product_value': product_value,
                    'product_text': product_text,
                    'support_level_text': relation.get_support_level_display(),
                    'is_missing_score': is_missing_score,
                })

            if not indicator_relations:
                indicator_warnings.append('当前指标点还没有配置支撑课程。')

            if indicator_relations and abs(weight_sum - Decimal('1.00')) > Decimal('0.01'):
                indicator_warnings.append(
                    '当前指标点权重和为 %s，不等于 1.00。' % _format_decimal(weight_sum)
                )

            if has_score_data:
                if indicator_relations:
                    indicator_value = _quantize(
                        sum(item['product_value'] for item in line_items)
                    )
                    formula_parts = []
                    for item in line_items:
                        if item['is_missing_score']:
                            formula_parts.append('0.00 × %s' % item['weight_text'])
                        else:
                            formula_parts.append('%s × %s' % (
                                item['course_value_text'],
                                item['weight_text'],
                            ))
                    formula_text = '%s = %s' % (
                        ' + '.join(formula_parts),
                        _format_decimal(indicator_value),
                    ) if formula_parts else '当前没有支撑课程，按 0.00 处理'
                else:
                    indicator_value = Decimal('0')
                    formula_text = '当前没有支撑课程，按 0.00 处理'
            else:
                indicator_value = None
                formula_text = '录入课程平均分后自动计算。'

            indicator_results.append({
                'key': 'indicator-%s' % indicator.id,
                'code': indicator.code,
                'content': indicator.content,
                'value': indicator_value,
                'value_text': _format_decimal(indicator_value),
                'line_items': line_items,
                'formula_text': formula_text,
                'weight_sum_text': _format_decimal(weight_sum) if indicator_relations else '--',
                'warning_list': _unique_messages(indicator_warnings),
            })

            requirement_warnings.extend(indicator_warnings)

        requirement_warnings = _unique_messages(requirement_warnings)

        if not indicator_rows:
            requirement_warnings.append('当前毕业要求还没有配置指标点。')

        if has_score_data and indicator_rows:
            indicator_values = [
                item['value'] if item['value'] is not None else Decimal('0')
                for item in indicator_results
            ]
            comprehensive_value = _quantize(
                sum(indicator_values) / Decimal(len(indicator_values))
            )
            min_value = min(indicator_values)
            comprehensive_formula = '(%s) / %s = %s' % (
                ' + '.join(_format_decimal(item) for item in indicator_values),
                len(indicator_values),
                _format_decimal(comprehensive_value),
            )
            min_formula = 'min(%s) = %s' % (
                ', '.join(_format_decimal(item) for item in indicator_values),
                _format_decimal(min_value),
            )
            is_reached = comprehensive_value >= PASS_LINE and min_value >= PASS_LINE
            status_text = '达成' if is_reached else '未达成'
            status_class = 'ok' if is_reached else 'bad'
            status_rule_text = (
                '综合达成值和最低指标点值是否都大于等于 %s 即为达成。'
                % _format_decimal(PASS_LINE)
            )
        elif indicator_rows:
            comprehensive_value = None
            min_value = None
            comprehensive_formula = '录入课程平均分后自动计算。'
            min_formula = '录入课程平均分后自动计算。'
            status_text = '待计算'
            status_class = 'pending'
            status_rule_text = (
                '综合达成值和最低指标点值是否都大于等于 %s 即为达成。'
                % _format_decimal(PASS_LINE)
            )
        else:
            comprehensive_value = None
            min_value = None
            comprehensive_formula = '当前毕业要求还没有配置指标点。'
            min_formula = '当前毕业要求还没有配置指标点。'
            status_text = '待配置'
            status_class = 'empty'
            status_rule_text = '当前毕业要求还没有配置指标点，暂时无法判定最终结果。'

        result_cards.append({
            'detail_key': 'requirement-%s' % requirement.id,
            'code': requirement.code or ('GR%s' % index),
            'name': requirement.name or ('毕业要求%s' % index),
            'display_index': index,
            'indicator_count': len(indicator_rows),
            'indicator_results': indicator_results,
            'comprehensive_value': comprehensive_value,
            'comprehensive_text': _format_decimal(comprehensive_value),
            'comprehensive_formula': comprehensive_formula,
            'min_value': min_value,
            'min_text': _format_decimal(min_value),
            'min_formula': min_formula,
            'status_text': status_text,
            'status_class': status_class,
            'status_rule_text': status_rule_text,
            'warning_list': requirement_warnings,
            'warning_count': len(requirement_warnings),
            'is_placeholder': False,
        })

    if len(result_cards) < 12:
        start_index = len(result_cards) + 1
        for index in range(start_index, 13):
            result_cards.append({
                'detail_key': 'requirement-empty-%s' % index,
                'code': 'GR%s' % index,
                'name': '毕业要求%s' % index,
                'display_index': index,
                'indicator_count': 0,
                'indicator_results': [],
                'comprehensive_value': None,
                'comprehensive_text': '--',
                'comprehensive_formula': '当前系统还没有配置这个毕业要求。',
                'min_value': None,
                'min_text': '--',
                'min_formula': '当前系统还没有配置这个毕业要求。',
                'status_text': '未配置',
                'status_class': 'empty',
                'status_rule_text': '当前系统还没有配置这个毕业要求，暂时无法判定最终结果。',
                'warning_list': ['当前系统还没有配置这个毕业要求。'],
                'warning_count': 1,
                'is_placeholder': True,
            })

    default_detail_key = ''
    for row in result_cards:
        if not row['is_placeholder']:
            default_detail_key = row['detail_key']
            break
    if not default_detail_key and result_cards:
        default_detail_key = result_cards[0]['detail_key']

    return result_cards, default_detail_key, has_score_data


@login_required
def attainment_list(request):
    if request.method == 'GET':
        default_year, default_term = _get_default_cycle()
        selected = {
            'college_name': request.GET.get('college_name', '').strip(),
            'major_name': request.GET.get('major_name', '').strip(),
            'grade_name': request.GET.get('grade_name', '').strip(),
            'class_name': request.GET.get('class_name', '').strip(),
            'academic_year': request.GET.get('academic_year', '').strip() or default_year,
            'term': request.GET.get('term', '').strip() or default_term,
        }
        action_type = 'query'
    else:
        selected = {
            'college_name': request.POST.get('college_name', '').strip(),
            'major_name': request.POST.get('major_name', '').strip(),
            'grade_name': request.POST.get('grade_name', '').strip(),
            'class_name': request.POST.get('class_name', '').strip(),
            'academic_year': request.POST.get('academic_year', '').strip(),
            'term': request.POST.get('term', '').strip(),
        }
        action_type = request.POST.get('action_type', 'query').strip() or 'query'

    filter_options = _build_filter_options(selected)
    courses, relation_map, support_count_map = _get_analysis_courses()

    if request.method == 'POST' and action_type in ['calculate', 'save', 'export']:
        course_rows = _build_rows_from_post(request, courses, support_count_map)
    else:
        course_rows = _build_prefill_rows(courses, support_count_map, selected)

    if request.method == 'POST' and action_type == 'save':
        save_result = _save_course_rows(selected, course_rows, request.user)
        if save_result['saved_count']:
            messages.success(
                request,
                '已录入系统：%s 门课程，新增 %s 条，更新 %s 条。' % (
                    save_result['saved_count'],
                    save_result['created_count'],
                    save_result['updated_count'],
                )
            )
        else:
            messages.warning(request, '当前还没有可录入系统的课程平均分，请先填写成绩。')
        return redirect(_build_return_url(selected))

    result_cards, default_detail_key, has_score_data = _build_requirement_results(
        course_rows,
        relation_map,
    )

    selected_label_parts = []
    for item in [
        selected['college_name'],
        selected['major_name'],
        selected['grade_name'],
        selected['class_name'],
        selected['academic_year'],
        selected['term'],
    ]:
        if item:
            selected_label_parts.append(item)

    selected_label = ' / '.join(selected_label_parts)

    if request.method == 'POST' and action_type == 'export':
        return _export_analysis_file(
            selected,
            selected_label,
            course_rows,
            result_cards,
        )

    context = {
        'selected': selected,
        'action_type': action_type,
        'course_rows': course_rows,
        'course_count': len(course_rows),
        'filled_course_count': len([row for row in course_rows if row['has_score']]),
        'manual_course_count': len([
            row for row in course_rows
            if row['source_text'] == '手工录入' and row['has_score']
        ]),
        'prefill_course_count': len([
            row for row in course_rows
            if row['source_text'] == '系统已保存' and row['has_score']
        ]),
        'result_cards': result_cards,
        'default_detail_key': default_detail_key,
        'has_score_data': has_score_data,
        'pass_line': _format_decimal(PASS_LINE),
        'selected_label': selected_label,
    }
    context.update(filter_options)
    return render(request, 'accreditation/attainment_list.html', context)
