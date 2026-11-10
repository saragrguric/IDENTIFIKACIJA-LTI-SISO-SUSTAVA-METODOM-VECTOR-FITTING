# Prijedlog odluka za sastanak Z0

**Pripremio:** Lovro, 2026-11-07 · **Status:** povijesni zapis; ishod sastanka je u nastavku.

## Ishod sastanka 2026-11-09

Lovro je 2026-11-09 prenio ishod sastanka. Sara potvrđuje prijedloge s ove stranice, uz ove
iznimke i dopune:

| # | Ishod | Zapis |
|---|---|---|
| 1 | Potvrđeno | ADR-0004 i ADR-0005, dodaci 2026-11-09 |
| 2 | Potvrđeno, uključujući naziv `vfdebye` | ADR-0005, dodatak 2026-11-09 |
| 3 | Prijedlog prihvaćen; Sara radi na Windowsu, Lovro na Linuxu, pa CI pokreće oba sustava | [ADR-0006](adr/0006-choose-python-environment.md) |
| 4 | Razine 5 %, 1 % i 0,1 %, zasebno za obje mjere; pojas privremeno 10 MHz–10 GHz do Z2 | ADR-0004, dodatak 2026-11-09 |
| 5 | Seminar i prezentaciju pišemo u Overleafu, izvan repozitorija | [zadaci](TASKS.md), T6 |
| 6 | Rok utvrđuje nastavnik; faze se raspoređuju kad ga znamo | otvoreno |
| 7 | Temu smatramo prihvatljivom; prethodnu potvrdu nastavnika ne tražimo | ADR-0004, dodatak 2026-11-09 |
| 8 | Potvrđeno: B1 nakon A1 | [podjela rada](PODJELA.md) |

Ostatak stranice je izvorni prijedlog i nije mijenjan.

Ova stranica priprema sastanak Z0 iz [podjele rada](PODJELA.md). Za svako otvoreno pitanje daje
konkretan prijedlog i obrazloženje, kako AGENTS.md traži prije odluke tima. Odluke sa sastanka
zapisujemo u zadatak Z0, a važne i u ADR. Nakon toga ova stranica postaje povijesni zapis
prijedloga.

Neki prijedlozi spominju Sarin probni pokus. On nije dio repozitorija i njegovi brojevi nisu
rezultati projekta; ovdje služe samo kao polazište.

## Sažetak: što treba odlučiti

| # | Pitanje | Prijedlog | Odlučuju |
|---|---|---|---|
| 1 | Tema, niti i osobni planovi | Potvrditi ADR-0004, ADR-0005 i planove; izmjene unijeti u jedan PR nakon Z0 | Sara potvrđuje |
| 2 | Zajednička sučelja | Potvrditi [sučelja](PODJELA.md#zajednička-sučelja) i naziv paketa `vfdebye` | oboje |
| 3 | Python okruženje | Python 3.12, `numpy`, `scipy`, `matplotlib`; razvojno `pytest` i `ruff`; `uv` i datoteka zaključanih verzija | oboje; provodi A1 |
| 4 | Pojas i razine točnosti | Privremeno 10 MHz–10 GHz i 5 %, 1 %, 0,1 %; konačno u Z2 | oboje |
| 5 | Seminar i prezentacija | Format otvoren; prijedlog LaTeX i Beamer, mjesto izvora dogovoriti | oboje |
| 6 | Rok i raspored faza | Kad znamo rok, faze rasporediti unatrag od njega | oboje |
| 7 | Prihvatljivost teme | Pitati nastavnika prije faze 1 | oboje |
| 8 | Sarin probni kod | Unijeti ga u repozitorij u B1, nakon A1 | Sara |

## 1. Tema, niti i osobni planovi

- Sara potvrđuje [ADR-0004](adr/0004-choose-debye-models-of-human-tissues.md),
  [ADR-0005](adr/0005-divide-work-into-end-to-end-threads.md) i [plan B](podjela/b-sara.md) ili
  traži izmjene. Lovro potvrđuje [plan A](podjela/a-lovro.md).
- PR-ovi #5 i #6 spojeni su bez Sarina pregleda (ADR-0002, dodatak 2026-11-07). Sara potvrđuje
  njihov sadržaj ovdje. Ako niti ne prođu, novi zapis zamjenjuje ADR-0005 i vraća podjelu po
  temama iz dodatka ADR-0001 od 2026-11-03.
- Sve izmjene sa sastanka unose se u jedan PR, koji pregledava drugi član.

## 2. Zajednička sučelja

Sučelja iz [podjele rada](PODJELA.md) predlažem potvrditi uz tri napomene:

1. **Granica između A4 i B3.** `vector_fit` prima čvorove $s$, vrijednosti $H(s)$ i težine.
   QuadVF ne treba vlastitu iteraciju, nego samo čvorove i težine iz `vfdebye.quadrature`. Tako
   postoji jedna implementacija VF-a, a razlika između VF-a i QuadVF-a je samo u ulazu.
2. **Težine.** U (1.1) težina množi kvadrat odstupanja, a u (3.3) i (3.6) množi rezidual
   (metodologija, odjeljak 2). Predlažem da `weights` množi rezidual, a da se to izričito navede u
   docstringu i testu.
3. **Relativne težine.** Sarin pokus koristi težine $1/\lvert\varepsilon\rvert$. To je izbor težina
   pozivatelja, a ne posebna inačica algoritma.

## 3. Python okruženje

| Što | Prijedlog | Zašto |
|---|---|---|
| Python | 3.12 | Aktualne verzije `numpy` i `scipy` |
| Ovisnosti | `numpy`, `scipy`, `matplotlib` | Linearna algebra, kvadratura za provjeru i slike; ništa više ne treba |
| Razvojne ovisnosti | `pytest`, `ruff` | Numerički testovi i statička provjera iz AGENTS.md, odjeljak 5 |
| Zaključavanje | `uv` i datoteka zaključanih verzija; CI instalira iz nje | Isti brojevi na oba računala; potrebno za Z4 |
| Testovi alata | ostaju `unittest` u `tools/` | Rade bez okruženja, kao i dosad |

Ništa od toga još nije instalirano ni razriješeno. Na sastanku svatko navede operacijski sustav i
ima li `uv`.

## 4. Pojas i razine točnosti

Sarin probni pokus koristio je 10 MHz–10 GHz. Prema stranici WebNIR, Gabrielov model pouzdan je
iznad 1 MHz; gornju granicu pouzdanosti treba provjeriti u izvješću. Predlažem taj pojas kao privremen za faze 1 i 2 te razine
točnosti 5 %, 1 % i 0,1 %. Konačni izbor, razvojni podskup tkiva i podskup za detaljnu analizu
dio su plana eksperimenata (Z2) i biraju se prije završnih pokretanja.

## 5. Seminar i prezentacija

Format nije odabran. Predlažem LaTeX za seminar i Beamer za prezentaciju, sa zajedničkim
makronaredbama za oznake i jednom bibliografijom. Treba odlučiti jesu li izvori u ovom
repozitoriju (planirane mape `seminar/` i `presentation/`) ili na drugom mjestu. Ako kolegij
propisuje predložak, opseg ili trajanje, to ima prednost.

## 6. Rok i raspored

Rok nije poznat. Kad ga dobijemo, faze rasporedimo unatrag od njega i unaprijed dogovorimo što se
reže ako ponestane vremena. Prijedlog redoslijeda rezanja:

1. **Prvo:** druga razina pojasa, RegVF i osjetljivost na početne polove.
2. **Zatim:** detaljna analiza svodi se na manji podskup tkiva.
3. **Ne reže se:** VF, QuadVF, referentna metoda, sva tkiva u zbirnoj tablici, obje mjere
   pogreške, izvodi niti A i B te reprodukcija u Z4.

## 7. Prihvatljivost teme

Fizika permitivnosti izvan je gradiva kolegija. Temu opravdavamo matematikom: aproksimacija
iracionalne prijenosne funkcije racionalnom, s mjerljivom globalnom pogreškom. Predlažem da to
pitamo nastavnika prije faze 1, uz jednu rečenicu o pitanju i podacima.

## 8. Sarin probni kod

Sara spominje kod koji radi, test-sustav i skriptu s matematikom. Prijedlog: B1 ih unosi u
repozitorij odmah nakon A1, prije nego Lovro počne A4, kako ne bismo dvaput pisali isto.

## Nakon sastanka

1. Odluke se zapisuju u zadatak Z0.
2. Lovro otvara PR s izmjenama podjele rada i planova.
3. Uz Lovrino ovlaštenje stvaraju se GitHub issuei za zadatke, oznake niti i milestonei faza.
4. Lovro počinje A1, a Sara B1 i B2.
