# 06 - Update/Delete i transakcije u 2.0 toku

## Update obrazac koji vec radis

Tvoj pristup (ucitaj model -> menjaj polja -> commit) ostaje odlican i u 2.0.

Primer:

1. ucitaj record,
2. setuj nova polja,
3. `db.commit()`.

## Delete obrazac

Isto vazi:

1. ucitaj record uz ownership proveru,
2. `db.delete(record)`,
3. `db.commit()`.

## Kada koristiti rollback

Ako dodajes `try/except` za DB greske:

1. u `except` uradi `db.rollback()`,
2. zatim podigni HTTPException ili domain gresku.

## Bitna poenta

SQLAlchemy 2.0 menja stil pisanja upita, ali ne menja osnovni transakcioni princip koji vec primenjujes.
