import os
from pathlib import Path
from dotenv import load_dotenv

BACKEND_DIR = Path(__file__).resolve().parent
BASE_DIR = BACKEND_DIR.parent

# Load environment variables (.env in backend/ first, then project root)
if (BACKEND_DIR / '.env').exists():
    load_dotenv(BACKEND_DIR / '.env')
elif (BASE_DIR / '.env').exists():
    load_dotenv(BASE_DIR / '.env')
else:
    load_dotenv()

# Neon PostgreSQL production URI (default fallback if not in env)
NEON_DATABASE_URL = (
    "postgresql://neondb_owner:npg_nCVKtBg2dhM4@"
    "ep-blue-wave-b3o5k41a-pooler.c-4.ap-southeast-1.aws.neon.tech/neondb"
    "?sslmode=require&channel_binding=require"
)


class Config:
    """Production-grade configuration for Flask & SQLAlchemy."""
    SECRET_KEY = os.getenv('SECRET_KEY', 'spms_prod_secret_key_2026_xyz987654321')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Engine connection pooling options (crucial for serverless Neon PostgreSQL & Render)
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': int(os.getenv('DB_POOL_SIZE', '10')),
        'max_overflow': int(os.getenv('DB_MAX_OVERFLOW', '20')),
        'pool_recycle': int(os.getenv('DB_POOL_RECYCLE', '300')),
        'pool_pre_ping': True,
    }

    # CORS configuration for Vercel frontend communication
    CORS_ORIGIN = os.getenv('CORS_ORIGIN', '*')

    @classmethod
    def get_database_uri(cls):
        """
        Resolves the database URI.
        Priority:
        1. DATABASE_URL environment variable (from Render / .env)
        2. Configured NEON_DATABASE_URL
        Fixes legacy 'postgres://' schema prefix if set by Render.
        """
        raw_uri = os.getenv('DATABASE_URL', '').strip()
        if not raw_uri:
            raw_uri = NEON_DATABASE_URL

        # SQLAlchemy 2.0 requires postgresql:// instead of postgres://
        if raw_uri.startswith('postgres://'):
            raw_uri = raw_uri.replace('postgres://', 'postgresql://', 1)

        return raw_uri


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    TESTING = False
    SQLALCHEMY_DATABASE_URI = Config.get_database_uri()


class TestingConfig(Config):
    """Isolated Testing configuration for unit & integration tests."""
    DEBUG = False
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SQLALCHEMY_ENGINE_OPTIONS = {}
    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    """Production configuration for Render / cloud deployments."""
    DEBUG = False
    TESTING = False
    SQLALCHEMY_DATABASE_URI = Config.get_database_uri()
    # Enhanced session security in production
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    # SESSION_COOKIE_SECURE will be enabled when running under HTTPS (Render/Vercel)
    SESSION_COOKIE_SECURE = os.getenv('SESSION_COOKIE_SECURE', 'true').lower() in ('true', '1')


config_by_name = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': ProductionConfig
}
