# A3: od permitivnosti do linearnih problema SK iteracije

**Stanje 2026-11-23:** pripremljen izvod za pregled u B9. Sarin neovisni prolaz i zajedničko
objašnjenje još nisu provedeni. Ove bilješke ne odabiru postavke metode za Z2 i ne uvode
implementaciju VF iteracije.

**Izvori:** L1, §1 i §2.1, (1.1)–(1.3) i (2.1)–(2.7), str. A626–A629, za racionalnu
aproksimaciju i SK; model tkiva iz D1 i prihvaćena primjena iz
[ADR-0004](../plan/adr/0004-choose-debye-models-of-human-tissues.md). Bibliografski podaci
nalaze se u [vodiču kroz literaturu](../research/LITERATURE.md).

Tekst označen **vlastiti izvod** razrađuje algebru ili tumačenje projektnog modela; nije nova
tvrdnja pripisana L1. Mali primjer u §7 ima namjerno poznato točno rješenje i nije eksperiment
na tkivima. Oznake slijede [metodologiju](../plan/METHODOLOGY.md).

## 1. Koji je sustav i koju funkciju aproksimiramo

### 1.1 Linearni model tkiva i jedinice

**Projektni model i vlastito tumačenje.** Promatramo jednu komponentu električnog polja u
homogenom izotropnom tkivu s fiksnim parametrima. Pretpostavljamo linearni odziv i vremensku
nepromjenjivost; početni uvjeti su nulti. Prostorno širenje polja i promjena svojstava tkiva
s vremenom nisu dio ovog skalarnog modela materijala. U frekvencijskoj domeni efektivna
relativna permitivnost povezuje polje $E$ i ukupnu gustoću struje $J_{\mathrm{tot}}$:

$$
J_{\mathrm{tot}}(s)=s\varepsilon_0\varepsilon(s)E(s),\qquad
\varepsilon(s)=\varepsilon_\infty+
\sum_{n=1}^{4}\frac{\Delta\varepsilon_n}{1+(s\tau_n)^{1-\alpha_n}}
+\frac{\sigma_i}{s\varepsilon_0}.
$$

Ukupna struja obuhvaća polarizaciju, trenutni odziv i ionsku vodljivost. Stoga je
$\varepsilon(s)$ prijenos od $E$ prema $J_{\mathrm{tot}}/(s\varepsilon_0)$, tj. integriranoj
ukupnoj struji podijeljenoj s $\varepsilon_0$. Time ne poistovjećujemo efektivni član
vodljivosti s čistim električnim pomakom. Riječ je o realnom LTI SISO opisu materijala;
LTI prijenosna funkcija može biti neracionalna i tada nema konačnu realizaciju običnim
diferencijalnim jednadžbama.

| Oznaka | Značenje | Jedinica |
|---|---|---|
| $f$ | frekvencija na sučelju koda | Hz |
| $\omega=2\pi f$, $s=\imath\omega$ | kružna frekvencija i Laplaceova varijabla na osi | rad/s |
| $\varepsilon$, $\varepsilon_\infty$, $\Delta\varepsilon_n$, $\alpha_n$ | relativna permitivnost i parametri | bezdimenzijski |
| $\tau_n$ | vrijeme relaksacije, nakon pretvorbe tablice | s |
| $\sigma_i$, $\varepsilon_0$ | ionska vodljivost i permitivnost vakuuma | S/m, F/m |
| $\lambda_j$, $\phi_j$ | pol i rezidual bezdimenzijskog modela $H_r$ | rad/s |

Za konvenciju $s=\imath\omega$ vrijedi $\varepsilon=\varepsilon'-\imath\varepsilon''$.
Faktor $2\pi$ ne smije se izostaviti pri pretvorbi Hz u položaj pola. U modelu se koristi
glavna grana potencije; za $0\le\alpha_n<1$ i točke izvan reza negativne realne osi vrijedi
$H(\overline{s})=\overline{H(s)}$. To svojstvo izražava realnost sustava.

### 1.2 Poznati članovi ostaju točni

**Vlastiti izvod iz modela.** Aproksimiramo samo

$$
H(s)=\sum_{n=1}^{4}\frac{\Delta\varepsilon_n}{1+(s\tau_n)^{1-\alpha_n}},\qquad
\varepsilon_r(s)=\varepsilon_\infty+H_r(s)+\frac{\sigma_i}{s\varepsilon_0}.
$$

Tada je $\varepsilon_r-\varepsilon=H_r-H$: pogrešku stvaraju samo aproksimirane disperzije.
Konstanta $\varepsilon_\infty$ ne pada u beskonačnosti, a nenulti član vodljivosti ima pol
u nuli. Zato pojedinačno nemaju konačnu punu $\mathcal{H}_2$ normu. Na pojasu udaljenom od
nule mogli bismo ih numerički prilagođavati, ali time bismo trošili parametre i unosili
pogrešku u već poznate članove. Njihovo izdvajanje odluka je ADR-0004.

Za svaki prisutni član tražimo $\Delta\varepsilon_n>0$, $\tau_n>0$ i
$0\le\alpha_n<1$. Član s $\Delta\varepsilon_n=0$ izostaje. Funkcija $H$ teži nuli za
$|s|\to\infty$ u desnoj poluravnini; u projektu je zato zovemo strogo pravim dijelom i
kada nije racionalna. Konačnost pune norme traži dodatne uvjete brzine pada, obrađene u
[izvodu B2](b2-h2-kvadratura.md), §2; sam pad prema nuli nije dovoljan.

### 1.3 Od Cole–Coleova do Debyejeva člana

**Vlastiti izvod.** Za $\alpha=0$ dobivamo

$$
\frac{\Delta\varepsilon}{1+s\tau}
=\frac{\Delta\varepsilon/\tau}{s-(-1/\tau)}.
$$

To je jedan Debyejev član s realnim negativnim polom $\lambda=-1/\tau$ i pozitivnim
rezidualom $\phi=\Delta\varepsilon/\tau$. Za $0<\alpha<1$ potencija $s^{1-\alpha}$ ima
točku grananja u nuli pa član nije racionalna funkcija. U zbroju prisutnih tabličnih
članova pozitivne amplitude ne mogu poništiti vodeći necjelobrojni član razvoja u nuli.
Zato model s takvom disperzijom općenito traži aproksimaciju, a ne točan oporavak konačnog
reda. Tražimo najmanji broj polova za zadanu točnost na odabranom pojasu.

Za jednostavne polove racionalni je cilj

$$
H_r(s)=\sum_{j=1}^{r}\frac{\phi_j}{s-\lambda_j}.
$$

Realan racionalni model ima realne polove s realnim rezidualima ili konjugirane parove
polova s konjugiranim rezidualima. Stabilan je ako svi stvarni polovi imaju negativan
realni dio (L1, §1). L1 zasebno naziva granično stabilnim slučaj u kojem su preostali
polovi jednostavni i na imaginarnoj osi; to nije uvjet stabilnosti potreban za
$\mathcal{H}_2$ model. LS korak bez dodatnih uvjeta sam ne nameće stabilnost, realnost
svih polova ni pozitivnost reziduala. Konjugirani par daje realan sustav, ali nije zbroj
Debyejevih relaksacija s realnim polovima. To treba razlikovati pri vrednovanju rezultata.

## 2. Racionalni problem najmanjih kvadrata

**Prema L1, §1, (1.1)–(1.2).** Zadani su konačni uzorci $h_i=H(\xi_i)$,
$i=1,\dots,\ell$, i pozitivne težine $\rho_i$. Za frekvencijske podatke
$\xi_i=\imath\,2\pi f_i$. Tražimo strogo pravi racionalni model reda $r$:

$$
\min_{H_r\in\mathcal{R}_r}J(H_r),\qquad
J(H_r)=\sum_{i=1}^{\ell}\rho_i\,|H_r(\xi_i)-h_i|^2.
$$

Nazivnik ima stupanj $r$, a brojnik najviše $r-1$; nakon eventualnog kraćenja stvarni red
može biti manji. Zapis zbrojem jednostavnih polova pretpostavlja jednostavne polove.
Višestruki polovi zahtijevaju dodatne članove višeg reda i ne stanu u taj zapis.

**Zašto problem nije linearan ni konveksan (vlastita ilustracija).** Uz $H_r=n/d$,
koeficijenti nazivnika ulaze u razlomak. Ni skup dopuštenih funkcija nije konveksan:
prosjek $1/(s+1)$ i $1/(s+2)$ jest $(2s+3)/(2(s+1)(s+2))$, što ima dva nekraćena pola i
ne pripada klasi reda jedan. Nekonveksnost se pojavljuje i uz realne stabilne polove.
L1 zato upozorava na moguća različita lokalna rješenja; niz linearnih LS koraka nije
dokaz pronalaska globalnog minimuma.

Težina $\rho_i$ množi **kvadrat** pogreške. Odgovarajuća težina retka LS matrice jest
$\sqrt{\rho_i}$. Funkcije kvadrature u kodu vraćaju integralne težine $w_i$, pa za taj
slučaj ovdje vrijedi $\rho_i=w_i$. B2 i komentari koda ponegdje označavaju težinu retka
simbolom $\rho_i$; tamo je to $\sqrt{w_i}$, a ne $\rho_i$ iz (1.1). Razlikujemo značenje
prije prijenosa formule u kod. Zajednički pozitivan faktor svih težina ne mijenja minimizator.

## 3. Levyjeva linearizacija: što se mijenja u cilju

**L1, §1, (1.2)–(1.3); razrada je vlastita.** Uz pretpostavku $d(0)\ne0$ uklonimo
slobodu istodobnog množenja brojnika i nazivnika nenultom konstantom normalizacijom

$$
n(s)=\sum_{j=0}^{r-1}\alpha_js^j,\qquad
d(s)=1+\sum_{j=1}^{r}\beta_js^j.
$$

Ovdje su $\alpha_j$ polinomni koeficijenti, a ne parametri Cole–Coleova modela. Ako je
$d(\xi_i)\ne0$, točno vrijedi

$$
H_r(\xi_i)-h_i=\frac{n(\xi_i)-d(\xi_i)h_i}{d(\xi_i)},\qquad
J(n/d)=\sum_i\frac{\rho_i}{|d(\xi_i)|^2}|n(\xi_i)-d(\xi_i)h_i|^2.
$$

Brojnik tog izraza jest afin u nepoznatim koeficijentima, ali težina još ovisi o traženom
nazivniku. Levy izostavlja faktor $1/|d(\xi_i)|^2$ i minimizira

$$
J_{\mathrm{Levy}}(n,d)=\sum_i\rho_i|n(\xi_i)-d(\xi_i)h_i|^2
=\sum_i\rho_i|d(\xi_i)|^2|H_r(\xi_i)-h_i|^2.
$$

Dobivamo linearni LS problem, ali drugi cilj: mjesta s velikim $|d(\xi_i)|$ dobivaju
veći utjecaj nego u izvornom racionalnom problemu. Nije riječ o točnoj algebarskoj
linearizaciji funkcije $J$. Normalizacija je nužna: bez nje bi $n=d=0$ trivijalno
poništili linearizirani rezidual, a racionalna funkcija ne bi bila definirana.

## 4. SK: težina dolazi iz prethodnog koraka

**L1, §2.1, (2.1); ovdje dodajemo zadane težine iz (1.1).** Počevši s
$d^{(0)}(s)=1$, u koraku $k$ rješavamo

$$
\min_{n^{(k+1)},d^{(k+1)}}\sum_i\rho_i
\left|\frac{n^{(k+1)}(\xi_i)-d^{(k+1)}(\xi_i)h_i}{d^{(k)}(\xi_i)}\right|^2.
$$

Prethodni nazivnik je poznat, pa je ovo linearni problem u novim koeficijentima, uz
odabranu normalizaciju novog nazivnika. Njegova dijagonalna matrica težina retka jest

$$
\Delta^{(k)}=\operatorname{diag}\left(
\frac{\sqrt{\rho_i}}{|d^{(k)}(\xi_i)|}\right)_{i=1}^{\ell}.
$$

Mogli bismo dijeliti kompleksnim $d^{(k)}(\xi_i)$: uklanjanje njegove faze samo množi svaki
redak jediničnim kompleksnim faktorom i ne mijenja normu. Prvi korak jest Levyjev problem
u ovoj normalizaciji. Ako su novi nazivnici nenulti u čvorovima, isti cilj možemo pisati

$$
\sum_i\rho_i\left|\frac{d^{(k+1)}(\xi_i)}{d^{(k)}(\xi_i)}\right|^2
|H_r^{(k+1)}(\xi_i)-h_i|^2.
$$

Ideja je da se faktor približi jedinici. To objašnjava iteraciju, ali ne dokazuje
konvergenciju, pad izvorne funkcije $J$ ni lokalnu optimalnost njezine granice.
Očekivanje lokalne optimalnosti iz L1, §2.1 nije teorem. Posebno, poklapanje vrijednosti
dvaju ciljeva u granici ne znači poklapanje njihovih derivacija po parametrima.
Mali rezidual na uzorcima također ne jamči malu pogrešku između čvorova ni u punim
$\mathcal{H}_2$ ili $\mathcal{H}_\infty$ normama (L1, Primjer 3.1; izvod B2, §3).

Ako je $d^{(k)}(\xi_i)=0$, korak nije definiran. Mali nazivnik može proizvesti vrlo velike
težine. Takav slučaj i loš numerički rang moraju se prijaviti; proizvoljno odrezivanje
težina bilo bi promjena metode.

## 5. Polinomni prikaz: od jednadžbe do retka matrice

**Vlastita razrada L1, (2.2)–(2.3).** Pišemo

$$
\sum_{j=0}^{r-1}\alpha_j\xi_i^j-h_i\sum_{j=1}^{r}\beta_j\xi_i^j\approx h_i.
$$

Za $y=(\alpha_0,\dots,\alpha_{r-1},\beta_1,\dots,\beta_r)^T$ dobivamo

$$
B_{i,:}=\left(1,\xi_i,\dots,\xi_i^{r-1},
-h_i\xi_i,\dots,-h_i\xi_i^r\right),\qquad
\min_y\|\Delta^{(k)}(By-h)\|_2^2.
$$

Matrica $B$ ima $\ell$ redaka i $2r$ stupaca; nastaje od potencija čvorova, pa je
Vandermondeova tipa. Čvorovi i uzorci ostaju zadani, a u SK-u se mijenja $\Delta^{(k)}$.
Za jednoznačan kompleksni LS korak treba puni stupčani rang $2r$ i zato barem
$\ell\ge2r$ kompleksnih jednadžbi. Broj redaka sam ne jamči rang.

Za realni model možemo tražiti realne polinomne koeficijente. Tada se rješava

$$
\min_{y\in\mathbb{R}^{2r}}
\left\|\begin{pmatrix}\operatorname{Re}(\Delta^{(k)}B)\\
\operatorname{Im}(\Delta^{(k)}B)\end{pmatrix}y-
\begin{pmatrix}\operatorname{Re}(\Delta^{(k)}h)\\
\operatorname{Im}(\Delta^{(k)}h)\end{pmatrix}\right\|_2^2.
$$

Sada ima $2\ell$ realnih redaka, a i dalje treba rang $2r$. Konjugirani uzorci s jednakim
težinama samo udvostručuju cilj za realne koeficijente; nisu nova neovisna mjerenja.
Kod stvarnih podataka simetriju treba provjeriti, a ne prešutno nametnuti usrednjavanjem.
Velik raspon potencija $\xi_i^j$ može uzrokovati lošu uvjetovanost (L1, §4.3).

## 6. Baricentrični prikaz

### 6.1 Izvod iz polinoma

**L1, §2.1, (2.4)–(2.5); vlastita razrada.** Odaberimo međusobno različite pomoćne točke
$\lambda_1,\dots,\lambda_r$ i definirajmo čvorni polinom i Lagrangeove faktore

$$
\omega_r(s)=\prod_{j=1}^{r}(s-\lambda_j),\qquad
\gamma_j=\frac{1}{\omega_r'(\lambda_j)}
=\frac{1}{\prod_{m\ne j}(\lambda_j-\lambda_m)}.
$$

$\omega_r$ ovdje je polinom, a ne kružna frekvencija. Za $\deg n\le r-1$ i
$\deg d=r$ Lagrangeova interpolacija daje

$$
\frac{n(s)}{\omega_r(s)}=\sum_j\frac{\gamma_jn(\lambda_j)}{s-\lambda_j},\qquad
\frac{d(s)}{\omega_r(s)}=a+\sum_j\frac{\gamma_jd(\lambda_j)}{s-\lambda_j}.
$$

Za prvu jednakost obje strane nakon množenja s $\omega_r$ imaju stupanj najviše $r-1$
i jednake vrijednosti u $r$ točaka. U drugoj je $a\ne0$ vodeći koeficijent od $d$:
polinom $d-a\omega_r$ ima stupanj najviše $r-1$ pa vrijedi isti argument. L1 taj
koeficijent određuje i pomoću dodatne točke $\lambda_0$; ovdje nam ona nije potrebna.

Podijelimo oba izraza s $a$ i definirajmo
$\phi_j=\gamma_jn(\lambda_j)/a$, $\varphi_j=\gamma_jd(\lambda_j)/a$. Dobivamo

$$
H_r(s)=\frac{\widetilde n(s)}{\widetilde d(s)},\qquad
\widetilde n(s)=\sum_j\frac{\phi_j}{s-\lambda_j},\qquad
\widetilde d(s)=1+\sum_j\frac{\varphi_j}{s-\lambda_j}.
$$

Koeficijenti $\phi_j$ ovdje su reziduali pomoćnog brojnika; općenito još nisu reziduali
konačnog modela $H_r$. Pomoćne točke $\lambda_j$ također općenito nisu njegovi polovi.
Primjerice, uz $\varphi_j\ne0$ granična vrijednost u toj točki jest
$H_r(\lambda_j)=\phi_j/\varphi_j$: singularnosti pomoćnih izraza mogu se skratiti.
Stvarne polove određuje nazivnik nakon množenja s $\omega_r$ i eventualnog kraćenja.

### 6.2 LS matrica Cauchyjeva tipa

**Vlastiti izvod L1, (2.6)–(2.7).** Za $\xi_i\ne\lambda_j$ vrijedi

$$
\sum_j\frac{\phi_j}{\xi_i-\lambda_j}
-h_i\sum_j\frac{\varphi_j}{\xi_i-\lambda_j}\approx h_i.
$$

Uz $C_{ij}=1/(\xi_i-\lambda_j)$ i
$x=(\phi_1,\dots,\phi_r,\varphi_1,\dots,\varphi_r)^T$:

$$
A=\left(C,\;-\operatorname{diag}(h)C\right),\qquad
\min_x\|\widetilde\Delta^{(k)}(Ax-h)\|_2^2,\qquad
\widetilde\Delta_{ii}^{(k)}=\frac{\sqrt{\rho_i}}{|\widetilde d^{(k)}(\xi_i)|}.
$$

To je matrica Cauchyjeva tipa s $\ell$ redaka i $2r$ stupaca. U SK-u iz §2.1 pomoćne
točke ostaju fiksne. VF iz §2.2 ih zatim mijenja apsorbirajući SK težinu u novu bazu;
izvod tog koraka pripada A5. Fiksne točke u ovom odjeljku nisu referentna metoda B4:
ovdje se određuju i koeficijenti nazivnika $\varphi_j$, a u B4 samo reziduali uz već
fiksirane stvarne polove. Bliske pomoćne točke mogu dati gotovo zavisne stupce, pa
baricentrični zapis sam ne rješava svu lošu uvjetovanost.

Za realne $\lambda_j$ mogu se tražiti realni $\phi_j,\varphi_j$ slaganjem realnih i
imaginarnih dijelova kao u §5. Za konjugirane pomoćne točke koeficijenti se moraju
povezati u konjugirane parove; slobodan kompleksni LS samo na pozitivnim frekvencijama
sam po sebi to ne jamči. Podudaranje $\xi_i=\lambda_j$ i višestruke točke nisu dopušteni
ulazi za upravo izvedenu matricu; eventualno posebno rukovanje treba zasebno izvesti.

### 6.3 Ista funkcija, različiti koeficijenti i normalizacije

**Vlastita provjera pretpostavki pri promjeni baze.** Permutacija pomoćnih točaka s
pripadajućim koeficijentima ne mijenja funkciju. Ni izbor drugog skupa različitih
pomoćnih točaka ne mijenja klasu racionalnih funkcija, ali mijenja $\phi,\varphi$.
Zato se uspoređuju funkcije ili skupovi stvarnih polova, a ne pojedini koeficijenti.

Pri prijenosu LS problema mora se pratiti i normalizacija. L1 oba prikaza opisuje kao
formulacije SK-a. No uvjet $d(0)=1$ iz polinomnog zapisa i uvjet
$\widetilde d(\infty)=1$ iz baricentričnog zapisa nisu ista normalizacija: drugi znači
da je polinom $\omega_r\widetilde d$ moničan. Ako ih pretvaramo formulama iz §6.1,
uz isti čvorni polinom i nenulte vodeće koeficijente $a_k,a_{k+1}$ vrijedi

$$
\frac{\widetilde n^{(k+1)}-\widetilde d^{(k+1)}h}{\widetilde d^{(k)}}
=\frac{a_k}{a_{k+1}}
\frac{n^{(k+1)}-d^{(k+1)}h}{d^{(k)}}.
$$

Faktor ovisi o novom nepoznatom nazivniku; ne smije se proglasiti nevažnom konstantom
u minimizaciji. Zbog toga ovdje ne tvrdimo da dvije neovisno normalizirane iteracije,
obje pokrenute s jediničnim pomoćnim nazivnikom, moraju dati iste iteracije.

Za točnu promjenu baze možemo, primjerice, uzeti **monične polinomne nazivnike**
$d=\omega_r\widetilde d$, $n=\omega_r\widetilde n$, bez dodatnog dijeljenja s
nepoznatim $a$. Ako je i prethodni nazivnik povezan istom formulom, faktor
$\omega_r(\xi_i)$ krati se između lineariziranog reziduala i prethodnog nazivnika.
Tada su ciljevi doista jednaki. Početni $\widetilde d^{(0)}=1$ pritom odgovara
$d^{(0)}=\omega_r$, a ne $d^{(0)}=1$. Alternativa je prenijeti isti normalizacijski
uvjet kao linearnu vezu među baricentričnim koeficijentima. Odabir za implementaciju A4
treba zapisati uz izvod A5; ova provjera ne donosi novu odluku o algoritmu.

## 7. Ručno razrađen primjer reda jedan

**Vlastiti analitički primjer.** Kako ne bismo skrivali jedinice, uzmimo
$\omega_*=1\ \mathrm{rad/s}$, $z=s/\omega_*$ i bezdimenzijsku funkciju
$G(z)=H(\omega_*z)=2/(z+1)$. Dvije točke su $z_1=\imath$, $z_2=2\imath$, odnosno
$f_1=\omega_*/(2\pi)$, $f_2=2\omega_*/(2\pi)$ u Hz. Uzorci su

$$
h_1=1-\imath,\qquad h_2=\frac25-\frac45\imath.
$$

### 7.1 Polinomni korak

Za $G_1(z)=\alpha_0/(1+\beta_1z)$, jedinične težine i $d^{(0)}=1$ tražimo realne
$(\alpha_0,\beta_1)$. Iz retka $(1,-h_iz_i)$ dobivamo, s realnim i imaginarnim retkom
svakog uzorka jedan ispod drugoga,

$$
\min_{\alpha_0,\beta_1\in\mathbb R}
\left\|
\begin{pmatrix}1&-1\\0&-1\\1&-8/5\\0&-4/5\end{pmatrix}
\begin{pmatrix}\alpha_0\\\beta_1\end{pmatrix}
-\begin{pmatrix}1\\-1\\2/5\\-4/5\end{pmatrix}
\right\|_2^2.
$$

Drugi redak daje $\beta_1=1$, prvi $\alpha_0=2$, a preostali su točno zadovoljeni.
Matrica ima rang dva pa je rješenje jedinstveno. Model je $G_1=2/(z+1)$ s nultim
rezidualom. U idućem koraku težine dvaju kompleksnih redaka bile bi $1/\sqrt2$ i
$1/\sqrt5$; rješenje ostaje isto jer se nulti rezidual ne mijenja pozitivnim težinama.

### 7.2 Baricentrični korak

Odaberimo pomoćnu točku $\lambda=-3$ u varijabli $z$ i $\widetilde d^{(0)}=1$.
Prvi korak ima kompleksni sustav

$$
\begin{pmatrix}
(3-\imath)/10&(-1+2\imath)/5\\
(3-2\imath)/13&(2+16\imath)/65
\end{pmatrix}
\begin{pmatrix}\phi\\\varphi\end{pmatrix}
\approx\begin{pmatrix}1-\imath\\(2-4\imath)/5\end{pmatrix}.
$$

Rješenje je realno, $\phi=2$, $\varphi=-2$, s nultim rezidualom:

$$
G_1(z)=\frac{2/(z+3)}{1-2/(z+3)}=\frac{2}{z+1}.
$$

Pomoćna točka $-3$ nije stvarni pol $-1$. Uz pomoćnu točku $-5$ isti model imao bi
$\phi=2$, $\varphi=-4$. U fizikalnoj varijabli $s$ stvarni pol jest $-\omega_*$, a
rezidual $2\omega_*$. Oba LS problema ovdje vraćaju istu funkciju jer točno rješenje
poništava sve reziduale; to ne dokazuje jednakost dviju normalizacija za netočne podatke.
Primjer ne dokazuje opću konvergenciju VF-a i ne bira početne polove za tkiva.

## 8. Predaja za B9 i nastavak

Za Sarin neovisni pregled preostaje provjeriti izvode redaka u §5 i §6.2, račun u §7 i
razliku normalizacija u §6.3. Stvarni pregled i eventualne nejasnoće bilježe se tek kad
se provedu. Korisna pitanja za zajednički prolaz:

1. Zašto promjena iz $|n-dh|^2$ u $|n-dh|^2/|d|^2$ nije samo množenje cilja konstantom?
2. Zašto $w_i$ iz kvadrature daje težinu retka $\sqrt{w_i}$?
3. Zašto pomoćna točka $\lambda$ i koeficijent $\phi$ još nisu nužno pol i rezidual modela?
4. Koji se početni nazivnik i normalizacija prenose pri promjeni baze?

A5 nastavlja premještanjem polova, identifikacijom reziduala, zrcaljenjem i granicama
tvrdnji o konvergenciji. A4 i dalje čeka probni kod B1; ovaj dokument nije implementacija.
