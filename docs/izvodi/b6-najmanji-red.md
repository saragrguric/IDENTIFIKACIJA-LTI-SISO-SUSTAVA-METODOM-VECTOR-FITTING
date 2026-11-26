# B6: najmanji pronađeni red na završnim skupinama

Zapis zadatka B6 ([plan B](../plan/podjela/b-sara.md)). Postavke su iz zaključanog plana Z2
([ADR-0008](../plan/adr/0008-accept-z2-experiment-plan.md), dodaci nakon A7 i B5); ovdje se ne
mijenjaju. Pokretač je `experiments/min_order.py` (porijeklo i pregled u
[zapisu B5](b5-razvoj.md), §1).

## 1. Pokretanje

    uv run python experiments/min_order.py --experiments final_base

Pokretanje `20261125T150024274524Z-min_order`: revizija `0b086d8` (nakon zaključavanja plana),
čisto stablo, Gabrielova tablica SHA-256 `0644be91…`, Linux u AI radnom prostoru. 36 završnih
skupina (47 naziva), 6912 slučajeva, 59 s ukupnog vremena prilagodbe. Nema procjena s
$\lvert E_\text{fino}-E_\text{grubo}\rvert>10^{-6}$ ni graničnih ćelija. Zapis svakog slučaja te CSV i tekstualni sažetak su u `results/runs/<run_id>/`, izvan Gita.

Statusi: fiksni polovi 4608 (svi riješeni); `vf_log` 628 ustaljenih (131 i s nazivnikom),
517 `rank_deficient`, 7 `cycle`; `quadvf_band` 687 ustaljenih (79 i s nazivnikom), 461
`rank_deficient`, 4 `cycle`. Gubitak ranga javlja se samo kod redova iznad najvećeg reda potrebnog za 0,1 % u istoj skupini;
takvi slučajevi ostaju u zapisu kao neuspjesi.

Pri ponavljanju brojevi statusa mogu ovisiti o računalu i numeričkim bibliotekama: prethodni
lokalni pregled PR-a #28 dao je 626 ustaljenih / 9 kruženja za `vf_log` i 684 / 7 za
`quadvf_band`, uz iste tablice najmanjih redova. Razlike su bile kod r ≥ 13. U reprodukciji
treba usporediti sve tablice i zabilježiti statuse odvojeno, bez prešućivanja razlika.

## 2. Glavni rezultat: Debyejevi modeli

Najmanji pronađeni broj Debyejevih članova (realni negativni polovi, strogo pozitivni reziduali)
preko 36 skupina, zapisan kao najmanji / medijan / najveći:

| postupak | mjera | 5 % | 1 % | 0,1 % |
|---|---|---|---|---|
| `vf_log` | najveća relativna pogreška $\varepsilon$ | 1 / 5 / 6 | 1 / 7 / 8 | 2 / 10 / 10 |
| `quadvf_band` | najveća relativna pogreška $\varepsilon$ | 1 / 4 / 5 | 1 / 6 / 6 | 2 / 8 / 9 |
| `vf_log` | $\mathcal{H}_2$ pogreška na pojasu | 1 / 4 / 5 | 1 / 6 / 7 | 2 / 8,5 / 9 |
| `quadvf_band` | $\mathcal{H}_2$ pogreška na pojasu | 1 / 3 / 4 | 1 / 5 / 6 | 2 / 7 / 8 |
| fiksni polovi (sva četiri) | obje | – | – | – |

Oba VF postupka prolaze u svih 36 skupina na svim razinama. Fiksni polovi ni u jednoj skupini
ne daju Debyejev model (reziduali nisu svi pozitivni ili LS gubi rang).

## 3. Opći realni modeli (referentna metoda)

U tablici općih realnih modela (bez uvjeta pozitivnih reziduala) fiksni polovi daju modele, ali s
mnogo više članova. Najveća relativna pogreška $\varepsilon$, broj skupina s prolazom i
najmanji / medijan / najveći red:

| postupak | 5 % | 1 % | 0,1 % |
|---|---|---|---|
| `fixed_log` (pojas) | 36: 15 / 18,5 / 23 | 27: 25 / 28 / 32 | 0 |
| `fixed_band` (pojas) | 36: 15 / 19,5 / 25 | 21: 23 / 28 / 32 | 0 |
| `fixed_log_wide` (1 kHz–100 GHz) | 36: 8 / 10 / 11 | 29: 10 / 11 / 12 | 0 |
| `fixed_band_wide` (1 kHz–100 GHz) | 36: 8 / 9 / 10 | 32: 10 / 11 / 12 | 0 |

VF postupci u općoj tablici imaju iste redove kao u Debyejevoj (§2).

## 4. Hipoteze (zapisane u planu prije rezultata)

- **H1 (VF treba manje polova od fiksnih polova): podržana.** U Debyejevoj tablici samo VF
  prolazi, pa su sve usporedbe jednostrane (36 od 36 skupina, sve razine, obje mjere i oba
  raspona fiksnih polova). U općoj tablici uz 5 % VF ima manji red u svih 36 skupina, i prema
  širem rasponu; uz 1 % manji red ili jedini prolaz u svih 36. Uz 0,1 % najveće relativne
  pogreške prolazi samo VF. Za pojasnu mjeru fiksni polovi na pojasu prolaze u četiri skupine
  s redovima 29–32, a VF i tada treba manji red.
- **H2 (manja medijalna razlika redova za pojasnu mjeru): podržana.** Kako je unaprijed
  formulirano u Z2, §1, uspoređuje se pojasna mjera: medijan razlike
  r(`quadvf_band`) − r(`vf_log`) je −1 na svim razinama. QuadVF ima manji red u 32–33 od 36
  skupina, jednak u ostalima, a nigdje veći. Dodatno opažanje za najveću relativnu pogrešku:
  medijan razlike je −2 za 5 % i 1 %, a −1 za 0,1 %; manji red u 32–34 skupine. Taj ishod
  za relativnu pogrešku nije bio pretpostavljen u H2.
- **H3 (red raste s najvećim aktivnim α): istraživačka, slab trend.** Tkiva s većim α češće
  trebaju 8 umjesto 7 članova za 1 %, ali trend nije strog i ne pokazuje uzročnost.

## 5. Ograničenja

- Brojevi su **najmanji pronađeni** redovi za ove postupke i postavke, a ne dokaz da manji red
  ne postoji (AGENTS.md, pravilo 2). Ustaljeni polovi nisu dokaz optimalnosti.
- Jedan pojas (10 MHz–10 GHz), jedan način početnih polova i $N=240$. Zaključak ovisi o
  početnom rasponu: uz širi početni raspon VF petlja većinom gubi rang (B5, §4).
- Završne skupine nisu slijepe: sve skupine pregledane su u B3, a postavke nisu birane prema
  njima. Završni pokus ranije je pokrenut i viđen na grani `lovro/b6-min-order` (PR #25); ovo
  pokretanje na zaključanom planu daje iste tablice, a postavke nisu mijenjane ni prema njemu.
- QuadVF je naša prilagodba konačnom pojasu (B2, §6), pa tvrdnje L1 o QuadVF-u nisu izravno
  provjerene; H2 vrijedi za ovu prilagodbu.
- Fiksni polovi s pozitivnim rezidualima nisu bili cilj referentne metode; zato je njezina
  usporedba prikazana i u općoj tablici.
