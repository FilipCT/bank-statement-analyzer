# Troškomer 📊

Aplikacija za analizu bankovnih izvoda iz Banca Intesa banke. Parsira PDF izvode, automatski kategorizuje transakcije i prikazuje statistiku potrošnje.

## Stranice aplikacije

### 🏠 Početna (Ukupna statistika)
- Rang lista kategorija sortirana po maksimalnoj potrošnji
- Za svaku kategoriju: max iznos, prosek, top brend
- "Gde najviše trošiš?" highlight sekcija
- Export u Excel (svi izvodi)

### 📂 Izvodi
- Upload PDF izvoda iz Banca Intesa
- Pregled sačuvanih izvoda (grupisano po godinama)
- Brisanje pojedinačnih ili svih izvoda
- Rekategorizacija svih izvoda

### 📅 Mesečni prikaz
- Navigacija po mesecima (prev/next kartice)
- Kategorije sa iznosima (expandable)
- Brendovi unutar svake kategorije
- Pojedinačne transakcije u tabeli
- Bilans na dnu (primanja, potrošnja, bilans)
- **Mapiranje iz "Ostalo"** - direktno mapiranje nekategorisanih transakcija
- Export u Excel

### ⚙️ Podešavanja
- Upravljanje kategorijama i ključnim rečima
- Upravljanje brendovima i varijantama
- Pregled nemapranih trgovaca
- Reset na podrazumevane vrednosti

## Kako radi kategorizacija i mapiranje

### Dva koncepta

| Koncept | Svrha | Gde se podešava |
|---------|-------|-----------------|
| **Kategorija** | U koju grupu spada transakcija (Marketi, Restorani...) | Podešavanja → Kategorije |
| **Brend** | Kako se prikazuje naziv trgovca | Podešavanja → Mapiranje brendova |

### Tok kategorizacije

```
Transakcija: "LIDL CACAK 123"
     │
     ▼
┌─────────────────────────────────────┐
│ 1. KATEGORIZACIJA                   │
│    Traži ključnu reč u tekstu       │
│    "LIDL" pronađeno → 🛒 Marketi    │
└─────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────┐
│ 2. NORMALIZACIJA BRENDA             │
│    Traži varijantu u tekstu         │
│    "LIDL" pronađeno → prikaži LIDL  │
└─────────────────────────────────────┘
     │
     ▼
Rezultat: Kategorija "🛒 Marketi", Brend "LIDL"
```

### Mapiranje novog trgovca

Kada se pojavi nov trgovac (npr. `KAFANACACAK 688`):

1. **Pojavljuje se u "❓ Ostalo"** jer nema ključnu reč koja ga prepoznaje

2. **Mapiranje iz Mesečnog prikaza:**
   - Otvori "❓ Ostalo" kategoriju
   - Pronađi trgovca
   - Unesi jednostavnu ključnu reč: `KAFANA`
   - Izaberi kategoriju: `🍔 Restorani i dostava`
   - Unesi naziv brenda: `KAFANA ČAČAK`
   - Klikni "Mapiraj"

3. **Šta se dešava:**
   - Ključna reč `KAFANA` se dodaje u kategoriju "Restorani"
   - Brend `KAFANA ČAČAK` se kreira sa varijantom `KAFANA`
   - Svi izvodi se automatski rekategorizuju
   - Transakcija se premešta iz "Ostalo" u "Restorani"

### Saveti za mapiranje

- **Ključna reč** treba da bude što kraća i jedinstvena
  - ✅ Dobro: `KAFANA`, `LIDL`, `WOLT`
  - ❌ Loše: `KAFANACACAK 688 BEOGRAD` (previše specifično)

- **Brend** je naziv koji će se prikazivati
  - Može biti čitljiviji od originala
  - Npr. `JKP VODOVOD` umesto `"VODOVOD"JKP CACAK 123`

## Podešavanja kategorija

### Dodavanje nove kategorije
1. Idi na ⚙️ Podešavanja → Kategorije
2. Unesi naziv (npr. `🎮 Gaming`)
3. Unesi prvu ključnu reč (npr. `STEAM`)
4. Klikni "Dodaj kategoriju"

### Izmena postojeće kategorije
1. Otvori expander kategorije
2. Izmeni naziv ili ključne reči
3. Klikni "💾 Sačuvaj sve izmene"
4. Automatski se rekategorizuju svi izvodi

## Podešavanja brendova

### Dodavanje novog brenda
1. Idi na ⚙️ Podešavanja → Mapiranje brendova
2. Unesi naziv brenda (npr. `JKP VODOVOD`)
3. Unesi varijantu (npr. `VODOVOD`)
4. Opciono izaberi kategoriju
5. Klikni "Dodaj brend"

### Nemapirani trgovci
Na dnu stranice Podešavanja nalazi se lista trgovaca koji se pojavljuju u transakcijama ali nemaju mapiranje. Odatle možeš:
- **➕ Novi brend** - kreira brend sa nazivom trgovca
- **📎 Postojeći** - dodaje kao varijantu postojećeg brenda

## Struktura podataka

```
data/
├── categories.json      # Kategorije i ključne reči
├── brand_mapping.json   # Brendovi i varijante
└── statements/
    ├── 2025-08/
    │   ├── transactions.csv
    │   ├── metadata.json
    │   └── statement.pdf
    ├── 2025-09/
    └── ...
```

### categories.json
```json
{
  "🛒 Marketi": ["LIDL", "MAXI", "IDEA", "TEMPO"],
  "🍔 Restorani i dostava": ["WOLT", "GLOVO", "KAFANA"],
  ...
}
```

### brand_mapping.json
```json
{
  "LIDL": ["LIDL", "LIDL CACAK", "LIDL123"],
  "KAFANA ČAČAK": ["KAFANA", "KAFANACACAK"],
  ...
}
```

## Tehnički stack

- **Python 3.10+**
- **Streamlit** - web framework
- **pdfplumber** - parsiranje PDF-a
- **pandas** - obrada podataka
- **xlsxwriter** - Excel export

## Instalacija

```bash
# Kloniraj repo
git clone https://github.com/FilipCT/bank-statement-analyzer.git
cd bank-statement-analyzer

# Kreiraj virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ili: venv\Scripts\activate  # Windows

# Instaliraj dependencies
pip install -r requirements.txt

# Pokreni aplikaciju
streamlit run app.py
```

## Deployment na Streamlit Cloud

1. Push kod na GitHub (privatni repo preporučen)
2. Idi na [share.streamlit.io](https://share.streamlit.io)
3. Poveži GitHub nalog
4. Odaberi repo i `app.py`
5. Deploy!

### Čuvanje podataka na Streamlit Cloud
- Podaci se čuvaju u `data/` folderu
- Na Streamlit Cloud, filesystem je ephemeral (briše se pri redeploy-u)
- Za trajno čuvanje: commit `data/` folder u repo

## Responsive dizajn

Aplikacija je prilagođena za mobilne uređaje:
- Kompaktni prikaz na malim ekranima
- Scrollable tabele
- Touch-friendly expanders

## Autor

Filip Milićević

## Licenca

Privatni projekat - samo za ličnu upotrebu.
