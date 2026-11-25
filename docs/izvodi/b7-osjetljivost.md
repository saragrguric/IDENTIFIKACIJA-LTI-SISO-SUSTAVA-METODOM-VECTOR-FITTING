# B7: osjetljivost na čvorove i početne polove, uvjetovanost

Zapis zadatka B7 ([plan B](../plan/podjela/b-sara.md)) u smanjenom opsegu. Pokusi osjetljivosti
iz §7 plana Z2 ([ADR-0008](../plan/adr/0008-accept-z2-experiment-plan.md)) već su provedeni u
razvojnom pokretanju B5 (`dev_nodes`, `dev_start`). Završni brojevi uvjetovanosti zapisani su u
pokretanju B6. Zato B7 ne radi nove prilagodbe: `experiments/sensitivity.py` čita zapise
slučajeva tih dvaju pokretanja i sažima ih.

## 1. Pokretanje

    uv run python experiments/sensitivity.py \
        --dev-run results/runs/20261125T144135977334Z-min_order \
        --final-run results/runs/20261125T150024274524Z-min_order

Pokretanje `20261125T151857241449Z-sensitivity`, revizija `c92c203`, čisto stablo. Ulazi su
pokretanja B5 (`20261125T144135977334Z-min_order`, razvojne skupine) i B6
(`20261125T150024274524Z-min_order`, 36 završnih skupina). Tekstualni sažetak spremljen je uz
zapis pokretanja, izvan Gita.

## 2. Broj čvorova N

Pet razvojnih skupina, redovi 4, 8, 16 i 32, početni polovi 10 MHz–10 GHz. Uspoređeni su
$N=120$ i $N=480$ s primarnim $N=240$ (40 parova po postupku).

| postupak | promjena statusa | promjena Debyejeva svojstva | promjena presude | najveći omjer pogrešaka |
|---|---|---|---|---|
| `vf_log` | 0 | 0 | 1 | 1,38 |
| `quadvf_band` | 0 | 0 | 0 | 1,00 |
| `fixed_log` | 0 | 0 | 1 | 1,15 |
| `fixed_band` | 0 | 0 | 0 | 1,00 |

Jedina promjena presude je Fat, $r=32$, $N=120$, za 1 % najveće relativne pogreške. Taj VF
slučaj gubi rang u prvom koraku, pa vraća model na početnim polovima, isti kao `fixed_log`. Na
redovima koji određuju rezultat B6 (do 10) nijedna presuda se ne mijenja. Postupci na pojasnim
čvorovima Gauss–Legendre gotovo ne ovise o N (omjer 1,00). Logaritamski čvorovi s jednakim
težinama mijenjaju pogrešku do 38 %, ali bez promjene presude.

**Zaključak:** izbor $N=240$ ne mijenja zaključke B6.

## 3. Početni polovi

Iste skupine i redovi, $N=240$. Broj slučajeva po statusu (od 20):

| postupak | 10 MHz–10 GHz (primarni) | 1 kHz–100 GHz | 1 Hz–1 THz |
|---|---|---|---|
| `vf_log` | 15 ustaljenih, 5 gubitak ranga ($r=32$) | 8 / 12 (gubitak ranga od $r=8$) | 5 / 15 (od $r=8$) |
| `quadvf_band` | 15 / 5 ($r=32$) | 10 / 10 (od $r=16$) | 5 / 15 (od $r=8$) |

Debyejevih modela s VF-om: 13 i 15 (primarni), 7 i 7 (1 kHz–100 GHz), 5 i 5 (1 Hz–1 THz).
Fiksni polovi daju modele uz svaki raspon, ali ne Debyejeve, osim jednog slučaja bez prolaza.

**Zaključak:** rezultat ovisi o početnom rasponu. Uz šire raspone VF gubi rang već u prvom
koraku, pa redovi potrebni za 1 % i 0,1 % nisu dostupni. To je razlog odluke o primarnom
rasponu iz dodatka ADR-0008 nakon A7. Zato tvrdnje B6 vrijede za početne polove na pojasu.

## 4. Uvjetovanost matrica najmanjih kvadrata

Za svaki slučaj `experiments/min_order.py` bilježi najveći broj uvjetovanosti LS matrica u svim koracima.
Za VF je to $[C,\,-\operatorname{diag}(h)\,C]$ s težinama redaka, a za fiksne polove $C$. Ispod
su medijan i najveća konačna vrijednost na 36 završnih skupina:

| postupak | $r=1$–4 | $r=5$–8 | $r=9$–16 | $r=17$–32 | iznad $10^{12}$ / gubitak ranga |
|---|---|---|---|---|---|
| `vf_log` | 4e5 / 2e7 | 2e7 / 3e10 | 1e10 / 9e12 | 3e12 / 9e12 | 71 / 517 |
| `quadvf_band` | 4e4 / 8e6 | 4e6 / 5e9 | 2e9 / 3e12 | 1e12 / 9e12 | 67 / 461 |
| `fixed_log` | 3e2 / 5e2 | 1e3 / 3e3 | 4e4 / 3e5 | 8e7 / 1e10 | 0 / 0 |
| `fixed_band` | 3e1 / 4e1 | 1e2 / 3e2 | 4e3 / 4e4 | 1e7 / 2e9 | 0 / 0 |
| `fixed_log_wide` | 3e3 / 5e3 | 1e5 / 4e6 | 2e12 / 2e16 | 3e16 / 7e16 | 720 / 0 |
| `fixed_band_wide` | 4e2 / 5e2 | 1e5 / 4e6 | 3e12 / 2e16 | 2e16 / 5e16 | 720 / 0 |

Odabrani Debyejevi modeli iz B6 su dobro ispod praga $10^{12}$. Za najveću relativnu pogrešku
$\varepsilon$ medijan i najveća vrijednost su:
- `quadvf_band`: $8\cdot10^4$ i $2\cdot10^5$ (5 %), $9\cdot10^5$ i $4\cdot10^6$ (1 %), $3\cdot10^7$ i $1\cdot10^8$ (0,1 %);
- `vf_log`: $4\cdot10^6$ i $2\cdot10^7$ (5 %), $6\cdot10^7$ i $3\cdot10^8$ (1 %), $8\cdot10^8$ i $3\cdot10^9$ (0,1 %).

Za pojasnu mjeru vrijednosti su manje.

**Zaključak:**
- Uvjetovanost raste s redom, a najbrže kod fiksnih polova u širem rasponu: medijan je
  $4\cdot10^6$ kod $r=8$, $3\cdot10^{11}$ kod $r=12$ i $4\cdot10^{12}$ kod $r=13$, a iznad
  toga do $10^{16}$. Redovi 8–12 koje tablica općih modela u B6 bira za te postupke ostaju
  ispod praga, ali se reziduali kod $r=11$–12 dobivaju iz matrice s brojem uvjetovanosti
  $10^{10}$–$10^{11}$.
- VF matrice su lošije uvjetovane od matrica fiksnih polova istog reda jer stupci
  $\operatorname{diag}(h)\,C$ imaju drukčiju skalu od $C$. Gubitak ranga javlja se tek iznad
  redova potrebnih za 0,1 % (B6, §1).
- QuadVF ima oko red veličine manju uvjetovanost od `vf_log` na istom redu. To je opažanje na
  ovim podacima, a ne dokazano svojstvo.

## 5. Što nije napravljeno

Skaliranje i redanje redaka LS matrice (L1, §4.3) nisu ispitani. Zbog roka je taj dio B7
izostavljen prema redoslijedu rezanja iz plana. Nijedan model odabran u tablicama B6 (Debyejeva i
opća, svi postupci) nije označen kao `ill_conditioned`, pa uvjetovanost ne mijenja te tablice.
