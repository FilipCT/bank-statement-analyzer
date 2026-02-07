# AI Development Workflow – 3 Amigos Model

Ovaj dokument opisuje kako se koristi kombinacija:
- čovek (vlasnik ideje),
- arhitektonska validacija,
- i Claude Code (AI implementer)

za razvoj aplikacija na održiv i kontrolisan način.

Cilj je:
- izbeći overengineering,
- poštovati realna ograničenja frameworka,
- imati jasan trag odluka (decision log),
- i koristiti AI kao multiplikator, ne kao vođu.

---

## 1. Osnovni koncept – 3 Amigos (bez GWT)

Ne koristi se Given/When/Then formalizam.
Koristi se **3 Amigos koncept kao razgovorni i odlučivački model**.

### Uloge

#### 🧑‍💼 Amigo 1 – Product / Owner (čovek)
- Ima ideju ili problem
- Zna *zašto* se nešto pravi
- Definiše granice, non-goals i očekivanja
- Donosi konačne odluke

#### 🧭 Amigo 2 – Architecture / Reality Check (ChatGPT)
- Ne piše kod
- Ne implementira feature-e
- Validira **odluke**, ne linije koda
- Postavlja granice i upozorava na:
  - framework ograničenja
  - budući tehnički dug
  - pogrešne apstrakcije
- Seče opcije i daje presudu (šta NE raditi)

#### 🤖 Amigo 3 – Implementer (Claude Code)
- Piše kod
- Refaktoriše
- Sledi instrukcije
- Radi u compound režimu (plan → work → review)
- Ne donosi proizvodne ili arhitektonske odluke

---

## 2. Zašto Claude Code ne vodi arhitekturu

Claude Code, čak i uz compound engineering:

- teži generalnim rešenjima
- favorizuje apstrakciju i “best practices”
- nudi opcije umesto da ih seče
- nema osećaj dugoročnog bola (technical debt)

Zbog toga:
- nije pouzdan kao arhitekta
- nije dobar u definisanju granica
- često predlaže rešenja koja su “lepa”, ali nepraktična

Claude je **odličan izvršilac**, ali slab donosilac odluka.

---

## 3. Ograničenja Claude Code-a (koja se moraju eksplicitno navesti)

Claude uvek mora raditi uz sledeće pretpostavke (ako nisu navedene, on će ih ignorisati):

- Framework ima realna ograničenja (npr. Streamlit rerun model)
- Nema event-driven UI
- Nema fine kontrole nad lifecycle-om
- session_state mora biti minimalan
- skupe operacije moraju biti keširane
- filesystem može biti ephemeral
- nema background job-ova
- nema “kasnije ćemo to srediti”

Ako se ova ograničenja ne navedu — Claude će ih prekršiti.

---

## 4. Uloga arhitektonske validacije (ChatGPT)

Arhitektonska validacija:
- NE zahteva pristup kodu
- NE zahteva diff
- NE zahteva review svake linije

Validira se:
- **pravac**
- **odluke**
- **mentalni model**
- **poštovanje ograničenja**

Drugim rečima:
> Validira se *kako se razmišlja*, ne *šta je napisano*.

---

## 5. Artefakti koje Claude mora da proizvodi

Da bi validacija bila moguća bez čitanja koda, Claude mora da ostavlja **decision artifacts**.

Minimalni set:

### 5.1 PLAN.md
Dokument koji opisuje **šta se planira pre nego što se piše kod**.

Obavezni delovi:
- Goal
- Constraints
- Proposed Changes
- Out of Scope

### 5.2 WORK.md
Dokument koji opisuje **šta je stvarno urađeno**.

Obavezni delovi:
- Changes Made
- Deviations from Plan
- Open Questions

### 5.3 REVIEW.md
Claude-ov self-review iz arhitektonske perspektive.

Obavezni fokus:
- hidden risks
- framework anti-patterns
- potencijalni tehnički dug
- stvari koje mogu pući kasnije

---

## 6. Kako izgleda kompletan workflow

1. Čovek ima ideju ili problem
2. Čovek + ChatGPT vode **planning razgovor**
3. Iz razgovora se formira **Project / Feature Brief**
4. Claude dobija:
   - jasan zadatak
   - jasna ograničenja
   - obavezu da proizvede PLAN / WORK / REVIEW
5. Claude radi u compound režimu
6. Čovek uzima `.md` fajlove
7. ChatGPT validira:
   - odluke
   - pravac
   - rizike
8. Čovek odlučuje:
   - merge
   - korekcija
   - rollback

Kod se tretira kao **izvedeni artefakt**, ne kao izvor istine.

---

## 7. Zašto ovaj model radi

- sprečava prerano kodiranje
- sprečava AI overengineering
- daje trag odluka kroz vreme
- omogućava arhitektonsku validaciju bez pristupa kodu
- skalira od solo projekta do kompleksnijih sistema

Najvažnije:
> AI se koristi kao **alat**, ne kao autor.

---

## 8. Ključna rečenica ovog dokumenta

> Arhitektura je skup donetih odluka.  
> Kod je samo trenutna implementacija tih odluka.

Ako su odluke zdrave, kod se može popraviti.  
Ako su odluke loše, kod će uvek stvarati problem.

---

Kraj dokumenta.