# Database Normalization Report (1NF to 3NF & BCNF)
## Student Placement Management System (SPMS)

### 1. Introduction to Relational Normalization
Normalization is a systematic database design technique that decomposes tables to eliminate data redundancy and anomalies (Insertion, Update, and Deletion anomalies) while preserving data dependencies and referential integrity.

This document formally details the normalization journey of the **Student Placement Management System (SPMS)** from an unnormalized representation (UNF) through First Normal Form (1NF), Second Normal Form (2NF), and Third Normal Form (3NF).

---

### 2. Universal Relation / Unnormalized Form (UNF)
Consider an initial, unnormalized representation capturing placement drive data in a single monolithic flat table:

$$\text{PLACEMENT\_DATA}(\text{roll\_no}, \text{student\_name}, \text{email}, \text{dept\_name}, \text{dept\_code}, \text{cgpa}, \text{backlogs}, \text{company\_name}, \text{company\_website}, \text{job\_title}, \text{salary\_lpa}, \text{app\_date}, \text{app\_status}, \text{offer\_date}, \text{package\_lpa})$$

#### Anomalies in UNF:
1. **Insertion Anomaly:** A new department or recruiting company cannot be registered without simultaneously enrolling a student or posting a job.
2. **Update Anomaly:** If a company updates its website or email, multiple rows corresponding to every student application must be modified, risking data inconsistency.
3. **Deletion Anomaly:** Deleting a student's record may inadvertently erase the entire institutional record of a company or job drive.

---

### 3. First Normal Form (1NF)
> **Definition:** A relation $R$ is in First Normal Form (1NF) if and only if all underlying attribute domains contain only **atomic (indivisible)** values, and there are no repeating groups or multivalued attributes.

#### Actions Taken to Achieve 1NF:
1. **Atomicity of Attributes:**
   - Instead of a single composite `student_name`, decompose into `first_name` and `last_name`.
   - Contact numbers and email addresses are single-valued, atomic scalar values.
2. **Elimination of Repeating Groups:**
   - Multiple interview rounds and application stages are removed from repeating columns in the student record and modeled as distinct rows in normalized child entities.
3. **Primary Key Defined:**
   - A candidate key or surrogate integer primary key is identified for each relation.

---

### 4. Second Normal Form (2NF)
> **Definition:** A relation $R$ is in Second Normal Form (2NF) if and only if it is in 1NF and **every non-prime attribute is fully functionally dependent on the entire primary key** (i.e., there are **no partial dependencies** on any candidate key).

#### Functional Dependencies in Application Management:
Consider the composite candidate key for an application: $\{\text{student\_id}, \text{job\_id}\}$.

- $\text{student\_id}, \text{job\_id} \rightarrow \text{application\_date}, \text{application\_status}, \text{resume\_url}$ (Full Dependency)
- $\text{student\_id} \rightarrow \text{first\_name}, \text{last\_name}, \text{cgpa}, \text{backlogs}$ (**Partial Dependency** on part of composite key)
- $\text{job\_id} \rightarrow \text{job\_title}, \text{salary\_lpa}, \text{deadline}$ (**Partial Dependency** on part of composite key)

#### Decomposition to Achieve 2NF:
To resolve these partial functional dependencies, the relation is decomposed into three distinct relations:
1. **`students`** ($PK: \text{student\_id}$):
   $$\text{student\_id} \rightarrow \text{roll\_number}, \text{first\_name}, \text{last\_name}, \text{email}, \text{phone}, \text{cgpa}, \text{backlogs}, \text{department\_id}$$
2. **`jobs`** ($PK: \text{job\_id}$):
   $$\text{job\_id} \rightarrow \text{company\_id}, \text{job\_title}, \text{salary\_lpa}, \text{deadline}, \text{job\_status}$$
3. **`applications`** ($PK: \text{application\_id}, \text{Candidate Key}: \{\text{student\_id}, \text{job\_id}\}$):
   $$\text{student\_id}, \text{job\_id} \rightarrow \text{application\_date}, \text{application\_status}, \text{resume\_url}$$

*Result: Every non-prime attribute is fully functionally dependent on the primary key of its relation.*

---

### 5. Third Normal Form (3NF)
> **Definition:** A relation $R$ is in Third Normal Form (3NF) if and only if it is in 2NF and **no non-prime attribute is transitively dependent on the primary key** ($X \rightarrow Y$ and $Y \rightarrow Z$, where neither $Y$ nor $Z$ is a candidate key).

#### Transitive Dependencies Identified:
1. **In Student Data:**
   $$\text{student\_id} \rightarrow \text{department\_id} \quad \text{and} \quad \text{department\_id} \rightarrow \text{department\_name}, \text{department\_code}$$
   - Here, $\text{student\_id} \rightarrow \text{department\_name}$ is a **transitive dependency** through `department_id`.
   - If not normalized, repeating department names for 5,000 students creates substantial redundancy and update anomalies.
   - **Resolution:** Extract into a separate `departments` table:
     $$\text{departments}(\underline{\text{department\_id}}, \text{department\_name}, \text{department\_code})$$
     Where $\text{students}$ retains only the foreign key `department_id`.

2. **In Job Postings:**
   $$\text{job\_id} \rightarrow \text{company\_id} \quad \text{and} \quad \text{company\_id} \rightarrow \text{company\_name}, \text{industry}, \text{website}, \text{contact\_email}$$
   - Here, $\text{job\_id} \rightarrow \text{company\_name}$ is a **transitive dependency** through `company_id`.
   - **Resolution:** Extract into a separate `companies` table:
     $$\text{companies}(\underline{\text{company\_id}}, \text{company\_name}, \text{industry}, \text{website}, \text{contact\_email}, \text{contact\_phone})$$
     Where $\text{jobs}$ retains only the foreign key `company_id`.

3. **In Interview Scheduling:**
   $$\text{interview\_id} \rightarrow \text{application\_id} \quad \text{and} \quad \text{application\_id} \rightarrow \text{student\_id}, \text{job\_id}$$
   - Resolves scheduling specifics independently of the student profile.
   - **Resolution:**
     $$\text{interviews}(\underline{\text{interview\_id}}, \text{application\_id}, \text{interview\_round}, \text{interview\_date}, \text{interview\_mode}, \text{interview\_result})$$

---

### 6. Boyce-Codd Normal Form (BCNF) Analysis
> **Definition:** A relation $R$ is in BCNF if and only if for every non-trivial functional dependency $X \rightarrow Y$, the determinant $X$ is a **Superkey**.

In the finalized schema:
- In `departments`: $\text{department\_id} \rightarrow \text{department\_name}, \text{department\_code}$. Determinant $\text{department\_id}$ is a Superkey. Furthermore, $\text{department\_code} \rightarrow \text{department\_id}$ holds, and `department_code` is also a unique candidate key.
- In `students`: $\text{student\_id} \rightarrow \text{all attributes}$; and $\text{roll\_number} \rightarrow \text{all attributes}$. Both determinants are candidate keys.
- In `users`: $\text{user\_id} \rightarrow \text{all attributes}$; and $\text{username} \rightarrow \text{all attributes}$. Both determinants are candidate keys.
- In `applications`: $\text{application\_id} \rightarrow \text{all attributes}$; and $\{\text{student\_id}, \text{job\_id}\} \rightarrow \text{all attributes}$. Both determinants are candidate keys.

Therefore, every determinant across the entire SPMS schema is a Superkey, satisfying both **3NF and BCNF**.

---

### 7. Summary of Final Normalized Schema

| Relation | Primary Key | Foreign Keys | Normal Form | Key Dependencies Satisfied |
| :--- | :--- | :--- | :---: | :--- |
| `departments` | `department_id` | *None* | **3NF / BCNF** | Unique codes & department names |
| `students` | `student_id` | `department_id` | **3NF / BCNF** | No transitive dependency on department info |
| `users` | `user_id` | `student_id` | **3NF / BCNF** | Isolated authentication & role credentials |
| `companies` | `company_id` | *None* | **3NF / BCNF** | No repeating company metadata in job records |
| `jobs` | `job_id` | `company_id` | **3NF / BCNF** | Determinant `job_id` is Superkey |
| `applications` | `application_id` | `student_id`, `job_id` | **3NF / BCNF** | Resolves M:N Student-Job relation without partial dependencies |
| `interviews` | `interview_id` | `application_id` | **3NF / BCNF** | Preserves atomic round evaluations |
| `placements` | `placement_id` | `student_id`, `job_id`, `company_id` | **3NF / BCNF** | Historical integrity with RESTRICT deletion behavior |
