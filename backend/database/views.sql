-- =============================================================================
-- STUDENT PLACEMENT MANAGEMENT SYSTEM (SPMS)
-- Database: student_placement_db
-- Target Engine: MySQL 8.0+
-- Script: views.sql (Database Views for Abstraction, Reporting & Security)
-- =============================================================================

USE student_placement_db;

-- -----------------------------------------------------------------------------
-- 1. VIEW: view_active_job_postings
-- Purpose: Provides a consolidated view of all open job postings with company
-- details and live application counts, filtering out expired or closed jobs.
-- -----------------------------------------------------------------------------
DROP VIEW IF EXISTS view_active_job_postings;
CREATE VIEW view_active_job_postings AS
SELECT 
    j.job_id,
    c.company_id,
    c.company_name,
    c.industry,
    j.job_title,
    j.job_type,
    j.location,
    j.minimum_cgpa,
    j.maximum_backlogs,
    j.salary_lpa,
    j.application_deadline,
    j.created_at,
    COUNT(a.application_id) AS total_applicants
FROM jobs j
INNER JOIN companies c ON j.company_id = c.company_id
LEFT JOIN applications a ON j.job_id = a.job_id
WHERE j.job_status = 'Open' 
  AND j.application_deadline >= CURRENT_DATE()
GROUP BY 
    j.job_id, c.company_id, c.company_name, c.industry,
    j.job_title, j.job_type, j.location, j.minimum_cgpa,
    j.maximum_backlogs, j.salary_lpa, j.application_deadline, j.created_at;

-- -----------------------------------------------------------------------------
-- 2. VIEW: view_student_application_summary
-- Purpose: Summarizes application progression for every student, showing counts
-- of applications in various stages and final placement status.
-- -----------------------------------------------------------------------------
DROP VIEW IF EXISTS view_student_application_summary;
CREATE VIEW view_student_application_summary AS
SELECT 
    s.student_id,
    s.roll_number,
    CONCAT(s.first_name, ' ', s.last_name) AS student_name,
    d.department_code,
    s.cgpa,
    s.backlogs,
    COUNT(a.application_id) AS total_applied,
    SUM(CASE WHEN a.application_status = 'Shortlisted' THEN 1 ELSE 0 END) AS count_shortlisted,
    SUM(CASE WHEN a.application_status = 'Interview Scheduled' THEN 1 ELSE 0 END) AS count_interviews,
    SUM(CASE WHEN a.application_status = 'Selected' THEN 1 ELSE 0 END) AS count_selected,
    SUM(CASE WHEN a.application_status = 'Rejected' THEN 1 ELSE 0 END) AS count_rejected,
    CASE 
        WHEN p.placement_id IS NOT NULL THEN 'Placed'
        ELSE 'Unplaced'
    END AS current_placement_status,
    p.package_lpa AS placed_package_lpa
FROM students s
INNER JOIN departments d ON s.department_id = d.department_id
LEFT JOIN applications a ON s.student_id = a.student_id
LEFT JOIN placements p ON s.student_id = p.student_id
GROUP BY 
    s.student_id, s.roll_number, s.first_name, s.last_name,
    d.department_code, s.cgpa, s.backlogs, p.placement_id, p.package_lpa;

-- -----------------------------------------------------------------------------
-- 3. VIEW: view_company_recruitment_summary
-- Purpose: Aggregates recruitment outcomes per company: number of postings,
-- applicant volume, offers made, and average package provided.
-- -----------------------------------------------------------------------------
DROP VIEW IF EXISTS view_company_recruitment_summary;
CREATE VIEW view_company_recruitment_summary AS
SELECT 
    c.company_id,
    c.company_name,
    c.industry,
    c.contact_email,
    COUNT(DISTINCT j.job_id) AS total_jobs_posted,
    COUNT(DISTINCT a.application_id) AS total_applications_received,
    COUNT(DISTINCT p.placement_id) AS total_students_placed,
    ROUND(COALESCE(AVG(p.package_lpa), 0), 2) AS average_package_offered_lpa,
    ROUND(COALESCE(MAX(p.package_lpa), 0), 2) AS highest_package_offered_lpa
FROM companies c
LEFT JOIN jobs j ON c.company_id = j.company_id
LEFT JOIN applications a ON j.job_id = a.job_id
LEFT JOIN placements p ON c.company_id = p.company_id
GROUP BY c.company_id, c.company_name, c.industry, c.contact_email;

-- -----------------------------------------------------------------------------
-- 4. VIEW: view_department_placement_summary
-- Purpose: Department-level KPIs including placement percentage, average salary,
-- and total offers for accreditation and administrative reporting.
-- -----------------------------------------------------------------------------
DROP VIEW IF EXISTS view_department_placement_summary;
CREATE VIEW view_department_placement_summary AS
SELECT 
    d.department_id,
    d.department_name,
    d.department_code,
    COUNT(DISTINCT s.student_id) AS total_registered_students,
    COUNT(DISTINCT p.student_id) AS total_placed_students,
    (COUNT(DISTINCT s.student_id) - COUNT(DISTINCT p.student_id)) AS total_unplaced_students,
    ROUND(
        COALESCE(
            (COUNT(DISTINCT p.student_id) * 100.0) / NULLIF(COUNT(DISTINCT s.student_id), 0), 
            0.00
        ), 2
    ) AS placement_percentage,
    ROUND(COALESCE(AVG(p.package_lpa), 0), 2) AS average_package_lpa,
    ROUND(COALESCE(MAX(p.package_lpa), 0), 2) AS highest_package_lpa
FROM departments d
LEFT JOIN students s ON d.department_id = s.department_id
LEFT JOIN placements p ON s.student_id = p.student_id
GROUP BY d.department_id, d.department_name, d.department_code;

-- -----------------------------------------------------------------------------
-- 5. VIEW: view_unplaced_students
-- Purpose: Identifies students who have not yet secured an offer, enabling
-- the placement cell to schedule remedial training and special recruitment drives.
-- -----------------------------------------------------------------------------
DROP VIEW IF EXISTS view_unplaced_students;
CREATE VIEW view_unplaced_students AS
SELECT 
    s.student_id,
    s.roll_number,
    CONCAT(s.first_name, ' ', s.last_name) AS student_name,
    s.email,
    s.phone,
    d.department_name,
    d.department_code,
    s.graduation_year,
    s.cgpa,
    s.backlogs,
    COUNT(a.application_id) AS total_applications_submitted
FROM students s
INNER JOIN departments d ON s.department_id = d.department_id
LEFT JOIN applications a ON s.student_id = a.student_id
WHERE s.student_id NOT IN (
    SELECT student_id FROM placements
)
GROUP BY 
    s.student_id, s.roll_number, s.first_name, s.last_name,
    s.email, s.phone, d.department_name, d.department_code,
    s.graduation_year, s.cgpa, s.backlogs;
