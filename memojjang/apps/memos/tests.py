from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from .models import Memo


class MemoModelTest(TestCase):
    """메모 모델 테스트"""
    
    def setUp(self):
        """테스트 데이터 준비"""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.memo = Memo.objects.create(
            title='테스트 메모',
            content='테스트 내용입니다.',
            category=Memo.CATEGORY_DAILY,
            author=self.user
        )
    
    def test_memo_creation(self):
        """메모 생성 테스트"""
        self.assertEqual(self.memo.title, '테스트 메모')
        self.assertEqual(self.memo.content, '테스트 내용입니다.')
        self.assertEqual(self.memo.category, Memo.CATEGORY_DAILY)
        self.assertEqual(self.memo.author, self.user)
        self.assertIsNotNone(self.memo.created_at)
        self.assertIsNotNone(self.memo.updated_at)
    
    def test_memo_str_method(self):
        """__str__ 메서드 테스트"""
        self.assertEqual(str(self.memo), '테스트 메모')
    
    def test_memo_ordering(self):
        """메모 정렬 순서 테스트 (최신순)"""
        memo2 = Memo.objects.create(
            title='두 번째 메모',
            content='두 번째 내용',
            author=self.user
        )
        memos = Memo.objects.all()
        self.assertEqual(memos[0], memo2)  # 최신 메모가 먼저
        self.assertEqual(memos[1], self.memo)
    
    def test_memo_category_nullable(self):
        """범주 없는 메모 생성 테스트"""
        memo_no_category = Memo.objects.create(
            title='범주 없는 메모',
            content='범주가 설정되지 않은 메모',
            author=self.user
        )
        self.assertIsNone(memo_no_category.category)
    
    def test_memo_get_absolute_url(self):
        """get_absolute_url 메서드 테스트"""
        expected_url = reverse('memos:detail', kwargs={'pk': self.memo.pk})
        self.assertEqual(self.memo.get_absolute_url(), expected_url)
    
    def test_memo_category_display_badge(self):
        """범주 뱃지 CSS 클래스 테스트"""
        self.assertEqual(self.memo.get_category_display_badge(), 'bg-info')
        
        memo_work = Memo.objects.create(
            title='업무 메모',
            content='업무 내용',
            category=Memo.CATEGORY_WORK,
            author=self.user
        )
        self.assertEqual(memo_work.get_category_display_badge(), 'bg-primary')


class MemoViewTest(TestCase):
    """메모 뷰 테스트"""
    
    def setUp(self):
        """테스트 데이터 및 클라이언트 준비"""
        self.client = Client()
        self.user1 = User.objects.create_user(
            username='user1',
            password='pass1234'
        )
        self.user2 = User.objects.create_user(
            username='user2',
            password='pass5678'
        )
        
        # 사용자1의 메모들
        self.memo1 = Memo.objects.create(
            title='일상 메모',
            content='일상 내용',
            category=Memo.CATEGORY_DAILY,
            author=self.user1
        )
        self.memo2 = Memo.objects.create(
            title='업무 메모',
            content='업무 내용',
            category=Memo.CATEGORY_WORK,
            author=self.user1
        )
        self.memo3 = Memo.objects.create(
            title='범주 없는 메모',
            content='범주 없음',
            author=self.user1
        )
        
        # 사용자2의 메모
        self.memo_user2 = Memo.objects.create(
            title='다른 사용자 메모',
            content='다른 사용자 내용',
            author=self.user2
        )
    
    def test_memo_list_view_requires_login(self):
        """메모 목록 뷰 로그인 필요 테스트"""
        response = self.client.get(reverse('memos:list'))
        self.assertEqual(response.status_code, 302)  # 리다이렉트
        self.assertIn('/users/login/', response.url)
    
    def test_memo_list_view_shows_only_user_memos(self):
        """메모 목록에 자신의 메모만 표시 테스트"""
        self.client.login(username='user1', password='pass1234')
        response = self.client.get(reverse('memos:list'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '일상 메모')
        self.assertContains(response, '업무 메모')
        self.assertNotContains(response, '다른 사용자 메모')
    
    def test_memo_list_view_category_filter(self):
        """범주별 필터링 테스트"""
        self.client.login(username='user1', password='pass1234')
        
        # 일상 메모 필터
        response = self.client.get(reverse('memos:list') + '?category=daily')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '일상 메모')
        self.assertNotContains(response, '업무 메모')
        
        # 업무 메모 필터
        response = self.client.get(reverse('memos:list') + '?category=work')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '업무 메모')
        self.assertNotContains(response, '일상 메모')
        
        # 범주 없는 메모 필터
        response = self.client.get(reverse('memos:list') + '?category=none')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '범주 없는 메모')
    
    def test_memo_detail_view_requires_login(self):
        """메모 상세 뷰 로그인 필요 테스트"""
        response = self.client.get(
            reverse('memos:detail', kwargs={'pk': self.memo1.pk})
        )
        self.assertEqual(response.status_code, 302)
    
    def test_memo_detail_view_author_only(self):
        """메모 상세 뷰 작성자만 접근 가능 테스트"""
        # user2로 로그인하여 user1의 메모 접근 시도
        self.client.login(username='user2', password='pass5678')
        response = self.client.get(
            reverse('memos:detail', kwargs={'pk': self.memo1.pk})
        )
        self.assertEqual(response.status_code, 403)  # Forbidden
    
    def test_memo_create_view(self):
        """메모 작성 뷰 테스트"""
        self.client.login(username='user1', password='pass1234')
        
        response = self.client.post(reverse('memos:create'), {
            'title': '새 메모',
            'content': '새 내용',
            'category': Memo.CATEGORY_PERSONAL
        })
        
        self.assertEqual(response.status_code, 302)  # 리다이렉트
        self.assertTrue(Memo.objects.filter(title='새 메모').exists())
        
        new_memo = Memo.objects.get(title='새 메모')
        self.assertEqual(new_memo.author, self.user1)
        self.assertEqual(new_memo.category, Memo.CATEGORY_PERSONAL)
    
    def test_memo_create_without_category(self):
        """범주 없이 메모 작성 테스트"""
        self.client.login(username='user1', password='pass1234')
        
        response = self.client.post(reverse('memos:create'), {
            'title': '범주 없는 새 메모',
            'content': '범주 선택 안 함',
            'category': ''  # 빈 값
        })
        
        self.assertEqual(response.status_code, 302)
        new_memo = Memo.objects.get(title='범주 없는 새 메모')
        self.assertIsNone(new_memo.category)
    
    def test_memo_update_view(self):
        """메모 수정 뷰 테스트"""
        self.client.login(username='user1', password='pass1234')
        
        response = self.client.post(
            reverse('memos:update', kwargs={'pk': self.memo3.pk}),
            {
                'title': '수정된 제목',
                'content': '수정된 내용',
                'category': Memo.CATEGORY_PERSONAL  # 범주 추가
            }
        )
        
        self.assertEqual(response.status_code, 302)
        self.memo3.refresh_from_db()
        self.assertEqual(self.memo3.title, '수정된 제목')
        self.assertEqual(self.memo3.category, Memo.CATEGORY_PERSONAL)
    
    def test_memo_update_view_author_only(self):
        """메모 수정 뷰 작성자만 가능 테스트"""
        self.client.login(username='user2', password='pass5678')
        
        response = self.client.post(
            reverse('memos:update', kwargs={'pk': self.memo1.pk}),
            {
                'title': '해킹 시도',
                'content': '수정 시도',
            }
        )
        
        self.assertEqual(response.status_code, 403)
        self.memo1.refresh_from_db()
        self.assertNotEqual(self.memo1.title, '해킹 시도')
    
    def test_memo_delete_view(self):
        """메모 삭제 뷰 테스트"""
        self.client.login(username='user1', password='pass1234')
        memo_pk = self.memo1.pk
        
        response = self.client.post(
            reverse('memos:delete', kwargs={'pk': memo_pk})
        )
        
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Memo.objects.filter(pk=memo_pk).exists())
    
    def test_memo_delete_view_author_only(self):
        """메모 삭제 뷰 작성자만 가능 테스트"""
        self.client.login(username='user2', password='pass5678')
        
        response = self.client.post(
            reverse('memos:delete', kwargs={'pk': self.memo1.pk})
        )
        
        self.assertEqual(response.status_code, 403)
        self.assertTrue(Memo.objects.filter(pk=self.memo1.pk).exists())
    
    def test_memo_search_functionality(self):
        """메모 검색 기능 테스트"""
        self.client.login(username='user1', password='pass1234')
        
        response = self.client.get(reverse('memos:list') + '?q=일상')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '일상 메모')
        self.assertNotContains(response, '업무 메모')


class MemoCategoryIntegrationTest(TestCase):
    """범주 기능 통합 테스트"""
    
    def setUp(self):
        """테스트 데이터 준비"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')
    
    def test_full_category_workflow(self):
        """범주 관련 전체 워크플로우 테스트"""
        # 1. 범주 없이 메모 작성
        response = self.client.post(reverse('memos:create'), {
            'title': '워크플로우 테스트',
            'content': '처음엔 범주 없음',
            'category': ''
        })
        self.assertEqual(response.status_code, 302)
        
        memo = Memo.objects.get(title='워크플로우 테스트')
        self.assertIsNone(memo.category)
        
        # 2. 나중에 범주 추가
        response = self.client.post(
            reverse('memos:update', kwargs={'pk': memo.pk}),
            {
                'title': '워크플로우 테스트',
                'content': '처음엔 범주 없음',
                'category': Memo.CATEGORY_WORK
            }
        )
        self.assertEqual(response.status_code, 302)
        
        memo.refresh_from_db()
        self.assertEqual(memo.category, Memo.CATEGORY_WORK)
        
        # 3. 범주별 필터링으로 찾기
        response = self.client.get(reverse('memos:list') + '?category=work')
        self.assertContains(response, '워크플로우 테스트')
        
        # 4. 다른 범주로 변경
        response = self.client.post(
            reverse('memos:update', kwargs={'pk': memo.pk}),
            {
                'title': '워크플로우 테스트',
                'content': '처음엔 범주 없음',
                'category': Memo.CATEGORY_PERSONAL
            }
        )
        
        memo.refresh_from_db()
        self.assertEqual(memo.category, Memo.CATEGORY_PERSONAL)
        
        # 5. 업무 필터에서는 더 이상 보이지 않음
        response = self.client.get(reverse('memos:list') + '?category=work')
        self.assertNotContains(response, '워크플로우 테스트')
        
        # 6. 개인 필터에서 보임
        response = self.client.get(reverse('memos:list') + '?category=personal')
        self.assertContains(response, '워크플로우 테스트')
