# Podaci

Ulaz projekta je tablica parametara Gabrielova modela permitivnosti tkiva
([ADR-0004](../docs/plan/adr/0004-choose-debye-models-of-human-tissues.md)). Tablica ostaje
izvan Gita; ova datoteka i skripta za preuzimanje omogućuju da je svatko dobije u istom obliku.

## Izvor i licenca

- **Izvorno izvješće:** C. Gabriel i S. Gabriel, *Compilation of the dielectric properties of body
  tissues at RF and microwave frequencies*, Armstrong Laboratory, AL/OE-TR-1996-0037, 1996
  (DTIC AD-A305826), označeno „Approved for public release, distribution unlimited”. U
  [literaturi](../docs/research/LITERATURE.md) je to izvor D1.
- **Prijepis koji preuzimamo:** WebNIR (CNR-IFAC),
  <https://webnir.eu/04-Dosimetry/04-Gabriel.php?lang=gb>, tablica parametara na kartici
  „parametri”. Stranica je objavljena pod CC BY-NC-SA 4.0, pa njezin sadržaj ne spremamo u Git.
- **Datum pristupa:** 2026-11-09.

## Preuzimanje i priprema

Iz korijena repozitorija, uz okruženje iz `uv.lock`:

```bash
uv run python data/fetch_gabriel.py
```

Skripta:

1. sprema stranicu u data/raw/webnir-gabriel.html.new;
2. pronalazi tablicu po točnom zaglavlju (nazivi i jedinice stupaca), a promijenjeno zaglavlje
   prijavljuje kao pogrešku;
3. provjerava svaki redak funkcijom `vfdebye.gabriel.tissue_from_row`;
4. zapisuje data/processed/gabriel_parameters.csv.new s vrijednostima doslovno kako su
   objavljene (iste jedinice kao u tablici, LF završeci redaka, UTF-8);
5. uspoređuje SHA-256 CSV-a sa zabilježenim. Tek kad se podudaraju, nove datoteke
   zamjenjuju data/raw/webnir-gabriel.html i data/processed/gabriel_parameters.csv. Inače
   skripta vraća pogrešku, ranije provjerene datoteke ostaju nepromijenjene, a nove ostaju
   s nastavkom .new radi usporedbe.

S `--offline` skripta ponovno gradi CSV iz spremljenog HTML-a bez preuzimanja. Ništa se ne
interpolira, ne preuzorkuje ni ne izbacuje.

| Datoteka | SHA-256 (2026-11-09) |
|---|---|
| CSV | `0644be919b775d19425bd51d2bd732d2cbb6c05cbbaf7b1d76b4e792c3e4d21a` |
| HTML | `412e4e1155203dce3885ab0ffbc4560497cc067f032a5c01fba7aeb72f95c2a1` (samo informativno: izgled stranice se može promijeniti bez promjene tablice) |

Mjerodavan je kontrolni zbroj CSV-a. Ako se promijeni, prije uporabe usporedite retke s
prethodnom inačicom i novi zbroj zabilježite ovdje i u `data/fetch_gabriel.py` kroz pregledani PR.
Neovisno raščlanjivanje istog HTML-a regularnim izrazima 2026-11-09 dalo je jednake retke.

## Sadržaj tablice

- **57 redaka**, stupci: naziv tkiva, $\varepsilon_\infty$, $\sigma_i$ u S/m te za
  $n=1,\dots,4$: $\Delta\varepsilon_n$, $\tau_n$ i $\alpha_n$. Jedinice od $\tau_1$ do $\tau_4$
  redom su ps, ns, µs i ms; `vfdebye.gabriel` ih pretvara u sekunde.
- **Zrak i vakuum** nemaju disperziju: svi $\Delta\varepsilon_n=0$, a $\alpha_n=1$. Član s
  $\Delta\varepsilon_n=0$ ne pridonosi modelu, pa za njega $\tau_n$ i $\alpha_n$ nisu
  ograničeni. Svaki prisutni član traži $\tau_n>0$ i $0\le\alpha_n<1$. Zrak i vakuum nisu dio
  eksperimenta (ADR-0004).
- **Retci s jednakim parametrima** ostaju u tablici i označeni su
  (`vfdebye.gabriel.duplicate_groups`): Air i Vacuum; Aorta i Blood vessel; Body fluid i
  Vitreous humor; Bone cortical, Nail i Tooth; Duodenum, Oesophagus i Stomach; Eye sclera i
  Retina; Gland, Lymph, Pancreas, Thymus i Thyroid; Mucous membrane i Skin wet; Nerve i Spinal
  cord; Prostate i Testis. Od 55 disperzivnih redaka 41 ima različite parametre.

## Nesigurnost modela

Prema prijepisu izvješća na istoj stranici (izvorno izvješće nismo zasebno pročitali):

- ponovljivost mjerenja na standardnim uzorcima je oko 1 %;
- prirodno rasipanje svojstava tkiva je oko ±5 % iznad 100 MHz i do ±15 % na niskim
  frekvencijama;
- model se može pouzdano koristiti iznad 1 MHz, a mjerenja sežu do 20 GHz.

Razine točnosti od 1 % i 0,1 % (dodatak ADR-0004 od 2026-11-09) zato su ispod nesigurnosti
samog modela. One odgovaraju na matematičko pitanje o aproksimaciji funkcije $H$, a ne na
fizikalno pitanje o tkivu. Privremeni pojas 10 MHz–10 GHz nalazi se unutar područja mjerenja.

## Kontrolne vrijednosti

Na 900 MHz model daje: krv $\varepsilon'=61{,}36$ i $\sigma=1{,}538$ S/m; mišić
$\varepsilon'=55{,}03$ i $\sigma=0{,}943$ S/m. To su Sarine vrijednosti iz probnog pokusa,
ponovno izračunate 2026-11-07 (ADR-0004), a `tests/test_gabriel.py` ih provjerava.
