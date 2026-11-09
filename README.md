# Seminar: identifikacija LTI SISO sustava metodom vector fitting

Seminar iz kolegija **Matematičko modeliranje i znanstveno računanje** izrađuju **Sara i Lovro**.
Cilj je detaljno razumjeti matematiku metode vector fitting (VF) i njezine inačice temeljene na
kvadraturi, implementirati metodu u Pythonu i primijeniti je na nov konkretan problem i skup
podataka. Oboje trebaju razumjeti cijeli projekt.

Glavni i jedini izvor je rad Z. Drmača, S. Gugercina i C. Beattieja *Quadrature-Based Vector
Fitting for Discretized H2 Approximation* (SIAM J. Sci. Comput., 2015).
[Pregled literature](docs/research/LITERATURE.md) povezuje njegove odjeljke s ciljevima učenja.

## Trenutačno stanje

Repozitorij sadrži pravila rada, istraživački plan i automatizirane provjere preuzete iz
projekta nonneg-matrix-fact-clustering i prilagođene ovoj temi. Primjena je odabrana
([ADR-0004](docs/plan/adr/0004-choose-debye-models-of-human-tissues.md)): koliko je realnih
polova (Debyejevih članova) najmanje potrebno da racionalni model reproducira Gabrielov model
permitivnosti ljudskih tkiva uz zadanu točnost i štede li VF i QuadVF polove. Rad je podijeljen
na dvije niti prema [podjeli rada](docs/plan/PODJELA.md), što je Sara potvrdila na sastanku Z0.
Python okruženje odabrano je u
[ADR-0006](docs/plan/adr/0006-choose-python-environment.md), a razine točnosti
u dodatku ADR-0004. Konačni pojas, postavke metode i rok još nisu odabrani.
Implementacija i eksperimentalni rezultati još ne postoje.

Predajemo pisani seminar, prezentaciju, kod i ponovljive rezultate. Seminar, prezentacija i
projektna dokumentacija pišu se na hrvatskom. [Opseg projekta](docs/plan/PROJECT.md),
[matematički i eksperimentalni plan](docs/plan/METHODOLOGY.md) i
[popis zadataka](docs/plan/TASKS.md) povezuju sve dijelove predaje.

## Odakle krenuti

1. Pročitaj [AGENTS.md](AGENTS.md), zajednička pravila za ljude i AI alate.
2. U [kazalu dokumentacije](docs/INDEX.md) pronađi aktualne odluke i istraživačke materijale.
3. Odaberi malen zadatak s [popisa zadataka](docs/plan/TASKS.md) i radi na zasebnoj grani.
   Promjenu pregledava drugi član tima. [Protokol promjena](docs/CHANGE_PROTOCOL.md) opisuje
   koju dokumentaciju treba uskladiti uz pojedinu vrstu promjene.
4. Prije predaje rada drugom članu pokreni lokalne provjere:

```bash
uv run --no-project python tools/check_before_stop.py
```

Potrebni su Git i [uv](https://docs.astral.sh/uv/), koji sam instalira Python 3.12 i zaključane
ovisnosti iz `uv.lock` ([ADR-0006](docs/plan/adr/0006-choose-python-environment.md)). Na Linuxu
je ista naredba `python3 tools/check_before_stop.py`. Provjera pokreće provjeru dokumentacije,
jedinične testove alata te numeričke provjere (`pytest` i `ruff`).

Zasebne naredbe, CI i postavljanje lokalnih hookova opisani su u
[tijeku rada i provjera](docs/plan/PIPELINE.md). Postupanje s nalazima i probno pokretanje
dnevne provjere bez pisanja na GitHub opisani su u
[uputama za pregled i nalaze](docs/plan/AI_REVIEW.md). Samo dodavanje datoteka ne postavlja
GitHub postavke, labele ni zaštitu grana i ne objavljuje promjene.
