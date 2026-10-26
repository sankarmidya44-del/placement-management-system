# Entity-Relationship (ER) Diagram & Data Model
## Student Placement Management System (SPMS)

### 1. Conceptual ER Modeling Overview
The Student Placement Management System (SPMS) models the core entities and operational relationships of a higher education placement and recruitment cell. The architecture resolves many-to-many relationships between Students and Job Postings through the associative entity **Applications**, and models confirmed career selections through **Placements**.

---

### 2. Mermaid Entity-Relationship Diagram

```mermaid
erDiagram
    DEPARTMENTS ||--o{ STUDENTS : "offers degree to"
    STUDENTS ||--o| USERS : "authenticates via"
    STUDENTS ||--o{ APPLICATIONS : "submits"
    STUDENTS ||--o{ PLACEMENTS : "receives"
    COMPANIES ||--o{ JOBS : "posts"
    COMPANIES ||--o{ PLACEMENTS : "employs"
    JOBS ||--o{ APPLICATIONS : "receives"
    JOBS ||--o{ PLACEMENTS : "fulfills"
    APPLICATIONS ||--o{ INTERVIEWS : "scheduled for"

    DEPARTMENTS {
        int department_id PK "Primary Key, Auto Increment"
        string department_name UK "Unique, Not Null"
        string department_code UK "Unique, Not Null"
        timestamp created_at "Default Current Timestamp"
    }

    STUDENTS {
        int student_id PK "Primary Key, Auto Increment"
        string roll_number UK "Unique, Not Null"
        string first_name "Not Null"
        string last_name "Not Null"
        string email UK "Unique, Not Null"
        string phone "Contact Number"
        int department_id FK "References DEPARTMENTS"
        int graduation_year "Graduation Cohort Year"
        decimal cgpa "Check 0.00 to 10.00"
        int backlogs "Check >= 0"
        string resume_url "Document Link"
        timestamp created_at "Registration Timestamp"
    }

    USERS {
        int user_id PK "Primary Key, Auto Increment"
        string username UK "Unique, Not Null"
        string email UK "Unique, Not Null"
        string password_hash "Argon2 / Scrypt Hash"
        string role "Admin or Student"
        int student_id FK "Nullable, References STUDENTS"
        timestamp created_at "Creation Timestamp"
    }

    COMPANIES {
        int company_id PK "Primary Key, Auto Increment"
        string company_name "Not Null"
        string industry "Sector Classification"
        string website "Corporate URL"
        string contact_email "Recruiter Email"
        string contact_phone "Contact Phone"
        text company_description "Company Profile"
        timestamp created_at "Registration Timestamp"
    }

    JOBS {
        int job_id PK "Primary Key, Auto Increment"
        int company_id FK "References COMPANIES"
        string job_title "Not Null"
        text job_description "Responsibilities & Scope"
        string job_type "Full-Time or Internship"
        string location "Job Location"
        decimal minimum_cgpa "Check 0.00 to 10.00"
        int maximum_backlogs "Check >= 0"
        decimal salary_lpa "Package in Lakhs Per Annum"
        date application_deadline "Cutoff Date"
        string job_status "Open or Closed"
        timestamp created_at "Posting Timestamp"
    }

    APPLICATIONS {
        int application_id PK "Primary Key, Auto Increment"
        int student_id FK "References STUDENTS"
        int job_id FK "References JOBS"
        timestamp application_date "Submission Timestamp"
        string application_status "Applied, Shortlisted, etc."
        string resume_url "Application Resume"
        timestamp updated_at "Update Timestamp"
    }

    INTERVIEWS {
        int interview_id PK "Primary Key, Auto Increment"
        int application_id FK "References APPLICATIONS"
        string interview_round "Technical, HR, etc."
        datetime interview_date "Scheduled Date Time"
        string interview_mode "Online or Offline"
        string interview_location "Room or Link"
        text interviewer_notes "Evaluation Notes"
        string interview_result "Pending, Passed, Failed"
        timestamp created_at "Creation Timestamp"
    }

    PLACEMENTS {
        int placement_id PK "Primary Key, Auto Increment"
        int student_id FK "References STUDENTS"
        int job_id FK "References JOBS"
        int company_id FK "References COMPANIES"
        date offer_date "Offer Extended Date"
        decimal package_lpa "Confirmed Salary in LPA"
        string placement_status "Offered, Accepted, Declined"
        timestamp created_at "Creation Timestamp"
    }
```

---

### 3. Entity Relationships & Cardinalities

1. **Departments to Students (1 : M)**
   - One Department can enroll many Students.
   - Each Student must belong to exactly one Department (`ON DELETE RESTRICT`).

2. **Students to Users (1 : 1 / 1 : 0..1)**
   - A registered student may have one User authentication record.
   - An administrator user does not link to any student (`student_id IS NULL`).

3. **Companies to Jobs (1 : M)**
   - A Company can publish multiple recruitment openings over time.
   - Each Job belongs to exactly one hiring Company (`ON DELETE RESTRICT`).

4. **Students to Jobs (M : N via Applications)**
   - A Student may submit applications to multiple Job openings.
   - A Job receives applications from multiple eligible candidates.
   - **Associative Entity**: `applications` resolves this M:N relationship, with a composite unique constraint `UNIQUE(student_id, job_id)`.

5. **Applications to Interviews (1 : M)**
   - An Application can progress through multiple sequential evaluation rounds (Assessment, Technical Round 1, Director Interview, HR Round).
   - Each Interview is tied to exactly one Application (`ON DELETE CASCADE`).

6. **Placements (Ternary Relationship between Student, Job, and Company)**
   - Each final offer links the placed Student, the Job role, and the recruiting Company.
   - `ON DELETE RESTRICT` guarantees that historical placement records cannot be accidentally deleted by cascading student or company removals.
