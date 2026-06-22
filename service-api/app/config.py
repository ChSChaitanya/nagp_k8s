"""
Configuration module for database connection.
Reads configuration from environment variables (injected via ConfigMap/Secrets).
"""
import os


class Config:
    """Application configuration loaded from environment variables."""
    
    # Database configuration - loaded from ConfigMap
    DB_HOST = os.environ.get('DB_HOST', 'postgres-service')
    DB_PORT = os.environ.get('DB_PORT', '5432')
    DB_NAME = os.environ.get('DB_NAME', 'nagpdb')
    DB_USER = os.environ.get('DB_USER', 'nagpuser')
    
    # Database password - loaded from Secret
    DB_PASSWORD = os.environ.get('DB_PASSWORD', '')
    
    # Connection pool settings
    DB_POOL_MIN_CONN = int(os.environ.get('DB_POOL_MIN_CONN', '1'))
    DB_POOL_MAX_CONN = int(os.environ.get('DB_POOL_MAX_CONN', '10'))
    
    @classmethod
    def get_db_uri(cls):
        """Get PostgreSQL connection URI."""
        return f"postgresql://{cls.DB_USER}:{cls.DB_PASSWORD}@{cls.DB_HOST}:{cls.DB_PORT}/{cls.DB_NAME}"
