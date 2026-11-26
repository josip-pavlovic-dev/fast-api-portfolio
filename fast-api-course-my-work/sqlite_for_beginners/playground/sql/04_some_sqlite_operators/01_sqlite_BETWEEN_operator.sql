-- Oblast 04, lekcija 01: BETWEEN
-- Teorija: ../../../04_some_sqlite_operators/01_sqlite_BETWEEN_operator.md
-- Svi blokovi su samo za čitanje. Vežbaj nad ChinookPractice ili SQLite CLI-jem
-- otvorenim nad chinook_practice.db, nikada nad bazom aplikacije.
--
-- SQLTools: pokreni pojedinačni -- @block ili označeni upit.
-- SQLite CLI: iz root-a repozitorijuma pokreni:
--   sqlite3 -readonly fast-api-course-my-work/sqlite_for_beginners/playground/databases/chinook_practice.db
-- pa u CLI promptu:
--   .read fast-api-course-my-work/sqlite_for_beginners/playground/sql/04_some_sqlite_operators/01_sqlite_BETWEEN_operator.sql

-- @block Vežba 1: Računi u opsegu od 5 do 10
SELECT InvoiceId, BillingAddress, Total
FROM invoices
WHERE Total BETWEEN 5 AND 10
ORDER BY Total, InvoiceId;

-- U ovoj kopiji opseg uključuje 115 računa.

-- @block Vežba 1.1: Prikaži samo prvih pet, uz stabilan redosled
SELECT InvoiceId, BillingAddress, Total
FROM invoices
WHERE Total BETWEEN 5 AND 10
ORDER BY Total, InvoiceId
LIMIT 5;

-- LIMIT prikazuje samo pet od 115 redova koji ispunjavaju BETWEEN uslov.

-- @block Vežba 2: Proveri da li su obe granice uključene
SELECT
    5 BETWEEN 5 AND 10 AS lower_boundary_included,
    10 BETWEEN 5 AND 10 AS upper_boundary_included,
    4.99 BETWEEN 5 AND 10 AS just_below_range,
    10.01 BETWEEN 5 AND 10 AS just_above_range;

-- Očekivano: 1, 1, 0, 0. SQLite prikazuje TRUE/FALSE kao 1/0.

-- @block Vežba 3: Računi izvan opsega
SELECT COUNT(*) AS invoices_outside_range
FROM invoices
WHERE Total NOT BETWEEN 5 AND 10;

SELECT InvoiceId, Total
FROM invoices
WHERE Total NOT BETWEEN 5 AND 10
ORDER BY Total, InvoiceId
LIMIT 10;

-- NOT BETWEEN isključuje i same granice; za ovu NOT NULL kolonu ima 297 pogodaka.

-- @block Vežba 4: Opseg i dodatni uslov
SELECT InvoiceId, BillingCountry, Total
FROM invoices
WHERE (Total BETWEEN 5 AND 10)
  AND BillingCountry = 'USA'
ORDER BY Total, InvoiceId;

-- @block Vežba 5: Trajanje numera između 180000 i 240000 ms
SELECT TrackId, Name, Milliseconds
FROM tracks
WHERE Milliseconds BETWEEN 180000 AND 240000
ORDER BY Milliseconds, TrackId
LIMIT 10;

-- Obe granice trajanja su uključene.

-- @block Vežba 6: Ceo januar 2009. (poluotvoren opseg za timestamp)
SELECT InvoiceId, InvoiceDate
FROM invoices
WHERE InvoiceDate >= '2009-01-01 00:00:00'
  AND InvoiceDate <  '2009-02-01 00:00:00'
ORDER BY InvoiceDate, InvoiceId;

-- U ovoj kopiji januar 2009. sadrži 6 računa. Gornja granica je isključena,
-- pa su obuhvaćena sva vremena tokom 31. januara.

-- @block Ivični slučaj: Obrnut numerički opseg
SELECT COUNT(*) AS reversed_range_matches
FROM invoices
WHERE Total BETWEEN 10 AND 5;

-- Očekivano: 0 redova; nijedna obična numerička vrednost nije istovremeno >= 10 i <= 5.

-- @block Ivični slučaj: NULL ostaje UNKNOWN
SELECT
    NULL BETWEEN 1 AND 10 AS null_between,
    NULL NOT BETWEEN 1 AND 10 AS null_not_between;

-- Oba izraza vraćaju NULL, ne TRUE/FALSE. WHERE ne zadržava UNKNOWN.
