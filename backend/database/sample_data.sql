-- =============================================================================
-- STUDENT PLACEMENT MANAGEMENT SYSTEM (SPMS)
-- Database: student_placement_db
-- Target Engine: MySQL 8.0+
-- Script: sample_data.sql (DML - Data Manipulation Language)
-- =============================================================================

USE student_placement_db;

-- -----------------------------------------------------------------------------
-- 1. DEPARTMENTS (5 Records)
-- -----------------------------------------------------------------------------
INSERT INTO departments (department_id, department_name, department_code) VALUES
(1, 'Computer Science & Engineering', 'CSE'),
(2, 'Information Technology', 'IT'),
(3, 'Electronics & Communication Engineering', 'ECE'),
(4, 'Mechanical Engineering', 'ME'),
(5, 'Electrical & Electronics Engineering', 'EEE');

-- -----------------------------------------------------------------------------
-- 2. STUDENTS (22 Records)
-- -----------------------------------------------------------------------------
INSERT INTO students (student_id, roll_number, first_name, last_name, email, phone, department_id, graduation_year, cgpa, backlogs, resume_url) VALUES
(1, '21CS001', 'Aarav', 'Sharma', 'aarav.sharma@college.edu', '9876543210', 1, 2025, 9.40, 0, 'https://storage.college.edu/resumes/21CS001.pdf'),
(2, '21CS002', 'Priya', 'Patel', 'priya.patel@college.edu', '9876543211', 1, 2025, 8.85, 0, 'https://storage.college.edu/resumes/21CS002.pdf'),
(3, '21CS003', 'Rohan', 'Verma', 'rohan.verma@college.edu', '9876543212', 1, 2025, 7.60, 1, 'https://storage.college.edu/resumes/21CS003.pdf'),
(4, '21CS004', 'Sneha', 'Reddy', 'sneha.reddy@college.edu', '9876543213', 1, 2025, 9.15, 0, 'https://storage.college.edu/resumes/21CS004.pdf'),
(5, '21IT001', 'Aditya', 'Nair', 'aditya.nair@college.edu', '9876543214', 2, 2025, 8.20, 0, 'https://storage.college.edu/resumes/21IT001.pdf'),
(6, '21IT002', 'Ananya', 'Iyer', 'ananya.iyer@college.edu', '9876543215', 2, 2025, 9.05, 0, 'https://storage.college.edu/resumes/21IT002.pdf'),
(7, '21IT003', 'Vikram', 'Singh', 'vikram.singh@college.edu', '9876543216', 2, 2025, 6.90, 2, 'https://storage.college.edu/resumes/21IT003.pdf'),
(8, '21EC001', 'Kavya', 'Menon', 'kavya.menon@college.edu', '9876543217', 3, 2025, 8.45, 0, 'https://storage.college.edu/resumes/21EC001.pdf'),
(9, '21EC002', 'Rahul', 'Gupta', 'rahul.gupta@college.edu', '9876543218', 3, 2025, 7.80, 0, 'https://storage.college.edu/resumes/21EC002.pdf'),
(10, '21EC003', 'Deepika', 'Joshi', 'deepika.joshi@college.edu', '9876543219', 3, 2025, 9.30, 0, 'https://storage.college.edu/resumes/21EC003.pdf'),
(11, '21ME001', 'Arjun', 'Kulkarni', 'arjun.kulkarni@college.edu', '9876543220', 4, 2025, 7.50, 0, 'https://storage.college.edu/resumes/21ME001.pdf'),
(12, '21ME002', 'Pooja', 'Deshmukh', 'pooja.deshmukh@college.edu', '9876543221', 4, 2025, 8.10, 0, 'https://storage.college.edu/resumes/21ME002.pdf'),
(13, '21EE001', 'Siddharth', 'Rao', 'siddharth.rao@college.edu', '9876543222', 5, 2025, 8.60, 0, 'https://storage.college.edu/resumes/21EE001.pdf'),
(14, '21EE002', 'Meera', 'Pillai', 'meera.pillai@college.edu', '9876543223', 5, 2025, 7.20, 1, 'https://storage.college.edu/resumes/21EE002.pdf'),
(15, '22CS001', 'Karan', 'Malhotra', 'karan.malhotra@college.edu', '9876543224', 1, 2026, 8.90, 0, 'https://storage.college.edu/resumes/22CS001.pdf'),
(16, '22CS002', 'Divya', 'Bansal', 'divya.bansal@college.edu', '9876543225', 1, 2026, 9.60, 0, 'https://storage.college.edu/resumes/22CS002.pdf'),
(17, '22IT001', 'Varun', 'Mehta', 'varun.mehta@college.edu', '9876543226', 2, 2026, 7.40, 0, 'https://storage.college.edu/resumes/22IT001.pdf'),
(18, '22EC001', 'Tanvi', 'Shah', 'tanvi.shah@college.edu', '9876543227', 3, 2026, 8.70, 0, 'https://storage.college.edu/resumes/22EC001.pdf'),
(19, '22ME001', 'Nikhil', 'Chopra', 'nikhil.chopra@college.edu', '9876543228', 4, 2026, 6.75, 1, 'https://storage.college.edu/resumes/22ME001.pdf'),
(20, '22EE001', 'Riya', 'Sen', 'riya.sen@college.edu', '9876543229', 5, 2026, 8.35, 0, 'https://storage.college.edu/resumes/22EE001.pdf'),
(21, '21CS005', 'Harsh', 'Vardhan', 'harsh.vardhan@college.edu', '9876543230', 1, 2025, 6.40, 3, 'https://storage.college.edu/resumes/21CS005.pdf'),
(22, '21IT004', 'Simran', 'Kaur', 'simran.kaur@college.edu', '9876543231', 2, 2025, 9.75, 0, 'https://storage.college.edu/resumes/21IT004.pdf');

-- -----------------------------------------------------------------------------
-- 3. USERS (Admin + Registered Students)
-- Default password for admin: 'admin123'
-- Default password for students: 'student123'
-- -----------------------------------------------------------------------------
INSERT INTO users (user_id, username, email, password_hash, role, student_id) VALUES
(1, 'admin', 'placement.officer@college.edu', 'scrypt:32768:8:1$SorsNERPtigXDygs$fab22f231430b2998d9e1dc531f2c3d7b2ffcc2fabbd95d4ccddc0dc5bfa8da486e7c3f3fd32448ff50e48bf7fbe8abb2a5226f19d66b449975827b60e7a04b9', 'Admin', NULL),
(2, 'aarav.sharma', 'aarav.sharma@college.edu', 'scrypt:32768:8:1$KKT0j3gHdGsHgXud$29b7de9e05a5bb62e95fe3ce63a675ae3893d67276e5726a7d7982bc0f0ec3ff7b80580bd98d70aebf71dbe5f3317edfb8d4a059ef79da210a504fc7f42eacbf', 'Student', 1),
(3, 'priya.patel', 'priya.patel@college.edu', 'scrypt:32768:8:1$KKT0j3gHdGsHgXud$29b7de9e05a5bb62e95fe3ce63a675ae3893d67276e5726a7d7982bc0f0ec3ff7b80580bd98d70aebf71dbe5f3317edfb8d4a059ef79da210a504fc7f42eacbf', 'Student', 2),
(4, 'sneha.reddy', 'sneha.reddy@college.edu', 'scrypt:32768:8:1$KKT0j3gHdGsHgXud$29b7de9e05a5bb62e95fe3ce63a675ae3893d67276e5726a7d7982bc0f0ec3ff7b80580bd98d70aebf71dbe5f3317edfb8d4a059ef79da210a504fc7f42eacbf', 'Student', 4),
(5, 'ananya.iyer', 'ananya.iyer@college.edu', 'scrypt:32768:8:1$KKT0j3gHdGsHgXud$29b7de9e05a5bb62e95fe3ce63a675ae3893d67276e5726a7d7982bc0f0ec3ff7b80580bd98d70aebf71dbe5f3317edfb8d4a059ef79da210a504fc7f42eacbf', 'Student', 6);

-- -----------------------------------------------------------------------------
-- 4. COMPANIES (9 Records)
-- -----------------------------------------------------------------------------
INSERT INTO companies (company_id, company_name, industry, website, contact_email, contact_phone, company_description) VALUES
(1, 'Google India', 'Technology / Internet', 'https://careers.google.com', 'india-campus@google.com', '+91 80 6721 8000', 'Global technology leader specializing in search, cloud computing, AI, and enterprise software.'),
(2, 'Microsoft India', 'Software / Cloud', 'https://careers.microsoft.com', 'msindia-campus@microsoft.com', '+91 80 4010 3000', 'World leader in personal computing platforms, Azure cloud services, and productivity applications.'),
(3, 'Amazon Web Services', 'Cloud / E-Commerce', 'https://amazon.jobs', 'aws-grad-hiring@amazon.com', '+91 80 4344 0000', 'Pioneering cloud computing infrastructure and large-scale distributed systems.'),
(4, 'Tata Consultancy Services', 'IT Services / Consulting', 'https://www.tcs.com/careers', 'campus.tcs@tcs.com', '+91 22 6778 9999', 'Premier multinational information technology services and consulting organization.'),
(5, 'Infosys Limited', 'IT Services', 'https://www.infosys.com/careers', 'talent@infosys.com', '+91 80 2852 0261', 'Global provider of digital services, next-generation IT consulting, and outsourcing solutions.'),
(6, 'Cisco Systems', 'Networking / Cybersecurity', 'https://www.cisco.com/careers', 'cisco-india-campus@cisco.com', '+91 80 4426 0000', 'Worldwide leader in computer networking hardware, IoT, and cybersecurity software.'),
(7, 'Deloitte USI', 'Management & Tech Consulting', 'https://www2.deloitte.com', 'usi-campus@deloitte.com', '+91 40 6762 1000', 'Top-tier audit, consulting, tax, and advisory services for global enterprises.'),
(8, 'Qualcomm India', 'Semiconductors / Wireless', 'https://www.qualcomm.com/careers', 'qualcomm-campus@qualcomm.com', '+91 40 6608 0000', 'World leading wireless technology innovator and semiconductor designer.'),
(9, 'Larsen & Toubro', 'Engineering / Infrastructure', 'https://www.larsentoubro.com', 'lnt-campus@larsentoubro.com', '+91 22 6752 5656', 'Major technology, engineering, construction, manufacturing, and financial conglomerate.');

-- -----------------------------------------------------------------------------
-- 5. JOBS (14 Records)
-- -----------------------------------------------------------------------------
INSERT INTO jobs (job_id, company_id, job_title, job_description, job_type, location, minimum_cgpa, maximum_backlogs, salary_lpa, application_deadline, job_status) VALUES
(1, 1, 'Software Engineer - Campus', 'Build distributed cloud infrastructure, search algorithms, and machine learning models.', 'Full-Time', 'Bangalore / Hyderabad', 8.50, 0, 32.00, '2026-11-30', 'Open'),
(2, 2, 'Software Development Engineer I', 'Develop Azure cloud solutions, developer tooling, and distributed backend services.', 'Full-Time', 'Hyderabad', 8.00, 0, 28.50, '2026-11-25', 'Open'),
(3, 3, 'Cloud Support Associate', 'Provide enterprise cloud architecture guidance and technical troubleshooting on AWS.', 'Full-Time', 'Bangalore', 7.50, 0, 18.00, '2026-12-05', 'Open'),
(4, 3, 'Software Development Engineer - Intern', 'Summer intern program working on retail microservices and DynamoDB high-scale features.', 'Internship', 'Hyderabad', 8.00, 0, 12.00, '2026-10-15', 'Closed'),
(5, 4, 'Digital Software Developer', 'Next-gen software engineering, IoT, and cloud-native application modernization.', 'Full-Time', 'Pan India', 7.00, 1, 7.50, '2026-12-15', 'Open'),
(6, 4, 'Ninja Developer', 'Core software systems engineering, competitive programming, and automation.', 'Full-Time', 'Pune / Chennai', 6.50, 1, 3.80, '2026-12-31', 'Open'),
(7, 5, 'Specialist Programmer', 'High-performance computing, advanced data structures, and enterprise architecture.', 'Full-Time', 'Bangalore / Mysore', 7.50, 0, 9.50, '2026-11-20', 'Open'),
(8, 5, 'Systems Engineer', 'Application maintenance, system testing, and full-stack software development.', 'Full-Time', 'Pan India', 6.00, 2, 4.00, '2026-12-20', 'Open'),
(9, 6, 'Network Software Engineer', 'Design software-defined networking (SDN) stacks, routing protocols, and security.', 'Full-Time', 'Bangalore', 7.80, 0, 19.50, '2026-11-15', 'Open'),
(10, 7, 'Technology Analyst', 'Implement SAP, Salesforce, data visualization, and cloud transformation projects.', 'Full-Time', 'Hyderabad / Mumbai', 7.00, 0, 9.00, '2026-11-28', 'Open'),
(11, 8, 'Hardware / Embedded Engineer', 'ASIC design, RTL verification, firmware development, and Snapdragon SoC validation.', 'Full-Time', 'Hyderabad / Chennai', 8.00, 0, 22.00, '2026-11-18', 'Open'),
(12, 9, 'Graduate Engineer Trainee', 'Mechanical systems design, robotics automation, and industrial infrastructure planning.', 'Full-Time', 'Mumbai / Baroda', 6.80, 0, 6.50, '2026-12-10', 'Open'),
(13, 1, 'Data Engineering Specialist', 'Large-scale BigQuery pipelines and stream processing engines.', 'Full-Time', 'Bangalore', 8.20, 0, 26.00, '2026-10-01', 'Closed'),
(14, 2, 'Support Engineer', 'Customer engineering support for enterprise Office 365 and Windows Server platforms.', 'Full-Time', 'Bangalore', 6.50, 1, 14.00, '2026-12-28', 'Open');

-- -----------------------------------------------------------------------------
-- 6. APPLICATIONS (30 Records)
-- Varied statuses: Applied, Shortlisted, Interview Scheduled, Selected, Rejected, Withdrawn
-- -----------------------------------------------------------------------------
INSERT INTO applications (application_id, student_id, job_id, application_date, application_status, resume_url) VALUES
(1, 1, 1, '2026-09-10 10:30:00', 'Selected', 'https://storage.college.edu/resumes/21CS001.pdf'),
(2, 1, 2, '2026-09-12 11:15:00', 'Shortlisted', 'https://storage.college.edu/resumes/21CS001.pdf'),
(3, 2, 1, '2026-09-10 14:00:00', 'Interview Scheduled', 'https://storage.college.edu/resumes/21CS002.pdf'),
(4, 2, 2, '2026-09-11 09:20:00', 'Selected', 'https://storage.college.edu/resumes/21CS002.pdf'),
(5, 3, 5, '2026-09-15 16:45:00', 'Shortlisted', 'https://storage.college.edu/resumes/21CS003.pdf'),
(6, 3, 6, '2026-09-16 10:00:00', 'Applied', 'https://storage.college.edu/resumes/21CS003.pdf'),
(7, 4, 1, '2026-09-10 12:10:00', 'Interview Scheduled', 'https://storage.college.edu/resumes/21CS004.pdf'),
(8, 4, 3, '2026-09-14 15:30:00', 'Selected', 'https://storage.college.edu/resumes/21CS004.pdf'),
(9, 5, 3, '2026-09-14 17:00:00', 'Selected', 'https://storage.college.edu/resumes/21IT001.pdf'),
(10, 5, 5, '2026-09-18 11:40:00', 'Withdrawn', 'https://storage.college.edu/resumes/21IT001.pdf'),
(11, 6, 2, '2026-09-11 10:50:00', 'Selected', 'https://storage.college.edu/resumes/21IT002.pdf'),
(12, 6, 7, '2026-09-19 14:15:00', 'Shortlisted', 'https://storage.college.edu/resumes/21IT002.pdf'),
(13, 7, 6, '2026-09-16 13:25:00', 'Rejected', 'https://storage.college.edu/resumes/21IT003.pdf'),
(14, 7, 8, '2026-09-20 09:30:00', 'Applied', 'https://storage.college.edu/resumes/21IT003.pdf'),
(15, 8, 9, '2026-09-15 11:00:00', 'Selected', 'https://storage.college.edu/resumes/21EC001.pdf'),
(16, 8, 11, '2026-09-17 15:45:00', 'Shortlisted', 'https://storage.college.edu/resumes/21EC001.pdf'),
(17, 9, 5, '2026-09-18 10:15:00', 'Shortlisted', 'https://storage.college.edu/resumes/21EC002.pdf'),
(18, 9, 9, '2026-09-15 12:30:00', 'Rejected', 'https://storage.college.edu/resumes/21EC002.pdf'),
(19, 10, 11, '2026-09-17 14:20:00', 'Selected', 'https://storage.college.edu/resumes/21EC003.pdf'),
(20, 11, 12, '2026-09-22 09:00:00', 'Selected', 'https://storage.college.edu/resumes/21ME001.pdf'),
(21, 12, 10, '2026-09-21 16:00:00', 'Selected', 'https://storage.college.edu/resumes/21ME002.pdf'),
(22, 13, 10, '2026-09-21 15:10:00', 'Interview Scheduled', 'https://storage.college.edu/resumes/21EE001.pdf'),
(23, 13, 11, '2026-09-18 11:00:00', 'Rejected', 'https://storage.college.edu/resumes/21EE001.pdf'),
(24, 14, 6, '2026-09-20 14:00:00', 'Applied', 'https://storage.college.edu/resumes/21EE002.pdf'),
(25, 15, 2, '2026-09-12 16:30:00', 'Shortlisted', 'https://storage.college.edu/resumes/22CS001.pdf'),
(26, 16, 1, '2026-09-11 11:45:00', 'Interview Scheduled', 'https://storage.college.edu/resumes/22CS002.pdf'),
(27, 17, 7, '2026-09-22 10:15:00', 'Applied', 'https://storage.college.edu/resumes/22IT001.pdf'),
(28, 18, 9, '2026-09-16 13:40:00', 'Shortlisted', 'https://storage.college.edu/resumes/22EC001.pdf'),
(29, 21, 8, '2026-09-23 11:20:00', 'Applied', 'https://storage.college.edu/resumes/21CS005.pdf'),
(30, 22, 1, '2026-09-11 09:00:00', 'Shortlisted', 'https://storage.college.edu/resumes/21IT004.pdf');

-- -----------------------------------------------------------------------------
-- 7. INTERVIEWS (10 Records)
-- -----------------------------------------------------------------------------
INSERT INTO interviews (interview_id, application_id, interview_round, interview_date, interview_mode, interview_location, interviewer_notes, interview_result) VALUES
(1, 1, 'Technical Round 1', '2026-09-25 10:00:00', 'Online', 'Google Meet / Room A', 'Excellent problem solving in DSA and graph algorithms.', 'Passed'),
(2, 1, 'System Design & HR', '2026-09-28 14:00:00', 'Online', 'Google Meet / Room B', 'Strong communication, culture fit, and clear scalability insights.', 'Passed'),
(3, 3, 'Technical Round 1', '2026-10-02 11:00:00', 'Online', 'Google Meet / Room C', 'Strong understanding of databases and SQL query execution.', 'Pending'),
(4, 4, 'Technical Round 1', '2026-09-24 10:30:00', 'Online', 'MS Teams / Room 1', 'Clean C++ coding style, solved concurrency problem.', 'Passed'),
(5, 4, 'Director Round', '2026-09-27 15:00:00', 'Online', 'MS Teams / Executive', 'Outstanding vision and cloud architecture concepts.', 'Passed'),
(6, 7, 'Technical Round 1', '2026-10-03 14:30:00', 'Online', 'Google Meet / Room A', 'Good analytical thinking; questions on dynamic programming scheduled.', 'Pending'),
(7, 8, 'Online Assessment', '2026-09-20 09:00:00', 'Online', 'Hackerrank Platform', 'Score 100/100 on operating systems and network fundamentals.', 'Passed'),
(8, 9, 'AWS Architecture Round', '2026-09-26 11:30:00', 'Online', 'Amazon Chime', 'Hands-on knowledge of VPC, S3, and IAM policies.', 'Passed'),
(9, 15, 'Network Protocol Round', '2026-09-29 10:00:00', 'Offline', 'Campus Placement Cell - Lab 2', 'Demonstrated TCP/IP handshake and subnetting calculations accurately.', 'Passed'),
(10, 22, 'Consulting Aptitude & Case Study', '2026-10-04 14:00:00', 'Offline', 'Campus Placement Cell - Board Room', 'Case presentation on supply-chain tech optimization.', 'Pending');

-- -----------------------------------------------------------------------------
-- 8. PLACEMENTS (8 Records)
-- Consistency: Matches student, job, and company accurately.
-- -----------------------------------------------------------------------------
INSERT INTO placements (placement_id, student_id, job_id, company_id, offer_date, package_lpa, placement_status) VALUES
(1, 1, 1, 1, '2026-10-01', 32.00, 'Accepted'),
(2, 2, 2, 2, '2026-10-02', 28.50, 'Accepted'),
(3, 4, 3, 3, '2026-10-03', 18.00, 'Accepted'),
(4, 5, 3, 3, '2026-10-03', 18.00, 'Accepted'),
(5, 6, 2, 2, '2026-10-04', 28.50, 'Accepted'),
(6, 8, 9, 6, '2026-10-05', 19.50, 'Accepted'),
(7, 10, 11, 8, '2026-10-05', 22.00, 'Accepted'),
(8, 12, 10, 7, '2026-10-06', 9.00, 'Accepted');

-- -----------------------------------------------------------------------------
-- 9. AUDIT LOGS (Sample Initial Records)
-- -----------------------------------------------------------------------------
INSERT INTO audit_logs (table_name, record_id, action, old_values, new_values, changed_by) VALUES
('applications', 1, 'UPDATE', 'status: Shortlisted', 'status: Selected', 'admin'),
('placements', 1, 'INSERT', NULL, 'placement_id: 1, student: Aarav Sharma, package: 32.00 LPA', 'admin'),
('applications', 4, 'UPDATE', 'status: Interview Scheduled', 'status: Selected', 'admin'),
('placements', 2, 'INSERT', NULL, 'placement_id: 2, student: Priya Patel, package: 28.50 LPA', 'admin');
