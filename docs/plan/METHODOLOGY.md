# Matematička i eksperimentalna metodologija

Ovo je okvir potrebne dubine obrade i donošenja odluka, a ne dovršeno teorijsko poglavlje ili
prihvaćena specifikacija implementacije. Jedini izvor je rad L1 (Drmač, Gugercin i Beattie,
2015) iz [vodiča kroz literaturu](../research/LITERATURE.md); oznake jednadžbi i odjeljaka u
nastavku odnose se na taj rad. Primjena je odabrana u
[ADR-0004](adr/0004-choose-debye-models-of-human-tissues.md) i opisana u odjeljku 6; postavke
metode, uzorkovanje i red još nisu odabrani.

## 1. Oznake i model

Promatramo linearni vremenski nepromjenjiv (LTI) sustav s jednim ulazom i jednim izlazom
(SISO) i prijenosnom funkcijom $H(s)$. Jedina pretpostavljena informacija su vrijednosti
$H(\xi_1),\dots,H(\xi_\ell)$ u unaprijed zadanim točkama $\xi_j\in\mathbb{C}$ (L1, §1). Za
mjerenja na frekvencijama $f_j$ u Hz vrijedi $\xi_j=\imath\,2\pi f_j$. U tekstu i kodu
imenovati jedinice ($f$ u Hz ili $\omega$ u rad/s) i svaku pretvorbu.

$\mathcal{R}_r$ označava strogo prave racionalne funkcije reda $r$: nazivnik stupnja $r$,
brojnik stupnja najviše $r-1$ (L1, §1). Proširenje na prave funkcije s direktnim članom
$d_H$ rad navodi u §1; treba ga izričito odabrati ili odbaciti. Ciljni oblik rezultata je
zapis polovima i rezidualima

$$
H_r(s)=\sum_{j=1}^{r}\frac{\phi_j}{s-\lambda_j}.
$$

Objasniti stabilnost (svi polovi u otvorenoj lijevoj poluravnini), graničnu stabilnost i
nestabilnost prema definicijama iz L1, §1. Za realan sustav vrijedi
$H(\overline{s})=\overline{H(s)}$ pa polovi i reziduali dolaze u kompleksno konjugiranim
parovima; to je standardno svojstvo, a L1 ga koristi u §3.3 kada čvorovi zatvoreni na
konjugiranje prepolovljuju broj potrebnih izračuna $H$. Ako kod računa u kompleksnoj
aritmetici, objasniti kako se čuva i provjerava realnost modela. Simbol $\lambda_j$ u L1
označava točke baricentričnog prikaza i, nakon premještanja, polove aproksimanta; u seminaru
tu dvojnost izričito objasniti.

## 2. Funkcija cilja i linearizacija

Referentna formulacija za raspravu jest (L1, (1.1))

$$
\min_{H_r\in\mathcal{R}_r}\ \sum_{j=1}^{\ell}\rho_j\,\lvert H_r(\xi_j)-H(\xi_j)\rvert^2,
\qquad \rho_j>0 .
$$

Ovaj zapis ne određuje konačne težine ni čvorove. Uskladiti ulogu težina: u (1.1) težina
množi kvadrat odstupanja, a u (3.3) i (3.6) dijagonalna matrica $\Delta$ množi rezidual, pa
se u funkciji cilja pojavljuju kvadrati težina. Objasniti zašto skup $\mathcal{R}_r$ nije
konveksan i zašto je problem nelinearan i nekonveksan, s mogućim lokalnim minimumima (L1, §1).

Iz zapisa $H_r=n/d$ i identiteta (1.3) izvesti zašto Levyjevo pojednostavljenje daje linearan
problem najmanjih kvadrata u koeficijentima, ali mijenja težine faktorom $1/\lvert d(\xi_i)\rvert^2$.
Zatim izvesti SK iteraciju (2.1), koja tu težinu aproksimira nazivnikom iz prethodnog koraka.
Izvesti oba prikaza iz L1, §2.1: polinomni (2.2)–(2.3) s matricom Vandermondeova tipa i
baricentrični (2.4)–(2.7) s matricom Cauchyjeva tipa. Pokazati vlastitim izvodom kako redak
matrice $A$ slijedi množenjem jednadžbe $H_r(\xi_i)\approx H(\xi_i)$ nazivnikom $\tilde d(\xi_i)$.
Objasniti da su to dva zapisa iste iteracije u različitim bazama; vezu preko diskretne
Fourierove transformacije (2.8) obraditi samo ako je potrebna.

L1 navodi da se uz konvergenciju nazivnika može očekivati lokalno optimalno rješenje problema
(1.1) (§2.1). To nije dokaz: u seminaru tu tvrdnju navesti kao očekivanje, a ne kao teorem.

## 3. Vector fitting: premještanje polova i reziduali

Izvesti korake (2.9)–(2.12): VF za nove točke $\lambda^{(k+1)}$ uzima nultočke nazivnika
$\tilde d^{(k)}$, čime se SK težina apsorbira u novu bazu i svaki korak postaje netežinski
problem najmanjih kvadrata (2.12) (L1, §2.2). Objasniti računanje nultočaka kao spektra
perturbacije ranga jedan dijagonalne matrice (L1, §4.2, opažanje (i)) i završnu identifikaciju
reziduala problemom najmanjih kvadrata sa zadržanim polovima (L1, §4.2, nakon opažanja (iii)).
Uz zapis (2.5) i $\Lambda=\operatorname{diag}(\lambda)$ vrijedi
$\tilde d(s)=1+e^T(sI-\Lambda)^{-1}\varphi$, pa lema o determinanti daje
$\det(sI-\Lambda+\varphi e^T)=\det(sI-\Lambda)\,\tilde d(s)$. Nultočke od $\tilde d$ koje
nisu ujedno točke $\lambda_j$ zato su svojstvene vrijednosti matrice $\Lambda-\varphi e^T$
(numerički provjereno u `tests/test_vf.py`). Opažanje (i) piše $\operatorname{diag}(\lambda)+\tilde\varphi e^T$; razliku
predznaka treba razjasniti u A5. Ocjena (4.4) ne ovisi o predznaku.

Objasniti osjetljivost na početne polove (L1, §2.2). U primjerima L1 početni polovi leže na
logaritamskoj mreži preko područja koje približno sadrži spektar (Primjer 3.1); to traži
informaciju o modelu, pa u postavci samo s mjerenjima početni izbor treba posebno odabrati i
obrazložiti.

Zrcaljenje nestabilnih polova (L1, §4.1): polovi iz desne poluravnine reflektiraju se preko
imaginarne osi. Nakon zrcaljenja korak formalno ostaje u težinskom SK obliku; Propozicija 4.1
pokazuje da je za čvorove na imaginarnoj osi pripadna dijagonalna težina unitarna pa se
rješenje ne mijenja. Navesti tu pretpostavku o čvorovima i provjeriti stabilnost konačnog modela.

Konvergencija i zaustavljanje (L1, §2.2 i §4.2): teorijska konvergencija VF-a otvoren je
problem; rad navodi primjer s odbojnim fiksnim točkama, a Primjer 4.2 pokazuje kruženje polova s
periodom 2 i slučaj ustaljenih polova uz reziduale nazivnika koji ne teže nuli. Obraditi mjeru
udaljenosti skupova polova do na permutaciju (4.3), ocjene (4.4)–(4.5) i kriterij povratne
pogreške iz opažanja (iii), uz pretpostavke pod kojima vrijede. Napomena 4.3 opisuje potrebu
za kontrolom petlje s memorijom radi prepoznavanja periodičnosti.

Razdvojiti četiri tvrdnje: (a) mali rezidual najmanjih kvadrata na uzorcima, (b) ustaljenje
polova, (c) dobra aproksimacija u $\mathcal{H}_2$ ili $\mathcal{H}_\infty$ normi i (d) globalna
optimalnost. Nijedna ne slijedi automatski iz prethodne. Uključiti barem jednu malu razrađenu
iteraciju ili neovisno provjerljiv numerički primjer, primjerice racionalnu funkciju reda 1 ili 2.

## 4. $\mathcal{H}_2$ pogreška i uzorkovanje kvadraturom

Izvod ovog odjeljka, s našim odmakom na pojas i prijedlogom kvadrature za Z2, nalazi se u
[izvodu B2](../izvodi/b2-h2-kvadratura.md).

Definirati prostor $\mathcal{H}_2(\mathbb{C}_+)$, skalarni produkt i normu (3.1) te
$\mathcal{H}_\infty$ normu (L1, §3.4.1). Objasniti nužne uvjete $\mathcal{H}_2$ optimalnosti
(3.2), Hermiteovu interpolaciju u zrcalnim slikama polova, i ulogu metode IRKA kao reference
(L1, §3.1). IRKA računa $H$ i $H'$ u točkama koje nisu poznate unaprijed, dok VF koristi
unaprijed zadane uzorke. Primjer 3.1 pokazuje mali rezidual najmanjih kvadrata uz veliku
relativnu $\mathcal{H}_2$ pogrešku.

Diskretizacija (3.3): uz $\rho_\pm=0$, jedinične težine i ekvidistantne konjugirane čvorove,
funkcija cilja VF-a odgovara složenoj trapeznoj formuli. Boyd/Clenshaw–Curtisova formula
(3.4)–(3.5) supstitucijom $\omega=L\cot t$ daje

$$
\int_{-\infty}^{\infty}\lvert H(\imath\omega)\rvert^2\,d\omega
\approx\sum_{j=1}^{\ell}\frac{L\pi}{(\ell+1)\sin^2 t_j}\,\lvert H(\imath L\cot t_j)\rvert^2
+\frac{\pi}{2L(\ell+1)}\Bigl(\lvert M_+[H]\rvert^2+\lvert M_-[H]\rvert^2\Bigr),
\qquad t_j=\frac{j\pi}{\ell+1}.
$$

QuadVF (3.6)–(3.7) koristi te čvorove i fiksne težine te dodatni redak s $M_+[H]$ dvostruke
težine; za $H(s)=C(sI-F)^{-1}B$ vrijedi $M_+[H]=M_-[H]=CB$. Navesti što to traži od podataka:
vrijednosti $H$ u čvorovima kvadrature i vrijednost ili procjenu $M_+[H]$. Uz fiksne izmjerene
frekvencije QuadVF nije izravno primjenjiv; svaku interpolaciju ili procjenu treba obrazložiti.
Izbor parametra $L>0$ rad ne rješava (§3.3) i ilustrira osjetljivost na primjeru. Konstanta
$1/(2\pi)$ iz (3.1) u (3.4) nije zapisana; za relativne pogreške ne utječe na rezultat, ali u
kodu i tekstu normalizacija mora biti dosljedna. Približavanje rješenja diskretnog problema
rješenju metode IRKA s rastom $\ell$ (Tablica 1, §3.4.3) numeričko je opažanje na jednom
primjeru, a ne teorem.

## 5. Proširenja i numerička pitanja

- **SobVF** (L1, §3.5, (3.8)–(3.11), Propozicija 3.3): uključuje derivacije $H'(\xi_j)$ i
  diskretnu Sobolevljevu normu; korak (3.9) izostavlja korekcijski član. Napomena 3.4 opisuje
  kada su derivacije jeftine; u postavci samo s mjerenjima često nisu dostupne.
- **Uvjetovanost** (L1, §4.3): matrice Vandermondeova i Cauchyjeva tipa mogu biti vrlo loše
  uvjetovane, pa normalne jednadžbe općenito nisu prikladne. Skaliranje redaka može poništiti
  težine kvadrature ili težine šuma; rad predlaže redanje redaka prema normi prije rješavanja
  problema najmanjih kvadrata. Prijavljivati brojeve uvjetovanosti koji se stvarno računaju.
- **RegVF** (L1, (4.6)): regularizacija parametrima $\eta_1,\eta_2$; rad navodi da njihov izbor
  nije trivijalan, a prikazani brojevi odnose se na jedan primjer.
- **Šumni podaci** (L1, §5): težinska formulacija (5.1) uz nekorelirane pogreške, tumačenje VF-a
  kao približnog miješanog LS/TLS postupka (§5.2) i predložena formulacija (5.7) bez dovršene
  numeričke metode (§5.3).
- **Ortonormirane baze** (Napomena 4.4): rad ih navodi kao otvorenu raspravu.

Svako proširenje uvodi se samo ako ga opravdava pitanje; ovaj plan ne zahtijeva nijedno.

## 6. Od stvarnog problema do podataka

Prije odabira podataka zapisati pitanje i što bi koristan model trebao omogućiti. Zabilježiti
izvor, licencu i pristup, verziju ili kontrolni zbroj, način nastanka frekvencijskog odziva
(mjerenje, simulacija ili analitički model), jedinice i frekvencijski raspon, broj i raspored
uzoraka, šum, dostupnost derivacija, mogućnost računanja $H$ u proizvoljnim točkama, postojanje
referentnog modela za točnu globalnu pogrešku te očekivani red i stabilnost stvarnog sustava.
Ne uklanjati, ne interpolirati i ne preuzorkovati mjerenja prešutno i ne mijenjati raspon
frekvencija samo da bi metoda radila.

Modeli korišteni u L1 (toplinski model, FOM, zgrada i greda iz zbirke NICONET te modul
ISS 1R) mogu služiti za razumijevanje i provjeru implementacije. Nov konkretan problem mora se od njih
razlikovati; objasniti po čemu.

### 6.1 Odabrana primjena: Debyejevi modeli tkiva

Prema [ADR-0004](adr/0004-choose-debye-models-of-human-tissues.md) prijenosna funkcija je
relativna permitivnost tkiva u Gabrielovu modelu s četiri Cole–Coleove disperzije,

$$
\varepsilon(s)=\varepsilon_\infty+\sum_{n=1}^{4}\frac{\Delta\varepsilon_n}{1+(s\tau_n)^{1-\alpha_n}}
+\frac{\sigma_i}{s\,\varepsilon_0},\qquad s=\imath\,2\pi f .
$$

Članovi $\varepsilon_\infty$ i $\sigma_i/(s\varepsilon_0)$ poznati su točno i ne aproksimiraju se.
Aproksimira se strogo pravi dio $H(s)=\varepsilon(s)-\varepsilon_\infty-\sigma_i/(s\varepsilon_0)$
oblikom $H_r$ iz odjeljka 1. Debyejev član $\Delta\varepsilon/(1+s\tau)$ ima jedan realan pol
$-1/\tau$, pa je zbroj Debyejevih članova upravo $H_r$ s realnim polovima. Za $\alpha_n>0$
Cole–Coleov član nije racionalan, pa točan konačan red ne postoji i pitanje glasi koliko je
polova potrebno za zadanu točnost.

Treba izvesti i obrazložiti:

- **Realnost.** $H(\overline{s})=\overline{H(s)}$ uz glavnu granu potencije. Model je realan ako su
  polovi realni s realnim rezidualima ili dolaze u konjugiranim parovima.
- **Konačnost $\mathcal{H}_2$ norme.** Za $0\le\alpha_n\le0{,}3$, što vrijedi za sva tkiva u
  tablici osim zraka i vakuuma, Cole–Coleov član pada barem kao $\omega^{-0{,}7}$, pa je
  $\int\lvert H(\imath\omega)\rvert^2d\omega$ konačan. Na cijeloj osi tu normu određuju
  niskofrekvencijske disperzije s velikim $\Delta\varepsilon_n$, pa se pogreška mjeri na pojasu
  $[\omega_1,\omega_2]$. To je odmak od L1.
- **QuadVF na pojasu.** Formula (3.4)–(3.5) integrira po cijeloj osi i koristi redak s
  $M_+[H]=\lim_{s\to\infty}sH(s)$. Za $\alpha_n>0$ ta granica nije konačna, pa se redak izostavlja,
  a kvadratura prilagođava pojasu. Oba odmaka treba izvesti i opravdati.
- **Mjere.** Najveća relativna pogreška $\max_k\lvert\varepsilon_r(\imath\omega_k)-\varepsilon(\imath\omega_k)\rvert/\lvert\varepsilon(\imath\omega_k)\rvert$
  na gustoj kontrolnoj mreži, koja nije skup čvorova prilagodbe, i relativna $\mathcal{H}_2$
  pogreška na pojasu. Mjera na logaritamskoj mreži pogoduje logaritamskim čvorovima i relativnim
  težinama, pa se poredak metoda prijavljuje u obje mjere.
- **Razine točnosti.** $\delta\in\{5\,\%,\ 1\,\%,\ 0{,}1\,\%\}$; najmanji $r$ traži se zasebno
  za svaku mjeru (ADR-0004, dodatak 2026-11-09). Nazivnici mjera su različiti, pa ista $\delta$
  u njima nema isto značenje. Pojas je privremeno 10 MHz–10 GHz, a konačno se bira u Z2.
- **Referentna metoda.** Polovi $-1/\tau_j$ fiksni su i logaritamski raspoređeni po pojasu, a
  reziduali se dobivaju linearnim problemom najmanjih kvadrata. Tako se izolira učinak
  premještanja polova.
- **Realnost polova i pozitivnost reziduala** prijavljuju se kao provjereno svojstvo svakog
  rezultata. L1 ih ne jamči; tvrdnja da ih ima najbolja aproksimacija traži izvor koji tim još
  nije dodao.

Član s $\Delta\varepsilon_n=0$ ne pridonosi modelu, pa za njega $\tau_n$ i $\alpha_n$ nisu
ograničeni; svaki prisutni član traži $\tau_n>0$ i $0\le\alpha_n<1$ (`vfdebye.gabriel`).
Testovi s točnim konačnim redom koriste umjetne modele s tabličnim $\Delta\varepsilon_n$ i
$\tau_n$ uz sve $\alpha_n=0$, jer nijedno tkivo u tablici nema sve $\alpha_n=0$.

## 7. Provjera implementacije

Na početku implementacije odabrati podržano Python okruženje i zaključane verzije ovisnosti.
Numeričku metodu omogućiti pozivati neovisno o bilježnici ili stvarnom skupu podataka.
Obuhvatiti provjeru ulaza, realnost i konačnost izlaza, stabilnost ili izričitu prijavu
nestabilnih polova, oporavak poznatog racionalnog modela reda najviše $r$ iz egzaktnih uzoraka
uz navedene pretpostavke, ponašanje kriterija zaustavljanja uključujući nekonvergenciju i
kruženje, zrcaljenje te rubne slučajeve kao što su čvor jednak polu ili bliski polovi.
Kvadraturu provjeriti na funkciji poznate norme; primjerice za $H(s)=1/(s+a)$, $a>0$, vrijedi
$\int_{-\infty}^{\infty}\lvert H(\imath\omega)\rvert^2\,d\omega=\pi/a$ (vlastiti izračun).

Udaljenost (4.3) skupova polova je problem uparivanja s najmanjim najvećim odstupanjem
(engl. *bottleneck assignment*), a ne s najmanjim zbrojem; računa ga
`vfdebye.vf.matching_distance`, a test ga uspoređuje s definicijom preko svih permutacija za
$r\le6$. Udaljenost (4.3) je apsolutna i simetrična. Slika 2 i Primjer 4.2 u L1 prate relativnu
promjenu $\lVert(\lambda^{(k)}-\lambda^{(k+1)})./\lambda^{(k)}\rVert_\infty$, normiranu
ranijim skupom. Relativna udaljenost nije simetrična: za $a=\{-1,-100\}$ i $b=\{-2,-100\}$
iznosi 1 normirana s $a$, a 0,5 normirana s $b$. L1 cik-cak oblik te krivulje na desnoj
slici pripisuje upravo računanju relativnih udaljenosti. `vfdebye.vf.detect_period` zato,
kao L1, normira skupom starijim za $\tau$ koraka. L1 za sliku 2 ne navodi uparivanje: zapis
$./$ je po elementima, a opažanje (ii) u §4.2 za relativne razlike u (4.5) traži uparivanje
odgovarajućom permutacijom. Naše je tumačenje da se polovi uparuju permutacijom koja daje
najmanji najveći relativni pomak, kako to radi `matching_distance` s `relative=True`. Polovi su određeni samo do poretka, a koeficijenti baricentričnog prikaza ovise o odabranim
točkama. Zato uspoređivati vrijednosti $H_r$ na kontrolnoj mreži ili skupove polova
uparivanjem, kao u (4.3), a ne vektore koeficijenata. Koristiti opravdane tolerancije i
neovisne izračune; uvjetovanost određuje dostižnu točnost. Kada se biblioteka koristi kao
referenca, uskladiti funkciju cilja, težine, čvorove, početne polove i kriterij zaustavljanja.
Testovi i CI koriste male sintetičke podatke ili testne podatke koje je dopušteno dalje
distribuirati te ne traže preuzimanje cijelog skupa podataka ni plaćenu uslugu.

## 8. Eksperimenti i evaluacija

Prije glavnih pokretanja dogovoriti pitanja, redove, broj i raspored čvorova (linearan,
logaritamski ili kvadraturni), parametar kvadrature, početne polove, zrcaljenje, regularizaciju,
kriterije zaustavljanja i najveći broj iteracija, referentnu metodu, metrike i način njihova
računanja te raspoložive računalne resurse. Usporedbe iz L1, §3.4 predložak su, a ne propis.
Evaluaciju u domeni odabrati nakon što je poznata primjena.

Za svako prikazano pokretanje navesti:

- Izvor i verziju ulaza ili kontrolni zbroj, frekvencijski raspon, čvorove i težine te
  predobradu.
- Reviziju koda i postojanje nezabilježenih izmjena; ako commit još ne postoji, navesti tu
  činjenicu i identificirati radnu snimku umjesto izmišljanja revizije.
- Python okruženje i ovisnosti, inačicu metode, red i sve numeričke postavke, uključujući
  rješavač najmanjih kvadrata i regularizaciju.
- Početne polove i sjeme generatora ako se koristi, razlog zaustavljanja, broj iteracija,
  povijest promjene polova, zrcaljenja i konačni rezidual najmanjih kvadrata.
- Relativnu $\mathcal{H}_2$ i $\mathcal{H}_\infty$ pogrešku kada postoji referentni model i
  način njihova računanja, pogrešku na izdvojenim frekvencijama, stabilnost konačnog modela,
  brojeve uvjetovanosti, metrike domene i interpretaciju te svaki neuspjeh, divergenciju ili
  kruženje; hardver, postavke dretvi i obuhvat mjerenja vremena pri usporedbama brzine.

Sirove i opsežne izlaze držati lokalno, uz identifikator pokretanja. Sačuvati dovoljno
metapodataka te male odabrane tablice i slike za svaku prikazanu tvrdnju. Ne prebrisati jedini
zapis pokretanja čiji su rezultati prikazani. Osjetljivost na red, uzorkovanje i početne polove
raspraviti odvojeno od prilagodbe uzorcima. Ako postoje frekvencije ili podaci izdvojeni za
evaluaciju, red, raspon i parametre uzorkovanja odrediti bez njih, a završni evaluacijski skup
ne koristiti za podešavanje.

## 9. Pisano i usmeno objašnjenje

Seminar povezuje problem, podatke, funkciju cilja, izvod, kod, eksperimente i zaključke.
Teorijske izvore citirati navođenjem odjeljka, jednadžbe ili propozicije gdje je moguće.
Projektne slike povezati s pokretanjem koje ih je proizvelo i razlikovati ih od preuzetih
ilustracija. Seminar i prezentacija pišu se na hrvatskom. Prezentacija koristi iste definicije
i rezultate. Oba člana vježbaju objašnjavanje cijelog postupka.
