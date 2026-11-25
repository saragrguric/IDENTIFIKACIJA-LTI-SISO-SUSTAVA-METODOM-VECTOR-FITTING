# Z1: vodič za prolaz 1, prvi VF model krvi

**Stanje 2026-11-25: pripremljeno, prolaz nije održan.** Ovaj vodič priprema zajednički prolaz
iz [podjele rada](PODJELA.md#z1-prolaz-1-prvi-vf-model-jednog-tkiva). Nit A objašnjava Sara,
a nit B Lovro; nositelj niti dopunjuje. Zapis na kraju popunjava se tek nakon prolaza.
Krv je razvojna skupina iz [ADR-0008](adr/0008-accept-z2-experiment-plan.md), pa brojevi
ovdje nisu rezultat seminara.

## Priprema, svatko na svom računalu

```bash
uv sync
uv run python data/fetch_gabriel.py
uv run python experiments/z1_blood.py
```

Drugi korak treba samo ako lokalna tablica ne postoji. Pokretanje
`20261125T091152576258Z-z1_blood` (revizija `75c22da`, čisto stablo) daje brojeve navedene
ispod. Rezultat na drugom računalu treba se slagati do zaokruživanja; razliku zapišite.
Izlaz je u direktoriju pokretanja opisanom u [tijeku rada](PIPELINE.md).

## Tijek, oko 75 minuta

### 1. Od tablice do H(s): Sara, izlaz 1–2

Literatura: [A3](../izvodi/a3-problem-sk.md), §1.1–1.3, i [B2](../izvodi/b2-h2-kvadratura.md),
§2.3–2.4. Kod je `gabriel.strictly_proper_part`.

- Jedinice τ u tablici i konvencija ε = ε′ − iε″.
- Zašto ε∞ i σi/(s ε0) ostaju točni i ne ulaze u prilagodbu.
- Krv ima samo dva aktivna člana. Prvi relaksira na 19 GHz, iznad pojasa, a drugi na
  1,2 MHz, ispod pojasa. U pojasu se vide uglavnom njihovi repovi.
- Uz α = 0,1 članovi nisu racionalni, pa točan konačan red ne postoji.

### 2. VF korak po korak: Sara, izlaz 3

Literatura: A3, §2–6 (linearizacija, SK, baricentrični prikaz), i
[A5](../izvodi/a5-polovi-reziduali.md), §1–4 (premještanje polova i realnost). Kontrole petlje
opisane su u [A4](../izvodi/a4-implementacija.md), §1–2, i u ADR-0008, §5 s dodatkom.

- Početni polovi su logaritamski na pojasu 10 MHz–10 GHz, kao u dodatku ADR-0008.
- Rang je 14 = 2r jer LS korak ima r reziduala brojnika i r reziduala nazivnika.
  Uvjetovanost je oko 5·10⁷.
- δk pada oko 2,3 puta po koraku. Ustaljenje je nakon 23 koraka, kad je δ dvaput zaredom
  ispod 10⁻⁸.
- Tada je q ≈ 3,5·10⁻⁸, iznad 10⁻⁸, pa je status `poles_settled`, a ne
  `poles_and_denominator_settled`. To se slaže s [A7](../izvodi/a7-konvergencija.md),
  opažanje 5.

### 3. Model kao Debyejevi članovi: Sara, izlaz 4

Iz λ = −1/τ i φ = Δε/τ slijedi τ = −1/λ i Δε = φτ. Model je Debyejev (`is_debye`):

- Sedam realnih polova od 1,5 MHz do 23 GHz aproksimira dva Cole–Coleova člana.
- Najsporiji pol, na 1,5 MHz s Δε ≈ 4150, nosi rep drugog člana (Δε = 5200 na 1,2 MHz).
- Pitanje za raspravu: može li se pojedini pol fizikalno tumačiti ili tek zbroj članova?

### 4. Pogreške: Lovro, izlaz 5

Literatura: B2, §1 i §6.1–6.2, §6.6; kod `metrics`, `quadrature` i `baseline`.

- Najveća relativna pogreška dijeli s abs(ε), a ne s abs(H). Pojasna norma koristi faktor 1/π.
  Iste razine točnosti zato u dvjema mjerama ne znače isto.
- Kontrolna mreža nije skup čvorova prilagodbe.
- Uz r = 7 `vf_log` daje 7,1·10⁻³, a `quadvf_band` 1,6·10⁻³ najveće relativne pogreške.
- U tablici redova `vf_log` prolazi 1 % kod r = 7 i 0,1 % kod r = 10. `quadvf_band` prolazi
  1 % kod r = 6 i 0,1 % kod r = 8.
- Za r ≥ 4 nijedan postupak s fiksnim polovima nije Debyejev, jer ima nepozitivan
  rezidual. Za r ≥ 7 fiksni polovi sa širim rasponom daju manju pogrešku nego u pojasu.

### 5. Zajedno: A7 i odluka o rasponu

Prolazite [A7](../izvodi/a7-konvergencija.md) i dodatak ADR-0008. Oboje treba moći objasniti
zašto raspon 1 kHz–100 GHz u prvom koraku ruši rang i zašto su fiksni polovi dodani sa širim
rasponom. Odluku je donio AI alat po ovlaštenju tima; ako je netko ne prihvaća, zapišite to.

## Pitanja za provjeru razumijevanja

Nit A; odgovara Sara, a Lovro dopunjuje:

1. Zašto ε∞ i σi/(s ε0) ne ulaze u H i što bi se dogodilo da ulaze?
2. Što minimizira jedan baricentrični LS korak, a što ne?
3. Zašto nova baza apsorbira SK težinu i zašto su novi polovi svojstvene vrijednosti
   diag(λ) − φeᵀ?
4. Zašto je puni rang 2r i što znači gubitak ranga u prvom koraku?
5. Zašto `poles_settled` ne jamči malu pogrešku ni optimalnost?

Nit B; odgovara Lovro, a Sara dopunjuje:

1. Zašto je nazivnik najveće relativne pogreške abs(ε) i kako to utječe na prag 0,1 %?
2. Po čemu se pojasna norma razlikuje od pune H2 norme i zašto puna norma ne odgovara tkivima?
3. Zašto kontrolna mreža ne smije biti skup čvorova prilagodbe?
4. Zašto `quadvf_band` uz isti red ovdje daje manju pogrešku od `vf_log`? Odgovor je tumačenje,
   a ne teorem.
5. Što negativni reziduali fiksnih polova znače za Debyejevu tablicu?

## Zapis nakon prolaza

Popuniti nakon sastanka, ne unaprijed.

- Datum i trajanje:
- Sudionici:
- Tko je što objasnio:
- Pitanja na koja nismo znali odgovor:
- Nejasnoće i naknadni zadaci:
- Razlike u brojevima na drugom računalu:
