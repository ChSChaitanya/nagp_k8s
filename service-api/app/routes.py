"""
API routes for the Service API tier.
"""
from flask import Blueprint, jsonify
from app.database import get_db_connection
import socket
import os

api = Blueprint('api', __name__)


@api.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for Kubernetes probes."""
    return jsonify({
        'status': 'healthy',
        'pod_name': os.environ.get('HOSTNAME', 'unknown'),
        'pod_ip': socket.gethostbyname(socket.gethostname())
    }), 200


@api.route('/ready', methods=['GET'])
def readiness_check():
    """Readiness check endpoint - verifies database connectivity."""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT 1")
        return jsonify({
            'status': 'ready',
            'database': 'connected'
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'not ready',
            'database': 'disconnected',
            'error': str(e)
        }), 503


@api.route('/', methods=['GET'])
def root():
    """Root endpoint with API information."""
    return jsonify({
        'service': 'NAGP Service API',
        'version': '1.0.0',
        'description': 'NAGP 2026 Kubernetes Assignment - Service API Tier',
        'endpoints': {
            '/': 'API Information',
            '/health': 'Health check endpoint',
            '/ready': 'Readiness check endpoint',
            '/api/employees': 'Get all employees',
            '/api/employees/<id>': 'Get employee by ID',
            '/api/info': 'Pod and environment information'
        }
    }), 200


@api.route('/api/employees', methods=['GET'])
def get_employees():
    """Fetch all employees from the database tier."""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT id, name, department, position, email, salary, created_at 
                    FROM employees 
                    ORDER BY id
                """)
                rows = cursor.fetchall()
                
                employees = []
                for row in rows:
                    employees.append({
                        'id': row[0],
                        'name': row[1],
                        'department': row[2],
                        'position': row[3],
                        'email': row[4],
                        'salary': float(row[5]),
                        'created_at': row[6].isoformat() if row[6] else None
                    })
                
                return jsonify({
                    'success': True,
                    'count': len(employees),
                    'data': employees,
                    'served_by': os.environ.get('HOSTNAME', 'unknown')
                }), 200
                
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api.route('/api/employees/<int:employee_id>', methods=['GET'])
def get_employee(employee_id):
    """Fetch a specific employee by ID."""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT id, name, department, position, email, salary, created_at 
                    FROM employees 
                    WHERE id = %s
                """, (employee_id,))
                row = cursor.fetchone()
                
                if row:
                    employee = {
                        'id': row[0],
                        'name': row[1],
                        'department': row[2],
                        'position': row[3],
                        'email': row[4],
                        'salary': float(row[5]),
                        'created_at': row[6].isoformat() if row[6] else None
                    }
                    return jsonify({
                        'success': True,
                        'data': employee,
                        'served_by': os.environ.get('HOSTNAME', 'unknown')
                    }), 200
                else:
                    return jsonify({
                        'success': False,
                        'error': f'Employee with ID {employee_id} not found'
                    }), 404
                    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api.route('/api/info', methods=['GET'])
def get_pod_info():
    """Get current pod and environment information."""
    return jsonify({
        'pod_name': os.environ.get('HOSTNAME', 'unknown'),
        'pod_ip': socket.gethostbyname(socket.gethostname()),
        'db_host': os.environ.get('DB_HOST', 'not configured'),
        'db_port': os.environ.get('DB_PORT', 'not configured'),
        'db_name': os.environ.get('DB_NAME', 'not configured')
    }), 200
