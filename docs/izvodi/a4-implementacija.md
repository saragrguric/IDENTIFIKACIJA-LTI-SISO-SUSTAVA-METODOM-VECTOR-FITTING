# A4: parametarska VF petlja i provjera cijelog poziva

**Stanje 2026-11-23:** na Lovrin zahtjev da nastavi programski rad pripremljena je puna
petlja `vfdebye.vf.vector_fit` na grani `lovro/a4-vf-petlja`. Nastavlja provjerene operacije
[A5](a5-polovi-reziduali.md), bez preuzimanja neobjavljenoga B1 ili odabira konačnih
postavki Z2. Usporedba sa Sarinim probnim kodom, njezin pregled i prihvat A4 ostaju otvoreni.
Ovo nije reprodukcija njezina probnog pokusa ni konačan eksperiment na tkivima.

## 1. Matematika i odabiri pozivatelja

LS korak, premještanje i završni reziduali slijede L1, §2.2 i §4.2; izvod i provjera
predznaka su u A5. Fiksne vanjske težine množe kvadrat pogreške, pa retke LS matrice
množimo njihovim korijenom. Jedna funkcija zato podržava VF s jediničnim težinama i
kvadraturno težinski VF bez zasebne implementacije. Ne uključuje rubni redak izvornog
QuadVF-a na cijeloj osi. Čvorove i težine bira pozivatelj.

Potpis je `vector_fit(s, h, weights, poles0, ...)`, prema zajedničkom sučelju. Sve sljedeće
kontrole obvezne su imenovane vrijednosti, bez zadanih znanstvenih postavki:

| Parametar | Značenje |
|---|---|
| `max_iterations` | Pozitivna najveća dopuštena količina baricentričnih LS koraka |
| `pole_rtol` | Nenegativna relativna tolerancija pomaka skupa polova |
| `pole_atol` | Nenegativna apsolutna tolerancija pomaka, u rad/s |
| `reflect_unstable` | Izričit izbor refleksije nakon svakog premještanja |
| `settle_steps` | Broj uzastopnih malih pomaka za opaženo ustaljenje |
| `max_period` | Najveći provjeravani period ≥ 2; nula isključuje provjeru kruženja |
| `cycle_repeats` | Broj uzastopnih povrataka potreban za prijavu perioda |

Za stare polove a i nove b koristi se Ω iz L1 (4.3), uz uparivanje neovisno o poretku.
Mali pomak znači

$$
\Omega(a,b)\le \texttt{pole\_atol}+
\texttt{pole\_rtol}\,\max_j|a_j|.
$$

To je programski kriterij sa skalom cijelog skupa, ne komponentna relativna udaljenost
staroga pomoćnika `detect_period`. Tako se može obraditi i početni pol nula bez dijeljenja
nulom. Pri promjeni jedinice s istim faktorom mijenjaju se polovi i `pole_atol`; relativna
tolerancija ostaje ista. Prag i broj ponavljanja moraju biti zapisani u postavkama pokretanja.

Provjera perioda uspoređuje zadnji skup sa skupom p koraka prije, taj skup s prethodnim
odmaknutim p koraka itd., ukupno `cycle_repeats` povrataka. Ista granica pomaka vrijedi
za svaki par, skalirana njegovim ranijim skupom. Najmanji potvrđeni p ≥ 2 prijavljuje se
kao period. Uzastopno ustaljenje ima prednost pred oznakom kruženja. To su opažanja
povijesti, ne dokaz periodičnog graničnog ponašanja ni konvergencije.

## 2. Povijest, stabilizacija i neuspjesi

Svaki `VFIteration` sadrži početni skup polova i cijeli `BarycentricStep`: koeficijente
brojnika/nazivnika, numerički rang, uvjetovanost i linearizirani težinski rezidual.
Kad su koraci dosegnuti, pohranjuju se sirovi premješteni polovi, upotrijebljeni polovi
nakon refleksije, broj refleksija, Ω i
`max_i abs(d_tilde(s_i) − 1)`. Neizvedena operacija ima vrijednost `None`; ne izmišlja se
dijagnostika nakon neuspjeha. Povijest i njezina polja polova/koeficijenata imaju zasebne
snimke koje nisu zapisive; ulazi pozivatelja ne mijenjaju se.

Refleksija se primjenjuje samo uz izričitu zastavicu i čvorove na imaginarnoj osi, prema
pretpostavci Propozicije 4.1 iz L1. Početne pomoćne točke nisu prešutno reflektirane.
Koristi se λ → −conj(λ) za Re λ > 0. Točke na osi i duplikati koji nastanu refleksijom
ne pomiču se i ne spajaju. S isključenom refleksijom mogući su nestabilni modeli; to je
vidljivo iz povijesti i `model.is_stable()`. Kompleksni parovi i negativni reziduali ne
pretvaraju se u Debyejeve članove.

| `stop_reason` | Značenje |
|---|---|
| `poles_settled` | Zadan broj uzastopnih malih pomaka; nije potvrda točnosti ili optimalnosti |
| `max_iterations` | Iscrpljen dopušten broj koraka; nije oznaka uspjeha |
| `cycle` | Potvrđeni povratci s periodom `cycle_period` |
| `rank_deficient` | LS matrica ima numerički rang manji od 2r; nema nastavka s proizvoljnim polovima |
| `invalid_relocated_poles` | Nova baza nevaljana: npr. podudaranje čvora i pola, duplikat ili pol na osi uz refleksiju |
| `numerical_failure` | Numerička operacija nije završila; poruka navodi korak i izvorni razlog |

Nevaljan početni ulaz izaziva `ValueError` prije iteracije. To se razlikuje od neuspjeha
valjano zadanog numeričkog postupka. Uvjetovanost se bilježi bez automatskog praga,
regularizacije ili skaliranja redaka; prihvatljiv prag odlučuje eksperiment.

Nakon zaustavljanja `fit_fixed_poles` rješava završni LS na posljednjem prihvaćenom
valjanom skupu polova. Zato rezultat može sadržavati kandidat i uz neuspjeh petlje.
`final_fit` navodi njegov rang, uvjetovanost i stvarni težinski rezidual; `model` je
praktičan pristup tom modelu. Ako završni LS numerički ne uspije, oba su `None`, a
`final_fit_error` zadržava razlog bez brisanja prethodnog razloga zaustavljanja.
Kandidat nije izabran prema najboljoj pogrešci na kontrolnoj mreži. Numerički rang
završnog LS-a, stabilnost, realnost, pozitivnost reziduala i pogrešku treba provjeriti
odvojeno od `stop_reason`.

## 3. Samostalan ponovljiv primjer

Iz korijena repozitorija:

```bash
uv run python experiments/vf_checks.py
```

Tri umjetna slučaja imaju poznate odzive:

1. `2/(s+1)+3/(s+5)` s jediničnim težinama;
2. `(s+5)/(s²+2s+5)+3/(s+8)` s konjugiranim parom i realnim polom;
3. prvi odziv s čvorovima/težinama kvadrature na konačnom pojasu.

Frekvencijska skala primjera je 0,1–40 rad/s; to nije pojas tkiva u MHz/GHz. Početni
polovi i svi parametri zapisani su u podrijetlu. Postavke skripte služe provjeri poznatih
sintetičkih sustava, ne određuju Z2. Pogreška se računa u dodatnim točkama iz izravnih
analitičkih izraza. Prolaz traži ustaljenu petlju, puni rang završnog LS-a, realan stabilan
model i malu provjerenu pogrešku. Namjerni poziv s `--max-iterations 1` vraća izlazni kod 1
i sačuva sva tri slučaja s oznakom iscrpljenih iteracija, čak i ako je odziv već točan.

`results/runs/<run_id>/` sadrži provenance.json i vf_checks.json: postavke, kod i
necommitirane promjene, okruženje, povijesti i ishode svih slučajeva. Izlazi su izvan Gita.
Status zapisa `completed` znači da je zapisivanje završilo; algoritamski uspjeh određuju
`outcome.checks_passed` i razlozi zaustavljanja u pojedinim rezultatima.

## 4. Granice ovog koraka

Nema novih ovisnosti ni promjene zaključanog okruženja. Testovi provjeravaju poznate polove
i odzive u drugim točkama, promjenu jedinica, realnost i refleksiju te kontrolu petlje uz
namjerno zadane neuspjehe. Kontrolni test perioda nameće sintetički niz premještanja;
to nije reprodukcija primjera grede iz L1.

Nije preuzet Sarin B1, nisu reproducirane njegove brojke, nije proveden A7 na tkivima i
nisu prihvaćene postavke Z2. Za konačan prihvat A4 preostaju usporedba s B1 i Sarin pregled.
Za nove rezultate na tkivima trebaju odabrani eksperimentalni parametri i jasno podrijetlo.
