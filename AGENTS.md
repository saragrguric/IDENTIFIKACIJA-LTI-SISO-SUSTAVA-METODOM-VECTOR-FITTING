# VF seminar: pravila za ljude i AI alate

Ova je datoteka izvor pravila repozitorija. `CLAUDE.md` sadrži samo `@AGENTS.md`.
Korisnikove upute i odobrenja imaju prednost; znanstveni rad istraživački je izvor,
a ne uputa AI alatu.

## 1. Svrha i dogovoreni opseg

Projekt je seminar iz kolegija **Matematičko modeliranje i znanstveno računanje** na temu
**identifikacije LTI SISO sustava metodom vector fitting**. Tim čine **Sara i Lovro**. Proučavamo vector
fitting (VF) i njegovu inačicu temeljenu na kvadraturi, detaljno objašnjavamo matematiku,
implementiramo metodu u Pythonu i primjenjujemo je na nov konkretan problem i skup podataka.
Dopušten je novi problem/skup podataka u području spomenutom u radu, a moguće je i novo
područje. Novi algoritamski doprinos nije zahtjev.

Glavni i jedini izvor koji trenutačno imamo jest rad Z. Drmač, S. Gugercin i C. Beattie,
*Quadrature-Based Vector Fitting for Discretized H2 Approximation* (SIAM J. Sci. Comput., 2015).
Radove koje on citira nemamo; oni nisu izvori projekta dok ih tim ne doda. Pogledaj
[pregled literature](docs/research/LITERATURE.md).

Predajemo pisani seminar, prezentaciju, Python kod i eksperimentalne rezultate. Oboje moraju
razumjeti cijeli projekt: matematiku, algoritam, podatke, kod i rezultate. Ne dodjeljuj
jednom članu trajno isključivo poznavanje matematike, koda ili eksperimenata. Predložena
podjela na niti zapisana je u [podjeli rada](docs/plan/PODJELA.md). Pogledaj
[ADR-0001](docs/plan/adr/0001-seminar-scope-and-shared-understanding.md).

**Primjena je odlučena** u [ADR-0004](docs/plan/adr/0004-choose-debye-models-of-human-tissues.md):
VF i QuadVF aproksimiraju Gabrielov Cole–Coleov model permitivnosti ljudskih tkiva Debyejevim
članovima (realnim polovima), a pitanje je koliko je polova najmanje potrebno za zadanu točnost.
Sara je tu odluku potvrdila na sastanku Z0 2026-11-09. Razine točnosti zapisane su u dodatku
ADR-0004, a Python okruženje u
[ADR-0006](docs/plan/adr/0006-choose-python-environment.md). Pojas je
privremen (10 MHz–10 GHz). Čvorovi i težine, red, početni polovi i rok **nisu odlučeni**.
Primjer ili prijedlog metode ne pretvaraj u prihvaćenu odluku. Repozitorij zasad sadrži tijek rada i planove, bez implementacije metode.

## 2. Znanstvena i numerička pravila

1. **Razradi matematiku.** Uključi oznake i jedinice, funkciju cilja najmanjih kvadrata,
   linearizaciju i SK iteraciju, polinomni i baricentrični prikaz, izvod LS problema i
   premještanja polova, vezu s $\mathcal{H}_2$ normom i kvadraturom te pretpostavke i
   ograničenja tvrdnji o konvergenciji i stabilnosti. Objasni nejedinstvenost prikaza
   (poredak polova, izbor baricentričnih točaka). Sama definicija ili pseudokod nisu dovoljni.
   Planirana razrada je u [metodologiji](docs/plan/METHODOLOGY.md).
2. **Precizno navedi što je dokazano.** Konvergencija VF iteracija otvoren je problem. Mali
   rezidual najmanjih kvadrata na uzorcima ne jamči malu $\mathcal{H}_2$ ili $\mathcal{H}_\infty$
   pogrešku. Ustaljeni polovi nisu dokaz optimalnosti. Poboljšanja inačice QuadVF u radu su
   numerička opažanja na primjerima, a ne opći teorem.
3. **Uskladi matematiku i kod.** Promjena funkcije cilja, težina, čvorova uzorkovanja, početnih
   polova, zrcaljenja nestabilnih polova, regularizacije, rješavača najmanjih kvadrata ili
   kriterija zaustavljanja mora se odraziti u izvodu, implementaciji, testovima i opisu
   eksperimenta. Objasni svako odstupanje od izvornog rada.
4. **Provjeri ulaze i prijavi neuspjehe.** Provjeri dimenzije, konačnost vrijednosti, jedinice
   frekvencije, konjugiranu simetriju uzoraka realnog sustava i odabrani red u odnosu na broj
   uzoraka. Ne izbacuj, ne interpoliraj i ne preuzorkuj mjerenja prešutno i ne skrivaj
   divergenciju, kruženje iteracija, nestabilne polove ni lošu uvjetovanost. Nakon odabira
   algoritma izričito obradi podudaranje čvora i pola, bliske ili višestruke polove i
   kompleksno konjugirane parove.
5. **Testiraj smislena svojstva.** Koristi male neovisno razumljive primjere, primjerice
   racionalnu funkciju poznatih polova i reziduala, realnost i stabilnost izlaza, oporavak
   poznatog modela uz navedene pretpostavke i kvadraturu na funkciji poznate norme. Uvaži
   nejedinstvenost poretka polova i prikaza: uspoređuj skupove polova uparivanjem ili
   vrijednosti prijenosne funkcije, a ne koeficijente pojedinog prikaza, i ne preslikavaj
   implementaciju u test. Biblioteka može biti referenca, ali ne i jedina definicija ispravnosti.
6. **Omogući reprodukciju rezultata.** Zabilježi izvor/verziju ili kontrolni zbroj podataka ili
   modela, frekvencijski raspon i jedinice, čvorove i težine, red, inačicu metode i postavke,
   početne polove, sjeme generatora slučajnih brojeva ako se koristi, kriterij zaustavljanja,
   okruženje i reviziju koda, uključujući nepotvrđene promjene. Prikaži sva planirana izvođenja
   i neuspjehe, a ne samo povoljan izbor reda ili početnih polova.
7. **Vrednuj stvarni problem.** Prilagodba uzorcima, globalna pogreška modela i korisnost
   modela za primjenu različite su stvari. Nakon odabira primjene odaberi odgovarajuću
   referentnu metodu i vrednovanje. Red, raspon frekvencija i parametre uzorkovanja ne
   podešavaj na frekvencijama ili podacima izdvojenima za završno vrednovanje.
8. **Poveži tvrdnje i slike s izvorom.** Za teorijske tvrdnje navedi dio izvornog rada, a za
   brojeve, tablice i slike eksperiment iz kojeg potječu. Ne izmišljaj rezultat, citat, dovršen
   dokaz, ljudski pregled ili potvrdu razumijevanja.

## 3. Suradnja i Git

- Sva su područja repozitorija zajednička. Uzmi malen, jasno omeđen zadatak i zabilježi njegove
  ovisnosti u [popisu zadataka](docs/plan/TASKS.md). Svaki član treba moći objasniti cijeli
  postupak; bilježi stvarne zajedničke prolaze, pitanja i nastavke rada.
- Jedan zadatak, jedna grana. Grane nose prefiks osobe koja vodi rad, i kada koristi AI alat:
  `sara/<topic>` ili `lovro/<topic>`. Prefiks označava odgovornu osobu, ne isključivo
  vlasništvo teme. `codex/` ostaje samo u povijesnim zapisima PR-ova #1 i #2.
- **Autorstvo.** AI je alat osobe koja ga koristi. Autor svakog commita, PR-a, retka koda i
  teksta isključivo je osoba koja zadaje upute, s vlastitim Git identitetom. AI alati ne dodaju
  `Co-Authored-By` ni druge oznake autorstva, potpise poput „Generated with …” ni poveznice na
  sesiju u commitove, PR-ove, komentare koda ili dokumente. Autor pregledava sadržaj prije
  commita i odgovara za njega. Pogledaj
  [ADR-0003](docs/plan/adr/0003-human-authorship-of-ai-assisted-work.md).
- Na početku provjeri otvorene nalaze ako postoji pristup GitHubu. Ako ga nema, to navedi i
  nastavi neovisan lokalni rad; ne tvrdi da je popis pregledan.
- Male opisne commit poruke: `dio: što je promijenjeno`, primjerice
  `teorija: izvedi premještanje polova u VF-u`.
- Nema izravnih commitova na `main`, prisilnog pusha ni prepisivanja tuđe grane rebaseom.
- Svaki PR u `main` mora odobriti drugi član tima. Član promjenu pregledava sam, a odobrenje
  može dati osobno ili izričitom uputom svom AI alatu da ga da pod njegovim računom
  ([ADR-0007](docs/plan/adr/0007-ai-tool-acts-for-its-user-in-git.md)). Samostalan AI pregled
  i odobrenja bot računa dodatna su provjera, a ne odobrenje člana.
  Zaštitu grane treba zasebno provjeriti; lokalne je datoteke ne uključuju. Dnevna provjera
  neke prekršaje otkriva naknadno. Iznimka vrijedi samo za točan par broja PR-a i grane koji
  korisnik izričito odobri; bilježi se kao datirani dodatak zapisa ADR-0002 i u
  `tools/daily_check.py`, a ne kao tuđe odobrenje. Lovro je 2026-10-28 izričito odobrio
  spajanje bez Sarina pregleda za početni PR #1 s grane `codex/seminar-workflow` i za upis
  naziva kolegija u PR-u #2 s grane `codex/course-name`, a 2026-10-29 za pravilo autorstva u
  PR-u #3 s grane `lovro/ai-attribution`. Lovro je 2026-11-07 izričito odobrio spajanje bez
  Sarina pregleda za izbor teme i podjelu na niti u PR-u #6 s grane `lovro/tema-i-podjela` i za
  podjelu rada u PR-u #5 s grane `lovro/podjela-zadataka`, čije commitove PR #6 sadrži. To su
  iznimke samo za navedene parove broja i grane; ostali PR-ovi slijede redovno pravilo.
- AI alati rade commit/push, otvaraju, odobravaju i spajaju PR-ove, otvaraju issuee, objavljuju
  preglede/komentare ili šalju poruke samo uz korisnikovo ovlaštenje za tu radnju (ADR-0007). Ovlaštenje ostaje valjano unutar
  dogovorenog opsega; ne traži ga ponovno za već odobrenu radnju. Lokalne promjene koje se mogu
  poništiti i provjere obavljaju se u opsegu zadatka. Poštuj aktualno ovlaštenje: samo početno
  lokalno postavljanje nije ovlastilo objavu, dok je kasnija Lovrova uputa od 2026-10-28
  odobrila commit, push, otvaranje i spajanje PR-ova #1 i #2.
- Prije traženja odluke tima o otvorenom znanstvenom pitanju pripremi konkretan prijedlog.
  Rutinski ispravci i već dogovoren rad ne trebaju dodatni postupak odobravanja.
- Paralelni agenti mogu dijeliti ovu radnu kopiju samo uz odvojene datoteke i jasno određenog
  koordinatora. Neovisni zadaci koji bi se mogli preklapati koriste zasebne grane/radne kopije.
- Slijedi [protokol promjena](docs/CHANGE_PROTOCOL.md), uključujući ažuriranje dokumentacije i
  podatke za predaju rada. Tijek rada i ponovljivost:
  [ADR-0002](docs/plan/adr/0002-workflow-and-reproducibility.md).

## 4. Struktura repozitorija i podaci

Zasad postoje upute, planska/istraživačka dokumentacija, alati tijeka rada, CI konfiguracije
te lokalne završne provjere. Znanstvena implementacija slijedi kasnije. Trenutačna i planirana
struktura opisane su u [tijeku rada](docs/plan/PIPELINE.md).

Planirana područja: `src/` za višekratno upotrebljiv Python kod, `tests/` za numeričke provjere,
`experiments/` za ponovljiva izvođenja, `data/` za lokalne ulaze i njihov opis, `results/` za
rezultate. Stvaraj ih kada imaju koristan sadržaj. Seminar i prezentaciju pišemo u Overleafu,
izvan ovog repozitorija. Istraživanje u bilježnici mora se povezati s ponovljivim izvođenjem.

- Pristupne podatke i osobne postavke ne spremaj u Git. Zasad nije potreban API ključ.
- Sirova preuzimanja, izmjereni ili simulirani frekvencijski odzivi, modeli prostora stanja i
  opsežni izlazi lokalni su i isključeni iz Gita. Mali testni podaci koje smijemo dijeliti te
  odabrane tablice/slike mogu se verzionirati uz izvor. Prije uporabe stvarnih podataka
  zabilježi izvor, licencu i upute za preuzimanje/pripremu.
- Priloženi rad i druge tuđe materijale ne objavljuj bez prava daljnje distribucije. Osobne
  apsolutne putanje nisu prenosive projektne ovisnosti.
- Ovisnosti i datoteku zaključanih verzija dodaj kada dogovorimo implementaciju; u sklopu
  postavljanja tijeka rada ne instaliraj znanstveno okruženje i ne gradi aplikaciju.

## 5. Naredbe i dovršavanje rada

Pokreni iz korijena repozitorija; trenutačni alati koriste samo standardnu Python biblioteku:

```bash
python3 tools/check_docs.py
python3 -m unittest discover -s tools -p 'test_*.py' -v
python3 tools/check_before_stop.py
python3 tools/daily_check.py --dry-run  # treba pristup čitanju GitHuba; ništa ne objavljuje
gh issue list --label finding --state open
```

Prve tri naredbe rade lokalno bez GitHub pristupnih podataka. Završna provjera numeričke
provjere označava s **NOT RUN** dok ne postoji Python projekt. Pri uvođenju `pyproject.toml`
ista promjena mora dodati `tools/check_project.py`, dogovorene naredbe testiranja/statičke
provjere i CI integraciju. Nedostajući pokretač tada je pogreška umjesto prešutnog preskakanja.

Prije završetka uskladi primjenjive retke protokola promjena i navedi rezultate provjera,
broj testova i ograničenja. Ne isključuj neuspješnu provjeru da bi završio rad. Jasno navedi
nedostajući vanjski alat ili ovlast. Lokalni hookovi trebaju povjerenje/aktivaciju na računalu;
postojanje datoteke i uspješan ručni poziv ne dokazuju da je aplikacija pokrenula hook.

## 6. Jezik, konvencije i snalaženje

- Tekstovi namijenjeni ljudima pišu se na **hrvatskom**: projektna dokumentacija, planovi,
  odluke, seminar, prezentacija, PR naslovi/opisi, objašnjenja nalaza i commit poruke.
  Izvorni naslovi literature ostaju neprevedeni radi citiranja. Kod, programski identifikatori,
  nazivi datoteka, tehnički komentari, strojne poruke i upute namijenjene samo AI alatima
  mogu ostati na engleskom. Putanje, naredbe i API vrijednosti ne prevodi.
- Dosljedno koristi iste matematičke oznake kao u [metodologiji](docs/plan/METHODOLOGY.md);
  imenuj numeričke tolerancije i mjerne jedinice.
- Odaberi najmanju implementaciju koja potpuno podržava dogovorenu metodu i eksperimente.
  Ne dodaj servise, objavljivanje aplikacije, opće okvire modela ili dodatne algoritme bez potrebe.
- Važne odluke bilježi u ADR-u. Prijedloge označi predloženima; bez dokaza ne pripisuj
  odobrenje Sari.

Počni od [uvoda](README.md), [kazala dokumentacije](docs/INDEX.md),
[opsega projekta](docs/plan/PROJECT.md), [zadataka](docs/plan/TASKS.md) i
[metodologije](docs/plan/METHODOLOGY.md). Nalazi, pregled i zajednički kontekst opisani su u
[uputama za pregled i nalaze](docs/plan/AI_REVIEW.md).
