# B2: $\mathcal{H}_2$ greška, kvadratura i QuadVF

**Izvor:** L1 = Z. Drmač, S. Gugercin, C. Beattie, *Quadrature-Based Vector Fitting for Discretized
$\mathcal{H}_2$ Approximation*, SIAM J. Sci. Comput. 37(2), 2015, A625–A652.

**Oznake vrste tvrdnje.** Uz svaku tvrdnju piše je li:
**citirano** (s mjestom u L1), **vlastiti izvod/izračun** (naš račun, provjerljiv na papiru ili
numerički) ili **opažanje** (rezultat izračuna na primjeru, ne opća tvrdnja).

**Pregled.** Projekt traži najmanji broj polova $r$ za koji model $H_r$ reproducira funkciju tkiva $H$
uz zadanu točnost. Za to treba: (§1) mjera greške, (§2) jasno definirana funkcija koju aproksimiramo,
(§3) razumijevanje zašto obični VF ne minimizira tu mjeru, (§4) kvadratura koja integral pretvara u
zbroj, (§5) QuadVF, koji tu kvadraturu ugrađuje u VF, i (§6) naše prilagodbe za tkiva.

---

## 1. $\mathcal{H}_2$ norma kao mjera greške

### 1.1 Definicija

**Citirano (L1, §3.1, (3.1), str. A631).** $\mathcal{H}_2(\mathbb{C}_+)$ je prostor funkcija $G(s)$ analitičkih u
otvorenoj desnoj poluravnini $\mathbb{C}_+=\{s:\operatorname{Re}s>0\}$ za koje je
$\sup_{x>0}\int_{-\infty}^{\infty}\lvert G(x+\imath y)\rvert^2dy<\infty$. Skalarni produkt i norma su

$$
\langle G,H\rangle_{\mathcal{H}_2}=\frac{1}{2\pi}\int_{-\infty}^{\infty}\overline{H(\imath\omega)}\,G(\imath\omega)\,d\omega,
\qquad
\|G\|_{\mathcal{H}_2}^2=\frac{1}{2\pi}\int_{-\infty}^{\infty}\lvert G(\imath\omega)\rvert^2\,d\omega .
$$

Funkcija se poistovjećuje sa svojim vrijednostima na imaginarnoj osi $s=\imath\omega$ (L1: operator
$\mathcal{T}$), pa sve računamo samo za $s=\imath\omega$, gdje je $\omega$ kružna frekvencija u rad/s. To su
upravo vrijednosti koje se mjere (frekvencijski odziv).

**Tumačenje (vlastito).** Na svakoj frekvenciji uzmemo kvadrat iznosa $\lvert G(\imath\omega)\rvert^2$ i zbrojimo
(integriramo) po svim frekvencijama. Norma dakle mjeri koliko je funkcija „velika” ukupno, po
cijelom frekvencijskom području.

### 1.2 Greška modela

Za funkciju $H$ i model $H_r$:

$$
\text{greška}=\|H-H_r\|_{\mathcal{H}_2},\qquad
\text{relativna greška}=\frac{\|H-H_r\|_{\mathcal{H}_2}}{\|H\|_{\mathcal{H}_2}} .
$$

Relativna greška $0{,}01$ znači točnost od otprilike 1 %. Faktor $1/(2\pi)$ pojavljuje se i u
brojniku i u nazivniku, pa se u relativnoj grešci krati.

### 1.3 Kada norma postoji

Integral mora biti konačan. Za racionalnu funkciju to znači dvije stvari (vlastito, iz definicije):

1. **nema polova u $\mathbb{C}_+$ ni na imaginarnoj osi** (sustav je stabilan, $\operatorname{Re}\lambda<0$);
2. **$G(\imath\omega)\to0$ kad $\omega\to\pm\infty$**, tj. funkcija je strogo prava (stupanj brojnika manji od
   stupnja nazivnika). Konstanta ne pada prema nuli, pa nema konačnu normu.

### 1.4 Primjer: jedan pol

**Vlastiti izračun.** Neka je $G(s)=\dfrac{1}{s+a}$, $a>0$ (jedan pol u $-a$). Na imaginarnoj osi

$$
\lvert G(\imath\omega)\rvert^2=\frac{1}{\lvert\imath\omega+a\rvert^2}=\frac{1}{\omega^2+a^2}.
$$

Uz poznati integral $\displaystyle\int_{-\infty}^{\infty}\frac{d\omega}{\omega^2+a^2}=\frac{1}{a}\Bigl[\arctan\frac{\omega}{a}\Bigr]_{-\infty}^{\infty}=\frac{\pi}{a}$ dobivamo

$$
\boxed{\ \|G\|_{\mathcal{H}_2}^2=\frac{1}{2\pi}\cdot\frac{\pi}{a}=\frac{1}{2a}\ }
$$

**Tumačenje.** Za veći $a$ norma je manja jer je funkcija niža: $\lvert G(0)\rvert^2=1/a^2$. Funkcija je
„široka” do $\omega\approx a$, ali visina pada brže ($1/a^2$) nego što širina raste ($a$), pa je površina
$\pi/a$ manja. Norma zbraja veličinu funkcije po svim frekvencijama.

**Za kod (B3).** Ovo je test s poznatim rezultatom. Postojeći test u `tests/test_environment.py`
provjerava sam integral $\pi/a$ bez faktora $1/(2\pi)$; u kodu B3/B4 normalizacija mora biti
dosljedna i zapisana.

### 1.5 Optimalni model, IRKA i $\mathcal{H}_\infty$ norma (za tumačenje)

**Citirano (L1, §3.1, (3.2), str. A631–A632).** Ako je $H_r(s)=\sum_{i=1}^{r}\phi_i/(s-\lambda_i)$ najbolji model
reda $r$ u $\mathcal{H}_2$ normi, onda za sve $j=1,\dots,r$

$$
H(-\lambda_j)=H_r(-\lambda_j),\qquad H'(-\lambda_j)=H_r'(-\lambda_j),
$$

tj. optimalni model se s $H$ poklapa po vrijednosti i po derivaciji u **zrcalnim slikama vlastitih
polova** preko imaginarne osi (Hermiteova interpolacija). To su nužni, ne dovoljni uvjeti; vrijede
i za lokalne optimume. L1 dokaz ne daje, nego upućuje na literaturu.

**Tumačenje (vlastito).** Točke $-\lambda_j$ ovise o traženom optimumu, pa nisu poznate unaprijed. IRKA ih
iterativno namješta: iz trenutnih polova računa $H$ i $H'$ u $-\lambda_j$ i gradi novi model. Za to mora
moći izračunati $H$ u točkama koje sama izabere. VF koristi unaprijed zadane uzorke i aproksimira
samo njih, pa nema jamstva $\mathcal{H}_2$ optimalnosti (§3). U L1 IRKA služi kao referenca za
$\mathcal{H}_2$ grešku (Primjer 3.1, §3.4). Za naš problem optimum na cijeloj osi nije ono što tražimo,
jer je norma na cijeloj osi određena niskim frekvencijama (§6.1); analogni uvjeti za grešku na
pojasu nisu izvedeni.

**$\mathcal{H}_\infty$ norma (L1, §3.4.1).** $\|G\|_{\mathcal{H}_\infty}=\sup_{\omega\in\mathbb{R}}\lvert G(\imath\omega)\rvert$, najveća vrijednost na
imaginarnoj osi. Naša druga mjera (najveća relativna greška na gustoj mreži točaka, ADR-0004)
diskretna je inačica te ideje: gleda najgoru frekvenciju umjesto prosjeka.

**Što QuadVF traži od podataka (L1, §3.3).** Vrijednosti $H$ u čvorovima kvadrature, koje bira metoda,
a ne mjerenje. Uz fiksne izmjerene frekvencije QuadVF nije izravno primjenjiv. Kod nas to nije
problem: $H$ je zadan formulom (§2), pa ga možemo izračunati u bilo kojoj točki.

---

## 2. Koju funkciju aproksimiramo

### 2.1 Gabrielov model

**Iz ADR-0004.** Permitivnost tkiva (Gabriel & Gabriel, 1996), uz $s=\imath\omega$:

$$
\varepsilon(s)=\varepsilon_\infty+\sum_{n=1}^{4}\frac{\Delta\varepsilon_n}{1+(s\tau_n)^{1-\alpha_n}}+\frac{\sigma_i}{s\,\varepsilon_0}.
$$

Ima tri vrste dijelova. Za svaki provjeravamo uvjete iz §1.3.

### 2.2 Koji dijelovi imaju normu

**Vlastiti izvod.**

**(a) Konstanta $\varepsilon_\infty$.** Ne pada prema nuli:
$\displaystyle\int_{-\infty}^{\infty}\lvert\varepsilon_\infty\rvert^2d\omega=\infty$. **Nema normu.**

**(b) Član vodljivosti $\sigma_i/(s\varepsilon_0)$.** Na imaginarnoj osi

$$
\Bigl\lvert\frac{\sigma_i}{\imath\omega\,\varepsilon_0}\Bigr\rvert^2=\frac{\sigma_i^2}{\varepsilon_0^2}\cdot\frac{1}{\omega^2}.
$$

Za velike $\omega$ pada, ali oko $\omega=0$ integral $\int d\omega/\omega^2$ divergira: to je pol u $s=0$, na samoj
imaginarnoj osi. **Nema normu.**

**(c) Cole–Coleov član** $\dfrac{\Delta\varepsilon}{1+(s\tau)^{1-\alpha}}$, $0\le\alpha<1$:

- *Analitičnost u $\mathbb{C}_+$.* Za $\operatorname{Re}s>0$ je $\lvert\arg s\rvert<\pi/2$, pa uz glavnu granu
  $\lvert\arg(s\tau)^{1-\alpha}\rvert<(1-\alpha)\pi/2<\pi/2$. Zato je $\operatorname{Re}(s\tau)^{1-\alpha}>0$ i
  $\operatorname{Re}\bigl(1+(s\tau)^{1-\alpha}\bigr)>1$: nazivnik nema nultočaka, član je analitički.
- *Ponašanje za $\omega\to0$:* član teži $\Delta\varepsilon$, konačan, pa nema problema.
- *Ponašanje za $\omega\to\infty$:* $1$ u nazivniku postaje zanemariv, pa

$$
\Bigl\lvert\frac{\Delta\varepsilon}{1+(\imath\omega\tau)^{1-\alpha}}\Bigr\rvert^2\approx\frac{\Delta\varepsilon^2}{(\omega\tau)^{2(1-\alpha)}} .
$$

  Integral $\int^{\infty}\omega^{-p}d\omega$ konačan je samo za $p>1$. Ovdje je $p=2(1-\alpha)$, pa

$$
2(1-\alpha)>1\quad\Longleftrightarrow\quad\alpha<\tfrac12 .
$$

U Gabrielovoj tablici je najveći $\alpha=0{,}3$, pa **svi članovi imaju normu**, a time i njihov zbroj
($\mathcal{H}_2$ je vektorski prostor). Uvjet sa $\sup_{x>0}$ iz definicije provjeren je samo skicom (isto
ponašanje na pravcima $\operatorname{Re}s=x$), ne potpunim dokazom.

### 2.3 Odluka projekta: što fitamo

**Odluka iz ADR-0004, ovdje s obrazloženjem.** Dijelove (a) i (b) znamo točno i nemaju normu, pa ih
oduzimamo i aproksimiramo samo ostatak:

$$
\boxed{\ H(s)=\varepsilon(s)-\varepsilon_\infty-\frac{\sigma_i}{s\,\varepsilon_0}=\sum_{n=1}^{4}\frac{\Delta\varepsilon_n}{1+(s\tau_n)^{1-\alpha_n}}\ }
$$

modelom s $r$ polova

$$
H_r(s)=\sum_{j=1}^{r}\frac{\phi_j}{s-\lambda_j},
$$

**bez konstante**: dodana konstanta $c\neq0$ učinila bi $H-H_r$ funkcijom koja ne pada prema nuli, pa bi
$\|H-H_r\|_{\mathcal{H}_2}$ bila beskonačna.

### 2.4 Debyejev član kao jedan pol

**Vlastiti izračun.** Za $\alpha=0$:

$$
\frac{\Delta\varepsilon}{1+s\tau}=\frac{\Delta\varepsilon/\tau}{s+1/\tau}
\qquad\Rightarrow\qquad
\lambda=-\frac{1}{\tau},\quad \phi=\frac{\Delta\varepsilon}{\tau}.
$$

To je oblik iz §1.4 s $a=1/\tau$, pomnožen s $\phi$, pa je

$$
\Bigl\|\frac{\Delta\varepsilon}{1+s\tau}\Bigr\|_{\mathcal{H}_2}^2=\phi^2\cdot\frac{1}{2a}=\frac{\Delta\varepsilon^2}{\tau^2}\cdot\frac{\tau}{2}=\frac{\Delta\varepsilon^2}{2\tau}.
$$

Za $\alpha>0$ član **nije** racionalna funkcija, pa ga konačan broj polova može samo približiti. Otuda
pitanje projekta: koliko polova treba za zadanu točnost.

**Za kod (B4).** Za tkivo s $\alpha=0$ točna norma je poznata, pa je to test za `metrics`.

---

## 3. LS rezidual nije $\mathcal{H}_2$ greška (Primjer 3.1)

### 3.1 Što VF minimizira

**Citirano (L1, (1.1), str. A626).** Za zadane čvorove $\xi_j=\imath\omega_j$, $j=1,\dots,\ell$, i težine $\rho_j>0$,
VF traži model reda $r$ koji minimizira

$$
\sum_{j=1}^{\ell}\rho_j\,\lvert H_r(\xi_j)-H(\xi_j)\rvert^2 .
$$

(U (1.1) težina $\rho_j$ množi kvadrat odstupanja. U (3.3) i (3.6) $\rho_j$ množi redak sustava, pa se
u funkciji cilja pojavljuje $\rho_j^2$; vidi §5.)

**Što mi želimo (§1):**

$$
\|H-H_r\|_{\mathcal{H}_2}^2=\frac{1}{2\pi}\int_{-\infty}^{\infty}\lvert H(\imath\omega)-H_r(\imath\omega)\rvert^2\,d\omega .
$$

**Razlika (vlastito).** Prvo je zbroj grešaka u izabranim točkama (LS rezidual), drugo integral po
svim frekvencijama. Zbroj:

- ne vidi što se događa **između i izvan** čvorova;
- svakom čvoru daje težinu $\rho_j$ bez obzira na to **koliki dio osi** taj čvor predstavlja.

### 3.2 Primjer iz članka

**Citirano (L1, Primjer 3.1, str. A632–A633); opažanje na jednom primjeru.** Sustav reda $n=1006$
(benchmark NICONET), VF reda $r=12$, $\ell=40$ čvorova logaritamski raspoređenih između $10^{-3}$ i $10^{3}$ Hz:

| | relativni LS rezidual | relativna $\mathcal{H}_2$ greška |
|---|---|---|
| VF | $2{,}75\cdot10^{-4}$ | $1{,}78\cdot10^{-1}$ |
| IRKA, isti red | | $1{,}92\cdot10^{-4}$ |

U točkama je VF model točan na 0,03 %, a po $\mathcal{H}_2$ normi griješi 18 %. Model istog reda može biti
točan na 0,02 % (IRKA), pa problem nije premali $r$, nego **funkcija cilja**. Primjer pokazuje da se to
*može* dogoditi, ne da se uvijek događa.

### 3.3 Ideja: zbroj kao kvadraturna formula

**Citirano (L1, (3.3), str. A633).** Ako su čvorovi $\xi_j$ i težine $\rho_j$ izabrani kao kvadraturna formula,
onda

$$
\int_{-\infty}^{\infty}\lvert H(\imath\omega)-H_r(\imath\omega)\rvert^2d\omega\approx
\sum_{j=1}^{\ell}\rho_j^2\lvert H(\xi_j)-H_r(\xi_j)\rvert^2+\rho_+^2M_+\bigl[\lvert H-H_r\rvert^2\bigr]+\rho_-^2M_-\bigl[\lvert H-H_r\rvert^2\bigr],
$$

pa VF, minimizirajući zbroj, minimizira diskretiziranu $\mathcal{H}_2$ grešku. Uz ekvidistantne čvorove u
konjugiranim parovima, $\rho_j=1$ i $\rho_\pm=0$, zbroj je složena trapezna formula, tj. obični VF.

### 3.4 Primjer: kolika treba biti težina

**Vlastiti primjer.** Kvadratura zamjenjuje integral zbrojem „visina × širina”: težina $\rho_j^2$ treba
biti približno **širina komada osi** koji čvor predstavlja. Za čvorove $\omega=1,10,100,1000$ s granicama
komada na polovici razmaka:

| čvor $\omega_j$ | komad osi | širina $\approx\rho_j^2$ |
|---|---|---|
| 1 | $[0;\,5{,}5]$ | 5,5 |
| 10 | $[5{,}5;\,55]$ | 49,5 |
| 100 | $[55;\,550]$ | 495 |
| 1000 | $[550;\,1450]$ | 900 |

Za $\lvert E\rvert^2\equiv1$ na $[0,1450]$ točan integral je $1450$. Zbroj sa širinama daje
$5{,}5+49{,}5+495+900=1450$, a zbroj s $\rho_j=1$ daje $4$. Kod logaritamskih čvorova s jednakim
težinama **visoke frekvencije su podcijenjene**. Kod jednako razmaknutih čvorova težine su jednake
(trapezna formula).

### 3.5 Posljedica za projekt

Zato mjerimo dvije mjere (ADR-0004): najveću relativnu grešku na gustoj mreži točaka i $\mathcal{H}_2$
grešku na pojasu (§6). Mogu dati različit poredak metoda.

---

## 4. Kvadratura na cijeloj osi, (3.4)–(3.5)

### 4.1 Formula iz članka

**Citirano (L1, §3.3, str. A634).** Uz $L>0$ i $t_j=\dfrac{j\pi}{\ell+1}$, $j=1,\dots,\ell$:

$$
\int_{-\infty}^{\infty}\lvert H(\imath\omega)\rvert^2d\omega\approx
\sum_{j=1}^{\ell}\frac{L\pi}{(\ell+1)\sin^2t_j}\,\lvert H(\imath L\cot t_j)\rvert^2
+\frac{\pi}{2L(\ell+1)}\Bigl(\lvert M_+[H]\rvert^2+\lvert M_-[H]\rvert^2\Bigr),
\tag{3.4}
$$

$$
M_\pm[H]=\lim_{\omega\to\pm\infty}\imath\omega\,H(\imath\omega).
\tag{3.5}
$$

L1 formulu zove Boyd/Clenshaw–Curtis. Izbor $L$ jako utječe na točnost, a optimalni izbor L1 ne
rješava (str. A634). (L1 u (3.4) lijevu stranu piše kao $\|H\|_{\mathcal{H}_2}^2$, bez faktora $1/(2\pi)$ iz (3.1).)

### 4.2 Izvod: zamjena varijable

**Vlastiti izvod.** Problem: os $\omega\in(-\infty,\infty)$ je beskonačna, pa je ne možemo podijeliti na
konačno mnogo komada iste širine. Zamjenom varijable prebacimo je na konačan interval:

$$
\omega=L\cot t,\qquad t\in(0,\pi),\qquad L>0 .
$$

Kad $t$ raste od $0$ do $\pi$, $\cot t$ monotono pada od $+\infty$ do $-\infty$, pa interval $(0,\pi)$ pokriva
cijelu os. Derivacija je

$$
\frac{d\omega}{dt}=-\frac{L}{\sin^2t},
$$

pa

$$
\int_{-\infty}^{\infty}\lvert H(\imath\omega)\rvert^2d\omega
=\int_{\pi}^{0}\lvert H(\imath L\cot t)\rvert^2\Bigl(-\frac{L}{\sin^2t}\Bigr)dt
=\int_{0}^{\pi}\underbrace{\frac{L}{\sin^2t}\,\lvert H(\imath L\cot t)\rvert^2}_{=:f(t)}\,dt .
$$

(Granice se zamijene jer $t=0$ odgovara $\omega=+\infty$, a $t=\pi$ odgovara $\omega=-\infty$; minus iz derivacije
vraća ih u uobičajeni poredak.)

### 4.3 Izvod: trapezna formula u varijabli $t$

**Vlastiti izvod.** Interval $[0,\pi]$ podijelimo na $\ell+1$ jednakih komada širine $h=\dfrac{\pi}{\ell+1}$, s
točkama $t_0=0$, $t_j=jh$, $t_{\ell+1}=\pi$. Složena trapezna formula glasi

$$
\int_0^{\pi}f(t)\,dt\approx h\Bigl[\tfrac12f(0)+f(t_1)+f(t_2)+\dots+f(t_\ell)+\tfrac12f(\pi)\Bigr].
$$

**Unutarnje točke.** $h\,f(t_j)=\dfrac{\pi}{\ell+1}\cdot\dfrac{L}{\sin^2t_j}\,\lvert H(\imath L\cot t_j)\rvert^2$. To je točno zbroj u (3.4).

**Rubna točka $t=0$.** Treba izračunati $f(0)=\lim_{t\to0^+}f(t)$. Koristimo identitet
$\dfrac{1}{\sin^2t}=1+\cot^2t$ i $\cot t=\omega/L$:

$$
\frac{L}{\sin^2t}=L\bigl(1+\cot^2t\bigr)=L+\frac{\omega^2}{L},
$$

pa je

$$
f(t)=\Bigl(L+\frac{\omega^2}{L}\Bigr)\lvert H(\imath\omega)\rvert^2
=L\,\lvert H(\imath\omega)\rvert^2+\frac{1}{L}\,\lvert\imath\omega\,H(\imath\omega)\rvert^2 .
$$

Kad $t\to0^+$, $\omega\to+\infty$. Prvi član teži $0$ jer $H(\imath\omega)\to0$, a drugi prema $\lvert M_+[H]\rvert^2/L$
po definiciji (3.5). Dakle

$$
f(0)=\frac{\lvert M_+[H]\rvert^2}{L},\qquad\text{i analogno (}t\to\pi^-,\ \omega\to-\infty\text{)}\qquad f(\pi)=\frac{\lvert M_-[H]\rvert^2}{L}.
$$

**Rubni doprinos.** S težinom $h/2$:

$$
\frac{h}{2}\bigl(f(0)+f(\pi)\bigr)=\frac{\pi}{2(\ell+1)}\cdot\frac{\lvert M_+[H]\rvert^2+\lvert M_-[H]\rvert^2}{L}
=\frac{\pi}{2L(\ell+1)}\Bigl(\lvert M_+[H]\rvert^2+\lvert M_-[H]\rvert^2\Bigr),
$$

što je točno zadnji član u (3.4). **Zaključak:** formula (3.4) je složena trapezna formula u varijabli $t$,
uključujući rubove.

### 4.4 Tumačenje težina i rubnog člana

**Težina čvora (vlastito).** Komad širine $h$ u varijabli $t$ odgovara komadu širine približno
$\lvert d\omega/dt\rvert\,h$ u varijabli $\omega$. Zato je

$$
\rho_j^2=\Bigl\lvert\frac{d\omega}{dt}\Bigr\rvert_{t_j}\cdot h=\frac{L}{\sin^2t_j}\cdot\frac{\pi}{\ell+1},
$$

tj. težina je širina komada frekvencijske osi koji čvor predstavlja (pravilo iz §3.4). Komadi su
jednaki u $t$, ali nejednaki u $\omega$: čvorovi blizu $t=0$ i $t=\pi$ su na velikim $\lvert\omega\rvert$, rijetki i s
velikim težinama; čvorovi oko $t=\pi/2$ su gusti oko $\omega=0$ i s malim težinama.

**Rubni član (vlastito).** Najviši čvor je na konačnoj frekvenciji $L\cot t_1$. Rubni član pokriva **rep**
funkcije iza njega, do $\omega=\pm\infty$. Primjeri:

- $H=\dfrac{1}{s+a}$: $\ \imath\omega\cdot\dfrac{1}{\imath\omega+a}\to1$, pa $M_\pm=1$ i rep doprinosi;
- $H=\dfrac{1}{(s+a)^2}$: $\ \imath\omega H(\imath\omega)\to0$, pa $M_\pm=0$ i član nestaje.

### 4.5 Uloga parametra $L$

**Vlastito.** Čvorovi su $\omega_j=L\cot t_j$, pa promjena $L$ samo **pomnoži sve čvorove** istim brojem:
na logaritamskoj osi pomiče cijeli skup bez promjene oblika. Za $t=\pi/4$ je $\omega=L$, pa je polovica
pozitivnih čvorova ispod $L$, a polovica iznad. Npr. za $L=1$, $\ell=15$ pozitivni čvorovi su
$5{,}03;\ 2{,}41;\ 1{,}50;\ 1{,}00;\ 0{,}67;\ 0{,}41;\ 0{,}20$.

**Kada je formula točna (vlastiti izvod).** Za $H=\dfrac{1}{s+a}$ i $L=a$:

$$
f(t)=\frac{a}{\sin^2t}\cdot\frac{1}{a^2\cot^2t+a^2}=\frac{a}{\sin^2t}\cdot\frac{\sin^2t}{a^2}=\frac{1}{a},
$$

konstanta, koju trapezna formula integrira točno. Opća pouka: čvorovi trebaju biti gusti tamo
gdje se funkcija mijenja; za $\frac{1}{s+a}$ to je oko $\omega\approx a$.

**Opažanje (vlastiti izračun).** Relativna greška formule (3.4) za $H=\frac{1}{s+1}$ (točan integral $\pi$):

| $L$ | $\ell=10$ | $\ell=20$ | $\ell=40$ |
|---|---|---|---|
| $0{,}1$ | $2{,}5\cdot10^{-1}$ | $3{,}0\cdot10^{-2}$ | $5{,}3\cdot10^{-4}$ |
| $1$ | točno | točno | točno |
| $10$ | $2{,}0\cdot10^{-1}$ | $2{,}9\cdot10^{-2}$ | $5{,}3\cdot10^{-4}$ |

**Za kod (B3).** Test: za $H=\frac{1}{s+a}$ i $L=a$ formula mora dati $\pi/a$ do strojne preciznosti.

### 4.6 Zašto to ne odgovara tkivima

**Opažanje (vlastiti izračun).** Pozitivni čvorovi pokrivaju raspon od otprilike

| $\ell$ | 15 | 100 | 1000 | 10 000 | 40 000 |
|---|---|---|---|---|---|
| dekade | 1,4 | 3,3 | 5,3 | 7,3 | 8,5 |

(dekada = raspon u kojem frekvencija naraste 10 puta). Frekvencije relaksacije mišića
$f_n=1/(2\pi\tau_n)$ su oko 70 Hz, 500 Hz, 450 kHz i 22 GHz, dakle oko 8,5 dekada. Jedan $L$ ne može
postaviti guste čvorove oko svih njih. Uz to, za Cole–Coleov član s $\alpha>0$ je
$\lvert\imath\omega H(\imath\omega)\rvert\sim\omega^{\alpha}\to\infty$, pa $M_+$ ne postoji. Rješenje je §6.

---

## 5. QuadVF, (3.6)–(3.7)

### 5.1 Što treba znati o VF-u

(Detaljan izvod je Lovrin A3; ovdje samo ono što QuadVF koristi. L1 §2, str. A627–A631.)

- **Baricentrični oblik (L1 (2.4)–(2.5)).** Za izabrane točke $\lambda_1,\dots,\lambda_r$ svaki model reda $r$ može se
  pisati kao

$$
H_r(s)=\frac{\sum_{k=1}^{r}\frac{\phi_k}{s-\lambda_k}}{1+\sum_{k=1}^{r}\frac{\varphi_k}{s-\lambda_k}}
$$

  (parcijalni razlomci od $n/\ell$ i $d/\ell$, $\ell(s)=\prod_k(s-\lambda_k)$). Polovi modela su nultočke nazivnika.
  (Oznake kao u L1 i [metodologiji](../plan/METHODOLOGY.md): $\phi_k$ u brojniku, $\varphi_k$ u nazivniku; skripta s predavanja ih ima zamijenjene.)
- **Linearizacija (Levy, SK).** Množenjem $H_r(\xi_j)\approx H(\xi_j)$ nazivnikom dobije se jednadžba linearna u
  $\phi_k,\varphi_k$, tj. jedan redak sustava za svaki čvor:

$$
\Bigl[\tfrac{1}{\xi_j-\lambda_1}\cdots\tfrac{1}{\xi_j-\lambda_r}\ \ \tfrac{-H(\xi_j)}{\xi_j-\lambda_1}\cdots\tfrac{-H(\xi_j)}{\xi_j-\lambda_r}\Bigr]x\approx H(\xi_j),
\qquad x=(\phi_1,\dots,\phi_r,\varphi_1,\dots,\varphi_r).
$$

  Množenje nazivnikom mijenja težine greške faktorom $\lvert d\rvert$; SK to ispravlja nazivnikom iz
  prethodnog koraka.
- **VF (L1 §2.2, (2.9)–(2.12)).** Nove točke $\lambda^{(k+1)}$ su nultočke prethodnog nazivnika; time SK težina
  prelazi u novu bazu i svaki korak je LS bez težine. Nultočke se računaju kao svojstvene vrijednosti
  od $\operatorname{diag}(\lambda)-\varphi\mathbf{1}^T$. Nestabilni polovi se zrcale (L1 §4.1), a na kraju se reziduali
  računaju LS-om uz fiksne polove. Pri konvergenciji $\varphi\to0$. Konvergencija nije zajamčena
  (L1, str. A631).

### 5.2 Tri promjene

**Citirano (L1, §3.3, (3.6)–(3.7), str. A634–A635).** QuadVF je algoritam VF u kojem LS korak glasi

$$
\bigl\lVert\Delta\,\bigl(\mathcal{A}(\lambda)\,x-h\bigr)\bigr\rVert_2\to\min,
\qquad
\Delta=\operatorname{diag}(\rho_1,\dots,\rho_\ell,\rho_+),
$$

s tri promjene u odnosu na VF:

1. **Čvorovi kvadrature:** $\ \xi_j=\imath L\cot t_j$, $\ t_j=\dfrac{j\pi}{\ell+1}$.
2. **Retci pomnoženi težinama:** $\ \rho_j=\dfrac{1}{\sin t_j}\sqrt{\dfrac{L\pi}{\ell+1}}$, tj. $\rho_j^2=\dfrac{L\pi}{(\ell+1)\sin^2t_j}$, težina iz (3.4).
3. **Dodatni redak** $\ [\,1\ \cdots\ 1\ \ 0\ \cdots\ 0\,]\,x=M_+[H]\ $ s težinom $\ \rho_+=\sqrt{\dfrac{\pi}{L(\ell+1)}}$.

Cijeli sustav:

$$
\mathcal{A}=\begin{pmatrix}
\frac{1}{\xi_1-\lambda_1}&\cdots&\frac{1}{\xi_1-\lambda_r}&\frac{-H(\xi_1)}{\xi_1-\lambda_1}&\cdots&\frac{-H(\xi_1)}{\xi_1-\lambda_r}\\
\vdots&&\vdots&\vdots&&\vdots\\
\frac{1}{\xi_\ell-\lambda_1}&\cdots&\frac{1}{\xi_\ell-\lambda_r}&\frac{-H(\xi_\ell)}{\xi_\ell-\lambda_1}&\cdots&\frac{-H(\xi_\ell)}{\xi_\ell-\lambda_r}\\
1&\cdots&1&0&\cdots&0
\end{pmatrix},
\qquad
h=\begin{pmatrix}H(\xi_1)\\\vdots\\H(\xi_\ell)\\M_+[H]\end{pmatrix}.
$$

$\Delta$ ovisi samo o čvorovima, pa je ista u svim iteracijama. Čvorovi su zatvoreni na konjugiranje
($\xi_j=\overline{\xi_{\ell+1-j}}$, $\rho_j=\rho_{\ell+1-j}$), pa $H$ treba izračunati samo u pola čvorova.

### 5.3 Zašto baš tako

**Vlastito objašnjenje.**

- **Zašto $\rho_j$, a ne $\rho_j^2$.** LS minimizira zbroj kvadrata redaka. Redak pomnožen s $\rho_j$ ulazi kao
  $\lvert\rho_j\cdot(\text{greška retka})\rvert^2=\rho_j^2\,\lvert\text{greška retka}\rvert^2$, pa u funkciji cilja ostaje točno težina
  kvadrature $\rho_j^2$ iz (3.4).
- **Otkud dodatni redak.** Za model u baricentričnom obliku

$$
\imath\omega\,H_r(\imath\omega)=\frac{\sum_k\frac{\imath\omega}{\imath\omega-\lambda_k}\phi_k}{1+\sum_k\frac{\varphi_k}{\imath\omega-\lambda_k}}\ \xrightarrow{\ \omega\to\infty\ }\ \sum_k\phi_k,
$$

  jer $\frac{\imath\omega}{\imath\omega-\lambda_k}\to1$, a nazivnik $\to1$. Rubni član iz (3.4) traži da model ima isti
  rep kao $H$: $\sum_k\phi_k=M_+[H]$.
- **Otkud $\rho_+^2$.** Za realne sustave $M_+=M_-$, pa se dva rubna člana iz (3.4) spoje u jedan:
  $2\cdot\dfrac{\pi}{2L(\ell+1)}=\dfrac{\pi}{L(\ell+1)}=\rho_+^2$.
- **Što QuadVF minimizira.** Greška retka je Levyjeva greška, koja u VF bazi sadrži SK težinu
  $1/\lvert d^{(k)}\rvert$; pri konvergenciji ($\varphi\to0$) ta težina nestaje. Uz konvergenciju LS dakle
  minimizira kvadraturu $\int\lvert H_r(\imath\omega)-H(\imath\omega)\rvert^2d\omega$, tj. diskretiziranu $\mathcal{H}_2$ grešku.

### 5.4 Rezultat u članku

**Citirano (L1, §3.4.1, str. A635); opažanje na jednom primjeru.** Model topline, $r=4$, $\ell=20$,
čvorovi u istom rasponu, različit samo raspored:

| | relativna $\mathcal{H}_2$ greška |
|---|---|
| VF | $8{,}48\cdot10^{-1}$ |
| QuadVF | $6{,}93\cdot10^{-3}$ |

### 5.5 Za kod

QuadVF ne treba novu jezgru: to je Lovrin `vector_fit` s čvorovima $\xi_j$ i težinama $\rho_j$ koje
**množe redak** (u [podjeli rada](../plan/PODJELA.md) to je zasad prijedlog; dogovoriti s Lovrom). Kod nas otpada dodatni
redak (§6).

---

## 6. Naši odmaci: greška i kvadratura na pojasu

(Ovoga nema u L1. Vlastiti izvod i prijedlog; konačne odluke zapisuju se u Z2.)

### 6.1 Zašto pojas

1. **Pitanje projekta.** Zanima nas točnost tamo gdje se modeli tkiva koriste (MHz–GHz), a Gabrielov
   model je pouzdan tek iznad oko 1 MHz.
2. **Norma na cijeloj osi gleda krivo područje.** *Opažanje (vlastiti izračun, mišić, ADR-0004):*

| frekvencija | 100 Hz | 10 kHz | 1 MHz | 10 MHz | 1 GHz | 10 GHz |
|---|---|---|---|---|---|---|
| $\lvert H(\imath\omega)\rvert$ | $1{,}5\cdot10^{7}$ | $2{,}5\cdot10^{5}$ | $5{,}7\cdot10^{3}$ | $770$ | $53$ | $43$ |

   Od $\|H\|^2$ na cijeloj osi $99{,}8\,\%$ otpada na frekvencije ispod 1 MHz, a $0{,}04\,\%$ na pojas
   10 MHz–10 GHz. Model jednak $H$ svugdje osim na pojasu, a na pojasu nula, imao bi relativnu grešku
   na cijeloj osi $\sqrt{0{,}0004}\approx1{,}9\,\%$: mjera ne prepoznaje model koji je beskoristan na pojasu.
   Fit na cijeloj osi trošio bi polove na niske frekvencije, pa bi procijenjeni najmanji $r$ bio
   iskrivljen.
3. **Tehnički razlozi (§4.6).** Jedan $L$ ne pokriva 8 dekada relaksacija, a $M_+$ za $\alpha>0$ ne postoji.

**Cijena.** Ponašanje modela izvan pojasa ne kontroliramo. To treba navesti u seminaru.

### 6.2 Greška na pojasu

Za realne sustave $\lvert G(-\imath\omega)\rvert=\lvert G(\imath\omega)\rvert$, pa

$$
\|G\|_{\text{pojas}}^2=\frac{1}{2\pi}\int_{\omega_1\le\lvert\omega\rvert\le\omega_2}\lvert G(\imath\omega)\rvert^2d\omega=\frac{1}{\pi}\int_{\omega_1}^{\omega_2}\lvert G(\imath\omega)\rvert^2d\omega,
$$

privremeno $\omega_1=2\pi\cdot10\,\text{MHz}$, $\omega_2=2\pi\cdot10\,\text{GHz}$ (odluka u Z2). To je **polunorma**, ne norma
prostora $\mathcal{H}_2$: funkcija jednaka nuli na pojasu, a različita od nule izvan njega, ima vrijednost 0.
U tekstu pisati „$\mathcal{H}_2$ greška na pojasu”.

**Test za B3 (vlastiti izračun, numerički provjeren).** Za $G=\frac{1}{s+a}$:

$$
\int_{\omega_1}^{\omega_2}\frac{d\omega}{\omega^2+a^2}=\frac{1}{a}\Bigl(\arctan\frac{\omega_2}{a}-\arctan\frac{\omega_1}{a}\Bigr).
$$

### 6.3 Kvadratura na pojasu (prijedlog za Z2)

Pojas obuhvaća 3 dekade, pa radimo u logaritmu frekvencije. Uz $\omega=e^u$, $d\omega=\omega\,du=e^u\,du$:

$$
\int_{\omega_1}^{\omega_2}\lvert G(\imath\omega)\rvert^2d\omega=\int_{\ln\omega_1}^{\ln\omega_2}\lvert G(\imath e^{u})\rvert^2e^{u}\,du .
$$

Interval u $u$ je konačan, a podintegralna funkcija glatka. Gauss–Legendreova formula s $N$ čvorova $x_j$
i težinama $g_j$ na $[-1,1]$, preslikana na $[\ln\omega_1,\ln\omega_2]$, daje

$$
u_j=\frac{\ln\omega_2-\ln\omega_1}{2}\,x_j+\frac{\ln\omega_2+\ln\omega_1}{2},\qquad
\omega_j=e^{u_j},\qquad
\rho_j^2=\frac{\ln\omega_2-\ln\omega_1}{2}\,g_j\,\omega_j .
$$

Čvorovi su približno logaritamski raspoređeni (kao kod običnog VF-a), ali **težina raste s $\omega_j$**,
jer viši čvor predstavlja širi komad osi (§3.4). L1 Gauss–Legendre spominje samo kao jednu od mogućnosti
(str. A633).

**Opažanje (vlastiti izračun, mišić, pojas 10 MHz–10 GHz).**

- Uz 40 logaritamskih čvorova i jednake težine dekada 1–10 GHz nosi $1{,}5\,\%$ zbroja, a u pravom
  integralu $67\,\%$.
- Relativna greška kvadrature za $\int\lvert H\rvert^2d\omega$ na pojasu:

| $N$ | trapezna u $u$ | Gauss–Legendre u $u$ |
|---|---|---|
| 10 | $2{,}6\cdot10^{-2}$ | $5\cdot10^{-8}$ |
| 20 | $5{,}7\cdot10^{-3}$ | $3\cdot10^{-15}$ |
| 40 | $1{,}4\cdot10^{-3}$ | $7\cdot10^{-15}$ |

### 6.4 Bez retka $M_+$

Konačan interval nema rubnog člana u beskonačnosti, pa dodatnog retka iz §5.2 nema. To je i nužno, jer
za $\alpha>0$ granica $M_+$ ne postoji. Odmaci „bez $M_+$” i „greška na pojasu” su jedna odluka.

### 6.5 QuadVF na pojasu

Algoritam VF (§5.1) s:

- čvorovima $\pm\imath\omega_j$ (konjugirani parovi, da model ostane realan);
- težinama $\rho_j$ iz §6.3, koje množe retke;
- bez dodatnog retka.

Budući da su čvorovi u oba slučaja približno logaritamski, usporedba VF i QuadVF na pojasu svodi se
uglavnom na težine. **Tvrdnje L1 o QuadVF-u (npr. §3.4.1) ne prenose se automatski na ovu varijantu**;
to provjerava eksperiment.

### 6.6 Mjerenje greške odvojeno od fita (za B4)

Grešku modela mjerimo formulom iz §6.3 s mnogo više čvorova (npr. 200), **odvojenih od čvorova fita**.
Inače bismo mjerili samo ono što je minimizirano, a to je upravo zamka iz Primjera 3.1.

---

## Otvoreno i za odluku u Z2

- točan pojas $[\omega_1,\omega_2]$;
- kvadraturno pravilo na pojasu (prijedlog: Gauss–Legendre u $\ln\omega$) i broj čvorova fita $N$;
- broj čvorova za mjerenje greške;
- uvjeti optimalnosti za grešku na pojasu (analogni (3.2) iz L1) nisu izvedeni.
