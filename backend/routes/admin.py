from flask import Blueprint, render_template, request
from flask_login import login_required
from sqlalchemy import func, select
from routes import admin_required
from models import db, Student, Department, Company, Job, Application, Placement, AuditLog
from services.placement_service import PlacementService

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    analytics = PlacementService.get_dashboard_analytics()
    recent_applications = Application.query.order_by(Application.application_date.desc()).limit(6).all()
    recent_placements = Placement.query.order_by(Placement.created_at.desc()).limit(6).all()
    
    return render_template(
        'dashboard.html',
        analytics=analytics,
        recent_applications=recent_applications,
        recent_placements=recent_placements
    )


@admin_bp.route('/reports')
@login_required
@admin_required
def reports():
    # 1. Department-wise placement statistics
    dept_stats = db.session.query(
        Department.department_name,
        Department.department_code,
        func.count(Student.student_id).label('total_students'),
        func.count(Placement.placement_id).label('placed_students'),
        func.round(func.avg(Placement.package_lpa), 2).label('avg_package'),
        func.max(Placement.package_lpa).label('max_package')
    ).join(Student, Department.department_id == Student.department_id)\
     .outerjoin(Placement, Student.student_id == Placement.student_id)\
     .group_by(Department.department_id, Department.department_name, Department.department_code)\
     .all()

    # 2. Company-wise recruitment statistics
    company_stats = db.session.query(
        Company.company_name,
        Company.industry,
        func.count(Job.job_id).label('jobs_posted'),
        func.count(Placement.placement_id).label('hires_count'),
        func.round(func.avg(Placement.package_lpa), 2).label('avg_package'),
        func.max(Placement.package_lpa).label('highest_package')
    ).outerjoin(Job, Company.company_id == Job.company_id)\
     .outerjoin(Placement, Company.company_id == Placement.company_id)\
     .group_by(Company.company_id, Company.company_name, Company.industry)\
     .order_by(func.count(Placement.placement_id).desc())\
     .all()

    # 3. Unplaced students list
    placed_student_ids = select(Placement.student_id)
    unplaced_students = Student.query.filter(
        Student.student_id.not_in(placed_student_ids)
    ).order_by(Student.cgpa.desc()).all()

    # 4. Salary Tier Breakdown (Super Dream >= 20 LPA, Dream 10-19.9 LPA, Regular < 10 LPA)
    super_dream = Placement.query.filter(Placement.package_lpa >= 20.0).count()
    dream = Placement.query.filter(Placement.package_lpa >= 10.0, Placement.package_lpa < 20.0).count()
    regular = Placement.query.filter(Placement.package_lpa < 10.0).count()

    tier_stats = {
        'super_dream': super_dream,
        'dream': dream,
        'regular': regular
    }

    # 5. Conversion funnel counts
    total_apps = Application.query.count()
    applied_count = Application.query.filter_by(application_status='Applied').count()
    shortlisted_count = Application.query.filter_by(application_status='Shortlisted').count()
    interview_count = Application.query.filter_by(application_status='Interview Scheduled').count()
    selected_count = Application.query.filter_by(application_status='Selected').count()
    rejected_count = Application.query.filter_by(application_status='Rejected').count()

    funnel_stats = {
        'total': total_apps,
        'applied': applied_count,
        'shortlisted': shortlisted_count,
        'interviews': interview_count,
        'selected': selected_count,
        'rejected': rejected_count,
        'selection_rate': round((selected_count * 100.0 / total_apps), 2) if total_apps > 0 else 0
    }

    # 6. Audit logs
    audit_logs = AuditLog.query.order_by(AuditLog.changed_at.desc()).limit(20).all()

    return render_template(
        'reports.html',
        dept_stats=dept_stats,
        company_stats=company_stats,
        unplaced_students=unplaced_students,
        tier_stats=tier_stats,
        funnel_stats=funnel_stats,
        audit_logs=audit_logs
    )
