import pathlib
import config
from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from talkoo import Talkoo
from customDICT.dict_main import get_tkdic_list, select_tkdic
from customDICT.tkdic_paser import parse_tkdic
from pydantic import BaseModel, Field
from typing import Any

from translation_manager import trans_start

app = FastAPI()
STATIC_DIR = pathlib.Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

class TranslationRequest(BaseModel):
    text: str = Field(..., example="(기본문장) I want to kill two birds with one stone.")

class TranslationResponse(BaseModel):
    status: str
    modelTrans: str
    prePostTrans: str
    geminiReson: str
    geminiIntegra: str

@app.post("/translate/", response_model=TranslationResponse)
def run_api_translation(translation_data: TranslationRequest, http_request: Request):
    
    tokenizer = http_request.app.state.tokenizer
    base_model = http_request.app.state.base_model
    actual_device = http_request.app.state.device
    
    try:
        original_text = translation_data.text
        nomal_text, per_text, refined_reson, refined_trans_text = trans_start(original_text, tokenizer, base_model, actual_device)

        return TranslationResponse(status="success", modelTrans=nomal_text, prePostTrans=per_text, geminiReson=refined_reson, geminiIntegra=refined_trans_text)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class SettingResponse(BaseModel):
    model_type: int
    model_device: int
    device_map: int
    debug_mod: bool

@app.post("/setting/", response_model=SettingResponse)
def update_setting(request: SettingResponse):
    config.model_type = request.model_type
    config.model_device = request.model_device
    config.device_map = request.device_map
    config.debug_mod = request.debug_mod

    return SettingResponse(
        model_type=config.model_type,
        model_device=config.model_device,
        device_map=config.device_map,
        debug_mod=config.debug_mod
    )

@app.get("/setting/", response_model=SettingResponse)
def get_setting():
    return SettingResponse(
        model_type=config.model_type,
        model_device=config.model_device,
        device_map=config.device_map,
        debug_mod=config.debug_mod
    )
    
class TransSettingResponse(BaseModel):
    nomal_trans: bool
    per_post_trans: bool
    gemini_integration: bool
    gemini_api: str | None = None
    # NOTE: 경로/선택은 서버 상태를 신뢰. 클라이언트가 보낼 때 무시할 수 있도록 optional 처리
    tkdic_path: str | None = None
    tkdic_list: list[str] | None = None
    tkdic_select: str | None = None
    
@app.post("/setting/trans/", response_model=TransSettingResponse)
def update_trans_settings(request: TransSettingResponse):
    config.nomal_trans = request.nomal_trans
    config.per_post_trans = request.per_post_trans
    config.gemini_integration = request.gemini_integration
    config.gemini_api = request.gemini_api
    # tkdic_* 값은 클라이언트에서 넘어와도 서버 기준을 유지

    return TransSettingResponse(
        nomal_trans=config.nomal_trans,
        per_post_trans=config.per_post_trans,
        gemini_integration=config.gemini_integration,
        gemini_api=config.gemini_api,
        tkdic_path=config.tkdic_path,
        tkdic_list=get_tkdic_list(config.tkdic_path),
        tkdic_select=config.tkdic_select
    )

@app.get("/setting/trans/", response_model=TransSettingResponse)
def get_trans_settings():
    return TransSettingResponse(
        nomal_trans=config.nomal_trans,
        per_post_trans=config.per_post_trans,
        gemini_integration=config.gemini_integration,
        gemini_api=config.gemini_api,
        tkdic_path=config.tkdic_path,
        tkdic_list=get_tkdic_list(config.tkdic_path),
        tkdic_select=config.tkdic_select
    )


class ReloadResponse(BaseModel):
    status: str


@app.post("/setting/reload/config/", response_model=ReloadResponse)
def config_reload_settings():
    config.reload_config()
    return ReloadResponse(status="config_reloaded")


class ReloadResponse(BaseModel):
    status: str


@app.post("/setting/reload/model/", response_model=ReloadResponse)
def model_reload_settings():
    Talkoo()
    return ReloadResponse(status="model_reloaded")


class DictionaryListResponse(BaseModel):
    dictionaries: list[str]


@app.get("/dict/list/", response_model=DictionaryListResponse)
def list_available_dictionaries():
    available_dics = get_tkdic_list(config.tkdic_path)
    return DictionaryListResponse(dictionaries=available_dics)
    
    
class SelectDictionaryRequest(BaseModel):
    filename: str

@app.post("/dict/select/")
def set_active_dictionary(request: SelectDictionaryRequest):
    success = select_tkdic(request.filename)
    
    if success:
        # 선택 성공 시 실제 사용되는 설정에도 반영
        config.tkdic_select = request.filename
        return {"status": "success", "selected_dictionary": config.tkdic_select}
    else:
        raise HTTPException(
            status_code=404, 
            detail=f"'{request.filename}' 사전을 찾을 수 없습니다."
        )

class UploadDictionaryResponse(BaseModel):
    status: str
    filename: str

class UploadDictionaryJsonRequest(BaseModel):
    filename: str
    content_base64: str
    overwrite: bool | None = False

@app.post("/dict/upload/", response_model=UploadDictionaryResponse)
def upload_dictionary_json(request: UploadDictionaryJsonRequest):
    try:
        filename = request.filename
        if not filename or not filename.endswith('.tkdic'):
            raise HTTPException(status_code=400, detail=".tkdic 파일만 업로드할 수 있습니다.")

        import base64
        try:
            content_bytes = base64.b64decode(request.content_base64)
        except Exception:
            raise HTTPException(status_code=400, detail="content_base64 디코딩 실패")

        save_path = pathlib.Path(config.tkdic_path)
        save_path.mkdir(parents=True, exist_ok=True)
        dest = save_path / filename
        if dest.exists() and not request.overwrite:
            raise HTTPException(status_code=409, detail="파일이 이미 존재합니다.")

        with open(dest, 'wb') as f:
            f.write(content_bytes)

        return UploadDictionaryResponse(status="success", filename=filename)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class DeleteDictionaryResponse(BaseModel):
    status: str
    filename: str

@app.delete("/dict/{filename}", response_model=DeleteDictionaryResponse)
def delete_dictionary(filename: str):
    try:
        if not filename.endswith('.tkdic'):
            raise HTTPException(status_code=400, detail="잘못된 파일명입니다.")
        file_path = pathlib.Path(config.tkdic_path) / filename
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="사전을 찾을 수 없습니다.")
        file_path.unlink()

        # 선택된 사전을 삭제했다면 선택 해제
        if config.tkdic_select == filename:
            config.tkdic_select = None

        return DeleteDictionaryResponse(status="success", filename=filename)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class DictEntryRequest(BaseModel):
    filename: str
    word: str
    kor: str
    fuzzy: int | None = None
    create_if_missing: bool | None = True
    main_fuzzy: int | None = 85

class DictEntryResponse(BaseModel):
    status: str
    filename: str

@app.post("/dict/entry/", response_model=DictEntryResponse)
def add_dict_entry(request: DictEntryRequest):
    try:
        filename = request.filename
        if not filename or not filename.endswith('.tkdic'):
            raise HTTPException(status_code=400, detail="파일명은 .tkdic 이어야 합니다.")
        if not request.word or not request.kor:
            raise HTTPException(status_code=400, detail="word와 kor는 필수입니다.")

        tk_path = pathlib.Path(config.tkdic_path)
        tk_path.mkdir(parents=True, exist_ok=True)
        dest = tk_path / filename

        if not dest.exists():
            if not request.create_if_missing:
                raise HTTPException(status_code=404, detail="사전 파일이 존재하지 않습니다.")
            # 새 파일 생성 시 main_fuzzy 헤더 작성
            with open(dest, 'w', encoding='utf-8') as f:
                header_val = request.main_fuzzy if isinstance(request.main_fuzzy, int) else 85
                f.write(f"main_fuzzy[{header_val}]\n\n")

        # 엔트리 추가
        lines = []
        lines.append(f"word[{request.word}]")
        lines.append(f"kor[{request.kor}]")
        if isinstance(request.fuzzy, int):
            lines.append(f"fuzzy[{request.fuzzy}]")
        entry_block = "\n".join(lines) + "\n\n"
        with open(dest, 'a', encoding='utf-8') as f:
            f.write(entry_block)

        return DictEntryResponse(status="success", filename=filename)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class DictEntriesResponse(BaseModel):
    filename: str
    main_fuzzy: int | None
    entries: list[dict[str, Any]]

@app.get("/dict/entries/{filename}", response_model=DictEntriesResponse)
def get_dict_entries(filename: str):
    try:
        if not filename.endswith('.tkdic'):
            raise HTTPException(status_code=400, detail="잘못된 파일명입니다.")
        file_path = pathlib.Path(config.tkdic_path) / filename
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="사전을 찾을 수 없습니다.")

        main_fuzzy, results = parse_tkdic(str(file_path))
        # 표준화: 필요한 키만 유지
        normalized = []
        for it in results or []:
            normalized.append({
                'word': it.get('word', ''),
                'kor': it.get('kor', ''),
                'fuzzy': it.get('fuzzy') if isinstance(it.get('fuzzy'), int) else None,
            })
        return DictEntriesResponse(filename=filename, main_fuzzy=main_fuzzy, entries=normalized)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ***** frontend templates routing
# SPA 형태로 만들 듯
@app.get("/{full_path:path}")
async def serve_spa(full_path: str):
    return FileResponse(f"{STATIC_DIR}/index.html")


@app.get("/health")
def health():
    return {"status": "ok"}