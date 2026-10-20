import socket
import uvicorn
import os
import sys

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

if __name__ == "__main__":
    local_ip = get_local_ip()
    print("=====================================================")
    print("  Starting Medical Diary Application...")
    print("  Local access:         http://127.0.0.1:8000")
    if local_ip != "127.0.0.1":
        print(f"  Share on your Wi-Fi:  http://{local_ip}:8000")
    print("=====================================================")
    uvicorn.run("src.app:app", host="0.0.0.0", port=8000, reload=True)
