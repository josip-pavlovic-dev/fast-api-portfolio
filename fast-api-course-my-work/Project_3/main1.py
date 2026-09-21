from typing import Annotated

from fastapi import Depends, FastAPI
from sqlalchemy.orm import Session

import models
from models import Todos
from database import SessionLocal, engine



app = FastAPI()

models.Base.metadata.create_all(
    bind=engine
)  # Izvršava kreiranje svih tabela definisanih u ORM modelima samo ako one još ne postoje u bazi. Ako postoje linija koda se ne izvršava.


def get_db():
    db = SessionLocal()  # Kreira novu sesiju za rad sa bazom podataka
    try:
        yield db  # Prvo se vraća sesija za korišćenje u endpoint-u, a kada se završi request, šalje se response u vidu JSON-a, izvršava se finally blok i sesija se zatvara. Na taj način se otvara konekcija ka bazi samo za trajanje jednog HTTP zahteva i odmah se zatvara nakon što je request obrađen.
    finally:
        db.close()


# Funkcija get_db() se koristi kao dependency u FastAPI endpoint-ima kako bi se obezbedila sesija za rad sa bazom podataka.

# Šta je Depends, a šta dependency injection?
# get_db je dependency funkcija: ona sadrži kod potreban za pripremu resursa
# Te resurse endpoint koristi, u ovom slučaju za kreiranje i zatvaranje DB sesije.

# Depends(get_db) govori FastAPI-ju da endpoint zavisi od funkcije get_db.
# FastAPI tada automatski poziva get_db, uzima vrednost koju generator daje pomoću yield-a i tu vrednost ubacuje u parametar db endpointa.

# To automatsko izvršavanje dependency funkcije i ubacivanje njenog rezultata u endpoint jeste dependency injection. Mi pišemo dependency funkciju inavodimo je kroz Depends, a FastAPI obavlja povezivanje iza scene.

db_dependency = Annotated[Session, Depends(get_db)] # Definiše tip anotaciju za dependency injection u FastAPI endpoint-ima.
@app.get("/")
async def read_all(db: db_dependency):
    return db.query(Todos).all() # Čita sve zapise iz tabele "todos" u bazi podataka.

# db.query(Todos).all(), napišemo query (skriptu namenjenu našoj bazi podataka, SQL upit) u kojem tražimo sve zapise iz tabele "todos".
