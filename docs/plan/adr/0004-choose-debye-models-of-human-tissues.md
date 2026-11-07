# ADR-0004: Primijeniti VF i QuadVF na Debyejeve modele ljudskih tkiva

**Datum:** 2026-11-07 · **Status:** prihvaćeno (Lovro i Sara prema Lovrinoj izjavi, 2026-11-07)

## Kontekst

ADR-0001 ostavio je otvorenima primjenu, podatke, inačicu metode i uzorkovanje.
[Prijedlog tema](../prijedlog-tema/prijedlog-tema-vf.pdf) od 2026-11-07 usporedio je HRTF-ove,
impedancijske spektre litij-ionskih ćelija i FRF-ove kompozitne ploče. Lovro je zatim zatražio
matematički lakšu temu od HRTF-a koja ispunjava iste uvjete. U razgovoru su predložena još dva
kandidata: toplinski model višeslojnog zida i Debyejevi modeli ljudskih tkiva. Ni jedan od njih
nije u PDF-u prijedloga.

Sara je za temu tkiva napravila probni pokus vlastitim kodom na krvi i mišiću i opisala ga u
dokumentu „Prijedlog teme projekta: Debyejevi modeli ljudskih tkiva”. Dokument, kod i rezultati
nisu u repozitoriju, pa njihovi brojevi nisu rezultati projekta. Lovro je 2026-11-07 prenio
Sarinu poruku u kojoj temu ocjenjuje dobrom, uz uvjet da se tablica parametara može nabaviti, i
naveo da se oboje slažu s temom. PR #6, koji uvodi ovaj zapis, spojen je bez Sarina pregleda
(ADR-0002, dodatak 2026-11-07). Sara zapis potvrđuje na sastanku Z0 ili traži izmjenu novim
PR-om.

Isti je dan provjerena tablica parametara na stranici WebNIR (CNR-IFAC). Ona prenosi izvješće
C. Gabriel i S. Gabriel, *Compilation of the dielectric properties of body tissues at RF and
microwave frequencies*, Armstrong Laboratory, AL/OE-TR-1996-0037, 1996. Izvješće je označeno
„Approved for public release, distribution unlimited” (DTIC AD-A305826). Stranica WebNIR
objavljena je pod CC BY-NC-SA 4.0. Tablica ima 57 redaka: 44 tipa tkiva iz izvješća, unose koji
ponavljaju parametre postojećeg tkiva te zrak i vakuum bez disperzije. Prema stranici, model je
pouzdan iznad 1 MHz. Iz redaka za krv i mišić ponovno su izračunate Sarine kontrolne vrijednosti
na 900 MHz (krv $\varepsilon'=61{,}36$, $\sigma=1{,}538$ S/m; mišić $\varepsilon'=55{,}03$,
$\sigma=0{,}943$ S/m). To je provjera prijepisa tablice, a ne rezultat projekta.

## Odluka

1. **Pitanje.** Koliko je najmanje realnih polova (Debyejevih članova) potrebno da racionalni
   model u zadanom frekvencijskom pojasu reproducira Gabrielov model permitivnosti tkiva uz
   zadanu točnost? Štede li VF i QuadVF polove u odnosu na uobičajeni postupak s unaprijed
   zadanim polovima? Simulatori elektromagnetskog polja u vremenskoj domeni ne mogu izravno
   koristiti Cole–Coleov model, a svaki pol dodaje jednu jednadžbu u svakoj ćeliji mreže. Zato
   broj polova određuje cijenu simulacije.
2. **Sustav.** Relativna permitivnost tkiva je prijenosna funkcija realnog LTI SISO sustava:
   $$
   \varepsilon(s)=\varepsilon_\infty+\sum_{n=1}^{4}\frac{\Delta\varepsilon_n}{1+(s\tau_n)^{1-\alpha_n}}
   +\frac{\sigma_i}{s\,\varepsilon_0},\qquad s=\imath\omega .
   $$
   Članove $\varepsilon_\infty$ i $\sigma_i/(s\varepsilon_0)$ znamo točno i ne aproksimiramo ih.
   Aproksimira se strogo pravi dio
   $H(s)=\varepsilon(s)-\varepsilon_\infty-\sigma_i/(s\varepsilon_0)$ oblikom
   $H_r(s)=\sum_{j=1}^{r}\phi_j/(s-\lambda_j)$ iz [metodologije](../METHODOLOGY.md).
3. **Podaci.** Parametri iz izvješća AL/OE-TR-1996-0037 za 44 tipa tkiva. Tablica ostaje izvan
   Gita; repozitorij čuva izvor, upute za preuzimanje i kontrolni zbroj. Zrak i vakuum nisu dio
   eksperimenta jer nemaju disperziju. Ostala tkiva ne izbacujemo prešutno: sva ulaze u zbirnu
   tablicu, uključujući ona na kojima metoda ne uspije.
4. **Metode.** VF (L1, §2) s težinama i čvorovima koje odabiremo, QuadVF (L1, §3.3) prilagođen
   ograničenom pojasu te referentna metoda s fiksnim logaritamski raspoređenim polovima i
   rezidualima iz linearnog problema najmanjih kvadrata.
5. **Vrednovanje.** Za svako tkivo, metodu i razinu točnosti tražimo najmanji red $r$. Mjere su
   najveća relativna pogreška od $\varepsilon$ na gustoj kontrolnoj mreži i relativna
   $\mathcal{H}_2$ pogreška na pojasu. Model računamo u bilo kojoj točki, pa je pogreška izvan
   čvorova točno mjerljiva. Parametre metode (npr. $L$ i broj čvorova) biramo na razvojnom
   podskupu tkiva, a ne na tkivima za završno vrednovanje (AGENTS.md, pravilo 7).
6. **Ostaje otvoreno** i odlučuje se u zadacima iz [podjele rada](../PODJELA.md):
   - frekvencijski pojas (Sarin probni pokus koristi 10 MHz–10 GHz) i razine točnosti;
   - način prilagodbe kvadrature pojasu i postupanje s retkom $M_+[H]$;
   - broj i raspored čvorova, početni polovi, zrcaljenje, kriterij zaustavljanja i
     regularizacija;
   - razvojni podskup tkiva i podskup za detaljnu analizu;
   - Python ovisnosti, format seminara i prezentacije te rok;
   - je li tema prihvatljiva nastavniku kolegija, jer je fizika permitivnosti izvan gradiva.

## Obrazloženje

- **Pokriva cijeli L1, a ne samo VF.** $H$ znamo izračunati u bilo kojoj točki imaginarne osi.
  Zato sami biramo čvorove za QuadVF (L1, §3.3), točno mjerimo globalnu pogrešku i možemo na
  stvarnom problemu pokazati pojavu iz Primjera 3.1 (mali rezidual uz veliku
  $\mathcal{H}_2$ pogrešku).
- **Matematički je jednostavnija od HRTF teme.** Sve je u kontinuiranom vremenu kao u L1, pa
  nema prijelaza na jediničnu kružnicu. U Sarinu probnom pokusu svi su dobiveni polovi bili
  realni, što odgovara fizikalnom značenju vremena relaksacije.
- **$\mathcal{H}_2$ norma je konačna.** Osim zraka i vakuuma, najveći $\alpha_n$ u tablici je
  0,3. Cole–Coleov član zato pada barem kao $\omega^{-0{,}7}$, pa je
  $\int\lvert H(\imath\omega)\rvert^2d\omega$ konačan. Normu na cijeloj osi ipak određuju
  niskofrekvencijske disperzije s velikim $\Delta\varepsilon_n$ i $\tau_n$ u milisekundama, koje
  za primjenu nisu važne. Zato mjerimo pogrešku na pojasu, što je odmak od L1 koji treba izvesti.
- **Pitanje ima praktičnu posljedicu.** Manje polova znači jeftiniju simulaciju, a odgovor se ne
  zna unaprijed. Ako VF ili QuadVF ne štede polove, to je i dalje valjan rezultat.
- **Podaci su javni i maleni**, a model je standardni opis u literaturi o dozimetriji.
- **Razlikuje se od primjera iz L1.** L1 koristi modele iz zbirke NICONET (toplinski model, FOM,
  zgrada, greda) i modul ISS 1R, koji su konačnodimenzionalni modeli prostora stanja. Ovdje
  aproksimiramo iracionalnu funkciju bez konačnog točnog reda.

## Odbačene mogućnosti

- **HRTF-ovi (HUTUBS).** Jedini od triju kandidata iz prijedloga dopuštaju izbor čvorova, ali
  traže vlastiti izvod u diskretnom vremenu. Lovro je tražio matematički lakšu temu.
- **Impedancijski spektri baterija.** Čvorove određuje mjerenje i nema referentnog modela, pa
  QuadVF primjenjujemo samo težinama. Velik dio rada otišao bi na regresiju.
- **FRF-ovi kompozitne ploče.** Bila je rezerva u prijedlogu. Nema referentnog modela, a svaki
  scenarij izmjeren je jednom.
- **Toplinski model zida.** Ispunjava iste uvjete i ostaje rezerva ako se tablica pokaže
  neupotrebljivom. Blizak je toplinskom modelu iz L1, §3.3–§3.4, pa je teže pokazati da je
  problem nov.
- **Ovjes automobila sa šumom** (Sarin raniji primjer, izvan repozitorija). Prema Sarinoj procjeni
  manje je originalan.

## Posljedice

- U istoj promjeni usklađuju se `AGENTS.md`, `README.md`, [projekt](../PROJECT.md),
  [zadaci](../TASKS.md), [metodologija](../METHODOLOGY.md) i
  [literatura](../../research/LITERATURE.md). T2 je dovršen, a T3 djelomično.
- Rad se dijeli prema prijedlogu iz
  [ADR-0005](0005-divide-work-into-end-to-end-threads.md).
- Implementacija treba učitavanje i provjeru tablice, računanje $\varepsilon(s)$ i $H(s)$, VF,
  kvadraturu na pojasu, referentnu metodu, mjere pogreške i zapis podrijetla pokretanja.
- Sarin kod i brojeve iz probnog pokusa treba unijeti u repozitorij i ponovno pokrenuti prije
  nego se koriste kao rezultat.
- Testovi s točnim konačnim redom ne mogu koristiti stvarno tkivo: nijedno tkivo nema sve
  $\alpha_n=0$. Koristimo umjetne modele s tabličnim $\Delta\varepsilon_n$ i $\tau_n$ uz
  $\alpha_n=0$.
- Tvrdnju da su polovi najbolje aproksimacije realni i reziduali pozitivni L1 ne dokazuje. Može
  se navesti kao opažanje, a kao tvrdnja tek kad tim doda izvor u literaturu.
- Seminar mora ukratko objasniti permitivnost i Cole–Coleov model, a temu opravdati matematikom
  racionalne aproksimacije.
