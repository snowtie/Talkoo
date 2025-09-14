from enum import IntEnum

class ErrorCode(IntEnum):
    UNKNOWN = -1  # 원인을 알 수 없는 오류
    MODEL_INPUT = 1  # 모델 입력 값 오류
    DEVICE_MAP_INPUT = 2  # 디바이스 맵 입력값 오류
    MODEL_TRANSLATION = 5  # 모델 번역 오류
    GEMINI_API_ERROR = 7 # 제미니 API 오류
    TOKENIZER_LOAD_FAIL = 10  # 토크나이저 로드 실패
    BASE_MODEL_LOAD_FAIL = 11  # 베이스 모델 로드 또는 이동 실패
    AUTO_DEVICE_MAP_FAIL = 12  # Auto device_map 로드 실패
    TKDIC_NOT_FOUND = 20  # 선택한 사전이 존재하지 않음
    TKDIC_PROCESS_ERROR = 21  # tkdic 처리 중 오류
    TRANSLATION_FAILED = 23  # 번역 실패