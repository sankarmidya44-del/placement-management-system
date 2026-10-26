# Automated Test Cases & Quality Assurance Specification
## Student Placement Management System (SPMS)

### 1. Test Architecture & Environment
The SPMS automated testing framework uses `pytest` with an isolated test configuration (`TestingConfig`).
- **Database Engine:** Isolated in-memory SQLite (`sqlite:///:memory:`) ensures that test runs have zero side effects on development or production databases.
- **Foreign Key Enforcement:** SQLite connection PRAGMA `foreign_keys = ON` is enforced via SQLAlchemy engine listeners, ensuring behavioral parity with MySQL 8 InnoDB.
- **Client Emulation:** Flask test client simulates HTTP GET/POST requests, session state, and flash notifications.

---

### 2. Test Execution Command
To execute the automated test suite in Windows PowerShell:
```powershell
# Activate the virtual environment
.\.venv\Scripts\Activate.ps1

# Run pytest with verbose reporting
pytest -v tests/test_app.py
```

---

### 3. Comprehensive Test Case Matrix

| Test ID | Test Function Name | Tested Component | Input / Scenario | Expected Outcome | Actual Result | Status |
| :---: | :--- | :--- | :--- | :--- | :---: | :---: |
| **TC-01** | `test_app_startup` | Core App Factory | `GET /` without authentication | HTTP 302 Redirect to `/auth/login` | Redirected to `/auth/login` | **PASS** |
| **TC-02** | `test_login_validation` | Auth / Security | Bad credentials (`admin`/`wrongpass`), then valid credentials | Error alert on bad pass; Success greeting & dashboard render on valid | Authenticated & directed to dashboard | **PASS** |
| **TC-03** | `test_registration_validation` | Student Onboarding | Password mismatch, then valid registration payload | Blocked on mismatch; Created `Student` & `User` in single transaction | Profile registered & ready for login | **PASS** |
| **TC-04** | `test_authorization_rbac` | Security / RBAC | Student user attempts to access `/admin/dashboard` & `/admin/reports` | Access Denied alert flashed, redirected to student job index | Non-admins forbidden | **PASS** |
| **TC-05** | `test_student_creation` | Relational Entity | Programmatic creation of Student linked to Department | Successfully committed; Department relation accessible; unplaced flag | Record created & accessible | **PASS** |
| **TC-06** | `test_duplicate_student_prevention` | DB Integrity | Insertion of student with duplicate `roll_number` | Database engine raises `IntegrityError` violating UNIQUE constraint | Duplicate blocked | **PASS** |
| **TC-07** | `test_duplicate_application_prevention` | DB & Service Integrity | Student submits two applications for the same `job_id` | Second attempt rejected with "You have already applied" | Second submission blocked | **PASS** |
| **TC-08** | `test_invalid_foreign_key_references` | Referential Integrity | Job inserted with non-existent `company_id = 99999` | Database engine raises foreign key violation exception | Invalid foreign key rejected | **PASS** |
| **TC-09** | `test_job_eligibility_checks` | Placement Service | Student with 8.50 CGPA applies for job requiring 9.00 CGPA | Rejected with "CGPA requirement not met" | Ineligible student blocked | **PASS** |
| **TC-10** | `test_application_deadline_checks` | Business Rules | Student applies for expired job or closed job | Rejected with deadline expired or job closed notice | Expired/closed jobs blocked | **PASS** |
| **TC-11** | `test_placement_record_creation` | Multi-table Workflow | Admin selects candidate with 16.50 LPA offer package | Status updated to `Selected`, `Placement` record created atomically | Offer recorded & student placed | **PASS** |
| **TC-12** | `test_invalid_cgpa_values` | Domain Validation | Registration with invalid `cgpa = 11.50` | Form rejected with "CGPA must be between 0.00 and 10.00" | Out-of-bounds CGPA rejected | **PASS** |
| **TC-13** | `test_sql_transaction_rollback_on_failure` | ACID Transactions | Selection executed with negative salary (`-5.00 LPA`) | Fails validation; transaction rolled back; application status untouched | Atomicity preserved | **PASS** |

---

### 4. ACID Transaction Demonstration Details

#### Atomicity Test Case (TC-13):
- **Scenario:** During candidate selection, multiple database writes occur:
  1. `UPDATE applications SET application_status = 'Selected'`
  2. `INSERT INTO placements (...)`
  3. `INSERT INTO audit_logs (...)`
- **Failure Injection:** An invalid package amount (`-5.00 LPA`) is passed.
- **Verification:**
  - The service intercepts the error, rolls back the database session (`db.session.rollback()`).
  - Inspection of the database verifies that `applications.application_status` remains strictly unchanged at `'Applied'`.
  - No orphaned row exists in `placements`.
  - Atomicity is 100% verified: *All operations succeed together, or none take effect.*
