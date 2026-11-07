# Plan osobe B: Sara, nit „od polova do odgovora”

Zajednička pravila, sučelja i faze opisani su u [podjeli rada](../PODJELA.md). Ovaj plan je
prijedlog koji je napisao Lovro uz pomoć AI alata; promijeni ga u PR-u ili zadatku ako nešto ne
odgovara.

## Ukratko

Tvoja nit mjeri koliko je model dobar i odgovara na pitanje iz
[ADR-0004](../adr/0004-choose-debye-models-of-human-tissues.md): koliko je polova najmanje
potrebno i štede li VF i QuadVF polove. Nastavlja tvoj probni pokus na krvi i mišiću.

- **Matematika:** prostor $\mathcal{H}_2$ i uvjeti optimalnosti (L1, §3.1), Primjer 3.1,
  kvadratura i QuadVF (§3.3), prilagodba ograničenom pojasu, uvjetovanost i RegVF (§4.3),
  referentna metoda s fiksnim polovima.
- **Kod:** `vfdebye.quadrature`, `vfdebye.baseline` i `vfdebye.metrics`, svaki s testovima, te
  pokretači eksperimenata.
- **Eksperimenti:** reprodukcija probnog pokusa, glavni eksperiment, osjetljivost na $L$ i broj
  čvorova, uvjetovanost.
- **Seminar i prezentacija:** $\mathcal{H}_2$ norma i kvadratura, QuadVF, plan eksperimenata,
  rezultati i rasprava.
- **Pregled:** pregledavaš Lovrinu nit A (PR-ovi, neovisna provjera izvoda u A9 i reprodukcija u
  Z4) i na prolazima objašnjavaš nit A. Tvoju nit pregledava Lovro.

## Redoslijed

| Faza | Zadatak | Ovisi o | Tko čeka tebe |
|---|---|---|---|
| 0 | Z0 dogovor | — | oboje |
| 1 | B1 probni kod u repozitorij | A1 | A4, B3, B5 |
| 1 | B2 matematika: $\mathcal{H}_2$, kvadratura, QuadVF | Z0 | A9, B8 |
| 1 | B3 kvadratura na pojasu | A1, B2 | B5 |
| 1 | B4 mjere pogreške i referentna metoda | A1, A2 | Z1, B6 |
| 2 | B5 QuadVF i reprodukcija probnog pokusa | A4, A6, B3 | Z2 |
| 2 | B9 neovisna provjera izvoda niti A | A3, A5 | Z3 |
| 2 | Z2 plan eksperimenata (nositeljica) | B5 | B6, B7, A7 |
| 3 | B6 glavni eksperiment | Z2 | B8 |
| 3 | B7 osjetljivost i uvjetovanost | Z2 | B8 |
| 3 | B8 seminar: poglavlja niti B | B2–B7 | Z5 |
| 4 | B10 slajdovi niti B | B8 | Z6 |

B2 možeš početi odmah nakon Z0.

## B1: probni kod u repozitorij

**Cilj:** tvoj kod iz probnog pokusa postaje polazište, a njegovi brojevi postaju provjerljivi.

1. Nakon A1 dodaj kod na granu `sara/b1-probni-kod`, s kratkim opisom što radi i kojim je
   postavkama dao tablicu iz tvog dokumenta.
2. Dogovori s Lovrom što prelazi u `vfdebye.vf` (A4), a što u tvoje module (B3, B4).
3. Ako imaš skriptu s matematikom ili testni sustav, dodaj ih ili navedi gdje su.

**Gotovo kada:** kod je u repozitoriju, a podjela na module dogovorena.

## B2: matematika $\mathcal{H}_2$ dijela

**Cilj:** čitljiv izvod prema [metodologiji](../METHODOLOGY.md), odjeljak 4.

1. Prostor $\mathcal{H}_2$, skalarni produkt i norma (3.1); uvjeti optimalnosti (3.2) do dubine
   potrebne za tumačenje rezultata.
2. Primjer 3.1: zašto mali rezidual ne znači malu pogrešku.
3. Trapezna formula (3.3), Boyd/Clenshaw–Curtis (3.4)–(3.5) i QuadVF (3.6)–(3.7).
4. **Naš odmak od L1:** kvadratura na ograničenom pojasu i izostavljanje retka $M_+[H]$, jer za
   $\alpha_n>0$ izraz $sH(s)$ nema konačnu granicu. Izvedi i obrazloži.
5. Zašto je $\mathcal{H}_2$ norma $H$ konačna za $\alpha_n\le0{,}3$ i zašto je na cijeloj osi
   ipak određuju niskofrekvencijske disperzije.

**Gotovo kada:** Lovro je u A9 neovisno prošao izvod, a nejasnoće su zapisane.

## B3: kvadratura na pojasu

Modul `vfdebye.quadrature`: čvorovi i težine na pojasu i $\mathcal{H}_2$ norma na pojasu.
Testovi:

- integral za $H(s)=1/(s+a)$ na cijeloj osi jednak je $\pi/a$ (metodologija, odjeljak 7);
- na pojasu $[\omega_1,\omega_2]$ jednak je $\bigl(\arctan(\omega_2/a)-\arctan(\omega_1/a)\bigr)/a$
  za pozitivne frekvencije (provjeriti izvod prije testa);
- konvergencija s brojem čvorova.

## B4: mjere pogreške i referentna metoda

1. `vfdebye.metrics`: najveća relativna pogreška od $\varepsilon$ na gustoj mreži, relativna
   $\mathcal{H}_2$ pogreška na pojasu i pretraga najmanjeg $r$ za zadanu točnost.
2. `vfdebye.baseline`: fiksni logaritamski polovi i reziduali najmanjim kvadratima.
3. Testovi na umjetnom modelu s poznatim polovima: referentna metoda s točnim polovima daje
   pogrešku na razini zaokruživanja.

## B5: QuadVF i reprodukcija probnog pokusa

experiments/pilot.py ponavlja probni pokus (krv i mišić, VF s logaritamskim i linearnim
čvorovima, relativne težine, QuadVF, fiksni polovi) iz repozitorija, uz zapis podrijetla.
Razlike u odnosu na brojeve iz tvog dokumenta zapiši i objasni.

## Z2: plan eksperimenata

Nositeljica si ti. Prije završnih pokretanja zapisuju se hipoteze, pojas, razine točnosti,
razvojni podskup tkiva i podskup za detaljnu analizu. $L$ i broj čvorova biraju se samo na
razvojnom podskupu.

## B6: glavni eksperiment

experiments/min_order.py: najmanji $r$ za svako tkivo, metodu i razinu točnosti, u objema
mjerama pogreške. Sva tkiva ulaze u zbirnu tablicu, uključujući neuspjehe.

## B7: osjetljivost i uvjetovanost

experiments/sensitivity.py: ovisnost o $L$ i broju čvorova, brojevi uvjetovanosti matrica
najmanjih kvadrata (frekvencije su reda $10^7$–$10^{10}$ rad/s), utjecaj skaliranja i redanja
redaka (L1, §4.3).

## B8 i B10: seminar i slajdovi niti B

Poglavlja: $\mathcal{H}_2$ norma i kvadratura, QuadVF, plan eksperimenata, rezultati i rasprava.
Svaki broj i slika imaju identifikator pokretanja. Slajdovi prate ista poglavlja.

## B9: neovisna provjera izvoda niti A

Na papiru prođi Lovrin izvod linearizacije, SK iteracije, baricentričnog prikaza i premještanja
polova. Nejasnoće i ishod zapiši u zadatak.
