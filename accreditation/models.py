from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


# 毕业要求
class GraduationRequirement(models.Model):
    code = models.CharField(max_length=20, verbose_name='编号')
    name = models.CharField(max_length=100, verbose_name='名称')
    content = models.TextField(verbose_name='内容说明')
    version = models.CharField(max_length=50, verbose_name='版本', default='2024版')
    is_active = models.BooleanField(default=True, verbose_name='是否启用')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    creator = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='创建人'
    )

    def __str__(self):
        return '%s-%s' % (self.code, self.name)

    class Meta:
        verbose_name = '毕业要求'
        verbose_name_plural = verbose_name
        ordering = ['code']


# 指标点
class RequirementIndicator(models.Model):
    graduation_requirement = models.ForeignKey(
        GraduationRequirement,
        on_delete=models.CASCADE,
        related_name='indicators',
        verbose_name='所属毕业要求'
    )
    code = models.CharField(max_length=20, verbose_name='指标点编号')
    content = models.TextField(verbose_name='指标点内容')
    sort = models.PositiveIntegerField(default=1, verbose_name='排序值')
    is_active = models.BooleanField(default=True, verbose_name='是否启用')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    def __str__(self):
        return self.code

    class Meta:
        verbose_name = '指标点'
        verbose_name_plural = verbose_name
        ordering = ['graduation_requirement__code', 'sort', 'id']


# 课程
class Course(models.Model):
    COURSE_TYPE_CHOICES = (
        ('required', '必修'),
        ('elective', '选修'),
    )

    code = models.CharField(max_length=50, verbose_name='课程编号')
    name = models.CharField(max_length=100, verbose_name='课程名称')
    credit = models.DecimalField(max_digits=4, decimal_places=1, verbose_name='学分', default=0)
    course_type = models.CharField(
        max_length=20,
        choices=COURSE_TYPE_CHOICES,
        verbose_name='课程类型',
        default='required'
    )
    term = models.CharField(max_length=30, verbose_name='开课学期', blank=True, null=True)
    teacher = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='负责人'
    )
    is_active = models.BooleanField(default=True, verbose_name='是否启用')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '课程'
        verbose_name_plural = verbose_name
        ordering = ['code']


# 培养方案
class TrainingPlan(models.Model):
    college_name = models.CharField(max_length=100, verbose_name='学院')
    major_name = models.CharField(max_length=100, verbose_name='专业')
    plan_year = models.PositiveIntegerField(verbose_name='年份')
    plan_file = models.FileField(
        upload_to='training_plans/',
        blank=True,
        null=True,
        verbose_name='培养方案文件'
    )
    remark = models.TextField(blank=True, null=True, verbose_name='说明')
    is_active = models.BooleanField(default=True, verbose_name='是否启用')
    creator = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='创建人'
    )
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    @property
    def file_name(self):
        if not self.plan_file:
            return ''
        return self.plan_file.name.rsplit('/', 1)[-1]

    def __str__(self):
        return '%s-%s-%s' % (self.college_name, self.major_name, self.plan_year)

    class Meta:
        verbose_name = '培养方案'
        verbose_name_plural = verbose_name
        ordering = ['-plan_year', 'college_name', 'major_name', 'id']
        unique_together = ('college_name', 'major_name', 'plan_year')


# 学生基础信息
class Student(models.Model):
    STATUS_CHOICES = (
        ('studying', '在读'),
        ('suspended', '休学'),
        ('graduated', '毕业'),
    )

    GENDER_CHOICES = (
        ('male', '男'),
        ('female', '女'),
    )

    name = models.CharField(max_length=50, verbose_name='姓名')
    student_no = models.CharField(max_length=30, unique=True, verbose_name='学号')
    college_name = models.CharField(max_length=100, verbose_name='学院')
    major_name = models.CharField(max_length=100, verbose_name='专业')
    grade_name = models.CharField(max_length=30, verbose_name='年级')
    class_name = models.CharField(max_length=50, verbose_name='班级')
    gender = models.CharField(
        max_length=10,
        choices=GENDER_CHOICES,
        blank=True,
        null=True,
        verbose_name='性别'
    )
    mobile = models.CharField(max_length=20, blank=True, null=True, verbose_name='手机号')
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='studying',
        verbose_name='状态'
    )
    remark = models.TextField(blank=True, null=True, verbose_name='备注')
    creator = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='创建人'
    )
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    def __str__(self):
        return '%s-%s' % (self.student_no, self.name)

    class Meta:
        verbose_name = '学生'
        verbose_name_plural = verbose_name
        ordering = ['student_no', 'id']


# 课程支撑关系
class CourseIndicatorRelation(models.Model):
    SUPPORT_LEVEL_CHOICES = (
        ('high', '高'),
        ('middle', '中'),
        ('low', '低'),
    )

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='indicator_relations',
        verbose_name='课程'
    )
    indicator = models.ForeignKey(
        RequirementIndicator,
        on_delete=models.CASCADE,
        related_name='course_relations',
        verbose_name='指标点'
    )
    support_level = models.CharField(
        max_length=20,
        choices=SUPPORT_LEVEL_CHOICES,
        verbose_name='支撑强度',
        default='middle'
    )
    weight = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='权重', default=0)
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    def __str__(self):
        return '%s -> %s' % (self.course.name, self.indicator.code)

    class Meta:
        verbose_name = '课程支撑关系'
        verbose_name_plural = verbose_name
        ordering = ['course__code', 'indicator__code']


# 课程目标
class CourseGoal(models.Model):
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='goals',
        verbose_name='所属课程'
    )
    code = models.CharField(max_length=20, verbose_name='目标编号')
    content = models.TextField(verbose_name='目标内容')
    sort = models.PositiveIntegerField(default=1, verbose_name='排序值')

    def __str__(self):
        return '%s-%s' % (self.course.name, self.code)

    class Meta:
        verbose_name = '课程目标'
        verbose_name_plural = verbose_name
        ordering = ['course__code', 'sort', 'id']


# 目标支撑关系
class GoalIndicatorRelation(models.Model):
    goal = models.ForeignKey(
        CourseGoal,
        on_delete=models.CASCADE,
        related_name='indicator_relations',
        verbose_name='课程目标'
    )
    indicator = models.ForeignKey(
        RequirementIndicator,
        on_delete=models.CASCADE,
        related_name='goal_relations',
        verbose_name='指标点'
    )
    weight = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='权重', default=0)
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    def __str__(self):
        return '%s -> %s' % (self.goal.code, self.indicator.code)

    class Meta:
        verbose_name = '目标支撑关系'
        verbose_name_plural = verbose_name
        ordering = ['goal__course__code', 'goal__sort', 'indicator__code']


# 材料分类
class MaterialCategory(models.Model):
    name = models.CharField(max_length=100, verbose_name='分类名称')
    sort = models.PositiveIntegerField(default=1, verbose_name='排序值')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '材料分类'
        verbose_name_plural = verbose_name
        ordering = ['sort', 'id']


# 课程材料
class CourseMaterial(models.Model):
    STATUS_CHOICES = (
        ('draft', '草稿'),
        ('submitted', '已提交'),
        ('approved', '已通过'),
        ('rejected', '已退回'),
    )

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='materials',
        verbose_name='所属课程'
    )
    category = models.ForeignKey(
        MaterialCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='materials',
        verbose_name='材料分类'
    )
    title = models.CharField(max_length=200, verbose_name='材料标题')
    file = models.FileField(upload_to='materials/', blank=True, null=True, verbose_name='上传文件')
    description = models.TextField(blank=True, null=True, verbose_name='说明')
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft',
        verbose_name='审核状态'
    )
    uploader = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='上传人'
    )
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = '课程材料'
        verbose_name_plural = verbose_name
        ordering = ['-create_time']


# 课程达成度记录
class CourseAttainmentRecord(models.Model):
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='attainment_records',
        verbose_name='课程'
    )
    college_name = models.CharField(max_length=100, verbose_name='学院', blank=True, default='')
    major_name = models.CharField(max_length=100, verbose_name='专业', blank=True, default='')
    grade_name = models.CharField(max_length=30, verbose_name='年级', blank=True, default='')
    class_name = models.CharField(max_length=50, verbose_name='班级', blank=True, default='')
    academic_year = models.CharField(max_length=30, verbose_name='学年')
    term = models.CharField(max_length=30, verbose_name='学期')
    average_score = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        verbose_name='平均分',
        blank=True,
        null=True,
    )
    total_score = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        verbose_name='总分',
        default=100,
    )
    target_value = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='目标值', default=0)
    actual_value = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='实际达成值', default=0)
    conclusion = models.CharField(max_length=200, verbose_name='达成结论', blank=True, null=True)
    remark = models.TextField(verbose_name='备注', blank=True, null=True)
    creator = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='创建人'
    )
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    def __str__(self):
        return '%s-%s-%s-%s' % (
            self.course.name,
            self.academic_year,
            self.term,
            self.class_name or '未分班',
        )

    class Meta:
        verbose_name = '课程达成度记录'
        verbose_name_plural = verbose_name
        ordering = ['-create_time']


# 持续改进整改项
class ContinuousImprovement(models.Model):
    STATUS_CHOICES = (
        ('pending', '待处理'),
        ('in_progress', '进行中'),
        ('completed', '已完成'),
    )

    SOURCE_CHOICES = (
        ('attainment', '达成分析'),
        ('material', '材料检查'),
        ('course', '课程评估'),
        ('other', '其他'),
    )

    title = models.CharField(max_length=200, verbose_name='问题标题')
    source = models.CharField(
        max_length=30,
        choices=SOURCE_CHOICES,
        default='other',
        verbose_name='问题来源'
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name='关联课程'
    )
    attainment_record = models.ForeignKey(
        CourseAttainmentRecord,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='improvement_items',
        verbose_name='关联达成度记录'
    )
    problem_description = models.TextField(verbose_name='问题描述')
    improvement_measure = models.TextField(verbose_name='整改措施')
    responsible_person = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='improvement_items',
        verbose_name='责任人'
    )
    planned_finish_date = models.DateField(
        blank=True,
        null=True,
        verbose_name='计划完成时间'
    )
    progress = models.PositiveIntegerField(default=0, verbose_name='进度(%)')
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='整改状态'
    )
    effect_evaluation = models.TextField(blank=True, null=True, verbose_name='效果评价')
    remark = models.TextField(blank=True, null=True, verbose_name='备注')
    creator = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='created_improvement_items',
        verbose_name='创建人'
    )
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    def save(self, *args, **kwargs):
        if self.progress > 100:
            self.progress = 100
        if self.status == 'completed' and self.progress < 100:
            self.progress = 100
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = '持续改进'
        verbose_name_plural = verbose_name
        ordering = ['status', 'planned_finish_date', '-create_time']
