import socket
import sys
from pathlib import Path

HOST = "127.0.0.1"
PORT = 4434


def enviar_archivo_a_maya(file_path: str):
    safe_path = str(file_path).replace("\\", "/")
    maya_cmd = f"exec(open(r'{safe_path}', encoding='utf-8').read())"
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))
            s.send(f'python("{maya_cmd}")\r\n'.encode())
            print(f"✅ Ejecutado en Maya con UTF-8: {safe_path}")
    except Exception as e:
        print("❌ Error:", e)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("⚠️ Pasa el archivo .py como argumento")
        sys.exit(1)

    file_path = Path(sys.argv[1]).resolve()
    enviar_archivo_a_maya(file_path)
