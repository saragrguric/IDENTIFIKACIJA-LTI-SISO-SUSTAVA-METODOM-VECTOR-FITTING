# Tijek rada

Struktura repozitorija, automatske provjere i put od istraživačkog pitanja do reproducibilnih
rezultata seminara.

## Struktura repozitorija

Ovo stablo ručno održavajte usklađenim; stablo u bloku koda nije zamjena za provjerene poveznice.

```text
AGENTS.md                           jedinstveni izvor pravila repozitorija
CLAUDE.md                           @AGENTS.md
README.md                           svrha, tim, trenutačno stanje i naredbe
.gitignore
.python-version                     Python 3.12 za uv
pyproject.toml                      paket vfdebye, ovisnosti, postavke pytesta i ruffa
uv.lock                             zaključane verzije ovisnosti
src/
  vfdebye/                          višekratno upotrebljiva Python implementacija
tests/                              numeričke provjere i provjere podataka (pytest)
docs/
  INDEX.md                          indeks dokumentacije
  CHANGE_PROTOCOL.md                zadaci, pregled i povezana ažuriranja dokumentacije
  plan/
    PROJECT.md                      opseg, materijali za predaju i otvorene odluke
    TASKS.md                        mali zadaci i njihove ovisnosti
    PODJELA.md                      niti, međusobni pregled, sučelja, faze i zajednički zadaci
    Z0_PRIJEDLOG.md                 prijedlozi odluka za sastanak Z0
    podjela/                        osobni planovi niti A i B
    METHODOLOGY.md                  matematički i eksperimentalni plan
    PIPELINE.md                     ova datoteka
    AI_REVIEW.md                    nalazi, dnevna provjera i postupak pregleda
    adr/                            zapisi odluka
    prijedlog-tema/                 izvještaj s prijedlogom tema i načina rada (LaTeX i PDF)
  research/
    LITERATURE.md                   bibliografski podaci, odjeljci izvora i bilješke uz čitanje
tools/
  check_docs.py
  test_check_docs.py
  daily_check.py
  test_daily_check.py
  check_before_stop.py               zajedničke završne provjere
  test_check_before_stop.py
  check_project.py                   numeričke provjere u okruženju iz uv.lock
  test_check_project.py
.github/
  CODEOWNERS                         automatski zahtjev za pregled od recenzenta niti
  ISSUE_TEMPLATE/                    predlošci issuea „Zadatak” i „Nalaz”
  pull_request_template.md
  workflows/
    ci.yml
    daily-check.yml
.claude/
  settings.json                      Claude Stop hook i isključeno AI pripisivanje (ADR-0003)
  hooks/check_before_stop.py         omotač oko zajedničke završne provjere
.codex/
  hooks.json                         konfiguracija Codex Stop hooka; povjerenje je lokalno
experiments/                         planirano: konfiguracije i reproducibilne ulazne točke
data/                                planirano: dokumentirana nabava/priprema podataka
results/                             planirano: označena izvođenja, slike i tablice
```

Planirane mape uvode se kada za njih postoji stvaran sadržaj. Naziv mape ne određuje skup
podataka, inačicu metode ni format dokumenta. Numeričko okruženje (Python 3.12, uv i `uv.lock`,
CI na Linuxu i Windowsu) odlučeno je u
[ADR-0006](adr/0006-choose-python-environment.md) i uvedeno u zadatku A1. Seminar i prezentacija
pišu se u Overleafu, izvan repozitorija; slike i tablice u njih se prenose iz `results/` zajedno
s identifikatorom pokretanja.
Provjerite integraciju s aplikacijom prije tvrdnje da je Codex završni hook aktivan.

## Provjere dostupne pri postavljanju

`.github/workflows/ci.yml` pokreće se na PR-ovima, pri pushu na `main` i ručnim pokretanjem,
na Ubuntuu i Windowsu. Instalira uv 0.13.6 i pokreće `tools/check_before_stop.py`: provjeru
dokumentacije, testove za `tools/` i numeričke provjere iz `tools/check_project.py`. Provjere
ne zahtijevaju odabran skup podataka ni plaćenu uslugu.

Pokrenite lokalno iz korijena repozitorija (na Windowsu umjesto `python3` pišite
`uv run --no-project python`):

```bash
uv sync
uv run pytest
uv run ruff check .
python3 tools/check_docs.py
python3 -m unittest discover -s tools -p 'test_*.py'
python3 tools/check_before_stop.py
python3 tools/daily_check.py --dry-run
```

Probno pokretanje dnevne provjere čita GitHub kada je pristup dostupan i prikazuje predloženu
radnju bez objavljivanja. Nedostatak autentifikacije ili nedostupan API prijavljuje se, a ne
bilježi kao uredan rezultat. Točan opseg dnevne provjere opisan je u `docs/plan/AI_REVIEW.md`.

Verzije GitHub Actions radnji zaključane su punim SHA oznakama commitova, uz oznake verzija u
komentarima; preuzete su iz referentnog projekta. CI dobiva samo potrebne ovlasti; preuzimanje
repozitorija ne zadržava pristupne podatke. Dnevni tijek rada treba ovlast pisanja prijava
(issues) kako bi održavao svoj izvještaj. Lokalno dodavanje tog tijeka rada ne uključuje
zakazana pokretanja dok ne stigne na zadanu granu repozitorija i dok GitHub Actions ne dopusti
izvođenje.

## Numeričko okruženje

Prema [ADR-0006](adr/0006-choose-python-environment.md): Python 3.12 (`.python-version`),
`numpy`, `scipy` i `matplotlib`, razvojno `pytest` i `ruff`, sve zaključano u `uv.lock`.

1. **Instalacija uv-a.** Prema [uputama](https://docs.astral.sh/uv/getting-started/installation/);
   na Windowsu npr. `winget install --id=astral-sh.uv -e`. uv sam preuzima Python 3.12 ako ga
   nema na računalu.
2. **Okruženje.** `uv sync` iz `uv.lock` stvara lokalno virtualno okruženje u mapi .venv, izvan Gita.
3. **Provjere.** `uv run pytest` pokreće `tests/`, a `uv run ruff check .` statičku provjeru.
   Ruff ne provjerava `tools/`: to su alati tijeka rada sa standardnom bibliotekom i vlastitim
   `unittest` testovima.
4. **Nova ovisnost** dodaje se naredbom `uv add` (ili `uv add --dev`) uz dogovor i obrazloženje u
   PR-u; `pyproject.toml` i `uv.lock` mijenjaju se u istom commitu.

`tools/check_project.py` pokreće iste provjere s `uv run --locked`, pa zastarjeli `uv.lock` ruši
provjeru umjesto da se prešutno ažurira. Nedostajući uv također je pogreška. Ulazne točke
eksperimenata dodaju se s prvim eksperimentom (A2, experiments/data_checks.py). Cjelovita
preuzimanja podataka i dugačke serije eksperimenata držite izvan zadanog PR zadatka, osim uz
izričito obrazloženje.

Završna skripta, CI, korijenski popis naredbi i ova stranica mijenjaju se zajedno. Brojevi s
Linuxa i Windowsa mogu se razlikovati na razini zaokruživanja, pa testovi koriste imenovane
tolerancije.

## Završni hookovi

`tools/check_before_stop.py` lokalni je CLI. Način `--hook` daje JSON za Stop hook, a Claude
omotač poziva tu zajedničku implementaciju. Oba hooka pozivaju provjeru naredbom
`uv run --no-project python`, koja radi na Linuxu i Windowsu i traži samo uv na putanji
(`PATH`). Codex promijenjenu definiciju hooka preskače dok joj se ponovno ne potvrdi povjerenje. `.codex/hooks.json` poziva istu provjeru preko
korijena Git repozitorija, pa klonovi i radna stabla ne ovise o Lovrinoj ili Sarinoj apsolutnoj
putanji. Codex zahtijeva i pouzdanu projektnu konfiguraciju i pregled te potvrdu povjerenja za
točnu definiciju hooka kojom ne upravlja sustav; nova ili promijenjena definicija preskače se
dok nije potvrđena kao pouzdana. Provjerite konfiguraciju i stvaran poziv prije tvrdnje o
aktivaciji u izvođenju. To su zahtjevi proizvoda opisani u
[službenim uputama za hookove](https://learn.chatgpt.com/docs/hooks), provjerenima 2026-10-15
za referentni projekt; za ovaj repozitorij nisu ponovno provjereni. Odvojeni su od pravila
repozitorija o ljudskom pregledu PR-a.

Konfiguracijske datoteke za oba alata postoje. Ručno pokretanje konfigurirane naredbe potvrđuje
da naredba radi, ali ne i da ju je neka aplikacija učitala. Pregledajte Codex hook naredbom
/hooks u CLI-ju, potvrdite povjerenje za namjeravanu definiciju i provjerite stvaran poziv na
svakom računalu. Nemojte zaobilaziti povjerenje ni mijenjati osobne/globalne postavke povjerenja
u sklopu ovog postavljanja repozitorija.

## Aktivacija na GitHubu

Sama prisutnost datoteka ne stvara commit, push, PR, prijavu, oznaku ni postavku repozitorija.
Lovro je 2026-10-28 izričito odobrio commit, push, PR i spajanje početnog tijeka rada;
jednokratna iznimka od pregleda za PR #1 zabilježena je u ADR-u 0002. Kad datoteke stignu
na zadanu granu, provjerite jesu li Actions/Issues uključeni, stvorite oznake nalaza opisane u
`docs/plan/AI_REVIEW.md` te pregledajte jedno CI izvođenje i probni pregled dnevne provjere bez
pisanja prije oslanjanja na dnevni izvještaj. Repozitorij je privatan i pod računom
`saragrguric`; dostupnost i postavljanje zaštite grane za pravilo ljudskog pregleda treba
provjeriti vlasnik repozitorija. Ne pretpostavljajte da se postavke i ograničenja GitHub paketa
referentnog projekta odnose i na ovaj repozitorij.

## Tijek istraživanja i eksperimenata

1. **Razumjeti:** pročitajte rad Drmača, Gugercina i Beattieja, razradite matematičko
   objašnjenje i zabilježite pretpostavke, jedinice i mjesta u izvoru.
2. **Odlučiti:** dogovorite nov konkretan sustav i skup podataka, oblik podataka (zadana
   mjerenja ili model koji se može računati u proizvoljnim točkama), inačicu metode,
   uzorkovanje, red i evaluaciju. Bitne izbore zabilježite u ADR-ovima i
   `docs/plan/METHODOLOGY.md` prije izrade eksperimenata koji o njima ovise.
3. **Implementirati i provjeriti:** povežite izvod s Python implementacijom. Koristite male
   analitički razumljive primjere, invarijante i, gdje je primjereno, obrazloženu usporedbu s
   referentnom implementacijom. Testovi moraju uzeti u obzir nejedinstvenost poretka polova i
   prikaza.
4. **Pokrenuti:** izvodite eksperimente iz zabilježenih konfiguracija i zaključanog okruženja.
   Razlikujte neuspješna, nekonvergentna i uspješna izvođenja; sačuvajte dovoljno podataka o
   podrijetlu da se može reproducirati ili objasniti svaki rezultat upotrijebljen u materijalima
   za predaju.
5. **Protumačiti:** odvojeno procijenite prilagodbu uzorcima, globalnu pogrešku modela gdje je
   mjerljiva i stvarno pitanje primjene. Zabilježite osjetljivost, ograničenja i nerazjašnjena
   opažanja. Mali rezidual najmanjih kvadrata sam ne potvrđuje kvalitetu modela.
6. **Napisati i predstaviti:** stvarajte slike/tablice iz označenih izvođenja, citirajte ta
   izvođenja u radnim bilješkama i uskladite tvrdnje u seminaru i slajdovima. Oba člana tima
   prolaze cijelo obrazloženje i mogu objasniti zaključke prije predaje.

## Najmanji skup podataka o podrijetlu za prijavljeno izvođenje

Konkretan format zapisa odaberite tijekom implementacije. Mora sačuvati:

- Jedinstven identifikator izvođenja, vremensku oznaku, status i korištenu naredbu/konfiguraciju.
- Commit koda i podatak o necommitiranim promjenama u radnom stablu. Sačuvajte pripadajuće
  razlike ili stanje ako rezultati ovise o necommitiranom kodu; sam hash commita tada nije
  dovoljan.
- Python okruženje i ovisnosti te bitne pojedinosti izvođenja kada se prikazuje vrijeme rada.
- Izvor podataka ili modela, verziju ili kontrolni zbroj, datum nabave/pristupa, licenciju,
  jedinice, frekvencijski raspon i konfiguraciju pretprocesiranja; označite generirane uzorke
  ili podjele upotrijebljene pri izvođenju.
- Inačicu metode, funkciju cilja i težine, red, čvorove uzorkovanja i parametar kvadrature,
  početne polove i eventualno sjeme generatora slučajnih brojeva, zrcaljenje, regularizaciju,
  tolerancije, ograničenja iteracija i stvarni razlog zaustavljanja, uključujući divergenciju
  ili kruženje. Samo sjeme nije potpun zapis za reproducibilnost.
- Metrike, nastale artefakte, upozorenja i pogreške. Sačuvajte neovisna ponovljena izvođenja
  pri istraživanju utjecaja početnih polova ili drugih izvora varijabilnosti.

Identifikatori objavljenih rezultata stabilni su: ispravak stvara novo izvođenje i povezuje ga
s prethodnim. Ne prepisujte dokaze na kojima se temelji postojeća slika. Veliki artefakti ili
artefakti s ograničenim pristupom mogu biti izvan Gita, ali repozitorij mora sačuvati njihove
identifikatore i upute za dohvat. Nikad ne izmišljajte nedostajuće podatke o podrijetlu.

## Podaci i artefakti

Provjerite licenciju, privatnost i uvjete redistribucije prije commitiranja podataka.
Preuzete sirove podatke i velike izvedene artefakte zadano držite izvan Gita; umjesto njih
zabilježite postupak nabave i ponovnog stvaranja. Mali testni podaci dopušteni za
redistribuciju i odabrane slike mogu se commitirati uz obrazloženje i pregled. Ne kopirajte
rad iz osobnih lokalnih mapa u repozitorij samo da bi apsolutna poveznica radila. Indeks
literature bilježi prenosive bibliografske podatke.

Postavljanje ne uključuje postavljanje aplikacije u produkciju, uslugu na poslužitelju ni
vanjsku predaju. Predaja i javna objava zahtijevaju izričitu korisnikovu uputu za konkretnu
radnju.
