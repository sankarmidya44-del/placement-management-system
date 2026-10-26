-- =============================================================================
-- STUDENT PLACEMENT MANAGEMENT SYSTEM (SPMS)
-- Database: student_placement_db
-- Target Engine: MySQL 8.0+
-- Script: procedures.sql (Stored Procedures for Encapsulated Business Logic)
-- =============================================================================

USE student_placement_db;

DELIMITER $$

-- -----------------------------------------------------------------------------
-- 1. PROCEDURE: sp_get_student_application_history
-- Purpose: Retrieves complete chronological application timeline for a given student.
-- Parameters:
--   p_student_id (INT): ID of the student.
-- -----------------------------------------------------------------------------
DROP PROCEDURE IF EXISTS sp_get_student_application_history$$
CREATE PROCEDURE sp_get_student_application_history(IN p_student_id INT)
BEGIN
    SELECT 
        a.application_id,
        j.job_id,
        c.company_name,
        j.job_title,
        j.location,
        j.salary_lpa,
        a.application_date,
        a.application_status,
        i.interview_round,
        i.interview_date,
        i.interview_result,
        p.placement_id,
        p.package_lpa AS offered_package_lpa,
        p.placement_status
    FROM applications a
    INNER JOIN jobs j ON a.job_id = j.job_id
    INNER JOIN companies c ON j.company_id = c.company_id
    LEFT JOIN interviews i ON a.application_id = i.application_id
    LEFT JOIN placements p ON a.student_id = p.student_id AND a.job_id = p.job_id
    WHERE a.student_id = p_student_id
    ORDER BY a.application_date DESC;
END$$

-- -----------------------------------------------------------------------------
-- 2. PROCEDURE: sp_company_recruitment_summary
-- Purpose: Generates recruitment statistics for a specific company or all companies.
-- Parameters:
--   p_company_id (INT, NULL allowed): Optional company filter.
-- -----------------------------------------------------------------------------
DROP PROCEDURE IF EXISTS sp_company_recruitment_summary$$
CREATE PROCEDURE sp_company_recruitment_summary(IN p_company_id INT)
BEGIN
    SELECT 
        c.company_id,
        c.company_name,
        c.industry,
        COUNT(DISTINCT j.job_id) AS total_jobs_posted,
        COUNT(DISTINCT a.application_id) AS total_applicants,
        COUNT(DISTINCT p.placement_id) AS total_hires,
        ROUND(COALESCE(AVG(p.package_lpa), 0), 2) AS avg_package_lpa,
        ROUND(COALESCE(MAX(p.package_lpa), 0), 2) AS max_package_lpa
    FROM companies c
    LEFT JOIN jobs j ON c.company_id = j.company_id
    LEFT JOIN applications a ON j.job_id = a.job_id
    LEFT JOIN placements p ON c.company_id = p.company_id
    WHERE (p_company_id IS NULL OR c.company_id = p_company_id)
    GROUP BY c.company_id, c.company_name, c.industry
    ORDER BY total_hires DESC, avg_package_lpa DESC;
END$$

-- -----------------------------------------------------------------------------
-- 3. PROCEDURE: sp_get_eligible_students_for_job
-- Purpose: Finds all students meeting the academic eligibility criteria of a job.
-- Parameters:
--   p_job_id (INT): Target job ID.
-- -----------------------------------------------------------------------------
DROP PROCEDURE IF EXISTS sp_get_eligible_students_for_job$$
CREATE PROCEDURE sp_get_eligible_students_for_job(IN p_job_id INT)
BEGIN
    DECLARE v_min_cgpa DECIMAL(4, 2);
    DECLARE v_max_backlogs INT;
    
    -- Retrieve job eligibility criteria
    SELECT minimum_cgpa, maximum_backlogs 
    INTO v_min_cgpa, v_max_backlogs
    FROM jobs 
    WHERE job_id = p_job_id;
    
    -- Return eligible candidates with their current application status if applied
    SELECT 
        s.student_id,
        s.roll_number,
        CONCAT(s.first_name, ' ', s.last_name) AS student_name,
        d.department_code,
        s.cgpa,
        s.backlogs,
        s.email,
        CASE 
            WHEN a.application_id IS NOT NULL THEN 'Already Applied'
            ELSE 'Eligible - Not Applied'
        END AS application_status
    FROM students s
    INNER JOIN departments d ON s.department_id = d.department_id
    LEFT JOIN applications a ON s.student_id = a.student_id AND a.job_id = p_job_id
    WHERE s.cgpa >= v_min_cgpa 
      AND s.backlogs <= v_max_backlogs
    ORDER BY s.cgpa DESC;
END$$

-- -----------------------------------------------------------------------------
-- 4. PROCEDURE: sp_process_student_selection
-- Purpose: Transactional stored procedure demonstrating ACID execution in MySQL.
-- Atomically selects an applicant and creates their placement offer record.
-- -----------------------------------------------------------------------------
DROP PROCEDURE IF EXISTS sp_process_student_selection$$
CREATE PROCEDURE sp_process_student_selection(
    IN p_application_id INT,
    IN p_offer_date DATE,
    IN p_package_lpa DECIMAL(10, 2),
    OUT p_result_message VARCHAR(255)
)
proc_block: BEGIN
    DECLARE v_student_id INT;
    DECLARE v_job_id INT;
    DECLARE v_company_id INT;
    DECLARE v_current_status VARCHAR(50);
    DECLARE v_existing_placement_id INT;

    -- Declare error handler for automatic rollback on SQL failure
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        SET p_result_message = 'ERROR: Database transaction failed. All changes rolled back.';
    END;

    -- Start Atomic Transaction
    START TRANSACTION;

    -- 1. Verify application exists and fetch details
    SELECT student_id, job_id, application_status 
    INTO v_student_id, v_job_id, v_current_status
    FROM applications 
    WHERE application_id = p_application_id;

    IF v_student_id IS NULL THEN
        ROLLBACK;
        SET p_result_message = 'ERROR: Application record not found.';
        LEAVE proc_block;
    END IF;

    -- 2. Fetch associated company from jobs
    SELECT company_id INTO v_company_id 
    FROM jobs 
    WHERE job_id = v_job_id;

    -- 3. Check for existing placement record for this student and job
    SELECT placement_id INTO v_existing_placement_id
    FROM placements
    WHERE student_id = v_student_id AND job_id = v_job_id;

    IF v_existing_placement_id IS NOT NULL THEN
        ROLLBACK;
        SET p_result_message = 'ERROR: Placement offer already recorded for this student and job.';
        LEAVE proc_block;
    END IF;

    -- 4. Update application status to 'Selected'
    UPDATE applications 
    SET application_status = 'Selected'
    WHERE application_id = p_application_id;

    -- 5. Insert placement record
    INSERT INTO placements (student_id, job_id, company_id, offer_date, package_lpa, placement_status)
    VALUES (v_student_id, v_job_id, v_company_id, p_offer_date, p_package_lpa, 'Accepted');

    -- Commit transaction if all steps succeed
    COMMIT;
    SET p_result_message = 'SUCCESS: Student successfully selected and placement record generated.';
END$$

DELIMITER ;
