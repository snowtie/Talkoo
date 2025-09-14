// 번역 결과 저장 변수
let translationResults = {
  modelTrans: { text: '여기에 결과가 나와요.', isValid: false },
  prePostTrans: { text: '여기에 결과가 나와요.', isValid: false },
  geminiIntegra: { text: '여기에 결과가 나와요.', isValid: false }
};

let geminiReson = '제미나이의 상세한 답변이 여기에 표시됩니다.';

// 현재 선택된 번역 모드에 따라 결과 표시
const updateTranslationDisplay = () => {
  const resultTextElement = document.getElementById('result-text');
  const selectedMode = document.querySelector('input[name="mode"]:checked');
  const showAiReplyBtnElement = document.getElementById('show-ai-reply-btn');
  const tooltipElement = document.getElementById('global-tooltip');
  
  if (!selectedMode || !translationResults[selectedMode.value]) {
    return;
  }
  
  const result = translationResults[selectedMode.value];
  resultTextElement.textContent = result.text;
  
  // 유효성에 따라 스타일 적용
  if (result.isValid) {
    resultTextElement.classList.remove('text-[#999]');
  } else {
    resultTextElement.classList.add('text-[#999]');
  }

  if (selectedMode.value === 'geminiIntegra') {
    console.log('geminiIntegra');
    showAiReplyBtnElement.classList.remove('hidden');
    tooltipElement.querySelector('.tooltip-title').textContent = '제미나이 상세 답변';
    tooltipElement.querySelector('.tooltip-content').textContent = geminiReson;
  } else {
    showAiReplyBtnElement.classList.add('hidden');
  }
};

// 번역 폼 제출 핸들러
const handleSubmit = async (event) => {
  const sourceTextElement = document.getElementById('source-text');
  const resultTextElement = document.getElementById('result-text');
  const form = sourceTextElement.closest('form');
  const submitButton = form ? form.querySelector('button[type="submit"]') : null;
  const backgroundElement = document.querySelector('.text-box-background');
  const radioButtons = document.querySelectorAll('input[name="mode"]');
  const selectedMode = document.querySelector('input[name="mode"]:checked');
  const resultBtns = document.querySelector('.result-btns-container');

  event.preventDefault();
  event.stopPropagation();

  const text = sourceTextElement.value.trim();
  if (!text) {
    alert('번역할 문장을 입력해주세요.');
    return;
  }
  
  // 번역 시작 시 버튼 및 라디오 버튼 비활성화  
  if (submitButton) {
    submitButton.disabled = true;
    submitButton.classList.add('loading');
    submitButton.textContent = '번역 중...';
  }
  sourceTextElement.disabled = true;
  radioButtons.forEach(radio => radio.disabled = true);
  backgroundElement.classList.add('loading');
  backgroundElement.classList.remove('right');
  resultTextElement.textContent = '번역 중...';
  resultTextElement.classList.add('text-[#999]');
  resultBtns.classList.add('hidden');

  let invalidResult = false;
  
  try {
    const response = await fetch('/translate/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        text: text,
      })
    });

    if (response.ok) {
      const data = await response.json();
      
      // 유효성 검사 함수
      const isValidResult = (result) => {
        return result && result.trim() !== '' && result !== '번역 결과가 없습니다.';
      };
      
      // 모든 번역 결과 저장 (유효성 포함)
      translationResults = {
        modelTrans: {
          text: data.modelTrans || '번역 결과가 없습니다.',
          isValid: isValidResult(data.modelTrans)
        },
        prePostTrans: {
          text: data.prePostTrans || '번역 결과가 없습니다.',
          isValid: isValidResult(data.prePostTrans)
        },
        geminiIntegra: {
          text: data.geminiIntegra || '번역 결과가 없습니다.',
          isValid: isValidResult(data.geminiIntegra)
        }
      };

      geminiReson = data.geminiReson || '번역 결과가 없습니다.';
      
      // 현재 선택된 모드에 따라 결과 표시
      updateTranslationDisplay();
      invalidResult = false;
    } else {
      resultTextElement.textContent = '번역 중 오류가 발생했습니다.';
      invalidResult = true;
    }
  } catch (error) {
    console.error('번역 요청 오류:', error);
    resultTextElement.textContent = '네트워크 오류가 발생했습니다.';
    invalidResult = true;
  } finally {
    sourceTextElement.disabled = false;
    // 번역 완료 후 버튼 및 라디오 버튼 다시 활성화
    if (submitButton) {
      submitButton.disabled = false;
      submitButton.classList.remove('loading');
      submitButton.textContent = '번역하기';
    }
    radioButtons.forEach(radio => radio.disabled = false);
    backgroundElement.classList.remove('loading');
    backgroundElement.classList.add('right');
    resultBtns.classList.remove('hidden');

    if (invalidResult) {
      resultTextElement.classList.add('text-[#999]');
    } else {
      resultTextElement.classList.remove('text-[#999]');
    }
  }
}

// 모달 인스턴스 생성
const settingModal = new window.Modal('setting-modal');
const dictModal = new window.Modal('dict-modal');

// settings.js 제공: SettingManager

// 설정 매니저 인스턴스 생성
const settingManager = new window.SettingManager();

// 설정 정의
settingManager.defineSettings('general', [
  {
    id: 'model_type',
    label: '모델 타입',
    type: 'select',
    options: [
      { value: 1, label: '1' },
      { value: 2, label: '2' },
      { value: 3, label: '3' }
    ],
    desc: '모델의 무게를 선택합니다. 클 수록 성능 및 용량이 상승합니다.'
  },
  {
    id: 'model_device',
    label: '모델 디바이스',
    type: 'select',
    options: [
      { value: 0, label: 'GPU' },
      { value: 1, label: 'CPU' }
    ],
    desc: '모델이 사용하는 디바이스를 선택합니다.'
  },
  {
    id: 'device_map',
    label: '디바이스 맵 활성화',
    type: 'select',
    options: [
      { value: 0, label: '비활성화' },
      { value: 1, label: '활성화' }
    ],
    desc: 'CPU와 GPU를 동시에 사용하여 부담을 줄입니다. 단, 로딩이 좀 느려질 수 있습니다.'
  },
  {
    id: 'debug_mod',
    label: '디버그 모드',
    type: 'select',
    options: [
      { value: false, label: '비활성화' },
      { value: true, label: '활성화' }
    ],
    desc: '로그에 디버그 표시를 활성화합니다.',
  },
  {
    id: 'log_path',
    label: '로그 경로',
    type: 'input',
    inputType: 'text',
    disabled: true,
    value: '/log',
    desc: '모든 로그가 저장되는 폴더 위치입니다.'
  }
]);

settingManager.defineSettings('translation', [
  {
    id: 'nomal_trans',
    label: '기본 번역 활성화',
    type: 'select',
    options: [
      { value: true, label: '활성화' },
      { value: false, label: '비활성화' }
    ],
    desc: '모델 번역을 활성화합니다.'
  },
  {
    id: 'per_post_trans',
    label: '사전 번역 활성화',
    type: 'select',
    options: [
      { value: true, label: '활성화' },
      { value: false, label: '비활성화' }
    ],
    desc: '커스텀 사전 번역을 활성화 합니다.'
  },
  {
    id: 'gemini_integration',
    label: '제미니 처리 활성화',
    type: 'select',
    options: [
      { value: true, label: '활성화' },
      { value: false, label: '비활성화' }
    ],
    desc: '문장을 제미니가 다듬어 줍니다.'
  },
  {
    id: 'gemini_api',
    label: '제미니 API 키',
    type: 'input',
    inputType: 'text',
    desc: '제미니 처리 활성화에 필요합니다.'
  }
]);

// ===== 사전 관리 =====
async function refreshDictPanel() {
  const containerId = 'dict-panel';
  const container = document.getElementById(containerId);
  if (!container) return;

  // 서버 상태 조회
  let tkList = [];
  let selected = null;
  try {
    const res = await fetch('/setting/trans/');
    if (res.ok) {
      const data = await res.json();
      tkList = Array.isArray(data.tkdic_list) ? data.tkdic_list : [];
      selected = data.tkdic_select || null;
    }
  } catch {}

  let html = '';

  html += `<div class="dict-list">`;
  if (!tkList.length) {
    html += `<div class="text-[#999]">사전이 없습니다. 업로드하여 추가하세요.</div>`;
  } else {
    html += `<ul>`;
    tkList.forEach(name => {
      const isSel = selected === name;
      html += `<li class="flex items-center justify-between py-1 no-scale-down">
        <span>${name}${isSel ? ' <span class="text-[#0a7]">(선택됨)</span>' : ''}</span>
        <span class="flex gap-2">
          <button data-action="select" data-name="${name}">${isSel ? '재선택' : '선택'}</button>
          <button data-action="delete" data-name="${name}">삭제</button>
        </span>
      </li>`;
    });
    html += `</ul>`;
  }
  html += `</div>`;

  container.innerHTML = html;

  // 선택/삭제 위임 핸들러
  container.querySelectorAll('button[data-action]').forEach(btn => {
    btn.addEventListener('click', async () => {
      const action = btn.getAttribute('data-action');
      const name = btn.getAttribute('data-name');
      if (action === 'select') {
        try {
          const res = await fetch('/dict/select/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ filename: name })
          });
          if (res.ok) {
            await refreshDictPanel();
          } else {
            alert('선택 실패');
          }
        } catch { alert('네트워크 오류'); }
      } else if (action === 'delete') {
        if (!confirm('정말 삭제하시겠습니까?')) return;
        try {
          const res = await fetch(`/dict/${encodeURIComponent(name)}`, { method: 'DELETE' });
          if (res.ok) {
            await refreshDictPanel();
          } else {
            alert('삭제 실패');
          }
        } catch { alert('네트워크 오류'); }
      }
    });
  });
}

// 독립 사전 모달용 패널 렌더러
async function renderDictOnlyPanel() {
  const container = document.getElementById('dict-only-panel');
  if (!container) return;

  // 서버 상태 조회
  let tkList = [];
  let selected = null;
  try {
    const res = await fetch('/setting/trans/');
    if (res.ok) {
      const data = await res.json();
      tkList = Array.isArray(data.tkdic_list) ? data.tkdic_list : [];
      selected = data.tkdic_select || null;
    }
  } catch {}

  // 저장된 검색/정렬 상태 읽기
  const LS_DICT_FILTER = 'talkoo_dict_filter';
  const LS_DICT_SORT = 'talkoo_dict_sort';
  const filterValue = (localStorage.getItem(LS_DICT_FILTER) || '').trim();
  const sortValue = localStorage.getItem(LS_DICT_SORT) || 'name_asc';

  // 필터 적용/정렬 준비
  let filtered = tkList.filter(n => n.toLowerCase().includes(filterValue.toLowerCase()))
    .slice();
  if (sortValue === 'name_desc') {
    filtered.sort((a, b) => b.localeCompare(a));
  } else if (sortValue === 'selected_first') {
    filtered.sort((a, b) => {
      const av = a === selected ? 0 : 1;
      const bv = b === selected ? 0 : 1;
      if (av !== bv) return av - bv;
      return a.localeCompare(b);
    });
  } else {
    filtered.sort((a, b) => a.localeCompare(b));
  }

  let html = '';

  html += `<div class="search-bar flex items-center gap-2 my-2">
    <input
      id="dict-search" class="no-scale-down" type="text" placeholder="검색(.tkdic 이름)" value="${filterValue.replace(/"/g, '&quot;')}"
    />
    <select id="dict-sort">
      <option value="name_asc" ${sortValue==='name_asc'?'selected':''}>이름 오름차순</option>
      <option value="name_desc" ${sortValue==='name_desc'?'selected':''}>이름 내림차순</option>
      <option value="selected_first" ${sortValue==='selected_first'?'selected':''}>선택 사전 우선</option>
    </select>
  </div>`;

  html += `<div class="dict-list">`;
  if (!filtered.length) {
    html += `<div class="text-[#999]">사전이 없습니다. 업로드하여 추가하세요.</div>`;
  } else {
    html += `<ul>`;
    filtered.forEach(name => {
      const isSel = selected === name;
      html += `<li class="flex items-center justify-between py-1 ${isSel ? 'selected' : ''}" data-name="${name}">
        <button class="dict-name text-left no-scale-down" data-action="open" data-name="${name}">
          <span class="icon material-symbols-outlined">
            ${isSel ? 'book_5' : 'book_4'}
          </span>
          ${name}
        </button>
        <span class="right-box flex gap-2 ${isSel ? 'justify-center items-center rounded-md bg-[#0a7] text-white text-sm w-16 h-8 font-semibold' : ''}">
          ${isSel ? '선택됨' : ''}
          ${isSel ? '' : `<button data-action="select" data-name="${name}" class="flex items-center justify-center ${isSel ? 'bg-white text-[#0a7]' : 'bg-[#333] text-white'} px-1 py-1 rounded-md text-sm" ${isSel ? 'disabled' : ''}>
            <span class="material-symbols-outlined select-icon">check</span>
          </button>`}
          ${isSel ? '' : `<button data-action="delete" data-name="${name}" class="flex items-center justify-center"><span class="delete material-symbols-outlined">remove</span></button>`}
        </span>
      </li>`;
    });
    html += `</ul>`;
  }
  html += `</div>`;

  const content = document.getElementById('dict-content') || container;
  content.innerHTML = html;

  // offsetTop 기반 FLIP: 선택 항목을 맨 앞으로 이동시키는 애니메이션
  const animateSelectReorder = (selectedName) => new Promise((resolve) => {
    const sortVal = localStorage.getItem(LS_DICT_SORT) || 'name_asc';
    if (sortVal !== 'selected_first') { resolve(); return; }
    const ul = content.querySelector('.dict-list ul');
    if (!ul) { resolve(); return; }
    const items = Array.from(ul.querySelectorAll('li[data-name]'));
    if (!items.length) { resolve(); return; }

    const byName = Object.fromEntries(items.map(li => [li.getAttribute('data-name'), li]));
    const originalOrder = items.map(li => li.getAttribute('data-name'));
    if (!byName[selectedName]) { resolve(); return; }

    // 1) 기존 offsetTop 기록
    const oldTop = {};
    originalOrder.forEach(n => { oldTop[n] = byName[n].offsetTop; });

    // 2) 목표 순서 적용해 새 offsetTop 측정
    const others = originalOrder.filter(n => n !== selectedName).sort((a, b) => a.localeCompare(b));
    const targetOrder = [selectedName, ...others];
    targetOrder.forEach(n => ul.appendChild(byName[n]));
    const newTop = {};
    targetOrder.forEach(n => { newTop[n] = byName[n].offsetTop; });

    // 원래 순서로 되돌려 화면은 아직 그대로 유지
    originalOrder.forEach(n => ul.appendChild(byName[n]));

    const duration = 200;
    
    // 강제 리플로우
    void ul.offsetHeight;
    originalOrder.forEach(n => {
      const li = byName[n];
      
      const dy = (newTop[n] ?? oldTop[n]) - oldTop[n];
      if (dy !== 0) {
        li.style.transition = `transform ${duration}ms ease`;
        li.style.transform = `translateY(${dy}px)`;
      }
    });

    // 4) 200ms 뒤 실제 순서를 적용하고 스타일 정리
    setTimeout(() => {
      targetOrder.forEach(n => ul.appendChild(byName[n]));
      originalOrder.forEach(n => {
        const li = byName[n];
        li.style.transition = '';
        li.style.transform = '';
      });
      resolve();
    }, duration);
  });

  // 선택/삭제 위임
  container.querySelectorAll('button[data-action]').forEach(btn => {
    btn.addEventListener('click', async () => {
      const action = btn.getAttribute('data-action');
      const name = btn.getAttribute('data-name');
      if (action === 'open') {
        await openDictEntries(name);
        // scroll 내리기
        const modalBody = document.querySelector('#dict-modal .modal-body');
        if (modalBody) {
          modalBody.scrollTo({
            top: modalBody.scrollHeight,
            behavior: 'smooth'
          });
        }
        return;
      }
      if (action === 'select') {
        try {
          const res = await fetch('/dict/select/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ filename: name })
          });
          if (res.ok) {
            const sortVal = localStorage.getItem(LS_DICT_SORT) || 'name_asc';

            // 즉시 UI에 선택 상태 반영
            // const ul = (document.getElementById('dict-content') || container).querySelector('.dict-list ul');
            // if (ul) {
            //   // 다른 항목의 임시 selected 제거 (시각적 일관성)
            //   ul.querySelectorAll('li.selected').forEach(li => li.classList.remove('selected'));
            //   const li = ul.querySelector(`li[data-name="${CSS.escape(name)}"]`);
            //   if (li) {
            //     li.classList.add('selected');
            //     const icon = li.querySelector('.icon.material-symbols-outlined');
            //     if (icon) icon.textContent = 'book_5';
            //     const rightbox = li.querySelector('button[data-action="select"][data-name="' + name + '"]');
            //     if (selBtn) {
            //       selBtn.remove();
            //     }
            //   }
            // }

            document.querySelectorAll('.dict-list > ul > li[data-name]').forEach(li => {
              if (li.getAttribute('data-name') === name) {
                li.classList.add('selected');
              } else {
                li.classList.remove('selected');
              }

              const rightbox = li.querySelector('.right-box');
              if (rightbox) {
                // rightbox.style.opacity = 0.1;
                rightbox.remove();
              }
            })

            if (sortVal === 'selected_first') {
              await animateSelectReorder(name);
              await renderDictOnlyPanel();
            } else {
              await renderDictOnlyPanel();
            }
          } else {
            alert('선택 실패');
          }
        } catch { alert('네트워크 오류'); }
      } else if (action === 'delete') {
        if (!confirm('정말 삭제하시겠습니까?')) return;
        try {
          const res = await fetch(`/dict/${encodeURIComponent(name)}`, { method: 'DELETE' });
          if (res.ok) {
            await renderDictOnlyPanel();
          } else {
            alert('삭제 실패');
          }
        } catch { alert('네트워크 오류'); }
      }
    });
  });

  // 검색/정렬 이벤트
  const searchEl = document.getElementById('dict-search');
  if (searchEl) {
    searchEl.addEventListener('input', () => {
      localStorage.setItem(LS_DICT_FILTER, searchEl.value);
      renderDictOnlyPanel();
    });
  }
  const sortEl = document.getElementById('dict-sort');
  if (sortEl) {
    sortEl.addEventListener('change', () => {
      localStorage.setItem(LS_DICT_SORT, sortEl.value);
      renderDictOnlyPanel();
    });
  }
}

// 사전 엔트리 뷰어
async function openDictEntries(filename) {
  try {
    const res = await fetch(`/dict/entries/${encodeURIComponent(filename)}`);
    if (!res.ok) {
      alert('사전 로드 실패');
      return;
    }
    const data = await res.json();
    // 간단한 인라인 뷰어 렌더
    const wrap = document.createElement('div');
    wrap.className = 'mt-3';
    const searchId = `entry-search-${Date.now()}`;
    wrap.innerHTML = `
      <hr class="border-t-2 border-[#e8e8e8] my-4 border-dashed" />
      <div class="flex items-center justify-between">
        <h3 class="code">${data.filename} (main_fuzzy: ${data.main_fuzzy ?? '―'})</h3>
        <button id="close-entry-view"><span class="material-symbols-outlined">close</span></button>
      </div>
      <div class="flex items-center gap-2 my-2">
        <input class="no-scale-down grow px-3 py-2" id="${searchId}" type="text" placeholder="엔트리 검색(word/kor)" />
      </div>
      <div class="entry-list" style="max-height: 240px; overflow:auto;"></div>
    `;
    const container = document.getElementById('dict-only-panel');
    const prev = container.querySelector('.entry-view-wrap');
    if (prev) prev.remove();
    wrap.classList.add('entry-view-wrap');
    container.appendChild(wrap);

    const listEl = wrap.querySelector('.entry-list');
    let items = Array.isArray(data.entries) ? data.entries : [];
    const render = (q='') => {
      const qq = q.toLowerCase();
      const filtered = items.filter(it => (it.word||'').toLowerCase().includes(qq) || (it.kor||'').toLowerCase().includes(qq));
      if (!filtered.length) {
        listEl.innerHTML = '<div class="text-[#999]">엔트리가 없습니다.</div>';
        return;
      }
      listEl.innerHTML = `<table class="w-full text-sm">
        <thead><tr class="bold"><th class="text-left">word</th><th class="text-left">kor</th><th class="text-left">fuzzy</th></tr></thead>
        <tbody>
          ${filtered.map(it => `<tr><td>${escapeHtml(it.word||'')}</td><td>${escapeHtml(it.kor||'')}</td><td>${it.fuzzy ?? '―'}</td></tr>`).join('')}
        </tbody>
      </table>`;
    };
    render();
    wrap.querySelector(`#${searchId}`).addEventListener('input', (e) => render(e.target.value));
    wrap.querySelector('#close-entry-view').addEventListener('click', () => wrap.remove());
  } catch {
    alert('사전 로드 중 오류');
  }
}


// ===== 이벤트 리스너 설정 =====
window.addEventListener('DOMContentLoaded', () => {
  // 모달 버튼 이벤트 설정
  setupModalButtons();
  
  // 탭 버튼 이벤트 연결
  document.querySelectorAll('.setting-tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      settingManager.switchTab(btn.dataset.tab);
    });
  });

  // 기본 탭 활성화
  settingManager.switchTab('general');

  // 파일 업로드 이벤트 설정
  setupFileUploadEvents();
  
  // 키보드 이벤트 설정
  setupKeyboardEvents();
  
  // 라디오 버튼 변경 이벤트 설정
  document.querySelectorAll('input[name="mode"]').forEach(radio => {
    radio.addEventListener('change', updateTranslationDisplay);
  });
  
  // textarea 키보드 이벤트 설정 (DOM이 완전히 로드된 후)
  const sourceTextElement = document.getElementById('source-text');
  if (sourceTextElement) {
    sourceTextElement.addEventListener('keydown', (e) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        e.preventDefault();
        const form = sourceTextElement.closest('form');
        if (form) {
          handleSubmit(new Event('submit', { bubbles: true, cancelable: true }));
        }
      }
    });

    sourceTextElement.addEventListener('focus', () => {
      document.querySelector('.text-box-background').classList.remove('right');
    });
  }

  const showAiReplyBtnElement = document.getElementById('show-ai-reply-btn');
  const tooltipElement = document.getElementById('global-tooltip');
  let isTooltipPinned = false;

  showAiReplyBtnElement.addEventListener('mouseenter', () => {
    if (!isTooltipPinned) {
      const btnRect = showAiReplyBtnElement.getBoundingClientRect();
    
      const left = btnRect.right - 300;
      const top = (btnRect.top + 32);
  
      tooltipElement.style.left = left + 'px';
      tooltipElement.style.top = top + 'px';

      tooltipElement.classList.remove('hidden');
    }
  });

  showAiReplyBtnElement.addEventListener('mouseleave', () => {
    if (!isTooltipPinned) {
      tooltipElement.classList.add('hidden');
    }
  });

  // 클릭 시 툴팁 고정/해제 토글
  // showAiReplyBtnElement.addEventListener('click', () => {
  //   isTooltipPinned = !isTooltipPinned;
  //   showAiReplyBtnElement.classList.toggle('active', isTooltipPinned);
  //   tooltipElement.classList.toggle('hidden', !isTooltipPinned);
  // });
});

// 모달 버튼 이벤트 설정 함수
const setupModalButtons = () => {
  // 설정 버튼 클릭 시 설정 모달 열기
  const settingBtnById = document.getElementById('setting-btn');
  if (settingBtnById) {
    settingBtnById.addEventListener('click', () => {
      settingManager.switchTab('general');
      settingModal.open();
    });
  }

  // dict 버튼 클릭 시 사전 모달 열기
  const dictBtnElById = document.getElementById('dict-btn');
  if (dictBtnElById) {
    dictBtnElById.addEventListener('click', () => {
      renderDictOnlyPanel();
      dictModal.open();
    });
  }

  // 아이콘 텍스트 기반 보조 트리거
  const menuButtons = document.querySelectorAll('.menu-list button span.material-symbols-outlined');
  menuButtons.forEach(spanEl => {
    const label = spanEl.textContent.trim();
    if (label === 'settings') {
      spanEl.parentElement.addEventListener('click', () => {
        settingManager.switchTab('general');
        settingModal.open();
      });
    } else if (label === 'box') {
      spanEl.parentElement.addEventListener('click', () => {
        renderDictOnlyPanel();
        dictModal.open();
      });
    }
  });
};

let uploadEventsInitialized = false;

// 파일 업로드 이벤트 설정 함수
const setupFileUploadEvents = () => {
  if (uploadEventsInitialized) return;
  uploadEventsInitialized = true;

  const dictFileInput = document.getElementById('dict-file');
  const dictDropBtn = document.getElementById('dict-drop-btn');
  const dropzone = document.getElementById('dict-dropzone');

  if (dictDropBtn && dictFileInput) {
    dictDropBtn.addEventListener('click', () => dictFileInput.click());
  }

  if (dictFileInput) {
    dictFileInput.addEventListener('change', async (event) => {
      const file = event.target.files[0];
      if (!file) return;
      await uploadDictionary(file);
      event.target.value = '';
    });
  }

  if (dropzone) {
    // 버튼 위 드래그도 반응하도록 버튼에도 동일 처리
    const hoverOn = () => {
      dropzone.classList.add('drag-over');
    };
    const hoverOff = () => {
      dropzone.classList.remove('drag-over');
    };
    dropzone.addEventListener('dragover', (e) => {
      e.preventDefault();
      hoverOn();
    });
    dropzone.addEventListener('dragleave', () => {
      hoverOff();
    });
    dropzone.addEventListener('drop', async (e) => {
      e.preventDefault();
      hoverOff();
      const files = e.dataTransfer.files;
      if (files && files.length) {
        if (files.length === 1) {
          await uploadDictionary(files[0]);
        } else {
          await uploadMultipleDictionaries(files);
        }
      }
    });
    if (dictDropBtn) {
      dictDropBtn.addEventListener('dragover', (e) => { e.preventDefault(); e.stopPropagation(); hoverOn(); });
      dictDropBtn.addEventListener('dragleave', (e) => { e.stopPropagation(); hoverOff(); });
      dictDropBtn.addEventListener('drop', async (e) => {
        e.preventDefault();
        e.stopPropagation();
        hoverOff();
        const files = e.dataTransfer.files;
        if (files && files.length) {
          if (files.length === 1) {
            await uploadDictionary(files[0]);
          } else {
            await uploadMultipleDictionaries(files);
          }
        }
      });
    }
  }
};

// 키보드 이벤트 설정 함수
const setupKeyboardEvents = () => {
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      const settingModalEl = document.getElementById('setting-modal');
      const dictModalEl = document.getElementById('dict-modal');
      
      if (settingModalEl && !settingModalEl.classList.contains('hidden')) {
        settingModal.close();
      } else if (dictModalEl && !dictModalEl.classList.contains('hidden')) {
        dictModal.close();
      }
    }
  });
};