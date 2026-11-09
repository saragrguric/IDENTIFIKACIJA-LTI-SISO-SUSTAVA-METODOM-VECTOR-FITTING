# ADR-0005: Podijeliti rad na dvije niti od matematike do rezultata, uz međusobni pregled

**Datum:** 2026-11-07 · **Status:** prihvaćeno (Lovro i Sara prema Lovrinoj izjavi, 2026-11-09)

## Kontekst

ADR-0001 traži da oba člana razumiju cijeli projekt i da se znanje trajno ne dijeli po
područjima. PR #5 predložio je podjelu po temama rada L1: u svakoj temi jedan član provjerava
izvod i testove, a drugi vodi AI alat pri implementaciji i pregledava kod. Lovro je 2026-11-03
naveo raspodjelu uloga: osoba A je Lovro, a osoba B Sara. Sara PR #5 još nije odobrila.

Nakon izbora teme ([ADR-0004](0004-choose-debye-models-of-human-tissues.md)) Lovro je
2026-11-07 zatražio da se repozitorij složi kao projekt nonneg-matrix-fact-clustering. Ondje je
rad podijeljen na niti: svaka nit ide od matematike preko koda i eksperimenata do dijela seminara
i prezentacije, a recenzent niti neovisno provjerava izvode, pregledava PR-ove i reproducira
eksperimente. Ovaj zapis prenosi taj način rada na dvočlani tim i temu tkiva. Lovro ga predlaže,
a Sara ga potvrđuje na sastanku Z0 ili traži izmjene. Niti i osobne planove napisao je Lovro uz
pomoć AI alata; oni su prijedlog sadržaja.

## Odluka

1. Rad se dijeli na dvije niti, uz zadržane uloge iz PR-a #5:
   - **Nit A, Lovro: od tablice do polova.** Podaci i model tkiva, problem (1.1), linearizacija,
     SK iteracija, baricentrični prikaz, premještanje polova, reziduali, zrcaljenje i
     konvergencija; kod jezgre VF-a, okruženje i zapis podrijetla.
   - **Nit B, Sara: od polova do odgovora.** $\mathcal{H}_2$ norma, kvadratura, QuadVF na pojasu,
     uvjetovanost, referentna metoda i mjere pogreške; glavni eksperiment i usporedba metoda.
2. **Pregled je međusobni:** Sara pregledava nit A, a Lovro nit B. Recenzent pregledava PR-ove
   niti, neovisno na papiru izvodi njezine tvrdnje, objašnjava je na zajedničkim prolazima i
   reproducira njezine eksperimente.
3. Ostaju načela iz PR-a #5 i dodatka ADR-0001 od 2026-11-01: kod, testove i nacrte piše AI alat;
   autor commita je član koji vodi rad (ADR-0003); testovi se temelje na izvodu i analitičkim
   primjerima, a ne na kodu koji provjeravaju.
4. Zajednički plan, sučelja i faze nalaze se u [podjeli rada](../PODJELA.md), a detaljni koraci
   u osobnim planovima ([plan A](../podjela/a-lovro.md), [plan B](../podjela/b-sara.md)).
   Tablica „Podjela rada” iz PR-a #5 u [popisu zadataka](../TASKS.md) zamjenjuje se poveznicom
   na podjelu rada.

## Obrazloženje

- Svaka nit završava provjerljivim rezultatom: nit A modelom koji iz tablice daje polove, a nit B
  odgovorom na pitanje iz ADR-0004.
- Podjela prati tok podataka, pa su sučelja između niti malobrojna: model tkiva, funkcija
  `vector_fit` i model s polovima i rezidualima.
- Sara je u probnom pokusu već napisala kvadraturu, QuadVF i usporedbu metoda. Nit B nastavlja
  taj rad, a nit A pokriva dijelove koje je Lovro u PR-u #5 trebao provjeravati.
- Neovisna provjera izvoda i reprodukcija čuvaju zahtjev ADR-0001 da oba člana razumiju cijeli
  projekt, kao u NMF projektu.

## Odbačene mogućnosti

- **Podjela po temama iz PR-a #5 bez niti.** Odvaja provjeru izvoda od pisanja koda unutar svake
  teme, ali ne određuje tko vodi podatke, eksperimente i dijelove seminara. Ta pitanja ostaju
  otvorena dok se ne dogovore zasebno.
- **Podjela na teoriju i kod.** Proturječi ADR-0001: jedan bi član postao jedini stručnjak za
  izvod, a drugi za pokretanje.
- **Rad bez podjele.** Dva člana mogu sve raditi zajedno, ali tada je teže pratiti tko što
  pregledava, a pregled u PR-u postaje formalan.

## Posljedice

- Dodaju se [podjela rada](../PODJELA.md), osobni planovi, [prijedlog za Z0](../Z0_PRIJEDLOG.md),
  `.github/CODEOWNERS` te predlošci issuea „Zadatak” i „Nalaz”.
- CODEOWNERS automatski traži pregled od recenzenta niti; za spajanje i dalje vrijedi odobrenje
  drugog člana (ADR-0002).
- GitHub issuei, oznake niti i milestonei faza stvaraju se tek nakon potvrde na Z0 i uz
  Lovrino ovlaštenje za tu radnju.
- Ako Sara na Z0 ne prihvati niti, novi zapis zamjenjuje ovaj, a vrijedi podjela iz PR-a #5.

## Dodatak 2026-11-09: potvrda na Z0

Lovro je 2026-11-09 u razgovoru prenio da Sara na sastanku Z0 potvrđuje ovaj zapis, oba osobna
plana, zajednička sučelja iz [podjele rada](../PODJELA.md) i naziv paketa `vfdebye`. Status je
promijenjen u prihvaćeno na temelju te izjave; Sarin pregled PR-a koji uvodi ovaj dodatak njezina
je potvrda u repozitoriju. Podjela iz PR-a #5 ostaje zamijenjena. GitHub issuei, oznake niti i
milestonei faza i dalje traže Lovrino ovlaštenje za tu radnju.
