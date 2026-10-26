import os
import pytest
from datetime import date, timedelta, datetime
from decimal import Decimal
from sqlalchemy.exc import IntegrityError

from app import create_app
from models import db, User, Department, Student, Company, Job, Application, Placement, AuditLog
from services.placement_service import PlacementService


@pytest.fixture
def app():
    """Create and configure an isolated application instance for testing."""
    test_app = create_app('testing')

    with test_app.app_context():
        db.create_all()

        # Seed baseline test entities
        dept = Department(department_name='Computer Science', department_code='CSE')
        db.session.add(dept)
        db.session.flush()

        admin = User(username='admin', email='admin@test.edu', role='Admin')
        admin.set_password('admin123')
        db.session.add(admin)

        student = Student(
            roll_number='21CS999',
            first_name='Test',
            last_name='Student',
            email='student@test.edu',
            phone='9999999999',
            department_id=dept.department_id,
            graduation_year=2025,
            cgpa=Decimal('8.50'),
            backlogs=0
        )
        db.session.add(student)
        db.session.flush()

        student_user = User(
            username='teststudent',
            email='student@test.edu',
            role='Student',
            student_id=student.student_id
        )
        student_user.set_password('student123')
        db.session.add(student_user)

        company = Company(
            company_name='TestCorp',
            industry='Technology',
            contact_email='recruiter@testcorp.com'
        )
        db.session.add(company)
        db.session.flush()

        # Active Job
        job_active = Job(
            company_id=company.company_id,
            job_title='Software Engineer',
            job_type='Full-Time',
            location='Bangalore',
            minimum_cgpa=Decimal('7.50'),
            maximum_backlogs=0,
            salary_lpa=Decimal('15.00'),
            application_deadline=date.today() + timedelta(days=30),
            job_status='Open'
        )

        # Expired Job
        job_expired = Job(
            company_id=company.company_id,
            job_title='Expired Associate',
            job_type='Full-Time',
            minimum_cgpa=Decimal('6.00'),
            maximum_backlogs=1,
            salary_lpa=Decimal('8.00'),
            application_deadline=date.today() - timedelta(days=5),
            job_status='Open'
        )

        # Closed Job
        job_closed = Job(
            company_id=company.company_id,
            job_title='Closed Role',
            job_type='Full-Time',
            minimum_cgpa=Decimal('6.00'),
            maximum_backlogs=1,
            salary_lpa=Decimal('8.00'),
            application_deadline=date.today() + timedelta(days=10),
            job_status='Closed'
        )

        db.session.add_all([job_active, job_expired, job_closed])
        db.session.commit()

        yield test_app

        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Test client for HTTP requests."""
    return app.test_client()


# ------------------------------------------------------------------------------
# 1. Test Application Startup
# ------------------------------------------------------------------------------
def test_app_startup(client):
    """Verify application initializes and routes root to login or dashboard."""
    response = client.get('/', follow_redirects=False)
    assert response.status_code == 302
    assert '/auth/login' in response.headers['Location']


# ------------------------------------------------------------------------------
# 2. Test Login Validation
# ------------------------------------------------------------------------------
def test_login_validation(client):
    """Verify login validation for valid and invalid credentials."""
    # Invalid password
    bad_resp = client.post('/auth/login', data={
        'username': 'admin',
        'password': 'wrongpassword'
    }, follow_redirects=True)
    assert b'Invalid username or password' in bad_resp.data

    # Valid login
    good_resp = client.post('/auth/login', data={
        'username': 'admin',
        'password': 'admin123'
    }, follow_redirects=True)
    assert b'Welcome back, admin!' in good_resp.data
    assert b'Placement Administration Dashboard' in good_resp.data


# ------------------------------------------------------------------------------
# 3. Test Registration Validation
# ------------------------------------------------------------------------------
def test_registration_validation(client, app):
    """Verify student registration form validations."""
    with app.app_context():
        dept = Department.query.first()

        # Mismatched passwords
        mismatch_resp = client.post('/auth/register', data={
            'username': 'newuser',
            'email': 'newuser@college.edu',
            'password': 'password123',
            'confirm_password': 'differentpassword',
            'roll_number': '21CS101',
            'first_name': 'New',
            'last_name': 'User',
            'department_id': dept.department_id,
            'graduation_year': 2026,
            'cgpa': '8.20',
            'backlogs': 0
        }, follow_redirects=True)
        assert b'Passwords do not match' in mismatch_resp.data

        # Valid registration
        valid_resp = client.post('/auth/register', data={
            'username': 'newstudent',
            'email': 'newstudent@college.edu',
            'password': 'password123',
            'confirm_password': 'password123',
            'roll_number': '21CS101',
            'first_name': 'Jane',
            'last_name': 'Doe',
            'department_id': dept.department_id,
            'graduation_year': 2026,
            'cgpa': '8.80',
            'backlogs': 0
        }, follow_redirects=True)
        assert b'Registration successful' in valid_resp.data

        created = Student.query.filter_by(roll_number='21CS101').first()
        assert created is not None
        assert created.full_name == 'Jane Doe'


# ------------------------------------------------------------------------------
# 4. Test Authorization and Role-Based Access Control (RBAC)
# ------------------------------------------------------------------------------
def test_authorization_rbac(client):
    """Verify students cannot access administrative dashboards and routes."""
    # Log in as regular Student
    client.post('/auth/login', data={
        'username': 'teststudent',
        'password': 'student123'
    }, follow_redirects=True)

    # Attempt to access admin dashboard
    admin_resp = client.get('/admin/dashboard', follow_redirects=True)
    assert b'Access Denied: Administrative privileges required' in admin_resp.data

    # Attempt to access admin reports
    reports_resp = client.get('/admin/reports', follow_redirects=True)
    assert b'Access Denied: Administrative privileges required' in reports_resp.data


# ------------------------------------------------------------------------------
# 5. Test Student Creation
# ------------------------------------------------------------------------------
def test_student_creation(app):
    """Verify programmatic creation of students with relational integrity."""
    with app.app_context():
        dept = Department.query.first()
        student = Student(
            roll_number='21CS888',
            first_name='Kavita',
            last_name='Roy',
            email='kavita@college.edu',
            department_id=dept.department_id,
            graduation_year=2025,
            cgpa=Decimal('9.10'),
            backlogs=0
        )
        db.session.add(student)
        db.session.commit()

        retrieved = Student.query.filter_by(roll_number='21CS888').first()
        assert retrieved is not None
        assert retrieved.department.department_code == 'CSE'
        assert retrieved.is_placed is False


# ------------------------------------------------------------------------------
# 6. Test Duplicate Student Prevention
# ------------------------------------------------------------------------------
def test_duplicate_student_prevention(app):
    """Enforces UNIQUE roll_number and UNIQUE email constraints."""
    with app.app_context():
        dept = Department.query.first()
        # Duplicate roll number
        dup_roll = Student(
            roll_number='21CS999',  # Already exists in fixture
            first_name='Duplicate',
            last_name='Roll',
            email='unique.email@test.edu',
            department_id=dept.department_id,
            graduation_year=2025,
            cgpa=Decimal('8.00'),
            backlogs=0
        )
        db.session.add(dup_roll)
        with pytest.raises(IntegrityError):
            db.session.commit()
        db.session.rollback()


# ------------------------------------------------------------------------------
# 7. Test Duplicate Application Prevention
# ------------------------------------------------------------------------------
def test_duplicate_application_prevention(app):
    """Enforces UNIQUE(student_id, job_id) constraint preventing multiple applications."""
    with app.app_context():
        student = Student.query.filter_by(roll_number='21CS999').first()
        job = Job.query.filter_by(job_title='Software Engineer').first()

        # First application succeeds
        ok1, msg1 = PlacementService.apply_for_job(student.student_id, job.job_id)
        assert ok1 is True

        # Second application must fail
        ok2, msg2 = PlacementService.apply_for_job(student.student_id, job.job_id)
        assert ok2 is False
        assert "already applied" in msg2.lower()


# ------------------------------------------------------------------------------
# 8. Test Invalid Foreign Key References
# ------------------------------------------------------------------------------
def test_invalid_foreign_key_references(app):
    """Verify that records with non-existent foreign keys are rejected."""
    with app.app_context():
        invalid_job = Job(
            company_id=99999,  # Non-existent company
            job_title='Ghost Job',
            salary_lpa=Decimal('10.00'),
            application_deadline=date.today() + timedelta(days=5),
            job_status='Open'
        )
        db.session.add(invalid_job)
        # In SQLite / MySQL FK violation raises IntegrityError on commit/flush
        with pytest.raises(Exception):
            db.session.commit()
        db.session.rollback()


# ------------------------------------------------------------------------------
# 9. Test Job Eligibility Checks
# ------------------------------------------------------------------------------
def test_job_eligibility_checks(app):
    """Verify minimum CGPA and maximum backlogs academic validation."""
    with app.app_context():
        dept = Department.query.first()
        company = Company.query.first()

        # High bar job: Min CGPA 9.00
        elite_job = Job(
            company_id=company.company_id,
            job_title='Elite SDE',
            minimum_cgpa=Decimal('9.00'),
            maximum_backlogs=0,
            salary_lpa=Decimal('40.00'),
            application_deadline=date.today() + timedelta(days=20),
            job_status='Open'
        )
        db.session.add(elite_job)
        db.session.commit()

        # Student with 8.50 CGPA applies
        student = Student.query.filter_by(roll_number='21CS999').first() # CGPA is 8.50
        ok, msg = PlacementService.apply_for_job(student.student_id, elite_job.job_id)
        assert ok is False
        assert "CGPA requirement not met" in msg


# ------------------------------------------------------------------------------
# 10. Test Application Deadline Checks
# ------------------------------------------------------------------------------
def test_application_deadline_checks(app):
    """Enforce that expired and closed jobs reject applications."""
    with app.app_context():
        student = Student.query.filter_by(roll_number='21CS999').first()
        expired_job = Job.query.filter_by(job_title='Expired Associate').first()
        closed_job = Job.query.filter_by(job_title='Closed Role').first()

        # Expired deadline
        ok1, msg1 = PlacementService.apply_for_job(student.student_id, expired_job.job_id)
        assert ok1 is False
        assert "deadline" in msg1.lower()

        # Closed job
        ok2, msg2 = PlacementService.apply_for_job(student.student_id, closed_job.job_id)
        assert ok2 is False
        assert "closed" in msg2.lower()


# ------------------------------------------------------------------------------
# 11. Test Placement Record Creation
# ------------------------------------------------------------------------------
def test_placement_record_creation(app):
    """Verify candidate selection atomically creates placement and updates status."""
    with app.app_context():
        student = Student.query.filter_by(roll_number='21CS999').first()
        job = Job.query.filter_by(job_title='Software Engineer').first()

        # Submit application
        ok_app, _ = PlacementService.apply_for_job(student.student_id, job.job_id)
        assert ok_app is True

        app_record = Application.query.filter_by(student_id=student.student_id, job_id=job.job_id).first()

        # Select candidate
        ok_select, msg_select = PlacementService.select_and_place_candidate(
            application_id=app_record.application_id,
            package_lpa=Decimal('16.50'),
            admin_user='admin'
        )
        assert ok_select is True
        assert "successfully selected" in msg_select.lower()

        # Verify application status
        assert app_record.application_status == 'Selected'

        # Verify placement record
        plc = Placement.query.filter_by(student_id=student.student_id, job_id=job.job_id).first()
        assert plc is not None
        assert plc.package_lpa == Decimal('16.50')
        assert student.is_placed is True


# ------------------------------------------------------------------------------
# 12. Test Invalid CGPA Values
# ------------------------------------------------------------------------------
def test_invalid_cgpa_values(client, app):
    """Enforces CGPA range check (0.0 to 10.0)."""
    with app.app_context():
        dept = Department.query.first()
        # Post registration with CGPA = 11.50
        resp = client.post('/auth/register', data={
            'username': 'invalidcgpa',
            'email': 'invalidcgpa@college.edu',
            'password': 'password123',
            'confirm_password': 'password123',
            'roll_number': '21CS998',
            'first_name': 'Invalid',
            'last_name': 'CGPA',
            'department_id': dept.department_id,
            'graduation_year': 2026,
            'cgpa': '11.50',
            'backlogs': 0
        }, follow_redirects=True)
        assert b'CGPA must be between 0.00 and 10.00' in resp.data


# ------------------------------------------------------------------------------
# 13. Test SQL Transaction Rollback on Failure
# ------------------------------------------------------------------------------
def test_sql_transaction_rollback_on_failure(app):
    """Demonstrates Atomicity: If an operation fails, the transaction rolls back cleanly."""
    with app.app_context():
        student = Student.query.filter_by(roll_number='21CS999').first()
        job = Job.query.filter_by(job_title='Software Engineer').first()

        PlacementService.apply_for_job(student.student_id, job.job_id)
        app_record = Application.query.filter_by(student_id=student.student_id, job_id=job.job_id).first()

        # Attempt to select candidate with negative package (triggers validation rollback)
        ok, msg = PlacementService.select_and_place_candidate(
            application_id=app_record.application_id,
            package_lpa=Decimal('-5.00')
        )
        assert ok is False
        assert "greater than zero" in msg.lower()

        # Verify status did not change and placement was not inserted
        app_record_after = db.session.get(Application, app_record.application_id)
        assert app_record_after.application_status == 'Applied'
        assert Placement.query.filter_by(student_id=student.student_id).first() is None
