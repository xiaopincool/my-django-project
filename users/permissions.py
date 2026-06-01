def is_admin(user):
    return user.is_authenticated and getattr(user, 'role', '') == 'admin'


def is_teacher(user):
    return user.is_authenticated and getattr(user, 'role', '') == 'teacher'


def is_program(user):
    return user.is_authenticated and getattr(user, 'role', '') == 'program'


def role_label(user):
    role = getattr(user, 'role', '')
    if role == 'admin':
        return '管理员'
    if role == 'teacher':
        return '任课教师'
    if role == 'program':
        return '专业负责人'
    return '未分配'


def can_manage_requirement(user):
    return is_admin(user) or is_program(user)


def can_manage_course_obj(user, course):
    return is_admin(user) or is_program(user) or (is_teacher(user) and course.teacher_id == user.id)


def can_view_course_obj(user, course):
    return is_admin(user) or is_program(user) or (is_teacher(user) and course.teacher_id == user.id)
