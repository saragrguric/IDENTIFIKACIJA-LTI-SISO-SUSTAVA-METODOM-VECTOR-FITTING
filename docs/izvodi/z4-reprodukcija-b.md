# Z4: reprodukcija eksperimenata niti B u čistom okruženju

**Stanje 2026-11-26:** Lovro je reproducirao B5, B6 i B7 prema
[podjeli rada](../plan/PODJELA.md), Z4, uz AI alat u svojoj sesiji. Ovo je zapis reprodukcije
tablica, a ne pregled izvoda B2 ni potvrda razumijevanja. Reprodukcija niti A (Sara) nije
dio ovog zapisa.

## 1. Postupak

1. Čist klon s GitHuba, grana `sara/b7-osjetljivost`, revizija `b6f1bd4` (vrh PR-a #29, bez
   dorada iz PR-a #31). Lokalne datoteke iz radne kopije nisu korištene, osim spremljene
   stranice WebNIR-a.
2. `uv sync --locked`: okruženje iz `uv.lock` (SHA-256 `45a43129…`), Python 3.12.3,
   NumPy 2.5.4, SciPy 1.18.1, OpenBLAS 0.3.34.
3. Podaci: `uv run python data/fetch_gabriel.py --offline` iz spremljenog HTML-a. CSV ima
   57 redaka i SHA-256 `0644be91…`, jednak zabilježenom u [podacima](../../data/README.md).
   Preuzimanje s WebNIR-a nije ponovljeno.
4. `uv run pytest`: 323 testa prolaze; `uv run ruff check .` prolazi.
5. Pokretanja, sva s čistim stablom na `b6f1bd4`, Linux x86_64:

   | zadatak | naredba | pokretanje | vrijeme |
   |---|---|---|---|
   | B5 | `experiments/min_order.py` | `20261126T085246317923Z-min_order` | 26 s |
   | B6 | `experiments/min_order.py --experiments final_base` | `20261126T085311855775Z-min_order` | 112 s |
   | B7 | `experiments/sensitivity.py` na ova dva pokretanja | `20261126T085533205051Z-sensitivity` | 1 s |

   Izlazi su lokalni i izvan Gita, kao što je opisano u [tijeku rada](../plan/PIPELINE.md).

## 2. Usporedba sa zapisima B5–B7

**Tablice se podudaraju u svakoj ćeliji:**

- [B5](b5-razvoj.md), §4: najmanji redovi za pet razvojnih skupina, četiri postupka i tri
  razine, uključujući raspone za pojasnu mjeru. Usporedba s probnim pokusom (§5) koristi iste
  brojeve.
- [B6](b6-najmanji-red.md), §2: najmanji / medijan / najveći red Debyejevih modela za oba VF
  postupka, obje mjere i tri razine. Nijedan postupak s fiksnim polovima ne daje Debyejev
  model.
- B6, §3: broj skupina s prolazom i najmanji / medijan / najveći red za sva četiri postupka
  s fiksnim polovima u općoj tablici.
- B6, §4: H1 vrijedi u svih 36 skupina, uz sve usporedbe kao u ispisu. Za H2 `quadvf_band`
  ima manji red u 33, 34 i 34 skupine (najveća relativna pogreška; 5 %, 1 %, 0,1 %) te u 32,
  33 i 32 skupine (pojasna mjera). U ostalima je red jednak, a nigdje veći. Medijani razlika
  su −2, −2 i −1, odnosno −1, −1 i −1. Za pojasnu mjeru uz 0,1 % fiksni polovi na pojasu
  prolaze u četiri skupine, s redovima 29–32; to potvrđuje ispravak iz PR-a #31.
- [B7](b7-osjetljivost.md), §2–§4: najveći omjeri pogrešaka za N (1,38 za `vf_log`, 1,15 za
  `fixed_log`, 1,00 za postupke na pojasnim čvorovima). Presuda se mijenja samo za Fat,
  r = 32, N = 120, uz 1 % najveće relativne pogreške. Podudaraju se i broj Debyejevih VF
  modela po rasponu početnih polova, svi brojevi uvjetovanosti po rasponima redova i uvjetovanost odabranih modela.

**Razlike, sve samo u statusima petlje:**

| | zapis | ova reprodukcija |
|---|---|---|
| B5, `vf_log` | 134 ustaljenih (18 s nazivnikom), 1 `cycle` | 131 (18), 4 `cycle` |
| B5, `quadvf_band` | 145 (10), 1 `cycle` | 144 (10), 2 `cycle` |
| B6, `vf_log` | 628 (131), 7 `cycle` | 626 (125), 9 `cycle` |
| B6, `quadvf_band` | 687 (79), 4 `cycle` | 684 (81), 7 `cycle` |
| B7, §2, promjene statusa `vf_log` uz N | 0 | 1 |
| B7, §3, `vf_log`, primarni raspon | 15 ustaljenih, 5 gubitak ranga | 14 ustaljenih, 1 `cycle`, 5 gubitak ranga |

Broj slučajeva s gubitkom ranga je isti (B6: 517 i 461; B5: 105 i 94). Iste brojeve B6 dao je i
lokalni pregled PR-a #28 (626 / 9 i 684 / 7). Razlike su dakle između Sarina radnog
prostora i ovog računala, a ne između dvaju pokretanja na istom računalu. Odgovaraju
opažanju 6 iz [A7](a7-konvergencija.md): kod većih redova razina šuma u δ približava se
pragu 10⁻⁸. Tada odluka između ustaljenja i kruženja ovisi o zaokruživanju. Nijedna razlika
ne mijenja kandidata odabranog u tablicama.

## 3. Zaključak i granice

Tablice B5–B7 reproduciraju se iz čistog klona i zaključanog okruženja. Brojevi statusa
petlje ne reproduciraju se točno među računalima. Seminar zato treba navoditi tablice kao
rezultat, a brojeve statusa kao približne, uz napomenu o ovisnosti o računalu.

Granice: ponovljeno je na jednom računalu i jednom operacijskom sustavu, bez Windowsa.
Podaci su izgrađeni iz spremljenog HTML-a, a ne ponovnim preuzimanjem. Ispis
`experiments/sensitivity.py` iz PR-a #31 (uvjetovanost po redu u širem rasponu) nije dio ove revizije.
Sarin izvorni zapis pokretanja nije dostupan na ovom računalu; usporedba se oslanja na
brojeve u njezinim zapisima.
