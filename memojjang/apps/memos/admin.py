from django.contrib import admin
from .models import Memo


@admin.register(Memo)
class MemoAdmin(admin.ModelAdmin):
    """메모 관리자 페이지"""
    list_display = ['title', 'category', 'author', 'created_at', 'updated_at']
    list_filter = ['category', 'created_at', 'updated_at', 'author']
    search_fields = ['title', 'content']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('기본 정보', {
            'fields': ('title', 'content', 'category')
        }),
        ('작성자 정보', {
            'fields': ('author',)
        }),
        ('날짜 정보', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """슈퍼유저는 모든 메모, 일반 사용자는 자신의 메모만"""
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(author=request.user)
