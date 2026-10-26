from datetime import datetime, timezone
from sqlalchemy import UniqueConstraint, CheckConstraint
from models import db


class Application(db.Model):
    """Job applications submitted by students."""
    __tablename__ = 'applications'
    __table_args__ = (
        UniqueConstraint('student_id', 'job_id', name='uq_student_job_application'),
        CheckConstraint(
            "application_status IN ('Applied', 'Shortlisted', 'Interview Scheduled', 'Selected', 'Rejected', 'Withdrawn')",
            name='chk_app_status'
        ),
    )

    application_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.student_id', ondelete='CASCADE'), nullable=False, index=True)
    job_id = db.Column(db.Integer, db.ForeignKey('jobs.job_id', ondelete='CASCADE'), nullable=False, index=True)
    application_date = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    application_status = db.Column(db.String(50), nullable=False, default='Applied', index=True)
    resume_url = db.Column(db.String(255))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    student = db.relationship('Student', back_populates='applications')
    job = db.relationship('Job', back_populates='applications')
    interviews = db.relationship('Interview', back_populates='application', cascade='all, delete-orphan', lazy='dynamic')

    @property
    def latest_interview(self):
        return self.interviews.order_by(Interview.interview_date.desc()).first()

    def __repr__(self):
        return f"<Application {self.application_id}: Student {self.student_id} -> Job {self.job_id} ({self.application_status})>"


class Interview(db.Model):
    """Scheduled interview rounds and technical evaluations."""
    __tablename__ = 'interviews'
    __table_args__ = (
        CheckConstraint("interview_mode IN ('Online', 'Offline')", name='chk_interview_mode'),
        CheckConstraint("interview_result IN ('Pending', 'Passed', 'Failed')", name='chk_interview_result'),
    )

    interview_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    application_id = db.Column(db.Integer, db.ForeignKey('applications.application_id', ondelete='CASCADE'), nullable=False, index=True)
    interview_round = db.Column(db.String(50), nullable=False)
    interview_date = db.Column(db.DateTime, nullable=False, index=True)
    interview_mode = db.Column(db.String(20), nullable=False, default='Online')
    interview_location = db.Column(db.String(255))
    interviewer_notes = db.Column(db.Text)
    interview_result = db.Column(db.String(50), nullable=False, default='Pending')
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    application = db.relationship('Application', back_populates='interviews')

    def __repr__(self):
        return f"<Interview {self.interview_round} for App {self.application_id} ({self.interview_result})>"
