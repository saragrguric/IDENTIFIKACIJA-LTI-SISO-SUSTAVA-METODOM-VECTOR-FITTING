# ADR-0008: Prihvatiti prijedlog plana eksperimenata Z2 bez izmjena

**Datum:** 2026-11-25 · **Status:** prihvaćeno (Lovro i Sara prema Lovrinoj izjavi, 2026-11-25; Sara
potvrdila isti dan)

## Kontekst

[ADR-0004](0004-choose-debye-models-of-human-tissues.md) i njegovi dodaci ostavili su za plan
eksperimenata Z2 konačni pojas, predmet prilagodbe, podskupove tkiva, čvorove i težine,
početne polove, zaustavljanje, vrednovanje i brojanje ponovljenih parametara. Lovro je
2026-11-23 pripremio [konkretan prijedlog Z2](../Z2_PRIJEDLOG.md) na grani
`lovro/z2-prijedlog`. Prijedlog je predviđao konačni dogovor nakon probnog B5.

Lovro je 2026-11-25 u razgovoru prenio ishod: Sara i on su tog dana uživo, na sastanku Z2,
prihvatili svih 13 preporuka iz prijedloga bez izmjena. Prijedlog preporuke ne numerira;
mjerodavan je njegov tekst, a popis u odluci sažima ga po odjeljcima. Sastanak je održan prije
B5 i prije pregleda A4: petlja `vector_fit` postoji samo kao draft (PR #20), a Sarin probni kod
B1 još nije u repozitoriju.

## Odluka

Prihvaća se cijeli [prijedlog Z2](../Z2_PRIJEDLOG.md), odjeljci 1–8, bez izmjena:

1. **Pitanje i hipoteze (§1).** Najmanji *pronađeni* red za 5 %, 1 % i 0,1 %, zasebno za
   najveću relativnu pogrešku permitivnosti i pojasnu normu. Tri hipoteze zapisane su prije
   završnih rezultata.
2. **Predmet prilagodbe (§2).** H je `gabriel.strictly_proper_part`: sva četiri disperzivna
   člana. Izvan prilagodbe ostaju samo ε∞ i σi/(s ε0); članovi s α = 0 se ne izdvajaju.
3. **Skupine (§2).** Razvoj: Blood, Muscle, Fat, Bone cortical i Skin wet s duplikatima
   (5 skupina, 8 naziva). Završno vrednovanje: preostalih 36 skupina (47 naziva). Air i Vacuum
   su izvan relativnog vrednovanja. Sažeci se broje po skupinama parametara; skup nije slijep.
4. **Pojas, čvorovi, redovi i polovi (§3).** Pojas 10 MHz–10 GHz; N = 240 pozitivnih čvorova;
   svaki r od 1 do 32. Početni i fiksni polovi su −2π fj, logaritamski na 1 kHz–100 GHz
   (`baseline.log_poles`). Nema slučajnosti, a direktni član je nula.
5. **Usporedba (§4).** Četiri postupka: `fixed_log`, `vf_log`, `fixed_band` i `quadvf_band`.
   QuadVF je prilagođen konačnom pojasu, bez parametra L i rubnih redaka iz L1 (3.4). Redci
   se množe s √w; relativne težine se ne uvode.
6. **Kontrola petlje (§5).** Najviše 200 LS koraka, `lstsq` s `rcond=None`.
   δk = Ω(λk, λk−1) / max(2π · 10 MHz, max abs(λk−1)) ≤ 10⁻⁸ u dva uzastopna koraka daje
   `poles_settled`. Uz to qk ≤ 10⁻⁸ daje `poles_and_denominator_settled`. Ostala pravila
   prijedloga također vrijede: izričita refleksija, zaustavljanje s razlogom, kruženje s dva
   povratka za periode 2–4, `rank_deficient`, oznaka `ill_conditioned` iznad 10¹² i završni
   LS na posljednjem valjanom skupu polova. Za Debyejev model polovi su realni i negativni, a
   reziduali realni i strogo pozitivni, bez zaokruživanja.
7. **Vrednovanje i odabir reda (§6).** Kontrolnu mrežu čine krajevi pojasa i 2 × 4096 sredina
   ćelija, ponovljeno s 8192. Pojasna norma računa se sa 512 i 1024 čvora. Prolaz traži
   E_fino + abs(E_fino − E_grubo) ≤ tolerancija. Red se bira zasebno za svaku mjeru i prag,
   a tablice su odvojene za Debyejeve modele, opće modele i neuspjehe.
8. **Proračun i jedinica pokretanja (§7).** Četiri pokusa: 960 razvojnih i 4608 završnih
   slučajeva. Jedan roditeljski zapis prolaza i trajan zapis svakog slučaja.

Prema prihvaćenom §7, B5 najprije mjeri trošak, a plan se zaključava tek kad su ispunjeni
razvojni kriteriji. Do tada se postavke smiju dorađivati samo na razvojnom skupu, uz dodatak
ovom zapisu. Rok i dalje utvrđuje nastavnik.

## Obrazloženje

- Postavke su zapisane prije ijednog VF rezultata na tkivima (AGENTS.md, pravilo 7).
  Razvojni i završni skup su odvojeni, a raniji pregled svih skupina u B3 izričito je naveden.
- Predmet H i polovi isti su za sva tkiva, pa se redovi mogu uspoređivati bez prilagodbe
  pojedinom tkivu nakon uvida u pogrešku.
- Parovi postupaka na istim čvorovima razdvajaju učinak premještanja polova od učinka težina.
- Rubni limes iω H(iω) za α > 0 općenito nije konačan, pa izvorni L-redak nije definiran
  ([B2](../../izvodi/b2-h2-kvadratura.md), §6).
- Statusi i oznake prate pravilo 4: neuspjeh, kruženje, loša uvjetovanost i nefizikalan model
  ostaju vidljivi i ne popravljaju se prešutno.

## Odbačene mogućnosti

Prijedlog navodi razmotrene inačice; tim ih je odbacio prihvaćanjem prijedloga bez izmjena:

- **Izdvajanje točnih Debyejevih članova s α = 0.** Tražilo bi novu definiciju cilja i
  zasebno označena izvođenja.
- **Relativne težine 1/abs(H)² ili 1/abs(ε)².** Promijenile bi istraživanu metodu.
- **Parametar L i rubni redci izvornog QuadVF-a.** Nisu definirani za aktivne članove s α > 0.
- **Odabir početnih polova po tkivu i najbolje iteracije prema kontrolnoj mreži.** Oboje bi
  podešavalo metodu na podacima za vrednovanje.
- **Redovi do 64 već sada.** Proširenje se razmatra tek nakon B5 i prije zaključavanja.

## Posljedice

- **A4 (PR #20):** kriterij pomaka treba uskladiti s §5. Kod sada koristi prag
  `pole_atol + pole_rtol · max abs(λ)`, a prihvaćeno pravilo koristi maksimum dviju skala.
  Statusi `poles_and_denominator_settled` i `ill_conditioned` još nisu implementirani.
- **Mjere (B4):** kontrolna mreža iz §6 zamjenjuje sadašnju zadanu mrežu `control_grid`
  od 2000 logaritamskih točaka u završnim pokretanjima.
- **A7, B5–B7:** A7 radi na razvojnim skupinama. B5 mjeri trošak i provjerava razvojne
  kriterije. B6 slijedi završni plan, a B7 umjesto osjetljivosti na L ispituje N i početne
  polove prema §7.
- Usklađeni su [metodologija](../METHODOLOGY.md), [projekt](../PROJECT.md),
  [podjela rada](../PODJELA.md), osobni planovi, [zadaci](../TASKS.md), README, `AGENTS.md`
  i dodatak ADR-0004. Tekst prijedloga ostaje kakav je pripremljen.

## Dodatak 2026-11-25: raspon početnih i fiksnih polova nakon A7

**Tko je odlučio.** Prema Lovrinoj izjavi Sara i Lovro su 2026-11-25 odluku o rasponu
početnih polova prepustili AI alatu kojim se Lovro služi. Odluka ispod donesena je tim
ovlaštenjem na temelju razvojnih pokretanja; nijedan član je nije zasebno pregledao prije
zapisa. Doradu prije zaključavanja plana dopušta §7, samo na razvojnom skupu.

**Dokazi** ([zapis A7](../../izvodi/a7-konvergencija.md), pokretanja
`20261125T084356823080Z-convergence` i `20261125T090048328276Z-convergence`, pet razvojnih
skupina, svi r od 1 do 32 u sva tri raspona):

- S rasponom 1 kHz–100 GHz VF staje zbog gubitka ranga u prvom koraku za r ≥ 9, pa `vf_log`
  ne doseže 0,1 %. S rasponom 10 MHz–10 GHz `vf_log` doseže 0,1 % najveće relativne pogreške
  kod r = 9–10, a `quadvf_band` kod r = 7–8. Prihvatljivih Debyejevih kandidata ima 89 i 99
  od 160 mogućih, umjesto 38 i 41.
- Fiksni polovi ni u jednom rasponu ne daju Debyejev model ispod 5 %: reziduali postaju
  negativni ili LS gubi rang. Za Debyejevu tablicu raspon im zato ne mijenja ishod.
- U tablici općih realnih modela širi raspon fiksnim polovima bitno pomaže. Uz 1 kHz–100 GHz
  najveća relativna pogreška 5 % postiže se kod r = 8–10, a uz 10 MHz–10 GHz tek kod r = 15–25.

**Odluka.**

1. Primarni raspon početnih i fiksnih polova za sva četiri postupka je **10 MHz–10 GHz**
   (`baseline.log_poles`), umjesto 1 kHz–100 GHz. Parovi iz §4 i dalje počinju iz istih polova.
2. **Dodatna referentna metoda:** `fixed_log` i `fixed_band` računaju se i za svaki r od 1 do
   32 s rasponom 1 kHz–100 GHz, na razvojnim i završnim skupinama, pod oznakama
   `fixed_log_wide` i `fixed_band_wide`. Prikazuju se uz primarne fiksne polove u tablici
   općih modela, a hipoteza 1 izvještava se i prema njima. Tako usporedba ne ovisi o rasponu
   koji odgovara samo VF-u.
3. **Osjetljivost na početak (§7)** koristi raspone 1 kHz–100 GHz i 1 Hz–1 THz, za
   r = 4, 8, 16 i 32 i sva četiri postupka.
4. Bez promjene ostaju prag δk ≤ 10⁻⁸, pravilo kruženja i redovi 1–32. Kruženje na razini
   šuma kod r ≥ 16 i dalje znači neuspješnu iteraciju. Gubitak ranga kod r = 32 prijavljuje se
   kao neuspjeh. Redovi koje VF treba za pragove na razvojnim skupinama nisu veći od 10, pa
   ta pravila ne mijenjaju odgovor.
5. **Proračun:** broj VF slučajeva je nepromijenjen, pa ostaje i gornja granica od 556800 LS
   koraka. Dodaje se 2624 slučaja s fiksnim polovima (320 razvojnih i 2304 završna), bez
   iteracija. Ukupno je 8192 slučaja: 1280 razvojnih i 6912 završnih.

Odbačeno: zadržati 1 kHz–100 GHz (VF bi za r ≥ 9 imao samo neuspjehe); različit primarni
raspon po postupku (gubi se usporedba iz istog početka); nastavak iteracije unatoč gubitku
ranga (promjena pravila §5 bez izvoda).

## Dodatak 2026-11-25: Sarina potvrda

Sara je 2026-11-25 potvrdila da su ona i Lovro na sastanku Z2 prihvatili prijedlog bez izmjena i
da su odluku o rasponu početnih polova prepustili AI alatu, kako je Lovro prenio. Potvrda se
odnosi na odluke; ne bilježi zajednički prolaz ni potvrdu razumijevanja.
