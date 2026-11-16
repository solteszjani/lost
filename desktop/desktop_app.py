from __future__ import annotations
import os, sys, time, socket, threading
from pathlib import Path
from urllib.request import urlopen
import uvicorn
import webview

def resource_path(*parts: str) -> Path:
    base = Path(getattr(sys, '_MEIPASS', Path(__file__).resolve().parent))
    return base.joinpath(*parts)

def user_data_dir() -> Path:
    base = Path(os.getenv('LOCALAPPDATA', str(Path.home() / 'AppData' / 'Local')))
    path = base / 'Talaltam'
    path.mkdir(parents=True, exist_ok=True)
    return path

def free_port() -> int:
    with socket.socket() as sock:
        sock.bind(('127.0.0.1', 0))
        return int(sock.getsockname()[1])

def main() -> None:
    project = resource_path('server')
    sys.path.insert(0, str(project))
    os.environ['TALALTAM_DATA_DIR'] = str(user_data_dir())
    from app.main import app
    port = free_port()
    server = uvicorn.Server(uvicorn.Config(app, host='127.0.0.1', port=port, log_level='error', access_log=False))
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    url = f'http://127.0.0.1:{port}'
    for _ in range(150):
        if server.started:
            try:
                with urlopen(url + '/health', timeout=1) as response:
                    if response.status == 200:
                        break
            except Exception:
                pass
        time.sleep(0.1)
    else:
        raise RuntimeError('Az alkalmazás háttérrendszere nem indult el.')
    webview.create_window('Találtam', url, width=1280, height=820, min_size=(900, 620), text_select=True)
    try:
        webview.start()
    finally:
        server.should_exit = True
        thread.join(timeout=5)

if __name__ == '__main__':
    main()
