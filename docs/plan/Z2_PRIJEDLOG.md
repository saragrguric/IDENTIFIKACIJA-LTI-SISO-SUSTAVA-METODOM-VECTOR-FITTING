# Z2: konkretan prijedlog plana eksperimenata

**Stanje: prihvaćeno bez izmjena 2026-11-25 ([ADR-0008](adr/0008-accept-z2-experiment-plan.md)).**
Prema Lovrinoj izjavi Sara i Lovro su na sastanku Z2 uživo prihvatili sve preporuke iz ovog
prijedloga. Tekst ispod ostaje kakav je pripremljen 2026-11-23, pa njegove napomene o
„prijedlogu” i „potvrdi” opisuju stanje prije sastanka. Plan je zaključan 2026-11-25 nakon
razvojnih kriterija iz §7 (dodatak ADR-0008). Raspon početnih i fiksnih polova iz §3 i §7 promijenjen je nakon A7
([dodatak ADR-0008](adr/0008-accept-z2-experiment-plan.md#dodatak-2026-11-25-raspon-početnih-i-fiksnih-polova-nakon-a7)).

**Izvorno stanje: predloženo, 2026-11-23.** Ovo nije zapis održanog sastanka niti prihvaćena
specifikacija. Nositeljica Z2 je Sara, sudjeluju oboje. Lovro priprema početni prijedlog
prema [podjeli rada](PODJELA.md#z2-plan-eksperimenata-prije-završnih-pokretanja).
Završni dogovor slijedi nakon probnog B5; puna petlja A4 još čeka B1. Ovaj dokument ne
mijenja implementaciju niti pokreće završne eksperimente.

## 1. Pitanje i hipoteze

Za Gabrielov referentni model tražimo najmanji **pronađeni** broj polova koji zadovoljava
svaku od prihvaćenih tolerancija 5 %, 1 % i 0,1 %, odvojeno za najveću relativnu pogrešku
permitivnosti na kontrolnoj mreži i relativnu normu pogreške disperzivnog dijela na pojasu.
To nije dokaz najmanjega mogućeg reda niti točnosti prema novim mjerenjima tkiva.

Prije završnih rezultata predlažemo zapisati:

1. VF s pomicanjem polova postiže manji pronađeni red od usporedive metode s fiksnim
   polovima kod više od polovice završnih skupina parametara. Brojimo i izjednačenja i
   slučajeve bez prihvatljivog kandidata; hipotezu provjeravamo zasebno po toleranciji i mjeri.
2. Kvadraturno težinski VF na pojasu daje manju medijalnu razliku pronađenih redova prema
   VF-u s jediničnim težinama za pojasnu mjeru. Ne pretpostavljamo isti ishod za najveću
   relativnu pogrešku permitivnosti.
3. Veza najvećeg aktivnog parametra α i potrebnog reda istraživačka je analiza. Sama α ne
   određuje težinu aproksimacije: važni su i vremena, jakosti i njihov položaj prema pojasu.

Primarno pitanje odnosi se na **Debyejeve** modele. Nekonjugirani izlaz, nestabilan model,
kompleksni polovi ili negativni reziduali nisu uspješan fizikalni Debyejev model, čak ni uz
malu pogrešku. Opće realne racionalne kandidate prikazujemo zasebno. VF-u ne pripisujemo
nedokazano jamstvo realnih polova ili pozitivnih reziduala.

## 2. Ulaz, predmet prilagodbe i razdvajanje skupina

Koristimo kanonski CSV iz [opisa podataka](../../data/README.md), SHA-256
`0644be919b775d19425bd51d2bd732d2cbb6c05cbbaf7b1d76b4e792c3e4d21a`.
Parametri dolaze iz WebNIR-ova prijepisa D1; L1 ostaje jedini izvor matematike metode
([literatura](../research/LITERATURE.md)). Ne dodajemo šum niti nova mjerenja.

**Preporuka za H:** zadržati postojeću definiciju `gabriel.strictly_proper_part`, tj. sva
četiri aktivna disperzivna člana. Samo poznati ε∞ i σi/(s ε0) ostaju izvan prilagodbe.
Ne izdvajamo dodatno članove s α = 0. Time r broji sve pronađene disperzivne polove, a ne
samo aproksimaciju frakcijskih članova. To je jednostavnije za usporedbu tkiva i odgovara
sadašnjem kodu. Alternativa je točne Debyejeve članove izdvojiti i njihov broj pribrojiti
prijavljenom ukupnom redu; ona bi tražila novu definiciju cilja i zasebno označena izvođenja.
Tim treba potvrditi ovu preporuku prije B6.

| Uloga | Predloženi nazivi za odabir skupina | Broj različitih skupina | Broj naziva |
|---|---|---:|---:|
| Razvoj i detaljna analiza | Blood, Muscle, Fat, Bone cortical, Skin wet, zajedno sa svim njihovim duplikatima | 5 | 8 |
| Završno vrednovanje | Svi preostali disperzivni parametri | 36 | 47 |
| Izvan relativnog vrednovanja H | Air i Vacuum, jer H = 0 | 1 | 2 |

Duplikati razvojnih skupina su Bone cortical/Nail/Tooth i Skin wet/Mucous membrane.
Skupine se određuju po **svim** parametrima, ne samo po nazivu. Ukupno ostaje 41 različit
disperzivni model i 55 naziva. Jedan izračun može se dijeliti unutar identične skupine uz
sačuvanu vezu na svaki naziv; sažetke primarno brojimo po skupinama, a puni izvoz po nazivima.

Blood i Muscle već su korišteni pri ranijim provjerama. Parametri i omjeri pojasne i pune
norme za svih 41 skupinu također su ranije pregledani u B3. Zato ovaj skup **nije slijepo,
dosad neviđeno vrednovanje**. Razdvajamo buduće podešavanje algoritma od završnih usporedbi,
ali ne prikrivamo prethodni uvid. Predloženi razvojni izbor pokriva krv/mišić, masno,
koštano i kožno tkivo; ne temelji se na novim uspješnim VF rezultatima.

## 3. Pojas, polovi i redovi

| Postavka | Preporuka za potvrdu | Obrazloženje |
|---|---|---|
| Pojas | 10 MHz–10 GHz | Zadržava sadašnji privremeni pojas; nije dokaz univerzalne fizikalne valjanosti |
| Primarni broj pozitivnih čvorova | N = 240 | Dovoljno više od r ≤ 32; trošak i osjetljivost provjeriti u B5 |
| Redovi | Svaki cijeli r od 1 do 32 | Bez preskakanja redova i bez pretpostavke monotonosti pogreške |
| Primarni raspon početnih/fiksnih polova | 1 kHz–100 GHz | Obuhvaća pojas i repove sporijih/bržih disperzija; isti za sve metode i tkiva |
| Početni i fiksni polovi | λj = −2π fj, fj logaritamski raspoređeni po rasponu | `baseline.log_poles`; za r = 1 geometrijska sredina |
| Slučajnost | Nema slučajnog inicijaliziranja | Deterministički slučajevi; sjeme nije primjenjivo |
| Direktni član H | Nula | ε∞ je već točno izdvojen |

Raspon pomoćnih polova nije ograničenje kasnije premještenih polova. Vrlo spora relaksacija
može utjecati svojim repom i kad joj je karakteristična frekvencija ispod pojasa. Ne
postavljamo polove prema pojedinom tkivu nakon uvida u završnu pogrešku.

Ako do r = 32 nema prolaza, zapisujemo „nema prihvatljivog modela među ispitanim redovima
1–32”. Ne tvrdimo da takav model ne postoji. Proširenje do 64 odlučuje se nakon B5 i prije
zaključavanja završnog plana, uz novi izračun proračuna. Nakon zaključavanja takvo proširenje
postaje dopunski eksperiment s vlastitom oznakom, a ne prešutna zamjena.

## 4. Usporedba koja odvaja težine od premještanja polova

Predlažemo četiri postupka. Posljednja dva su na istim kvadraturnim čvorovima, tako da
razliku među njima ne uzrokuje drugačija funkcija cilja.

| Oznaka slučaja | Čvorovi u pojasu | w u zbroju w · abs(pogreška)² | Polovi |
|---|---|---|---|
| `fixed_log` | N logaritamskih čvorova, uključeni krajevi | 1 | Fiksni početni polovi |
| `vf_log` | Isti kao `fixed_log` | 1 | VF, isti početni polovi |
| `fixed_band` | `quadrature.band_nodes` (Gauss–Legendre u ln ω) | Iz te kvadrature | Fiksni početni polovi |
| `quadvf_band` | Isti kao `fixed_band` | Iste kvadraturne težine | VF, isti početni polovi |

`quadvf_band` označava **prilagodbu QuadVF-a konačnom pojasu**, a ne izvornu L1 formulu na
cijeloj osi. Za aktivne Cole–Coleove članove s α > 0 rubni limes iω H(iω) općenito nije
konačan. Stoga nema L-parametra ni rubnih redaka iz L1 (3.4) u ovoj primarnoj usporedbi.
Odluka o rasponu L iz izvornog plana postaje neprimjenjiva ako tim odabere ovu prilagodbu;
to pri potvrdi treba uskladiti u metodologiji i ADR-u. Izvod je u
[B2](../izvodi/b2-h2-kvadratura.md), §6.

Sve LS retke množimo s korijenom w. Težine se ne kvadriraju još jednom. U VF koraku
apsorpcija SK težine u novu bazu ne uklanja ove vanjske težine. U završnom LS-u za
reziduale ostaju iste težine kao tijekom prilagodbe. Ne uvodimo relativne težine 1/abs(H)²
ili 1/abs(ε)²; one bi promijenile istraživanu metodu. Razlika cilja i dviju završnih mjera
ostaje vidljiva, ne prilagođava se skrivenim ponderiranjem.

## 5. Predložena kontrola petlje A4

Ovo je **specifikacija za raspravu**, ne opis postojeće pune implementacije.
Pojedinačne operacije i njihova ograničenja razrađeni su u
[A5](../izvodi/a5-polovi-reziduali.md).

- Najviše 200 LS koraka; `numpy.linalg.lstsq`, `rcond=None`, bez normalnih jednadžbi,
  regularizacije i automatskog skaliranja redaka. Radimo u fizičkoj s-skali i bilježimo
  singularne vrijednosti/rang stvarno rješavane matrice.
- Realna parametrizacija za realne polove i konjugirane parove. Pozitivni čvorovi dovoljni
  su za realni model. Nema projekcije kompleksnog pola na realnu os ni apsolutne vrijednosti
  negativnog reziduala.
- Sirove nove polove dobivamo iz `diag(λ) − varphi eᵀ`. Ako je realni dio pozitivan,
  izričito reflektiramo u `−conj(λ)` i bilježimo oba skupa. Pol na imaginarnoj osi,
  duplikat, čvor jednak polu ili nekonačan rezultat zaustavlja slučaj s navedenim razlogom;
  nema pomaka za „mali epsilon”, brisanja ni novog slučajnog početka.
- Relativni pomak je δk = Ω(λk, λk−1) / max(2π · 10 MHz, max abs(λk−1)), gdje je Ω
  najmanji mogući najveći pomak uparenih polova. Skala je u rad/s; prag je 10⁻⁸.
  Dva uzastopna koraka ispod praga daju status `poles_settled`.
- Odvojeno bilježimo qk = max_i abs(d_tilde(ξi) − 1) i ocjenu η iz A5. Ako je uz dva mala
  pomaka i qk ≤ 10⁻⁸, status je `poles_and_denominator_settled`. To i dalje nije dokaz
  optimalnosti ni globalne konvergencije. Primjer 4.2 u L1 objašnjava zašto mali pomaci
  ne zahtijevaju mali qk.
- Pohranjujemo cijelu povijest do 200 koraka. Za periode 2, 3 i 4 isti prag za Ω mora
  potvrditi **dva uzastopna povratka**; ako polovi pritom nisu uzastopno ustaljeni,
  status je `cycle`. Konačni kriteriji koriste polove nakon intervencija, a sirovi pomaci
  ostaju dostupni radi provjere ocjena L1.
- Nedovoljan numerički rang prekida slučaj kao `rank_deficient`. Uvjetovanost iznad 10¹²
  označava `ill_conditioned`, bez prešutnog popravka; kandidata prikazujemo odvojeno od
  pouzdanijih slučajeva. Puni rang sam po sebi nije dokaz numeričke točnosti.
- Na kraju uvijek pokušavamo završni LS na posljednjem valjanom skupu polova i provjeravamo
  odziv. Ne biramo najbolju iteraciju prema završnoj kontrolnoj mreži. Ako je petlja završila
  kruženjem ili ograničenjem, kandidat ne dobiva status uspješne iteracije čak ni uz malu
  izmjerenu pogrešku.

Pri izvještavanju odvojeno postoje razlog zaustavljanja, stabilnost, realnost, uvjetovanost,
Debyejeva prihvatljivost i postignuta tolerancija. Primarna tablica najmanjeg r zahtijeva
ustaljenu petlju (ili fiksne polove), puni rang, uvjetovanost ≤ 10¹², konačan stabilan
odziv i za Debyejevu tablicu realne negativne polove s realnim strogo pozitivnim rezidualima.
Realni pol znači imaginarni dio jednak nuli u vraćenom modelu; nema naknadnog zaokruživanja.
Nulti rezidual i gotovo poništen pol zasebno se označavaju i ne brišu. Dodatna tablica
kandidata zadržava sve ostale razloge i pogreške. Tako se ne prešućuju ni neuspjesi ni
aproksimacijski dobri kandidati iz neuspjele petlje.

## 6. Neovisno vrednovanje i odabir reda

**Najveća relativna pogreška:** koristi puni ε u nazivniku, a H_r − H u brojniku.
Unaprijed zadana kontrolna mreža sadrži krajeve pojasa i dva skupa od po 4096 sredina
ćelija: jedan u ln f, drugi u f. Ne ovisi o pronađenim polovima. Račun ponavljamo s 8192
sredina po skupu; prijavljujemo gušći maksimum i apsolutnu razliku. Krajevi mogu biti i
čvorovi prilagodbe; kontrolna mreža kao cjelina nije skup čvorova prilagodbe. To nisu dva
nezavisna skupa mjerenja nego evaluacija istoga analitičkog modela.

**Pojasna pogreška:** koristi relativni omjer normi disperzivnog H, normaliziran s 1/π
u integralu preko pozitivnih kutnih frekvencija. Kontrolna kvadratura ima 512 i 1024
čvora `band_nodes`, ne 240 čvorova prilagodbe. Čvorove/težine izračunamo jednom po
postavci i ponovno koristimo. Prijavljujemo gušću procjenu i razliku, uz napomenu da su
oba pravila iste obitelji i njihovo slaganje nije dokaz točne integralne pogreške.

Za obje mjere tražimo razliku finije i grublje procjene ≤ 10⁻⁶ u **apsolutnoj relativnoj
pogrešci**. Konzervativan prolaz zahtijeva E_fino + abs(E_fino − E_grubo) ≤ tolerancija.
U suprotnom slučaj je iznad praga ili graničan/numerički nerazriješen, ovisno o procjenama.
Ne dorađujemo model na kontrolnim frekvencijama. Mrežni maksimum nije potvrđena kontinuirana
H∞ pogreška, a pojasna norma nije puna H2 norma. Ne navodimo više značajnih znamenaka nego
što podržava provjera gustoće.

Odabir r radi se zasebno za svaku mjeru i prag. Sva 32 reda ostaju u izvođenju čak i nakon
prvoga prolaza, jer uspjeh i pogreška VF-a nisu zajamčeno monotoni. Odvojene tablice daju:

- najmanji pronađeni prihvatljiv Debyejev red;
- najmanji pronađeni prihvatljiv opći realan stabilan racionalni red;
- sve neuspjehe, granične slučajeve i razlog izostanka prihvatljivog reda.

Ako samo jedna metoda ima prolaz, to izvještavamo kao jednostrani prolaz, a ne kao konačnu
brojčanu razliku prema nepostojećem r. Medijane razlika daju broj uparenih prolaza uz zaseban
broj jednostranih prolaza, obostranih neuspjeha i izjednačenja. Zaključak ne smije počivati
samo na povoljnom podskupu preživjelih pokretanja.

## 7. Razvojni proračun, osjetljivost i zaključavanje

Prvi B5 mjeri vrijeme po slučaju i provjerava zapis neuspjeha na pet razvojnih skupina.
Predlažemo ove unaprijed određene pokuse, bez pune kartezijske eksplozije:

| Pokus | Skupine | Redovi | N | Raspon polova u Hz | Broj slučajeva |
|---|---:|---|---|---|---:|
| Razvojni osnovni | 5 | 1–32 | 240 | 10³–10¹¹ | 640 |
| Osjetljivost na čvorove | 5 | 4, 8, 16, 32 | 120 i 480 | 10³–10¹¹ | 160 |
| Osjetljivost na početak | 5 | 4, 8, 16, 32 | 240 | 1–10¹² i 10⁷–10¹⁰ | 160 |
| Završni osnovni | 36 | 1–32 | 240 | 10³–10¹¹ | 4608 |

Svaki broj uključuje sva četiri postupka. To je 960 razvojnih i 4608 završnih slučajeva,
ukupno 5568. Polovica slučajeva ima VF petlju: gornja granica je 556800 baricentričnih LS
koraka uz najviše 200 po slučaju, bez završnih LS i troška kontrolnih mreža. Ovo je
proračun plana, **nije rezultat niti procjena vremena izvođenja**. B5 najprije mjeri trošak
malog poznatog popisa; ako proračun ne stane u raspoloživo vrijeme, promjenu opsega tim
zapisuje prije završnog vrednovanja. Prekid zbog proračuna ne pretvara se u algoritamski
neuspjeh niti u preskočen slučaj bez oznake.

Razvojni kriteriji prije zaključavanja: svojstva analitičkih testova prolaze, nema skrivenih
intervencija, gustoća kontrolnog vrednovanja daje navedenu razlučivost, podrijetlo omogućuje
ponavljanje i trošak svih planiranih slučajeva je izmjeren/procijenjen iz B5. Osjetljivost
na N ili početak koja bitno mijenja zaključak ostaje rezultat za prikaz. Parametre smijemo
doraditi samo na razvojnom skupu i svaku promjenu zabilježiti; završne pogreške ne služe
ponovnom podešavanju.

**Jedinica pokretanja:** predlažemo jedan roditeljski zapis prolaza i zaseban trajni zapis
svakog slučaja `(skupina, postupak, r, N, početni raspon)`. To koristi postojeće mogućnosti
`vfdebye.provenance`, omogućuje nastavak nakon prekida i čuva neuspjele slučajeve. Uzorci
i postavke moraju imati isti identitet pri nastavku; ponovljeni slučaj dobiva novu oznaku
i vezu na prethodnika, bez prepisivanja citiranih rezultata. Ovo treba potvrditi prije
prvog pokretača B5–B7.

## 8. Što treba potvrditi, a što se može pripremati odmah

Prije zaključavanja Sara i Lovro trebaju odlučiti o H i brojanju točnih α = 0 članova,
konačnom pojasu, podjeli skupina, četirima usporedbama, redovima i proračunu, pravilima
zaustavljanja te jedinici pokretanja. Predložene vrijednosti stoje gore pa odluka ne
zahtijeva novi nacrt od nule. Prihvat se bilježi novim ADR-om i dopunom
[metodologije](METHODOLOGY.md), podjele rada i [zadataka](TASKS.md); ovaj prijedlog
ostaje povijesno prepoznatljiv.

Odmah se mogu pripremati teorijska poglavlja A8 i pitanja za zajednički prolaz, pregled
pojedinačnih operacija A5 i format tablica s praznim mjestima za identifikatore pokretanja.
Puna petlja A4 čeka B1; A7 i završna usporedba čekaju A4, A6 i odluke Z2. Ovaj prijedlog
ne bilježi Sarin pregled, ljudsko razumijevanje, izvedene VF pokuse ni prihvaćen rezultat.
