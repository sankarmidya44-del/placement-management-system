from datetime import datetime, date, timezone
from sqlalchemy import UniqueConstraint, CheckConstraint
from models import db


class Placement(db.Model):
    """Confirmed placement offers extended to candidates."""
    __tablename__ = 'placements'
    __table_args__ = (
        UniqueConstraint('student_id', 'job_id', name='uq_student_job_placement'),
        CheckConstraint("placement_status IN ('Offered', 'Accepted', 'Declined')", name='chk_placement_status'),
        CheckConstraint('package_lpa > 0.00', name='chk_placement_package'),
    )

    placement_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.student_id', ondelete='RESTRICT'), nullable=False, index=True)
    job_id = db.Column(db.Integer, db.ForeignKey('jobs.job_id', ondelete='RESTRICT'), nullable=False, index=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.company_id', ondelete='RESTRICT'), nullable=False, index=True)
    offer_date = db.Column(db.Date, nullable=False, default=date.today)
    package_lpa = db.Column(db.Numeric(10, 2), nullable=False)
    placement_status = db.Column(db.String(50), nullable=False, default='Accepted')
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    student = db.relationship('Student', back_populates='placements')
    job = db.relationship('Job', back_populates='placements')
    company = db.relationship('Company', back_populates='placements')

    def __repr__(self):
        return f"<Placement {self.placement_id}: Student {self.student_id} -> {self.company.company_name} ({self.package_lpa} LPA)>"


class AuditLog(db.Model):
    """Audit log capturing key status changes and compliance events."""
    __tablename__ = 'audit_logs'

    log_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    table_name = db.Column(db.String(50), nullable=False)
    record_id = db.Column(db.Integer, nullable=False)
    action = db.Column(db.String(20), nullable=False)
    old_values = db.Column(db.Text)
    new_values = db.Column(db.Text)
    changed_by = db.Column(db.String(100), default='SYSTEM')
    changed_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f"<AuditLog {self.log_id}: {self.table_name} #{self.record_id} {self.action}>"
