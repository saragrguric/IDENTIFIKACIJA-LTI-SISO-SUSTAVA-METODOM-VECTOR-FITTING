# A5: premještanje polova, reziduali, zrcaljenje i zaustavljanje

**Stanje 2026-11-23:** pripremljeni izvod i numeričke operacije na grani
`lovro/a5-polovi-reziduali`. Preostaju neovisni pregled B9 i zajedničko objašnjenje.
Puna petlja `vector_fit` još čeka probni kod B1, a postavke eksperimenata ostaju za Z2.
Ovaj zadatak nastavlja [izvod A3](a3-problem-sk.md), uključen u ovu granu kao ovisnost.

**Izvor:** L1, §2.1–§2.2, (2.5)–(2.12), str. A628–A631; §4.1, (4.1)–(4.2) i
Propozicija 4.1, str. A641–A642; §4.2, (4.3)–(4.5), Primjer 4.2 i Napomena 4.3,
str. A642–A645. Bibliografski podaci: [literatura](../research/LITERATURE.md).
Algebra označena kao vlastiti izvod razrada je tih formula. Primjeri u
[testovima](../../tests/test_vf_steps.py) umjetne su racionalne funkcije, a ne rezultati na tkivima.

## 1. Korak koji rješavamo i njegove pretpostavke

Uz zadane uzorke $h_i=H(\xi_i)$, $\xi_i=s_i$ u rad/s, i međusobno različite pomoćne
točke $\lambda_j$, definiramo

$$
\widetilde n(s)=\sum_{j=1}^r\frac{\phi_j}{s-\lambda_j},\qquad
\widetilde d(s)=1+\sum_{j=1}^r\frac{\varphi_j}{s-\lambda_j},\qquad
C_{ij}=\frac{1}{\xi_i-\lambda_j}.
$$

**Prema L1, (2.7), (2.12), uz zadane vanjske težine.** U baricentričnoj bazi nakon
apsorpcije SK težine rješavamo linearni problem

$$
\min_{\phi,\varphi}\sum_i w_i\left|
\widetilde n(\xi_i)-h_i\widetilde d(\xi_i)\right|^2
=\min_x\|W(Ax-h)\|_2^2,\qquad
A=(C,-\operatorname{diag}(h)C),\quad W=\operatorname{diag}(\sqrt{w_i}).
$$

Ovdje $w_i>0$ množi kvadrat odstupanja i odgovara $\rho_i$ iz L1, (1.1). To nisu
težine retka. Funkcija `barycentric_step` prima upravo $w_i$; izostavljene težine znače
jedinice. Za SK u fiksnoj bazi efektivne su težine $w_i/|\widetilde d_{\mathrm{preth}}(\xi_i)|^2$;
težina prethodnog nazivnika ne dodaje se automatski u VF korak.

Potrebni su konačni jednodimenzijski ulazi, $\xi_i\ne\lambda_j$ i pozitivne konačne
težine odgovarajuće duljine. Implementacija je za realne sustave: pomoćne točke moraju
biti realne ili točno konjugirano uparene. Točke se ne projiciraju ni usrednjavaju.
Ako su oba konjugirana uzorka zadana, kod provjerava njihovo slaganje relativnom
tolerancijom `SAMPLE_SYMMETRY_RTOL = 1e-10`, bez apsolutnog dodatka. Uzorak u realnoj
točki također mora biti realan unutar iste provjere. Jednostrani frekvencijski podaci
dopušteni su, a realnost modela nameće se parametrizacijom u §4.

Normalizacija $\widetilde d(\infty)=1$ znači da je polinomni nazivnik ispod moničan.
To nije normalizacija konstantnog koeficijenta $d(0)=1$. Pri promjeni baze u nastavku
zadržavamo moničnost, isti stupanj i odgovarajući prethodni nazivnik.

## 2. Od nazivnika do svojstvenih vrijednosti

### 2.1 Koji se korijeni računaju

**Vlastiti izvod L1, (2.9).** Neka je $\omega_r(s)=\prod_j(s-\lambda_j)$ i

$$
P(s)=\omega_r(s)\widetilde n(s),\qquad
Q(s)=\omega_r(s)\widetilde d(s)
=\omega_r(s)+\sum_j\varphi_j\prod_{m\ne j}(s-\lambda_m).
$$

$P$ ima stupanj najviše $r-1$, a $Q$ stupanj $r$ i vodeći koeficijent jedan. Novi
skup pomoćnih točaka $\nu_j=\lambda_j^{(k+1)}$ čine svi korijeni polinoma $Q$, s
višestrukostima. Zato vrijedi $\widetilde d(s)=\prod_j(s-\nu_j)/\omega_r(s)$.

Kad je neki $\varphi_j=0$, $Q$ može zadržati pomoćnu točku $\lambda_j$ iako je ona
uklonjiva singularnost racionalnog izraza $\widetilde d$. Primjerice, uz sve
$\varphi_j=0$ jest $\widetilde d=1$, ali $Q=\omega_r$ i premještanje mora zadržati
svih $r$ pomoćnih točaka. Ne smijemo izgubiti red tražeći samo nekraćene nultočke
racionalnog izraza.

### 2.2 Predznak perturbacije ranga jedan

**Vlastiti izvod.** Za $\Lambda=\operatorname{diag}(\lambda)$ i $e=(1,\dots,1)^T$:

$$
\widetilde d(s)=1+e^T(sI-\Lambda)^{-1}\varphi,
$$

pa lema o determinanti daje

$$
\det\bigl(sI-(\Lambda-\varphi e^T)\bigr)
=\det(sI-\Lambda)\bigl(1+e^T(sI-\Lambda)^{-1}\varphi\bigr)=Q(s).
$$

Identitet vrijedi izvan pomoćnih točaka, a kao jednakost polinoma proteže se i na njih.
Dakle, računamo spektar **$\Lambda-\varphi e^T$**. U L1, §4.2, opažanje (i), piše
plus; uz definiciju s plusom u $\widetilde d$ iz (2.5) ispravan je upravo izvedeni minus.
To potvrđuje neovisni primjer reda jedan: $\lambda=-3$, $\varphi=-2$ daju
$\widetilde d=(s+1)/(s+3)$, pa novi pol mora biti $-1=-3-(-2)$.
Ocjena (4.4), koja ovisi o normi perturbacije, ne ovisi o tom predznaku.

`relocate_poles` računa taj spektar. Vraća i nestabilne i višestruke korijene; ne
izbacuje ih, ne zrcali i ne spaja. Za konjugirane ulaze koristi realnu sličnu matricu
iz §4, tako da realna aritmetika problema svojstvenih vrijednosti čuva konjugirane parove.

## 3. Zašto nova baza apsorbira SK težinu

**Vlastita razrada L1, (2.9)–(2.12).** U jednom prijelazu označimo stare i nove čvorne
polinome s $\omega_{\mathrm{staro}}$ i $\omega_{\mathrm{novo}}=Q_{\mathrm{preth}}$.
Prethodni pomoćni nazivnik jest
$\widetilde d_{\mathrm{preth}}=\omega_{\mathrm{novo}}/\omega_{\mathrm{staro}}$.
Za nove nepoznate polinome $P_{\mathrm{novo}},Q_{\mathrm{novo}}$ vrijedi

$$
\frac{P_{\mathrm{novo}}/\omega_{\mathrm{staro}}
-h Q_{\mathrm{novo}}/\omega_{\mathrm{staro}}}
{\omega_{\mathrm{novo}}/\omega_{\mathrm{staro}}}
=\frac{P_{\mathrm{novo}}-h Q_{\mathrm{novo}}}{\omega_{\mathrm{novo}}}.
$$

Lagrangeovim rastavom desnu stranu ponovno izražavamo kao
$\sum_j\phi_j/(s-\nu_j)-h(1+\sum_j\varphi_j/(s-\nu_j))$.
Težina prethodnog nazivnika nestala je iz eksplicitne dijagonale, ali vanjske težine
$w_i$ ostaju. Potrebni su različiti novi čvorovi i nazivnici nenulti u uzorcima.
Jednakost se odnosi na isti monično normalizirani polinomni problem; ne uvodi
nepoznat skalarni faktor pri svakom koraku.

Ovo je objašnjenje pojedinog koraka, a ne dokaz konvergencije niza. Višestruki novi
korijeni onemogućuju upravo korištenu jednostavnu Cauchyjevu bazu. U kodu sljedeći LS
poziv odbija točno ponovljene polove; gotovo ponovljeni polovi ostaju u problemu, a
gubitak numeričkog ranga i loša uvjetovanost prijavljuju se. Posebna baza za višestruke
polove nije implementirana.

## 4. Kako kod čuva realnost

**Vlastiti izvod parametrizacije.** Za realan pol rezidual je realan. Za par
$\lambda,\overline\lambda$ postavimo $\phi=a+\imath b$, $\overline\phi=a-\imath b$:

$$
\frac{\phi}{s-\lambda}+\frac{\overline\phi}{s-\overline\lambda}
=a\left(\frac1{s-\lambda}+\frac1{s-\overline\lambda}\right)
+b\imath\left(\frac1{s-\lambda}-\frac1{s-\overline\lambda}\right).
$$

To daje transformaciju $T$ iz realnih parametara u konjugirane reziduale, s blokom
$\begin{pmatrix}1&\imath\\1&-\imath\end{pmatrix}$ za svaki par. Ista transformacija
vrijedi za $\varphi$. `barycentric_step` rješava realni sustav dobiven slaganjem
realnih i imaginarnih dijelova matrice $(CT,-\operatorname{diag}(h)CT)$ i desne strane.
Prema tome, ima $2\ell$ realnih jednadžbi i $2r$ realnih nepoznanica. Provjerava se
$\ell\ge r$, a puni rang $2r$ nije zajamčen brojem uzoraka.

Za premještanje polova matrica
$T^{-1}(\Lambda-\varphi e^T)T$ realna je uz navedenu strukturu. Kod provjerava da je
tako prije računanja njezina spektra. Ne uzima proizvoljno realne dijelove kompleksnih
polova ili reziduala. Redoslijed konjugiranih parova u ulazu nije propisan.

LS se rješava istim pozivom `numpy.linalg.lstsq(..., rcond=None)` kao postojeća
referentna metoda B4. Nema normalnih jednadžbi, dodatnog skaliranja redaka ni dodane
regularizacije; `rcond=None` zadržava NumPyjev prag numeričkog ranga. Vraćaju se numerički
rang, omjer najveće i najmanje singularne vrijednosti
te norma **težinskog lineariziranog** reziduala. Uz gubitak stupčanog ranga uvjetovanost
se prijavljuje kao beskonačna. Riječ je o realnoj parametriziranoj matrici; njezin broj
uvjetovanosti ne treba poistovjetiti s brojem iz slobodnog kompleksnog LS problema L1.
Nekonačan izračun ili preljev prijavljuju se kao numerički neuspjeh.

## 5. Završni reziduali uz zadržane polove

**L1, §4.2, nakon opažanja (iii); vlastita razrada.** Nakon što se odabere konačni
skup polova $\lambda$, sigurnije je ponovno riješiti

$$
\min_\phi\sum_i w_i\left|\sum_j\frac{\phi_j}{\xi_i-\lambda_j}-h_i\right|^2,
$$

bez pomoćnog nazivnika. `fit_fixed_poles` to radi istom parametrizacijom $\phi=Tz$,
$z\in\mathbb R^r$, i vraća `PoleResidueModel` s $d=0$, rang, uvjetovanost i normu
težinskog reziduala. Puni stupčani rang sada je $r$. Nestabilan ulazni pol ostaje
nestabilan; pozitivnost reziduala ne nameće se. `model.is_stable()` i `model.is_real()`
ostaju izričite provjere rezultata.

B4 već rješava poseban slučaj s realnim negativnim polovima i frekvencijama u Hz.
Novi poziv u `vfdebye.vf` koristi varijablu $s$ i podržava i konjugirane parove; postojeće
sučelje B4 ostaje isto. Reziduali pomoćnog brojnika iz §1 nisu općenito završni reziduali
jer dijeljenje s $\widetilde d$ mijenja racionalnu funkciju.

## 6. Zrcaljenje nestabilnih polova

**L1, §4.1 i Propozicija 4.1; vlastiti zapis dokaza.** Za $\operatorname{Re}\nu>0$
refleksija preko imaginarne osi jest $\widehat\nu=-\overline\nu$. Na realnom skupu
zatvorenom na konjugiranje to daje isti skup kao promjena predznaka svih nestabilnih
polova iz L1; pojedinačno čuva imaginarni dio pola.

Za $s=\imath\omega$ vrijedi

$$
\left|\frac{\imath\omega-\nu}{\imath\omega-\widehat\nu}\right|
=\left|\frac{\imath\omega-\nu}{\imath\omega+\overline\nu}\right|=1.
$$

Umnožak tih faktora novi je pomoćni nazivnik koji povezuje nezrcaljeni i zrcaljeni
čvorni polinom. Njegova je apsolutna vrijednost jedan na imaginarnoj osi. Zato se
dodatna SK dijagonalna težina u novoj bazi može izostaviti bez promjene LS cilja;
isto vrijedi uz fiksne pozitivne vanjske težine $w_i$. To ne tvrdi da izvorni i
zrcaljeni konačni model imaju iste vrijednosti ili istu pogrešku.

Pretpostavka o uzorcima na imaginarnoj osi bitna je: izvan nje navedeni modul općenito
nije jedan. `reflect_unstable_poles` samo vraća kopiju s tom refleksijom. Polove na osi
ostavlja na osi, pa rezultat nije nužno strogo stabilan. Refleksija može stvoriti
duplikate; kod ih ne spaja i ne pomiče, a novi LS korak ih odbija. Je li i kada se ova
operacija poziva u VF petlji, zajedno s postupkom za polove na osi, ostaje odluka metode.

## 7. Što govore kriteriji zaustavljanja

### 7.1 Uparivanje i ocjena pomaka

**L1, (4.3)–(4.4).** Skupove starih polova i nezrcaljenih novih korijena uspoređujemo
do na permutaciju:

$$
\Omega_k=\min_{\sigma\in S_r}\max_j
|\lambda_j^{(k)}-\lambda_{\sigma(j)}^{(k+1)}|.
$$

To je apsolutna udaljenost u rad/s, koju računa `matching_distance`. L1 navodi ocjenu

$$
\Omega_k\le(2r-1)\|\varphi e^T\|_2
=\sqrt r(2r-1)\|\varphi\|_2
\le r(2r-1)\max_j|\varphi_j|.
$$

Prva nejednakost citirana je ocjena perturbacije spektra iz L1, a jednakost i zadnja
nejednakost slijede iz norme matrice ranga jedan i $\|\varphi\|_2\le\sqrt r\|\varphi\|_\infty$.
Ocjena se odnosi na spektar matrice prije vanjske intervencije zrcaljenjem; pomake nakon
intervencije treba bilježiti zasebno. Mali pomak ne dokazuje nestajanje $\varphi$.

### 7.2 Promjena LS matrice

**Vlastiti izvod L1, (4.5).** Neka je
$\mu_k=\min_{i,j}|\xi_i-\lambda_j^{(k)}|>0$. Nakon uparivanja,

$$
\frac{C(\lambda^{(k)})_{ij}-C(\lambda^{(k+1)})_{ij}}
{C(\lambda^{(k+1)})_{ij}}
=\frac{\lambda_j^{(k)}-\lambda_j^{(k+1)}}{\xi_i-\lambda_j^{(k)}},
$$

pa je najveća relativna promjena najviše $\Omega_k/\mu_k$. Isto vrijedi za nenulte
elemente drugog bloka $-h_iC_{ij}$. Za $h_i=0$ cijeli je taj redak drugog bloka nula;
ne računa se neodređeni relativni omjer $0/0$. Blizina čvora i pola pojačava osjetljivost.
Ocjena promjene matrice ne jamči malu promjenu njezina LS rješenja kad je matrica loše
uvjetovana.

### 7.3 Koliko je pomoćni nazivnik blizu jedinici

**L1, §4.2, opažanje (iii); razrada tumačenja je vlastita.** Za svaki uzorak,

$$
|\widetilde d(\xi_i)-1|
\le\frac{\sqrt r\|\varphi\|_2}{\mu_k}
\le\frac{r\max_j|\varphi_j|}{\mu_k}=:\eta.
$$

Uvjet $\max_j|\varphi_j|\le\epsilon\mu_k/r$ dovoljan je za $\eta\le\epsilon$.
To ograničava promjenu podataka $\widetilde h_i=h_i\widetilde d(\xi_i)$ jer
$|\widetilde h_i-h_i|\le\eta|h_i|$. Pomoćni brojnik dobiven LS korakom aproksimira te
perturbirane podatke. Kad linearizirani rezidual $e_i=\widetilde n_i-h_i\widetilde d_i$
nije nula, vrijedi

$$
\widetilde n_i-h_i=e_i+h_i(\widetilde d_i-1).
$$

Zato samu granicu $\eta$ ne smijemo proglasiti ukupnom relativnom pogreškom prilagodbe.
Ona je pokazatelj perturbacije podataka i opravdava razmatranje završne identifikacije
reziduala, ne zaključak o optimalnosti ili kvaliteti između čvorova. Kod zasad ne bira
$\epsilon$ i na temelju tih ocjena ne zaustavlja petlju.

### 7.4 Kruženje i granice tvrdnji

**L1, §4.2, Primjer 4.2 i Napomena 4.3.** Konvergencija VF iteracije nije općenito dokazana.
Primjer reda 17 pokazuje period dva; za red 18 polovi se ustaljuju uz nenulte reziduale
nazivnika. Ne smijemo zaključiti $\varphi\to0$ samo iz ustaljenja polova. Ni mali
$\varphi$, mali rezidual ili ustaljenje sami ne dokazuju lokalni ili globalni minimum
racionalnog cilja ni malu $\mathcal H_2$ ili $\mathcal H_\infty$ pogrešku.

Postojeći `detect_period` uspoređuje zadnji skup sa starijima pomoću uparivanja i
relativne udaljenosti normirane starijim skupom. Vraća kandidat za period, a ne odluku
o uspješnoj konvergenciji. Potreban broj ponavljanja, maksimalni broj iteracija,+tolerancije i postupak pri nekonvergenciji ostaju za B1/Z2. Primjer grede iz L1 ovdje
nije reproduciran; testovi provjeravaju male poznate modele i umjetne povijesti polova.

## 8. Provjere i granice implementacije

Novi testovi obuhvaćaju:

- jedan korak za $H(s)=2/(s+1)$ s očekivanim $\phi=2$, $\varphi=-2$ uz pomoćni pol $-3$;
- oporavak $(s+5)/(s^2+2s+5)+3/(s+8)$, uključujući konjugirani par i različite poretke;
- neovisno faktoriziran nazivnik drugog reda, nulte reziduale nazivnika i višestruke korijene;
- analitički težinski fit jednog realnog reziduala i stacionarnost lineariziranog cilja;
- realnost, nestabilne rezultate, unitarnu težinu zrcaljenja samo na imaginarnoj osi;
- nevaljane ulaze, preljev, bliske polove i prijavu gubitka ranga, uključujući nulte podatke
  kod kojih nulti LS rezidual ne znači da su polovi određeni.

`barycentric_step`, `relocate_poles`, `reflect_unstable_poles` i `fit_fixed_poles` pojedinačne
su operacije. Još nema petlje VF-a, automatskog zrcaljenja, kriterija zaustavljanja ni
pokretača eksperimenta A7. Nisu odabrani početni polovi, čvorovi, redovi ni konačni pojas.
Realni negativni polovi s pozitivnim rezidualima svojstvo su koje treba provjeriti na
svakom rezultatu; L1 ga ne jamči. Konjugirano uparen model realan je, ali nije nužno
Debyejev model s isključivo realnim polovima.
