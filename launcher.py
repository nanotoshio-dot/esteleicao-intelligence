"""Local Windows entry point with diagnostics and health-gated browser launch."""
import logging
import multiprocessing
import os
import socket
import sys
import threading
import time
import urllib.request
import webbrowser
from pathlib import Path

os.environ["STREAMLIT_GLOBAL_DEVELOPMENT_MODE"] = "false"
os.environ["STREAMLIT_BROWSER_GATHER_USAGE_STATS"] = "false"
HOST = "127.0.0.1"


def get_app_dir():
    return Path(sys._MEIPASS) if getattr(sys, "frozen", False) else Path(__file__).resolve().parent


def escolher_porta(preferida=8501):
    with socket.socket() as sock:
        try:
            sock.bind((HOST, preferida))
        except OSError:
            sock.bind((HOST, 0))
        return sock.getsockname()[1]


def erro_windows(mensagem):
    logging.error(mensagem)
    if sys.platform == "win32" and os.environ.get("ESTELEICAO_NO_BROWSER") != "1":
        import ctypes
        ctypes.windll.user32.MessageBoxW(None, mensagem, "ESTELEIÇÃO — erro de inicialização", 0x10)


def abrir_navegador(url, log_file):
    for _ in range(120):
        try:
            with urllib.request.urlopen(url + "/_stcore/health", timeout=1) as resposta:
                if resposta.status == 200:
                    logging.info("Servidor pronto: %s", url)
                    if os.environ.get("ESTELEICAO_NO_BROWSER") != "1":
                        webbrowser.open(url)
                    return
        except OSError:
            pass
        time.sleep(.5)
    erro_windows(f"O servidor local não iniciou a tempo. Consulte {log_file}")


def main():
    from paths import LOG_DIR
    log_file = LOG_DIR / "startup.log"
    # windowed PyInstaller sets stdout/stderr to None; libraries still print.
    stream = log_file.open("a", encoding="utf-8", buffering=1)
    sys.stdout = sys.stderr = stream
    logging.basicConfig(level=logging.INFO, stream=stream, force=True,
                        format="%(asctime)s %(levelname)s %(message)s")
    try:
        app = get_app_dir() / "dashboard.py"
        if not app.is_file():
            raise FileNotFoundError(f"Dashboard não encontrado: {app}")
        porta = escolher_porta(int(os.environ.get("ESTELEICAO_PORT", "8501")))
        url = f"http://{HOST}:{porta}"
        logging.info("Iniciando %s em %s", app, url)
        threading.Thread(target=abrir_navegador, args=(url, log_file), daemon=True).start()
        from streamlit.web import cli as stcli
        sys.argv = ["streamlit", "run", str(app), "--global.developmentMode=false",
                    f"--server.address={HOST}", f"--server.port={porta}", "--server.headless=true",
                    "--server.fileWatcherType=none", "--browser.gatherUsageStats=false"]
        result = stcli.main()
        return result or 0
    except Exception:
        logging.exception("Falha de inicialização")
        erro_windows(f"Não foi possível iniciar o ESTELEIÇÃO. Consulte o diagnóstico em {log_file}")
        return 1


if __name__ == "__main__":
    multiprocessing.freeze_support()
    sys.exit(main())
