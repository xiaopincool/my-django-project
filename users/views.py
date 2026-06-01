from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_http_methods


def get_safe_next_url(request):
    next_url = (request.POST.get('next') or request.GET.get('next') or '').strip()
    if not next_url:
        return ''

    if url_has_allowed_host_and_scheme(
        next_url,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return next_url

    return ''


# 登录页面和登录提交
@require_http_methods(['GET', 'POST'])
def login_view(request):
    next_url = get_safe_next_url(request)

    def render_login_page(**context):
        page_context = {
            'selected_role': 'admin',
            'next_url': next_url,
        }
        page_context.update(context)
        return render(request, 'users/login.html', context=page_context)

    if request.user.is_authenticated:
        if next_url:
            return redirect(next_url)
        return redirect('index')

    if request.method == 'GET':
        return render_login_page()

    username = request.POST.get('username', '').strip()
    password = request.POST.get('password', '').strip()
    role = request.POST.get('role', '').strip()

    if not username or not password:
        return render_login_page(
            error='用户名和密码不能为空',
            username=username,
            selected_role=role or 'admin',
        )

    if role not in ['admin', 'teacher', 'program']:
        return render_login_page(
            error='请选择角色',
            username=username,
            selected_role='admin',
        )

    user = authenticate(request, username=username, password=password)
    if not user:
        return render_login_page(
            error='用户名或密码错误',
            username=username,
            selected_role=role,
        )

    if user.role != role:
        return render_login_page(
            error='该账号不属于你选择的角色',
            username=username,
            selected_role=role,
        )

    login(request, user)
    if next_url:
        return redirect(next_url)
    return redirect('index')


# 退出登录
@login_required
def logout_view(request):
    logout(request)
    return redirect('users:login')
