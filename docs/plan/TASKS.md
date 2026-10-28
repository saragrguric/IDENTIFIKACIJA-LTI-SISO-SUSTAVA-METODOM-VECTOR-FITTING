# Zadaci i ključne točke

Status se temelji na dokazima: plan nije implementacija, uspješne provjere alata nisu numerički
rezultati, a AI sažetak nije ljudsko odobrenje. Pojedinačna zaduženja nisu dogovorena. Svi su
zadaci zajednički; privremenog nositelja i osobu za pregled moguće je zabilježiti kasnije.

## Pregled

| Zadatak | Cilj | Ovisi o | Stanje |
|---|---|---|---|
| T0 | Utvrditi kontekst projekta i prilagoditi tijek rada u repozitoriju | Korisnikove odluke o opsegu | Pripremljeno lokalno na grani `codex/seminar-workflow`; nije commitano ni objavljeno, čeka Sarin pregled |
| T1 | Razviti zajedničko matematičko razumijevanje na temelju rada Drmača, Gugercina i Beattieja | Kontekst T0 | Spremno za početak |
| T2 | Odabrati konkretan LTI SISO sustav i skup podataka frekvencijskog odziva | Kontekst T0 | Otvoreno; može teći usporedno s T1 |
| T3 | Dogovoriti inačicu metode, uzorkovanje, red i plan eksperimenata | T1, T2 | Otvoreno |
| T4 | Implementirati i provjeriti dogovorenu inačicu VF-a u Pythonu | T3 | Odgođeno do dogovora tima o implementaciji |
| T5 | Provesti eksperimente koji omogućuju reprodukciju rezultata i protumačiti ih | T4, priprema podataka | Otvoreno |
| T6 | Sastaviti pisani seminar i prezentaciju | Od T1 nadalje; konačni rezultati iz T5 | Otvoreno |
| T7 | Reproducirati konačne rezultate i zajedno uvježbati cjelovito objašnjenje | T5, T6 | Otvoreno |

Rok projekta nije poznat. Ovo je redoslijed ovisnosti, a ne vremenski raspored ili podjela
pojedinih područja među članovima.

## T0: postavljanje tijeka rada

Pripremiti pravila, pregled literature, metodološki plan, zapise odluka, popis za usklađivanje
dokumentacije, predložak PR-a, CI, završne provjere i definiciju dnevnog audita prema projektu
nonneg-matrix-fact-clustering. Provjeriti lokalno. Razlikovati pripremljenu konfiguraciju od
pouzdanih i aktivnih hookova te tijekova rada omogućenih na udaljenom repozitoriju. Ne raditi
commit, push ni objavljivati sadržaj na GitHubu bez ovlaštenja.

Lokalna provjera 2026-10-28: provjera dokumentacije prijavila je 0 upozorenja i prošla su sva
45 testova alata za tijek rada. Završna provjera pokrenuta je iz korijena repozitorija u CLI i
`--hook` načinu: valjan JSON, uz izričitu oznaku NOT RUN za numeričke provjere. To ne dokazuje
povjerenje na računalu ni automatsko pokretanje hookova.

Snimka stanja GitHuba 2026-10-28 (samo čitanje, prije objave): privatni repozitorij pod računom
`saragrguric` sa zadanom granom main i početnim commitom `a21a894` (README), suradnici
`saragrguric` i `LRazum` (ovlast pisanja), bez tijekova rada, prijava, PR-ova i oznaka
finding; postoje samo zadane GitHub oznake. Stanje zaštite grane nije bilo moguće pročitati s
ovlašću pisanja (HTTP 404), pa ga treba provjeriti vlasnik repozitorija. Commit, push, PR i
spajanje postavljanja nisu odobreni. Prema pravilu pregleda PR za postavljanje odobrava Sara,
osim ako korisnik izričito odobri iznimku za točan PR. Preduvjeti objave i aktivacije navedeni
su u [uputama za tijek rada](PIPELINE.md).

## T1: matematičko razumijevanje

Proći sadržaj iz [metodološkog plana](METHODOLOGY.md), uz odgovarajuće odjeljke izvora iz
[vodiča kroz literaturu](../research/LITERATURE.md). Izraditi čitljive izvode s navedenim
pretpostavkama i malim razrađenim primjerom. Razlikovati dokazanu tvrdnju od intuicije ili
empirijskog opažanja. Zajedno proći oznake, funkciju cilja, linearizaciju i mehanizam
premještanja polova.

Zadatak je dovršen kada su bilješke pregledane, nejasnoće zabilježene i oba člana mogu
objasniti matematički argument. Ne označiti ga dovršenim samo zato što su bilješke generirane.

## T2: sustav i skup podataka

Usporediti manji broj konkretnih kandidata prema pitanju na koje odgovaraju, načinu nastanka
frekvencijskog odziva (mjerenje, simulacija ili model), mogućnosti računanja vrijednosti u
proizvoljnim točkama, postojanju referentnog modela za globalnu pogrešku, šumu, dostupnosti i
licenci, izvedivoj veličini, interpretaciji i evaluaciji. Objasniti po čemu se konkretni problem
i podaci razlikuju od primjera korištenih u radu (modeli iz zbirke NICONET i modul ISS 1R). Tim odabire kandidata i
bilježi odluku. Skup podataka još nije odabran.

Zadatak završava dogovorenim istraživačkim pitanjem, opisom izvora i podataka, planom
predobrade, predviđenim značenjem modela i izvedivom evaluacijom.

## T3: metoda i plan eksperimenata

Povezati inačicu metode i uzorkovanje s odabranim podacima i pitanjem. Dogovoriti redove,
čvorove i težine, parametar kvadrature, početne polove, zrcaljenje, regularizaciju, kriterije
zaustavljanja, referentnu metodu, metrike i raspoložive računalne resurse. Hipoteze i pitanja
zapisati prije pregleda konačnih rezultata. Ne dodavati inačice samo radi popunjavanja usporedne
tablice. Važne izbore i odbačene mogućnosti zabilježiti u ADR-u.

## T4: implementacija u Pythonu

Detalji implementacije namjerno su odgođeni. Na početku rada dodati definiciju okruženja
i zaključane verzije ovisnosti, ponovno upotrebljiv numerički kod i smislene testove, zajedno
s izvršavanjem projektnih provjera i naredbama za CI. Ponašanje usporediti s neovisnim malim
primjerima i, kada je korisno, bibliotečnom implementacijom s usklađenim postavkama.
Objasniti razlike u funkciji cilja, težinama, čvorovima i kriteriju zaustavljanja.

## T5: eksperimenti i interpretacija

Implementirati ponovljiva pokretanja i sačuvati podatke o podrijetlu rezultata. Izvijestiti o
prilagodbi uzorcima, globalnoj pogrešci gdje je mjerljiva, pitanju domene, osjetljivosti na red,
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
