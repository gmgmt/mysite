import string
import random
import time
from django.urls import reverse
from django.shortcuts import render, redirect
from django.contrib import auth
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.core.mail import send_mail

from .forms import LoginForm, RegForm, ChangeNicknameForm, BindEmailForm, ChangePasswordForm, ForgotPasswordForm
from .models import Profile


def login_for_medal(request):
    login_form = LoginForm(request.POST)
    data = {}
    if login_form.is_valid():
        user = login_form.cleaned_data['user']
        auth.login(request, user)
        data['status'] = 'SUCCESS'
    else:
        data['status'] = 'ERROR'
    return JsonResponse(data)



def login(request):
    '''
    username = request.POST.get('username', '')
    password = request.POST.get('password', '')
    user = auth.authenticate(request, username=username, password=password)
    # 获取登陆之前的页面链接,如果获取不到返回首页,reverse()反向回去上一级
    referer = request.META.get('HTTP_REFERER', reverse('home'))
    if user is not None:
        auth.login(request, user)
        # Redirect to a success page.重定向到首页
        return redirect(referer)
        
    else:
        return render(request, 'error.html',{'message': '用户名或密码不正确'})
    '''

    if request.method == 'POST':
        # 提交数据
        # 带有提交数据的初始化对象
        login_form = LoginForm(request.POST)
        # 判断是否有效
        if login_form.is_valid():
            user = login_form.cleaned_data['user']
            auth.login(request, user)
            # 跳转到之前页面，如果没有from参数，跳转到首页
            return redirect(request.GET.get('from', reverse('home')))
    else:
        # 加载页面
        login_form = LoginForm()


    context = {}
    context['login_form'] = login_form
    return render(request, 'user/login.html', context)



def register(request):
    if request.method == 'POST':
        # 提交数据
        # 带有提交数据的初始化对象
        reg_form = RegForm(request.POST, request=request)
        # 判断是否有效
        if reg_form.is_valid():
            username = reg_form.cleaned_data['username']
            email = reg_form.cleaned_data['email']
            password = reg_form.cleaned_data['password']
            # 创建用户
            user = User.objects.create_user(username, email, password)
            user.save()
            # 清除session
            del request.session['register_code']
            # 登录用户
            user = auth.authenticate(username=username, password=password)
            auth.login(request, user)
            # 跳转到之前页面，如果没有from参数，跳转到首页
            return redirect(request.GET.get('from', reverse('home')))

    else:
        # 加载页面
        reg_form = RegForm()


    context = {}
    context['reg_form'] = reg_form
    return render(request, 'user/register.html', context)



def logout(request):
    auth.logout(request)
    # 跳转到之前页面，如果没有from参数，跳转到首页
    return redirect(request.GET.get('from', reverse('home')))




def user_info(request):
    context = {}
    return render(request, 'user/user_info.html', context)



def change_nickname(request):
    redirect_to = request.GET.get('from', reverse('home'))
    if request.method == 'POST':
        form = ChangeNicknameForm(request.POST, user=request.user)
        if form.is_valid():
            nickname_new = form.cleaned_data['nickname_new']
            profile, created = Profile.objects.get_or_create(user=request.user)
            profile.nickname = nickname_new
            profile.save()
            # 跳转到之前页面，如果没有from参数，跳转到首页
            return redirect(redirect_to)
    else:
        form = ChangeNicknameForm()
    context = {}
    context['page_title'] = '修改昵称'
    context['form_title'] = '修改昵称'
    context['submit_text'] = '修改'
    context['form'] = form
    context['return_back_url'] = redirect_to
    return render(request, 'user/form.html', context)



def bind_email(request):
    redirect_to = request.GET.get('from', reverse('home'))
    if request.method == 'POST':
        form = BindEmailForm(request.POST, request=request)
        if form.is_valid():
            # 获取email
            email = form.cleaned_data['email']
            request.user.email = email
            request.user.save()
            # 清除session
            del request.session['bind_email_code']
            # 跳转到之前页面，如果没有from参数，跳转到首页
            return redirect(redirect_to)
    else:
        form = BindEmailForm()
    context = {}
    context['page_title'] = '绑定邮箱'
    context['form_title'] = '绑定邮箱'
    context['submit_text'] = '绑定'
    context['form'] = form
    context['return_back_url'] = redirect_to
    return render(request, 'user/bind_email.html', context)


def send_verification_code(request):
    data = {}
    email = request.GET.get('email', '')
    send_for = request.GET.get('send_for', '')

    if email != '':
        # 生成验证码, sample()样本，取自哪里, 第二个参数生成多少位，第一个参数，前面是所有字母，后面是所有数字
        code = ''.join(random.sample(string.ascii_letters + string.digits, 4))
        now = int(time.time())
        send_code_time = request.session.get('send_code_time', 0)
        if now - send_code_time < 30:
            data['status'] = 'ERROR'
        else:
            # 储存验证码到session,默认有效期两周
            request.session[send_for] = code
            request.session['send_code_time'] = now
            
            # 发送邮件
            send_mail(
                # 邮件主题
                '绑定邮箱',
                # 内容 验证码
                '验证码： %s' % code,
                # 从哪儿发送过来
                '3386993382@qq.com',
                # 发到哪儿
                [email],
                # 是否忽略错误
                fail_silently=False,
            )
            data['status'] = 'SUCCESS'
    else:
        data['status'] = 'ERROR'
    return JsonResponse(data)



       


def change_password(request):
    redirect_to = reverse('home')
    if request.method == 'POST':
        form = ChangePasswordForm(request.POST, user=request.user)
        if form.is_valid():
            user = request.user
            old_password = form.cleaned_data['old_password']
            new_password = form.cleaned_data['new_password']
            user.set_password(new_password)
            user.save()
            auth.logout(request)
            return redirect(redirect_to)
    else:
        form = ChangePasswordForm()

    context = {}
    context['page_title'] = '修改密码'
    context['form_title'] = '修改密码'
    context['submit_text'] = '修改'
    context['form'] = form
    context['return_back_url'] = redirect_to
    return render(request, 'user/form.html', context)



def forgot_password(request):
    redirect_to = reverse('login')
    if request.method == 'POST':
        form = ForgotPasswordForm(request.POST, request=request)
        if form.is_valid():
            email = form.cleaned_data['email']
            new_password = form.cleaned_data['new_password']
            user = User.objects.get(email=email)
            user.set_password(new_password)
            user.save()
            # 清除session
            del request.session['forgot_password_code']
            return redirect(redirect_to)
    else:
        form = ForgotPasswordForm()

    context = {}
    context['page_title'] = '重置密码'
    context['form_title'] = '重置密码'
    context['submit_text'] = '重置'
    context['form'] = form
    context['return_back_url'] = redirect_to
    return render(request, 'user/forgot_password.html', context)