import torch
import config
from utils.logger import error, debug, info
from utils.error_codes import ErrorCode

def first_translation(translate_text: str, tokenizer, base_model, actual_device):
    try:
        debug("모델 번역 실행중")
        
        tokenizer.src_lang = config.src_lang

        inputs = tokenizer(translate_text, return_tensors="pt", max_length=512, truncation=True)
        inputs = inputs.to(actual_device)

        debug(f"Tokenizer의 src_lang 설정: {tokenizer.src_lang}")
        debug(f"Forced BOS Token ID: {tokenizer.convert_tokens_to_ids(config.tgt_lang)}")
        debug(f"Forced BOS Token (디코딩): {tokenizer.decode(tokenizer.convert_tokens_to_ids(config.tgt_lang))}")
        
        with torch.no_grad():
            generated_tokens = base_model.generate(
                **inputs,
                forced_bos_token_id=tokenizer.convert_tokens_to_ids(config.tgt_lang),
                max_length=512,
                num_return_sequences=1,
                temperature=0.7,
                do_sample=False
            )
        
        translation = tokenizer.batch_decode(generated_tokens, skip_special_tokens=True)[0]
        info(f"모델 번역 : {translation}")

        return translation
        
    except Exception as e:
        error("모델 번역 오류", e, ErrorCode.MODEL_TRANSLATION)
        return "[번역 오류 발생]"