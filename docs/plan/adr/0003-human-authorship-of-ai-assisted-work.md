# ADR-0003: Autor rada uz AI alat isključivo je osoba koja ga vodi

**Datum:** 2026-10-29 · **Status:** prihvaćeno (Lovro, 2026-10-29)

## Kontekst

Prva dva commita na `main` (PR #1 i PR #2) sadržavala su redak `Co-Authored-By` koji Claude
Code dodaje po zadanoj postavci, a ADR-0002 propisuje zaseban prefiks `codex/<topic>` za grane
koje stvara AI. Lovro je 2026-10-29 zatražio da AI alat ne bude koautor ničega i da svaki
commit, redak koda i tekst bude pripisan isključivo osobi koja zadaje upute. Lovro je u
razgovoru naveo da se ostali sudionici slažu; ovaj zapis to ne bilježi kao Sarino odobrenje.

## Odluka

1. AI je alat osobe koja ga koristi. Autor commita, PR-a, koda, dokumentacije, seminara i
   prezentacije isključivo je osoba koja vodi rad i zadaje upute, sa svojim Git identitetom.
2. AI alati ne dodaju `Co-Authored-By` ni druge oznake autorstva, potpise poput „Generated
   with …” ni poveznice na sesiju u commitove, PR-ove, komentare koda ili dokumente.
   Claude Code to provodi postavkom `attribution` u `.claude/settings.json`; ostali alati
   slijede pravilo iz `AGENTS.md`.
3. Grane nose prefiks osobe koja vodi rad (`sara/<topic>` ili `lovro/<topic>`), i kada se pri
   radu koristi AI alat. To zamjenjuje prefiks AI grana iz točke 1 zapisa ADR-0002.
4. Autor odgovara za sadržaj: prije commita ga pregledava i mora ga moći objasniti. Pravilo
   pregleda drugog člana tima i zabrana izmišljanja ljudskog pregleda iz ADR-0002 ostaju.
5. Jednokratna iznimka od zabrane prisilnog pusha: Lovro je 2026-10-29 sam prepisao povijest
   `main` i uklonio retke `Co-Authored-By` iz commitova PR-ova #1 i #2. Sadržaj datoteka nije
   promijenjen. Zabrana prisilnog pusha i prepisivanja povijesti ostaje za sve druge slučajeve.

## Obrazloženje

Odgovornost za rad snosi osoba koja ga vodi i predaje, kao i kod drugih alata. Jedan identitet
autora i prefiks grane pojednostavljuju pregled: drugi član tima zna tko odgovara za promjenu.

## Odbačene mogućnosti

- **Zadržati AI koautorstvo i prefiks `codex/`:** Lovro je izričito zatražio pripisivanje
  isključivo osobi koja vodi rad.
- **Zadržati postojeće retke `Co-Authored-By` na `main`:** Lovro je zatražio novi početak bez
  AI oznaka autorstva u povijesti i sam proveo prepisivanje.

## Posljedice

- `AGENTS.md`, `docs/CHANGE_PROTOCOL.md`, `docs/plan/AI_REVIEW.md`,
  `.github/pull_request_template.md`, `docs/plan/PIPELINE.md` i `.claude/settings.json`
  usklađeni su s ovom odlukom; ADR-0002 dobiva dodatak koji upućuje na ovaj zapis.
  `tools/check_docs.py` nazive grana `sara/…` i `lovro/…` ne tumači kao putanje.
- Hashevi su promijenjeni: PR #1 `ff79853` → `4e37068`, PR #2 `3dc2fd6` → `3355648`;
  `a21a894` nije promijenjen. Lokalne kopije treba uskladiti s novim stanjem `main` na GitHubu.
- GitHub više ne povezuje nove commitove s PR-ovima #1 i #2, pa ih dnevna provjera prijavljuje
  kao commitove bez PR-a dok ne izađu iz njezina prozora od 48 sati (do 2026-10-30 oko
  20:37 UTC). To je očekivana posljedica prepisivanja; provjera nije mijenjana da ih prešuti.
- Izvorni commitovi PR-ova #1 i #2 ostaju na GitHubu u referencama tih PR-ova (refs/pull);
  suradnik ih ne može ukloniti.
- Povijesni nazivi grana `codex/seminar-workflow` i `codex/course-name` ostaju u zapisima i u
  `tools/daily_check.py` jer su vezani uz stvarne PR-ove #1 i #2.

## Dodatak 2026-11-01: vraćanje `main` nakon pogrešnog spajanja

Lokalna kopija koja nije bila usklađena s prepisanom poviješću vratila je 2026-11-01 `main` na
stari `3dc2fd6`, a zatim je na njega pushan merge `b6e993a` s nerazriješenim konfliktnim
markerima u 12 datoteka. CI je pao, a stari commitovi s retkom `Co-Authored-By` vratili su se u
povijest `main`.

Lovro je istog dana u razgovoru izričito odobrio prisilni push kojim je `main` vraćen na
`6ac9efa` (PR #3). Iz povijesti `main` uklonjeni su `b6e993a`, `3dc2fd6` i `ff79853`; sadržaj
datoteka jednak je stanju nakon PR-a #3. Iznimka vrijedi samo za taj push i ne bilježi Sarino
odobrenje. Zabrana prisilnog pusha i prepisivanja povijesti ostaje za sve druge slučajeve.
Lokalne kopije koje još sadrže te commitove treba uskladiti s `main` na GitHubu.
