import socket
import threading
import time

import webview

from app import run_saturn_server


APP_TITLE = "SATURN Control"
HOST = "127.0.0.1"
PORT = 5000
URL = f"http://localhost:{PORT}"


def wait_for_server(timeout=12):
    started_at = time.monotonic()
    while time.monotonic() - started_at < timeout:
        try:
            with socket.create_connection((HOST, PORT), timeout=0.35):
                return True
        except OSError:
            time.sleep(0.1)
    return False


def start_server_thread():
    server_thread = threading.Thread(
        target=run_saturn_server,
        kwargs={"open_browser": False, "host": HOST, "port": PORT},
        daemon=True,
    )
    server_thread.start()
    return server_thread


def main():
    start_server_thread()
    if wait_for_server():
        window = webview.create_window(
            APP_TITLE,
            URL,
            width=1440,
            height=920,
            min_size=(1100, 720),
            confirm_close=True,
        )
    else:
        window = webview.create_window(
            APP_TITLE,
            html="""
            <body style="margin:0;background:#07111f;color:#e7f0ff;font-family:Segoe UI,Arial,sans-serif;">
              <main style="max-width:720px;margin:12vh auto;padding:32px;">
                <h1>SATURN no pudo iniciar</h1>
                <p>No se pudo abrir el servidor local en http://localhost:5000.</p>
                <p>Probá ejecutar <strong>SATURN-Control-Debug.exe</strong> para ver el error.</p>
              </main>
            </body>
            """,
            width=900,
            height=560,
            min_size=(720, 420),
        )
    webview.start(debug=False)
    return window


if __name__ == "__main__":
    main()
