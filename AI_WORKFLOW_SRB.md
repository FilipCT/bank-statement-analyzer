# AI Development Workflow – 3 Amigos Model

Ovaj dokument opisuje praktičan i ponovljiv način razvoja aplikacija korišćenjem kombinacije:
- čoveka (vlasnika ideje),
- arhitektonske validacije,
- i Claude Code-a (AI implementera).

Ciljevi ovog workflow-a su:
- izbegavanje overengineering-a,
- poštovanje realnih ograničenja frameworka,
- jasan i trajan trag odluka,
- korišćenje AI-ja kao multiplikatora, a ne kao vođe.

Ovaj workflow je **odlukama vođen**, a ne chat-om vođen.

---

## 1. Osnovni koncept – 3 Amigos (bez GWT)

Ovaj workflow ne koristi Given/When/Then formalizam.  
Umesto toga, koristi **3 Amigos koncept** kao razgovorni i odlučivački model.

Fokus je na:
- zajedničkom razumevanju
- ranom razjašnjavanju ograničenja
- sečenju pogrešnih opcija na vreme
- donošenju odluka pre pisanja koda

---

## 2. Uloge i odgovornosti

### Amigo 1 – Product / Owner (Čovek)

- Ima ideju ili problem
- Zna zašto se nešto pravi
- Daje domen znanje i prioritete
- Definiše granice, non-goals i očekivanja
- Donosi konačne odluke i prihvata trade-off-ove

Ova uloga je **izvor istine** za smisao i vrednost.

---

### Amigo 2 – Arhitektura / Reality Check (ChatGPT)

- Ne piše kod
- Ne implementira feature-e
- Validira **odluke**, ne linije koda
- Čuva dugoročno razmišljanje i ograničenja
- Identifikuje:
  - skrivene rizike
  - ograničenja frameworka
  - budući tehnički dug
  - pogrešne apstrakcije
- Eksplicitno seče opcije i govori šta **NE treba raditi**

Fokus ove uloge je **pravac**, a ne implementacija.

---

### Amigo 3 – Implementer (Claude Code)

- Piše kod
- Refaktoriše
- Prati eksplicitna uputstva
- Radi u compound režimu (plan → work → review)
- Proizvodi decision artefakte (PLAN / WORK / REVIEW)
- Ne donosi proizvodne ni arhitektonske odluke

Claude Code je **izvršilac**, ne autor.

---

## 3. Zašto Claude Code ne treba da vodi arhitekturu

Čak i uz compound engineering, Claude Code:
- teži generalnim rešenjima
- favorizuje apstrakciju i “best practices”
- nudi opcije umesto da ih seče
- optimizuje eleganciju, ne održivost
- nema iskustveni osećaj tehničkog duga

Zbog toga:
- nije pouzdan arhitekta
- loše definiše granice
- često predlaže tehnički ispravna, ali praktično loša rešenja

Claude je odličan u **implementaciji**, ne u **presuđivanju**.

---

## 4. Ograničenja za Claude Code (moraju biti eksplicitna)

Claude uvek mora da radi pod **jasno napisanim ograničenjima**.  
Ako ih nema – on će ih sam izmisliti.

Tipična ograničenja:
- framework ima realna ograničenja (npr. Streamlit rerun model)
- nema event-driven UI-a
- nema fine kontrole lifecycle-a
- session_state mora biti minimalan
- skupe operacije moraju biti keširane
- filesystem može biti ephemeral
- nema background job-ova
- nema “sredićemo kasnije” pretpostavki

Ako ograničenja nisu eksplicitna, Claude će ih prekršiti.

---

## 5. Brainstorm faza – pravilna upotreba

Claude Code ima Brainstorm fazu koja je korisna, ali opasna ako se loše koristi.

### Šta Brainstorm JESTE
- divergentna faza razmišljanja
- služi za istraživanje alternativnih pristupa
- optimizovana za širinu, ne tačnost

### Šta Brainstorm NIJE
- donošenje odluka
- definisanje scope-a
- vlasništvo nad arhitekturom
- prioritizacija feature-a

### Ispravan redosled

1. Čovek ima ideju / problem  
2. Čovek + ChatGPT definišu problem i ograničenja  
3. Claude brainstorm-uje unutar granica  
4. ChatGPT seče opcije i bira pravac  
5. Claude planira (compound)  
6. Claude implementira i radi review  

Brainstorm je dozvoljen **samo unutar jasno definisanog okvira**.

### Pravila za Brainstorm
- ne širi scope
- ne dodaje feature-e
- ne menja arhitektonske pretpostavke
- jasno navodi trade-off-ove i rizike

Brainstorm bez ljudske presude je informativan, nikad autoritativan.

---

## 6. Arhitektonska validacija (ChatGPT)

Arhitektonska validacija **nije** code review.

ChatGPT:
- ne mora da vidi repo
- ne čita diff-ove
- ne pregleda liniju po liniju

Validira se:
- pravac
- donesene odluke
- mentalni model
- poštovanje ograničenja
- dugoročni rizici

Validira se **kako se razmišlja**, ne **šta je napisano**.

---

## 7. Decision artefakti kao izvor istine

Chat sesije su prolazne.  
Dokumenti su trajni.

Nijedan bitan kontekst ne sme da živi samo u chatu.

Claude uvek mora da proizvede:

PLAN.md  
- namera pre pisanja koda  
- cilj, ograničenja, predložene izmene, van opsega  

WORK.md  
- šta je stvarno urađeno  
- odstupanja i otvorena pitanja  

REVIEW.md  
- self-review  
- rizici, anti-patterni, tehnički dug  

Ovi dokumenti omogućavaju validaciju bez pristupa kodu.

---

## 8. Sesije vs Dokumenti

Chat sesije mogu isteći ili nestati.  
Dokumenti su jedina pouzdana memorija.

Pravila:
- nikad se ne oslanjati samo na chat
- odluke uvek zapisivati
- dokumente tretirati kao kanonski input

Kanonski dokumenti:
- AI_WORKFLOW.md – kako radimo
- PROJECT_BRIEF.md – šta gradimo
- Feature / decision log dokumenti

---

## 9. Uloga ChatGPT-a kroz sesije

ChatGPT nije dugoročna memorija.  
ChatGPT je arhitektonski reviewer i partner u odlučivanju.

Kada dobije dokumente, ChatGPT može:
- rekonstruisati ceo kontekst
- validirati odluke
- otkriti rizike
- predložiti korekcije

Kontinuitet je **dokument-baziran**, ne sesija-baziran.

---

## 9.1 ChatGPT kao kreator dokumentacije

ChatGPT ne samo da review-uje odluke,  
već aktivno pomaže u **kreiranju i održavanju dokumentacije**.

ChatGPT može da pravi:
- Project Brief-ove
- Feature Brief-ove
- Decision log-ove
- Arhitektonske beleške
- Definicije ograničenja
- Procene rizika

Ovi dokumenti su:
- čitljivi ljudima
- stabilni
- prenosivi između sesija
- kanonska memorija projekta

---

## 10. Sažetak kompletnog workflow-a

1. Čovek ima ideju ili problem  
2. Čovek + ChatGPT razjašnjavaju problem i ograničenja  
3. Kontekst se zapisuje u Project / Feature Brief  
4. Claude brainstorm-uje u okviru granica  
5. ChatGPT bira pravac  
6. Claude planira (compound)  
7. Claude implementira i review-uje  
8. Claude proizvodi PLAN / WORK / REVIEW  
9. ChatGPT validira odluke  
10. Čovek odlučuje: merge, izmena ili rollback  

Kod je izvedeni artefakt, ne izvor istine.

---

## 11. Zašto ovaj workflow radi

- sprečava prerano pisanje koda
- sprečava AI overengineering
- tera eksplicitno odlučivanje
- ostavlja trajan trag razmišljanja
- radi kroz više sesija
- skaluje od malih alata do većih sistema

AI je alat, ne autor.

---

## 12. Osnovni princip

Arhitektura je skup donetih odluka.  
Kod je samo trenutna implementacija tih odluka.

Ako su odluke dobre, kod se može popraviti.  
Ako su odluke loše, kod će uvek praviti problem.

---

Kraj dokumenta.