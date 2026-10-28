# Opseg seminara i predaja

## Dogovoreni cilj

Tema: **identifikacija LTI SISO sustava metodom vector fitting**. Kolegij:
**Matematičko modeliranje i znanstveno računanje**. Tim: **Sara i Lovro**. Svaki član mora razumjeti cijeli projekt.

Proučiti vector fitting (VF) za linearne vremenski nepromjenjive sustave s jednim ulazom i
jednim izlazom uz rad Z. Drmača, S. Gugercina i C. Beattieja, *Quadrature-Based Vector Fitting
for Discretized H2 Approximation*, kao glavni i jedini izvor koji tim trenutačno ima.
Razraditi matematiku detaljnije od uvodne definicije, razumjeti odabranu numeričku metodu,
implementirati je u Pythonu i primijeniti na nov konkretan problem i skup podataka.
Prihvatljiva je poznata domena s drugim konkretnim problemom i podacima. Moguća je i nova
domena; istraživačka novost algoritma nije uvjet.

Lovro je 2026-10-28 naveo da seminar ima ista pravila i strukturu kao projekt
nonneg-matrix-fact-clustering, uz drugu temu i kolegij, da je priloženi rad jedini izvor i da
ovaj put rade samo Sara i on. Naziv kolegija naveo je isti dan, nakon postavljanja tijeka rada.
Vidjeti
[ADR-0001](adr/0001-seminar-scope-and-shared-understanding.md). Ne pretpostavljati da je Sara
odobrila određeni skup podataka, inačicu metode ili pregled tijeka rada.

## Što se predaje i trenutačno stanje

| Stavka | Obvezni sadržaj | Trenutačno stanje |
|---|---|---|
| Pisani seminar | Motivacija, detaljna matematika, algoritam, podaci i metodologija, eksperimenti, interpretacija, ograničenja i literatura | Planiran na hrvatskom; format i opseg otvoreni |
| Prezentacija | Povezano objašnjenje istog modela, metode, rezultata i zaključaka | Planirana na hrvatskom; format i trajanje otvoreni |
| Python kod | Dogovorena inačica VF-a, smislene provjere i dokumentirano pokretanje koje omogućuje reprodukciju rezultata | Planirano; inačica metode, uzorkovanje i ovisnosti otvoreni |
| Rezultati | Numerički rezultati i nalazi u domeni s jasnim podrijetlom, slike i tablice te iskreno navedena ograničenja | Planirano; eksperimenti nisu provedeni |

## Razumijevanje cijelog projekta

Zadatak može imati privremenog nositelja i drugu osobu koja ga pregledava. Time se ne smije
stvoriti matematički stručnjak koji jedini razumije izvod ili programerski stručnjak koji
jedini zna pokrenuti projekt. Pojedinačna zaduženja i način izmjene uloga dogovorit će se
kasnije.

Na ključnim točkama zajednički proći matematiku, algoritam, podatke, kod i interpretaciju.
Oba člana trebaju moći objasniti:

1. Odakle potječu uzorci frekvencijskog odziva, u kojim su jedinicama i zašto je model LTI SISO
   sustav s racionalnom prijenosnom funkcijom.
2. Što predstavljaju red, polovi i reziduali aproksimanta te što nije jednoznačno određeno
   (poredak polova, izbor baricentričnih točaka).
3. Što funkcija cilja najmanjih kvadrata mjeri i kako iz linearizacije, SK iteracije i
   premještanja polova slijede implementirani problemi najmanjih kvadrata.
4. Koje su tvrdnje o konvergenciji, stabilnosti i kvaliteti aproksimacije opravdane te uz koje
   pretpostavke, a što je u radu ostalo otvoreno.
5. Kako reproducirati rezultate pokretanja, protumačiti prikazane metrike i objasniti
   ograničenje ili neuspjeh.

Stvarna pitanja i preostale nejasnoće zabilježiti u zadatku ili primopredaji. Popis za provjeru
poticaj je za stvarni razgovor, a ne dokaz da se razgovor održao. Svaka osoba potvrđuje vlastito
razumijevanje; AI alat to ne može potvrditi umjesto nje.

## Još otvorene odluke

- Format seminara i prezentacije, opseg i trajanje, kriteriji ocjenjivanja i rok.
- Konkretna primjena, istraživačko pitanje, sustav i skup podataka te uvjeti pristupa i daljnje
  distribucije; mogu li se vrijednosti prijenosne funkcije računati u proizvoljnim točkama ili
  postoje samo zadana mjerenja; postoji li referentni model za računanje globalne pogreške.
- Inačica metode (klasični VF, QuadVF ili proširenje iz rada), funkcija cilja i težine, čvorovi
  uzorkovanja i parametar kvadrature, red aproksimacije, početni polovi, zrcaljenje nestabilnih
  polova, rješavač najmanjih kvadrata, regularizacija, kriterij zaustavljanja te strogo pravi ili
  pravi oblik modela.
- Znanstvene Python ovisnosti, podržana verzija, okruženje i referentna bibliotečna implementacija.
- Prikladna referentna metoda, metrike domene i opseg eksperimenata.
- Pojedinačna zaduženja i potvrda GitHub identiteta: repozitorij je pod računom `saragrguric`,
  a Lovro radi kao `LRazum`.
- Dostupnost zaštite grana na GitHubu te povjerenje i aktivacija hookova na pojedinom računalu.

Za važne izbore pripremiti argumente i prijedlog, zatim dogovor zabilježiti u ADR-u i ažurirati
povezane dokumente. Postavljanje tijeka rada ne donosi te odluke.

## Granice opsega

Vector fitting za SISO sustave središnja je metoda. QuadVF, SobVF, RegVF i formulacija za
šumne podatke inačice su i proširenja iz rada, a nisu obvezne implementacije dok ih tim ne
odabere. IRKA je u radu referentna metoda za usporedbu; njezina implementacija nije zahtjev.
MIMO sustavi i Loewnerov okvir izvan su opsega rada (rad ih spominje kao srodne pristupe ili
buduće smjerove) i nisu projektni zahtjev. Trenutačno nisu potrebni web-proizvod, postupak
objave aplikacije ni produkcijska usluga.
