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

1. Prema [ADR-0006](../adr/0006-choose-python-environment.md) dodaj
   `pyproject.toml`, `uv.lock` i paket `vfdebye` u mapi `src/`. CI pokreće numeričke provjere
   na Linuxu i Windowsu; provjeri rade li završna provjera i hookovi na Windowsu, gdje
   `python3` često ne postoji.
2. Prema AGENTS.md, odjeljak 5, u istoj promjeni dodaj `tools/check_project.py`, naredbe testova
   i statičke provjere te CI integraciju. Ukloni ostvarene stavke iz popisa `PLANNED` u
   `tools/check_docs.py`.
3. Odluka je u ADR-0006; provedbu opiši u [tijeku rada](../PIPELINE.md).

**Gotovo kada:** `python3 tools/check_before_stop.py` izvršava numeričke provjere umjesto NOT RUN,
a CI prolazi.

**Stanje 2026-11-09:** okruženje, `tools/check_project.py`, CI na Linuxu i Windowsu te poziv
hookova preko uv-a dodani su na grani `lovro/a1-okruzenje`. Zadatak je gotov kad CI prođe na oba
sustava i Sara pregleda PR.

## A2: tablica tkiva i model $H(s)$

**Cilj:** ponovljivo preuzimanje tablice i modul `vfdebye.gabriel`.

**Stanje 2026-11-09:** `data/README.md`, `data/fetch_gabriel.py`, `vfdebye.gabriel`, testovi i
experiments/data_checks.py dodani su na grani `lovro/a2-gabriel`. Zadatak je gotov kad Sara
pregleda PR. Točka 2 ima jedno pojašnjenje: član s $\Delta\varepsilon_n=0$ ne pridonosi modelu,
pa se za njega ne provjerava $0\le\alpha_n<1$ (zrak i vakuum imaju $\alpha_n=1$).

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

**Stanje 2026-11-23:** [izvod A3](../../izvodi/a3-problem-sk.md) pripremljen je na grani
`lovro/a3-izvod-vf`. Sadrži oba LS prikaza, razliku normalizacija i ručno riješen primjer
reda jedan. Preostaje Sarin neovisni pregled B9; zajednički prolaz nije zabilježen.

1. Permitivnost kao prijenosna funkcija realnog LTI SISO sustava; zašto su $\varepsilon_\infty$ i
   $\sigma_i/(s\varepsilon_0)$ izdvojeni; zašto Cole–Coleov član nije racionalan.
2. Problem (1.1) i zašto je nekonveksan.
3. Levyjeva linearizacija i SK iteracija (2.1); polinomni (2.2)–(2.3) i baricentrični
   (2.4)–(2.7) prikaz. Ručno postavi jedan problem najmanjih kvadrata reda 1 ili 2.

**Gotovo kada:** Sara je u B9 neovisno prošla izvod, a nejasnoće su zapisane.

## A4: jezgra VF-a

**Cilj:** `vfdebye.vf.vector_fit` prema sučelju iz podjele rada.

**Stanje 2026-11-09:** dijelovi koji ne ovise o B1 dodani su na grani `lovro/a4-model`:
`PoleResidueModel` (model iz sučelja, izračun u bilo kojim točkama, provjera realnosti i
stabilnosti), `matching_distance` (uparivanje skupova polova, (4.3)) i `detect_period`
(prepoznavanje kruženja, Primjer 4.2 i Napomena 4.3). Sama iteracija `vector_fit` čeka B1.

**Stanje 2026-11-23:** u A5 dodani su samostalni `barycentric_step`, `relocate_poles`,
`reflect_unstable_poles` i `fit_fixed_poles`, s realnim polovima i konjugiranim parovima,
provjerama ulaza i LS dijagnostikom. Puna petlja i odluke o zaustavljanju nisu implementirane;
ovisnost A4 o B1 ostaje.

**Stanje 2026-11-25:** nacrt pune petlje `vector_fit` objavljen je kao draft PR s grane
`lovro/a4-vf-petlja` i opisan u [A4](../../izvodi/a4-implementacija.md). Provjeren je na
sintetičkim sustavima poznatih polova, a A7 ga pokreće na razvojnim skupinama. Lovro je
2026-11-25 odlučio da A4 ne čeka usporedbu s B1; preostaje Sarin pregled.

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

**Stanje 2026-11-23:** [izvod A5](../../izvodi/a5-polovi-reziduali.md) i njegove numeričke
operacije pripremljeni su na grani `lovro/a5-polovi-reziduali`. Razjašnjen je predznak u
matrici premještanja, realna parametrizacija, refleksija i ograničenja kriterija. Testovi
koriste analitičke modele; nema konačnih rezultata na tkivima. Preostaje neovisni pregled B9.

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

**Stanje 2026-11-09:** modul, testovi i zapis podrijetla u experiments/data_checks.py dodani su na
grani `lovro/a6-podrijetlo`. Pojas, čvorove, težine, red i početne polove eksperiment predaje u
`settings`, a razlog zaustavljanja u `rec.update(stop_reason=...)`; njihov sadržaj određuju A4
i Z2. Zadatak je gotov kad Sara pregleda PR.

## A7: ponašanje iteracija i zaustavljanje

experiments/convergence.py na podskupu iz Z2: broj iteracija, kretanje polova, kruženje,
kriteriji (4.3)–(4.5) i osjetljivost na početne polove. Prikaži i neuspjehe.

Razvojne skupine i postavke prihvaćene su 2026-11-25 u
[ADR-0008](../adr/0008-accept-z2-experiment-plan.md).

**Stanje 2026-11-25:** pokretač i prvo razvojno pokretanje opisani su u
[zapisu A7](../../izvodi/a7-konvergencija.md). Preostaju odluka tima o primarnom rasponu
početnih polova, slika putanja za seminar i Sarin pregled.

## A8 i A10: seminar i slajdovi niti A

**Stanje 2026-11-23:** pripremljen je prvi teorijski LaTeX nacrt izvan repozitorija, za
Overleaf; sadržaj, provjera i primopredaja opisani su u [zapisu A8](../A8_NACRT.md).
Rezultati A7, Sarin pregled, zajednički prolaz i završno usklađivanje ostaju otvoreni.
Kompilaciju i izgled treba ponovno provjeriti kad ugrađeni kompajler može dohvatiti paket.

**Stanje 2026-11-25:** prvi nacrt iz 2026-11-23 nije dostupan na Lovrinu računalu, pa su
poglavlja niti A napisana ponovno, izvan repozitorija, kao dvije samostalne LaTeX datoteke za
Overleaf:

- **nit-a-poglavlja.tex** (10 stranica): problem i podaci, predmet aproksimacije, Levy i SK,
  polinomni i baricentrični prikaz s primjerom reda jedan, premještanje polova (lema o
  determinanti i predznak), apsorpcija težine, realnost, završni reziduali, zrcaljenje,
  algoritam i statusi te konvergencija s opažanjima A7 i primjerom krvi uz r = 7;
  SHA-256 `21607d645765e34f28e072bb553e5e226d09fe1d04b221da42d2ef57f3d7a05e`;
- **nit-a-slajdovi.tex** (A10, 13 slajdova, beamer): ista poglavlja;
  SHA-256 `53fd7f1e8cb8784ad4febd538e1c74a838344941046156f6c4371a984abadaf7`.

Slike `fig_putanja` i `fig_raspon` dolaze iz pokretanja
`20261125T162207467610Z-figures_a7`, koje čita lokalno ponovljeno A7 pokretanje
`20261125T161800716035Z-convergence` (revizija `4d744d1`, čisto stablo, sva tri raspona za
svaki r). Primjer krvi je iz `20261125T161808718583Z-z1_blood`. Ostale brojke A7 navode
pokretanja iz [zapisa A7](../../izvodi/a7-konvergencija.md). Oba dokumenta kompiliraju se
lokalnim pdflatexom bez grešaka i preljeva redaka.

Tekst nije prenesen u Overleaf i nije usklađen s poglavljima niti B. Sarin pregled i zajednički
prolaz nisu provedeni. Rezultate najmanjeg reda (B6) poglavlja niti A ne navode.

**Stanje 2026-11-26:** datoteke iz 2026-11-25 nisu sačuvane na Lovrinu računalu, pa su oba
dokumenta napisana ponovno, sa sadržajem istim kao gore. Spremljene su izvan repozitorija u
trajnu lokalnu mapu zajedno sa slikama `fig_putanja` i `fig_raspon` iz istog pokretanja:

- **nit-a-poglavlja.tex**, dodatno uz gore navedeno: tablica statusa zaustavljanja, tablica
  Debyejevih članova krvi uz r = 7 i pitanja za zajednički prolaz;
  SHA-256 `f389c24b6e73de78af147c4b6ab1d8ce74add1d48c5ba804d6e5577e9cd9079a`;
- **nit-a-slajdovi.tex** (A10, 13 slajdova, beamer);
  SHA-256 `4afddb30ac513769dc42b1260d7a858eb20768fa1aa576d60b1c47de3ad6f948`.

Na računalu nema LaTeX distribucije, pa nova inačica nije kompilirana. Provjereni su samo
parovi okruženja, zagrade, oznake i citati. Kompilaciju i izgled treba provjeriti u Overleafu.

**Stanje 2026-11-28:** u PDF-u zajedničkog Overleaf rukopisa od 2026-11-28 nalaze se poglavlja
2 (problem i podaci), 3 (racionalna aproksimacija i SK) i 6 (konvergencija). Odjeljci 5.2
(vector fitting, premještanje polova) i 8.1 (iteracije) bili su prazni, slika nije bilo, a
tridesetak referenci prikazivalo se kao „??”. Za oba odjeljka pripremljen je LaTeX izvan
repozitorija, u oznakama rukopisa (korak m, čvor k), zajedno s popisom ključeva i postojećih
„??” s predloženim ciljem:

- **005_SK_iter/vector-fitting.tex** (odjeljak 5.2): premještanje kao spektar Λ − φeᵀ,
  predznak, veza sa SK korakom, realnost, zrcaljenje, završni reziduali i algoritam; u
  zaglavlju je i popis postojećih „??”; SHA-256
  `7c26eaf8e51e9fae0cf21a41787ecf666c99cb4c5a588b5f15ed7c6a1be403b3`;
- **008_konvergencija/iteracije.tex** (zadnji odjeljak poglavlja Konvergencija, „Ponašanje
  iteracija na razvojnim skupinama”): brojke iz
  [zapisa A7, §7](../../izvodi/a7-konvergencija.md), slike i tablica Debyejevih članova krvi
  uz r = 7; SHA-256 `a09cd058dcdf640b0673429ef7aabc588318a2926e9c5f71860a627680bfaf99`;
- **008_konvergencija/fig_putanja.pdf** i **fig_raspon.pdf** iz pokretanja
  `20261128T144806878825Z-figures_a7`.

Putanje su one iz Overleaf projekta. Odjeljak o iteracijama premješten je iz poglavlja
Rezultati (prazni 8.1) u poglavlje o konvergenciji, koje je u niti A, kako ga je Lovro
2026-11-28 smjestio u Overleafu. Datoteke se uključuju naredbom `\input` (ne `\include`, koja
počinje novu stranicu): vector fitting u poglavlju Metode umjesto praznog 5.2, a iteracije na
kraju poglavlja Konvergencija; prazan 8.1 briše se. Ta je raspodjela provjerena prijevodom
probnog projekta s istim glavnim dokumentom i mapama.

Izvor je preveden lokalnim pdflatexom u probnom omotaču s lažnim oznakama za ključeve
rukopisa, bez grešaka i preljeva. Ključevi rukopisa nisu provjereni u Overleafu, a tekst
nije unesen u Overleaf. Sarin pregled i zajednički prolaz nisu provedeni, a slajdovi A10
nisu dio tog PDF-a.

Poglavlja: problem i podaci, model tkiva, izvod VF-a, premještanje polova, konvergencija. Svaki
broj i slika imaju identifikator pokretanja. Slajdovi prate ista poglavlja.

## A9: neovisna provjera izvoda niti B

Na papiru prođi Sarin izvod $\mathcal{H}_2$ norme, kvadrature i prilagodbe pojasu. Nejasnoće i
ishod zapiši u zadatak.

**Stanje 2026-11-25:** prema Lovrinoj izjavi provjera je provedena i izvod je ispravan.
Pojedinosti i eventualne napomene nisu zabilježene.
