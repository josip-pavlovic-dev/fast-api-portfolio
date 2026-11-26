-- Oblast 05, lekcija 04: SELF JOIN
-- Teorija: ../../../05_table_joins/04_sqlite_SELF_join.md
-- Svi blokovi su samo za čitanje. Vežbaj nad ChinookPractice ili SQLite CLI-jem
-- otvorenim nad chinook_practice.db, nikada nad bazom aplikacije.
--
-- SQLTools: pokreni pojedinačni -- @block ili označeni upit.
-- SQLite CLI: iz root-a repozitorijuma pokreni:
--   sqlite3 -readonly fast-api-course-my-work/sqlite_for_beginners/playground/databases/chinook_practice.db
-- pa u CLI promptu:
--   .read fast-api-course-my-work/sqlite_for_beginners/playground/sql/05_table_joins/04_sqlite_SELF_join.sql

-- @block Vežba 1: Rukovodioci i njihovi neposredni podređeni
SELECT
    m.EmployeeId AS ManagerId,
    m.FirstName || ' ' || m.LastName AS Manager,
    e.EmployeeId AS DirectReportId,
    e.FirstName || ' ' || e.LastName AS DirectReport,
    e.Title AS DirectReportTitle
FROM employees AS e
INNER JOIN employees AS m
    ON m.EmployeeId = e.ReportsTo
ORDER BY
    m.LastName,
    m.FirstName,
    e.LastName,
    e.FirstName;

-- Očekivano: 7 parova. Andrew Adams ima dva neposredno podređena zaposlena.

-- @block Vežba 2: Prebroj zaposlene i parove
SELECT COUNT(*) AS employee_count
FROM employees;

SELECT COUNT(*) AS manager_report_pairs
FROM employees AS e
INNER JOIN employees AS m
    ON m.EmployeeId = e.ReportsTo;

-- U ovoj kopiji ima 8 zaposlenih i 7 parova; zaposleni bez rukovodioca
-- izostaje iz INNER JOIN rezultata.

-- @block Vežba 3: Zadrži sve zaposlene i opcionog rukovodioca
SELECT
    e.EmployeeId,
    e.FirstName || ' ' || e.LastName AS Employee,
    m.FirstName || ' ' || m.LastName AS Manager
FROM employees AS e
LEFT JOIN employees AS m
    ON m.EmployeeId = e.ReportsTo
ORDER BY e.EmployeeId;

-- Vraća 8 redova. Kod Andrewa Adamsa je Manager NULL.

-- @block Vežba 3.1: Pronađi zaposlenog bez rukovodioca
SELECT
    e.EmployeeId,
    e.FirstName || ' ' || e.LastName AS Employee
FROM employees AS e
LEFT JOIN employees AS m
    ON m.EmployeeId = e.ReportsTo
WHERE m.EmployeeId IS NULL
ORDER BY e.EmployeeId;

-- @block Vežba 4: Dodaj titule obeju uloga
SELECT
    m.Title AS ManagerTitle,
    m.FirstName || ' ' || m.LastName AS Manager,
    e.Title AS EmployeeTitle,
    e.FirstName || ' ' || e.LastName AS Employee
FROM employees AS e
INNER JOIN employees AS m
    ON m.EmployeeId = e.ReportsTo
ORDER BY Manager, Employee;

-- @block Vežba 5: Stariji implicitni oblik (INNER JOIN)
SELECT
    m.FirstName || ' ' || m.LastName AS Manager,
    e.FirstName || ' ' || e.LastName AS DirectReport
FROM employees AS e, employees AS m
WHERE m.EmployeeId = e.ReportsTo
ORDER BY Manager, DirectReport;

-- Uporedi ga sa eksplicitnim INNER JOIN-om iz prvog bloka. JOIN ... ON
-- jasnije odvaja uslov povezivanja od dodatnih filtera.

-- @block Ivični slučaj: NULL ReportsTo nema rukovodioca za spajanje
SELECT
    COUNT(*) AS all_employees,
    SUM(ReportsTo IS NULL) AS employees_without_manager
FROM employees;

-- Očekivano: 8 zaposlenih, 1 bez rukovodioca. NULL se ne poklapa sa ID-em.
