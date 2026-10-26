import os

# Render sets PORT in environment (defaults to 10000 on Render)
port = os.getenv('PORT', '10000')
bind = f"0.0.0.0:{port}"

# Free tier container optimization
workers = int(os.getenv('WEB_CONCURRENCY', '1'))
threads = int(os.getenv('PYTHON_GET_THREADS', '4'))
worker_class = 'gthread'

# Generous timeout for serverless Neon database connection wakeup
timeout = 120
keepalive = 5

# Production logging
accesslog = '-'
errorlog = '-'
loglevel = 'info'
