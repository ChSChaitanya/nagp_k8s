"""
Database module with connection pooling for PostgreSQL.
Implements best practices for database connections.
"""
import psycopg2
from psycopg2 import pool
from contextlib import contextmanager
from app.config import Config


class DatabasePool:
    """Singleton database connection pool manager."""
    
    _instance = None
    _pool = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def init_pool(self):
        """Initialize the connection pool."""
        if self._pool is None:
            try:
                self._pool = psycopg2.pool.ThreadedConnectionPool(
                    minconn=Config.DB_POOL_MIN_CONN,
                    maxconn=Config.DB_POOL_MAX_CONN,
                    host=Config.DB_HOST,
                    port=Config.DB_PORT,
                    database=Config.DB_NAME,
                    user=Config.DB_USER,
                    password=Config.DB_PASSWORD
                )
                print(f"Database pool initialized successfully. Connected to {Config.DB_HOST}:{Config.DB_PORT}")
            except Exception as e:
                print(f"Error initializing database pool: {e}")
                raise
    
    def get_connection(self):
        """Get a connection from the pool."""
        if self._pool is None:
            self.init_pool()
        return self._pool.getconn()
    
    def return_connection(self, conn):
        """Return a connection to the pool."""
        if self._pool:
            self._pool.putconn(conn)
    
    def close_all(self):
        """Close all connections in the pool."""
        if self._pool:
            self._pool.closeall()


# Singleton instance
db_pool = DatabasePool()


@contextmanager
def get_db_connection():
    """Context manager for database connections."""
    conn = None
    try:
        conn = db_pool.get_connection()
        yield conn
    finally:
        if conn:
            db_pool.return_connection(conn)


def init_database():
    """Initialize database with sample data if tables don't exist."""
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            # Create employees table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS employees (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    department VARCHAR(100) NOT NULL,
                    position VARCHAR(100) NOT NULL,
                    email VARCHAR(150) NOT NULL,
                    salary DECIMAL(10, 2) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Check if data exists
            cursor.execute("SELECT COUNT(*) FROM employees")
            count = cursor.fetchone()[0]
            
            if count == 0:
                # Insert sample data (5-10 records as required)
                sample_data = [
                    ('Alice Johnson', 'Engineering', 'Software Engineer', 'alice.johnson@company.com', 85000.00),
                    ('Bob Smith', 'Engineering', 'Senior Developer', 'bob.smith@company.com', 95000.00),
                    ('Carol Williams', 'Marketing', 'Marketing Manager', 'carol.williams@company.com', 78000.00),
                    ('David Brown', 'HR', 'HR Specialist', 'david.brown@company.com', 62000.00),
                    ('Eva Martinez', 'Finance', 'Financial Analyst', 'eva.martinez@company.com', 72000.00),
                    ('Frank Lee', 'Engineering', 'DevOps Engineer', 'frank.lee@company.com', 92000.00),
                    ('Grace Chen', 'Sales', 'Sales Representative', 'grace.chen@company.com', 68000.00),
                    ('Henry Wilson', 'Engineering', 'QA Engineer', 'henry.wilson@company.com', 75000.00)
                ]
                
                cursor.executemany(
                    """INSERT INTO employees (name, department, position, email, salary) 
                       VALUES (%s, %s, %s, %s, %s)""",
                    sample_data
                )
                print(f"Inserted {len(sample_data)} sample records into employees table")
            
            conn.commit()
            print("Database initialization completed")
