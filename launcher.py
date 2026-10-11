import sys
import threading
import time
import webbrowser
from pathlib import Path

from streamlit.web import cli as stcli


HOST = "127.0.0.1"
PORT = 8501
URL = f"http://{HOST}:{PORT}"


def abrir_navegador():
    """Abre o dashboard após o servidor local iniciar."""
    time.sleep(2.5)
    webbrowser.open(URL)


def main():
    base_dir = Path(__file__).resolve().parent
    painel = base_dir / "painel.py"

    if not painel.exists():
        raise FileNotFoundError(
            f"Arquivo do dashboard não encontrado: {painel}"
        )

    threading.Thread(
        target=abrir_navegador,
        daemon=True
    ).start()

    sys.argv = [
        "streamlit",
        "run",
        str(painel),
        "--server.address",
        HOST,
        "--server.port",
        str(PORT),
        "--server.headless",
        "true",
        "--browser.gatherUsageStats",
        "false",
    ]

    sys.exit(stcli.main())


if __name__ == "__main__":
    main()
