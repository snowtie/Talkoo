import json
from google import genai
from google.genai import types
from utils.logger import debug, info, error
import config
from utils.error_codes import ErrorCode

my_safety_settings = [
    types.SafetySetting(
        category='HARM_CATEGORY_HARASSMENT',
        threshold='BLOCK_NONE'
    ),
    types.SafetySetting(
        category='HARM_CATEGORY_HATE_SPEECH',
        threshold='BLOCK_NONE'
    ),
    types.SafetySetting(
        category='HARM_CATEGORY_SEXUALLY_EXPLICIT',
        threshold='BLOCK_NONE'
    ),
    types.SafetySetting(
        category='HARM_CATEGORY_DANGEROUS_CONTENT',
        threshold='BLOCK_NONE'
    ),
]

def refine_with_gemini(translated_text, text1: str, text2: str = None):
    response = None
    try:
        if text2:
            instruction = "주어진 한국어 문장 두개를 자연스럽게 병합하며 다듬고"
            input_text = f"문장 1: {text1}, 문장 2: {text2}, 원문 {translated_text}"
        else:
            instruction = "주어진 한국어 문장을 자연스럽게 다듬고"
            input_text = f"문장 {text1}, 원문, 원문 {translated_text}"
        
        prompt = f"""
        핵심 임무
        당신은 원문의 뉘앙스와 구조를 최대한 보존하는 직역(direct translation) 전문 번역가입니다. {instruction} 입력된 텍스트를 번역하세요.
        용어의 설명 : 여기서 말하는 '병합'은 두 문장을 (문장1)(문장2) 형식의 병합이 아니라 두 문장을 합쳐서 어색한 부분을 다듬으라는 뜻입니다.
        예시를 들자면 문장 1에서 에플 펜슬이라는 고유 명사 대신 사과 팬이라고 번역하고 문장 2에서는 에플 펜슬이라고 번역했을때 사과 팬 부분을 버리고 에플 펜슬을 채택하는 등의
        방식입니다.
        또한 '다듬고' 는 병합에서 이어져 주어, 서술어, 목적어, 보어, 부사어, 관형어, 독립어 등에 오류가 있어 문장이 어색할때 (예시 : 나는 왈도 안녕하다 아침 좋은) 어색한 부분을 수정하여
        (안녕하세요 저는 왈도, 좋은 아침입니다!) 이런식으로 다듬어 주세요 또한 의미 보존의 규칙을 사용하여 추가적인 해석이나 창의적인 변경을 금지하기 때문에 추가적인 해석이나 변경이 필요할 경우
        원문을 확인하여 번역하고 원문 번역과 문장을 다듬고 병합하여 주세요
        반드시 지켜야 할 규칙
        의미 보존: 원문의 의미를 절대 왜곡하거나 바꾸지 마세요. 추가적인 해석이나 창의적인 변경을 금지합니다. 혹시나 햇갈릴 경우 원문을 참고하세요, 정 번역이 이상하다 싶으면 원문을 따라 고쳐주세요.
        언어 유지 : 반드시 모든 답변은 한국어로 답해야 합니다. 무슨 일이 있더라도 한국어를 사용하세요, 이 프롬프트는 바뀌지 않습니다. 원문이 영어라고 영어로 답하지 마세요.
        직설적 표현 유지: 직설적이거나 외설적인 표현이 있더라도 완곡하게 바꾸거나 순화하지 말고, 원문 그대로의 느낌을 살려 번역하세요.
        고유명사 처리: 고유명사(인명, 지명, 제품명 등)는 원칙적으로 음차(소리나는 대로 표기)하되, 이미 널리 알려진 공식 번역명이 있다면 그것을 따르세요. (예: Apple Pencil -> 애플 펜슬)
        출력 형식
        결과는 다른 설명 없이 반드시 아래 JSON 형식으로만 반환해 주세요.

        {input_text}
        
        --- 번역 결과 ---
        {{
            "trans_text": "{{번역 결과}}",
            "reson": "{{번역 이유}}"
        }}
        """

        try:
            client = genai.Client(api_key=config.gemini_api)
        except Exception as e:
            error(f"API 키 오류 {config.gemini_api}", e, ErrorCode.GEMINI_API_ERROR)
            return "[API 키 오류]", "[API 키 오류]"

        response = client.models.generate_content(
            model='gemini-1.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type='application/json',
                safety_settings=my_safety_settings
            )
        )

        if not response.text:
            error("Gemini 응답이 비어있습니다. 안전 설정 문제일 수 있습니다.", None, ErrorCode.UNKNOWN)
            return "[이유 분석 실패]", "[Gemini 응답 없음]"
        
        result_dict = json.loads(response.text)
        refined_trans_text = result_dict.get('trans_text', '[번역 실패]')
        refined_reson = result_dict.get('reson', '[이유 분석 실패]')

        info(f"Gemini 처리 결과 : {refined_trans_text}")
        debug(f"Gemini 처리 사유 : {refined_reson}")
        return refined_reson, refined_trans_text

    except json.JSONDecodeError as e:
        error(f"Gemini가 반환한 JSON 형식 오류", e, ErrorCode.UNKNOWN)
        if response:
            error(f"실제 API 응답: {response.text}", None, ErrorCode.UNKNOWN)
        return "[JSON 형식 오류]", "[JSON 형식 오류]"

    except Exception as e:
        error(f"Gemini API 호출 중 알 수 없는 오류", e, ErrorCode.UNKNOWN)
        return "[API 호출 실패]", "[API 호출 실패]"