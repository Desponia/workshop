from django import forms
from .models import Memo


class MemoForm(forms.ModelForm):
    """메모 작성/수정 폼"""
    
    class Meta:
        model = Memo
        fields = ['title', 'content', 'category']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '메모 제목을 입력하세요'
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 10,
                'placeholder': '메모 내용을 입력하세요'
            }),
            'category': forms.Select(attrs={
                'class': 'form-select'
            }),
        }
        labels = {
            'title': '제목',
            'content': '내용',
            'category': '범주 (선택사항)',
        }
        help_texts = {
            'category': '메모의 범주를 선택하세요. 나중에 변경할 수 있습니다.',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 범주 필드에 빈 선택 옵션 추가
        self.fields['category'].empty_label = '선택 안 함'
        self.fields['category'].required = False