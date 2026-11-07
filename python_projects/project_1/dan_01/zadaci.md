# Dan 1: zadaci

Radi zadatke redom. Cilj nije da prepišeš ceo program, nego da razumeš po jedan
deo i proveriš ga pre nego što pređeš na sledeći.

## 1. Pokreni početni prozor

Iz korena repozitorijuma aktiviraj postojeće `.venv` okruženje, instaliraj
zavisnosti prema uputstvu iz glavnog `README.md` fajla i pokreni aplikaciju.

Proveri da li se otvara prozor sa naslovom „PDF Toolkit“ i porukom da je početni
prozor spreman.

## 2. Objasni početni kod

Pre nego što menjaš `app.py`, pokušaj svojim rečima da objasniš:

- Zašto `PdfToolkitApp` nasleđuje `ctk.CTk`?
- ODG: `PdfToolkitApp` nasleđuje `ctk.CTk` jer želi da koristi sve funkcionalnosti i izgled prilagođenog Tkinter prozora koji `ctk.CTk` pruža.
- Šta radi `super().__init__()`?
- ODG: `super().__init__()` poziva konstruktor roditeljske klase `ctk.CTk`, čime se inicijalizuje ceo prozor i sve njegove funkcionalnosti pre nego što se dodaju dodatni elementi specifični za `PdfToolkitApp`.
- Šta se podešava pozivima `title()`, `geometry()` i `minsize()`?
- ODG: `title()` postavlja naslov prozora, `geometry()` definiše početnu veličinu prozora, a `minsize()` postavlja minimalne dimenzije prozora ispod kojih korisnik ne može da ga smanji.
- Zašto se `mainloop()` poziva tek pošto je prozor napravljen?
- ODG: `mainloop()` pokreće glavnu petlju događaja Tkinter prozora, koja čeka i obrađuje korisničke akcije. Ako se pozove pre nego što je prozor potpuno napravljen, događaji ne bi mogli pravilno da se obrađuju i prozor možda ne bi bio prikazan ispravno.

Ne moraš imati savršene definicije. Važno je da otkriješ koji deo ti još nije
jasan.

## 3. Dodaj izbor PDF fajlova

- Dodaj dugme „Izaberi PDF-ove“.
- Poveži dugme sa metodom koja otvara dijalog za izbor više fajlova.
- Sačuvaj izabrane putanje u stanju aplikacije.
- Prikaži imena izabranih fajlova u prozoru.
- Proveri da otkazivanje dijaloga ne obriše prethodni izbor i ne sruši aplikaciju.

Za izbor koristi se dijalog iz `tkinter.filedialog`. Pokušaj prvo samostalno da
otkriješ potrebne argumente; ako zapneš, tražićemo ih zajedno.

## 4. Dodaj spajanje

- Dodaj dugme za spajanje izabranih fajlova.
- Omogući korisniku da izabere lokaciju i ime novog PDF fajla.
- Koristi `PdfWriter` i `append()` da dodaš izabrane fajlove redom.
- Sačuvaj rezultat u novi fajl, a ne preko jednog od ulaza.
- Prikaži poruku o uspešnom čuvanju.

## Provera završetka

Dan 1 je završen kada možeš da:

- pokreneš aplikaciju i objasniš šta radi `mainloop()`;
- izabereš najmanje dva PDF fajla;
- napraviš novi PDF čije su stranice spojene redom;
- potvrdiš da ulazni fajlovi nisu promenjeni;
- objasniš zašto se funkcija dugmetu prosleđuje bez zagrada.

Ako naiđeš na grešku, sačuvaj celu poruku i deo koda koji si poslednji menjao.
Rešićemo jednu stvar odjednom.
