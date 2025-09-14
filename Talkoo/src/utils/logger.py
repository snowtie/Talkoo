import datetime, os, inspect
from colorama import Fore, Style
import config

# ─── ① 프로그램 시작 시각으로 Crash 로그 파일명 생성 ───
_run_start = datetime.datetime.now()
_crash_logfile = os.path.join(
    config.log_path,
    f"CrashHandler-{_run_start.strftime('%Y-%m-%d_%H-%M-%S')}.log"
)

def _caller_info():
    frame = inspect.currentframe().f_back.f_back
    filename = os.path.basename(frame.f_code.co_filename)
    lineno   = frame.f_lineno
    return filename, lineno

def _format_text(text):
    if isinstance(text, list):
        return " ".join(str(x) for x in text)
    return str(text)

def insert_log(text, type):  # 1=error, 2=debug, 3=info
    os.makedirs(config.log_path, exist_ok=True)

    if type == 1:
        full_path = _crash_logfile
    elif type == 2:
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        full_path = os.path.join(config.log_path, f"Debug-{today}.log")
    elif type == 3:
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        full_path = os.path.join(config.log_path, f"{today}.log")
    else:
        raise ValueError("Unknown log type")

    if type == 1 or not os.path.exists(full_path):
        if config.debug_mod:
            print(f"로그 파일 미확인, 생성: {full_path}")
        with open(full_path, 'a', encoding='utf-8'):
            pass

    with open(full_path, 'a', encoding='utf-8') as f:
        f.write(text + "\n")

def error(text, e, code):
    fn, ln = _caller_info()
    text = _format_text(text)
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # prefix는 기본 색상, text 부분만 RED
    print(f"[Error] {now} {fn}, line:{ln} {Fore.RED}{text} {e} {Style.RESET_ALL}\nError codeㅣ오류 코드 : {code}")
    print("해당 오류 관련 로그 CrashHandler가 생성되었습니다.\n문의는 해당 오류의 CrashHandler를 제출하여 주시면 빠른 처리가 가능합니다.")
    insert_log(f"[Error] {now} {fn}, line:{ln} {text} {e}\nError codeㅣ오류 코드 : {code}", 1)

def debug(text):
    if config.debug_mod:
        fn, ln = _caller_info()
        text = _format_text(text)
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # text 부분만 GREEN
        print(f"[Debug] {now} {fn}, line:{ln} {Fore.GREEN}{text}{Style.RESET_ALL}")
        insert_log(f"[Debug] {now} {fn}, line:{ln} {text}", 2)

def info(text):
    fn, ln = _caller_info()
    text = _format_text(text)
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # text 부분만 CYAN
    print(f"[Info]  {now} {fn}, line:{ln} {Fore.CYAN}{text}{Style.RESET_ALL}")
    insert_log(f"[Info]  {now} {fn}, line:{ln} {text}", 3)