-- =============================================================================
-- STUDENT PLACEMENT MANAGEMENT SYSTEM (SPMS)
-- Database: student_placement_db
-- Target Engine: MySQL 8.0+
-- Script: indexes.sql (Database Indexes for Query Performance Optimization)
-- =============================================================================

USE student_placement_db;

-- -----------------------------------------------------------------------------
-- 1. INDEX: idx_students_dept_grad
-- Target: students (department_id, graduation_year)
-- Rationale:
--   The student management module frequently filters students by department
--   and graduation cohort (e.g. "Show 2025 CSE students").
--   A composite B-Tree index on (department_id, graduation_year) allows index
--   range scans instead of full table scans during filtering and grouping.
-- -----------------------------------------------------------------------------
CREATE INDEX idx_students_dept_grad 
ON students (department_id, graduation_year);

-- -----------------------------------------------------------------------------
-- 2. INDEX: idx_students_cgpa_backlogs
-- Target: students (cgpa, backlogs)
-- Rationale:
--   Eligibility checking is one of the most frequent operations in SPMS:
--   WHERE cgpa >= :min_cgpa AND backlogs <= :max_backlogs.
--   Indexing both numeric criteria allows MySQL to quickly identify eligible
--   candidates for any job drive without scanning the entire student table.
-- -----------------------------------------------------------------------------
CREATE INDEX idx_students_cgpa_backlogs 
ON students (cgpa, backlogs);

-- -----------------------------------------------------------------------------
-- 3. INDEX: idx_jobs_status_deadline
-- Target: jobs (job_status, application_deadline)
-- Rationale:
--   The student homepage loads active job postings with:
--   WHERE job_status = 'Open' AND application_deadline >= CURRENT_DATE().
--   This composite index filters out closed or past-deadline jobs in logarithmic
--   O(log N) time.
-- -----------------------------------------------------------------------------
CREATE INDEX idx_jobs_status_deadline 
ON jobs (job_status, application_deadline);

-- -----------------------------------------------------------------------------
-- 4. INDEX: idx_jobs_company
-- Target: jobs (company_id)
-- Rationale:
--   Accelerates JOIN operations between companies and jobs, as well as foreign
--   key constraint verification during INSERT and UPDATE operations.
-- -----------------------------------------------------------------------------
CREATE INDEX idx_jobs_company 
ON jobs (company_id);

-- -----------------------------------------------------------------------------
-- 5. INDEX: idx_applications_student_status
-- Target: applications (student_id, application_status)
-- Rationale:
--   When a student logs in, the portal fetches their specific application
--   history and status badges: WHERE student_id = :id.
--   The composite index allows index-only lookups for quick dashboard rendering.
-- -----------------------------------------------------------------------------
CREATE INDEX idx_applications_student_status 
ON applications (student_id, application_status);

-- -----------------------------------------------------------------------------
-- 6. INDEX: idx_applications_job_status
-- Target: applications (job_id, application_status)
-- Rationale:
--   Placement coordinators view applicants for a specific job grouped by stage:
--   WHERE job_id = :id AND application_status = 'Shortlisted'.
--   This index optimizes pipeline status filtering for large applicant pools.
-- -----------------------------------------------------------------------------
CREATE INDEX idx_applications_job_status 
ON applications (job_id, application_status);

-- -----------------------------------------------------------------------------
-- 7. INDEX: idx_interviews_date_result
-- Target: interviews (interview_date, interview_result)
-- Rationale:
--   Speeds up interview schedule calendars and upcoming rounds query:
--   WHERE interview_date >= NOW() AND interview_result = 'Pending'.
-- -----------------------------------------------------------------------------
CREATE INDEX idx_interviews_date_result 
ON interviews (interview_date, interview_result);

-- -----------------------------------------------------------------------------
-- 8. INDEX: idx_placements_company_package
-- Target: placements (company_id, package_lpa)
-- Rationale:
--   Speeds up recruiter analytics queries calculating MAX(package_lpa) and
--   AVG(package_lpa) per company for dashboard charts and institutional reports.
-- -----------------------------------------------------------------------------
CREATE INDEX idx_placements_company_package 
ON placements (company_id, package_lpa);
