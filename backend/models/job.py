from datetime import datetime, date, timezone
from sqlalchemy import CheckConstraint
from models import db


class Job(db.Model):
    """Placement openings and recruitment drives."""
    __tablename__ = 'jobs'
    __table_args__ = (
        CheckConstraint('minimum_cgpa >= 0.00 AND minimum_cgpa <= 10.00', name='chk_job_cgpa'),
        CheckConstraint('maximum_backlogs >= 0', name='chk_job_backlogs'),
        CheckConstraint('salary_lpa >= 0.00', name='chk_job_salary'),
        CheckConstraint("job_status IN ('Open', 'Closed')", name='chk_job_status'),
    )

    job_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.company_id', ondelete='RESTRICT'), nullable=False, index=True)
    job_title = db.Column(db.String(100), nullable=False)
    job_description = db.Column(db.Text)
    job_type = db.Column(db.String(50), nullable=False, default='Full-Time')
    location = db.Column(db.String(100))
    minimum_cgpa = db.Column(db.Numeric(4, 2), nullable=False, default=0.00)
    maximum_backlogs = db.Column(db.Integer, nullable=False, default=0)
    salary_lpa = db.Column(db.Numeric(10, 2), nullable=False)
    application_deadline = db.Column(db.Date, nullable=False, index=True)
    job_status = db.Column(db.String(20), nullable=False, default='Open', index=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    company = db.relationship('Company', back_populates='jobs')
    applications = db.relationship('Application', back_populates='job', cascade='all, delete-orphan', lazy='dynamic')
    placements = db.relationship('Placement', back_populates='job', lazy='dynamic')

    @property
    def is_active(self):
        """A job is active if status is Open and deadline is today or in the future."""
        return self.job_status == 'Open' and self.application_deadline >= date.today()

    def check_eligibility(self, student):
        """
        Validates academic eligibility for a candidate.
        Returns: (is_eligible: bool, reason: str)
        """
        if not student:
            return False, "Student record not found."
        if float(student.cgpa) < float(self.minimum_cgpa):
            return False, f"CGPA requirement not met (Required: {self.minimum_cgpa}, Current: {student.cgpa})."
        if student.backlogs > self.maximum_backlogs:
            return False, f"Backlog limit exceeded (Allowed: {self.maximum_backlogs}, Current: {student.backlogs})."
        return True, "Eligible"

    @property
    def total_applications(self):
        return self.applications.count()

    def __repr__(self):
        return f"<Job {self.job_title} at {self.company.company_name if self.company else 'N/A'}>"
