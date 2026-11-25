# B6: pokretač najmanjeg reda i razvojno pokretanje

**Stanje 2026-11-25:** `experiments/min_order.py` provodi plan Z2 s dodatkom nakon A7
([ADR-0008](../plan/adr/0008-accept-z2-experiment-plan.md)). Razvojni pokusi su pokrenuti
(`20261125T094340378378Z-min_order`, revizija `4a16801`, čisto stablo). Nakon zaključavanja
plana pokrenut je i završni pokus (`20261125T094751901934Z-min_order`, revizija `c63caea`,
čisto stablo; odjeljak 5). Nositeljica B6 je Sara; pokretač je napisao AI alat na Lovrin
zahtjev, a Sara još nije pregledala ni njega ni rezultate.

## 1. Što pokretač radi

- **Skupine:** disperzivna tkiva s istim parametrima čine jednu skupinu koja se računa jednom.
  Pet razvojnih skupina (8 naziva) i 36 završnih (47 naziva) izračunava se iz tablice. Air i
  Vacuum nemaju relativnu pogrešku (H = 0) i izostavljaju se s napomenom.
- **Postupci:** `vf_log` i `quadvf_band` (`vector_fit` s kontrolama iz §5) te `fixed_log` i
  `fixed_band` (`baseline.fit_residues`) iz istih logaritamskih polova na 10 MHz–10 GHz. Uz
  njih idu `fixed_log_wide` i `fixed_band_wide` s polovima na 1 kHz–100 GHz.
- **Pokusi:** `dev_base` (960), `dev_nodes` (N = 120 i 480, 160), `dev_start` (160) i
  `final_base` (6912), kako navodi dodatak ADR-0008. Test provjerava te brojeve i
  nepromijenjen broj VF slučajeva (2784).
- **Vrednovanje (§6):** gruba i fina procjena za obje mjere. Za najveću relativnu pogrešku to
  su krajevi pojasa i 4096 odnosno 8192 sredina ćelija u ln f i u f; za pojasnu pogrešku 512 i
  1024 čvora `band_nodes`. Prolaz traži E_fino + abs(E_fino − E_grubo) ≤ razina. Slučaj je pad
  ako je E_fino − abs(E_fino − E_grubo) > razina, a inače granični. Razlika veća od 10⁻⁶
  označava se kao nerazriješena.
- **Zapis:** svaki slučaj odmah se sprema kao zasebna JSON datoteka u direktoriju pokretanja.
  `--resume-from` preuzima gotove slučajeve ranijeg pokretanja s istim identitetom postavki i
  ulaza i bilježi vezu `reused_from`. Drukčije postavke prekidaju pokretanje.
- **Sažetak:** min_order.csv (najmanji r po skupini, postupku, tablici, mjeri i razini, uz
  granične manje redove), min_order.txt (tablice, H1–H3) i provenance.json.

## 2. Tumačenja koja plan nije potpuno odredio

Ovo su izbori pri provedbi, a ne nove odluke tima; mijenjaju se dodatkom ADR-0008 prije
završnog pokusa.

1. **Uvjetovanost ≤ 10¹²** traži se za svaku rješavanu LS matricu kandidata: za svaki korak
   petlje i za završni LS. Kod fiksnih polova postoji samo završni LS.
2. **Ustaljena petlja** znači status `poles_settled` ili `poles_and_denominator_settled`.
   Kruženje, iscrpljene iteracije, gubitak ranga i nevaljani polovi su neuspjesi.
3. **H1, „više od polovice”:** VF se broji kao manji kad ima manji red ili kad prolazi samo
   VF. Izjednačenja se ne broje. Sve kategorije ispisuju se zasebno, pa je moguće i drugo
   čitanje.
4. **H2:** medijan razlike r(`quadvf_band`) − r(`vf_log`) preko skupina u kojima oba prolaze,
   uz zasebno prebrojane jednostrane prolaze; negativan medijan znači manje polova uz QuadVF.
5. **Nulti rezidual** se bilježi u zapisu slučaja; Debyejev model ga isključuje. Za „gotovo
   poništen pol” nema definiranog praga, pa se ne označava.
6. U `dev_nodes` i `dev_start` najmanji r traži se samo među r = 4, 8, 16 i 32.

## 3. Razvojni rezultati

Sva opažanja odnose se na pet razvojnih skupina i nisu završni rezultat.

- **Trošak:** 1280 slučajeva za 35 s. Završni pokus ima 6912 slučajeva, pa se procjenjuje na
  nekoliko minuta.
- **Razlučivost:** nijedna procjena nema razliku fine i grube veću od 10⁻⁶; graničnih
  slučajeva nema.
- **Najmanji Debyejev red uz najveću relativnu pogrešku:** `vf_log` 5–6 za 5 %, 7–8 za 1 % i
  9–10 za 0,1 %; `quadvf_band` 3–4, 5–6 i 7–8. Uz pojasnu pogrešku redovi su jednaki ili
  manji za jedan do dva.
- **Fiksni polovi:** nemaju nijedan Debyejev model ispod 5 %. U općoj tablici `fixed_*_wide`
  postižu 5 % kod r = 8–10, a primarni fiksni polovi tek kod r = 15–25. Za 0,1 % nijedan
  postupak s fiksnim polovima ne prolazi do r = 32.
- **H1** je na razvojnim skupinama podržan u svih 48 usporedbi: obje tablice, obje mjere,
  tri razine i četiri para VF-a i fiksnih polova. Većinom prolazi samo VF; u općoj tablici uz
  5 % VF ima i manji red od fiksnih polova sa širim rasponom.
- **H2:** medijan r(`quadvf_band`) − r(`vf_log`) je −2 za najveću relativnu pogrešku i −1 za
  pojasnu pogrešku na sve tri razine.
- **Osjetljivost:** N = 120 i N = 480 daju iste najmanje redove među r = 4, 8, 16, 32. Šira
  početna područja ponavljaju nalaz A7: VF za r ≥ 8 većinom ne prolazi.

## 4. Razvojni kriteriji iz §7 i završni pokus

Prema §7 plan se zaključava kad su ispunjeni ovi kriteriji:

| Kriterij | Stanje |
|---|---|
| Analitički testovi prolaze | 318 numeričkih testova prolazi |
| Nema skrivenih intervencija | Statusi i neuspjesi su u zapisu svakog slučaja; ništa se ne popravlja prešutno |
| Gustoća kontrolnog vrednovanja | 0 nerazriješenih procjena |
| Podrijetlo omogućuje ponavljanje | Čista revizija, kontrolni zbroj ulaza i identitet postavki u zapisu |
| Trošak izmjeren | 35 s za 1280 razvojnih slučajeva |

Kriteriji su ispunjeni. Lovro je 2026-11-25 uputio da se plan zaključa (dodatak ADR-0008),
pa se završni pokus pokreće naredbom:

```bash
uv run python experiments/min_order.py --experiments final_base
```

Nakon zaključavanja postavke se više ne mijenjaju prema završnim pogreškama.

## 5. Završni rezultati

Pokretanje `20261125T094751901934Z-min_order` obuhvaća 36 završnih skupina (47 naziva) i
6912 slučajeva te traje 135 s. Nema nerazriješenih procjena ni graničnih slučajeva. Brojevi
vrijede za Gabrielov model na pojasu 10 MHz–10 GHz, a ne za nova mjerenja tkiva. Redovi su
najmanji *pronađeni*, ne dokazano najmanji mogući.

**Najmanji Debyejev red** (najmanji / medijan / najveći preko 36 skupina):

| Postupak i mjera | 5 % | 1 % | 0,1 % |
|---|---|---|---|
| `vf_log`, najveća relativna pogreška | 1 / 5 / 6 | 1 / 7 / 8 | 2 / 10 / 10 |
| `quadvf_band`, najveća relativna pogreška | 1 / 4 / 5 | 1 / 6 / 6 | 2 / 8 / 9 |
| `vf_log`, pojasna pogreška | 1 / 4 / 5 | 1 / 6 / 7 | 2 / 8,5 / 9 |
| `quadvf_band`, pojasna pogreška | 1 / 3 / 4 | 1 / 5 / 6 | 2 / 7 / 8 |

Svaka skupina ima prolaz za oba VF postupka na svim razinama. Nijedan postupak s fiksnim
polovima, ni u jednom rasponu, ne daje Debyejev model ni u jednoj skupini.

**Opća tablica, fiksni polovi** (najveća relativna pogreška; u zagradi broj skupina bez prolaza):

| Postupak | 5 % | 1 % | 0,1 % |
|---|---|---|---|
| `fixed_log` | 15 / 18,5 / 23 | 25 / 28 / 32 (9) | nijedan (36) |
| `fixed_band` | 15 / 19,5 / 25 | 23 / 28 / 32 (15) | nijedan (36) |
| `fixed_log_wide` | 8 / 10 / 11 | 10 / 11 / 12 (7) | nijedan (36) |
| `fixed_band_wide` | 8 / 9 / 10 | 10 / 11 / 12 (4) | nijedan (36) |

Za VF postupke opća tablica daje iste redove kao Debyejeva.

**H1** je podržan u svih 48 usporedbi. U Debyejevoj tablici svih 36 skupina su jednostrani
prolazi VF-a, jer fiksni polovi nemaju nijedan Debyejev model. Taj dio zato govori o
predznaku reziduala fiksnih polova, a ne samo o broju polova. Usporedbu redova daje opća
tablica prema jačoj referentnoj metodi:
- uz 5 % VF ima manji red u svih 36 skupina, za obje mjere;
- uz 1 % i najveću relativnu pogrešku manji red ima u 29 (`vf_log`) odnosno 32 (`quadvf_band`)
  skupine, a u ostalima prolazi samo VF;
- uz 1 % i pojasnu pogrešku manji red ima u 34 odnosno 35 skupina;
- uz 0,1 % prolazi samo VF.

**H2:** u svih 36 skupina prolaze oba postupka. Medijan r(`quadvf_band`) − r(`vf_log`) je −2
za najveću relativnu pogrešku uz 5 % i 1 % te −1 uz 0,1 %. Za pojasnu pogrešku iznosi −1 na
sve tri razine. To je opažanje na ovom modelu, a ne opći teorem o QuadVF-u.

**H3, istraživački:** najveći aktivni α i najmanji Debyejev red `vf_log` za 1 % (najveća
relativna pogreška). Uz α ≤ 0,1 redovi su 1–7, uz α = 0,2 su 4–8, a uz α ≥ 0,25 su 8. Trend
raste, ali nije strog: uz α = 0,15 red je 8, a uz α = 0,18 red je 7. Vremena τ, jakosti Δε i
položaj prema pojasu nisu držani stalnima, pa ovo nije uzročni zaključak.

**Ograničenja.**
- Najveća pogreška na mreži nije potvrđena kontinuirana H∞ pogreška, a pojasna norma nije puna
  H2 norma.
- Razvojne skupine bile su viđene ranije (B3), ali završne skupine nisu korištene za
  podešavanje.
- Rezultat ne govori o točnosti prema novim mjerenjima tkiva.

## 6. Slike za seminar

`experiments/figures.py` crta četiri slike iz zabilježenih pokretanja i zapisuje izvore u
provenance. Pokretanje `20261125T100131023934Z-figures` (revizija `f98453b`, čisto stablo)
koristi završni pokus `20261125T094751901934Z-min_order` i A7 pokretanje
`20261125T090048328276Z-convergence`. Svaka slika ima PDF za Overleaf i PNG za pregled, a
figures.txt sadrži sve prikazane vrijednosti kao tablice. Boje su provjerene validatorom
palete na bijeloj podlozi; svijetle nijanse imaju kontrast ispod 3:1, pa svaku seriju imenuje
legenda.

Prijedlozi opisa slika:

1. **fig_udio_skupina:** udio 36 završnih skupina tkiva za koje postupak nalazi prihvatljiv
   model reda najviše r, za obje mjere pogreške i tri razine točnosti. Prikazana je opća
   tablica; za VF i QuadVF ona je jednaka Debyejevoj, a fiksni polovi Debyejev model ne daju.
2. **fig_pogreska_red:** najveća relativna pogreška i relativna pogreška na pojasu za jetru
   (Liver) u ovisnosti o redu r. Vodoravne crte su razine 5 %, 1 % i 0,1 %. Prikazani su samo
   prihvatljivi kandidati; linija prestaje kad petlja gubi rang ili je uvjetovanost veća od
   10¹².
3. **fig_putanja:** relativni pomak polova δk i odmak pomoćnog nazivnika qk tijekom VF
   iteracije za krv (`vf_log`, početni polovi 10 MHz–10 GHz) uz r = 4, 7 i 10. Prag
   zaustavljanja je 10⁻⁸. Nakon ustaljenja obje veličine ostaju na razini šuma koja raste s r.
4. **fig_raspon:** broj razvojnih skupina (od pet) u kojima se VF petlja ustali, za tri
   raspona početnih polova. Uz šire raspone petlja se prestaje ustaljivati od r = 6–9, zbog
   gubitka ranga već u prvom koraku (A7).
