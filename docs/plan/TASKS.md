# Zadaci i ključne točke

Status se temelji na dokazima: plan nije implementacija, uspješne provjere alata nisu numerički
rezultati, a AI sažetak nije ljudsko odobrenje. Predložena podjela na niti opisana je u
[podjeli rada](PODJELA.md); Sara ju je potvrdila na sastanku Z0 2026-11-09. Svi su zadaci
zajednički.

## Pregled

| Zadatak | Cilj | Ovisi o | Stanje |
|---|---|---|---|
| T0 | Utvrditi kontekst projekta i prilagoditi tijek rada u repozitoriju | Korisnikove odluke o opsegu | Provedeno; Lovro je odobrio objavu i spajanje PR-a #1 bez Sarina pregleda, a Sarin naknadni pregled i povjerenje hookovima na svakom računalu preostaju |
| T1 | Razviti zajedničko matematičko razumijevanje na temelju rada Drmača, Gugercina i Beattieja | Kontekst T0 | Izvod B2 postoji, ispravljen je nakon pregleda i Lovro ga je neovisno provjerio (A9); A3 i A5 pripremljeni su za B9, a zajednički prolazi preostaju |
| T2 | Odabrati konkretan LTI SISO sustav i skup podataka frekvencijskog odziva | Kontekst T0 | Dovršeno 2026-11-07 (ADR-0004) |
| T3 | Dogovoriti inačicu metode, uzorkovanje, red i plan eksperimenata | T1, T2 | Prijedlog Z2 prihvaćen bez izmjena 2026-11-25 (ADR-0008); plan se zaključava nakon razvojnih kriterija B5 |
| T4 | Implementirati i provjeriti dogovorenu inačicu VF-a u Pythonu | T3 | Postoje samostalni LS korak, premještanje i refleksija polova te završni reziduali; puna petlja A4 provjerena je na sintetičkim sustavima i razvojnim skupinama (A7), a ne čeka usporedbu s B1 (odluka 2026-11-25); preostaje Sarin pregled |
| T5 | Provesti eksperimente koji omogućuju reprodukciju rezultata i protumačiti ih | T4, priprema podataka | Razvojna pokretanja A7 i B6 provedena 2026-11-25; završni pokus B6 čeka zaključavanje plana Z2 |
| T6 | Sastaviti pisani seminar i prezentaciju | Od T1 nadalje; konačni rezultati iz T5 | Otvoreno |
| T7 | Reproducirati konačne rezultate i zajedno uvježbati cjelovito objašnjenje | T5, T6 | Otvoreno |

Rok projekta je 2026-12-01 (prema Lovrinoj izjavi); prijedlog rasporeda je u
[podjeli rada](PODJELA.md#z0-dogovor). Ovo je redoslijed ovisnosti, a ne vremenski
raspored ili podjela pojedinih područja među članovima.

## B6: pokretač i razvojni pokusi, 2026-11-25

Na grani `lovro/b6-min-order` dodan je `experiments/min_order.py` prema ADR-0008 s dodatkom
nakon A7; opis, tumačenja i rezultati su u [zapisu B6](../izvodi/b6-najmanji-red.md).
Razvojno pokretanje `20261125T094340378378Z-min_order` obuhvaća 1280 slučajeva i traje 35 s.
Nema nerazriješenih procjena ni graničnih slučajeva. H1 je podržan u svih 48 razvojnih
usporedbi, a QuadVF medijalno treba 1–2 pola manje od `vf_log`. Razvojni kriteriji iz §7
su ispunjeni. Završni pokus `final_base` nije pokrenut jer zaključavanje plana odlučuje tim.
Pokretač je napisao AI alat na Lovrin zahtjev; nositeljica B6 Sara ga još nije pregledala.

Provjere: 9 novih testova; ukupno 318 numeričkih testova uz lokalnu Gabrielovu tablicu,
49 testova alata, Ruff, provjera dokumentacije i `python3 tools/check_before_stop.py`
prolaze.

## Z1, A9 i rok, 2026-11-25

Za prolaz Z1 pripremljeni su [vodič](Z1_PROLAZ.md) i `experiments/z1_blood.py`. Pokretanje
`20261125T091152576258Z-z1_blood` vodi od tablice preko VF koraka do Debyejevih članova i
pogrešaka za krv. Prolaz nije održan i zapis u vodiču je prazan.

Prema Lovrinoj izjavi Lovro je 2026-11-25 proveo A9: na papiru je neovisno provjerio Sarin
izvod B2 i nije našao pogreške. Pojedinosti provjere nisu zabilježene.

Prema Lovrinoj izjavi 2026-12-01 je dan izlaganja i predaje svih materijala. Prijedlog
rasporeda faza unatrag od tog dana nalazi se u [podjeli rada](PODJELA.md#z0-dogovor); tim ga
još nije potvrdio. Lovro je odlučio da A4 ne čeka usporedbu s B1; PR #20 zato izlazi iz
drafta, a usporedba s probnim kodom više nije uvjet prihvata A4.

Provjere: 3 nova testa za pokretač Z1; ukupno 309 numeričkih testova uz lokalnu Gabrielovu
tablicu, 49 testova alata, Ruff, provjera dokumentacije i `python3 tools/check_before_stop.py`
prolaze.

## A7: razvojno pokretanje, 2026-11-25

Na grani `lovro/a7-konvergencija` dodani su `experiments/convergence.py` i
`PoleResidueModel.is_debye` (s grane `lovro/debye-provjera`). Pokretanje
`20261125T084356823080Z-convergence` prolazi pet razvojnih skupina Z2 s postavkama iz
ADR-0008: 400 slučajeva, svaki s prihvaćenim zaustavljanjem i s cijelom putanjom.
[Zapis A7](../izvodi/a7-konvergencija.md) navodi opažanja. S primarnim rasponom početnih
polova 1 kHz–100 GHz petlja za r ≥ 9 staje zbog gubitka ranga već u prvom koraku, pa
`vf_log` na razvojnim skupinama ne doseže 0,1 %. Svi ustaljeni kandidati su Debyejevi
modeli, a ocjene (4.4) i q ≤ η vrijede do zaokruživanja.

Drugo pokretanje `20261125T090048328276Z-convergence` dodaje fiksne polove iz istih
početnih polova i sve redove u sva tri raspona. Tim je odluku o rasponu prepustio AI alatu
(prema Lovrinoj izjavi). Prema dodatku ADR-0008 primarni raspon za sva četiri postupka je
10 MHz–10 GHz, a fiksni polovi se dodatno računaju s 1 kHz–100 GHz kao jača referentna metoda.
Pokretač A7 sada kao primarni koristi raspon pojasa.

Provjere: 14 novih testova za pokretač A7 i 9 za provjeru Debyejeva modela; ukupno 306
numeričkih testova uz lokalnu Gabrielovu tablicu, 49 testova alata, Ruff, provjera
dokumentacije i `python3 tools/check_before_stop.py` prolaze. Završne skupine nisu pokretane,
nije dodana slika, a Sarin pregled i zajednički prolaz nisu provedeni.

## Z2: prihvat plana, 2026-11-25

Prema Lovrinoj izjavi Sara i Lovro su 2026-11-25 uživo na sastanku Z2 prihvatili svih 13
preporuka iz [prijedloga](Z2_PRIJEDLOG.md) bez izmjena. Odluka je zapisana u
[ADR-0008](adr/0008-accept-z2-experiment-plan.md), a metodologija, projekt, podjela rada,
osobni planovi, README i `AGENTS.md` usklađeni su s njom. Prijedlog preporuke ne numerira;
ADR sažima prihvaćeni tekst po odjeljcima.

Prema prihvaćenom §7 plan se zaključava tek nakon razvojnih kriterija B5. Za provedbu
preostaju usklađivanje kriterija pomaka u A4 s §5, statusi `poles_and_denominator_settled` i
`ill_conditioned` te kontrolna mreža iz §6. Zapis ne potvrđuje Sarin pregled PR-a ni rezultate.

## A4: nacrt pune petlje, 2026-11-25

Na grani `lovro/a4-vf-petlja` pripremljena je petlja `vfdebye.vf.vector_fit` prema
zajedničkom sučelju, opisana u [A4](../izvodi/a4-implementacija.md). Kontrole zaustavljanja,
refleksije i kruženja zadaje pozivatelj. Nakon prihvata Z2 prag pomaka koristi maksimum
dviju skala, a dodan je status `poles_and_denominator_settled` (ADR-0008, §5). Povijest čuva svaki LS
korak te sirove i upotrijebljene polove. Gubitak ranga, nevaljana nova baza, numerička
pogreška, kruženje i iscrpljene iteracije vraćaju se izričito. `experiments/vf_checks.py`
provjerava tri sintetička sustava poznatih polova uz zapis podrijetla.

Ovo je nacrt prije usporedbe sa Sarinim B1: B1 nije preuzet, A7 i eksperimenti na tkivima
nisu pokrenuti, a Sarin pregled i zajednički prolaz nisu provedeni.

Provjere: 41 novi numerički slučaj za petlju i pokretač, uključujući prag kao maksimum dviju
skala; ukupno 283 numerička testa uz lokalnu Gabrielovu tablicu, 49 testova alata, Ruff,
provjera dokumentacije i `python3 tools/check_before_stop.py` prolaze. Nova ovisnost nije dodana.

## Z2: priprema prijedloga, 2026-11-23

Na grani `lovro/z2-prijedlog` pripremljen je [konkretan prijedlog](Z2_PRIJEDLOG.md):
definicija H, pet razvojnih i 36 završnih skupina parametara, četiri usporediva postupka,
početni polovi, svi redovi 1–32, zaustavljanje, razdvajanje Debyejevih i općih racionalnih
modela, neovisno vrednovanje i proračun od 5568 slučajeva. Identitet CSV-a i podjela 8/47
disperzivnih naziva provjereni su prema lokalnom ulazu. Raniji pregled svih skupina u B3
izričito je naveden; završni skup nije predstavljen kao dosad neviđen.

Z2 nije održan ni prihvaćen. Nositeljica je Sara, sudjeluju oboje; konačni plan slijedi B5.
Nema novih pokretača, ovisnosti ni rezultata. Predložene brojke ne mijenjaju postojeće
algoritme. Puna petlja A4 i dalje čeka B1, a A7 i završni eksperimenti potvrđene postavke.

Provjere: identitet CSV-a, članstvo skupina i zbrojevi slučajeva provjereni su lokalno.
`python3 tools/check_before_stop.py` prolazi: 242 numerička testa uz lokalnu tablicu,
49 testova alata, Ruff i provjera dokumentacije. `git diff --check` nema nalaza.
Numerička implementacija nije mijenjana; novi testovi za sam prijedlog nisu dodani.

## A5: izvod i samostalne numeričke operacije, 2026-11-23

Na grani `lovro/a5-polovi-reziduali` pripremljen je [izvod A5](../izvodi/a5-polovi-reziduali.md)
i pojedinačne operacije u `vfdebye.vf`: baricentrični LS korak, premještanje polova,
izričito zrcaljenje i završni izračun reziduala. Za realne sustave obrađeni su i realni polovi
i konjugirani parovi. Vraćaju se težinski rezidual, numerički rang i uvjetovanost realne
matrice. Gubitak ranga i nevaljani ulazi ne popravljaju se prešutno. Ne provodi se automatska
stabilizacija ni odluka o konvergenciji.

Ovaj rad koristi L1 i [izvod A3](../izvodi/a3-problem-sk.md), uključen s grane
`lovro/a3-izvod-vf` kao ovisnost grane A5. Promjene A3 i A5 pregledavaju se zasebnim PR-ovima.
Numeričke operacije mogu se neovisno provjeriti bez B1 i Z2. Za potpunu petlju A4 i dalje
treba pregledati B1, a A7 i eksperimenti čekaju zapisane postavke Z2. Za prihvat izvoda A5
preostaje Sarin neovisni pregled B9; zajednički prolaz i razumijevanje nisu potvrđeni.

Provjere: 72 nova numerička slučaja za operacije A5 prolaze, uključujući promjenu frekvencijske
skale, težinski cilj, konjugirane parove, višestruke korijene i gubitak ranga uz nulte podatke.
Ukupno prolaze 242 numerička testa uz lokalnu ignoriranu Gabrielovu tablicu i 49 testova alata,
Ruff, provjera dokumentacije i `python3 tools/check_before_stop.py`. Nova ovisnost nije dodana.
Ovo su lokalne provjere; udaljene provjere na Linuxu i Windowsu izvode se u CI-ju PR-a.

## A3: priprema izvoda, 2026-11-23

Na grani `lovro/a3-izvod-vf` pripremljen je [izvod A3](../izvodi/a3-problem-sk.md):
permitivnost kao realan LTI SISO opis, izdvajanje poznatih članova, veza Cole–Coleova i
Debyejeva člana, nekonveksnost racionalne aproksimacije, Levyjeva linearizacija, SK težine i
izvodi polinomne i baricentrične matrice. Ručni primjer reda jedan ima poznat pol i rezidual.
Posebno je razjašnjena razlika normalizacija nazivnika pri promjeni baze. Ovaj korak ne bira
postavke Z2 i ne implementira VF. A3 ovisi o provedenom Z0; za prihvat izvoda preostaje Sarin
neovisni pregled B9. Zajedničko razumijevanje time nije potvrđeno. A5 može nastaviti izvod,
a implementacija A4 i dalje čeka B1.

Lokalne provjere: izravnim izračunom potvrđeni su uzorci, obje LS matrice i rješenja ručnog
primjera. Na dodatnom primjeru s nenultim rezidualom provjereni su prijenos moničnog
polinomnog problema u baricentrični i faktor promjene normalizacije. Završna provjera
`python3 tools/check_before_stop.py` prolazi: 170 numeričkih testova, 49 testova alata, Ruff i
provjera dokumentacije. Novi automatski testovi nisu dodani jer se mijenja izvod, a ne
numerička implementacija. CI za ovu lokalnu promjenu nije pokrenut.

## Pregled i ispravci B2–B4, 2026-11-23

Lovro je zatražio pregled Sarinih PR-ova #14–#16, zatim ispravke nalaza i spajanje. U PR-u #14
ispravljene su tvrdnje o konvergenciji i optimalnosti te tumačenje norme na pojasu. PR #15
preuzima ispravak, odbija kompleksne težine s nenultim imaginarnim dijelom i izračun omjera
normi više ne naziva pogreškom dopuštenog racionalnog modela. PR #16 provjerava realnost polova
i težina te oblik i konačnost odziva modela, prijavljuje nultu referentnu normu i odbija konačne
negativne pogreške pri odabiru reda. Sve nekonačne oznake neuspjelih fitova preskače.
Numerički algoritam i otvorene odluke Z2 time se ne biraju. A4 i dalje čeka probni kod B1;
ovaj pregled ne bilježi zajednički prolaz ni potvrdu razumijevanja članova.

Provjere B3: 112 numeričkih testova, Ruff i završna provjera prolaze. Pokretanje
`20261123T143501129808Z-quadrature_checks` ponovno računa tablice za svih 41 različitih
disperzivnih skupova parametara; podrijetlo i izvještaj ostaju u lokalnom direktoriju pokretanja
opisanom u [tijeku rada](PIPELINE.md), izvan Gita.

Provjere cijelog lanca nakon ispravaka B4: 170 numeričkih testova prolazi, uključujući 21 novi
regresijski slučaj u odnosu na izvorni vrh PR-a #16. Novi testovi prije ispravka otkrivaju
odbacivanje imaginarnih dijelova, proširivanje oblika, dijeljenje nulom i prihvaćanje nevaljane
pogreške. Ruff, provjera dokumentacije i završna provjera također prolaze.

## Podjela rada

Prijedlog od 2026-11-01 Lovro je prihvatio, a na sastanku 2026-11-03 naveo je uloge: osoba A je
Lovro, a osoba B Sara. Nakon izbora teme rad je 2026-11-07 predloženo podijeliti na dvije niti od
matematike do rezultata, uz međusobni pregled
([ADR-0005](adr/0005-divide-work-into-end-to-end-threads.md)). Niti, sučelja, faze i zadaci
nalaze se u [podjeli rada](PODJELA.md), a koraci u osobnim planovima. PR-ovi #5 i #6 spojeni su
bez Sarina pregleda (ADR-0002, dodatak 2026-11-07). Prema Lovrinoj izjavi Sara je podjelu
potvrdila na sastanku Z0 2026-11-09 (ADR-0005, dodatak 2026-11-09).

Načela ostaju ista. Kod, testove i nacrte piše AI alat (dodatak zapisa ADR-0001), a autor commita
je član koji vodi rad (ADR-0003). Testovi se temelje na izvodu i analitičkim primjerima, a ne na
kodu koji provjeravaju. Nositelj niti nije jedina osoba koja je razumije: recenzent neovisno
provjerava izvode i reproducira eksperimente. Rad nije dovršen dok ga oba člana ne mogu objasniti
i obraniti.

Zadaci T0–T7 ostaju pregled ovisnosti. Zadaci iz podjele rada razrađuju ih: T1 obuhvaća A3, A5 i
B2; T3 obuhvaća Z2; T4 obuhvaća A1, A2, A4, A6, B1, B3 i B4; T5 obuhvaća A7, B5, B6 i B7; T6
obuhvaća A8, A10, B8, B10 i Z5; T7 obuhvaća Z4 i Z6.

## T0: postavljanje tijeka rada

Pripremiti pravila, pregled literature, metodološki plan, zapise odluka, popis za usklađivanje
dokumentacije, predložak PR-a, CI, završne provjere i definiciju dnevnog audita prema projektu
nonneg-matrix-fact-clustering. Provjeriti lokalno. Razlikovati pripremljenu konfiguraciju od
pouzdanih i aktivnih hookova te tijekova rada omogućenih na udaljenom repozitoriju. Ne raditi
commit, push ni objavljivati sadržaj na GitHubu bez ovlaštenja.

Lokalna provjera 2026-10-28: provjera dokumentacije prijavila je 0 upozorenja i prošlo je svih
45 testova alata za tijek rada. Završna provjera pokrenuta je iz korijena repozitorija u CLI i
`--hook` načinu, a Claude i Codex naredbe hookova i iz podmape: valjan JSON, uz izričitu oznaku
NOT RUN za numeričke provjere. To ne dokazuje povjerenje na računalu ni automatsko pokretanje
hookova.

Snimka stanja GitHuba 2026-10-28 (samo čitanje, prije objave): privatni repozitorij pod računom
`saragrguric` sa zadanom granom main i početnim commitom `a21a894` (README), suradnici
`saragrguric` i `LRazum` (ovlast pisanja), bez tijekova rada, prijava, PR-ova i oznaka
finding; postoje samo zadane GitHub oznake. Stanje zaštite grane nije bilo moguće pročitati s
ovlašću pisanja (HTTP 404), pa ga treba provjeriti vlasnik repozitorija.

Lovro je zatim izričito zatražio commit, push, PR i spajanje u `main`. Početni PR #1 s grane
`codex/seminar-workflow` koristi tu dokumentiranu iznimku od pregleda (dodatak zapisa ADR-0002);
ne tvrdi se da ga je odobrila Sara, koja ga treba naknadno pregledati. PR i izvršavanja GitHub
Actions bilježe objavu i udaljenu provjeru. Preduvjeti objave i aktivacije navedeni su u
[uputama za tijek rada](PIPELINE.md); povjerenje hookovima na pojedinom računalu ostaje zasebno
provjeriti.

## T1: matematičko razumijevanje

Proći sadržaj iz [metodološkog plana](METHODOLOGY.md), uz odgovarajuće odjeljke izvora iz
[vodiča kroz literaturu](../research/LITERATURE.md). Izraditi čitljive izvode s navedenim
pretpostavkama i malim razrađenim primjerom. Razlikovati dokazanu tvrdnju od intuicije ili
empirijskog opažanja. Zajedno proći oznake, funkciju cilja, linearizaciju i mehanizam
premještanja polova.

Zadatak je dovršen kada su bilješke pregledane, nejasnoće zabilježene i oba člana mogu
objasniti matematički argument. Ne označiti ga dovršenim samo zato što su bilješke generirane.

## T2: sustav i skup podataka

Cilj seminara nije reprodukcija rada, nego primjena metode na rješavanje konkretnog problema.
Kandidat mora imati pitanje na koje model daje odgovor i odluku ili predviđanje koje se bez
modela ne bi moglo jednako dobro donijeti.

Usporediti manji broj konkretnih kandidata prema pitanju na koje odgovaraju, načinu nastanka
frekvencijskog odziva (mjerenje, simulacija ili model), mogućnosti računanja vrijednosti u
proizvoljnim točkama, postojanju referentnog modela za globalnu pogrešku, šumu, dostupnosti i
licenci, izvedivoj veličini, interpretaciji i evaluaciji. Objasniti po čemu se konkretni problem
i podaci razlikuju od primjera korištenih u radu (modeli iz zbirke NICONET i modul ISS 1R). Tim odabire kandidata i
bilježi odluku.

[Prijedlog tema](prijedlog-tema/prijedlog-tema-vf.pdf) (2026-11-07) uspoređuje tri kandidata:
HRTF-ove iz skupa HUTUBS, impedancijske spektre litij-ionskih ćelija i FRF-ove kompozitne ploče.
Isti su dan razmotreni i toplinski model zida te Debyejevi modeli ljudskih tkiva.

**Dovršeno 2026-11-07.** Tim je odabrao Debyejeve modele tkiva
([ADR-0004](adr/0004-choose-debye-models-of-human-tissues.md)). Pitanje je koliko je realnih
polova najmanje potrebno za zadanu točnost i štede li VF i QuadVF polove. Podaci su parametri
Gabrielova modela za tkiva iz Gabrielove tablice; preuzimanje i model tkiva
opisani su u [podacima](../../data/README.md) (zadatak A2).

Zadatak završava dogovorenim istraživačkim pitanjem, opisom izvora i podataka, planom
predobrade, predviđenim značenjem modela i izvedivom evaluacijom.

## T3: metoda i plan eksperimenata

Povezati inačicu metode i uzorkovanje s odabranim podacima i pitanjem. Dogovoriti redove,
čvorove i težine, parametar kvadrature, početne polove, zrcaljenje, regularizaciju, kriterije
zaustavljanja, referentnu metodu, metrike i raspoložive računalne resurse. Hipoteze i pitanja
zapisati prije pregleda konačnih rezultata. Ne dodavati inačice samo radi popunjavanja usporedne
tablice. Važne izbore i odbačene mogućnosti zabilježiti u ADR-u.

## T4: implementacija u Pythonu

Predloženo: što manja implementacija koju piše AI alat, s NumPyjem, SciPyjem i Matplotlibom,
bez vlastitih okvira. Ostali detalji implementacije namjerno su odgođeni. Na početku rada dodati definiciju okruženja
i zaključane verzije ovisnosti, ponovno upotrebljiv numerički kod i smislene testove, zajedno
s izvršavanjem projektnih provjera i naredbama za CI. Ponašanje usporediti s neovisnim malim
primjerima i, kada je korisno, bibliotečnom implementacijom s usklađenim postavkama.
Objasniti razlike u funkciji cilja, težinama, čvorovima i kriteriju zaustavljanja.

## T5: eksperimenti i interpretacija

Primjeri iz rada i poznati modeli služe samo za provjeru implementacije; glavni rezultat je
odgovor na pitanje iz T2. Implementirati ponovljiva pokretanja i sačuvati podatke o podrijetlu
rezultata. Izvijestiti o prilagodbi uzorcima, globalnoj pogrešci gdje je mjerljiva, pitanju domene, osjetljivosti na red,
uzorkovanje i početne polove te neuspjesima i ograničenjima. Svaku prikazanu tablicu i sliku
povezati s pokretanjem koje ju je proizvelo. Sam povoljan primjer nije dovoljan.

## T6: seminar i prezentacija

Pisati nacrte odjeljaka kako se razvija razumijevanje, zatim privremeni sadržaj zamijeniti
provjerenim rezultatima. Oznake, algoritam, postavke, slike i zaključke uskladiti s kodom.
Seminar i prezentaciju pišemo u Overleafu, izvan ovog repozitorija. Slike i tablice prenose se
iz `results/` zajedno s identifikatorom pokretanja koje ih je stvorilo. Seminar i prezentaciju
pisati na hrvatskom. Uključiti citate i razlikovati preuzete slike od slika nastalih u ovom projektu.

## T7: završna reprodukcija rezultata i zajednički prolazak

U novom okruženju reproducirati prikazane rezultate. Predaju provjeriti prema naknadno
utvrđenim zahtjevima kolegija. Oba člana vježbaju objašnjavanje cijelog puta od problema
i matematike do koda, rezultata i ograničenja. Zabilježiti stvarnu provjeru, preostale
nejasnoće i mjesta konačnih materijala; ne izmišljati odobrenja ni spremnost za predaju.
