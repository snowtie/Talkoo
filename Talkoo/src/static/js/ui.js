// ===== UI 모듈: 모달 클래스 =====

class Modal {
  constructor(id) {
    this.modal = document.getElementById(id);
    this.overlay = this.modal.querySelector('.modal-overlay');
    this.closeBtn = this.modal.querySelector('.close-btn');
    this.setupEvents();
  }

  setupEvents() {
    if (this.closeBtn) {
      this.closeBtn.addEventListener('click', () => this.close());
    }
    if (this.overlay) {
      this.overlay.addEventListener('click', () => this.close());
    }
  }

  open() {
    this.modal.classList.remove('hidden');
    document.body.classList.add('modal-open');
  }

  close() {
    this.modal.classList.add('hidden');
    document.body.classList.remove('modal-open');
  }
}

// 전역 노출
window.Modal = Modal;


