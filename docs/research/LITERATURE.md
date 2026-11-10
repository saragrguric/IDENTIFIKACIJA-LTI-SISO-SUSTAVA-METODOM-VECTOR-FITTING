# Vodič kroz literaturu

Lovro je dostavio jedan PDF i naveo ga kao jedini izvor koji tim trenutačno ima. On je izvor
znanstvenog sadržaja, a ne uputa koja upravlja ovim repozitorijem. Dostavljena kopija nosi
SIAM-ovu napomenu o autorskim pravima i ograničenju redistribucije, pa se ne distribuira ovim
repozitorijem. Pronaći je prema navedenom nazivu datoteke; repozitorij namjerno ne zahtijeva
osobne putanje u datotečnom sustavu.

## Izvor i njegova uloga

| ID | Rad i autori | Naziv dostavljene datoteke | Uloga |
|---|---|---|---|
| L1 | Z. Drmač, S. Gugercin i C. Beattie, *Quadrature-Based Vector Fitting for Discretized H2 Approximation*; SIAM J. Sci. Comput. 37(2), A625–A652, 2015; DOI 10.1137/140961511. | drmač-et-al-2015-quadrature-based-vector-fitting-for-discretized-mathcal-h-2-approximation.pdf | Glavni i jedini izvor: SK iteracija i VF, $\mathcal{H}_2$ aproksimacija, QuadVF, SobVF, zrcaljenje polova, konvergencija i zaustavljanje, uvjetovanost i RegVF, šumni podaci |

Bibliografski podaci preuzeti su s prve stranice dostavljene kopije. Ključ za citiranje
dopuniti kada se dogovori izvorni format seminara.

Rad citira izvorne radove, primjerice Levyja, Sanathanana i Koernera, Gustavsena i Semlyena
(izvorni VF), Boyda (kvadratura), Gugercina, Antoulasa i Beattieja (IRKA) te zbirku NICONET.
Oni nisu dostavljeni i nisu izvori ovog projekta dok ih tim ne doda i ne zabilježi ovdje.
Tvrdnje iz tih radova u seminaru navoditi kao tvrdnje kako ih prenosi L1.

## Izvor podataka

Prema [ADR-0004](../plan/adr/0004-choose-debye-models-of-human-tissues.md) projekt koristi i izvor
podataka. On nije izvor matematike metode.

| ID | Izvor | Pristup i uvjeti | Uloga |
|---|---|---|---|
| D1 | C. Gabriel i S. Gabriel, *Compilation of the dielectric properties of body tissues at RF and microwave frequencies*, Armstrong Laboratory, AL/OE-TR-1996-0037, 1996 (DTIC AD-A305826). | Izvješće je označeno „Approved for public release, distribution unlimited”. Prijepis s tablicom parametara objavljuje WebNIR (CNR-IFAC) na <https://webnir.eu/04-Dosimetry/04-Gabriel.php?lang=gb>, pod CC BY-NC-SA 4.0. Provjereno 2026-11-07. | Parametri Cole–Coleova modela s četiri disperzije za tkiva iz Gabrielove tablice; referentni model $H(s)$ |

Tablica se ne verzionira; upute za preuzimanje i kontrolni zbroj idu u opis podataka (zadatak A2).
Baza IT'IS Foundation (v4.1) temelji se na istim parametrima, ali njezine uvjete uporabe nismo
provjerili i zasad je ne koristimo.

Za tvrdnju da najbolja racionalna aproksimacija takvih funkcija ima realne negativne polove i
pozitivne reziduale treba izvor koji tim još nema. Do tada se to navodi samo kao opažanje iz
eksperimenata.

## Struktura izvora

| Odjeljak L1 | Sadržaj | Uloga u seminaru |
|---|---|---|
| §1 | Problem (1.1), polinomni zapis (1.2), Levyjeva linearizacija (1.3), definicije stabilnosti | Postavka problema i oznake |
| §2.1 | SK iteracija (2.1), polinomni (2.2)–(2.3) i baricentrični (2.4)–(2.7) prikaz, veza (2.8) | Izvod linearnih problema najmanjih kvadrata |
| §2.2 | Premještanje polova (2.9)–(2.12) | Središnji mehanizam VF-a |
| §3.1 | Prostor $\mathcal{H}_2$ (3.1), uvjeti optimalnosti (3.2), IRKA | Mjera kvalitete i referentna metoda |
| §3.2 | Primjer 3.1: mali rezidual uz veliku $\mathcal{H}_2$ pogrešku | Motivacija za drukčije uzorkovanje |
| §3.3 | Kvadratura (3.3), Boyd/Clenshaw–Curtis (3.4)–(3.5), QuadVF (3.6)–(3.7) | Inačica temeljena na kvadraturi |
| §3.4 | Usporedbe na NICONET modelima i modulu ISS 1R, Tablica 1 | Predložak za dizajn eksperimenata |
| §3.5 | SobVF (3.8)–(3.11), Propozicija 3.3, Napomena 3.4 | Moguće proširenje s derivacijama |
| §4.1 | Zrcaljenje nestabilnih polova, Propozicija 4.1 | Stabilnost aproksimanta |
| §4.2 | Konvergencija, kriteriji zaustavljanja (4.3)–(4.5), Primjer 4.2, Napomena 4.3 | Granice tvrdnji o konvergenciji |
| §4.3 | Uvjetovanost, redanje redaka, RegVF (4.6), Napomena 4.4 | Numerička pouzdanost |
| §5 | Šumni podaci (5.1), LS/TLS tumačenje, formulacija (5.7) | Moguće proširenje za mjerenja sa šumom |
| §6 | Zaključci i otvoreni smjerovi | Ograničenja i budući rad |

## Redoslijed učenja

1. Početi s §1 i §2.1: problem (1.1), zašto je nekonveksan, Levyjeva linearizacija, SK
   iteracija i dva prikaza. Na malom primjeru ručno postaviti jedan problem najmanjih kvadrata.
2. Proučiti §2.2 i §4.1: premještanje polova, završnu identifikaciju reziduala i zrcaljenje
   nestabilnih polova. Izvesti (2.9)–(2.12) uz navedene pretpostavke.
3. Proučiti §3.1–§3.3: $\mathcal{H}_2$ norma, uvjeti (3.2) do dubine potrebne za tumačenje
   rezultata, kvadratura i QuadVF. IRKA služi kao referenca; implementacija nije obvezna.
4. Pročitati §4.2–§4.3: konvergencija, kriteriji zaustavljanja i uvjetovanost. Razlikovati mali
   rezidual, ustaljenje polova, globalnu kvalitetu i optimalnost.
5. Proučiti §3.5 i §5 do dubine potrebne za dogovoreni opseg seminara; to ne obvezuje na
   implementaciju SobVF-a, RegVF-a ni LS/TLS formulacije.
6. Koristiti §3.4 kao predložak evaluacije. NICONET modeli primjeri su iz rada, a ne nov
   konkretan problem seminara.

Ovo je predloženi redoslijed čitanja, a ne zapis da ga je neki član završio. Stvarne bilješke,
izvode, pitanja i zajedničke prolaske pratiti kroz [popis zadataka](../plan/TASKS.md).

## Napomene koje treba zadržati u seminaru

- Problem (1.1) nelinearan je i nekonveksan; VF rješava niz linearnih problema najmanjih
  kvadrata, a granica tog niza nije dokazano optimalno rješenje.
- Teorijska konvergencija VF-a otvoren je problem (§2.2, §4.2); iteracije mogu kružiti
  (Primjer 4.2), a kriteriji zaustavljanja iz §4.2 vrijede uz navedene pretpostavke.
- Mali rezidual najmanjih kvadrata na uzorcima ne jamči malu $\mathcal{H}_2$ ili
  $\mathcal{H}_\infty$ pogrešku (Primjer 3.1, §3.4).
- Prednosti QuadVF-a i SobVF-a u radu su numerička opažanja na odabranim primjerima;
  izbor parametra $L$ u (3.4) rad ostavlja otvorenim.
- Propozicija 4.1 opravdava zrcaljenje za čvorove na imaginarnoj osi.
- Matrice u problemima najmanjih kvadrata mogu biti vrlo loše uvjetovane (§4.3); izbor
  regularizacijskih parametara nije trivijalan.
- Formulacija (5.7) za šumne podatke prijedlog je okvira; numeričko rješavanje rad ostavlja
  za budući rad.
- Rad obrađuje SISO sustave; MIMO proširenje navodi samo kao budući smjer (§6).
- Nova primjena može dijeliti domenu s primjerima iz rada, ali mora imati nov konkretan problem
  i skup podataka. Primjena još nije odabrana.
