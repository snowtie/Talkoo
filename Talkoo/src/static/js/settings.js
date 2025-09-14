// ===== 설정 관리 모듈 =====

class SettingManager {
  constructor() {
    this.settings = {};
    this.currentTab = 'general';
  }

  // 로컬스토리지 키
  getStorageKey(type) {
    return `talkoo_settings_${type}`;
  }

  // 로컬스토리지 사용 제거 (서버를 단일 진실 소스로 사용)
  loadValues() { return null; }
  saveValues() { /* no-op */ }

  // 값 문자열을 정의된 타입으로 보정
  coerceValue(setting, strValue) {
    if (setting.type === 'select' && Array.isArray(setting.options)) {
      const found = setting.options.find(opt => String(opt.value) === String(strValue));
      if (found) return found.value; // 원래 타입 유지
    }
    return strValue;
  }

  // 초기값 계산 (설정 기본값 > select 첫 옵션)
  computeInitialValues(type) {
    const defs = this.settings[type] || [];
    const initial = {};
    defs.forEach(def => {
      if (def.hasOwnProperty('value')) {
        initial[def.id] = def.value;
      } else if (def.type === 'select' && Array.isArray(def.options) && def.options.length) {
        initial[def.id] = def.options[0].value;
      } else {
        initial[def.id] = '';
      }
    });
    return initial;
  }

  // 설정 적용 이벤트 발생 (다른 모듈이 수신 가능)
  applyValues(type, values) {
    const event = new CustomEvent('settings:updated', { detail: { type, values } });
    window.dispatchEvent(event);
  }

  // 서버에서 현재 설정 조회
  async fetchServerValues(type) {
    try {
      const url = type === 'general' ? '/setting/' : '/setting/trans/';
      const res = await fetch(url);
      if (!res.ok) return null;
      return await res.json();
    } catch {
      return null;
    }
  }

  // 서버에 설정 저장
  async postServerValues(type, values) {
    const url = type === 'general' ? '/setting/' : '/setting/trans/';
    const payload = { ...values };
    // API와 무관한 필드 제거
    if (type === 'general') {
      delete payload.log_path;
    } else if (type === 'translation') {
      // 서버가 관리하는 tkdic_* 값은 전송 안 함
      delete payload.tkdic_path;
      delete payload.tkdic_list;
      delete payload.tkdic_select;
    }
    const res = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    if (!res.ok) throw new Error('설정 저장 실패');
    return await res.json();
  }

  async reloadModelOnly() {
    try { await fetch('/setting/reload/model/', { method: 'POST' }); } catch {}
  }

  defineSettings(type, settings) {
    this.settings[type] = settings;
  }

  async renderSettingsForm(type, containerId) {
    const settings = this.settings[type];
    if (!settings) return;

    const container = document.getElementById(containerId);
    if (!container) return;

    // 서버 값 우선 확보 (실패 시 기본값 폴백)
    const serverValues = await this.fetchServerValues(type);
    const initialValues = serverValues || this.computeInitialValues(type);

    let html = `<form id="${type}-setting-form">`;
    settings.forEach(setting => {
      html += `<div class="flex h-13 justify-between items-center">`;
      html += `<label class="flex flex-col" for="${setting.id}"><span class="name">${setting.label}</span>`;
      if (setting.desc) html += `<span class="text-xs text-[#bbb]">${setting.desc}</span>`;
      html += `</label>`;

      if (setting.type === 'select') {
        const current = initialValues[setting.id];
        html += `<select id="${setting.id}">`;
        setting.options.forEach(opt => {
          const selected = String(opt.value) === String(current) ? ' selected' : '';
          html += `<option value="${opt.value}"${selected}>${opt.label}</option>`;
        });
        html += `</select>`;
      } else if (setting.type === 'input') {
        const current = initialValues[setting.id] ?? (setting.value || '');
        const safeVal = String(current).replace(/"/g, '&quot;');
        html += `<input class="no-scale-down" id="${setting.id}" type="${setting.inputType || 'text'}" value="${safeVal}"${setting.disabled ? ' disabled' : ''} />`;
      }
      html += `</div>`;
    });
    html += `<div class="flex justify-end mt-2"><button type="submit">저장</button></div></form>`;

    container.innerHTML = html;

    // 제출 핸들러: 새로고침 방지 + 저장 + 즉시 적용
    const formEl = container.querySelector(`#${type}-setting-form`);
    if (formEl) {
      formEl.addEventListener('submit', async (e) => {
        e.preventDefault();
        e.stopPropagation();

        // 설정 모달을 로딩 UI로 전환
        const settingModalEl = document.getElementById('setting-modal');
        const modalOverlay = settingModalEl ? settingModalEl.querySelector('.modal-overlay') : null;
        const modalContent = settingModalEl ? settingModalEl.querySelector('.modal-content') : null;
        let loadingBox = null;
        if (settingModalEl && modalOverlay && modalContent) {
          // 모달은 열려 있어야 오버레이가 보임. 닫혀 있으면 연다
          settingModalEl.classList.remove('hidden');
          // 콘텐츠 숨김
          modalContent.style.visibility = 'hidden';
          // 로딩 박스 추가 (오버레이 위 중앙)
          loadingBox = document.createElement('div');
          loadingBox.className = 'loading-box';
          loadingBox.innerHTML = `<span class="spinner"></span><span>설정 적용 중...</span>`;
          settingModalEl.appendChild(loadingBox);
        }

        const values = {};
        settings.forEach(setting => {
          const el = formEl.querySelector(`#${setting.id}`);
          if (!el) return;
          if (setting.type === 'select') {
            values[setting.id] = this.coerceValue(setting, el.value);
          } else if (setting.type === 'input') {
            values[setting.id] = el.value;
          }
        });

        // 서버 저장 → 모델 리로드 → 알림 → 새로고침
        try {
          await this.postServerValues(type, values);
          await this.reloadModelOnly();
          alert('설정이 저장되었습니다');
          // 새로고침으로 전역 반영
          window.location.reload();
        } catch (err) {
          console.error(err);
          alert('설정 저장 중 오류가 발생했습니다');
        } finally {
          // 로딩 UI 원복
          if (loadingBox) {
            try { loadingBox.remove(); } catch {}
          }
          if (modalContent) {
            modalContent.style.visibility = '';
          }
        }

        this.applyValues(type, values);
      });
    }
  }

  async switchTab(tabName) {
    this.currentTab = tabName;
    document.querySelectorAll('.setting-tab-btn').forEach(btn => {
      btn.classList.toggle('active', btn.dataset.tab === tabName);
    });
    document.querySelectorAll('.tab-content').forEach(el => {
      el.classList.toggle('hidden', el.id !== `tab-content-${tabName}`);
    });
    if (tabName === 'general') {
      await this.renderSettingsForm('general', 'tab-content-general');
    } else if (tabName === 'translation') {
      await this.renderSettingsForm('translation', 'tab-content-translation');
      if (typeof renderDictPanel === 'function') renderDictPanel();
    }
  }
}

// 전역 노출
window.SettingManager = SettingManager;


