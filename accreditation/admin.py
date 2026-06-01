from django.contrib import admin
from .models import (
    GraduationRequirement,
    RequirementIndicator,
    Course,
    TrainingPlan,
    Student,
    CourseIndicatorRelation,
    CourseGoal,
    GoalIndicatorRelation,
    MaterialCategory,
    CourseMaterial,
    CourseAttainmentRecord,
    ContinuousImprovement,
)

# 毕业要求后台管理
@admin.register(GraduationRequirement)
class GraduationRequirementAdmin(admin.ModelAdmin):
    list_display = ['id', 'code', 'name', 'version', 'is_active', 'creator', 'create_time']
    list_filter = ['version', 'is_active']
    search_fields = ['code', 'name', 'content']


# 指标点后台管理
@admin.register(RequirementIndicator)
class RequirementIndicatorAdmin(admin.ModelAdmin):
    list_display = ['id', 'code', 'graduation_requirement', 'sort', 'is_active', 'create_time']
    list_filter = ['is_active', 'graduation_requirement']
    search_fields = ['code', 'content']


# 课程后台管理
@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['id', 'code', 'name', 'credit', 'course_type', 'term', 'teacher', 'is_active']
    list_filter = ['course_type', 'is_active']
    search_fields = ['code', 'name']


# 培养方案后台管理
@admin.register(TrainingPlan)
class TrainingPlanAdmin(admin.ModelAdmin):
    list_display = ['id', 'college_name', 'major_name', 'plan_year', 'is_active', 'creator', 'update_time']
    list_filter = ['college_name', 'major_name', 'plan_year', 'is_active']
    search_fields = ['college_name', 'major_name', 'remark']


# 学生后台管理
@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'student_no', 'college_name', 'major_name', 'grade_name', 'class_name', 'status']
    list_filter = ['college_name', 'major_name', 'grade_name', 'class_name', 'status']
    search_fields = ['name', 'student_no', 'mobile']


# 课程支撑关系后台管理
@admin.register(CourseIndicatorRelation)
class CourseIndicatorRelationAdmin(admin.ModelAdmin):
    list_display = ['id', 'course', 'indicator', 'support_level', 'weight', 'create_time']
    list_filter = ['support_level', 'course']
    search_fields = ['course__name', 'indicator__code']


# 课程目标后台管理
@admin.register(CourseGoal)
class CourseGoalAdmin(admin.ModelAdmin):
    list_display = ['id', 'course', 'code', 'sort']
    list_filter = ['course']
    search_fields = ['course__name', 'code', 'content']


# 目标支撑关系后台管理
@admin.register(GoalIndicatorRelation)
class GoalIndicatorRelationAdmin(admin.ModelAdmin):
    list_display = ['id', 'goal', 'indicator', 'weight', 'create_time']
    list_filter = ['goal__course']
    search_fields = ['goal__code', 'indicator__code']


# 材料分类后台管理
@admin.register(MaterialCategory)
class MaterialCategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'sort']


# 课程材料后台管理
@admin.register(CourseMaterial)
class CourseMaterialAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'course', 'category', 'status', 'uploader', 'create_time']
    list_filter = ['status', 'course', 'category']
    search_fields = ['title', 'description']


# 达成度记录后台管理
@admin.register(CourseAttainmentRecord)
class CourseAttainmentRecordAdmin(admin.ModelAdmin):
    list_display = ['id', 'course', 'academic_year', 'term', 'target_value', 'actual_value', 'creator', 'create_time']
    list_filter = ['course', 'academic_year', 'term']
    search_fields = ['course__name', 'academic_year', 'term']
# 持续改进后台管理
@admin.register(ContinuousImprovement)
class ContinuousImprovementAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'title',
        'source',
        'course',
        'attainment_record',
        'responsible_person',
        'progress',
        'status',
        'creator',
        'create_time',
    ]
    list_filter = ['source', 'status', 'course']
    search_fields = ['title', 'problem_description', 'improvement_measure']
