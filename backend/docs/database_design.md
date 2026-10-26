# Database Design & Relational Schema Specification
## Student Placement Management System (SPMS)
**Database Engine:** MySQL 8.0+ (InnoDB Storage Engine)  
**Character Set & Collation:** `utf8mb4` / `utf8mb4_unicode_ci`  
**Database Name:** `student_placement_db`

---

### 1. Architectural Overview & Design Philosophy
The SPMS database architecture is designed to enforce strict academic and institutional placement rules directly at the relational storage level. Rather than relying solely on application-layer checks, the schema utilizes:
- Primary Keys (`INT AUTO_INCREMENT`) for synthetic, immutable identifiers.
- Foreign Keys with explicit `ON DELETE` referential actions (`RESTRICT`, `CASCADE`, `SET NULL`).
- Domain Constraints (`CHECK`) on percentages, backlogs, monetary values, and enumerations.
- Candidate Keys (`UNIQUE`) preventing duplicate roll numbers, emails, applications, and placements.
- Specialized B-Tree Composite Indexes to optimize frequent range and equality queries.

---

### 2. Detailed Table Specifications

#### A. Table: `departments`
Stores academic departments offering degree programs.
```sql
CREATE TABLE departments (
    department_id INT AUTO_INCREMENT PRIMARY KEY,
    department_name VARCHAR(100) NOT NULL UNIQUE,
    department_code VARCHAR(20) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;
```
- **Primary Key:** `department_id` (Surrogate integer key for fast join indexing).
- **Unique Constraints:** `department_name` and `department_code` prevent duplicate institutional entries.

---

#### B. Table: `students`
Stores student academic credentials, contact info, and graduation metadata.
```sql
CREATE TABLE students (
    student_id INT AUTO_INCREMENT PRIMARY KEY,
    roll_number VARCHAR(50) NOT NULL UNIQUE,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    phone VARCHAR(20),
    department_id INT NOT NULL,
    graduation_year INT NOT NULL,
    cgpa DECIMAL(4, 2) NOT NULL,
    backlogs INT NOT NULL DEFAULT 0,
    resume_url VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_student_department
        FOREIGN KEY (department_id) REFERENCES departments(department_id)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT chk_student_cgpa
        CHECK (cgpa >= 0.00 AND cgpa <= 10.00),
    CONSTRAINT chk_student_backlogs
        CHECK (backlogs >= 0)
) ENGINE=InnoDB;
```
- **Referential Integrity:** `ON DELETE RESTRICT` on `department_id` prevents deleting an academic department while students are actively enrolled under it.
- **Data Integrity:** `chk_student_cgpa` enforces standard Indian 10-point GPA scale; `chk_student_backlogs` prevents negative backlog values.

---

#### C. Table: `users`
Handles authentication credentials and Role-Based Access Control (RBAC).
```sql
CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'Student',
    student_id INT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_user_student
        FOREIGN KEY (student_id) REFERENCES students(student_id)
        ON DELETE SET NULL ON UPDATE CASCADE,
    CONSTRAINT chk_user_role
        CHECK (role IN ('Admin', 'Student'))
) ENGINE=InnoDB;
```
- **Security:** Passwords are never stored in plaintext; salted hashes (Scrypt / Argon2) are stored.
- **Referential Integrity:** `ON DELETE SET NULL` ensures administrator accounts or detached student logins remain functional if student records are archived.

---

#### D. Table: `companies`
Stores corporate recruiters and hiring partners.
```sql
CREATE TABLE companies (
    company_id INT AUTO_INCREMENT PRIMARY KEY,
    company_name VARCHAR(100) NOT NULL,
    industry VARCHAR(100),
    website VARCHAR(255),
    contact_email VARCHAR(100),
    contact_phone VARCHAR(20),
    company_description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;
```

---

#### E. Table: `jobs`
Maintains campus recruitment postings, eligibility cutoffs, and deadlines.
```sql
CREATE TABLE jobs (
    job_id INT AUTO_INCREMENT PRIMARY KEY,
    company_id INT NOT NULL,
    job_title VARCHAR(100) NOT NULL,
    job_description TEXT,
    job_type VARCHAR(50) NOT NULL DEFAULT 'Full-Time',
    location VARCHAR(100),
    minimum_cgpa DECIMAL(4, 2) NOT NULL DEFAULT 0.00,
    maximum_backlogs INT NOT NULL DEFAULT 0,
    salary_lpa DECIMAL(10, 2) NOT NULL,
    application_deadline DATE NOT NULL,
    job_status VARCHAR(20) NOT NULL DEFAULT 'Open',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_job_company
        FOREIGN KEY (company_id) REFERENCES companies(company_id)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT chk_job_cgpa
        CHECK (minimum_cgpa >= 0.00 AND minimum_cgpa <= 10.00),
    CONSTRAINT chk_job_backlogs
        CHECK (maximum_backlogs >= 0),
    CONSTRAINT chk_job_salary
        CHECK (salary_lpa >= 0.00),
    CONSTRAINT chk_job_status
        CHECK (job_status IN ('Open', 'Closed'))
) ENGINE=InnoDB;
```
- **Referential Action:** `ON DELETE RESTRICT` ensures an organization cannot be deleted while active job postings exist.

---

#### F. Table: `applications`
Resolves the many-to-many relationship between Students and Jobs.
```sql
CREATE TABLE applications (
    application_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    job_id INT NOT NULL,
    application_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    application_status VARCHAR(50) NOT NULL DEFAULT 'Applied',
    resume_url VARCHAR(255),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_app_student
        FOREIGN KEY (student_id) REFERENCES students(student_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_app_job
        FOREIGN KEY (job_id) REFERENCES jobs(job_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT uq_student_job_application
        UNIQUE (student_id, job_id),
    CONSTRAINT chk_app_status
        CHECK (application_status IN ('Applied', 'Shortlisted', 'Interview Scheduled', 'Selected', 'Rejected', 'Withdrawn'))
) ENGINE=InnoDB;
```
- **Integrity Rule:** `UNIQUE(student_id, job_id)` structurally prohibits a candidate from submitting duplicate applications to the same drive.

---

#### G. Table: `interviews`
Tracks evaluation rounds for shortlisted applicants.
```sql
CREATE TABLE interviews (
    interview_id INT AUTO_INCREMENT PRIMARY KEY,
    application_id INT NOT NULL,
    interview_round VARCHAR(50) NOT NULL,
    interview_date DATETIME NOT NULL,
    interview_mode VARCHAR(20) NOT NULL DEFAULT 'Online',
    interview_location VARCHAR(255),
    interviewer_notes TEXT,
    interview_result VARCHAR(50) NOT NULL DEFAULT 'Pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_interview_app
        FOREIGN KEY (application_id) REFERENCES applications(application_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT chk_interview_mode
        CHECK (interview_mode IN ('Online', 'Offline')),
    CONSTRAINT chk_interview_result
        CHECK (interview_result IN ('Pending', 'Passed', 'Failed'))
) ENGINE=InnoDB;
```

---

#### H. Table: `placements`
Captures official final placement records.
```sql
CREATE TABLE placements (
    placement_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    job_id INT NOT NULL,
    company_id INT NOT NULL,
    offer_date DATE NOT NULL,
    package_lpa DECIMAL(10, 2) NOT NULL,
    placement_status VARCHAR(50) NOT NULL DEFAULT 'Accepted',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_placement_student
        FOREIGN KEY (student_id) REFERENCES students(student_id)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_placement_job
        FOREIGN KEY (job_id) REFERENCES jobs(job_id)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_placement_company
        FOREIGN KEY (company_id) REFERENCES companies(company_id)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT uq_student_job_placement
        UNIQUE (student_id, job_id),
    CONSTRAINT chk_placement_status
        CHECK (placement_status IN ('Offered', 'Accepted', 'Declined')),
    CONSTRAINT chk_placement_package
        CHECK (package_lpa > 0.00)
) ENGINE=InnoDB;
```
- **Historical Integrity:** `ON DELETE RESTRICT` on Student, Job, and Company guarantees placement records are permanent and never deleted accidentally.

---

#### I. Table: `audit_logs`
Records database trigger and system transaction audit logs.
```sql
CREATE TABLE audit_logs (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    table_name VARCHAR(50) NOT NULL,
    record_id INT NOT NULL,
    action VARCHAR(20) NOT NULL,
    old_values TEXT,
    new_values TEXT,
    changed_by VARCHAR(100) DEFAULT 'SYSTEM',
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;
```

---

### 3. Index Design Strategy & Rationale

| Index Name | Target Table & Columns | Performance Rationale |
| :--- | :--- | :--- |
| `idx_students_dept_grad` | `students(department_id, graduation_year)` | Accelerates administrative filtering by department and graduation batch. |
| `idx_students_cgpa_backlogs` | `students(cgpa, backlogs)` | Enables index range scans for job eligibility checks (`cgpa >= X AND backlogs <= Y`). |
| `idx_jobs_status_deadline` | `jobs(job_status, application_deadline)` | Optimizes active job queries on the student portal homepage. |
| `idx_jobs_company` | `jobs(company_id)` | Accelerates foreign key joins between jobs and recruiters. |
| `idx_applications_student_status` | `applications(student_id, application_status)` | Powers the personal dashboard view of student applications. |
| `idx_applications_job_status` | `applications(job_id, application_status)` | Powers recruitment drive applicant screening by stage. |
| `idx_interviews_date_result` | `interviews(interview_date, interview_result)` | Speeds up calendar schedules and pending interview queries. |
| `idx_placements_company_package` | `placements(company_id, package_lpa)` | Optimizes analytics aggregations for company-wise hiring packages. |
