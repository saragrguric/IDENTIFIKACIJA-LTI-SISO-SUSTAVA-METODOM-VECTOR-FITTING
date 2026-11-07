# Plan osobe A: Lovro, nit „od tablice do polova”

Zajednička pravila, sučelja i faze opisani su u [podjeli rada](../PODJELA.md). Ovaj plan je
prijedlog; promijeni ga u PR-u ili zadatku ako nešto ne odgovara.

## Ukratko

Tvoja nit pretvara redak Gabrielove tablice u prijenosnu funkciju $H(s)$ i iz njezinih uzoraka
VF-om dobiva polove i reziduale. Bez nje nit B nema ni model tkiva ni algoritam koji uspoređuje.

- **Matematika:** permitivnost kao prijenosna funkcija; Cole–Coleov i Debyejev član; problem
  (1.1), linearizacija, SK iteracija, baricentrični prikaz, premještanje polova, reziduali,
  zrcaljenje i konvergencija (L1, §1–§2, §4.1–§4.2).
- **Kod:** okruženje i CI, `vfdebye.gabriel`, `vfdebye.vf` i `vfdebye.provenance`, svaki s
  testovima.
- **Eksperimenti:** provjera podataka i jedinica; ponašanje iteracija i zaustavljanje.
- **Seminar i prezentacija:** problem i podaci, model tkiva, izvod VF-a, premještanje polova i
  konvergencija.
- **Pregled:** pregledavaš Sarinu nit B (PR-ovi, neovisna provjera izvoda u B9 i reprodukcija u
  Z4) i na prolazima objašnjavaš nit B. Tvoju nit pregledava Sara.

## Redoslijed

| Faza | Zadatak | Ovisi o | Tko čeka tebe |
|---|---|---|---|
| 0 | Z0 dogovor | — | oboje |
| 0 | A1 okruženje i CI | Z0 | svaki kod |
| 1 | A2 tablica tkiva i model $H(s)$ | A1 | Z1, B4, B5 |
| 1 | A3 matematika: problem, linearizacija, SK, baricentrični prikaz | Z0 | B9, A8 |
| 1 | A4 jezgra VF-a | A1, B1 | Z1, B5 |
| 2 | A5 matematika: premještanje polova, reziduali, zrcaljenje | A3 | B9, A8 |
| 2 | A6 zapis podrijetla | A1 | B5, B6 |
| 2 | A9 neovisna provjera izvoda niti B | B2 | Z3 |
| 3 | A7 ponašanje iteracija i zaustavljanje | A4, A6, Z2 | A8 |
| 3 | A8 seminar: poglavlja niti A | A3–A7 | Z5 |
| 4 | A10 slajdovi niti A | A8 | Z6 |

Ako te nešto blokira, počni sljedeći zadatak koji ne ovisi o blokadi. A3 možeš početi odmah nakon
Z0.

## A1: okruženje i CI

**Cilj:** dogovoreno Python okruženje sa zaključanim verzijama i numeričkim provjerama u CI-ju.

1. Prema odluci sa Z0 dodaj `pyproject.toml`, datoteku zaključanih verzija i paket
   `vfdebye` u mapi `src/`.
2. Prema AGENTS.md, odjeljak 5, u istoj promjeni dodaj `tools/check_project.py`, naredbe testova
   i statičke provjere te CI integraciju. Ukloni ostvarene stavke iz popisa `PLANNED` u
   `tools/check_docs.py`.
3. Zabilježi odluku o okruženju u novom ADR-u i u [tijeku rada](../PIPELINE.md).

**Gotovo kada:** `python3 tools/check_before_stop.py` izvršava numeričke provjere umjesto NOT RUN,
a CI prolazi.

## A2: tablica tkiva i model $H(s)$

**Cilj:** ponovljivo preuzimanje tablice i modul `vfdebye.gabriel`.

1. U data/README.md zapiši izvor (izvješće AL/OE-TR-1996-0037 i prijepis na WebNIR-u), licencu,
   datum pristupa, upute za preuzimanje i kontrolni zbroj. Tablica ostaje izvan Gita.
2. Učitaj svih 57 redaka. Pretvori $\tau_n$ u sekunde. Provjeri konačnost, predznake i
   $0\le\alpha_n<1$; nevaljan redak izaziva `ValueError`.
3. Označi retke koji ponavljaju parametre drugog tkiva te zrak i vakuum, ali ih ne briši.
4. Funkcije: $\varepsilon(s)$, točni članovi $\varepsilon_\infty$ i $\sigma_i/(s\varepsilon_0)$ te
   strogo pravi dio $H(s)$.
5. Testovi:
   - pretvorba jedinica za $\tau_n$;
   - kontrolne vrijednosti na 900 MHz za krv i mišić iz tablice, uz izvor tih vrijednosti;
   - $H(\overline{s})=\overline{H(s)}$;
   - za umjetni redak sa svim $\alpha_n=0$ vrijednost $H$ jednaka je zbroju Debyejevih članova.
6. experiments/data_checks.py: pregled raspona $\alpha_n$, $\tau_n$ i $\Delta\varepsilon_n$ po
   tkivu i usporedba s pojasom.

**Gotovo kada:** testovi prolaze, a data/README.md omogućuje drugoj osobi da dobije istu
tablicu.

## A3: matematika VF-a, prvi dio

**Cilj:** čitljiv izvod s pretpostavkama, prema [metodologiji](../METHODOLOGY.md), odjeljci 1–2.

1. Permitivnost kao prijenosna funkcija realnog LTI SISO sustava; zašto su $\varepsilon_\infty$ i
   $\sigma_i/(s\varepsilon_0)$ izdvojeni; zašto Cole–Coleov član nije racionalan.
2. Problem (1.1) i zašto je nekonveksan.
3. Levyjeva linearizacija i SK iteracija (2.1); polinomni (2.2)–(2.3) i baricentrični
   (2.4)–(2.7) prikaz. Ručno postavi jedan problem najmanjih kvadrata reda 1 ili 2.

**Gotovo kada:** Sara je u B9 neovisno prošla izvod, a nejasnoće su zapisane.

## A4: jezgra VF-a

**Cilj:** `vfdebye.vf.vector_fit` prema sučelju iz podjele rada.

1. Pregledaj Sarin probni kod iz B1 i odluči što od njega preuzimaš.
2. SK iteracija u baricentričnom obliku s težinama, premještanje polova (2.9)–(2.12), završna
   identifikacija reziduala, zrcaljenje nestabilnih polova (L1, §4.1).
3. Povijest iteracija: polovi, rezidual najmanjih kvadrata, broj uvjetovanosti, zrcaljenja i
   razlog zaustavljanja. Kruženje i nekonvergencija prijavljuju se, a ne skrivaju.
4. Testovi:
   - oporavak racionalne funkcije poznatih realnih polova i reziduala iz točnih uzoraka;
   - isto za konjugirani par;
   - polovi se uspoređuju uparivanjem, a ne poretkom;
   - zrcaljenje na umjetnom nestabilnom početnom polu;
   - čvor jednak polu i bliski polovi;
   - nevaljan ulaz.

**Gotovo kada:** testovi prolaze, a Sara je pregledala PR.

## A5: matematika VF-a, drugi dio

1. Izvedi premještanje polova (2.9)–(2.12) i identifikaciju reziduala.
2. Propozicija 4.1 i zrcaljenje.
3. Konvergencija: što L1 tvrdi, a što ostavlja otvorenim (§2.2, §4.2); kriteriji (4.3)–(4.5);
   Primjer 4.2.
4. Realnost polova i pozitivnost reziduala: navedi ih kao opažanje iz eksperimenata. Ako želimo
   tvrdnju, prvo predloži izvor za literaturu.

## A6: zapis podrijetla

Modul `vfdebye.provenance` prema [tijeku rada](../PIPELINE.md), odjeljak o podrijetlu: revizija
koda i necommitirane promjene, okruženje, kontrolni zbroj tablice, pojas, čvorovi i težine, red,
početni polovi, postavke i razlog zaustavljanja.

## A7: ponašanje iteracija i zaustavljanje

experiments/convergence.py na podskupu iz Z2: broj iteracija, kretanje polova, kruženje,
kriteriji (4.3)–(4.5) i osjetljivost na početne polove. Prikaži i neuspjehe.

## A8 i A10: seminar i slajdovi niti A

Poglavlja: problem i podaci, model tkiva, izvod VF-a, premještanje polova, konvergencija. Svaki
broj i slika imaju identifikator pokretanja. Slajdovi prate ista poglavlja.

## A9: neovisna provjera izvoda niti B

Na papiru prođi Sarin izvod $\mathcal{H}_2$ norme, kvadrature i prilagodbe pojasu. Nejasnoće i
ishod zapiši u zadatak.
