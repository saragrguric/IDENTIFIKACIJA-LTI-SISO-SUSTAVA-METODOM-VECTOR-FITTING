# ADR-0007: AI alat na uputu člana obavlja Git i GitHub radnje, uključujući odobrenje PR-a

**Datum:** 2026-11-10 · **Status:** prihvaćeno (Lovro, 2026-11-10)

## Kontekst

ADR-0002 traži da svaki PR u `main` odobri drugi član tima i da AI pregled samo dopunjuje taj
pregled, a `docs/plan/AI_REVIEW.md` navodi da AI pregled ne ispunjava obvezno ljudsko
odobrenje. Pravila nisu određivala smije li član odobrenje koje je sam donio dati preko svog AI
alata. Sarin AI alat 2026-11-10 zato nije htio odobriti PR-ove #8 i #9. Lovro je istog dana
zatražio da se, radi automatizacije i brzine, AI alatu dopusti da na izričitu uputu člana
obavi push, otvaranje PR-a, odobrenje i spajanje, dok član promjenu pregledava sam. Prema
Lovrinoj izjavi Sara se s tim slaže; ovaj zapis to ne bilježi kao Sarino odobrenje.

## Odluka

1. **Radnje na uputu.** AI alat smije pod računom i Git identitetom člana koji ga koristi
   raditi commit i push, otvarati, uređivati, odobravati i spajati PR-ove te objavljivati
   komentare, preglede i prijave. Svaku radnju obavlja samo na izričitu uputu tog člana u
   razgovoru koja je pokriva; jedna uputa može obuhvatiti više navedenih radnji.
2. **Odobrenje ostaje članovo.** Član promjenu pregledava sam. AI alat odobrava PR samo kada
   ga član, nakon vlastitog pregleda, izričito uputi da to učini. Takvo je odobrenje odobrenje
   tog člana i ispunjava pravilo pregleda drugog člana tima (ADR-0002, točka 2). AI alat ne
   odobrava na vlastitu inicijativu ni samo na temelju vlastitog pregleda i ne tvrdi da je član
   pregledao ili razumio promjenu ako to član nije rekao.
3. **Spajanje.** AI alat spaja PR na uputu člana kada je PR odobrio drugi član ili za njega
   postoji zabilježena iznimka iz dodataka ADR-0002 te kada CI prolazi.
4. **AI nikad nije koautor.** ADR-0003 ostaje u cijelosti: bez `Co-Authored-By`, potpisa poput
   „Generated with …” i poveznica na sesiju u commitovima, PR-ovima, komentarima i pregledima.
5. **Zaštitna pravila ostaju.** Autor ne odobrava vlastiti PR. Nema izravnih commitova na
   `main`, prisilnog pusha ni prepisivanja tuđe grane. Samostalan AI pregled i odobrenja bot
   računa ne zamjenjuju pregled člana.

## Obrazloženje

AI alat je alat člana (ADR-0003). Odluku o odobrenju donosi član nakon vlastitog pregleda, a AI
alat samo izvršava naredbe na GitHubu, kao što bi ih član izvršio sam. Time se ubrzava rad bez
promjene toga tko pregledava i tko odgovara za promjenu.

## Odbačene mogućnosti

- **Odobrenje samo osobno kroz sučelje GitHuba:** usporava rad, a ne mijenja tko donosi
  odluku.
- **Trajna ovlast AI alata bez upute za pojedinu radnju:** Lovro je izričito zatražio da se za
  push, PR, odobrenje i spajanje traži uputa člana.
- **AI kao zaseban recenzent ili bot račun:** odobrenje bota ne bi bilo odobrenje člana, a
  zaseban identitet AI-ja protivio bi se ADR-0003.

## Posljedice

- `AGENTS.md`, `docs/CHANGE_PROTOCOL.md`, `docs/plan/AI_REVIEW.md`,
  `.github/pull_request_template.md` i `docs/INDEX.md` usklađeni su s ovom odlukom; ADR-0002
  dobiva dodatak koji upućuje na ovaj zapis.
- `tools/daily_check.py` provjeru odobrenja ne mijenja: odobrenje pod računom člana koji nije
  autor već se broji, a odobrenja bot računa i dalje ne.
