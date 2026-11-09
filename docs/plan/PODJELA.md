# Podjela rada: dvije niti

Tema je odabrana u [ADR-0004](adr/0004-choose-debye-models-of-human-tissues.md), a podjela na
niti predložena je u [ADR-0005](adr/0005-divide-work-into-end-to-end-threads.md). Ova stranica je
zajednički plan; detaljni koraci za svaku osobu nalaze se u osobnim planovima. Sadržaj planova je
prijedlog koji je napisao Lovro uz pomoć AI alata. PR #6 spojen je bez Sarina pregleda (ADR-0002,
dodatak 2026-11-07); Sara ih je potvrdila na sastanku Z0 2026-11-09 (ADR-0005, dodatak
2026-11-09). Rok utvrđuje nastavnik; dok ga ne znamo, faze nemaju datume.

## Tko je tko

| Osoba | Član | GitHub | Nit | Pregledava nit | Osobni plan |
|---|---|---|---|---|---|
| A | Lovro | `@LRazum` | A: od tablice do polova | B | [plan A](podjela/a-lovro.md) |
| B | Sara | `@saragrguric` | B: od polova do odgovora | A | [plan B](podjela/b-sara.md) |

Svaka nit ima nositelja, a ne vlasnika. Svatko radi matematiku, vodi AI alat pri pisanju koda i
testova, provodi eksperimente te piše svoj dio seminara i prezentacije. Na kraju svatko mora moći
objasniti cijeli projekt, a ne samo svoju nit.

## Što koja nit radi

| | A: Lovro | B: Sara |
|---|---|---|
| **Matematika** | Permitivnost kao prijenosna funkcija; Cole–Coleov i Debyejev član; izdvajanje $\varepsilon_\infty$ i $\sigma_i/(s\varepsilon_0)$. Problem (1.1), nekonveksnost, Levyjeva linearizacija, SK iteracija, polinomni i baricentrični prikaz (L1, §1–§2.1). Premještanje polova, reziduali, zrcaljenje (§2.2, §4.1). Konvergencija i kriteriji zaustavljanja (§4.2). Realnost polova i pozitivnost reziduala kao opažanje | Prostor $\mathcal{H}_2$, norma i uvjeti optimalnosti (§3.1). Primjer 3.1. Kvadratura (3.3)–(3.5) i QuadVF (3.6)–(3.7); prilagodba ograničenom pojasu i izostavljanje retka $M_+[H]$ kao naš odmak. Uvjetovanost i RegVF (§4.3). Referentna metoda s fiksnim polovima kao linearni problem najmanjih kvadrata |
| **Kod** | Okruženje i CI, `vfdebye.gabriel`, `vfdebye.vf`, `vfdebye.provenance` | `vfdebye.quadrature`, `vfdebye.baseline`, `vfdebye.metrics`, pokretači eksperimenata |
| **Eksperimenti** | Provjera podataka i jedinica; ponašanje iteracija, zaustavljanje i kruženje | Reprodukcija probnog pokusa; glavni eksperiment (najmanji $r$ po tkivu, metodi i točnosti); osjetljivost na $L$ i broj čvorova; uvjetovanost |
| **Seminar** | Problem i podaci, model tkiva, izvod VF-a, premještanje polova, konvergencija | $\mathcal{H}_2$ norma i kvadratura, QuadVF, plan eksperimenata, rezultati i rasprava |
| **Prezentacija** | Slajdovi za svoja poglavlja | Slajdovi za svoja poglavlja |

## Međusobni pregled

**Sara pregledava nit A, a Lovro nit B.** Recenzent niti:

1. pregledava njezine PR-ove: kod, testove i usklađenost dokumentacije;
2. neovisno na papiru izvodi njezine tvrdnje, a nejasnoće zapisuje u zadatak (A9 i B9);
3. objašnjava tu nit na zajedničkim prolazima, a nositelj ga dopunjuje;
4. reproducira njezine eksperimente u čistom okruženju (Z4).

`.github/CODEOWNERS` automatski traži pregled od recenzenta niti. Datoteke koje ne pripadaju
nijednoj niti traže pregled od oboje. Za spajanje vrijedi odobrenje drugog člana (ADR-0002).

## Zajednička sučelja

Potvrđeno na sastanku Z0 2026-11-09, uključujući naziv paketa `vfdebye`. Mijenja se samo
dogovorom, uz ažuriranje ove stranice i pogođenih testova.

```text
src/vfdebye/
  gabriel.py       A  tablica parametara, provjera ulaza, ε(s) i strogo pravi dio H(s)
  vf.py            A  VF: SK iteracija, premještanje polova, reziduali, zrcaljenje, povijest iteracija
  provenance.py    A  zapis podrijetla pokretanja
  quadrature.py    B  čvorovi i težine na pojasu, H2 norma na pojasu
  baseline.py      B  fiksni logaritamski polovi i reziduali najmanjim kvadratima
  metrics.py       B  najveća relativna pogreška, H2 pogreška na pojasu, najmanji r za točnost
tests/             test_<modul>.py uz svaki modul
experiments/
  data_checks.py   A  jedinice, kontrolne vrijednosti, pregled parametara α i τ
  convergence.py   A  ponašanje iteracija i kriteriji zaustavljanja
  pilot.py         B  reprodukcija probnog pokusa (krv i mišić)
  min_order.py     B  najmanji r po tkivu, metodi i točnosti
  sensitivity.py   B  osjetljivost na L i broj čvorova, uvjetovanost
data/              README s izvorom, uputama za preuzimanje i kontrolnim zbrojem; tablica izvan Gita
results/           odabrane tablice i slike; results/runs/ izvan Gita
```

Dogovori o podacima:

- **Frekvencija** je na sučelju `f` u Hz, a kompleksna varijabla je `s = 2j * pi * f`. Polovi
  $\lambda_j$ i reziduali $\phi_j$ zadani su u varijabli $s$, dakle u rad/s.
- **Permitivnost** je relativna i bezdimenzijska, tipa `complex128`, uz konvenciju
  $\varepsilon=\varepsilon'-\imath\varepsilon''$ i $\sigma=\omega\varepsilon_0\varepsilon''$ u S/m.
- **Parametri tkiva** nakon učitavanja imaju $\tau_n$ u sekundama. Tablica ih daje u ps, ns, µs i
  ms; pretvorba je u jednoj funkciji i ima test.
- **Model** je objekt s poljima `poles` i `residues` (i eventualno `d`), koji se računa u bilo
  kojem polju točaka. Realnost se provjerava: realni polovi s realnim rezidualima ili konjugirani
  parovi s konjugiranim rezidualima.
- **`vector_fit(s, h, weights, poles0, ...)`** vraća model i povijest iteracija: polove po
  iteraciji, rezidual najmanjih kvadrata, broj uvjetovanosti, zrcaljenja i razlog zaustavljanja.
  QuadVF poziva istu funkciju s čvorovima i težinama iz `vfdebye.quadrature`.
- **Nevaljan ulaz** (NaN, krivi oblici, negativne vrijednosti gdje nisu dopuštene, $r$ veći od
  broja uzoraka) izaziva `ValueError` s jasnom porukom. Ništa se ne popravlja prešutno.
- **Slučajnost** se ne očekuje. Ako zatreba, dolazi samo iz `numpy.random.default_rng(seed)`.
- **Svako pokretanje eksperimenta** zapisuje podrijetlo preko `vfdebye.provenance`
  (`with provenance.run(...) as rec`; opis u [tijeku rada](PIPELINE.md)).

## Faze i zadaci

Svaki zadatak postaje GitHub issue s oznakom niti (`nit:A`, `nit:B`, `nit:zajedničko`) i
milestoneom faze tek nakon potvrde na Z0. Do tada zadatke pratimo po kodovima.

| Faza | Završava | Zadaci |
|---|---|---|
| **0: dogovor** | Potvrđena tema, niti i sučelja; radi okruženje | Z0, A1 |
| **1: temelji i prvi model** | Prolazom 1: VF model jednog tkiva uz izmjerenu pogrešku | A2, A3, A4, B1, B2, B3, B4, Z1 |
| **2: QuadVF i plan eksperimenata** | Zapisanim planom eksperimenata i prolazom 2 | A5, A6, A9, B5, B9, Z2, Z3 |
| **3: svi rezultati i nacrti** | Svim rezultatima i nacrtima poglavlja | A7, A8, B6, B7, B8 |
| **4: reprodukcija i probna obrana** | Reproduciranim rezultatima i probnom obranom | A10, B10, Z4, Z5, Z6 |

Najvažnije ovisnosti:

- okruženje A1 prethodi spajanju svakog koda;
- Sarin probni kod (B1) ulazi u repozitorij nakon A1, a njegovi dijelovi prelaze u A4 i B3;
- prolaz Z1 traži model tkiva (A2), jezgru VF-a (A4) i mjere pogreške (B4);
- QuadVF (B5) traži kvadraturu (B3) i jezgru VF-a (A4);
- glavni eksperiment B6 pokreće se tek nakon zapisanog plana eksperimenata (Z2).

## Zajednički zadaci

### Z0: dogovor

Sudjeluju oboje. Prijedlozi odluka nalaze se u [prijedlogu za Z0](Z0_PRIJEDLOG.md).

Sastanak je održan 2026-11-09; ishod je zapisan u [prijedlogu za Z0](Z0_PRIJEDLOG.md#ishod-sastanka-2026-11-09).

- [x] Sara potvrđuje ADR-0004, ADR-0005 i svoj plan ili traži izmjene.
- [x] Potvrditi zajednička sučelja s ove stranice ili ih izmijeniti.
- [x] Dogovoriti Python ovisnosti; A1 ih zatim provodi (ADR-0006).
- [x] Dogovoriti format seminara i prezentacije: pišemo ih u Overleafu, izvan repozitorija.
- [x] Odrediti razine točnosti (ADR-0004, dodatak 2026-11-09).
- [ ] Rok utvrđuje nastavnik; zatim rasporediti faze unatrag od njega.
- [ ] Svatko lokalno: klonirati repozitorij, pokrenuti `python3 tools/check_before_stop.py` i
  provjeriti povjerenje hookovima (vidi [tijek rada](PIPELINE.md)).

### Z1: prolaz 1, prvi VF model jednog tkiva

Lovro pokazuje kako se iz tablice dobiva $H(s)$ za krv i kako VF dolazi do polova. Sara na tom
modelu mjeri najveću relativnu i $\mathcal{H}_2$ pogrešku na pojasu. Nit A objašnjava Sara, a nit
B Lovro. Pitanja, nejasnoće i tko je stvarno sudjelovao zapisujemo u zadatak.

### Z2: plan eksperimenata prije završnih pokretanja

Nositeljica je Sara, a sudjeluju oboje. To je zadatak T3 iz [popisa zadataka](TASKS.md).

- Hipoteze se zapisuju prije završnih rezultata, npr.:
  - VF treba manje polova od fiksnih logaritamskih polova za istu točnost kod većine tkiva;
  - QuadVF ne treba više polova od VF-a s logaritamskim čvorovima;
  - tkiva s većim $\alpha_n$ u pojasu trebaju više polova.
- Odabrati konačni pojas, razvojni podskup tkiva, podskup za detaljnu analizu, broj
  čvorova, raspon za $L$, početne polove, kriterij zaustavljanja i računalni proračun. Važne
  izbore zabilježiti u ADR-u i [metodologiji](METHODOLOGY.md).

### Z3: prolaz 2, cijeli lanac na razvojnom podskupu

Od tablice do tablice „tkivo, najmanji $r$, metoda” na razvojnom podskupu. Nit ponovno objašnjava
njezin recenzent. Svatko pokrene cijeli lanac na svom računalu.

### Z4: reprodukcija u čistom okruženju

Sara reproducira eksperimente niti A, a Lovro eksperimente niti B: čist klon, instalacija iz
zaključanih ovisnosti, ponovno pokretanje i usporedba brojeva. Razlike i neuspjehe zapisujemo.

### Z5: uvod, zaključak i usklađivanje oznaka

Zajedno pišemo uvod i zaključak seminara. Provjeravamo da seminar, slajdovi i kod koriste iste
oznake, parametre i brojeve te da svaka slika i tablica ima identifikator pokretanja.

### Z6: prolaz 3, probna obrana

Svatko izlaže dio koji nije vodio i odgovara na pitanja iz tuđe niti. Praznine zapisujemo i zatim
ih ponovno obrađujemo.

## Kako se radi na zadatku

1. Napiši u zadatku da počinješ.
2. Napravi granu iz svježeg `main`:

   ```bash
   git switch main && git pull && git switch -c sara/b3-kvadratura
   ```

   Prefiks je ime člana, a ne slovo niti.
3. Radi u malim commitovima s porukama na hrvatskom, npr. `kvadratura: dodaj čvorove na pojasu`.
4. Prije PR-a lokalno pokreni `uv run --no-project python tools/check_before_stop.py` (na Linuxu može i
   `python3 tools/check_before_stop.py`).
5. Otvori PR prema predlošku. Ako zadatak ima issue, u opisu napiši `Closes #N`. GitHub
   automatski traži pregled od recenzenta niti, a spajanje je moguće tek nakon odobrenja drugog
   člana i uspješnog CI-ja.
6. Pitanja i blokade piši u komentare zadatka. Provjeren problem prijavi predloškom „Nalaz”
   (vidi [pregled i nalaze](AI_REVIEW.md)).

## Što je automatizirano na GitHubu

- **CI** na svakom PR-u i pushu na `main`, na Linuxu i Windowsu: provjera dokumentacije, testovi
  alata i numeričke provjere (`pytest` i `ruff`).
- **Dnevna provjera** prijavljuje pad CI-ja, konflikte, zastarjele PR-ove i spajanja bez pregleda.
- **`.github/CODEOWNERS`** automatski traži pregled od recenzenta niti.
- **Predlošci issuea** „Zadatak” i „Nalaz” te predložak PR-a.

Zaštitu grane `main`, oznake niti, issuee i milestoneove treba postaviti na GitHubu; samo
dodavanje datoteka to ne čini. Nijedna automatizacija ne može potvrditi da netko razumije gradivo;
to provjeravamo na prolazima.
