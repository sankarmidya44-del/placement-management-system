from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import event
from sqlalchemy.engine import Engine
import sqlite3

db = SQLAlchemy()

# Ensure SQLite enforces Foreign Key constraints matching MySQL behavior
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    if isinstance(dbapi_connection, sqlite3.Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


from models.student import Department, Student, User
from models.company import Company
from models.job import Job
from models.application import Application, Interview
from models.placement import Placement, AuditLog

__all__ = [
    'db',
    'Department',
    'Student',
    'User',
    'Company',
    'Job',
    'Application',
    'Interview',
    'Placement',
    'AuditLog'
]
