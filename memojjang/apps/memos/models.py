from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse


class Memo(models.Model):
    """메모 모델"""
    
    # 범주 선택 상수
    CATEGORY_DAILY = 'daily'
    CATEGORY_WORK = 'work'
    CATEGORY_PERSONAL = 'personal'
    
    CATEGORY_CHOICES = [
        (CATEGORY_DAILY, '일상'),
        (CATEGORY_WORK, '업무'),
        (CATEGORY_PERSONAL, '개인'),
    ]
    
    title = models.CharField('제목', max_length=200)
    content = models.TextField('내용')
    category = models.CharField(
        '범주',
        max_length=20,
        choices=CATEGORY_CHOICES,
        blank=True,
        null=True,
        help_text='메모의 범주를 선택하세요 (선택사항)'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='memos',
        verbose_name='작성자'
    )
    created_at = models.DateTimeField('작성일시', auto_now_add=True)
    updated_at = models.DateTimeField('수정일시', auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = '메모'
        verbose_name_plural = '메모 목록'
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('memos:detail', kwargs={'pk': self.pk})
    
    def get_category_display_badge(self):
        """범주를 Bootstrap 뱃지로 표시하기 위한 CSS 클래스"""
        badge_classes = {
            self.CATEGORY_DAILY: 'bg-info',
            self.CATEGORY_WORK: 'bg-primary',
            self.CATEGORY_PERSONAL: 'bg-success',
        }
        return badge_classes.get(self.category, 'bg-secondary')
