# Kreiranje knjige i vraćanje odgovora u FastAPI

## U praksi je bolje da imas return

Ako u endpointu samo uradis append, a ne vratis nista:

1. klijent dobije null (ili prazan odgovor) umesto podataka o novoj knjizi
2. teze je odmah proveriti sta je kreirano
3. API je manje “standardan”

---

## Preporuka za create endpoint

1. dodaj status_code=201
2. vrati kreiranu knjigu

Primer ideje:

- kreiras knjigu
- dodelis id
- append
- return ta knjiga

To je najbolja praksa.
