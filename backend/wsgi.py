import os
import sys
from pathlib import Path

# Setup paths
BACKEND_DIR = Path(__file__).resolve().parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app import create_app

# WSGI entry point for Gunicorn / Render production server
app = create_app(os.getenv('FLASK_ENV', 'production'))

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
