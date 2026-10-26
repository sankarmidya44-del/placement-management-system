from datetime import datetime, date
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from routes import admin_required
from models import db, Application, Interview, Job, Student, Placement
from services.placement_service import PlacementService

applications_bp = Blueprint('applications', __name__, url_prefix='/applications')


@applications_bp.route('/')
@login_required
def index():
    status_filter = request.args.get('status', '').strip()
    job_id = request.args.get('job_id', type=int)

    query = Application.query

    # Non-admins can only see their own applications
    if not current_user.is_admin:
        if not current_user.student:
            flash('No student profile associated with this account.', 'warning')
            return redirect(url_for('jobs.index'))
        query = query.filter(Application.student_id == current_user.student.student_id)
    elif job_id:
        query = query.filter(Application.job_id == job_id)

    if status_filter:
        query = query.filter(Application.application_status == status_filter)

    applications = query.order_by(Application.application_date.desc()).all()
    jobs = Job.query.order_by(Job.job_title).all()

    return render_template(
        'applications.html',
        applications=applications,
        jobs=jobs,
        selected_status=status_filter,
        selected_job=job_id
    )


@applications_bp.route('/apply', methods=['POST'])
@login_required
def apply():
    if current_user.is_admin:
        flash('Administrators cannot submit student job applications.', 'warning')
        return redirect(url_for('jobs.index'))

    if not current_user.student:
        flash('You must have a completed student profile to apply.', 'danger')
        return redirect(url_for('jobs.index'))

    job_id = request.form.get('job_id', type=int)
    resume_url = request.form.get('resume_url', '').strip()

    if not job_id:
        flash('Invalid job application request.', 'danger')
        return redirect(url_for('jobs.index'))

    success, message = PlacementService.apply_for_job(
        student_id=current_user.student.student_id,
        job_id=job_id,
        resume_url=resume_url or None
    )

    if success:
        flash(message, 'success')
    else:
        flash(message, 'danger')

    return redirect(url_for('jobs.detail', job_id=job_id))


@applications_bp.route('/<int:application_id>/status', methods=['POST'])
@login_required
@admin_required
def update_status(application_id):
    new_status = request.form.get('status', '').strip()
    success, message = PlacementService.update_application_status(
        application_id=application_id,
        new_status=new_status,
        admin_user=current_user.username
    )

    if success:
        flash(message, 'success')
    else:
        flash(message, 'danger')

    return redirect(request.referrer or url_for('applications.index'))


@applications_bp.route('/<int:application_id>/schedule-interview', methods=['POST'])
@login_required
@admin_required
def schedule_interview(application_id):
    round_name = request.form.get('interview_round', '').strip()
    interview_date = request.form.get('interview_date')
    mode = request.form.get('interview_mode', 'Online')
    location = request.form.get('interview_location', '').strip()
    notes = request.form.get('interviewer_notes', '').strip()

    if not round_name or not interview_date:
        flash('Interview round name and date/time are required.', 'warning')
        return redirect(request.referrer or url_for('applications.index'))

    success, message = PlacementService.schedule_interview(
        application_id=application_id,
        round_name=round_name,
        interview_date_str=interview_date,
        mode=mode,
        location=location or None,
        notes=notes or None,
        admin_user=current_user.username
    )

    if success:
        flash(message, 'success')
    else:
        flash(message, 'danger')

    return redirect(request.referrer or url_for('applications.index'))


@applications_bp.route('/<int:application_id>/select', methods=['POST'])
@login_required
@admin_required
def select_candidate(application_id):
    package_lpa = request.form.get('package_lpa')
    offer_date_str = request.form.get('offer_date')
    enforce_single_offer = request.form.get('enforce_single_offer') == '1'

    offer_date = datetime.strptime(offer_date_str, '%Y-%m-%d').date() if offer_date_str else date.today()

    success, message = PlacementService.select_and_place_candidate(
        application_id=application_id,
        offer_date=offer_date,
        package_lpa=package_lpa,
        admin_user=current_user.username,
        enforce_single_offer=enforce_single_offer
    )

    if success:
        flash(message, 'success')
    else:
        flash(message, 'danger')

    return redirect(request.referrer or url_for('applications.index'))


@applications_bp.route('/placements')
@login_required
def placements_list():
    query = Placement.query.join(Student).join(Job)

    if not current_user.is_admin:
        if current_user.student:
            query = query.filter(Placement.student_id == current_user.student.student_id)
        else:
            query = query.filter(Placement.student_id == -1)

    placements = query.order_by(Placement.offer_date.desc()).all()

    return render_template('placements.html', placements=placements)
