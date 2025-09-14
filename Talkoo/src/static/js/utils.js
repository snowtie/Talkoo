// ===== 유틸리티 함수 모음 =====

// 파일을 base64로 변환하는 함수
const toBase64 = (blob) => new Promise((resolve, reject) => {
  const reader = new FileReader();
  reader.onload = () => resolve(reader.result.split(',')[1]);
  reader.onerror = reject;
  reader.readAsDataURL(blob);
});

// 단일 사전 업로드
const uploadDictionary = async (file, showAlert = true) => {
  try {
    const content_base64 = await toBase64(file);
    let res = await fetch('/dict/upload/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ filename: file.name, content_base64, overwrite: false })
    });

    if (res.status === 409) {
      if (confirm(`${file.name} 이(가) 이미 있습니다. 덮어쓸까요?`)) {
        res = await fetch('/dict/upload/', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ filename: file.name, content_base64, overwrite: true })
        });
      }
    }

    if (res.ok) {
      if (typeof renderDictOnlyPanel === 'function') {
        await renderDictOnlyPanel();
      }
      if (showAlert) alert(`${file.name} 사전 업로드 완료`);
      return true;
    } else {
      return false;
    }
  } catch (error) {
    if (showAlert) alert('네트워크 오류');
    return false;
  }
};

// 여러 파일 업로드
const uploadMultipleDictionaries = async (files) => {
  let successCount = 0;
  for (const file of files) {
    const success = await uploadDictionary(file, false);
    if (success) successCount += 1;
  }

  if (typeof renderDictOnlyPanel === 'function') {
    await renderDictOnlyPanel();
  }
  if (successCount > 0) alert(`${successCount}개 사전 업로드 완료`);
  return successCount;
};

// HTML 이스케이프
const escapeHtml = (str) => {
  return String(str).replace(/[&<>"]/g, s => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[s]));
};


