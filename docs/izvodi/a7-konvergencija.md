# A7: ponašanje VF iteracija na razvojnim skupinama

**Stanje 2026-11-25:** razvojno pokretanje `20261125T084356823080Z-convergence`, revizija
`9877aae` bez necommitiranih promjena, na grani `lovro/a7-konvergencija`. Postavke su iz
prihvaćenog plana Z2 ([ADR-0008](../plan/adr/0008-accept-z2-experiment-plan.md)). Ovo nije
završni eksperiment B6 ni Sarin pregled. Pogreške su okvirne, a najmanji redovi ispod nisu
rezultat seminara. Brojevi se odnose samo na pet razvojnih skupina.

## 1. Što se pokreće

`experiments/convergence.py` za Blood, Muscle, Fat, Bone cortical i Skin wet pokreće oba VF
postupka iz §4 plana Z2: `vf_log` i `quadvf_band`, s N = 240 čvorova na 10 MHz–10 GHz.
Početne polove daje `baseline.log_poles`. Primarni raspon 1 kHz–100 GHz ide za svaki r od 1 do
32, a rasponi osjetljivosti 1 Hz–1 THz i 10 MHz–10 GHz za r = 4, 8, 16 i 32, kako predviđa §7.
To je 400 slučajeva.

Svaki se slučaj pokreće dvaput:

- **prihvaćeni poziv:** `vector_fit` s kontrolama iz §5. To je poziv koji bi pokrenuo B6;
- **putanja:** isti početak s isključenim zaustavljanjem, do 200 koraka ili do neuspjeha.

Iz putanje se za svaki korak računaju δk iz §5 i Ω prije refleksije uz ocjenu L1 (4.4)
u obliku √r(2r − 1)‖φ‖₂ ([A5](a5-polovi-reziduali.md), §7.1). Računaju se i
qk = max abs(d̃ − 1), granica η = r max abs(φ)/μ iz §7.3, omjer Ω/μ iz (4.5) i relativna mjera
sa slike 2 u L1. Ishod se naknadno računa i za pragove 10⁻⁶, 10⁻⁸, 10⁻¹⁰ i 10⁻¹².

Pogreške se računaju na mreži u duhu §6 plana: krajevi pojasa i po 4096 sredina ćelija u ln f
i u f. Pojasna norma koristi 1024 čvora, a provjera finijom mrežom se ne radi. Zato su to
okvirne vrijednosti, a ne konzervativan prolaz iz B6.

Za ponavljanje: `uv run python experiments/convergence.py`. Izlaz (provenance.json,
convergence.txt, convergence.json i convergence_iterations.npz) nastaje u lokalnom
direktoriju pokretanja izvan Gita, kako je opisano u [tijeku rada](../plan/PIPELINE.md).

## 2. Opažanja

Sva opažanja su numerička, na ovih pet skupina, a ne opći teoremi.

1. **Gubitak ranga u prvom koraku za veće redove.** S primarnim rasponom prihvaćeni poziv
   staje kao `rank_deficient` već u prvom LS koraku:
   - `vf_log`: za svaki r ≥ 9 na svih pet skupina, a za krv i mišić već od r = 8;
   - `quadvf_band`: od r = 9 na četiri skupine, a za svaki r ≥ 10 na svih pet.

   Zadnji ustaljeni red je 7–9. Raspon 1 Hz–1 THz pada već kod r = 8. S rasponom 10 MHz–10 GHz
   petlja se ustali za r = 4, 8 i 16 (uz jedno kruženje kod r = 16, opažanje 6), a pada tek
   za r = 32. Objašnjenje, koje nije zasebno provjereno: pomoćni polovi daleko ispod pojasa
   daju na pojasu gotovo jednake stupce 1/(s − λ) ≈ 1/s, a polovi daleko iznad pojasa gotovo
   konstantne stupce. Uz `rcond=None` takva se matrica proglašava rang-deficijentnom.
   Za ustaljene slučajeve to je posljedica izbora početnog raspona, a ne nemogućnosti
   aproksimacije: s polovima unutar pojasa r = 16 postiže okvirnu najveću relativnu pogrešku
   1,4·10⁻⁷–1,6·10⁻⁶.
2. **Posljedica za pragove točnosti.** S primarnim rasponom `vf_log` ni na jednoj skupini ne
   doseže najveću relativnu pogrešku 0,1 %; najbolja je 1,6·10⁻³ (Fat). `quadvf_band` je
   doseže kod r = 7–8. Prag 1 % oba postupka dosežu kod r = 5–8.
3. **Ustaljeni kandidati su Debyejevi modeli.** Svih 118 prihvaćenih poziva sa statusom
   ustaljenja daje realne negativne polove i realne strogo pozitivne reziduale
   (`is_debye`). Svi su punog ranga i uvjetovanosti najviše 10¹². Kompleksnih ni nestabilnih
   polova nema. To je opažanje, a ne svojstvo koje L1 jamči.
4. **Broj iteracija.** Ustaljenje nastupa nakon 7–84 koraka, uz medijan 23. Nijedan
   slučaj ne iscrpi 200 koraka. Naknadno računanje pravila zaustavljanja iz putanje daje
   isti broj koraka kao prihvaćeni poziv u svih 399 slučajeva bez kruženja.
5. **Nazivnik zaostaje za polovima.** Za r ≥ 4 je pri zaustavljanju qk između 7·10⁻⁹ i
   1,2·10⁻⁷, pa 87 od 88 takvih slučajeva ima status `poles_settled`, a ne
   `poles_and_denominator_settled`. Drugi status dobiva 26 slučajeva: 25 s r ≤ 3 i jedan s
   r = 4. Na kraju putanje od 200 koraka q je između 4·10⁻¹⁵ i 1,3·10⁻⁷. Prag δ = 10⁻¹⁰
   dostiže se medijalno 6 koraka nakon zaustavljanja (4–30; u 4 slučaja nikad). Prag 10⁻¹²
   dostiže se medijalno još 6 koraka kasnije (4–107); u 15 slučajeva s r = 8 ili 16 nikad.
   To se slaže s napomenom L1 (§4.2, Primjer 4.2) da ustaljenje polova ne znači φ = 0.
6. **Razina šuma δ raste s redom.** Medijan zadnjih 20 vrijednosti δ u putanji je
   najviše 5·10⁻¹³ za r ≤ 6 i do 9·10⁻¹² za r = 8. Za r = 16 iznosi 5·10⁻¹¹–6·10⁻⁹, što je blizu
   praga 10⁻⁸. Zato se kod r = 16 s polovima u pojasu u četiri slučaja δ nakon ustaljenja
   ponovno popne iznad 10⁻⁸. Za Muscle i `vf_log` prihvaćeni poziv prijavljuje `cycle` s
   periodom 2 nakon 25 koraka, iako je kandidat dobar (okvirno 9,4·10⁻⁷). To je kruženje na
   razini zaokruživanja, a ne kruženje iz Primjera 4.2.
7. **Ocjene vrijede do zaokruživanja.** U svim koracima vrijedi Ω prije refleksije ≤ ocjena
   (4.4) + 0,42 · eps · max abs(λ). Vrijedi i q ≤ η · (1 + 4·10⁻¹⁶). Za r = 1 obje vrijede s
   jednakošću, pa se vidi samo zaokruživanje.

## 3. Prijedlog i odluka o rasponu

**Odluka 2026-11-25:** tim je odluku prepustio AI alatu kojim se Lovro služi (prema Lovrinoj
izjavi), a ona je zapisana u
[dodatku ADR-0008](../plan/adr/0008-accept-z2-experiment-plan.md#dodatak-2026-11-25-raspon-početnih-i-fiksnih-polova-nakon-a7).
Primarni raspon za sva četiri postupka je 10 MHz–10 GHz. Fiksni polovi se dodatno računaju
s rasponom 1 kHz–100 GHz kao jača referentna metoda. Prijedlog niže ostaje kakav je bio prije
odluke.

Opažanja 1 i 2 pogađaju prihvaćeni plan. Primarna tablica B6 za `vf_log` bi prijavila „nema
prihvatljivog modela” na 0,1 % zbog prvog LS koraka, a ne zbog kvalitete aproksimacije. Prema
§7 plana postavke se prije zaključavanja smiju doraditi samo na razvojnom skupu i uz dodatak
ADR-0008. Mogućnosti za raspravu:

1. **Zadržati plan.** Neuspjeh je tada rezultat s jasnim uzrokom, ali usporedba VF-a i
   QuadVF-a postaje usporedba početnih raspona.
2. **Primarni raspon 10 MHz–10 GHz, a 1 kHz–100 GHz kao osjetljivost.** Na razvojnim skupinama
   ustali se do r = 16. Raspon vrijedi i za fiksne polove, pa treba u B5 provjeriti koliko time
   gube `fixed_log` i `fixed_band`: fiksnim polovima polovi izvan pojasa mogu pomoći opisati
   repove sporih disperzija.
3. **Ne prekidati na gubitku ranga u prvom koraku.** To bi bila promjena pravila §5 i rješenje
   s najmanjom normom kod neodređenih polova; ne preporučujem bez novog izvoda.

Prijedlog je mogućnost 2, uz provjeru fiksnih polova u B5 prije dodatka ADR-0008.
Neovisno o tome, r = 32 pada i s polovima u pojasu. Za r ≥ 16 prag 10⁻⁸ približava se šumu
δ, pa treba odlučiti tretira li se kruženje na razini šuma kao neuspjeh.

## 4. Provjera fiksnih polova prije odluke

Pokretanje `20261125T090048328276Z-convergence` (revizija `9e86ebd`, čisto stablo) dodaje
uparene fiksne polove iz istih početnih polova (`baseline.fit_residues`) i pokreće sva tri
raspona za svaki r od 1 do 32. Prihvatljiv kandidat ima puni rang, uvjetovanost najviše 10¹²,
stabilan i Debyejev model, a za VF i status ustaljenja.

- **VF:** u pojasu prihvatljivih Debyejevih kandidata ima 89 (`vf_log`) i 99 (`quadvf_band`)
  od 160, a s 1 kHz–100 GHz 38 i 41. Najveću relativnu pogrešku 0,1 % `vf_log` u pojasu
  postiže kod r = 9–10, a `quadvf_band` kod r = 7–8. Pojasnu pogrešku 0,1 % postižu kod
  r = 8–9 odnosno r = 7.
- **Fiksni polovi, Debyejeva tablica:** ni u jednom rasponu nema kandidata ispod 5 %.
  U pojasu 149 od 160 fitova `fixed_log` ima nepozitivan rezidual. S 1 kHz–100 GHz 95 ih
  gubi rang, a 45 ima nepozitivan rezidual.
- **Fiksni polovi, opći realni modeli:** s 1 kHz–100 GHz najveća relativna pogreška 5 %
  postiže se kod r = 8–10. U pojasu to se događa tek kod r = 15–25, a 1 % većinom ni do r = 32.

Zato jedan zajednički raspon ne može biti najbolji za obje vrste postupaka. Odluka zadržava
usporedbu iz istog početka u pojasu i dodaje fiksne polove sa širim rasponom kao jaču
referentnu metodu.

## 5. Granice

Samo pet razvojnih skupina; fiksni polovi samo iz istih početnih polova kao VF. Nije provjerena
osjetljivost na N, nije dodana slika i nije provedena provjera finijom mrežom iz §6.
Završne skupine nisu dirane. Okvirni redovi iz opažanja 2 nisu najmanji redovi iz B6.

## 6. Slike za seminar

`experiments/figures_a7.py` crta dvije slike iz pokretanja `20261125T090048328276Z-convergence`.
Pokretanje slika `20261125T102501836176Z-figures_a7` (revizija `1258799`, čisto stablo) sprema
PDF za Overleaf, PNG za pregled i figures_a7.txt sa svim prikazanim vrijednostima. Boje su
plava redoslijedna ljestvica provjerena validatorom palete na bijeloj podlozi.

Prijedlozi opisa:

1. **fig_putanja:** relativni pomak polova δk i odmak pomoćnog nazivnika qk tijekom VF
   iteracije za krv (`vf_log`, početni polovi 10 MHz–10 GHz) uz r = 4, 7 i 10. Prag
   zaustavljanja je 10⁻⁸. Nakon ustaljenja obje veličine ostaju na razini šuma koja raste s r.
2. **fig_raspon:** broj razvojnih skupina (od pet) u kojima se VF petlja ustali, za tri
   raspona početnih polova. Uz šire raspone petlja se prestaje ustaljivati od r = 6–9, zbog
   gubitka ranga već u prvom koraku (opažanje 1).
