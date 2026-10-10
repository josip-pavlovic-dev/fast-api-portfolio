# 01: Pojam transakcije i ACID

## Šta je transakcija?

Transakcija je logička celina rada sa bazom. Ona obuhvata jednu ili više SQL naredbi koje zajedno čine jednu promenu poslovnog stanja.

Primer: prenos 30 jedinica novca sa jednog računa na drugi zahteva najmanje dve promene:

1. umanji stanje prvog računa za 30;
2. uvećaj stanje drugog računa za 30.

Ako se izvrši samo prvi korak, novac je nestao sa prvog računa, ali se nije pojavio na drugom. Zato oba koraka treba da pripadaju istoj transakciji: ili se oba potvrde, ili se nepotvrđene promene ponište.

Transakcija nije isto što i jedan SQL iskaz. Jedna transakcija može sadržati više iskaza, a baza obično upravlja i transakcijskim kontekstom oko čitanja.

## Granice transakcije

Pojednostavljeni životni ciklus je:

```text
početak transakcije
    -> izvrši jedan ili više SQL iskaza
    -> COMMIT  (potvrdi promene)
       ili
    -> ROLLBACK (poništi nepotvrđene promene)
```

Dok transakcija nije potvrđena, upisane promene su nepotvrđene. One mogu biti vidljive konekciji koja ih je napravila, ali ne treba pretpostaviti da su trajne ili vidljive drugim konekcijama.

- `COMMIT` kaže bazi da potvrdi uspešnu transakciju.
- `ROLLBACK` traži da baza poništi promene trenutne nepotvrđene transakcije.
- Zatvaranje konekcije ili ORM sesije nije komanda za potvrdu. Nepotvrđene promene se obično poništavaju tokom čišćenja resursa.

Tačni detalji vidljivosti i trajnosti zavise od baze i podešavanja. Za osnovne primere najvažnije je jasno označiti gde posao počinje i gde se uspeh potvrđuje.

## Zašto ne potvrditi svaku naredbu zasebno?

Pretpostavimo da aplikacija pravi porudžbinu i njene stavke. Ako se porudžbina upiše, a upis druge stavke padne, stanje može ostati nepotpuno ako su raniji koraci već potvrđeni.

Transakcija grupiše povezane izmene:

```text
BEGIN
    INSERT porudžbina
    INSERT stavka 1
    INSERT stavka 2
COMMIT
```

Ako drugi INSERT izazove grešku koja prekida transakcioni blok:

```text
BEGIN
    INSERT porudžbina
    INSERT stavka 1
    INSERT stavka 2 -> greška
ROLLBACK
```

Cilj je da se izbegne polovično stanje. Sama transakcija, međutim, ne zna poslovno pravilo: aplikacija mora odlučiti koje naredbe pripadaju istoj celini i kada je posao uspešan.

## ACID — četiri osobine transakcije

ACID je skraćenica za osobine koje relaciona baza nastoji da pruži transakcijama. Konkretne garancije i konfiguracija razlikuju se među bazama.

### Atomicity — atomičnost

Transakcija se posmatra kao celina: izmene se potvrđuju zajedno ili se nepotvrđene izmene poništavaju. U primeru prenosa, ne želimo da se potvrdi samo skidanje novca, a da dodavanje novca ne uspe.

Atomičnost se odnosi na promene unutar transakcije. Ako aplikacija napravi dve zasebne transakcije i potvrdi prvu, kasniji rollback druge ne može poništiti već potvrđenu prvu.

### Consistency — konzistentnost

Uspešna transakcija treba da ostavi bazu u stanju koje poštuje njena pravila: ograničenja kao što su `NOT NULL`, `UNIQUE`, primarni/strani ključevi i poslovna pravila koja aplikacija proverava.

Baza ne može automatski pogoditi sva poslovna pravila. Na primer, ako stanje računa ne sme biti negativno, to pravilo mora biti sprovedeno odgovarajućom logikom ili constraint-om, a ne samo time što koristimo transakciju.

### Isolation — izolacija

Izolacija uređuje kako se istovremene transakcije međusobno ponašaju i koje promene mogu da vide. To je važno kada više korisnika ili procesa u isto vreme čita i menja podatke.

Za početak zapamti da izolacija nije sinonim za atomicity i ne znači nužno da se transakcije izvršavaju jedna po jedna. Baze nude različite izolacione nivoe i pravila zaključavanja; to je napredna tema koju ovde ne obrađujemo.

### Durability — trajnost

Kada baza uspešno potvrdi `COMMIT`, promene treba da ostanu sačuvane i posle završetka transakcije. Stvarna trajnost zavisi od baze, njenog storage-a i konfiguracije.

## Transakcija, konekcija i SQL iskaz nisu isto

| Pojam       | Uloga                                                                   |
| ----------- | ----------------------------------------------------------------------- |
| SQL iskaz   | Jedna naredba, na primer `INSERT` ili `SELECT`.                         |
| Konekcija   | Kanal/objekat preko kog aplikacija razgovara sa bazom.                  |
| Transakcija | Granica koja određuje koje se izmene potvrđuju ili poništavaju zajedno. |

Jedna konekcija može izvršiti više transakcija redom. Jedna transakcija može sadržati više SQL iskaza.

## Važna granica

Ova osnova objašnjava jednu vezu aplikacije sa bazom. Ne obrađuje još:

- šta se dešava kada dve transakcije istovremeno menjaju isti red;
- isolation level-e kao `READ COMMITTED` ili `SERIALIZABLE`;
- savepoint-e i ugnježdene transakcije;
- distribuirane transakcije kroz više baza/servisa.

Za početak treba umeti da kažeš: „Ove promene pripadaju zajedno; potvrdiću ih tek kada je ceo posao uspeo.“
