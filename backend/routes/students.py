from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from sqlalchemy import or_, desc, asc
from routes import admin_required
from models import db, Student, Department, User, Application, Placement

students_bp = Blueprint('students', __name__, url_prefix='/students')


@students_bp.route('/')
@login_required
@admin_required
def index():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '').strip()
    dept_id = request.args.get('department_id', type=int)
    grad_year = request.args.get('graduation_year', type=int)
    sort_by = request.args.get('sort_by', 'roll_number')
    order = request.args.get('order', 'asc')

    query = Student.query.join(Department)

    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            or_(
                Student.roll_number.ilike(search_pattern),
                Student.first_name.ilike(search_pattern),
                Student.last_name.ilike(search_pattern),
                Student.email.ilike(search_pattern)
            )
        )

    if dept_id:
        query = query.filter(Student.department_id == dept_id)

    if grad_year:
        query = query.filter(Student.graduation_year == grad_year)

    # Sorting
    sort_column = {
        'roll_number': Student.roll_number,
        'name': Student.first_name,
        'cgpa': Student.cgpa,
        'backlogs': Student.backlogs,
        'year': Student.graduation_year
    }.get(sort_by, Student.roll_number)

    if order == 'desc':
        query = query.order_by(desc(sort_column))
    else:
        query = query.order_by(asc(sort_column))

    pagination = query.paginate(page=page, per_page=10, error_out=False)
    departments = Department.query.order_by(Department.department_name).all()
    available_years = [r[0] for r in db.session.query(Student.graduation_year).distinct().order_by(Student.graduation_year).all()]

    return render_template(
        'students.html',
        pagination=pagination,
        students=pagination.items,
        departments=departments,
        available_years=available_years,
        search=search,
        selected_dept=dept_id,
        selected_year=grad_year,
        sort_by=sort_by,
        order=order
    )


@students_bp.route('/<int:student_id>')
@login_required
def detail(student_id):
    # Role-Based Access Control: Students can only view their own record
    if not current_user.is_admin and current_user.student_id != student_id:
        flash('Access Denied: You may only view your own student profile.', 'danger')
        if current_user.student_id:
            return redirect(url_for('students.detail', student_id=current_user.student_id))
        return redirect(url_for('jobs.index'))

    student = Student.query.get_or_404(student_id)
    applications = student.applications.order_by(Application.application_date.desc()).all()
    placements = student.placements.all()
    departments = Department.query.order_by(Department.department_name).all()

    return render_template(
        'student_details.html',
        student=student,
        applications=applications,
        placements=placements,
        departments=departments
    )


@students_bp.route('/add', methods=['POST'])
@login_required
@admin_required
def add():
    roll_number = request.form.get('roll_number', '').strip().upper()
    first_name = request.form.get('first_name', '').strip()
    last_name = request.form.get('last_name', '').strip()
    email = request.form.get('email', '').strip().lower()
    phone = request.form.get('phone', '').strip()
    department_id = request.form.get('department_id')
    graduation_year = request.form.get('graduation_year')
    cgpa = request.form.get('cgpa')
    backlogs = request.form.get('backlogs', 0)
    resume_url = request.form.get('resume_url', '').strip()

    if not all([roll_number, first_name, last_name, email, department_id, graduation_year, cgpa]):
        flash('All mandatory student fields must be provided.', 'warning')
        return redirect(url_for('students.index'))

    try:
        cgpa_val = float(cgpa)
        if not (0.0 <= cgpa_val <= 10.0):
            flash('CGPA must be between 0.00 and 10.00.', 'danger')
            return redirect(url_for('students.index'))
    except ValueError:
        flash('Invalid CGPA format.', 'danger')
        return redirect(url_for('students.index'))

    if Student.query.filter_by(roll_number=roll_number).first():
        flash(f'Student with roll number {roll_number} already exists.', 'danger')
        return redirect(url_for('students.index'))

    if Student.query.filter_by(email=email).first():
        flash(f'Student with email {email} already exists.', 'danger')
        return redirect(url_for('students.index'))

    try:
        new_student = Student(
            roll_number=roll_number,
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            department_id=int(department_id),
            graduation_year=int(graduation_year),
            cgpa=cgpa_val,
            backlogs=int(backlogs),
            resume_url=resume_url or None
        )
        db.session.add(new_student)
        db.session.flush()

        # Auto-provision user login account for the student
        default_username = roll_number.lower()
        if not User.query.filter_by(username=default_username).first() and not User.query.filter_by(email=email).first():
            student_user = User(
                username=default_username,
                email=email,
                role='Student',
                student_id=new_student.student_id
            )
            student_user.set_password('student123')
            db.session.add(student_user)

        db.session.commit()
        flash(f'Student {new_student.full_name} ({roll_number}) added successfully! Login: {default_username} / student123', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Database error adding student: {str(e)}', 'danger')

    return redirect(url_for('students.index'))


@students_bp.route('/<int:student_id>/edit', methods=['POST'])
@login_required
def edit(student_id):
    if not current_user.is_admin and current_user.student_id != student_id:
        flash('Access Denied.', 'danger')
        return redirect(url_for('jobs.index'))

    student = Student.query.get_or_404(student_id)

    # Students can update their phone & resume URL; Admins can update academic metrics
    student.phone = request.form.get('phone', student.phone).strip()
    student.resume_url = request.form.get('resume_url', student.resume_url).strip() or None

    if current_user.is_admin:
        student.first_name = request.form.get('first_name', student.first_name).strip()
        student.last_name = request.form.get('last_name', student.last_name).strip()
        student.department_id = int(request.form.get('department_id', student.department_id))
        student.graduation_year = int(request.form.get('graduation_year', student.graduation_year))
        
        cgpa_str = request.form.get('cgpa')
        if cgpa_str:
            try:
                cgpa_val = float(cgpa_str)
                if 0.0 <= cgpa_val <= 10.0:
                    student.cgpa = cgpa_val
            except ValueError:
                pass
        
        backlogs_str = request.form.get('backlogs')
        if backlogs_str:
            try:
                student.backlogs = max(0, int(backlogs_str))
            except ValueError:
                pass

    try:
        db.session.commit()
        flash('Student record updated successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Failed to update student: {str(e)}', 'danger')

    return redirect(url_for('students.detail', student_id=student_id))


@students_bp.route('/<int:student_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete(student_id):
    student = Student.query.get_or_404(student_id)

    # Referential Integrity Check: Placements have ON DELETE RESTRICT
    if student.placements.count() > 0:
        flash(f'Cannot delete student {student.roll_number}: Active placement offers exist. Remove placement record first to protect historical integrity.', 'danger')
        return redirect(url_for('students.index'))

    try:
        db.session.delete(student)
        db.session.commit()
        flash(f'Student {student.roll_number} deleted successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Referential integrity violation: Cannot delete student ({str(e)})', 'danger')

    return redirect(url_for('students.index'))
