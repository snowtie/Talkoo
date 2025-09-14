from pathlib import Path
from utils.logger import debug, info, error
from utils.error_codes import ErrorCode
import config

tkdic_select = None

def get_tkdic_list(path_str: str) -> list:
    path = Path(path_str)
    tkdic_files = [file.name for file in path.glob('*.tkdic')]
    return tkdic_files

def select_tkdic(selected_filename: str):
    global tkdic_select

    available_dics = get_tkdic_list(config.tkdic_path)
    info(f"사용 가능한 사전: {available_dics}")

    if selected_filename in available_dics:
        tkdic_select = selected_filename
        info(f"'{selected_filename}' 사전이 선택되었습니다.")
        return True
    else:
        error(f"선택한 사전 '{selected_filename}'이 존재하지 않습니다.", None, ErrorCode.TKDIC_NOT_FOUND)
        return False