-- =============================================================================
-- STUDENT PLACEMENT MANAGEMENT SYSTEM (SPMS)
-- Database: student_placement_db
-- Target Engine: MySQL 8.0+
-- Script: triggers.sql (Database Triggers for Auditing and Deep Data Integrity)
-- =============================================================================

USE student_placement_db;

DELIMITER $$

-- -----------------------------------------------------------------------------
-- 1. TRIGGER: trg_audit_application_status_update
-- Purpose: Automatically creates an audit trail whenever an application's
-- status transitions (e.g. from 'Shortlisted' to 'Interview Scheduled' or 'Selected').
-- Event: AFTER UPDATE ON applications
-- -----------------------------------------------------------------------------
DROP TRIGGER IF EXISTS trg_audit_application_status_update$$
CREATE TRIGGER trg_audit_application_status_update
AFTER UPDATE ON applications
FOR EACH ROW
BEGIN
    IF OLD.application_status <> NEW.application_status THEN
        INSERT INTO audit_logs (
            table_name,
            record_id,
            action,
            old_values,
            new_values,
            changed_by
        ) VALUES (
            'applications',
            NEW.application_id,
            'STATUS_CHANGE',
            CONCAT('Old Status: ', OLD.application_status),
            CONCAT('New Status: ', NEW.application_status),
            CURRENT_USER()
        );
    END IF;
END$$

-- -----------------------------------------------------------------------------
-- 2. TRIGGER: trg_audit_placement_created
-- Purpose: Automatically audits new placement offer generation.
-- Event: AFTER INSERT ON placements
-- -----------------------------------------------------------------------------
DROP TRIGGER IF EXISTS trg_audit_placement_created$$
CREATE TRIGGER trg_audit_placement_created
AFTER INSERT ON placements
FOR EACH ROW
BEGIN
    INSERT INTO audit_logs (
        table_name,
        record_id,
        action,
        old_values,
        new_values,
        changed_by
    ) VALUES (
        'placements',
        NEW.placement_id,
        'INSERT',
        NULL,
        CONCAT('Student ID: ', NEW.student_id, 
               ' | Job ID: ', NEW.job_id, 
               ' | Company ID: ', NEW.company_id, 
               ' | Package: ', NEW.package_lpa, ' LPA',
               ' | Status: ', NEW.placement_status),
        CURRENT_USER()
    );
END$$

-- -----------------------------------------------------------------------------
-- 3. TRIGGER: trg_audit_placement_deleted
-- Purpose: Records deletion of placement offers to maintain historic compliance.
-- Event: AFTER DELETE ON placements
-- -----------------------------------------------------------------------------
DROP TRIGGER IF EXISTS trg_audit_placement_deleted$$
CREATE TRIGGER trg_audit_placement_deleted
AFTER DELETE ON placements
FOR EACH ROW
BEGIN
    INSERT INTO audit_logs (
        table_name,
        record_id,
        action,
        old_values,
        new_values,
        changed_by
    ) VALUES (
        'placements',
        OLD.placement_id,
        'DELETE',
        CONCAT('Student ID: ', OLD.student_id, 
               ' | Job ID: ', OLD.job_id, 
               ' | Company ID: ', OLD.company_id, 
               ' | Package: ', OLD.package_lpa, ' LPA'),
        NULL,
        CURRENT_USER()
    );
END$$

-- -----------------------------------------------------------------------------
-- 4. TRIGGER: trg_validate_job_active_before_application
-- Purpose: Enforces at the database engine level that no new application can be
-- submitted for a job that is already 'Closed'.
-- Event: BEFORE INSERT ON applications
-- -----------------------------------------------------------------------------
DROP TRIGGER IF EXISTS trg_validate_job_active_before_application$$
CREATE TRIGGER trg_validate_job_active_before_application
BEFORE INSERT ON applications
FOR EACH ROW
BEGIN
    DECLARE v_job_status VARCHAR(20);
    DECLARE v_deadline DATE;

    SELECT job_status, application_deadline 
    INTO v_job_status, v_deadline
    FROM jobs 
    WHERE job_id = NEW.job_id;

    IF v_job_status = 'Closed' THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Integrity Violation: Applications are closed for this job drive.';
    END IF;

    IF v_deadline < CURRENT_DATE() THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Integrity Violation: The deadline for this job posting has expired.';
    END IF;
END$$

DELIMITER ;
