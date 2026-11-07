# Zadaci i ključne točke

Status se temelji na dokazima: plan nije implementacija, uspješne provjere alata nisu numerički
rezultati, a AI sažetak nije ljudsko odobrenje. Predložena podjela na niti opisana je u
[podjeli rada](PODJELA.md); Sara je potvrđuje na sastanku Z0. Svi su zadaci zajednički.

## Pregled

| Zadatak | Cilj | Ovisi o | Stanje |
|---|---|---|---|
| T0 | Utvrditi kontekst projekta i prilagoditi tijek rada u repozitoriju | Korisnikove odluke o opsegu | Provedeno; Lovro je odobrio objavu i spajanje PR-a #1 bez Sarina pregleda, a Sarin naknadni pregled i povjerenje hookovima na svakom računalu preostaju |
| T1 | Razviti zajedničko matematičko razumijevanje na temelju rada Drmača, Gugercina i Beattieja | Kontekst T0 | Spremno za početak |
| T2 | Odabrati konkretan LTI SISO sustav i skup podataka frekvencijskog odziva | Kontekst T0 | Dovršeno 2026-11-07 (ADR-0004) |
| T3 | Dogovoriti inačicu metode, uzorkovanje, red i plan eksperimenata | T1, T2 | Djelomično: metode i mjere u ADR-0004; ostatak u Z2 |
| T4 | Implementirati i provjeriti dogovorenu inačicu VF-a u Pythonu | T3 | Odgođeno do dogovora tima o implementaciji |
| T5 | Provesti eksperimente koji omogućuju reprodukciju rezultata i protumačiti ih | T4, priprema podataka | Otvoreno |
| T6 | Sastaviti pisani seminar i prezentaciju | Od T1 nadalje; konačni rezultati iz T5 | Otvoreno |
| T7 | Reproducirati konačne rezultate i zajedno uvježbati cjelovito objašnjenje | T5, T6 | Otvoreno |

Rok projekta nije poznat. Ovo je redoslijed ovisnosti, a ne vremenski raspored ili podjela
pojedinih područja među članovima.

## Podjela rada

Prijedlog od 2026-11-01 Lovro je prihvatio, a na sastanku 2026-11-03 naveo je uloge: osoba A je
Lovro, a osoba B Sara. Nakon izbora teme rad je 2026-11-07 predloženo podijeliti na dvije niti od
matematike do rezultata, uz međusobni pregled
([ADR-0005](adr/0005-divide-work-into-end-to-end-threads.md)). Niti, sučelja, faze i zadaci
nalaze se u [podjeli rada](PODJELA.md), a koraci u osobnim planovima. Sara potvrđuje podjelu na
sastanku Z0 ili odobrenjem PR-a koji je uvodi; ovaj zapis to ne zamjenjuje.

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
Gabrielova modela za 44 tipa tkiva; tablica još nije preuzeta u repozitorij (zadatak A2).

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
Odabrati izvorne formate i naredbe za izradu prije tvrdnje da je bilo koji od tih materijala
moguće izgraditi. Seminar i prezentaciju pisati na hrvatskom. Uključiti citate i razlikovati
preuzete slike od slika nastalih u ovom projektu.

## T7: završna reprodukcija rezultata i zajednički prolazak

U novom okruženju reproducirati prikazane rezultate. Predaju provjeriti prema naknadno
utvrđenim zahtjevima kolegija. Oba člana vježbaju objašnjavanje cijelog puta od problema
i matematike do koda, rezultata i ograničenja. Zabilježiti stvarnu provjeru, preostale
nejasnoće i mjesta konačnih materijala; ne izmišljati odobrenja ni spremnost za predaju.
