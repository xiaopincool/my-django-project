from .dashboard_urls import urlpatterns as dashboard_urlpatterns
from .training_plan_urls import urlpatterns as training_plan_urlpatterns
from .student_urls import urlpatterns as student_urlpatterns
from .teacher_urls import urlpatterns as teacher_urlpatterns
from .system_urls import urlpatterns as system_urlpatterns
from .requirement_urls import urlpatterns as requirement_urlpatterns
from .course_urls import urlpatterns as course_urlpatterns
from .attainment_urls import urlpatterns as attainment_urlpatterns
from .matrix_urls import urlpatterns as matrix_urlpatterns
from .improvement_urls import urlpatterns as improvement_urlpatterns

app_name = 'accreditation'

urlpatterns = []
urlpatterns += dashboard_urlpatterns
urlpatterns += training_plan_urlpatterns
urlpatterns += student_urlpatterns
urlpatterns += teacher_urlpatterns
urlpatterns += system_urlpatterns
urlpatterns += requirement_urlpatterns
urlpatterns += course_urlpatterns
urlpatterns += attainment_urlpatterns
urlpatterns += matrix_urlpatterns
urlpatterns += improvement_urlpatterns
