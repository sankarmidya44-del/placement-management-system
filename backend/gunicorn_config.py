import os

# Gunicorn production configuration for Render
port = os.getenv('PORT', '5000')
bind = f"0.0.0.0:{port}"

# Free tier container optimization (2 workers, 4 threads per worker)
workers = int(os.getenv('WEB_CONCURRENCY', '2'))
threads = int(os.getenv('PYTHON_GET_THREADS', '4'))
worker_class = 'gthread'

# Generous timeout to accommodate free tier cold starts and Neon connection wakeups
timeout = 120
keepalive = 5

# Production logging
accesslog = '-'
errorlog = '-'
loglevel = 'info'
