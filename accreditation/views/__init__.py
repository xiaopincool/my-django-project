from .dashboard import dashboard
from .training_plan_views import (
    training_plan_list,
    training_plan_create,
    training_plan_update,
)
from .student_manage_views import (
    student_list,
    student_create,
    student_detail,
    student_update,
    student_delete,
)
from .teacher_manage_views import (
    teacher_list,
    teacher_create,
    teacher_detail,
    teacher_update,
    teacher_delete,
)
from .system_manage_views import system_manage
from .requirement_views import (
    requirement_list,
    requirement_create,
    requirement_detail,
    requirement_update,
    requirement_delete,
    indicator_create,
    indicator_update,
    indicator_delete,
)
from .course_views import (
    course_list,
    course_create,
    course_detail,
    course_update,
    course_delete,
    relation_list,
    relation_entry,
    relation_create,
    relation_detail,
    relation_update,
    relation_delete,
)
from .attainment_analysis_views import attainment_list
from .attainment_views import (
    attainment_entry,
    attainment_create,
    attainment_detail,
    attainment_update,
    attainment_delete,
)
from .matrix_views import support_matrix
from .improvement_views import (
    improvement_list,
    improvement_entry,
    improvement_create,
    improvement_create_from_attainment,
    improvement_detail,
    improvement_update,
    improvement_delete,
)
