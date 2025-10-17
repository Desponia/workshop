from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.views.generic import CreateView

from .forms import UserRegisterForm


class RegisterView(CreateView):
    """사용자 회원가입 뷰"""
    form_class = UserRegisterForm
    template_name = 'users/register.html'
    success_url = reverse_lazy('users:login')
    
    def form_valid(self, form):
        """회원가입 성공 시 처리"""
        response = super().form_valid(form)
        username = form.cleaned_data.get('username')
        messages.success(
            self.request, 
            f'{username}님, 회원가입이 완료되었습니다! 로그인해주세요.'
        )
        return response
    
    def dispatch(self, request, *args, **kwargs):
        """이미 로그인한 사용자는 홈으로 리다이렉트"""
        if request.user.is_authenticated:
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)


class CustomLoginView(LoginView):
    """사용자 로그인 뷰"""
    template_name = 'users/login.html'
    redirect_authenticated_user = True
    
    def get_success_url(self):
        """로그인 성공 시 홈으로 이동"""
        return reverse_lazy('home')
    
    def form_valid(self, form):
        """로그인 성공 시 환영 메시지"""
        username = form.get_user().username
        messages.success(self.request, f'{username}님, 환영합니다!')
        return super().form_valid(form)


class CustomLogoutView(LogoutView):
    """사용자 로그아웃 뷰"""
    next_page = reverse_lazy('home')
    
    def dispatch(self, request, *args, **kwargs):
        """로그아웃 시 메시지"""
        if request.user.is_authenticated:
            messages.info(request, '성공적으로 로그아웃되었습니다.')
        return super().dispatch(request, *args, **kwargs)
