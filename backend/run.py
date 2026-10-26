import os
import sys
import socket
from pathlib import Path

if sys.platform == 'win32' and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

BACKEND_DIR = Path(__file__).resolve().parent

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app import create_app

app = create_app(os.getenv('FLASK_ENV', 'development'))


def get_local_ip():
    """Detects current machine IP on local Wi-Fi / LAN."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return '127.0.0.1'


if __name__ == '__main__':
    local_ip = get_local_ip()
    port = int(os.getenv('PORT', 5000))

    print("=" * 68)
    print(" 🚀 Student Placement Management System (SPMS)")
    print(" 🐘 Database: Neon Serverless PostgreSQL")
    print(" ☁️  Cloud: Ready for Render (Backend) & Vercel (Frontend)")
    print("-" * 68)
    print(f" 💻 Web App & API:       http://127.0.0.1:{port}")
    print(f" 🌐 Wi-Fi Network:       http://{local_ip}:{port}")
    print(f" 🩺 Health Probe:        http://127.0.0.1:{port}/api/health")
    print(f" 📊 Metrics API:         http://127.0.0.1:{port}/api/stats")
    print("=" * 68)
    app.run(debug=True, host='0.0.0.0', port=port)
