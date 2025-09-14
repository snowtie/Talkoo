import config
from translator.first_translation import first_translation
from translator.second_translation import second_translation
from translator.gemini_integration import refine_with_gemini
from utils.logger import error, info, debug
from utils.error_codes import ErrorCode

def trans_start(translated_text: str, tokenizer, base_model, actual_device):
    nomal_text = ""
    per_text = ""
    refined_reson = ""
    refined_trans_text = ""

    try:
        if config.nomal_trans:
            nomal_text = first_translation(translated_text, tokenizer, base_model, actual_device)
        else:
            info("기본 모델 번역 비활성화")

        if config.per_post_trans:
            per_text = second_translation(translated_text, config.tkdic_path, config.tkdic_select, tokenizer, base_model, actual_device)
        else:
            info("전처리 후처리 번역 비활성화")

        if config.gemini_integration:
            refined_reson, refined_trans_text = refine_with_gemini(translated_text, nomal_text, per_text)
        else:
            info("Gemini 통합 비활성화")

    except Exception as e:
        error("번역 실패.", e, ErrorCode.TRANSLATION_FAILED)

    return nomal_text, per_text, refined_reson, refined_trans_text