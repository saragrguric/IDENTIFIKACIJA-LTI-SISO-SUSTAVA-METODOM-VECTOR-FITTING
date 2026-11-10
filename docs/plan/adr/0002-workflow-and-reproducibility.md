# ADR-0002: Male pregledane promjene, zajedničko razumijevanje i sljedivi eksperimenti

**Datum:** 2026-10-28 · **Status:** prihvaćeno (Lovro, 2026-10-28)

## Kontekst

Sara i Lovro pripremaju seminar o identifikaciji LTI SISO sustava metodom vector fitting.
Predaju pisani seminar, prezentaciju, Python kod i eksperimentalne rezultate. Oboje moraju
razumjeti cijeli projekt. Primjena, skup podataka i detalji implementacije ostaju otvoreni te
će se dogovoriti kasnije.

Lovro je 2026-10-28 zatražio da se repozitorij posloži isto kao projekt
nonneg-matrix-fact-clustering, koji je sam prilagodio prakse projekta PelosiPlus. Preuzimaju se
male promjene, ljudski pregled, zapisi odluka, usklađivanje dokumentacije, nalazi, dnevna
provjera, završne provjere i hrvatski kao jezik tekstova za ljude. Znanstveni sadržaj, tročlani
tim, odobrene iznimke od pregleda i stanje GitHuba tog projekta ne opisuju ovaj seminar. Ovaj
zapis dokumentira postavljanje koje je zatražio Lovro, a ne Sarino odobrenje.

## Odluka

1. Jedan zadatak obrađuje se na jednoj grani i u malom PR-u. Grane članova tima koriste
   `sara/<topic>` i `lovro/<topic>`; grane koje stvara AI koriste `codex/<topic>`.
   Ne raditi commit izravno na `main`, prisilni push ni prepisivati tuđu granu.
2. Svaki PR prema `main` treba odobriti drugi član tima. AI pregled dopunjuje taj pregled.
   Izmjenjujte rad i zajedničke prolaze kroz projekt kako bi oboje moglo objasniti matematiku,
   implementaciju, eksperimente i zaključke; bilježite samo stvarno sudjelovanje.
3. Korijenski `AGENTS.md` ostaje jedini izvor pravila repozitorija, a `CLAUDE.md` sadrži
   `@AGENTS.md`. Važne odluke zapišite u ADR-ove te u istoj promjeni uskladite planove, naredbe
   i materijale na koje odluka utječe.
4. Neriješene znanstvene odluke ostaju jasno otvorene. Prije implementacije koja ovisi o njima
   pripremite mogućnosti i obrazloženje za timsku raspravu; rutinske odobrene ispravke obavite
   bez dodavanja novog koraka odobravanja.
5. AI alati trebaju izričito korisničko ovlaštenje u razgovoru prije commita, pusha, otvaranja
   PR-ova ili objavljivanja problema, komentara, pregleda, predaja ili javnih materijala.
   Već dano ovlaštenje vrijedi i dalje unutar svojeg opsega.
6. Pokrećite provjere dokumentacije i alata u CI-ju te zajedničkom završnom skriptom. Prije
   tvrdnje da je alat integriran provjerite jesu li lokalne završne provjere (*hooks*) stvarno
   aktivne. Numeričke provjere u CI-ju i zaključane ovisnosti dodaju se nakon izbora implementacije.
7. Za svako prijavljeno izvođenje sačuvajte označenu konfiguraciju eksperimenta, identitet
   podataka, podrijetlo koda i okruženja, podatke o zaustavljanju i izlaze. Ispravak dobiva
   novu oznaku izvođenja; citirani rezultati ne prepisuju se prešutno. Nedostajući dokazi
   ostaju jasno označeni kao nedostajući.
8. Koristite zajedničke nalaze i dnevnu GitHub provjeru stanja CI-ja, sukoba i zastarjelosti
   PR-ova, odobrenja te commitova koji su stigli na `main` bez PR-a. Provjera pravila počinje
   od zabilježenog početnog stanja, 2026-10-28 19:19:16 UTC; početni commit `a21a894` nastao
   prije uvođenja načina rada ne provjerava se retroaktivno. Aktivaciju na GitHubu i postavke
   identiteta treba zasebno provjeriti.
9. Tekstovi namijenjeni ljudima pišu se na hrvatskom: dokumentacija za tim, pisani seminar,
   prezentacija, commit poruke, tekstovi PR-ova i objašnjenja nalaza. Kod, identifikatori,
   nazivi datoteka i tehničke upute AI alatima mogu ostati na engleskom; naredbe, oznake na
   GitHubu i drugi tehnički identifikatori zadržavaju se kako bi alati radili.
10. Iznimka od pregleda moguća je samo uz izričitu korisnikovu uputu za točan par broja PR-a
    i grane, zabilježenu kao datirani dodatak ovog zapisa i u `tools/daily_check.py`. Zasad
    takvih iznimaka nema.

## Obrazloženje

Manje promjene drugi član lakše razumije i provjerava. Ljudski pregled i izmjenjivanje u
objašnjavanju podupiru cilj učenja bez dijeljenja znanja u odvojene uloge. Usklađivanje
dokumentacije sprječava da točna lokalna promjena ostavi netočan opis projekta. Zapisi odluka
razlikuju svjestan znanstveni izbor od usputnog detalja implementacije.

Vector fitting je iterativan, osjetljiv na početne polove, uzorkovanje i uvjetovanost, a
njegova konvergencija nije teorijski zajamčena. Reproducibilne konfiguracije i podrijetlo
materijala omogućuju tumačenje rezultata nakon promjena koda, podataka ili okruženja. Numerički
testovi, znanstveni pregled i sljedivi eksperimenti daju različite dokaze; nijedan ne zamjenjuje
ostale. Zakazana provjera otkriva neka kršenja načina rada, ali ne može dokazati razumijevanje
ni znanstvenu točnost.

## Odbačene mogućnosti

- **Trajna podjela odgovornosti za matematiku, kod i eksperimente:** nespojiva je sa zahtjevom
  da svaki član razumije cijeli projekt.
- **Prenošenje sadržaja i stanja referentnog seminara:** tema, literatura, tročlani tim,
  iznimke od pregleda za njegove PR-ove i stanje njegova GitHuba ne vrijede ovdje.
- **Izbor metode i podataka pri postavljanju načina rada:** te odluke o implementaciji i
  primjeni ostaju za kasniju raspravu.
- **AI odobrenje ili uspješan CI kao dovoljan uvjet:** nijedno ne zamjenjuje pregled drugog
  člana tima niti potvrđuje znanstvene tvrdnje.
- **Snimke rezultata bez reproducibilnih ulaza:** sama slika ne objašnjava koji su je izbori
  proizveli.
- **Zaseban repozitorij AI memorije sada:** trajne odluke, zadaci, bilješke o izvorima i nalazi
  ovdje već imaju zajednička mjesta; za ovo postavljanje ne treba dodatna infrastruktura.
- **Pretpostavka da su zaštite na GitHubu, oznake ili lokalne završne provjere aktivne:**
  lokalne datoteke ne utvrđuju stanje GitHuba ni računala pojedinog člana.

## Posljedice

- `docs/CHANGE_PROTOCOL.md` određuje postupak za zadatak, popis za usklađivanje i primopredaju.
- `docs/plan/PIPELINE.md` razlikuje trenutačne provjere od planiranog numeričkog rada i navodi
  minimalne podatke o podrijetlu rezultata.
- `docs/plan/AI_REVIEW.md` određuje nalaze, pregled i ograničenja dnevne provjere.
- `.github/pull_request_template.md`, `.github/workflows/ci.yml` i
  `.github/workflows/daily-check.yml` provode lokalno postavljanje načina rada.
- `tools/check_docs.py`, `tools/check_before_stop.py` i `tools/daily_check.py`, uz testove,
  provode automatizirane provjere. `.claude/settings.json` i `.codex/hooks.json` postavljaju
  istu završnu provjeru. Aktivacija lokalnih završnih provjera provjerava se neovisno o
  postojanju skripte.
- GitHub identiteti, dostupnost zaštite grane, aktivacija dnevne provjere na GitHubu, primjena,
  podaci, inačica metode i numeričko okruženje ostaju izričito navedeni naknadni zadaci.

## Dodatak 2026-10-28: izričito odobreno spajanje početnog načina rada

Tijekom postavljanja Lovro je u razgovoru izričito zatražio commit, push, PR i spajanje u
`main` nakon dovršetka rada. Time je odobrio objavu i spajanje početnog PR-a #1 za način rada s
grane `codex/seminar-workflow` bez čekanja Sarina pregleda. To ne bilježi niti podrazumijeva
Sarino odobrenje i ne mijenja pravilo pregleda za kasnije PR-ove; Sara treba naknadno
pregledati spojena pravila i plan.

Dnevna provjera prepoznaje samo taj broj PR-a i tu granu kao iznimku od pregleda. CI i dalje
mora proći; izravni commitovi i druga spajanja bez pregleda ostaju nalazi. Stvaranje oznaka
nalaza potrebnih objavljenoj dnevnoj provjeri dio je njezine aktivacije. Ova uputa ne odobrava
nepovezane prijave problema, poruke ni promjene pristupa repozitoriju.

## Dodatak 2026-10-28: odobreno spajanje naziva kolegija bez pregleda

Nakon spajanja PR-a #1 Lovro je naveo naziv kolegija i izričito zatražio commit, push, PR i
spajanje te promjene u `main` bez Sarina pregleda. Iznimka vrijedi samo za PR #2 s grane
`codex/course-name`; ne bilježi Sarino odobrenje i ne mijenja pravilo pregleda budućih PR-ova.
CI i ostale provjere moraju proći.

Pravila, protokol, PR predložak i dnevna provjera bilježe tu konkretnu iznimku. Prethodna
iznimka za PR #1 ostaje dio povijesti; drugi PR-ovi nisu izuzeti iz provjere odobrenja.

## Dodatak 2026-10-29: autorstvo i prefiks grana

Prefiks `codex/<topic>` za grane koje stvara AI iz točke 1 zamijenjen je zapisom
[ADR-0003](0003-human-authorship-of-ai-assisted-work.md): grane nose prefiks osobe koja vodi
rad, a autor commita i PR-a isključivo je ta osoba. Ostale točke ove odluke ne mijenjaju se.

## Dodatak 2026-10-29: odobreno spajanje pravila autorstva bez pregleda

Lovro je u razgovoru izričito zatražio commit, push, PR i spajanje pravila autorstva iz
ADR-0003 u `main` bez Sarina pregleda. Iznimka vrijedi samo za PR #3 s grane
`lovro/ai-attribution`; ne bilježi Sarino odobrenje i ne mijenja pravilo pregleda budućih
PR-ova. CI i ostale provjere moraju proći.

## Dodatak 2026-11-07: odobreno spajanje izbora teme i podjele rada bez pregleda

Lovro je u razgovoru izričito zatražio spajanje PR-a #6 s grane `lovro/tema-i-podjela` u
`main` bez Sarina pregleda. PR #6 sadrži commitove PR-a #5 s grane `lovro/podjela-zadataka`,
pa spajanjem u `main` ulazi i sadržaj PR-a #5, koji se zatim zatvara bez zasebnog spajanja.
Lovro je izričito odobrio iznimku za oba para. Iznimka ne
bilježi Sarino odobrenje i ne mijenja pravilo pregleda budućih PR-ova; CI i ostale provjere
moraju proći. Sara sadržaj obaju PR-ova (ADR-0004, ADR-0005, podjelu rada, osobne planove i
dodatke ADR-0001 od 2026-11-01 i 2026-11-03) potvrđuje na sastanku Z0 ili traži izmjene novim
PR-om.

## Dodatak 2026-11-10: odobrenje i spajanje preko AI alata

[ADR-0007](0007-ai-tool-acts-for-its-user-in-git.md) dopunjuje točke 2 i 5: AI alat na
izričitu uputu člana smije odobriti i spojiti PR pod računom tog člana. Odobrenje koje AI alat
da na uputu člana nakon njegova pregleda ispunjava točku 2. Odbačena mogućnost „AI odobrenje
ili uspješan CI kao dovoljan uvjet” i dalje vrijedi za samostalan AI pregled i odobrenja bot
računa.
