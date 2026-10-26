from datetime import datetime, timezone
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import CheckConstraint
from models import db


class Department(db.Model):
    """Academic departments offering degrees."""
    __tablename__ = 'departments'

    department_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    department_name = db.Column(db.String(100), unique=True, nullable=False)
    department_code = db.Column(db.String(20), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    students = db.relationship('Student', back_populates='department', lazy='dynamic')

    def __repr__(self):
        return f"<Department {self.department_code}>"


class Student(db.Model):
    """Student profiles for placement eligibility and tracking."""
    __tablename__ = 'students'
    __table_args__ = (
        CheckConstraint('cgpa >= 0.00 AND cgpa <= 10.00', name='chk_student_cgpa'),
        CheckConstraint('backlogs >= 0', name='chk_student_backlogs'),
    )

    student_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    roll_number = db.Column(db.String(50), unique=True, nullable=False, index=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False, index=True)
    phone = db.Column(db.String(20))
    department_id = db.Column(db.Integer, db.ForeignKey('departments.department_id', ondelete='RESTRICT'), nullable=False, index=True)
    graduation_year = db.Column(db.Integer, nullable=False)
    cgpa = db.Column(db.Numeric(4, 2), nullable=False)
    backlogs = db.Column(db.Integer, nullable=False, default=0)
    resume_url = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    department = db.relationship('Department', back_populates='students')
    user = db.relationship('User', back_populates='student', uselist=False)
    applications = db.relationship('Application', back_populates='student', cascade='all, delete-orphan', lazy='dynamic')
    placements = db.relationship('Placement', back_populates='student', lazy='dynamic')

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def is_placed(self):
        return self.placements.filter_by(placement_status='Accepted').first() is not None

    @property
    def active_placement(self):
        return self.placements.filter_by(placement_status='Accepted').first()

    def __repr__(self):
        return f"<Student {self.roll_number} - {self.full_name}>"


class User(UserMixin, db.Model):
    """User authentication and authorization model."""
    __tablename__ = 'users'
    __table_args__ = (
        CheckConstraint("role IN ('Admin', 'Student')", name='chk_user_role'),
    )

    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), unique=True, nullable=False, index=True)
    email = db.Column(db.String(100), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='Student')
    student_id = db.Column(db.Integer, db.ForeignKey('students.student_id', ondelete='SET NULL'), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    student = db.relationship('Student', back_populates='user')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def is_admin(self):
        return self.role == 'Admin'

    def get_id(self):
        return str(self.user_id)

    def __repr__(self):
        return f"<User {self.username} ({self.role})>"
