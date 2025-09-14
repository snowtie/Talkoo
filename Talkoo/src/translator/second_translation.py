import torch
import re
from thefuzz import process, fuzz
from utils.logger import debug, info, error
from utils.error_codes import ErrorCode
from customDICT.tkdic_paser import parse_tkdic
import config

def tkdic_start(text: str, tk_path: str, tk_select: str):
    placeholder_map = {}
    placeholder_index = 0
    processed_text = text

    try:
        if tk_select is None:
            return text, {}

        main_fuzzy, base_dict = parse_tkdic(f"{tk_path}/{tk_select}")
        if not base_dict:
            return text, {}

        text_lower = processed_text.lower()
        text_words_clean = [word.strip('.,?!').lower() for word in processed_text.split()]

        for entry in base_dict:
            final_fuzzy_score = entry.get('fuzzy', main_fuzzy)
            custom_word_orig = entry.get('word', '').strip()
            custom_word_clean = custom_word_orig.lower()
            is_phrase = len(custom_word_clean.split()) > 1

            found = False
            if is_phrase:
                score = fuzz.partial_ratio(custom_word_clean, text_lower)
                if score >= final_fuzzy_score:
                    found = True
            else:
                match = process.extractOne(custom_word_clean, text_words_clean)
                if match and match[1] >= final_fuzzy_score:
                    found = True
            
            if found:
                placeholder_index += 1
                if placeholder_index > 99:
                    break
                
                placeholder = f"TkdicoTranslate{placeholder_index}"
                pattern = r'\b' + re.escape(custom_word_orig) + r'\b'
                processed_text = re.sub(pattern, placeholder, processed_text, flags=re.IGNORECASE)
                
                placeholder_map[placeholder] = entry.get('kor', '')
        
        return processed_text, placeholder_map

    except Exception as e:
        error(f"tkdic_start 처리 중 오류 발생", e, ErrorCode.TKDIC_PROCESS_ERROR)
        return text, {}

def post_processing(translated_text: str, placeholder_map: dict) -> str:
    final_text = translated_text
    for placeholder, original_word in placeholder_map.items():
        final_text = final_text.replace(placeholder, original_word)
    return final_text

def second_translation(translate_text: str, tk_path: str, tk_select: str, tokenizer, base_model, actual_device):
    try:
        preprocessed_text, placeholder_map = tkdic_start(translate_text, tk_path, tk_select)
        
        tokenizer.src_lang = config.src_lang
        inputs = tokenizer(preprocessed_text, return_tensors="pt", max_length=512, truncation=True).to(actual_device)
        
        with torch.no_grad():
            generated_tokens = base_model.generate(
                **inputs,
                forced_bos_token_id=tokenizer.convert_tokens_to_ids(config.tgt_lang),
                max_length=512
            )
        
        translated_by_model = tokenizer.batch_decode(generated_tokens, skip_special_tokens=True)[0]
        
        debug(f"NLLB 번역 결과 (후처리 전): {translated_by_model}")

        final_translation = post_processing(translated_by_model, placeholder_map)

        info(f"최종 번역 결과 (후처리 후): {final_translation}")
        
        return final_translation
    except Exception as e:
        error("second_translation 중 오류 발생", e, ErrorCode.MODEL_TRANSLATION)
        return "[번역 오류 발생]"