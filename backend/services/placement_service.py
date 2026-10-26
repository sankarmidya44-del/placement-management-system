from datetime import datetime, date, timezone
from decimal import Decimal
from sqlalchemy import func
from models import db, Student, Department, Company, Job, Application, Interview, Placement, AuditLog


class PlacementService:
    """
    Encapsulates core placement business workflows, eligibility rules, 
    and multi-table ACID transaction management.
    """

    @staticmethod
    def apply_for_job(student_id, job_id, resume_url=None):
        """
        Submits an application with ACID guarantees.
        Validates:
        1. Job is currently Open.
        2. Application deadline has not expired.
        3. Candidate satisfies CGPA and backlog requirements.
        4. Candidate has not already applied (prevents duplicate applications).
        """
        try:
            student = db.session.get(Student, student_id)
            if not student:
                return False, "Student profile not found."

            job = db.session.get(Job, job_id)
            if not job:
                return False, "Job opening not found."

            if job.job_status != 'Open':
                return False, "Cannot apply: This job posting is closed."

            if job.application_deadline < date.today():
                return False, f"Cannot apply: The deadline ({job.application_deadline}) has expired."

            # Academic eligibility check
            is_eligible, reason = job.check_eligibility(student)
            if not is_eligible:
                return False, f"Eligibility requirement not met: {reason}"

            # Check duplicate application
            existing_app = Application.query.filter_by(student_id=student_id, job_id=job_id).first()
            if existing_app:
                return False, "You have already applied for this job opening."

            # Atomic transaction
            new_application = Application(
                student_id=student_id,
                job_id=job_id,
                application_status='Applied',
                resume_url=resume_url or student.resume_url,
                application_date=datetime.now(timezone.utc)
            )
            db.session.add(new_application)
            db.session.flush()

            # Audit log
            audit = AuditLog(
                table_name='applications',
                record_id=new_application.application_id,
                action='INSERT',
                old_values=None,
                new_values=f"Student {student.roll_number} applied for Job {job.job_title} at {job.company.company_name}",
                changed_by=student.roll_number
            )
            db.session.add(audit)

            db.session.commit()
            return True, "Application successfully submitted!"

        except Exception as e:
            db.session.rollback()
            return False, f"Transaction failed and was rolled back: {str(e)}"

    @staticmethod
    def select_and_place_candidate(application_id, offer_date=None, package_lpa=None, admin_user='admin', enforce_single_offer=False):
        """
        ACID Transaction demonstrating Atomicity, Consistency, Isolation, and Durability.
        Multi-step process:
        1. Verify application exists and retrieve student & job.
        2. Prevent duplicate placement records for same student & job.
        3. Optionally enforce college policy of one final accepted offer per student.
        4. Update application status to 'Selected'.
        5. Insert confirmed placement record.
        6. Record audit trail.
        7. Atomically commit or rollback on any error.
        """
        try:
            application = db.session.get(Application, application_id)
            if not application:
                return False, "Application record not found."

            student = application.student
            job = application.job

            if not student or not job:
                return False, "Associated student or job record is missing or corrupted."

            # Check if duplicate placement already exists for this exact job
            existing_job_placement = Placement.query.filter_by(
                student_id=student.student_id,
                job_id=job.job_id
            ).first()
            if existing_job_placement:
                return False, f"Student {student.roll_number} already has a placement record for this job."

            # Check if college permits only one final placement per student
            if enforce_single_offer:
                existing_any_placement = Placement.query.filter_by(
                    student_id=student.student_id,
                    placement_status='Accepted'
                ).first()
                if existing_any_placement:
                    return False, f"Policy violation: Student {student.roll_number} is already placed at {existing_any_placement.company.company_name}."

            # Determine offer package
            final_package = Decimal(str(package_lpa)) if package_lpa else job.salary_lpa
            if final_package <= 0:
                return False, "Package LPA must be greater than zero."

            final_offer_date = offer_date if offer_date else date.today()

            # Record previous application status for audit
            prev_status = application.application_status
            application.application_status = 'Selected'
            application.updated_at = datetime.now(timezone.utc)

            # Create Placement record
            new_placement = Placement(
                student_id=student.student_id,
                job_id=job.job_id,
                company_id=job.company_id,
                offer_date=final_offer_date,
                package_lpa=final_package,
                placement_status='Accepted',
                created_at=datetime.now(timezone.utc)
            )
            db.session.add(new_placement)
            db.session.flush()

            # Create Audit trail
            audit_app = AuditLog(
                table_name='applications',
                record_id=application.application_id,
                action='UPDATE',
                old_values=f"status: {prev_status}",
                new_values="status: Selected",
                changed_by=admin_user
            )
            audit_placement = AuditLog(
                table_name='placements',
                record_id=new_placement.placement_id,
                action='INSERT',
                old_values=None,
                new_values=f"Student {student.roll_number} placed at {job.company.company_name} with {final_package} LPA",
                changed_by=admin_user
            )
            db.session.add_all([audit_app, audit_placement])

            # Atomic commit of all changes
            db.session.commit()
            return True, f"Candidate {student.full_name} successfully selected and placement recorded at {final_package} LPA!"

        except Exception as e:
            db.session.rollback()
            return False, f"Database transaction failed and was safely rolled back: {str(e)}"

    @staticmethod
    def schedule_interview(application_id, round_name, interview_date_str, mode='Online', location=None, notes=None, admin_user='admin'):
        """
        Schedules an interview round and updates application status.
        """
        try:
            application = db.session.get(Application, application_id)
            if not application:
                return False, "Application not found."

            if isinstance(interview_date_str, str):
                interview_dt = datetime.fromisoformat(interview_date_str.replace(' ', 'T'))
            else:
                interview_dt = interview_date_str

            interview = Interview(
                application_id=application_id,
                interview_round=round_name,
                interview_date=interview_dt,
                interview_mode=mode,
                interview_location=location or ('Virtual Video Link' if mode == 'Online' else 'Campus Placement Cell'),
                interviewer_notes=notes,
                interview_result='Pending'
            )
            db.session.add(interview)

            # Update application status
            old_status = application.application_status
            application.application_status = 'Interview Scheduled'

            audit = AuditLog(
                table_name='applications',
                record_id=application_id,
                action='UPDATE',
                old_values=f"status: {old_status}",
                new_values=f"status: Interview Scheduled ({round_name})",
                changed_by=admin_user
            )
            db.session.add(audit)

            db.session.commit()
            return True, f"Interview round '{round_name}' successfully scheduled."

        except Exception as e:
            db.session.rollback()
            return False, f"Failed to schedule interview: {str(e)}"

    @staticmethod
    def update_application_status(application_id, new_status, admin_user='admin'):
        """Updates application status with audit trail."""
        valid_statuses = ('Applied', 'Shortlisted', 'Interview Scheduled', 'Selected', 'Rejected', 'Withdrawn')
        if new_status not in valid_statuses:
            return False, f"Invalid application status '{new_status}'."

        try:
            application = db.session.get(Application, application_id)
            if not application:
                return False, "Application not found."

            old_status = application.application_status
            application.application_status = new_status
            application.updated_at = datetime.now(timezone.utc)

            audit = AuditLog(
                table_name='applications',
                record_id=application_id,
                action='UPDATE',
                old_values=f"status: {old_status}",
                new_values=f"status: {new_status}",
                changed_by=admin_user
            )
            db.session.add(audit)
            db.session.commit()
            return True, f"Application status updated to '{new_status}'."
        except Exception as e:
            db.session.rollback()
            return False, f"Database error updating status: {str(e)}"

    @staticmethod
    def get_dashboard_analytics():
        """
        Aggregates live database metrics for the administration dashboard and Chart.js visuals.
        """
        total_students = Student.query.count()
        total_companies = Company.query.count()
        total_active_jobs = Job.query.filter_by(job_status='Open').count()
        total_applications = Application.query.count()
        
        # Placements count and distinct placed students
        placed_students_count = db.session.query(func.count(func.distinct(Placement.student_id))).scalar() or 0
        placement_percentage = round((placed_students_count * 100.0 / total_students), 2) if total_students > 0 else 0.0

        # Salary metrics
        avg_package = db.session.query(func.avg(Placement.package_lpa)).scalar()
        highest_package = db.session.query(func.max(Placement.package_lpa)).scalar()
        avg_package = round(float(avg_package), 2) if avg_package else 0.0
        highest_package = round(float(highest_package), 2) if highest_package else 0.0

        # 1. Applications by status (for doughnut chart)
        status_counts = db.session.query(
            Application.application_status,
            func.count(Application.application_id)
        ).group_by(Application.application_status).all()
        status_chart_data = {
            'labels': [row[0] for row in status_counts],
            'values': [row[1] for row in status_counts]
        }

        # 2. Placements by Department (for bar chart)
        dept_placements = db.session.query(
            Department.department_code,
            func.count(func.distinct(Placement.student_id))
        ).join(Student, Department.department_id == Student.department_id)\
         .outerjoin(Placement, Student.student_id == Placement.student_id)\
         .group_by(Department.department_code).all()
        dept_chart_data = {
            'labels': [row[0] for row in dept_placements],
            'values': [row[1] for row in dept_placements]
        }

        # 3. Recruitment by Company (for horizontal bar chart)
        company_recruits = db.session.query(
            Company.company_name,
            func.count(Placement.placement_id)
        ).join(Placement, Company.company_id == Placement.company_id)\
         .group_by(Company.company_name)\
         .order_by(func.count(Placement.placement_id).desc())\
         .limit(7).all()
        company_chart_data = {
            'labels': [row[0] for row in company_recruits],
            'values': [row[1] for row in company_recruits]
        }

        # 4. Placement trends by graduation year
        grad_year_trends = db.session.query(
            Student.graduation_year,
            func.count(func.distinct(Placement.student_id))
        ).join(Placement, Student.student_id == Placement.student_id)\
         .group_by(Student.graduation_year)\
         .order_by(Student.graduation_year).all()
        grad_chart_data = {
            'labels': [str(row[0]) for row in grad_year_trends],
            'values': [row[1] for row in grad_year_trends]
        }

        return {
            'total_students': total_students,
            'total_companies': total_companies,
            'total_active_jobs': total_active_jobs,
            'total_applications': total_applications,
            'placed_students_count': placed_students_count,
            'placement_percentage': placement_percentage,
            'avg_package': avg_package,
            'highest_package': highest_package,
            'status_chart_data': status_chart_data,
            'dept_chart_data': dept_chart_data,
            'company_chart_data': company_chart_data,
            'grad_chart_data': grad_chart_data
        }
