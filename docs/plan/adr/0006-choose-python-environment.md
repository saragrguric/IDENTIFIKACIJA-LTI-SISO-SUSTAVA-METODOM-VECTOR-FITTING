# ADR-0006: Koristiti Python 3.12 s uv-om, uz provjere na Linuxu i Windowsu

**Datum:** 2026-11-09 · **Status:** prihvaćeno (Lovro i Sara prema Lovrinoj izjavi, 2026-11-09)

## Kontekst

ADR-0001 i ADR-0004 ostavili su Python ovisnosti otvorenima. [Prijedlog za Z0](../Z0_PRIJEDLOG.md)
predložio je okruženje u odjeljku 3. Lovro je 2026-11-09 u razgovoru prenio ishod sastanka Z0:
Sara potvrđuje prijedloge, okruženje joj je svejedno i prihvaća ono što je potrebno. Sara radi
na Windowsu, a Lovro na Linuxu. Na Lovrinu računalu su Python 3.12.3 i uv 0.13.6, a Sarine
verzije nisu zabilježene.

Alati tijeka rada i hookovi pozivaju `python3`, koji na Windowsu često ne postoji. CI se zasad
izvodi samo na Ubuntuu.

## Odluka

1. **Python 3.12.** `pyproject.toml` traži Python 3.12 ili noviji, a `uv.lock` i CI koriste 3.12.
2. **Ovisnosti:** `numpy`, `scipy` i `matplotlib`. Razvojne ovisnosti: `pytest` i `ruff`. Nova
   ovisnost dodaje se samo dogovorom i uz obrazloženje u PR-u.
3. **uv** upravlja okruženjem. `pyproject.toml` i `uv.lock` su u Gitu; CI i oba člana
   instaliraju iz `uv.lock`.
4. **Dva operacijska sustava.** Numeričke provjere u CI-ju izvode se na Linuxu i Windowsu.
5. **Testovi alata** u `tools/` ostaju `unittest` sa standardnom bibliotekom.
6. Odluku **provodi zadatak A1** (okruženje i CI) iz [plana A](../podjela/a-lovro.md).

## Obrazloženje

- NumPy i SciPy pokrivaju linearnu algebru (QR, SVD, svojstvene vrijednosti) i kvadraturu za
  provjeru, a Matplotlib slike. Druge biblioteke ne trebaju za dogovorenu metodu (AGENTS.md,
  odjeljak 6).
- Zaključane verzije potrebne su za reprodukciju u Z4, gdje svaki član na svom računalu
  reproducira tuđu nit. uv instalira i odgovarajuću verziju Pythona, pa je postupak isti na oba
  sustava.
- Sara reproducira nit A na Windowsu. CI na oba sustava zato ranije otkriva razlike u putanjama,
  pozivu interpretera i završecima redaka nego reprodukcija u fazi 4.
- Brojevi s različitih sustava i BLAS biblioteka mogu se razlikovati na razini zaokruživanja.
  Testovi i reprodukcija zato uspoređuju vrijednosti uz imenovane tolerancije, a ne bit po bit.

## Odbačene mogućnosti

- **Conda ili pip bez zaključanih verzija.** Conda je teža za CI, a popis ovisnosti bez
  zaključavanja ne jamči iste verzije na oba računala.
- **Samo Linux u CI-ju.** Problem na Windowsu otkrio bi se tek u Z4.
- **Jupyter kao glavni oblik koda.** Bilježnice su dopuštene za istraživanje, ali rezultat mora
  dati ponovljivo pokretanje (AGENTS.md, odjeljak 4).

## Posljedice

- A1 dodaje `pyproject.toml`, `uv.lock`, paket `vfdebye` u `src/`, `tools/check_project.py` i
  numerički posao u `.github/workflows/ci.yml` s matricom Linux i Windows.
- A1 provjerava pokreću li se `tools/check_before_stop.py` i hookovi na Windowsu. Poziv `python3`
  zamjenjuje se pozivom koji radi na oba sustava ili se razlika dokumentira u
  [tijeku rada](../PIPELINE.md).
- `AGENTS.md`, [projekt](../PROJECT.md), [zadaci](../TASKS.md), [tijek rada](../PIPELINE.md),
  [podjela rada](../PODJELA.md) i README usklađuju se s ovom odlukom.
