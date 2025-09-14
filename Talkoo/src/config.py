import os
from dotenv import load_dotenv


def load_config() -> None:
    load_dotenv(override=True)

    global model_type, model_device, device_map
    global debug_mod, log_path
    global nomal_trans, per_post_trans, gemini_integration, gemini_api
    global tkdic_path, tkdic_list, tkdic_select
    global src_lang, tgt_lang

    # - < 공통 함수들 > -
    model_type = int(os.getenv("MODEL_TYPE", 1))  # 1~3번, 숫자가 높을수록 모델 크기가 커짐(성능 상승)
    model_device = int(os.getenv("MODEL_DEVICE", 1))  # 0 = 그래픽카드, 1 = CPU
    device_map = int(os.getenv("DEVICE_MAP", 0))  # 0 = 비활성화, 1 = 활성화

    # - < - 로그 관련 함수 - > -
    debug_mod = os.getenv("DEBUG_MOD", "True").lower() == "true"
    log_path = os.getenv("LOG_PATH", "log")

    # - < 번역 관련 함수들 > -
    # - < 번역 활성화 함수들 > -
    nomal_trans = os.getenv("NOMAL_TRANS", "True").lower() == "true"
    per_post_trans = os.getenv("PER_POST_TRANS", "True").lower() == "true"
    gemini_integration = os.getenv("GEMINI_INTEGRATION", "False").lower() == "true"
    gemini_api = os.getenv("GEMINI_API_KEY")

    # - < 커스텀 사전 관련 함수들 > -
    tkdic_path = os.getenv("TKDIC_PATH", "tkdics")
    tkdic_list = []
    tkdic_select = os.getenv("TKDIC_SELECT", "dd.tkdic")

    # -< 번역 함수(설정에 없음) >-
    src_lang = os.getenv("SRC_LANG", "eng_Latn")
    tgt_lang = os.getenv("TGT_LANG", "kor_Hang")


def reload_config() -> None:
    load_config()


# 초기 로드
load_config()
