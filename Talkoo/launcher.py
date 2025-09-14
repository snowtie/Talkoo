from __future__ import annotations
import hashlib
import os
import sys
import subprocess
import time
from pathlib import Path
from shutil import which

def get_base_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent

BASE_DIR = get_base_dir()
RUNTIME_DIR = BASE_DIR / ".runtime"
VENV_DIR = RUNTIME_DIR / "venv"

if os.name == "nt":
    PY_EXE = VENV_DIR / "Scripts" / "python.exe"
else:
    PY_EXE = VENV_DIR / "bin" / "python3"

REQ_FILE = BASE_DIR / "requirements.txt"
REQ_HASH_FILE = RUNTIME_DIR / ".req_hash"
DEPS_MARK_FILE = RUNTIME_DIR / ".deps_ok"
LOCK_FILE = RUNTIME_DIR / ".lock"
HP_FILE = BASE_DIR / "HP.txt"
MAIN_FILE = BASE_DIR / "src" / "main.py"

def info(msg: str) -> None:
    print(f"[launcher] {msg}", flush=True)

def fail(msg: str, code: int = 1) -> None:
    print(f"[launcher:ERROR] {msg}", flush=True)
    time.sleep(0.5)
    sys.exit(code)

def file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()

def read_text(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8")
    except Exception:
        return None

def write_text(path: Path, data: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(data, encoding="utf-8")

def get_system_python() -> list[str]:
    if os.name == "nt":
        if which("py"):
            try:
                subprocess.check_call(
                    ["py", "-3.11", "-c", "print(1)"],
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=5
                )
                return ["py", "-3.11"]
            except Exception:
                pass
        p = which("python3.11")
        if p:
            return [p]
        if which("py"):
            try:
                subprocess.check_call(
                    ["py", "-3", "-c", "print(1)"],
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=5
                )
                return ["py", "-3"]
            except Exception:
                pass
        for exe in ("python.exe", "python3.exe"):
            p = which(exe)
            if p:
                return [p]
    else:
        for exe in ("python3.11", "python3", "python"):
            p = which(exe)
            if p:
                return [p]
    return []

def ensure_hp_file() -> None:
    if HP_FILE.exists():
        return
    write_text(HP_FILE, "127.0.0.1\n8000\n")
    info(f"HP.txt 생성: {HP_FILE} (기본값 127.0.0.1:8000)")

def acquire_lock() -> bool:
    RUNTIME_DIR.mkdir(parents=True, exist_ok=True)
    try:
        fd = os.open(LOCK_FILE, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        os.close(fd)
        return True
    except FileExistsError:
        return False

def release_lock() -> None:
    try:
        LOCK_FILE.unlink(missing_ok=True)
    except Exception:
        pass

def ensure_venv() -> None:
    pyvenv_cfg = VENV_DIR / "pyvenv.cfg"
    if pyvenv_cfg.exists() and PY_EXE.exists():
        return
    sys_py = get_system_python()
    if not sys_py:
        fail("시스템 파이썬(우선 3.11)을 찾지 못했습니다. Python 3.11을 설치하거나 'py -3.11' 사용 가능 상태여야 합니다.")
    info(f"venv 생성 중: {VENV_DIR}")
    RUNTIME_DIR.mkdir(parents=True, exist_ok=True)
    try:
        subprocess.check_call(sys_py + ["-m", "venv", str(VENV_DIR)])
    except subprocess.CalledProcessError as e:
        fail(f"venv 생성 실패: {e}")
    if not PY_EXE.exists():
        fail(f"venv 파이썬 경로를 찾을 수 없습니다: {PY_EXE}")
    try:
        subprocess.check_call([str(PY_EXE), "-m", "pip", "--version"],
                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError:
        try:
            subprocess.check_call([str(PY_EXE), "-m", "ensurepip", "--upgrade"])
        except subprocess.CalledProcessError as e:
            fail(f"ensurepip 실패: {e}")

def req_hash() -> str:
    if not REQ_FILE.exists():
        return ""
    return file_sha256(REQ_FILE)

def saved_hash() -> str:
    return (read_text(REQ_HASH_FILE) or "").strip()

def write_hash(h: str) -> None:
    write_text(REQ_HASH_FILE, h)

def pip_check_ok() -> bool:
    try:
        subprocess.check_call([str(PY_EXE), "-m", "pip", "check"],
                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except subprocess.CalledProcessError:
        return False

def install_requirements(force: bool = False) -> None:
    if not REQ_FILE.exists():
        info("requirements.txt 가 존재하지 않습니다. 종속성 설치를 건너뜁니다.")
        write_text(DEPS_MARK_FILE, "ok:no-req")
        return
    h_now = req_hash()
    h_saved = saved_hash()
    if (not force) and h_now == h_saved and pip_check_ok():
        info("이미 종속성이 설치되어 종속성 설치를 건너뜁니다.")
        write_text(DEPS_MARK_FILE, f"ok:{h_now}")
        return
    info(f"종속성 설치: {REQ_FILE}")
    try:
        subprocess.check_call([str(PY_EXE), "-m", "pip", "install", "-r", str(REQ_FILE)])
    except subprocess.CalledProcessError as e:
        fail(f"종속성 설치 실패: {e}\n인터넷/프록시/사내 미러를 확인하세요.")
    if not pip_check_ok():
        fail("pip check 실패: 의존성 충돌 또는 손상 가능성. requirements.txt를 점검하세요.")
    write_hash(h_now)
    write_text(DEPS_MARK_FILE, f"ok:{h_now}")

def fast_path_ready() -> bool:
    if not (VENV_DIR.exists() and PY_EXE.exists()):
        return False
    if not REQ_FILE.exists():
        return True
    h_now = req_hash()
    if not h_now:
        return True
    if h_now != saved_hash():
        return False
    if not pip_check_ok():
        return False
    mark = (read_text(DEPS_MARK_FILE) or "")
    return mark.strip() == f"ok:{h_now}"

def run_app() -> int:
    if not MAIN_FILE.exists():
        fail(f"메인 파일을 찾을 수 없음: {MAIN_FILE}\n런처와 같은 폴더에 'src/main.py'가 있는지 확인하세요.")
    cmd = [str(PY_EXE), str(MAIN_FILE)]
    info(f"앱 실행: {' '.join(cmd)}")
    return subprocess.call(cmd)

def main() -> None:
    info(f"작업 폴더: {BASE_DIR}")
    ensure_hp_file()
    if fast_path_ready():
        info("준비 완료 감지 → 설치/검증 스킵하고 바로 실행")
        rc = run_app()
        info(f"앱 종료 (코드 {rc})")
        sys.exit(rc)
    got_lock = acquire_lock()
    if not got_lock:
        info("다른 프로세스가 초기화 중 → 잠시 대기")
        for _ in range(60):
            time.sleep(1)
            if fast_path_ready():
                break
        else:
            fail("초기화 락 대기 시간 초과")
        rc = run_app()
        info(f"앱 종료 (코드 {rc})")
        sys.exit(rc)
    try:
        ensure_venv()
        need_force = not (read_text(DEPS_MARK_FILE) or "").startswith("ok:")
        install_requirements(force=need_force)
    finally:
        release_lock()
    rc = run_app()
    info(f"앱 종료 (코드 {rc})")
    sys.exit(rc)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        info("사용자 중단")
        sys.exit(130)