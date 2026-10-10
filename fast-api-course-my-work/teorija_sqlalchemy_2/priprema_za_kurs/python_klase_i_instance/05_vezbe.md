# 05: Vežbe — klase, instance, SQLAlchemy i FastAPI

Pokušaj vežbe bez otvaranja [rešenja](06_resenja.md). Vežbe idu od obične Python klase ka deklarativnom SQLAlchemy modelu i FastAPI/Pydantic ugovoru. Nije potrebno praviti tabelu, slati SQL ili pisati transakcije.

## Vežba 1: klasa i dve instance

Napravi klasu `Book` sa konstruktorom koji prima `title` i `pages`. Sačuvaj ih kao instance atribute. Napravi dve instance i ispiši njihove naslove i broj strana.

Provera razumevanja: da li promena `pages` prve knjige menja drugu knjigu?

## Vežba 2: `self` i metoda

U `Book` dodaj metodu `description()` koja vraća tekst oblika `Naslov (N strana)`. Pozovi je preko instance. Objasni koji objekat Python prosleđuje kao `self`.

## Vežba 3: identitet i jednakost

Napravi dve različite instance sa istim podacima, pa napravi i drugu promenljivu koja pokazuje na prvu instancu.

Proveri `is` i `==`. Pre nego što pokreneš kod, predvidi rezultat i objasni zašto.

## Vežba 4: atribut klase naspram instance

Dodaj klasi `Product` atribut klase `currency = "RSD"`, a svakom proizvodu instance atribute `name` i `price`. Promeni `currency` samo na jednoj instanci.

Odredi vrednosti `first.currency`, `second.currency` i `Product.currency`. Zatim objasni zašto mutable atribut klase, na primer `items = []`, može biti opasan.

## Vežba 5: nasleđivanje

Napravi baznu klasu `Person` sa `name` atributom i metodom `introduce()`. Napravi `Student(Person)` koji dodaje `course`. Pozovi `super().__init__(name)` i koristi nasleđenu metodu na studentu.

## Vežba 6: deklarativni ORM model

Napravi `Base(DeclarativeBase)` i ORM klasu `User` sa `id`, `name` i opcionim `fullname` poljima. Nemoj kreirati engine ni tabelu.

Proveri:

- `User` je klasa, a `user = User(name="sandy")` je instanca;
- `User.__tablename__` je naziv SQL tabele;
- `User.__table__` je SQLAlchemy `Table` metadata objekat;
- `Base.metadata.tables` sadrži tabelu;
- `User.name` i `user.name` imaju različite uloge.

## Vežba 7: ORM atribut i kolona

Za `User.name` zapiši:

1. šta predstavlja na nivou klase;
2. šta vraća `user.name` na instanci;
3. kako `select(User.name)` koristi class-level atribut;
4. zašto `Mapped[str]` nije isto što i SQLAlchemy tip `String(80)`.

## Vežba 8: strani ključ i relationship atribut

Dodaj model `Address` sa `email_address` kolonom i obaveznim `user_id` FK-om ka `user_account.id`. Zatim opiši razliku između `address.user_id` i ORM atributa `address.user` koji bi se definisao sa `relationship()`.

Ne dodaj cascade, deletion pravila ili relationship konfiguraciju; zadatak je samo da prepoznaš ulogu atributa.

## Vežba 9: Pydantic zahtev i FastAPI ruta

Napravi Pydantic klasu `ItemCreate` sa obaveznim `name` i opcionim `description`. Napravi FastAPI endpoint koji prima `payload: ItemCreate` i vraća dictionary sa vrednostima zahteva.

Objasni zašto je `payload` instanca `ItemCreate`, a ne sama klasa i ne običan Python dictionary.

## Vežba 10: ORM objekat i izlazna šema

Napravi SQLAlchemy `Item` klasu i Pydantic `ItemOut` klasu sa `id`, `name` i `description`. Uključi `ConfigDict(from_attributes=True)`, napravi ORM instancu sa primer ID-jem i pretvori je u Pydantic model koristeći `ItemOut.model_validate(item)`.

Objasni zašto rezultat nije ista instanca i zašto `Item` nije Pydantic šema.

## Završna provera

Bez gledanja koda odgovori svojim rečima:

1. Šta se razlikuje između klase i instance?
2. Šta `self` označava?
3. Šta SQLAlchemy zaključuje iz `Mapped[str]`?
4. Koja je razlika između `User.name` i `user.name`?
5. Po čemu se ORM model razlikuje od Pydantic modela?
6. Koju klasu i koju instancu FastAPI koristi za telo zahteva?
