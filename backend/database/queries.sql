-- =============================================================================
-- STUDENT PLACEMENT MANAGEMENT SYSTEM (SPMS)
-- Database: student_placement_db
-- Target Engine: MySQL 8.0+
-- Script: queries.sql (DBMS Lab Demonstrations - 30 Practical Queries)
-- =============================================================================

USE student_placement_db;

-- =============================================================================
-- CATEGORY 1: BASIC RETRIEVAL, FILTERING, SORTING & ARITHMETIC
-- =============================================================================

-- Query 1: Retrieve all active open jobs with CTC >= 10 LPA sorted by salary descending
-- Purpose: Demonstrates SELECT, WHERE, ORDER BY, and numerical filtering.
SELECT 
    j.job_id,
    c.company_name,
    j.job_title,
    j.salary_lpa,
    j.location,
    j.application_deadline
FROM jobs j
JOIN companies c ON j.company_id = c.company_id
WHERE j.job_status = 'Open' 
  AND j.salary_lpa >= 10.00
ORDER BY j.salary_lpa DESC;

-- Query 2: Retrieve students from 2025 batch with high academic standing (CGPA >= 8.5) and 0 backlogs
-- Purpose: Multi-condition filtering on academic integrity fields.
SELECT 
    roll_number,
    CONCAT(first_name, ' ', last_name) AS full_name,
    email,
    cgpa,
    backlogs,
    graduation_year
FROM students
WHERE graduation_year = 2025 
  AND cgpa >= 8.50 
  AND backlogs = 0
ORDER BY cgpa DESC;

-- Query 3: Search companies in technology and cloud sectors using LIKE wildcard pattern matching
-- Purpose: Pattern matching on textual attributes.
SELECT 
    company_id,
    company_name,
    industry,
    website,
    contact_email
FROM companies
WHERE industry LIKE '%Technology%' 
   OR industry LIKE '%Cloud%'
ORDER BY company_name ASC;

-- =============================================================================
-- CATEGORY 2: RELATIONAL JOINS (INNER, LEFT, MULTI-WAY)
-- =============================================================================

-- Query 4: 4-Table INNER JOIN connecting Placements, Students, Departments, and Companies
-- Purpose: Demonstrates complex relational joining across 4 entities.
SELECT 
    p.placement_id,
    s.roll_number,
    CONCAT(s.first_name, ' ', s.last_name) AS student_name,
    d.department_code,
    c.company_name,
    j.job_title,
    p.package_lpa,
    p.offer_date
FROM placements p
INNER JOIN students s ON p.student_id = s.student_id
INNER JOIN departments d ON s.department_id = d.department_id
INNER JOIN jobs j ON p.job_id = j.job_id
INNER JOIN companies c ON p.company_id = c.company_id
ORDER BY p.package_lpa DESC;

-- Query 5: LEFT OUTER JOIN to list all students along with their placement offers (including unplaced)
-- Purpose: Demonstrates LEFT JOIN preserving unmatched left-table records.
SELECT 
    s.roll_number,
    CONCAT(s.first_name, ' ', s.last_name) AS student_name,
    d.department_code,
    s.cgpa,
    COALESCE(c.company_name, 'Not Placed Yet') AS placed_company,
    COALESCE(CAST(p.package_lpa AS CHAR), 'N/A') AS package_lpa
FROM students s
INNER JOIN departments d ON s.department_id = d.department_id
LEFT JOIN placements p ON s.student_id = p.student_id
LEFT JOIN companies c ON p.company_id = c.company_id
ORDER BY s.roll_number ASC;

-- Query 6: Complete Application Tracking View with Interview Status
-- Purpose: Multi-table join showing student progress in the recruitment pipeline.
SELECT 
    a.application_id,
    s.roll_number,
    CONCAT(s.first_name, ' ', s.last_name) AS student_name,
    c.company_name,
    j.job_title,
    a.application_status,
    i.interview_round,
    i.interview_date,
    i.interview_result
FROM applications a
INNER JOIN students s ON a.student_id = s.student_id
INNER JOIN jobs j ON a.job_id = j.job_id
INNER JOIN companies c ON j.company_id = c.company_id
LEFT JOIN interviews i ON a.application_id = i.application_id
ORDER BY a.application_date DESC;

-- =============================================================================
-- CATEGORY 3: AGGREGATE FUNCTIONS, GROUP BY & HAVING
-- =============================================================================

-- Query 7: Placement metrics grouped by Department (Total placed, Max, Min, Avg package)
-- Purpose: Demonstrates COUNT, AVG, MAX, MIN, and GROUP BY.
SELECT 
    d.department_name,
    d.department_code,
    COUNT(p.placement_id) AS total_placed_students,
    ROUND(AVG(p.package_lpa), 2) AS average_package_lpa,
    MAX(p.package_lpa) AS highest_package_lpa,
    MIN(p.package_lpa) AS lowest_package_lpa
FROM departments d
INNER JOIN students s ON d.department_id = s.department_id
INNER JOIN placements p ON s.student_id = p.student_id
GROUP BY d.department_id, d.department_name, d.department_code
ORDER BY total_placed_students DESC, average_package_lpa DESC;

-- Query 8: Application count per job with HAVING clause filtering high-demand jobs
-- Purpose: Demonstrates GROUP BY with HAVING filter on aggregated metric.
SELECT 
    j.job_id,
    c.company_name,
    j.job_title,
    j.salary_lpa,
    COUNT(a.application_id) AS total_applications
FROM jobs j
JOIN companies c ON j.company_id = c.company_id
LEFT JOIN applications a ON j.job_id = a.job_id
GROUP BY j.job_id, c.company_name, j.job_title, j.salary_lpa
HAVING total_applications >= 3
ORDER BY total_applications DESC;

-- Query 9: Overall Campus Placement Key Performance Indicators (KPIs)
-- Purpose: Single-row aggregate summary for institutional dashboards.
SELECT 
    (SELECT COUNT(*) FROM students) AS total_registered_students,
    (SELECT COUNT(*) FROM companies) AS total_recruiting_companies,
    (SELECT COUNT(*) FROM jobs WHERE job_status = 'Open') AS active_job_drives,
    (SELECT COUNT(*) FROM applications) AS total_applications_submitted,
    COUNT(DISTINCT p.student_id) AS total_placed_students,
    ROUND((COUNT(DISTINCT p.student_id) * 100.0) / (SELECT COUNT(*) FROM students), 2) AS overall_placement_percentage,
    ROUND(AVG(p.package_lpa), 2) AS campus_average_ctc,
    MAX(p.package_lpa) AS campus_highest_ctc
FROM placements p;

-- Query 10: Company-wise recruitment hiring count and total compensation commitment
-- Purpose: Analyzes recruiter volume and financial package commitment.
SELECT 
    c.company_name,
    c.industry,
    COUNT(p.placement_id) AS hires_count,
    ROUND(AVG(p.package_lpa), 2) AS avg_package_offered,
    ROUND(SUM(p.package_lpa), 2) AS total_ctc_offered
FROM companies c
INNER JOIN placements p ON c.company_id = p.company_id
GROUP BY c.company_id, c.company_name, c.industry
ORDER BY hires_count DESC, total_ctc_offered DESC;

-- =============================================================================
-- CATEGORY 4: SUBQUERIES (SCALAR, MULTI-ROW, CORRELATED)
-- =============================================================================

-- Query 11: Scalar Subquery - Find students placed with packages above the campus average
-- Purpose: Demonstrates scalar subquery comparison in the WHERE clause.
SELECT 
    s.roll_number,
    CONCAT(s.first_name, ' ', s.last_name) AS student_name,
    c.company_name,
    p.package_lpa
FROM placements p
JOIN students s ON p.student_id = s.student_id
JOIN companies c ON p.company_id = c.company_id
WHERE p.package_lpa > (SELECT AVG(package_lpa) FROM placements)
ORDER BY p.package_lpa DESC;

-- Query 12: Correlated Subquery - Students whose CGPA is strictly greater than their own Department's average CGPA
-- Purpose: Demonstrates row-by-row correlated subquery evaluation.
SELECT 
    s.roll_number,
    CONCAT(s.first_name, ' ', s.last_name) AS student_name,
    d.department_code,
    s.cgpa,
    (
        SELECT ROUND(AVG(s2.cgpa), 2) 
        FROM students s2 
        WHERE s2.department_id = s.department_id
    ) AS dept_average_cgpa
FROM students s
JOIN departments d ON s.department_id = d.department_id
WHERE s.cgpa > (
    SELECT AVG(s_sub.cgpa)
    FROM students s_sub
    WHERE s_sub.department_id = s.department_id
)
ORDER BY d.department_code, s.cgpa DESC;

-- Query 13: Multi-Row Subquery with IN - Find companies that have posted jobs offering >= 20 LPA
-- Purpose: Demonstrates IN clause evaluated against a nested result set.
SELECT 
    company_id,
    company_name,
    industry,
    contact_email
FROM companies
WHERE company_id IN (
    SELECT DISTINCT company_id 
    FROM jobs 
    WHERE salary_lpa >= 20.00
);

-- Query 14: Subquery in FROM clause (Derived Table) - Department-wise CGPA Distribution
-- Purpose: Demonstrates querying from an aliased inline subquery.
SELECT 
    dept_stats.department_code,
    dept_stats.student_count,
    dept_stats.avg_cgpa,
    dept_stats.max_cgpa
FROM (
    SELECT 
        d.department_code,
        COUNT(s.student_id) AS student_count,
        ROUND(AVG(s.cgpa), 2) AS avg_cgpa,
        MAX(s.cgpa) AS max_cgpa
    FROM departments d
    LEFT JOIN students s ON d.department_id = s.department_id
    GROUP BY d.department_id, d.department_code
) AS dept_stats
WHERE dept_stats.student_count > 0
ORDER BY dept_stats.avg_cgpa DESC;

-- =============================================================================
-- CATEGORY 5: EXISTS & NOT EXISTS CLAUSES
-- =============================================================================

-- Query 15: NOT EXISTS - Unplaced Students who have applied to at least one job
-- Purpose: Demonstrates NOT EXISTS to isolate active unplaced job-seekers.
SELECT 
    s.student_id,
    s.roll_number,
    CONCAT(s.first_name, ' ', s.last_name) AS student_name,
    d.department_code,
    s.cgpa
FROM students s
JOIN departments d ON s.department_id = d.department_id
WHERE EXISTS (
    SELECT 1 FROM applications a WHERE a.student_id = s.student_id
)
AND NOT EXISTS (
    SELECT 1 FROM placements p WHERE p.student_id = s.student_id
)
ORDER BY s.cgpa DESC;

-- Query 16: NOT EXISTS - Students who have NEVER applied to any job posting
-- Purpose: Isolates passive students requiring placement counseling.
SELECT 
    s.student_id,
    s.roll_number,
    CONCAT(s.first_name, ' ', s.last_name) AS student_name,
    s.email,
    s.phone,
    d.department_code
FROM students s
JOIN departments d ON s.department_id = d.department_id
WHERE NOT EXISTS (
    SELECT 1 FROM applications a WHERE a.student_id = s.student_id
);

-- Query 17: NOT EXISTS - Companies that have registered but posted NO job drives
-- Purpose: Quality control check for inactive corporate profiles.
SELECT 
    c.company_id,
    c.company_name,
    c.industry,
    c.contact_email
FROM companies c
WHERE NOT EXISTS (
    SELECT 1 FROM jobs j WHERE j.company_id = c.company_id
);

-- =============================================================================
-- CATEGORY 6: CONDITIONAL LOGIC WITH CASE EXPRESSIONS
-- =============================================================================

-- Query 18: Placement Tier Categorization (Super Dream, Dream, Regular) using CASE
-- Purpose: Demonstrates CASE WHEN ... THEN ... ELSE END classification.
SELECT 
    s.roll_number,
    CONCAT(s.first_name, ' ', s.last_name) AS student_name,
    c.company_name,
    p.package_lpa,
    CASE 
        WHEN p.package_lpa >= 20.00 THEN 'Super Dream Offer (>= 20 LPA)'
        WHEN p.package_lpa >= 10.00 THEN 'Dream Offer (10 - 19.9 LPA)'
        ELSE 'Regular Offer (< 10 LPA)'
    END AS placement_tier
FROM placements p
JOIN students s ON p.student_id = s.student_id
JOIN companies c ON p.company_id = c.company_id
ORDER BY p.package_lpa DESC;

-- Query 19: Application Status Health Categorization
-- Purpose: Evaluates recruitment funnel stages dynamically.
SELECT 
    a.application_id,
    s.roll_number,
    j.job_title,
    a.application_status,
    CASE 
        WHEN a.application_status = 'Selected' THEN 'Success - Offer Extended'
        WHEN a.application_status IN ('Shortlisted', 'Interview Scheduled') THEN 'In Progress - Active Evaluation'
        WHEN a.application_status = 'Applied' THEN 'Submitted - Pending Screening'
        ELSE 'Closed / Inactive'
    END AS pipeline_status
FROM applications a
JOIN students s ON a.student_id = s.student_id
JOIN jobs j ON a.job_id = j.job_id
ORDER BY a.application_id ASC;

-- =============================================================================
-- CATEGORY 7: BUSINESS ELIGIBILITY CHECKS & VALIDATION
-- =============================================================================

-- Query 20: Determine All Students Eligible for Google Campus Drive (Job ID = 1)
-- Criteria: CGPA >= job.minimum_cgpa AND backlogs <= job.maximum_backlogs
-- Purpose: Core placement business logic: eligibility filtering.
SELECT 
    s.student_id,
    s.roll_number,
    CONCAT(s.first_name, ' ', s.last_name) AS student_name,
    d.department_code,
    s.cgpa,
    s.backlogs,
    j.job_title,
    j.minimum_cgpa AS required_cgpa,
    j.maximum_backlogs AS allowed_backlogs
FROM students s
CROSS JOIN jobs j
JOIN departments d ON s.department_id = d.department_id
WHERE j.job_id = 1
  AND s.cgpa >= j.minimum_cgpa
  AND s.backlogs <= j.maximum_backlogs
ORDER BY s.cgpa DESC;

-- Query 21: Eligible Students who have NOT YET applied for Microsoft SDE (Job ID = 2)
-- Purpose: Targets proactive email notifications to eligible non-applicants.
SELECT 
    s.roll_number,
    CONCAT(s.first_name, ' ', s.last_name) AS student_name,
    s.email,
    s.cgpa
FROM students s
WHERE s.cgpa >= (SELECT minimum_cgpa FROM jobs WHERE job_id = 2)
  AND s.backlogs <= (SELECT maximum_backlogs FROM jobs WHERE job_id = 2)
  AND s.student_id NOT IN (
      SELECT student_id FROM applications WHERE job_id = 2
  )
ORDER BY s.cgpa DESC;

-- Query 22: Department-wise Placement Rate (Percentage of Placed Students)
-- Purpose: Academic Accreditation and NIRF Ranking KPI Query.
SELECT 
    d.department_code,
    d.department_name,
    COUNT(s.student_id) AS total_students,
    COUNT(p.placement_id) AS placed_students,
    ROUND(COALESCE(COUNT(p.placement_id) * 100.0 / NULLIF(COUNT(s.student_id), 0), 0), 2) AS placement_percentage
FROM departments d
LEFT JOIN students s ON d.department_id = s.department_id
LEFT JOIN placements p ON s.student_id = p.student_id
GROUP BY d.department_id, d.department_code, d.department_name
ORDER BY placement_percentage DESC;

-- Query 23: Application Funnel Conversion Analysis
-- Purpose: Aggregates conversion from application to selection.
SELECT 
    COUNT(*) AS total_applications,
    SUM(CASE WHEN application_status = 'Applied' THEN 1 ELSE 0 END) AS status_applied,
    SUM(CASE WHEN application_status = 'Shortlisted' THEN 1 ELSE 0 END) AS status_shortlisted,
    SUM(CASE WHEN application_status = 'Interview Scheduled' THEN 1 ELSE 0 END) AS status_interviews,
    SUM(CASE WHEN application_status = 'Selected' THEN 1 ELSE 0 END) AS status_selected,
    SUM(CASE WHEN application_status = 'Rejected' THEN 1 ELSE 0 END) AS status_rejected,
    ROUND(SUM(CASE WHEN application_status = 'Selected' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS selection_rate_pct
FROM applications;

-- =============================================================================
-- CATEGORY 8: DML DEMONSTRATIONS (SAFE INSERT, UPDATE, DELETE & TRANSACTIONS)
-- =============================================================================

-- Query 24: Parameterized INSERT of a new job drive
-- Purpose: Safe DML demonstration.
INSERT INTO jobs (
    company_id, job_title, job_description, job_type, 
    location, minimum_cgpa, maximum_backlogs, salary_lpa, 
    application_deadline, job_status
) VALUES (
    1, 'Security Engineer Trainee', 'Vulnerability assessment and cryptographic protocol analysis.',
    'Full-Time', 'Bangalore', 8.00, 0, 24.00, '2026-12-31', 'Open'
);

-- Query 25: Conditional UPDATE of application status upon interview outcome
-- Purpose: Updates status from 'Interview Scheduled' to 'Selected' safely.
UPDATE applications 
SET application_status = 'Selected'
WHERE application_id = 7 
  AND application_status = 'Interview Scheduled';

-- Query 26: Safe DELETE of a temporary test application
-- Purpose: Safe deletion demonstration with restricted WHERE scope.
DELETE FROM applications
WHERE application_id = 999; -- Safe dummy ID preventing disruption of sample data

-- Query 27: Top 3 Highest Paying Companies on Campus
-- Purpose: Ranking query utilizing ORDER BY and LIMIT.
SELECT 
    c.company_name,
    MAX(j.salary_lpa) AS max_offered_salary_lpa,
    c.website
FROM companies c
JOIN jobs j ON c.company_id = j.company_id
GROUP BY c.company_id, c.company_name, c.website
ORDER BY max_offered_salary_lpa DESC
LIMIT 3;

-- Query 28: Interview Schedule Report for Upcoming 14 Days
-- Purpose: Real-time schedule coordination for placement coordinators.
SELECT 
    i.interview_id,
    s.roll_number,
    CONCAT(s.first_name, ' ', s.last_name) AS candidate_name,
    c.company_name,
    j.job_title,
    i.interview_round,
    i.interview_date,
    i.interview_mode,
    i.interview_location
FROM interviews i
JOIN applications a ON i.application_id = a.application_id
JOIN students s ON a.student_id = s.student_id
JOIN jobs j ON a.job_id = j.job_id
JOIN companies c ON j.company_id = c.company_id
WHERE i.interview_result = 'Pending'
ORDER BY i.interview_date ASC;

-- Query 29: Students with Multiple Job Applications
-- Purpose: Detects active applicants balancing multiple recruitments.
SELECT 
    s.roll_number,
    CONCAT(s.first_name, ' ', s.last_name) AS student_name,
    COUNT(a.application_id) AS applications_count
FROM students s
JOIN applications a ON s.student_id = a.student_id
GROUP BY s.student_id, s.roll_number, s.first_name, s.last_name
HAVING applications_count > 1
ORDER BY applications_count DESC;

-- Query 30: Complete Audit Log Trail for Compliance Review
-- Purpose: Inspects chronological audit entries generated by database triggers.
SELECT 
    log_id,
    table_name,
    record_id,
    action,
    old_values,
    new_values,
    changed_by,
    changed_at
FROM audit_logs
ORDER BY changed_at DESC
LIMIT 50;
