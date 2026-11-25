# B6: pokretač najmanjeg reda i razvojno pokretanje

**Stanje 2026-11-25:** `experiments/min_order.py` provodi plan Z2 s dodatkom nakon A7
([ADR-0008](../plan/adr/0008-accept-z2-experiment-plan.md)). Razvojni pokusi su pokrenuti
(`20261125T094340378378Z-min_order`, revizija `4a16801`, čisto stablo). Završni pokus
`final_base` nije pokrenut: čeka da tim zaključa plan. Nositeljica B6 je Sara; pokretač je
napisao AI alat na Lovrin zahtjev, a Sara ga još nije pregledala.

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
