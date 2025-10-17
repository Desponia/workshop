// 메모짱 커스텀 JavaScript

document.addEventListener('DOMContentLoaded', function() {
    
    // 알림 메시지 자동 숨기기
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000); // 5초 후 자동 닫기
    });

    // 폼 유효성 검사
    const forms = document.querySelectorAll('.needs-validation');
    forms.forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });

    // 삭제 확인 다이얼로그
    const deleteButtons = document.querySelectorAll('.btn-delete');
    deleteButtons.forEach(function(button) {
        button.addEventListener('click', function(event) {
            const confirmed = confirm('정말로 삭제하시겠습니까? 이 작업은 되돌릴 수 없습니다.');
            if (!confirmed) {
                event.preventDefault();
            }
        });
    });

    // 툴팁 초기화
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // 팝오버 초기화
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function(popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

});

// 유틸리티 함수들
const MemoJjang = {
    
    // 로딩 스피너 표시
    showLoading: function(element) {
        const originalText = element.innerHTML;
        element.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>처리 중...';
        element.disabled = true;
        return originalText;
    },

    // 로딩 스피너 숨기기
    hideLoading: function(element, originalText) {
        element.innerHTML = originalText;
        element.disabled = false;
    },

    // 성공 메시지 표시
    showSuccessMessage: function(message) {
        this.showMessage(message, 'success');
    },

    // 에러 메시지 표시
    showErrorMessage: function(message) {
        this.showMessage(message, 'danger');
    },

    // 메시지 표시 (공통)
    showMessage: function(message, type = 'info') {
        const alertHtml = `
            <div class="alert alert-${type} alert-dismissible fade show" role="alert">
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;
        
        const container = document.querySelector('.container');
        const firstChild = container.firstElementChild;
        const alertDiv = document.createElement('div');
        alertDiv.innerHTML = alertHtml;
        
        container.insertBefore(alertDiv.firstElementChild, firstChild);
        
        // 5초 후 자동 제거
        setTimeout(function() {
            const alert = container.querySelector('.alert');
            if (alert) {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            }
        }, 5000);
    }
};

// 전역 객체로 노출
window.MemoJjang = MemoJjang;