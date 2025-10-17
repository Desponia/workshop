from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class UserRegisterForm(UserCreationForm):
    """사용자 회원가입 폼"""
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': '이메일 주소를 입력하세요'
        })
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # 기본 필드들에 Bootstrap 클래스 추가
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': '사용자명을 입력하세요'
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': '비밀번호를 입력하세요'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': '비밀번호를 다시 입력하세요'
        })
        
        # 한글 라벨 설정
        self.fields['username'].label = '사용자명'
        self.fields['email'].label = '이메일'
        self.fields['password1'].label = '비밀번호'
        self.fields['password2'].label = '비밀번호 확인'
    
    def save(self, commit=True):
        """이메일을 포함하여 사용자 저장"""
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user