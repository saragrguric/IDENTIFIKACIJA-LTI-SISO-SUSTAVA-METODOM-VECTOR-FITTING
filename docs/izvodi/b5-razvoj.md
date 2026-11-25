# B5: razvojni pokusi i razvojni kriteriji plana Z2

Zapis zadatka B5 ([plan B](../plan/podjela/b-sara.md)). Postavke su iz prihvaćenog plana Z2
([ADR-0008](../plan/adr/0008-accept-z2-experiment-plan.md) s dodatkom nakon A7) i ovdje se ne
mijenjaju. Rezultati na razvojnim skupinama nisu rezultati seminara; služe provjeri plana prije
zaključavanja (Z2, §7).

## 1. Pokretač i njegovo porijeklo

`experiments/min_order.py` i `tests/test_min_order.py` preuzeti su bez izmjena s grane
`lovro/b6-min-order` (stanje `f98453b`, zatvoreni PR #25). Napisao ih je AI alat u Lovrinoj
sesiji. AI alat u Sarinoj sesiji pregledao ih je 2026-11-25 prema planu Z2: skupine po
parametrima, isti logaritamski početni polovi za sve postupke, kontrole petlje iz ADR-0008, §5,
presude prolaz / granično / pad s grubom i finom mrežom (§6), kandidat se broji samo uz
ustaljenu petlju ili fiksne polove, puni rang, uvjetovanost najviše $10^{12}$, stabilan i realan
odziv, a za Debyejevu tablicu uz realne negativne polove i strogo pozitivne reziduale. Pogreška
nije nađena. Sara je pokretač preuzela kao svoj B5/B6 pokretač i za njega odgovara.

Završni pokus s grane #25 ranije je pokrenut i viđen. Ovaj zapis ga ne koristi, a postavke se
prema njemu ne mijenjaju (`docs/plan/TASKS.md`).

## 2. Pokretanje

    uv run python experiments/min_order.py        # razvojni pokusi dev_base, dev_nodes, dev_start

Pokretanje `20261125T144135977334Z-min_order`: revizija `8324725`, čisto stablo, Gabrielova
tablica SHA-256 `0644be91…`, Linux u AI radnom prostoru. Zapis svakog slučaja je u
`results/runs/<run_id>/cases/`, izvan Gita. Isto pokretanje s necommitanim stablom dalo je iste
tablice.

## 3. Razvojni kriteriji (Z2, §7)

| kriterij | provjera | ispunjen |
|---|---|---|
| svojstva analitičkih testova prolaze | `uv run pytest`: 319 testova (uz lokalnu tablicu), među njima točan oporavak sintetičkog Debyejeva tkiva u pokretaču | da |
| nema skrivenih intervencija | pokretač ne odbacuje uzorke ni polove, ne spaja, ne pomiče i ne zaokružuje polove ili reziduale; zrcaljenje je izričito i bilježi se; svaki neuspjeh ima oznaku | da |
| gustoća vrednovanja daje razlučivost | 0 procjena s $\lvert E_\text{fino}-E_\text{grubo}\rvert>10^{-6}$; 0 graničnih ćelija tablice | da |
| podrijetlo omogućuje ponavljanje | roditeljski zapis s identitetom postavki i ulaza, zaseban zapis svakog slučaja, nastavak nakon prekida s istim identitetom | da |
| trošak je izmjeren | 1280 razvojnih slučajeva, 12 s ukupnog vremena prilagodbe; završni pokus ima 6912 slučajeva, dakle reda veličine minute | da |

Statusi slučajeva: fiksni polovi 800 (svi riješeni); `vf_log` 134 ustaljenih (od toga 18 i s
nazivnikom), 105 `rank_deficient`, 1 `cycle`; `quadvf_band` 145 ustaljenih (10 i s
nazivnikom), 94 `rank_deficient`, 1 `cycle`. Gubitak ranga javlja se kod velikih $r$ i širih
početnih raspona, kao u A7; takvi slučajevi ostaju u zapisu kao neuspjesi.

## 4. Razvojni rezultati (nisu rezultati seminara)

Najmanji red koji prolazi, najveća relativna pogreška $\varepsilon$, za 5 %, 1 % i 0,1 % (Debyejeva
tablica; opća tablica daje iste brojeve za VF postupke, a fiksni polovi samo u njoj):

| skupina | `vf_log` | `quadvf_band` | `fixed_log` | `fixed_log_wide` |
|---|---|---|---|---|
| Blood | 5 / 7 / 10 | 3 / 6 / 8 | 17 / 27 / – | 10 / 11 / – |
| Bone cortical | 6 / 7 / 10 | 4 / 6 / 8 | 15 / 25 / – | 8 / – / – |
| Fat | 5 / 7 / 9 | 3 / 5 / 7 | 21 / – / – | 8 / 10 / – |
| Muscle | 5 / 7 / 10 | 3 / 5 / 8 | 23 / – / – | 10 / 11 / – |
| Skin wet | 6 / 8 / 10 | 4 / 6 / 8 | 22 / – / – | 10 / 11 / – |

(„–”: nijedan $r$ do 32 ne prolazi; brojevi za fiksne polove iz opće tablice, jer fiksni polovi
ni jednom ne daju Debyejev model.) Za pojasnu normu `quadvf_band` treba 3–4 / 5 / 7, a `vf_log`
4–5 / 6 / 8–9.

**Osjetljivost** (redovi 4, 8, 16, 32, kako plan predviđa):

- *Broj čvorova* $N=120$ i $480$: `quadvf_band` daje iste zaključke kao uz $N=240$ (na grubljoj
  mreži redova). `vf_log` uz 0,1 % kod krvi i mišića ne prolazi ni s $r=16$ ni s $r=32$, jer ti
  slučajevi završe gubitkom ranga; to je posljedica grube mreže redova i gubitka ranga, a ne
  dokaz da $N$ mijenja potreban red.
- *Početni raspon*: uz 1 Hz–1 THz i 1 kHz–100 GHz VF petlja kod većine skupina već od $r=8$
  završi gubitkom ranga, pa uz 1 % i 0,1 % uglavnom nema prolaza; `quadvf_band` uz $r=4$ i dalje
  prolazi 5 %. **Zaključak bitno ovisi o početnom rasponu**: to je rezultat za prikaz (Z2, §7) i
  razlog primarnog raspona 10 MHz–10 GHz iz dodatka ADR-0008.

## 5. Usporedba s probnim pokusom iz prijedloga teme

Probni pokus (Sarin prijedlog teme, PDF izvan repozitorija; kod nije u repozitoriju po
odluci od 2026-11-10) koristio je isti pojas, $N=40$ čvorova, najveću relativnu pogrešku $\varepsilon$ na
4000 točaka i QuadVF s parametrom $L$. Najmanji red za 1 % i 0,1 %:

| | krv, probni | krv, B5 | mišić, probni | mišić, B5 |
|---|---|---|---|---|
| VF, log. čvorovi | 7 / 9 | 7 / 10 | 7 / 9 | 7 / 10 |
| QuadVF | 6 / 9 ($L=1$); 5 / 7 ($L=3$) | 6 / 8 | 5 / 9 ($L=1$); 5 / 8 ($L=3$) | 5 / 8 |
| fiksni log. polovi | 12 / 20 | 27 / – (pojas); 11 / – (širi) | 17 / > 24 | – / – (pojas); 11 / – (širi) |

VF i QuadVF slažu se do jednog reda. Razlike uz 0,1 % objašnjavaju strože pravilo prolaza
(gruba i fina mreža), zahtjev ustaljene petlje i uvjetovanosti te gušći čvorovi ($N=240$).
Fiksni polovi u probnom pokusu nisu bili ograničeni na pojas; s pojasom kao rasponom trebaju
mnogo više polova, a sa širim rasponom 1 kHz–100 GHz broj je blizak probnom. QuadVF iz B5 nema
parametar $L$ (B2, §6), pa se ne uspoređuje izravno s varijantama $L=1$ i $L=3$.

## 6. Zaključak

Svih pet razvojnih kriterija je ispunjeno, pa se plan Z2 može zaključati bez izmjena
(dodatak ADR-0008). Osjetljivost na početni raspon prikazuje se uz rezultate B6.
