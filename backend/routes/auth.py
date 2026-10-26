from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from models import db, User, Student, Department

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.is_admin:
            return redirect(url_for('admin.dashboard'))
        return redirect(url_for('jobs.index'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        if not username or not password:
            flash('Please enter both username and password.', 'warning')
            return render_template('login.html')

        user = User.query.filter(
            (User.username == username) | (User.email == username)
        ).first()

        if user and user.check_password(password):
            login_user(user)
            flash(f'Welcome back, {user.username}!', 'success')
            next_page = request.args.get('next')
            if next_page and next_page.startswith('/'):
                return redirect(next_page)
            if user.is_admin:
                return redirect(url_for('admin.dashboard'))
            return redirect(url_for('jobs.index'))
        else:
            flash('Invalid username or password. Please try again.', 'danger')

    return render_template('login.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('jobs.index'))

    departments = Department.query.order_by(Department.department_name).all()

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        # Student details
        roll_number = request.form.get('roll_number', '').strip().upper()
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        department_id = request.form.get('department_id')
        graduation_year = request.form.get('graduation_year')
        cgpa = request.form.get('cgpa')
        backlogs = request.form.get('backlogs', 0)
        phone = request.form.get('phone', '').strip()
        resume_url = request.form.get('resume_url', '').strip()

        # Validations
        if not all([username, email, password, roll_number, first_name, last_name, department_id, graduation_year, cgpa]):
            flash('Please fill in all mandatory fields.', 'warning')
            return render_template('register.html', departments=departments)

        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('register.html', departments=departments)

        if len(password) < 6:
            flash('Password must be at least 6 characters long.', 'danger')
            return render_template('register.html', departments=departments)

        try:
            cgpa_val = float(cgpa)
            if not (0.0 <= cgpa_val <= 10.0):
                flash('CGPA must be between 0.00 and 10.00.', 'danger')
                return render_template('register.html', departments=departments)
        except ValueError:
            flash('Invalid CGPA format.', 'danger')
            return render_template('register.html', departments=departments)

        try:
            backlogs_val = int(backlogs)
            if backlogs_val < 0:
                flash('Backlogs cannot be negative.', 'danger')
                return render_template('register.html', departments=departments)
        except ValueError:
            flash('Invalid backlogs count.', 'danger')
            return render_template('register.html', departments=departments)

        # Uniqueness checks
        if User.query.filter_by(username=username).first():
            flash('Username is already taken.', 'danger')
            return render_template('register.html', departments=departments)

        if User.query.filter_by(email=email).first() or Student.query.filter_by(email=email).first():
            flash('Email address is already registered.', 'danger')
            return render_template('register.html', departments=departments)

        if Student.query.filter_by(roll_number=roll_number).first():
            flash('Roll number is already registered.', 'danger')
            return render_template('register.html', departments=departments)

        # Atomic Registration
        try:
            student = Student(
                roll_number=roll_number,
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone=phone,
                department_id=int(department_id),
                graduation_year=int(graduation_year),
                cgpa=cgpa_val,
                backlogs=backlogs_val,
                resume_url=resume_url or None
            )
            db.session.add(student)
            db.session.flush()

            user = User(
                username=username,
                email=email,
                role='Student',
                student_id=student.student_id
            )
            user.set_password(password)
            db.session.add(user)

            db.session.commit()
            flash('Registration successful! You may now sign in.', 'success')
            return redirect(url_for('auth.login'))

        except Exception as e:
            db.session.rollback()
            flash(f'Registration failed due to a system error: {str(e)}', 'danger')

    return render_template('register.html', departments=departments)


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('auth.login'))
