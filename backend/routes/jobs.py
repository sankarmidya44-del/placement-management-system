from datetime import date, datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from sqlalchemy import or_, desc, asc
from routes import admin_required
from models import db, Job, Company, Student, Application, Placement

jobs_bp = Blueprint('jobs', __name__, url_prefix='/jobs')


@jobs_bp.route('/')
@login_required
def index():
    search = request.args.get('search', '').strip()
    company_id = request.args.get('company_id', type=int)
    job_type = request.args.get('job_type', '').strip()
    location = request.args.get('location', '').strip()
    status_filter = request.args.get('status', 'Open')
    min_salary = request.args.get('min_salary', type=float)

    query = Job.query.join(Company)

    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            or_(
                Job.job_title.ilike(search_pattern),
                Company.company_name.ilike(search_pattern),
                Job.location.ilike(search_pattern)
            )
        )

    if company_id:
        query = query.filter(Job.company_id == company_id)

    if job_type:
        query = query.filter(Job.job_type == job_type)

    if location:
        query = query.filter(Job.location.ilike(f"%{location}%"))

    if status_filter and status_filter != 'All':
        query = query.filter(Job.job_status == status_filter)

    if min_salary:
        query = query.filter(Job.salary_lpa >= min_salary)

    # Order by active drives first, then highest package
    jobs = query.order_by(
        desc(Job.job_status == 'Open'),
        desc(Job.salary_lpa)
    ).all()

    companies = Company.query.order_by(Company.company_name).all()
    locations = [r[0] for r in db.session.query(Job.location).distinct().all() if r[0]]
    job_types = [r[0] for r in db.session.query(Job.job_type).distinct().all() if r[0]]

    # If student is logged in, build student application lookup map
    student_apps = {}
    is_eligible_map = {}
    if current_user.is_authenticated and not current_user.is_admin and current_user.student:
        student = current_user.student
        for app in student.applications:
            student_apps[app.job_id] = app.application_status
        for job in jobs:
            eligible, reason = job.check_eligibility(student)
            is_eligible_map[job.job_id] = (eligible, reason)

    return render_template(
        'jobs.html',
        jobs=jobs,
        companies=companies,
        locations=locations,
        job_types=job_types,
        search=search,
        selected_company=company_id,
        selected_type=job_type,
        selected_location=location,
        selected_status=status_filter,
        min_salary=min_salary,
        student_apps=student_apps,
        is_eligible_map=is_eligible_map
    )


@jobs_bp.route('/<int:job_id>')
@login_required
def detail(job_id):
    job = Job.query.get_or_404(job_id)
    companies = Company.query.order_by(Company.company_name).all()

    user_student = current_user.student if (current_user.is_authenticated and not current_user.is_admin) else None
    user_application = None
    is_eligible = True
    eligibility_reason = "Eligible"

    if user_student:
        user_application = Application.query.filter_by(student_id=user_student.student_id, job_id=job.job_id).first()
        is_eligible, eligibility_reason = job.check_eligibility(user_student)

    # For admin: get eligible students and current applications
    eligible_students = []
    job_applications = []
    if current_user.is_admin:
        job_applications = job.applications.order_by(Application.application_date.desc()).all()
        # Query eligible candidates using SQL conditions
        eligible_students = Student.query.filter(
            Student.cgpa >= job.minimum_cgpa,
            Student.backlogs <= job.maximum_backlogs
        ).order_by(Student.cgpa.desc()).all()

    return render_template(
        'job_details.html',
        job=job,
        companies=companies,
        user_application=user_application,
        is_eligible=is_eligible,
        eligibility_reason=eligibility_reason,
        eligible_students=eligible_students,
        job_applications=job_applications
    )


@jobs_bp.route('/create', methods=['POST'])
@login_required
@admin_required
def create():
    company_id = request.form.get('company_id')
    job_title = request.form.get('job_title', '').strip()
    job_description = request.form.get('job_description', '').strip()
    job_type = request.form.get('job_type', 'Full-Time')
    location = request.form.get('location', '').strip()
    minimum_cgpa = request.form.get('minimum_cgpa', 0.0)
    maximum_backlogs = request.form.get('maximum_backlogs', 0)
    salary_lpa = request.form.get('salary_lpa')
    deadline_str = request.form.get('application_deadline')
    job_status = request.form.get('job_status', 'Open')

    if not all([company_id, job_title, salary_lpa, deadline_str]):
        flash('Company, title, salary, and deadline are required.', 'warning')
        return redirect(url_for('jobs.index'))

    try:
        deadline = datetime.strptime(deadline_str, '%Y-%m-%d').date()
        salary_val = float(salary_lpa)
        cgpa_val = float(minimum_cgpa)
        backlogs_val = int(maximum_backlogs)

        if not (0.0 <= cgpa_val <= 10.0):
            flash('Minimum CGPA must be between 0.00 and 10.00.', 'danger')
            return redirect(url_for('jobs.index'))

        if salary_val < 0:
            flash('Salary LPA cannot be negative.', 'danger')
            return redirect(url_for('jobs.index'))

        new_job = Job(
            company_id=int(company_id),
            job_title=job_title,
            job_description=job_description or None,
            job_type=job_type,
            location=location or None,
            minimum_cgpa=cgpa_val,
            maximum_backlogs=backlogs_val,
            salary_lpa=salary_val,
            application_deadline=deadline,
            job_status=job_status
        )
        db.session.add(new_job)
        db.session.commit()
        flash(f'Job posting "{job_title}" published successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Database error creating job: {str(e)}', 'danger')

    return redirect(url_for('jobs.index'))


@jobs_bp.route('/<int:job_id>/edit', methods=['POST'])
@login_required
@admin_required
def edit(job_id):
    job = Job.query.get_or_404(job_id)

    job.company_id = int(request.form.get('company_id', job.company_id))
    job.job_title = request.form.get('job_title', job.job_title).strip()
    job.job_description = request.form.get('job_description', job.job_description).strip()
    job.job_type = request.form.get('job_type', job.job_type)
    job.location = request.form.get('location', job.location).strip()
    job.minimum_cgpa = float(request.form.get('minimum_cgpa', job.minimum_cgpa))
    job.maximum_backlogs = int(request.form.get('maximum_backlogs', job.maximum_backlogs))
    job.salary_lpa = float(request.form.get('salary_lpa', job.salary_lpa))
    job.job_status = request.form.get('job_status', job.job_status)

    deadline_str = request.form.get('application_deadline')
    if deadline_str:
        job.application_deadline = datetime.strptime(deadline_str, '%Y-%m-%d').date()

    try:
        db.session.commit()
        flash(f'Job "{job.job_title}" updated successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error updating job: {str(e)}', 'danger')

    return redirect(url_for('jobs.detail', job_id=job.job_id))


@jobs_bp.route('/<int:job_id>/toggle-status', methods=['POST'])
@login_required
@admin_required
def toggle_status(job_id):
    job = Job.query.get_or_404(job_id)
    job.job_status = 'Closed' if job.job_status == 'Open' else 'Open'
    db.session.commit()
    flash(f'Job "{job.job_title}" status changed to {job.job_status}.', 'info')
    return redirect(url_for('jobs.detail', job_id=job.job_id))


@jobs_bp.route('/<int:job_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete(job_id):
    job = Job.query.get_or_404(job_id)
    if job.placements.count() > 0:
        flash('Cannot delete job drive: Placement records exist for this opening.', 'danger')
        return redirect(url_for('jobs.index'))

    try:
        db.session.delete(job)
        db.session.commit()
        flash(f'Job "{job.job_title}" deleted successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Referential integrity error: {str(e)}', 'danger')

    return redirect(url_for('jobs.index'))
