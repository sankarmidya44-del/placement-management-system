from datetime import datetime, timezone
from flask import Blueprint, jsonify, request
from sqlalchemy import text, func
from models import db, Student, Department, Company, Job, Application, Placement

api_bp = Blueprint('api', __name__, url_prefix='/api')


@api_bp.route('/health')
def health():
    """Production health check probe for Render & Vercel."""
    try:
        db.session.execute(text('SELECT 1'))
        db_status = 'connected'
        db_type = 'Neon PostgreSQL'
    except Exception as e:
        db_status = f'error: {str(e)}'
        db_type = 'unknown'

    is_healthy = db_status == 'connected'
    status_code = 200 if is_healthy else 503

    return jsonify({
        'status': 'healthy' if is_healthy else 'degraded',
        'database': db_status,
        'database_engine': db_type,
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'platform': 'Render (Backend) & Vercel (Frontend Ready)'
    }), status_code


@api_bp.route('/stats')
def stats():
    """Returns overview placement metrics as JSON."""
    try:
        total_students = Student.query.count()
        total_jobs = Job.query.filter_by(job_status='Open').count()
        total_companies = Company.query.count()
        total_placements = Placement.query.filter_by(placement_status='Accepted').count()

        avg_pkg_result = db.session.query(func.avg(Placement.package_lpa)).filter(
            Placement.placement_status == 'Accepted'
        ).scalar()
        highest_pkg_result = db.session.query(func.max(Placement.package_lpa)).filter(
            Placement.placement_status == 'Accepted'
        ).scalar()

        avg_package = float(round(avg_pkg_result, 2)) if avg_pkg_result else 0.0
        highest_package = float(round(highest_pkg_result, 2)) if highest_pkg_result else 0.0
        placement_rate = round((total_placements * 100.0 / total_students), 1) if total_students > 0 else 0.0

        return jsonify({
            'success': True,
            'data': {
                'total_students': total_students,
                'total_jobs_open': total_jobs,
                'total_companies': total_companies,
                'total_placements': total_placements,
                'placement_rate_pct': placement_rate,
                'average_package_lpa': avg_package,
                'highest_package_lpa': highest_package
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@api_bp.route('/jobs')
def list_jobs():
    """Returns list of active job postings."""
    try:
        jobs = Job.query.filter_by(job_status='Open').order_by(Job.application_deadline.asc()).all()
        data = [{
            'job_id': j.job_id,
            'job_title': j.job_title,
            'company': j.company.company_name if j.company else 'N/A',
            'location': j.location,
            'salary_lpa': float(j.salary_lpa),
            'min_cgpa': float(j.minimum_cgpa),
            'max_backlogs': j.maximum_backlogs,
            'deadline': j.application_deadline.isoformat(),
            'job_type': j.job_type
        } for j in jobs]
        return jsonify({'success': True, 'count': len(data), 'jobs': data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@api_bp.route('/companies')
def list_companies():
    """Returns list of registered recruiting partner companies."""
    try:
        companies = Company.query.order_by(Company.company_name.asc()).all()
        data = [{
            'company_id': c.company_id,
            'company_name': c.company_name,
            'industry': c.industry,
            'website': c.website,
            'contact_email': c.contact_email
        } for c in companies]
        return jsonify({'success': True, 'count': len(data), 'companies': data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
