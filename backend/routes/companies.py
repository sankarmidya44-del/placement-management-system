from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from sqlalchemy import or_
from routes import admin_required
from models import db, Company, Job, Placement

companies_bp = Blueprint('companies', __name__, url_prefix='/companies')


@companies_bp.route('/')
@login_required
def index():
    search = request.args.get('search', '').strip()
    industry_filter = request.args.get('industry', '').strip()

    query = Company.query

    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            or_(
                Company.company_name.ilike(search_pattern),
                Company.industry.ilike(search_pattern),
                Company.contact_email.ilike(search_pattern)
            )
        )

    if industry_filter:
        query = query.filter(Company.industry == industry_filter)

    companies = query.order_by(Company.company_name.asc()).all()
    industries = [r[0] for r in db.session.query(Company.industry).distinct().order_by(Company.industry).all() if r[0]]

    return render_template(
        'companies.html',
        companies=companies,
        industries=industries,
        search=search,
        selected_industry=industry_filter
    )


@companies_bp.route('/add', methods=['POST'])
@login_required
@admin_required
def add():
    company_name = request.form.get('company_name', '').strip()
    industry = request.form.get('industry', '').strip()
    website = request.form.get('website', '').strip()
    contact_email = request.form.get('contact_email', '').strip()
    contact_phone = request.form.get('contact_phone', '').strip()
    description = request.form.get('company_description', '').strip()

    if not company_name:
        flash('Company name is required.', 'warning')
        return redirect(url_for('companies.index'))

    try:
        new_company = Company(
            company_name=company_name,
            industry=industry or None,
            website=website or None,
            contact_email=contact_email or None,
            contact_phone=contact_phone or None,
            company_description=description or None
        )
        db.session.add(new_company)
        db.session.commit()
        flash(f'Company "{company_name}" added successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Database error adding company: {str(e)}', 'danger')

    return redirect(url_for('companies.index'))


@companies_bp.route('/<int:company_id>/edit', methods=['POST'])
@login_required
@admin_required
def edit(company_id):
    company = Company.query.get_or_404(company_id)

    company.company_name = request.form.get('company_name', company.company_name).strip()
    company.industry = request.form.get('industry', company.industry).strip()
    company.website = request.form.get('website', company.website).strip()
    company.contact_email = request.form.get('contact_email', company.contact_email).strip()
    company.contact_phone = request.form.get('contact_phone', company.contact_phone).strip()
    company.company_description = request.form.get('company_description', company.company_description).strip()

    try:
        db.session.commit()
        flash(f'Company "{company.company_name}" details updated successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Failed to update company: {str(e)}', 'danger')

    return redirect(url_for('companies.index'))


@companies_bp.route('/<int:company_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete(company_id):
    company = Company.query.get_or_404(company_id)

    # Referential integrity check
    if company.jobs.count() > 0 or company.placements.count() > 0:
        flash(f'Cannot delete "{company.company_name}": Job postings or placement records reference this company. Please close associated drives instead.', 'danger')
        return redirect(url_for('companies.index'))

    try:
        db.session.delete(company)
        db.session.commit()
        flash(f'Company "{company.company_name}" removed.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Database error: Cannot delete company ({str(e)})', 'danger')

    return redirect(url_for('companies.index'))
