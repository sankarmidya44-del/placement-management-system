import os
import sys
from datetime import datetime, date, timezone
from decimal import Decimal
import click
from flask import Flask, redirect, url_for, render_template, flash
from flask_login import LoginManager, current_user
from sqlalchemy import text
from sqlalchemy.exc import OperationalError

from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent
BASE_DIR = BACKEND_DIR.parent
FRONTEND_DIR = BASE_DIR / 'frontend'

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from flask_cors import CORS
from config import config_by_name, BASE_DIR
from models import db, User, Department, Student, Company, Job, Application, Interview, Placement, AuditLog


def create_app(config_name=None):
    """Application Factory Pattern."""
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'production')

    # Resolve template and static asset locations across backend & frontend
    template_candidates = [
        FRONTEND_DIR / 'templates',
        BACKEND_DIR / 'templates',
        BASE_DIR / 'templates'
    ]
    static_candidates = [
        FRONTEND_DIR / 'static',
        BACKEND_DIR / 'static',
        BASE_DIR / 'static'
    ]
    template_dir = next((str(p) for p in template_candidates if p.exists()), 'templates')
    static_dir = next((str(p) for p in static_candidates if p.exists()), 'static')

    app = Flask(
        __name__,
        template_folder=template_dir,
        static_folder=static_dir
    )
    app.url_map.strict_slashes = False
    app.config.from_object(config_by_name.get(config_name, config_by_name['default']))

    # Initialize extensions
    db.init_app(app)
    CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

    # Initialize Flask-Login
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'warning'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    # Register blueprints
    from routes.auth import auth_bp
    from routes.admin import admin_bp
    from routes.students import students_bp
    from routes.companies import companies_bp
    from routes.jobs import jobs_bp
    from routes.applications import applications_bp
    from routes.api import api_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(students_bp)
    app.register_blueprint(companies_bp)
    app.register_blueprint(jobs_bp)
    app.register_blueprint(applications_bp)
    app.register_blueprint(api_bp)

    @app.route('/health')
    def health_redirect():
        return redirect(url_for('api.health'))

    # Root redirect
    @app.route('/')
    def root():
        if current_user.is_authenticated:
            if current_user.is_admin:
                return redirect(url_for('admin.dashboard'))
            return redirect(url_for('jobs.index'))
        return redirect(url_for('auth.login'))

    @app.route('/login')
    def login_alias():
        return redirect(url_for('auth.login'))

    @app.route('/register')
    def register_alias():
        return redirect(url_for('auth.register'))

    # Context processors for templates
    @app.context_processor
    def inject_globals():
        return {
            'app_name': 'Student Placement Management System',
            'current_year': datetime.now(timezone.utc).year,
            'today': date.today()
        }

    # Error handlers
    @app.errorhandler(403)
    def forbidden(e):
        return render_template('base.html', error_code=403, error_message="Access Forbidden: You do not have permissions for this resource."), 403

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('base.html', error_code=404, error_message="Page Not Found: The requested URL was not found on the server."), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('base.html', error_code=500, error_message="Internal Server Error: A database or system error occurred."), 500

    # CLI Commands
    @app.cli.command('init-db')
    def init_db():
        """Creates all database tables based on SQLAlchemy models."""
        with app.app_context():
            db.create_all()
            print("[SPMS] Database tables created successfully.")

    @app.cli.command('seed-db')
    def seed_db():
        """Seeds the database with realistic sample data if empty."""
        with app.app_context():
            populate_sample_data()
            print("[SPMS] Sample data seeded successfully.")

    @app.cli.command('create-user')
    @click.option('--username', prompt=True, help='Account username')
    @click.option('--email', prompt=True, help='Account email')
    @click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True, help='Account password')
    @click.option('--role', prompt=True, type=click.Choice(['Admin', 'Student'], case_sensitive=False), default='Admin')
    def create_user(username, email, password, role):
        """CLI tool to create a new user (Admin or Student)."""
        with app.app_context():
            role_norm = role.capitalize()
            if User.query.filter_by(username=username).first():
                print(f"[SPMS Error] Username '{username}' is already taken.")
                return
            if User.query.filter_by(email=email).first():
                print(f"[SPMS Error] Email '{email}' is already registered.")
                return

            new_user = User(
                username=username,
                email=email,
                role=role_norm
            )
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()
            print(f"[SPMS Success] User '{username}' with role '{role_norm}' created successfully.")

    # Populate sample data for SQLite fallback in development if empty
    if not app.config.get('TESTING', False):
        with app.app_context():
            try:
                db.create_all()
                populate_sample_data()
            except Exception as e:
                print(f"[SPMS Notice] Database initialization error: {e}")

    return app


def populate_sample_data():
    """Populates initial sample data if departments table is empty."""
    if Department.query.first():
        return

    print("[SPMS] Seeding departments, companies, jobs, students, and placements...")
    
    # 1. Departments
    dept_cse = Department(department_name='Computer Science & Engineering', department_code='CSE')
    dept_it = Department(department_name='Information Technology', department_code='IT')
    dept_ece = Department(department_name='Electronics & Communication Engineering', department_code='ECE')
    dept_me = Department(department_name='Mechanical Engineering', department_code='ME')
    dept_eee = Department(department_name='Electrical & Electronics Engineering', department_code='EEE')
    db.session.add_all([dept_cse, dept_it, dept_ece, dept_me, dept_eee])
    db.session.flush()

    # 2. Admin User
    admin = User(
        username='admin',
        email='placement.officer@college.edu',
        role='Admin'
    )
    admin.set_password('admin123')
    db.session.add(admin)

    # 3. Students
    students_data = [
        ('21CS001', 'Aarav', 'Sharma', 'aarav.sharma@college.edu', '9876543210', dept_cse.department_id, 2025, 9.40, 0),
        ('21CS002', 'Priya', 'Patel', 'priya.patel@college.edu', '9876543211', dept_cse.department_id, 2025, 8.85, 0),
        ('21CS003', 'Rohan', 'Verma', 'rohan.verma@college.edu', '9876543212', dept_cse.department_id, 2025, 7.60, 1),
        ('21CS004', 'Sneha', 'Reddy', 'sneha.reddy@college.edu', '9876543213', dept_cse.department_id, 2025, 9.15, 0),
        ('21IT001', 'Aditya', 'Nair', 'aditya.nair@college.edu', '9876543214', dept_it.department_id, 2025, 8.20, 0),
        ('21IT002', 'Ananya', 'Iyer', 'ananya.iyer@college.edu', '9876543215', dept_it.department_id, 2025, 9.05, 0),
        ('21IT003', 'Vikram', 'Singh', 'vikram.singh@college.edu', '9876543216', dept_it.department_id, 2025, 6.90, 2),
        ('21EC001', 'Kavya', 'Menon', 'kavya.menon@college.edu', '9876543217', dept_ece.department_id, 2025, 8.45, 0),
        ('21EC002', 'Rahul', 'Gupta', 'rahul.gupta@college.edu', '9876543218', dept_ece.department_id, 2025, 7.80, 0),
        ('21EC003', 'Deepika', 'Joshi', 'deepika.joshi@college.edu', '9876543219', dept_ece.department_id, 2025, 9.30, 0),
        ('21ME001', 'Arjun', 'Kulkarni', 'arjun.kulkarni@college.edu', '9876543220', dept_me.department_id, 2025, 7.50, 0),
        ('21ME002', 'Pooja', 'Deshmukh', 'pooja.deshmukh@college.edu', '9876543221', dept_me.department_id, 2025, 8.10, 0),
        ('21EE001', 'Siddharth', 'Rao', 'siddharth.rao@college.edu', '9876543222', dept_eee.department_id, 2025, 8.60, 0),
        ('21EE002', 'Meera', 'Pillai', 'meera.pillai@college.edu', '9876543223', dept_eee.department_id, 2025, 7.20, 1),
        ('22CS001', 'Karan', 'Malhotra', 'karan.malhotra@college.edu', '9876543224', dept_cse.department_id, 2026, 8.90, 0),
        ('22CS002', 'Divya', 'Bansal', 'divya.bansal@college.edu', '9876543225', dept_cse.department_id, 2026, 9.60, 0),
        ('22IT001', 'Varun', 'Mehta', 'varun.mehta@college.edu', '9876543226', dept_it.department_id, 2026, 7.40, 0),
        ('22EC001', 'Tanvi', 'Shah', 'tanvi.shah@college.edu', '9876543227', dept_ece.department_id, 2026, 8.70, 0),
        ('22ME001', 'Nikhil', 'Chopra', 'nikhil.chopra@college.edu', '9876543228', dept_me.department_id, 2026, 6.75, 1),
        ('22EE001', 'Riya', 'Sen', 'riya.sen@college.edu', '9876543229', dept_eee.department_id, 2026, 8.35, 0),
        ('21CS005', 'Harsh', 'Vardhan', 'harsh.vardhan@college.edu', '9876543230', dept_cse.department_id, 2025, 6.40, 3),
        ('21IT004', 'Simran', 'Kaur', 'simran.kaur@college.edu', '9876543231', dept_it.department_id, 2025, 9.75, 0)
    ]

    created_students = []
    for roll, fn, ln, em, ph, dept_id, yr, cgpa, backlogs in students_data:
        st = Student(
            roll_number=roll, first_name=fn, last_name=ln, email=em, phone=ph,
            department_id=dept_id, graduation_year=yr, cgpa=Decimal(str(cgpa)),
            backlogs=backlogs, resume_url=f"https://storage.college.edu/resumes/{roll}.pdf"
        )
        db.session.add(st)
        created_students.append(st)
    db.session.flush()

    # Create user accounts for first 4 students
    for st in created_students[:4]:
        username = st.email.split('@')[0]
        u = User(username=username, email=st.email, role='Student', student_id=st.student_id)
        u.set_password('student123')
        db.session.add(u)

    # 4. Companies
    companies_data = [
        ('Google India', 'Technology / Internet', 'https://careers.google.com', 'india-campus@google.com', '+91 80 6721 8000', 'Global technology leader specializing in search, cloud computing, and AI.'),
        ('Microsoft India', 'Software / Cloud', 'https://careers.microsoft.com', 'msindia-campus@microsoft.com', '+91 80 4010 3000', 'World leader in personal computing platforms and Azure cloud services.'),
        ('Amazon Web Services', 'Cloud / E-Commerce', 'https://amazon.jobs', 'aws-grad-hiring@amazon.com', '+91 80 4344 0000', 'Pioneering cloud computing infrastructure and large-scale distributed systems.'),
        ('Tata Consultancy Services', 'IT Services / Consulting', 'https://www.tcs.com/careers', 'campus.tcs@tcs.com', '+91 22 6778 9999', 'Premier multinational information technology services and consulting organization.'),
        ('Infosys Limited', 'IT Services', 'https://www.infosys.com/careers', 'talent@infosys.com', '+91 80 2852 0261', 'Global provider of digital services, next-generation IT consulting, and outsourcing.'),
        ('Cisco Systems', 'Networking / Cybersecurity', 'https://www.cisco.com/careers', 'cisco-india-campus@cisco.com', '+91 80 4426 0000', 'Worldwide leader in computer networking hardware, IoT, and cybersecurity software.'),
        ('Deloitte USI', 'Management & Tech Consulting', 'https://www2.deloitte.com', 'usi-campus@deloitte.com', '+91 40 6762 1000', 'Top-tier audit, consulting, tax, and advisory services for global enterprises.'),
        ('Qualcomm India', 'Semiconductors / Wireless', 'https://www.qualcomm.com/careers', 'qualcomm-campus@qualcomm.com', '+91 40 6608 0000', 'World leading wireless technology innovator and semiconductor designer.'),
        ('Larsen & Toubro', 'Engineering / Infrastructure', 'https://www.larsentoubro.com', 'lnt-campus@larsentoubro.com', '+91 22 6752 5656', 'Major technology, engineering, construction, manufacturing, and financial conglomerate.')
    ]
    created_companies = []
    for name, ind, web, em, ph, desc in companies_data:
        comp = Company(company_name=name, industry=ind, website=web, contact_email=em, contact_phone=ph, company_description=desc)
        db.session.add(comp)
        created_companies.append(comp)
    db.session.flush()

    # 5. Jobs
    jobs_data = [
        (created_companies[0].company_id, 'Software Engineer - Campus', 'Build distributed cloud infrastructure and AI models.', 'Full-Time', 'Bangalore / Hyderabad', 8.50, 0, 32.00, date(2026, 11, 30), 'Open'),
        (created_companies[1].company_id, 'Software Development Engineer I', 'Develop Azure cloud solutions and developer tooling.', 'Full-Time', 'Hyderabad', 8.00, 0, 28.50, date(2026, 11, 25), 'Open'),
        (created_companies[2].company_id, 'Cloud Support Associate', 'Enterprise cloud architecture guidance on AWS.', 'Full-Time', 'Bangalore', 7.50, 0, 18.00, date(2026, 12, 5), 'Open'),
        (created_companies[2].company_id, 'Software Development Engineer - Intern', 'Microservices and DynamoDB high-scale features.', 'Internship', 'Hyderabad', 8.00, 0, 12.00, date(2026, 10, 15), 'Closed'),
        (created_companies[3].company_id, 'Digital Software Developer', 'Next-gen software engineering and cloud-native applications.', 'Full-Time', 'Pan India', 7.00, 1, 7.50, date(2026, 12, 15), 'Open'),
        (created_companies[3].company_id, 'Ninja Developer', 'Core software systems engineering and automation.', 'Full-Time', 'Pune / Chennai', 6.50, 1, 3.80, date(2026, 12, 31), 'Open'),
        (created_companies[4].company_id, 'Specialist Programmer', 'High-performance computing and enterprise architecture.', 'Full-Time', 'Bangalore / Mysore', 7.50, 0, 9.50, date(2026, 11, 20), 'Open'),
        (created_companies[4].company_id, 'Systems Engineer', 'Application maintenance and full-stack software development.', 'Full-Time', 'Pan India', 6.00, 2, 4.00, date(2026, 12, 20), 'Open'),
        (created_companies[5].company_id, 'Network Software Engineer', 'Design software-defined networking stacks.', 'Full-Time', 'Bangalore', 7.80, 0, 19.50, date(2026, 11, 15), 'Open'),
        (created_companies[6].company_id, 'Technology Analyst', 'Implement SAP, Salesforce, and cloud transformation.', 'Full-Time', 'Hyderabad / Mumbai', 7.00, 0, 9.00, date(2026, 11, 28), 'Open'),
        (created_companies[7].company_id, 'Hardware / Embedded Engineer', 'ASIC design, RTL verification, and SoC firmware.', 'Full-Time', 'Hyderabad / Chennai', 8.00, 0, 22.00, date(2026, 11, 18), 'Open'),
        (created_companies[8].company_id, 'Graduate Engineer Trainee', 'Mechanical systems design and robotics automation.', 'Full-Time', 'Mumbai / Baroda', 6.80, 0, 6.50, date(2026, 12, 10), 'Open')
    ]
    created_jobs = []
    for cid, title, desc, jtype, loc, min_cgpa, max_b, sal, deadl, status in jobs_data:
        j = Job(
            company_id=cid, job_title=title, job_description=desc, job_type=jtype,
            location=loc, minimum_cgpa=Decimal(str(min_cgpa)), maximum_backlogs=max_b,
            salary_lpa=Decimal(str(sal)), application_deadline=deadl, job_status=status
        )
        db.session.add(j)
        created_jobs.append(j)
    db.session.flush()

    # 6. Applications (Varied statuses)
    apps_data = [
        (created_students[0].student_id, created_jobs[0].job_id, 'Selected'),
        (created_students[0].student_id, created_jobs[1].job_id, 'Shortlisted'),
        (created_students[1].student_id, created_jobs[0].job_id, 'Interview Scheduled'),
        (created_students[1].student_id, created_jobs[1].job_id, 'Selected'),
        (created_students[2].student_id, created_jobs[4].job_id, 'Shortlisted'),
        (created_students[2].student_id, created_jobs[5].job_id, 'Applied'),
        (created_students[3].student_id, created_jobs[0].job_id, 'Interview Scheduled'),
        (created_students[3].student_id, created_jobs[2].job_id, 'Selected'),
        (created_students[4].student_id, created_jobs[2].job_id, 'Selected'),
        (created_students[4].student_id, created_jobs[4].job_id, 'Withdrawn'),
        (created_students[5].student_id, created_jobs[1].job_id, 'Selected'),
        (created_students[5].student_id, created_jobs[6].job_id, 'Shortlisted'),
        (created_students[6].student_id, created_jobs[5].job_id, 'Rejected'),
        (created_students[6].student_id, created_jobs[7].job_id, 'Applied'),
        (created_students[7].student_id, created_jobs[8].job_id, 'Selected'),
        (created_students[7].student_id, created_jobs[10].job_id, 'Shortlisted'),
        (created_students[8].student_id, created_jobs[4].job_id, 'Shortlisted'),
        (created_students[8].student_id, created_jobs[8].job_id, 'Rejected'),
        (created_students[9].student_id, created_jobs[10].job_id, 'Selected'),
        (created_students[10].student_id, created_jobs[11].job_id, 'Selected'),
        (created_students[11].student_id, created_jobs[9].job_id, 'Selected'),
        (created_students[12].student_id, created_jobs[9].job_id, 'Interview Scheduled'),
        (created_students[12].student_id, created_jobs[10].job_id, 'Rejected'),
        (created_students[13].student_id, created_jobs[5].job_id, 'Applied'),
        (created_students[14].student_id, created_jobs[1].job_id, 'Shortlisted'),
        (created_students[15].student_id, created_jobs[0].job_id, 'Interview Scheduled'),
        (created_students[16].student_id, created_jobs[6].job_id, 'Applied')
    ]
    created_apps = []
    for sid, jid, status in apps_data:
        app_obj = Application(student_id=sid, job_id=jid, application_status=status)
        db.session.add(app_obj)
        created_apps.append(app_obj)
    db.session.flush()

    # 7. Interviews
    interviews_data = [
        (created_apps[0].application_id, 'Technical Round 1', datetime(2026, 9, 25, 10, 0), 'Online', 'Google Meet', 'Strong problem solving in algorithms.', 'Passed'),
        (created_apps[0].application_id, 'System Design & HR', datetime(2026, 9, 28, 14, 0), 'Online', 'Google Meet', 'Exceptional scalability insights.', 'Passed'),
        (created_apps[2].application_id, 'Technical Round 1', datetime(2026, 10, 2, 11, 0), 'Online', 'Google Meet', 'Good SQL execution concepts.', 'Pending'),
        (created_apps[3].application_id, 'Technical Round 1', datetime(2026, 9, 24, 10, 30), 'Online', 'MS Teams', 'Clean C++ coding style.', 'Passed'),
        (created_apps[6].application_id, 'Technical Round 1', datetime(2026, 10, 3, 14, 30), 'Online', 'Google Meet', 'Dynamic programming evaluation.', 'Pending')
    ]
    for aid, rnd, dt, mode, loc, notes, res in interviews_data:
        inv = Interview(application_id=aid, interview_round=rnd, interview_date=dt, interview_mode=mode, interview_location=loc, interviewer_notes=notes, interview_result=res)
        db.session.add(inv)

    # 8. Placements
    placements_data = [
        (created_students[0].student_id, created_jobs[0].job_id, created_companies[0].company_id, date(2026, 10, 1), Decimal('32.00')),
        (created_students[1].student_id, created_jobs[1].job_id, created_companies[1].company_id, date(2026, 10, 2), Decimal('28.50')),
        (created_students[3].student_id, created_jobs[2].job_id, created_companies[2].company_id, date(2026, 10, 3), Decimal('18.00')),
        (created_students[4].student_id, created_jobs[2].job_id, created_companies[2].company_id, date(2026, 10, 3), Decimal('18.00')),
        (created_students[5].student_id, created_jobs[1].job_id, created_companies[1].company_id, date(2026, 10, 4), Decimal('28.50')),
        (created_students[7].student_id, created_jobs[8].job_id, created_companies[5].company_id, date(2026, 10, 5), Decimal('19.50')),
        (created_students[9].student_id, created_jobs[10].job_id, created_companies[7].company_id, date(2026, 10, 5), Decimal('22.00')),
        (created_students[11].student_id, created_jobs[9].job_id, created_companies[6].company_id, date(2026, 10, 6), Decimal('9.00'))
    ]
    for sid, jid, cid, off_date, pkg in placements_data:
        plc = Placement(student_id=sid, job_id=jid, company_id=cid, offer_date=off_date, package_lpa=pkg, placement_status='Accepted')
        db.session.add(plc)

    # 9. Audit Logs
    audit1 = AuditLog(table_name='applications', record_id=1, action='UPDATE', old_values='status: Shortlisted', new_values='status: Selected', changed_by='admin')
    audit2 = AuditLog(table_name='placements', record_id=1, action='INSERT', old_values=None, new_values='Placement offer 32.00 LPA for Aarav Sharma', changed_by='admin')
    db.session.add_all([audit1, audit2])

    db.session.commit()
    print("[SPMS] Sample data initialized successfully.")


app = create_app()

if __name__ == '__main__':
    # Default local address http://127.0.0.1:5000
    app.run(host='127.0.0.1', port=5000, debug=True)
