# ADR-0001: Proučiti i implementirati vector fitting za LTI SISO sustave uz razumijevanje cijelog projekta za oboje

**Datum:** 2026-10-28 · **Status:** prihvaćeno (opseg odredio Lovro, 2026-10-28)

## Kontekst

Sara i Lovro zajedno rade seminar na temu identifikacije LTI SISO sustava metodom vector
fitting; naziv kolegija još nije zabilježen. Lovro je priložio jedan rad, Drmač, Gugercin i
Beattie, *Quadrature-Based Vector Fitting for Discretized H2 Approximation* (2015), i naveo ga
kao jedini izvor koji tim ima. Naveo je i da seminar ima ista pravila, strukturu i način rada
kao projekt nonneg-matrix-fact-clustering, uz drugu temu i kolegij, te da ovaj put rade samo
Sara i on.

## Odluka

1. Naučiti teoriju uz detaljnu matematičku razradu, razumjeti numeričku metodu, implementirati
   je u Pythonu i primijeniti na nov konkretan problem i skup podataka.
2. Dovoljan je nov konkretan slučaj u domeni koju rad već spominje; moguća je i druga domena.
   Razvoj novog algoritma za vector fitting nije obvezan.
3. Predati pisani seminar, prezentaciju, kod i eksperimentalne rezultate.
4. Oba člana uče matematiku, algoritam, podatke, implementaciju i interpretaciju. Znanje se
   dugoročno ne dijeli po područjima između članova. Podjela zadataka dogovara se kasnije.
5. Primjena, skup podataka, inačica metode (klasični VF, QuadVF ili proširenje iz rada), red i
   uzorkovanje, ovisnosti, formati dokumenata, rok i naziv kolegija ostaju otvoreni.
   Postavljanje načina rada ne uključuje izbor ni implementaciju metode.

## Obrazloženje

Cilj učenja je razumjeti metodu dovoljno dobro za njezinu implementaciju, objašnjenje i
evaluaciju. Matematički izvodi i reproducibilni dokazi podupiru to razumijevanje. Oba člana
trebaju moći objasniti cijeli projekt. Jedini izvor povezuje VF s diskretiziranom
$\mathcal{H}_2$ aproksimacijom, pa seminar mora razlikovati prilagodbu uzorcima od globalne
kvalitete modela.

## Odbačene mogućnosti

- Matematička obrada ograničena na definiciju ili pseudokod VF-a: zahtjevi su preuzeti iz
  referentnog seminara, koji izričito traži veću dubinu.
- Trajna podjela odgovornosti za matematiku, kod i eksperimente po članovima: Lovro traži ista
  pravila kao u referentnom projektu, prema kojima svi poznaju cijeli projekt.
- Preuzimanje tročlanog tima iz referentnog projekta: Lovro je naveo da ovaj put rade samo Sara
  i on.
- Pretpostavka da je QuadVF ili ponavljanje NICONET primjera iz rada već odabrani zadatak:
  vector fitting je glavna metoda, a inačica i primjena još su otvorene.
- Izbor detalja implementacije tijekom postavljanja načina rada: tim će ih dogovoriti kasnije.

## Posljedice

Opseg je prenesen u `AGENTS.md`, `README.md`, `docs/plan/PROJECT.md`, `docs/plan/TASKS.md`,
`docs/plan/METHODOLOGY.md` i `docs/research/LITERATURE.md`. Buduće odluke moraju zadržati
zajedničko učenje cijelog projekta i povezati matematiku, kod i interpretaciju eksperimenata.
Kada se utvrdi naziv kolegija, upisuje se u iste dokumente kao datirani dodatak ovog zapisa.

## Dodatak 2026-10-28: naziv kolegija

Nakon postavljanja tijeka rada Lovro je naveo da se kolegij zove Matematičko modeliranje i
znanstveno računanje. Naziv je upisan u `README.md`, `AGENTS.md` i `docs/plan/PROJECT.md`.
Time se ne mijenjaju opseg, materijali za predaju ni otvorene znanstvene odluke iz ovog zapisa;
rok, formati predaje i kriteriji ocjenjivanja ostaju otvoreni.

## Dodatak 2026-11-01: uloga AI alata u izradi

Lovro je naveo da je na seminaru uporaba AI alata dopuštena u svim dijelovima rada i da je
zadatak tima rad na kraju obraniti. Zato kod, testove i nacrte piše AI alat, a članovi tima vode
rad, pregledavaju ga i moraju ga moći objasniti. Točka 4 ove odluke ostaje: oba člana razumiju
cijeli projekt, a generirani sadržaj nije dokaz razumijevanja. Autorstvo slijedi ADR-0003.
Ovaj zapis ne bilježi Sarino odobrenje, a dopuštenje kolegija navodi se kako ga je prenio Lovro.

## Dodatak 2026-11-03: podjela tema

Točka 4 ostavila je podjelu zadataka za kasnije. Na zajedničkom sastanku 2026-11-03 Lovro je
naveo raspodjelu uloga iz popisa zadataka: osoba A je Lovro, a osoba B Sara. Podjela određuje
tko u pojedinoj temi provjerava izvod i testove, a tko vodi AI alat pri implementaciji i
pregledava kod. Ne mijenja točku 4: oba člana razumiju cijeli projekt. Vrijedi nakon Sarina
odobrenja PR-a #5 kojim je upisana; ovaj zapis to odobrenje ne zamjenjuje.
