-- =============================================================================
-- STUDENT PLACEMENT MANAGEMENT SYSTEM (SPMS)
-- Database: student_placement_db
-- Target Engine: MySQL 8.0+
-- Script: schema.sql (DDL - Data Definition Language)
-- =============================================================================

DROP DATABASE IF EXISTS student_placement_db;
CREATE DATABASE student_placement_db
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE student_placement_db;

-- -----------------------------------------------------------------------------
-- 1. TABLE: departments
-- Purpose: Academic departments offering degree programs.
-- -----------------------------------------------------------------------------
CREATE TABLE departments (
    department_id INT AUTO_INCREMENT PRIMARY KEY,
    department_name VARCHAR(100) NOT NULL UNIQUE,
    department_code VARCHAR(20) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- -----------------------------------------------------------------------------
-- 2. TABLE: students
-- Purpose: Profiles of registered students eligible for placements.
-- Integrity: Checks for CGPA (0.0 to 10.0) and Backlogs (>= 0).
-- -----------------------------------------------------------------------------
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

-- -----------------------------------------------------------------------------
-- 3. TABLE: users
-- Purpose: Authentication and Role-Based Access Control (Admin / Student).
-- Passwords stored only as secure cryptographic hashes (Werkzeug / bcrypt).
-- -----------------------------------------------------------------------------
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

-- -----------------------------------------------------------------------------
-- 4. TABLE: companies
-- Purpose: Corporate recruiters participating in campus recruitment drives.
-- -----------------------------------------------------------------------------
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

-- -----------------------------------------------------------------------------
-- 5. TABLE: jobs
-- Purpose: Placement drives / job openings published by companies.
-- -----------------------------------------------------------------------------
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

-- -----------------------------------------------------------------------------
-- 6. TABLE: applications
-- Purpose: Tracks student applications to individual job postings.
-- Integrity: A student can apply at most once per job (UNIQUE student_id, job_id).
-- -----------------------------------------------------------------------------
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

-- -----------------------------------------------------------------------------
-- 7. TABLE: interviews
-- Purpose: Scheduled interview rounds for shortlisted applications.
-- -----------------------------------------------------------------------------
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

-- -----------------------------------------------------------------------------
-- 8. TABLE: placements
-- Purpose: Final job placement offer records.
-- Integrity: Enforces referential integrity with student, job, and company.
-- Protects placement history from accidental cascade deletions (ON DELETE RESTRICT).
-- -----------------------------------------------------------------------------
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

-- -----------------------------------------------------------------------------
-- 9. TABLE: audit_logs
-- Purpose: Database trigger audit trail recording critical changes to 
-- applications and placements for compliance and debugging.
-- -----------------------------------------------------------------------------
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
