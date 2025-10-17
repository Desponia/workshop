from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView
)
from django.urls import reverse_lazy
from django.db.models import Q

from .models import Memo
from .forms import MemoForm


class MemoListView(LoginRequiredMixin, ListView):
    """메모 목록 뷰 (범주별 필터링 지원)"""
    model = Memo
    template_name = 'memos/memo_list.html'
    context_object_name = 'memos'
    paginate_by = 10
    
    def get_queryset(self):
        """로그인한 사용자의 메모만 조회, 범주 필터링 지원"""
        queryset = Memo.objects.filter(author=self.request.user)
        
        # 범주 필터링
        category = self.request.GET.get('category')
        if category and category in dict(Memo.CATEGORY_CHOICES):
            queryset = queryset.filter(category=category)
        elif category == 'none':  # 범주 없는 메모
            queryset = queryset.filter(category__isnull=True)
        
        # 검색 기능 (선택 사항)
        search_query = self.request.GET.get('q')
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(content__icontains=search_query)
            )
        
        return queryset
    
    def get_context_data(self, **kwargs):
        """컨텍스트에 범주 정보 추가"""
        context = super().get_context_data(**kwargs)
        context['categories'] = Memo.CATEGORY_CHOICES
        context['selected_category'] = self.request.GET.get('category', '')
        context['search_query'] = self.request.GET.get('q', '')
        
        # 범주별 메모 개수 계산
        context['category_counts'] = {
            'all': Memo.objects.filter(author=self.request.user).count(),
            'none': Memo.objects.filter(
                author=self.request.user, 
                category__isnull=True
            ).count(),
        }
        for category_code, category_name in Memo.CATEGORY_CHOICES:
            context['category_counts'][category_code] = Memo.objects.filter(
                author=self.request.user,
                category=category_code
            ).count()
        
        return context


class MemoDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    """메모 상세 뷰"""
    model = Memo
    template_name = 'memos/memo_detail.html'
    context_object_name = 'memo'
    
    def test_func(self):
        """작성자만 조회 가능"""
        memo = self.get_object()
        return self.request.user == memo.author


class MemoCreateView(LoginRequiredMixin, CreateView):
    """메모 작성 뷰"""
    model = Memo
    form_class = MemoForm
    template_name = 'memos/memo_form.html'
    
    def form_valid(self, form):
        """작성자를 현재 로그인한 사용자로 설정"""
        form.instance.author = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, '메모가 성공적으로 작성되었습니다!')
        return response
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = '새 메모 작성'
        context['submit_button_text'] = '작성하기'
        return context


class MemoUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """메모 수정 뷰"""
    model = Memo
    form_class = MemoForm
    template_name = 'memos/memo_form.html'
    
    def test_func(self):
        """작성자만 수정 가능"""
        memo = self.get_object()
        return self.request.user == memo.author
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, '메모가 성공적으로 수정되었습니다!')
        return response
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = '메모 수정'
        context['submit_button_text'] = '수정하기'
        return context


class MemoDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """메모 삭제 뷰"""
    model = Memo
    template_name = 'memos/memo_confirm_delete.html'
    success_url = reverse_lazy('memos:list')
    
    def test_func(self):
        """작성자만 삭제 가능"""
        memo = self.get_object()
        return self.request.user == memo.author
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, '메모가 성공적으로 삭제되었습니다!')
        return super().delete(request, *args, **kwargs)
