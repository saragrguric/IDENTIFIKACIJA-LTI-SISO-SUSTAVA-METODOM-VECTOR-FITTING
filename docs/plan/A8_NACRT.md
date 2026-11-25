# A8: predaja teorijskog nacrta za Overleaf

**Stanje 2026-11-23: pripremljen prvi nacrt, ne završen seminar.** Na grani
`lovro/a8-nacrt` vodi se zapis predaje. Sam tekst seminara ostaje izvan repozitorija,
prema dogovoru Z0. Lokalni samostalni izvor zove se **vf-seminar-nacrt.tex**, s naslovom
„Identifikacija LTI SISO sustava metodom vector fitting: Debyejeva aproksimacija
Cole–Coleovih modela ljudskih tkiva”. Datoteka je priložena razgovoru u kojem je nastala;
prije nastavka zajedničkog pisanja treba je prenijeti u dogovoreni Overleaf projekt.
Repozitorij ne ovisi o osobnoj apsolutnoj putanji te datoteke.

SHA-256 ove inačice izvora:
`f70c597c3c4fa57886d948c77df7b116d4d1e1d6cc403719985175895eea87ef`.

## Sadržaj koji je već napisan

- Problem, jedinice i konstitutivna veza za efektivnu permitivnost, uz izdvojenu vodljivost.
- Gabrielov model, podrijetlo tablice, duplikati i razlika modelskih podataka i novih mjerenja.
- Predmet prilagodbe H, veza Cole–Coleova i Debyejeva člana te uvjeti za fizikalnu relaksaciju.
- Racionalna funkcija cilja, nekonveksnost, Levyjeva linearizacija i SK iteracija.
- Polinomni i baricentrični LS, vlastita provjera normalizacija i točno riješen primjer r = 1.
- Premještanje polova, lema o determinanti i provjera predznaka; apsorpcija SK težine.
- Realna parametrizacija, uvjetovanost, refleksija i završni reziduali.
- Uparivanje polova, ocjene promjene baze/nazivnika i ograničenja zaključivanja o konvergenciji.
- Veza s punom H2 normom, normom na pojasu, kvadraturom i dvjema prihvaćenim mjerama pogreške.
- Veza s postojećim operacijama koda, zahtjevi podrijetla i pitanja za neovisni pregled.

Matematička podloga su [A3](../izvodi/a3-problem-sk.md),
[A5](../izvodi/a5-polovi-reziduali.md) i most prema [B2](../izvodi/b2-h2-kvadratura.md).
Bibliografija je samostalna: L1 je jedini izvor metode, a D1 izvor podataka preko prijepisa
WebNIR. Radovi koje L1 citira nisu dodani kao neovisno pročitani izvori. Algebarske dopune
označene su kao vlastite, bez pripisivanja teorema izvornom radu.

Nacrt je jedna datoteka bez dodatnog BibTeX-a, slika i ulaznih datoteka. Može se prenijeti
kao samostalan početni dokument. Pri uključivanju u postojeći Overleaf rukopis prenosi se
tijelo, usklađuju oznake jednadžbi i citatni ključevi te izostavlja ponovljena preambula.
Za taj prijenos nije provedena radnja u tuđem Overleaf računu; povezani projekt nije zadan.

## Što još nije dovršeno

A8 konačno ovisi o A3–A7. Teorija se može pripremiti prije pune petlje A4, ali rezultati
na tkivima, analiza iteracija A7, tablice i zaključak ostaju otvoreni. Konačne postavke Z2
nisu prihvaćene. U nacrtu nema izmišljenih vrijednosti pogreške, slika, pobjedničke metode
ni tvrdnje o najmanjem mogućem redu.

Za prihvat ostaju Sarin neovisni pregled B9, stvarni zajednički prolaz, spajanje s
poglavljima niti B i Z5. Popis pitanja u dodatku priprema razgovor; nije zapis da je itko
već potvrdio razumijevanje ili odobrio tekst. Nacrt slajdova A10 slijedi nakon sadržajno
usklađenog A8.

## Provjera i ograničenja

Provjerene su reference na postojeće izvode, nazivi operacija i identitet lokalnog CSV-a.
Brojke o ulazu (57 naziva, 55 disperzivnih i 41 različit disperzivni skup) nisu predstavljene
kao rezultati VF pokusa. Teorijski primjeri već imaju podlogu u provjerama A3/A5/B2.

Izvor je poslan ugrađenom LaTeX editoru. Pokušaj kompilacije nije uspio: Tectonic nema
predmemoriran paket i ne može ga dohvatiti s poslužitelja. Zato **PDF i izgled stranica
nisu potvrđeni**. Datoteka ostaje sačuvana za editor/Overleaf; nije instaliran zamjenski
TeX sustav i nema tvrdnje da je tekst u Overleafu objavljen. Nakon dostupnosti kompajlera
treba ponoviti kompilaciju i vizualno pregledati sve stranice.

Promjena slijedi retke protokola za matematički tekst, stanje zadatka i novi dokument.
Ne mijenja metodu, kod, rezultate, ovisnosti ni prihvaćene odluke.
`python3 tools/check_before_stop.py` prolazi: 242 numerička testa uz lokalnu tablicu,
49 testova alata, Ruff i provjera dokumentacije. `git diff --check` nema nalaza.
Statička provjera LaTeX izvora nije našla nepovezane unutarnje reference, ponovljene oznake
ni nezatvorene okoline; primjer reda jedan potvrđen je izravnim računom.
To ne nadomješta kompilaciju, vizualni, znanstveni ni ljudski pregled.
