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
projekta nonneg-matrix-fact-clustering i prilagođene ovoj temi. Primjena, podaci, inačica
metode, red aproksimacije, uzorkovanje i znanstveno Python okruženje još nisu odabrani.
Implementacija i eksperimentalni rezultati još ne postoje. Otvoreni su i rok i formati
predaje. Podjela tema između članova zapisana je u [popisu zadataka](docs/plan/TASKS.md).

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
python3 tools/check_before_stop.py
```

Za alate tijeka rada dovoljni su Python 3.11 ili noviji i Git; znanstveni paketi zasad nisu
potrebni. Provjera pokreće provjere dokumentacije i jedinične testove alata. Numeričke provjere
izričito označava s NOT RUN dok ne dogovorimo implementacijsko okruženje.

Zasebne naredbe, CI i postavljanje lokalnih hookova opisani su u
[tijeku rada i provjera](docs/plan/PIPELINE.md). Postupanje s nalazima i probno pokretanje
dnevne provjere bez pisanja na GitHub opisani su u
[uputama za pregled i nalaze](docs/plan/AI_REVIEW.md). Samo dodavanje datoteka ne postavlja
GitHub postavke, labele ni zaštitu grana i ne objavljuje promjene.
