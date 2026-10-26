# Comprehensive Project Report
# STUDENT PLACEMENT MANAGEMENT SYSTEM (SPMS)
**Course:** Database Management Systems (DBMS) Laboratory Project  
**Academic Year:** 2025–2026  
**Technology Stack:** Python 3.14, Flask, Flask-SQLAlchemy, MySQL 8.0, HTML5, CSS3, JavaScript, Bootstrap 5, Chart.js  

---

## 1. Title Page
- **Project Title:** Student Placement Management System (SPMS)
- **Domain:** Higher Education Institution Database & Campus Recruitment Automation
- **System Classification:** Database-Driven Web Application
- **Database Engine:** MySQL 8.0 (InnoDB Engine, utf8mb4) / SQLAlchemy ORM
- **Application Framework:** Flask 3.1 / Python 3.14

---

## 2. Abstract
The Student Placement Management System (SPMS) is a relational database-driven web application designed to automate, streamline, and audit the campus recruitment operations of collegiate placement departments. Traditional manual systems rely on ad-hoc spreadsheets, error-prone email chains, and disconnected records, leading to communication bottlenecks, duplicated student applications, and inaccurate placement statistics. 

SPMS provides a unified, normalized (up to 3NF/BCNF) database architecture that enforces strict data integrity constraints, foreign key referential actions, and automated database triggers. The platform delivers role-based access control (RBAC) separating administrative placement officers from student candidates. Key institutional capabilities include automated academic eligibility verification (minimum CGPA and maximum backlogs), multi-stage interview scheduling, atomic ACID transaction processing for final placement offers, and dynamic analytical dashboards powered by Chart.js.

---

## 3. Introduction
Campus recruitment is a vital benchmark of higher educational quality and institutional ranking (such as NIRF and NAAC accreditation). Hundreds of corporate recruiters evaluate thousands of student applications across multiple engineering departments. Managing this volume requires high transactional consistency, data confidentiality, and rapid reporting.

SPMS bridges the gap between academic student performance data and corporate recruitment pipelines, offering a centralized relational repository for departments, students, companies, job postings, applications, interview rounds, and confirmed placement records.

---

## 4. Problem Statement
Placement offices frequently encounter critical database and operational challenges:
1. **Data Redundancy and Inconsistency:** Student academic metrics (CGPA, backlogs) are duplicated across departmental rosters and company spreadsheets.
2. **Eligibility Violations:** Ineligible students accidentally apply for high-threshold recruitment drives, placing an administrative screening burden on coordinators.
3. **Double Selection and Policy Violations:** Candidates who have already accepted placement offers may improperly receive multiple offers contrary to institutional single-offer regulations.
4. **Lack of Auditability:** Changes in applicant stages (Shortlisted, Interviewed, Selected, Rejected) are not timestamped or attributed to authorized actors.
5. **Slow Institutional Reporting:** Compiling department-wise placement percentages, average packages, and highest offers requires laborious manual aggregation.

---

## 5. Objectives
- Design and implement a normalized relational schema (**3NF/BCNF**) for `student_placement_db`.
- Enforce domain and integrity constraints (`CHECK`, `UNIQUE`, `NOT NULL`, and `FOREIGN KEY` cascades/restrictions).
- Implement role-based access control (RBAC) ensuring data privacy.
- Develop atomic ACID transactions for multi-step candidate selection and offer generation.
- Implement database views, stored procedures, composite indexes, and triggers in MySQL 8.
- Provide a responsive dashboard with real-time Chart.js visualizations.
- Provide a full automated test suite verifying edge cases, constraints, and rollbacks.

---

## 6. Scope
### In-Scope:
- Student profile management and academic records tracking.
- Recruiter profile cataloging and job posting publication.
- Rule-based academic eligibility verification prior to application acceptance.
- Application pipeline tracking: `Applied` $\rightarrow$ `Shortlisted` $\rightarrow$ `Interview Scheduled` $\rightarrow$ `Selected` / `Rejected` / `Withdrawn`.
- Interview scheduling across technical, coding, and HR rounds.
- Atomic placement offer generation with salary package tracking.
- Institutional NIRF analytics, department-wise stats, and unplaced candidate tracking.
- Database trigger audit logging.

### Out-of-Scope (Future Scope):
- Payment gateway integration for drive fees.
- Video conferencing integration (Google Meet API / Zoom API).
- AI resume parsing and keyword matching.

---

## 7. Existing System vs. Proposed System

| Feature / Dimension | Existing Manual / Spreadsheet System | Proposed SPMS Application |
| :--- | :--- | :--- |
| **Data Storage** | Disconnected Google Sheets & Excel files | Centralized, normalized MySQL 8 database |
| **Integrity Enforcement** | Manual inspection; frequent duplicates | Engine-level `CHECK` and `UNIQUE` constraints |
| **Application Process** | Manual email submission of resumes | In-app self-service submission with instant eligibility validation |
| **Referential Integrity** | Risk of orphaned records upon deletion | Explicit `ON DELETE RESTRICT` on placements and jobs |
| **Audit Trail** | None; unauthorized overwrites untraceable | Automated MySQL triggers and transaction audit log |
| **Analytics & Reporting** | Days of manual Excel formula consolidation | Instant, real-time Chart.js dashboards and NIRF reports |

---

## 8. Hardware and Software Requirements

### Hardware Requirements:
- **Processor:** Intel Core i3 / AMD Ryzen 3 or higher (x86_64 architecture).
- **RAM:** 4 GB minimum (8 GB recommended for MySQL 8 and web browser).
- **Storage:** 500 MB available storage for database tables, logs, and Python environment.
- **Display:** Minimum 1024x768 resolution (Responsive on Mobile, Tablet, Desktop).

### Software Requirements:
- **Operating System:** Microsoft Windows 10/11, macOS, or Linux.
- **Database Engine:** MySQL Server 8.0+ or MySQL Workbench 8.0.
- **Programming Language:** Python 3.10+ (tested on Python 3.14.7).
- **Web Framework:** Flask 3.1.0, Flask-SQLAlchemy 3.1.1, Flask-Login 0.6.3.
- **Database Driver:** PyMySQL 1.1.1 with Cryptography.
- **Frontend Technologies:** HTML5, CSS3, JavaScript (ES6), Bootstrap 5.3, Chart.js 4.4.
- **Testing Framework:** Pytest 8.3.

---

## 9. System Architecture

```
+-------------------------------------------------------------+
|                     Client Web Browser                      |
|          (HTML5, Responsive CSS3, JavaScript, Chart.js)     |
+------------------------------+------------------------------+
                               | HTTP / JSON Requests
                               v
+-------------------------------------------------------------+
|                     Flask Web Application                   |
|  +--------------------+  +-------------------------------+  |
|  | Blueprint Routing  |  | Authentication & RBAC Filters |  |
|  +--------------------+  +-------------------------------+  |
|  +-------------------------------------------------------+  |
|  |           PlacementService Business Logic             |  |
|  |        (ACID Transactions, Eligibility Checks)         |  |
|  +-------------------------------------------------------+  |
|  +-------------------------------------------------------+  |
|  |             SQLAlchemy 2.0 ORM Mappings               |  |
|  +-------------------------------------------------------+  |
+------------------------------+------------------------------+
                               | PyMySQL Driver (TCP/IP Port 3306)
                               v
+-------------------------------------------------------------+
|                     MySQL 8.0 Engine                        |
|  +--------------------+  +-------------------------------+  |
|  |  Normalized Tables |  | Stored Procedures & Triggers  |  |
|  +--------------------+  +-------------------------------+  |
|  |  Composite Indexes |  | Abstracted Views & Audit Logs |  |
|  +--------------------+  +-------------------------------+  |
+-------------------------------------------------------------+
```

---

## 10. Functional & Non-Functional Requirements

### Functional Requirements:
1. **User Authentication & RBAC:** Secure login with password hashing; students restricted to personal dossiers; admins permitted to manage institutional records.
2. **Academic Eligibility Engine:** Dynamically validates that a candidate's CGPA $\ge$ job's minimum CGPA and candidate's backlogs $\le$ job's maximum allowed backlogs.
3. **Application Control:** Prevents duplicate applications via composite unique key `(student_id, job_id)` and blocks submissions to expired or closed jobs.
4. **Interview Progression Tracker:** Multi-round tracking with modes, schedules, and interviewer feedback.
5. **Placement Offer Confirmation:** Atomic transaction linking student, job, and company while generating audit log entries.
6. **Institutional KPI Generation:** Real-time computation of placement percentages, average packages, department-wise breakdowns, and salary tiers.

### Non-Functional Requirements:
1. **Data Integrity & Consistency:** Database tables normalized to 3NF/BCNF; check constraints enforced at the database layer.
2. **Performance:** Critical queries execute in sub-millisecond time via composite B-Tree indexes.
3. **Security:** Passwords salted and hashed with Scrypt/Argon2; parameterized SQL prevents injection attacks; CSRF protection on forms.
4. **Usability:** Modern, accessible UI with responsive layouts and clear status badges.

---

## 11. ER Diagram & Relational Schema
*(Refer to `docs/er_diagram.md` for the complete Mermaid ER diagram and cardinalities.)*

### Relational Schema Representation:
- **`departments`** ($\underline{\text{department\_id}}$, $\text{department\_name}^{\text{UK}}$, $\text{department\_code}^{\text{UK}}$, $\text{created\_at}$)
- **`students`** ($\underline{\text{student\_id}}$, $\text{roll\_number}^{\text{UK}}$, $\text{first\_name}$, $\text{last\_name}$, $\text{email}^{\text{UK}}$, $\text{phone}$, $\text{department\_id}^{\text{FK}}$, $\text{graduation\_year}$, $\text{cgpa}$, $\text{backlogs}$, $\text{resume\_url}$, $\text{created\_at}$)
- **`users`** ($\underline{\text{user\_id}}$, $\text{username}^{\text{UK}}$, $\text{email}^{\text{UK}}$, $\text{password\_hash}$, $\text{role}$, $\text{student\_id}^{\text{FK}}$, $\text{created\_at}$)
- **`companies`** ($\underline{\text{company\_id}}$, $\text{company\_name}$, $\text{industry}$, $\text{website}$, $\text{contact\_email}$, $\text{contact\_phone}$, $\text{company\_description}$, $\text{created\_at}$)
- **`jobs`** ($\underline{\text{job\_id}}$, $\text{company\_id}^{\text{FK}}$, $\text{job\_title}$, $\text{job\_description}$, $\text{job\_type}$, $\text{location}$, $\text{minimum\_cgpa}$, $\text{maximum\_backlogs}$, $\text{salary\_lpa}$, $\text{application\_deadline}$, $\text{job\_status}$, $\text{created\_at}$)
- **`applications`** ($\underline{\text{application\_id}}$, $\text{student\_id}^{\text{FK}}$, $\text{job\_id}^{\text{FK}}$, $\text{application\_date}$, $\text{application\_status}$, $\text{resume\_url}$, $\text{updated\_at}$)  
  *Candidate Key:* $\{\text{student\_id}, \text{job\_id}\}$
- **`interviews`** ($\underline{\text{interview\_id}}$, $\text{application\_id}^{\text{FK}}$, $\text{interview\_round}$, $\text{interview\_date}$, $\text{interview\_mode}$, $\text{interview\_location}$, $\text{interviewer\_notes}$, $\text{interview\_result}$, $\text{created\_at}$)
- **`placements`** ($\underline{\text{placement\_id}}$, $\text{student\_id}^{\text{FK}}$, $\text{job\_id}^{\text{FK}}$, $\text{company\_id}^{\text{FK}}$, $\text{offer\_date}$, $\text{package\_lpa}$, $\text{placement\_status}$, $\text{created\_at}$)  
  *Candidate Key:* $\{\text{student\_id}, \text{job\_id}\}$
- **`audit_logs`** ($\underline{\text{log\_id}}$, $\text{table\_name}$, $\text{record\_id}$, $\text{action}$, $\text{old\_values}$, $\text{new\_values}$, $\text{changed\_by}$, $\text{changed\_at}$)

---

## 12. Database Normalization Analysis
*(Refer to `docs/normalization.md` for mathematical functional dependency proofs.)*

- **1NF:** Ensured atomic scalar domains for all attributes; eliminated repeating interview round groups by decomposing them into the `interviews` table.
- **2NF:** Removed partial functional dependencies in application tracking. Student details (`name`, `cgpa`) and job details (`salary`, `title`) were extracted into `students` and `jobs` respectively.
- **3NF:** Removed transitive functional dependencies (e.g., $\text{student\_id} \rightarrow \text{department\_id} \rightarrow \text{department\_name}$ was normalized by creating `departments`).
- **BCNF:** Every non-trivial functional dependency determinant across all tables is a candidate key / Superkey.

---

## 13. Advanced SQL Concept Demonstrations

### Views Implemented (`database/views.sql`):
1. `view_active_job_postings`: Filters open drives with unexpired deadlines and applicant counts.
2. `view_student_application_summary`: Summarizes applications submitted, shortlisted, interviewed, and placed per student.
3. `view_company_recruitment_summary`: Consolidates recruitment volume, selections, and average salary offered per recruiter.
4. `view_department_placement_summary`: Computes institutional NIRF statistics (registered, placed, placement percentage, average/max CTC).
5. `view_unplaced_students`: Identifies candidates requiring placement assistance.

### Indexes Implemented (`database/indexes.sql`):
- `idx_students_dept_grad`: Optimizes administrative batch filtering.
- `idx_students_cgpa_backlogs`: Accelerates job eligibility filtering.
- `idx_jobs_status_deadline`: Speeds up active job queries on the student portal.
- `idx_applications_student_status`: Enables rapid personal application history retrieval.

### Stored Procedures Implemented (`database/procedures.sql`):
1. `sp_get_student_application_history(IN p_student_id INT)`: Returns complete chronological timeline for a student.
2. `sp_company_recruitment_summary(IN p_company_id INT)`: Calculates recruiter hiring metrics.
3. `sp_get_eligible_students_for_job(IN p_job_id INT)`: Dynamically retrieves candidate pool meeting job thresholds.
4. `sp_process_student_selection(...)`: Executes ACID candidate selection and offer generation in MySQL.

### Database Triggers Implemented (`database/triggers.sql`):
1. `trg_audit_application_status_update`: Logs application status transitions (`Shortlisted` $\rightarrow$ `Selected`) to `audit_logs`.
2. `trg_audit_placement_created`: Logs new placement offers.
3. `trg_audit_placement_deleted`: Preserves compliance trail if offers are rescinded.
4. `trg_validate_job_active_before_application`: Database engine-level trigger rejecting applications to closed or expired jobs.

---

## 14. Transaction Management & ACID Properties

| ACID Property | Implementation Mechanism in SPMS | Project Realization |
| :--- | :--- | :--- |
| **Atomicity** | `START TRANSACTION`, `COMMIT`, `ROLLBACK` in service & procedure | When a student is selected, application status update and placement record creation must both succeed; if salary validation fails, all steps roll back cleanly. |
| **Consistency** | Table constraints (`CHECK`, `FOREIGN KEY`, `UNIQUE`) | Prevents negative backlogs, CGPA $> 10$, duplicate applications, or dangling recruiter references. |
| **Isolation** | InnoDB default REPEATABLE READ isolation level | Concurrent candidate applications do not read uncommitted draft jobs or duplicate placements. |
| **Durability** | Write-Ahead Logging (WAL) and InnoDB Redo Log | Committed placement offers persist permanently on disk even during unexpected server crashes. |

---

## 15. Screenshots Section
*(Insert application screenshots here upon running the local server)*

- **Figure 1: Administrator Dashboard with Real-Time Chart.js Visuals**  
  `[ INSERT SCREENSHOT: Admin Dashboard KPI Cards & Charts ]`
- **Figure 2: Student Directory with Filters and Sorting**  
  `[ INSERT SCREENSHOT: Students Management Table & Pagination ]`
- **Figure 3: Campus Recruitment Job Openings Portal**  
  `[ INSERT SCREENSHOT: Active Job Openings Cards with Eligibility Badges ]`
- **Figure 4: Candidate Dossier & Application Progression**  
  `[ INSERT SCREENSHOT: Student Profile, Applications History & Placement Offer ]`
- **Figure 5: Institutional Accreditation & Audit Reports**  
  `[ INSERT SCREENSHOT: Department Placement Statistics & Database Audit Trail ]`
- **Figure 6: Automated Test Suite Execution in PowerShell**  
  `[ INSERT SCREENSHOT: Pytest Execution Showing 13 Passed Tests ]`

---

## 16. Testing & Results
Automated unit and integration testing was executed using `pytest 8.3.4` under an isolated in-memory test configuration. All 13 comprehensive test cases passed with zero errors:

```
tests/test_app.py::test_app_startup PASSED                     [  7%]
tests/test_app.py::test_login_validation PASSED                [ 15%]
tests/test_app.py::test_registration_validation PASSED         [ 23%]
tests/test_app.py::test_authorization_rbac PASSED              [ 30%]
tests/test_app.py::test_student_creation PASSED                [ 38%]
tests/test_app.py::test_duplicate_student_prevention PASSED    [ 46%]
tests/test_app.py::test_duplicate_application_prevention PASSED[ 53%]
tests/test_app.py::test_invalid_foreign_key_references PASSED  [ 61%]
tests/test_app.py::test_job_eligibility_checks PASSED          [ 69%]
tests/test_app.py::test_application_deadline_checks PASSED     [ 76%]
tests/test_app.py::test_placement_record_creation PASSED       [ 84%]
tests/test_app.py::test_invalid_cgpa_values PASSED             [ 92%]
tests/test_app.py::test_sql_transaction_rollback_on_failure PASSED [100%]

====================== 13 passed in 16.69s ======================
```

---

## 17. Limitations
- **Resume Storage:** The system currently stores resume URLs referencing cloud storage or web URLs rather than managing direct binary PDF uploads locally.
- **Single Institutional Database:** The system is architected for single-college campuses; multi-tenant university deployment would require institutional tenant partitioning.

---

## 18. Future Enhancements
- Integration with external email notification services (SendGrid / SMTP) for automated interview invites.
- Machine learning resume-job matching using natural language processing (NLP).
- Student skill portfolio tagging and online assessment integration.

---

## 19. Conclusion
The Student Placement Management System (SPMS) successfully demonstrates the practical application of core Database Management System (DBMS) principles in a modern software engineering context. By combining a mathematically normalized schema (3NF/BCNF) with relational constraints, stored procedures, triggers, views, and ACID transaction services, SPMS achieves data reliability, security, and institutional reporting efficiency.

---

## 20. References
1. Elmasri, R., & Navathe, S. B. (2016). *Fundamentals of Database Systems* (7th ed.). Pearson.
2. Silberschatz, A., Korth, H. F., & Sudarshan, S. (2020). *Database System Concepts* (7th ed.). McGraw-Hill.
3. MySQL 8.0 Reference Manual: *InnoDB Storage Engine and Transaction Model*. Oracle Corporation.
4. Grinberg, M. (2018). *Flask Web Development: Developing Web Applications with Python*. O'Reilly Media.
