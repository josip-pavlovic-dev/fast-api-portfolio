-- Oblast 06, lekcija 08: SQLite GROUP BY
-- Teorija: ../../../06_sqlite_aggregate_functions/08_sqlite_GROUP_BY_clause.md
-- Svi blokovi su samo za čitanje. Pokreći ih nad chinook_practice.db.
--
-- SQLTools: pokreni pojedinačni -- @block ili označeni upit.
-- SQLite CLI: iz root-a repozitorijuma pokreni:
--   sqlite3 -readonly fast-api-course-my-work/sqlite_for_beginners/playground/databases/chinook_practice.db
-- pa u CLI promptu:
--   .read fast-api-course-my-work/sqlite_for_beginners/playground/sql/06_sqlite_aggregate_functions/08_sqlite_GROUP_BY_clause.sql

-- @block Vežba 1: Broj numera po albumu
SELECT
    AlbumId,
    COUNT(TrackId) AS track_count
FROM tracks
GROUP BY AlbumId
ORDER BY AlbumId;

-- U ovoj kopiji ima 347 grupa; albumi 1, 2 i 3 imaju 10, 1 i 3 numere.

-- @block Vežba 2: Grupisanje po kombinaciji države i grada
SELECT
    BillingCountry,
    BillingCity,
    COUNT(*) AS invoice_count
FROM invoices
GROUP BY BillingCountry, BillingCity
ORDER BY BillingCountry, BillingCity;

-- @block Vežba 3: Grupisanje po izrazu za mesec
SELECT
    substr(InvoiceDate, 1, 7) AS invoice_month,
    COUNT(*) AS invoice_count,
    ROUND(SUM(Total), 2) AS revenue
FROM invoices
GROUP BY substr(InvoiceDate, 1, 7)
ORDER BY invoice_month;

-- @block Vežba 4: Više agregata u jednoj grupi
SELECT
    AlbumId,
    COUNT(*) AS track_count,
    MIN(Milliseconds) AS shortest_ms,
    MAX(Milliseconds) AS longest_ms,
    ROUND(AVG(Milliseconds), 2) AS average_ms,
    SUM(Milliseconds) AS total_ms
FROM tracks
GROUP BY AlbumId
ORDER BY AlbumId;

-- @block Ivični slučaj: NULL vrednosti kao grupni ključ
WITH sample(category, amount) AS (
    VALUES ('food', 10), (NULL, 5), (NULL, 7), ('food', 2)
)
SELECT category, COUNT(*) AS row_count, SUM(amount) AS total
FROM sample
GROUP BY category
ORDER BY category;

-- Dva reda sa NULL grupnim ključem pripadaju istoj grupi.

-- @block Ivični slučaj: prazan ulaz sa GROUP BY
SELECT AlbumId, COUNT(*) AS track_count
FROM tracks
WHERE AlbumId = -1
GROUP BY AlbumId;

-- Nema grupa, pa nema ni izlaznih redova.

-- @block Ivični slučaj: isti prazan ulaz bez GROUP BY
SELECT COUNT(*) AS track_count
FROM tracks
WHERE AlbumId = -1;

-- Vraća jedan red sa 0 jer agregat bez GROUP BY ima implicitnu grupu.

-- @block Ivični slučaj: kolacija pri grupisanju
WITH sample(value) AS (
    VALUES ('a'), ('A'), ('b')
)
SELECT value COLLATE NOCASE AS grouped_value, COUNT(*) AS row_count
FROM sample
GROUP BY value COLLATE NOCASE
ORDER BY value COLLATE NOCASE;

-- 'a' i 'A' se grupišu zajedno uz NOCASE.

-- @block Vežba 5: LEFT JOIN i broj povezanih albuma
SELECT
    ar.ArtistId,
    ar.Name,
    COUNT(*) AS joined_rows,
    COUNT(al.AlbumId) AS album_count
FROM artists AS ar
LEFT JOIN albums AS al
    ON al.ArtistId = ar.ArtistId
GROUP BY ar.ArtistId, ar.Name
ORDER BY ar.ArtistId;

-- Za izvođača bez albuma COUNT(*) je 1, a COUNT(al.AlbumId) je 0.
