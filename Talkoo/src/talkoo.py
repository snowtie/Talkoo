import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import config
from utils.logger import error, debug, info
from utils.error_codes import ErrorCode
from translation_manager import trans_start

class Talkoo:
    def __init__(self):
        try:
            if config.model_type == 3:
                model_name = "facebook/nllb-200-3.3B"
                info("모델 설정 : nllb-200-3.3B.")
            elif config.model_type == 2:
                model_name = "facebook/nllb-200-1.3B"
                info("모델 설정 : nllb-200-1.3B.")
            elif config.model_type == 1:
                model_name = "facebook/nllb-200-distilled-600M"
                info("모델 설정 : nllb-200-600M.")
            else:
                model_name = "facebook/nllb-200-distilled-600M"
                error("모델 입력 값 오류, 모델 nllb-200-600M으로 초기화.", None, ErrorCode.MODEL_INPUT)
        except Exception as e:
            error("예상을 벗어난 오류 발생, 확인 요함.", e, ErrorCode.UNKNOWN)
            exit()

        try:
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            info("토크나이저 로드 완료.")
        except Exception as e:
            error("토크나이저 로드 실패. 모델 이름 또는 네트워크 연결 확인 필요.", e, ErrorCode.TOKENIZER_LOAD_FAIL)
            exit()

        if config.device_map == 0:
            if config.model_device == 0 and torch.cuda.is_available():
                self.actual_device = "cuda"
                info("GPU 장치 설정 완료!")
            else:
                # ▼▼▼ 여기에 self.actual_device 선언을 추가해야 합니다 ▼▼▼
                self.actual_device = "cpu"
                info("CPU 장치 설정 완료!")
            
            try:
                self.base_model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
                info("베이스 모델 로드 완료.")
                self.base_model.to(self.actual_device)
                info(f"모델의 위치를 설정된 위치({self.actual_device})로 옮겼습니다.")
            except Exception as e:
                error("베이스 모델 로드 또는 이동 실패.", e, ErrorCode.BASE_MODEL_LOAD_FAIL)
                exit()

        elif config.device_map == 1:
            try:
                self.base_model = AutoModelForSeq2SeqLM.from_pretrained(model_name, device_map=config.device_map)
                info("베이스 모델을 device_map=Auto로 로드 완료.")
                self.actual_device = self.base_model.device
            except Exception as e:
                error("Auto device_map 모델 로드 실패.", e, ErrorCode.AUTO_DEVICE_MAP_FAIL)
                exit()
        else:
            error("오류, 디바이스 맵 입력값이 잘못 되었습니다.", None, ErrorCode.DEVICE_MAP_INPUT)
            exit()
            
        info(f"현재 모델 로딩 위치: {self.base_model.device}")