import streamlit as st
import pdfplumber
import pandas as pd
import re
import json
import os
from io import BytesIO
from datetime import datetime
from pathlib import Path
import xlsxwriter


# Page config
st.set_page_config(
    page_title="Troškomer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Intesa-style CSS
st.markdown("""
<style>
    /* ===== GLOBAL STYLES ===== */
    .main .block-container {
        padding-top: 1rem !important;
        max-width: 100% !important;
    }

    /* ===== DARK SIDEBAR (Intesa style) ===== */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%) !important;
        padding-top: 0 !important;
    }
    section[data-testid="stSidebar"] > div {
        padding-top: 1rem !important;
    }
    section[data-testid="stSidebar"] .stMarkdown,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] .stRadio label,
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] span {
        color: white !important;
    }
    section[data-testid="stSidebar"] hr {
        border-color: rgba(255,255,255,0.2) !important;
    }
    /* Sidebar navigation buttons */
    section[data-testid="stSidebar"] .stButton button {
        background: transparent !important;
        border: none !important;
        color: rgba(255,255,255,0.7) !important;
        text-align: left !important;
        padding: 12px 16px !important;
        font-size: 15px !important;
        font-weight: 500 !important;
        border-radius: 8px !important;
        transition: all 0.2s ease !important;
    }
    section[data-testid="stSidebar"] .stButton button:hover {
        background: rgba(255,255,255,0.1) !important;
        color: white !important;
    }
    section[data-testid="stSidebar"] .stButton button[kind="primary"] {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.4) 0%, rgba(118, 75, 162, 0.4) 100%) !important;
        border-left: 3px solid #667eea !important;
        color: white !important;
    }
    section[data-testid="stSidebar"] .stButton button[kind="primary"]:hover {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.5) 0%, rgba(118, 75, 162, 0.5) 100%) !important;
    }

    /* Google Font import - Financial style */
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600&display=swap');

    /* Sidebar logo */
    .sidebar-logo {
        display: flex;
        align-items: center;
        gap: 16px;
        padding: 20px 0;
        margin-bottom: 12px;
    }
    .sidebar-logo-text {
        font-family: 'Playfair Display', serif;
        font-size: 34px;
        font-weight: 600;
        color: white !important;
        letter-spacing: 0.5px;
        text-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
    }
    .sidebar-subtitle {
        font-size: 13px;
        color: rgba(255,255,255,0.7) !important;
        margin-top: -8px;
        letter-spacing: 0.5px;
    }

    /* Navigation menu items */
    .nav-item {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 14px 16px;
        margin: 4px 0;
        border-radius: 8px;
        cursor: pointer;
        transition: all 0.2s;
        color: rgba(255,255,255,0.8);
    }
    .nav-item:hover {
        background: rgba(255,255,255,0.1);
        color: white;
    }
    .nav-item.active {
        background: rgba(102, 126, 234, 0.3);
        color: white;
        border-left: 3px solid #667eea;
    }
    .nav-icon {
        font-size: 20px;
        width: 24px;
        text-align: center;
    }
    .nav-text {
        font-size: 15px;
        font-weight: 500;
    }

    /* ===== FANCY CATEGORY EXPANDERS ===== */
    .main [data-testid="stExpander"] {
        background: linear-gradient(135deg, #f8f9ff 0%, #fff5f5 100%);
        border-radius: 16px;
        border: none;
        box-shadow: 0 2px 12px rgba(102, 126, 234, 0.08);
        margin-bottom: 14px;
        overflow: hidden;
        transition: all 0.3s ease;
    }
    .main [data-testid="stExpander"]:hover {
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.15);
        transform: translateY(-2px);
    }
    .main [data-testid="stExpander"] summary {
        padding: 18px 24px;
        font-size: 16px;
        font-weight: 500;
        border-left: 4px solid #667eea;
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.08) 0%, rgba(118, 75, 162, 0.08) 100%);
    }
    .main [data-testid="stExpander"] summary:hover {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.15) 0%, rgba(118, 75, 162, 0.15) 100%);
    }
    .main [data-testid="stExpander"] summary span {
        font-size: 16px !important;
    }
    .main [data-testid="stExpander"] [data-testid="stExpanderDetails"] {
        padding: 16px 24px;
        background: white;
    }

    /* ===== INTESA CARD STYLE ===== */
    .intesa-card {
        background: white;
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 16px;
        box-shadow: 0 2px 12px rgba(0,0,0,0.08);
        border: 1px solid #f0f0f0;
    }
    .intesa-card-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        margin-bottom: 16px;
    }
    .intesa-card-title {
        font-size: 14px;
        color: #666;
        margin: 0;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .intesa-card-amount {
        font-size: 32px;
        font-weight: 700;
        color: #1a1a2e;
        margin: 8px 0;
    }
    .intesa-card-subtitle {
        font-size: 13px;
        color: #888;
    }
    .intesa-card-row {
        display: flex;
        justify-content: space-between;
        padding: 12px 0;
        border-bottom: 1px solid #f5f5f5;
    }
    .intesa-card-row:last-child {
        border-bottom: none;
    }
    .intesa-card-label {
        color: #666;
        font-size: 14px;
    }
    .intesa-card-value {
        font-weight: 600;
        color: #1a1a2e;
    }

    /* ===== STATS CARDS ===== */
    .stat-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 16px;
        padding: 20px;
        color: white;
        margin-bottom: 16px;
    }
    .stat-card-light {
        background: white;
        border-radius: 16px;
        padding: 20px;
        box-shadow: 0 2px 12px rgba(0,0,0,0.08);
        border: 1px solid #f0f0f0;
        margin-bottom: 16px;
    }
    .stat-label {
        font-size: 12px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        opacity: 0.8;
        margin-bottom: 4px;
    }
    .stat-value {
        font-size: 28px;
        font-weight: 700;
    }
    .stat-subtitle {
        font-size: 12px;
        opacity: 0.7;
        margin-top: 4px;
    }

    /* ===== PAGE HEADER ===== */
    .page-header {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 24px;
        padding-bottom: 16px;
        border-bottom: 1px solid #eee;
    }
    .page-title {
        font-size: 24px;
        font-weight: 700;
        color: #1a1a2e;
        margin: 0;
    }

    /* ===== TRANSACTION LIST ===== */
    .transaction-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 16px;
        border-bottom: 1px solid #f5f5f5;
    }
    .transaction-item:hover {
        background: #fafafa;
    }
    .transaction-info {
        display: flex;
        flex-direction: column;
        gap: 4px;
    }
    .transaction-merchant {
        font-weight: 600;
        color: #1a1a2e;
    }
    .transaction-category {
        font-size: 12px;
        color: #888;
    }
    .transaction-amount {
        font-weight: 600;
        color: #ef4444;
    }
    .transaction-amount.income {
        color: #10b981;
    }

    /* ===== WELCOME SECTION ===== */
    .welcome-section {
        margin-bottom: 24px;
    }
    .welcome-badge {
        display: inline-block;
        background: #e8f4fd;
        color: #1a73e8;
        padding: 4px 12px;
        border-radius: 12px;
        font-size: 12px;
        margin-bottom: 8px;
    }
    .welcome-text {
        font-size: 14px;
        color: #666;
    }
    .welcome-name {
        font-size: 24px;
        font-weight: 700;
        color: #1a1a2e;
    }

    /* ===== SELECTBOX CURSOR FIX ===== */
    .stSelectbox > div > div {
        cursor: pointer !important;
    }
    .stSelectbox input {
        cursor: pointer !important;
        caret-color: transparent !important;
    }

    /* ===== MONTH NAVIGATION - RESPONSIVE ===== */
    @media (max-width: 768px) {
        /* Smaller, nicer buttons on mobile */
        .main .stButton button[kind="secondary"] {
            font-size: 12px !important;
            padding: 10px 14px !important;
            border-radius: 20px !important;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
            border: none !important;
            color: white !important;
            box-shadow: 0 2px 8px rgba(102, 126, 234, 0.2) !important;
        }
    }

    /* ===== RESPONSIVE ===== */
    @media (max-width: 768px) {
        .intesa-card-amount {
            font-size: 24px;
        }
        .stat-value {
            font-size: 22px;
        }
        .page-title {
            font-size: 20px;
        }
    }
</style>
<script>
    // Auto-collapse sidebar on mobile after navigation (Safari compatible)
    (function() {
        function isMobile() {
            return window.innerWidth <= 768;
        }

        function collapseSidebar() {
            if (!isMobile()) return;

            // Try multiple selectors for Streamlit sidebar close button
            var selectors = [
                'button[data-testid="baseButton-headerNoPadding"]',
                'button[aria-label="Close sidebar"]',
                'section[data-testid="stSidebar"] button[kind="header"]',
                '[data-testid="stSidebarCollapsedControl"]'
            ];

            for (var i = 0; i < selectors.length; i++) {
                var btn = document.querySelector(selectors[i]);
                if (btn) {
                    btn.click();
                    return;
                }
            }

            // Fallback: try to find any close-like button in sidebar header
            var sidebar = document.querySelector('section[data-testid="stSidebar"]');
            if (sidebar) {
                var headerBtn = sidebar.querySelector('button');
                if (headerBtn) {
                    headerBtn.click();
                }
            }
        }

        // Listen for clicks on sidebar
        document.addEventListener('click', function(e) {
            var target = e.target;
            // Check if click was on a sidebar button
            while (target && target !== document) {
                if (target.tagName === 'BUTTON') {
                    var sidebar = document.querySelector('section[data-testid="stSidebar"]');
                    if (sidebar && sidebar.contains(target)) {
                        if (isMobile()) {
                            setTimeout(collapseSidebar, 200);
                        }
                        return;
                    }
                }
                target = target.parentNode;
            }
        }, true);
    })();
</script>
""", unsafe_allow_html=True)


# Data storage folder
DATA_DIR = Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)
STATEMENTS_DIR = DATA_DIR / "statements"
STATEMENTS_DIR.mkdir(exist_ok=True)
CATEGORIES_FILE = DATA_DIR / "categories.json"
BRAND_MAPPING_FILE = DATA_DIR / "brand_mapping.json"

# Default categories configuration (used for initialization)
DEFAULT_CATEGORIES = {
    "🏥 Apoteke": [
        "LILLY", "APOTEKA", "VIDAKOVI", "VUCKOVIC", "KRSENKOVIC", "BENU"
    ],
    "🩺 Zdravstveni pregledi i analize": [
        "MEDILAB", "DRPISCEVIC", "DR PISCEVIC", "MEDILEK", "MEDILEKCACAK", "NATASA RANDJELOVIC", "RANDJELOVICPR", "FIZIOKINETIKPR"
    ],
    "🛒 Marketi": [
        "LIDL", "TEMPO", "MERCATOR", "KMN", "MAXI", "IDEA", "RODA",
        "UNIVEREXPORT", "MESOVITE ROBE", "HARIZMA", "STKRJELENA", "STKR JELENA", "STR JELENA", "STRJELENA"
    ],
    "🧴 Drogerije": [
        "DM FILIJALA"
    ],
    "⛽ Gorivo": [
        "NIS", "BENZINSKA", "LUKOIL", "MOL", "OMV", "PETROL", "GAZPROM"
    ],
    "👗 Odeća i obuća": [
        "ZARA", "BERSHKA", "FASHION", "H&M", "PULL&BEAR",
        "STRADIVARIUS", "MASSIMO", "LC WAIKIKI", "NEW YORKER", "NEWYORKER", "C&A",
        "DEICHMANN", "OFFICE SHOES", "BUZZ", "SPORT VISION", "PLANETBIKE", "TOMTAILOR", "TOM TAILOR",
        "TAKKO", "TAKKOFASHION", "KIDSBEBA", "PLANETASPORT", "PLANETA SPORT",
        "JASMILPROD", "WOODLINE032"
    ],
    "📱 Računi i usluge": [
        "VODOVOD", "KOMUNALAC", "SRBIJAGAS", "A1 SRBIJA", "A1 265", "A1SRBIJA", "A1",
        "BROADBAND", "KABLOVSKE", "EPS", "INFOSTAN", "ELEKTRO",
        "BOR.DECE", "VRTIC", "PREDSKOLSK", "ALTAGROUP", "CORDIPS", "G.O.S.", "GENERALI",
        "NAKNADA", "ODRZAVANJE RACUNA", "MESECNO ODRZAVANJE", "STAMBENA"
    ],
    "🍔 Restorani i dostava": [
        "WOLT", "GLOVO", "DONESI", "BURRITO", "NICEFOODS", "RESTORAN",
        "CAFFE", "KAFE", "PICERIJA", "MCDONALDS", "KFC",
        "VELVET", "GALIJA", "CASTELLO", "GALLERY", "MORAVSKIALASI", "PEKARA", "PONS",
        "RICHARDGYROS", "ISHRANADOO", "ASIAFOODDOO", "ESSORRISO",
        "LANTERNACACAK", "KOFI", "KAFANAPALILULE"
    ],
    "💵 Gotovina (ATM)": [
        "ISPLATA GOTOVINE", "ATM"
    ],
    "🚗 Putarine": [
        "PUTEVI SRBIJE"
    ],
    "📚 Knjižare": [
        "LAGUNA", "VULKAN", "KNJIZARA", "DELFI"
    ],
    "💻 Tech i pretplate": [
        "APPLE.COM", "GOOGLE", "NETFLIX", "SPOTIFY", "OPENAI", "CHATGPT",
        "MICROSOFT", "ADOBE", "AMAZON"
    ],
    "🏠 Stanovanje": [
        "STAMBENA ZAJEDNICA", "ZAKUP", "KIRIJA"
    ],
    "⛷️ Sport i rekreacija": [
        "SKIJALISTA", "SKI SKOLA", "KOPAONIK", "ZLATIBOR", "FITNESS",
        "TERETANA", "SPORT"
    ],
    "💇 Lepota i nega": [
        "KOZMETICKI SALON", "FRIZERSKI", "SALON LEPOTE"
    ],
    "🦷 Zdravlje": [
        "STOM ORD", "STOMATOLOG", "ORDINACIJA"
    ],
    "🏦 Transferi": [
        "BEZGOTOVINSKI PRENOS"
    ],
    "💰 Primanja": [
        "NETO ZARADA", "NETO (OPJ", "NEOPOREZIVA PRIMANJA"
    ]
}


# Default brand normalization (used for initialization)
DEFAULT_BRAND_MAPPING = {
    "LIDL": ["LIDL"],
    "TEMPO": ["TEMPO", "214 - TEMPO", "214-TEMPO"],
    "MERCATOR": ["MERCATOR"],
    "KMN": ["KMN", "MESOVITE ROBE"],
    "MAXI": ["MAXI"],
    "IDEA": ["IDEA"],
    "LILLY APOTEKA": ["LILLY"],
    "APOTEKA VIDAKOVIĆ": ["VIDAKOVI", "OGRANAK APOTEKA"],
    "APOTEKA ČAČAK": ["APOTEKA CACAK"],
    "APOTEKA VUČKOVIĆ": ["VUCKOVIC"],
    "APOTEKA KRSENKOVIC": ["KRSENKOVIC"],
    "BENU APOTEKA": ["BENU"],
    "DM": ["DM FILIJALA", "DMFILIJALA"],
    "NIS": ["NIS"],
    "WOLT": ["WOLT"],
    "ZARA": ["ZARA"],
    "BERSHKA": ["BERSHKA"],
    "TAKKO FASHION": ["TAKKO", "TAKKOFASHION"],
    "FASHION COMPANY": ["FASHIONCOMPANY", "FASHION COMPANY"],
    "PLANET BIKE": ["PLANETBIKE", "PLANET BIKE"],
    "APPLE": ["APPLE.COM"],
    "OPENAI/CHATGPT": ["OPENAI", "CHATGPT"],
    "PUTEVI SRBIJE": ["PUTEVI SRBIJE"],
    "LAGUNA": ["LAGUNA"],
    "VULKAN": ["VULKAN"],
    "BANKOMAT PODIZANJE NOVCA": ["BANCA INTESA", "BANCAINTESA"],
    "UPLATA NA DEVIZNI RAČUN": ["PRODAJA"],
    "STAMBENA ZAJEDNICA": ["STAMBENA ZAJEDNICA", "STAMBENA"],
    "A1": ["A1 SRBIJA", "A1 265", "A1SRBIJA"],
    "STRUJA (ALTA GROUP)": ["ALTAGROUP"],
    "MATIČNE ĆELIJE (CORD IPS)": ["CORDIPS"],
    "GENERALI OSIGURANJE": ["G.O.S.", "GENERALI"],
    "AKSA": ["AKSA"],
    "STR JELENA": ["STKRJELENA", "STKR JELENA", "STR JELENA", "STRJELENA"],
    "ODRŽAVANJE RAČUNA": ["NAKNADA", "ODRZAVANJE RACUNA", "MESECNO ODRZAVANJE"],
    "MEDILAB": ["MEDILAB", "MEDILABCENTAR"],
    "VRTIĆ NEVEN": ["BOR.DECE", "VRTIC", "PREDSKOLSK", "PRIH.OD"],
}


# ===== CATEGORY & BRAND MANAGEMENT =====

def load_categories():
    """Load categories from JSON file, or initialize with defaults."""
    if CATEGORIES_FILE.exists():
        with open(CATEGORIES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        save_categories(DEFAULT_CATEGORIES)
        return DEFAULT_CATEGORIES.copy()


def save_categories(categories):
    """Save categories to JSON file."""
    with open(CATEGORIES_FILE, "w", encoding="utf-8") as f:
        json.dump(categories, f, ensure_ascii=False, indent=2)


def load_brand_mapping():
    """Load brand mapping from JSON file, or initialize with defaults."""
    if BRAND_MAPPING_FILE.exists():
        with open(BRAND_MAPPING_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        save_brand_mapping(DEFAULT_BRAND_MAPPING)
        return DEFAULT_BRAND_MAPPING.copy()


def save_brand_mapping(mapping):
    """Save brand mapping to JSON file."""
    with open(BRAND_MAPPING_FILE, "w", encoding="utf-8") as f:
        json.dump(mapping, f, ensure_ascii=False, indent=2)


# ===== HELPER FUNCTIONS =====

def parse_amount(value):
    """Parse amount string to float."""
    if pd.isna(value) or value == "" or value is None:
        return 0.0
    if isinstance(value, (int, float)):
        return float(value)
    cleaned = str(value).replace("\n", "").replace(" ", "")
    cleaned = cleaned.replace(".", "").replace(",", ".")
    try:
        return float(cleaned)
    except ValueError:
        return 0.0


def categorize_transaction(description, merchant):
    """Categorize a transaction based on description and merchant name."""
    desc_upper = str(description).upper().strip()
    text = f"{description} {merchant}".upper()

    if desc_upper == "PRODAJA":
        return "💱 Menjačnica"

    categories = load_categories()
    for category, keywords in categories.items():
        for keyword in keywords:
            if keyword.upper() in text:
                return category

    return "❓ Ostalo"


def normalize_merchant(merchant, description=""):
    """Normalize merchant name to a common brand."""
    merchant_upper = str(merchant).upper()
    desc_upper = str(description).upper()
    text = f"{merchant_upper} {desc_upper}"

    brand_mapping = load_brand_mapping()
    for brand, keywords in brand_mapping.items():
        for keyword in keywords:
            if keyword.upper() in text:
                return brand

    if merchant_upper in ["NAN", "", "NONE"] or pd.isna(merchant):
        if any(kw in desc_upper for kw in ["NAKNADA", "ODRZAVANJE", "MESECNO"]):
            return "ODRŽAVANJE RAČUNA"
        return "Nepoznato"

    cleaned = str(merchant).replace("\n", " ").strip()
    if len(cleaned) > 30:
        cleaned = cleaned[:30] + "..."
    return cleaned


def get_month_name(month):
    """Get Serbian month name."""
    months = {
        1: "Januar", 2: "Februar", 3: "Mart", 4: "April",
        5: "Maj", 6: "Jun", 7: "Jul", 8: "Avgust",
        9: "Septembar", 10: "Oktobar", 11: "Novembar", 12: "Decembar"
    }
    return months.get(month, str(month))


def period_to_name(period_key):
    """Convert period key (2025-12) to name (Decembar 2025)."""
    try:
        year, month = period_key.split("-")
        return f"{get_month_name(int(month))} {year}"
    except:
        return period_key


def extract_transactions_from_pdf(pdf_file):
    """Extract transactions from Banca Intesa PDF statement."""
    transactions = []

    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()

            for table in tables:
                for row in table:
                    if row is None or len(row) < 8:
                        continue

                    if row[0] and ("Knjiženje" in str(row[0]) or "Datum" in str(row[0])):
                        continue

                    date_pattern = r'\d{2}\.\d{2}\.\d{4}'
                    if row[0] and re.match(date_pattern, str(row[0])):
                        date = row[0]
                        description = row[3] if len(row) > 3 else ""
                        isplate = parse_amount(row[4]) if len(row) > 4 else 0
                        uplate = parse_amount(row[5]) if len(row) > 5 else 0
                        merchant = row[7] if len(row) > 7 else ""

                        if isplate > 0 or uplate > 0:
                            transactions.append({
                                "Datum": date,
                                "Opis": description,
                                "Isplata": isplate,
                                "Uplata": uplate,
                                "Primalac/Platilac": merchant,
                                "Kategorija": categorize_transaction(description, merchant)
                            })

    return pd.DataFrame(transactions)


def detect_statement_period(df):
    """Try to detect the month/year from transactions."""
    if df.empty:
        return None, None

    dates = []
    for date_str in df["Datum"]:
        try:
            date = datetime.strptime(str(date_str), "%d.%m.%Y")
            dates.append(date)
        except:
            pass

    if not dates:
        return None, None

    from collections import Counter
    month_years = [(d.month, d.year) for d in dates]
    most_common = Counter(month_years).most_common(1)
    if most_common:
        month, year = most_common[0][0]
        return month, year
    return None, None


def save_statement(df, month, year, pdf_bytes=None, filename=None):
    """Save parsed statement data and optionally the PDF."""
    period_key = f"{year}-{month:02d}"
    period_dir = STATEMENTS_DIR / period_key
    period_dir.mkdir(exist_ok=True)

    csv_content = df.to_csv(index=False)
    csv_path = period_dir / "transactions.csv"
    with open(csv_path, "w", encoding="utf-8") as f:
        f.write(csv_content)

    if pdf_bytes:
        pdf_path = period_dir / "statement.pdf"
        with open(pdf_path, "wb") as f:
            f.write(pdf_bytes)

    metadata = {
        "month": month,
        "year": year,
        "period_name": f"{get_month_name(month)} {year}",
        "total_transactions": len(df),
        "total_expenses": float(df[df["Isplata"] > 0]["Isplata"].sum()),
        "total_income": float(df[df["Uplata"] > 0]["Uplata"].sum()),
        "original_filename": filename or "statement.pdf",
        "saved_at": datetime.now().isoformat()
    }
    with open(period_dir / "metadata.json", "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)

    return period_key


def load_statement(period_key):
    """Load a saved statement."""
    period_dir = STATEMENTS_DIR / period_key
    csv_path = period_dir / "transactions.csv"

    if not csv_path.exists():
        return None, None

    df = pd.read_csv(csv_path)

    metadata_path = period_dir / "metadata.json"
    metadata = None
    if metadata_path.exists():
        with open(metadata_path, "r", encoding="utf-8") as f:
            metadata = json.load(f)

    return df, metadata


def delete_statement(period_key):
    """Delete a saved statement."""
    import shutil
    period_dir = STATEMENTS_DIR / period_key
    if period_dir.exists():
        shutil.rmtree(period_dir)
        return True
    return False


def recategorize_all_statements():
    """Re-apply categorization rules to all saved statements."""
    count = 0
    for period_dir in STATEMENTS_DIR.iterdir():
        if period_dir.is_dir() and not period_dir.name.startswith('.'):
            csv_path = period_dir / "transactions.csv"
            if csv_path.exists():
                df = pd.read_csv(csv_path)
                df["Kategorija"] = df.apply(
                    lambda row: categorize_transaction(row["Opis"], row["Primalac/Platilac"]),
                    axis=1
                )
                df.to_csv(csv_path, index=False)

                metadata_path = period_dir / "metadata.json"
                if metadata_path.exists():
                    with open(metadata_path, "r", encoding="utf-8") as f:
                        metadata = json.load(f)
                    metadata["total_expenses"] = float(df[df["Isplata"] > 0]["Isplata"].sum())
                    metadata["total_income"] = float(df[df["Uplata"] > 0]["Uplata"].sum())
                    with open(metadata_path, "w", encoding="utf-8") as f:
                        json.dump(metadata, f, ensure_ascii=False, indent=2)
                count += 1
    return count


def get_saved_periods():
    """Get list of all saved statement periods."""
    periods = []
    for period_dir in sorted(STATEMENTS_DIR.iterdir(), reverse=True):
        if period_dir.is_dir() and not period_dir.name.startswith('.'):
            metadata_path = period_dir / "metadata.json"
            if metadata_path.exists():
                with open(metadata_path, "r", encoding="utf-8") as f:
                    metadata = json.load(f)
                    periods.append({
                        "key": period_dir.name,
                        "name": metadata.get("period_name", period_dir.name),
                        "expenses": metadata.get("total_expenses", 0),
                        "income": metadata.get("total_income", 0),
                        "transactions": metadata.get("total_transactions", 0),
                        "filename": metadata.get("original_filename", ""),
                        "saved_at": metadata.get("saved_at", "")
                    })
    return periods


def load_all_statements():
    """Load all saved statements into one combined DataFrame."""
    all_dfs = []
    for period_dir in STATEMENTS_DIR.iterdir():
        if period_dir.is_dir() and not period_dir.name.startswith('.'):
            csv_path = period_dir / "transactions.csv"
            if csv_path.exists():
                df = pd.read_csv(csv_path)
                df["Period"] = period_dir.name
                all_dfs.append(df)

    if all_dfs:
        return pd.concat(all_dfs, ignore_index=True)
    return pd.DataFrame()


def create_excel_export(df, period_name=""):
    """Create Excel file with multiple sheets."""
    expenses_df = df[df["Isplata"] > 0].copy()
    expenses_df["Brend"] = expenses_df.apply(
        lambda row: normalize_merchant(row["Primalac/Platilac"], row["Opis"]), axis=1
    )

    cat_summary = expenses_df.groupby("Kategorija")["Isplata"].agg(["sum", "count"])
    cat_summary.columns = ["Ukupno (RSD)", "Br. transakcija"]
    cat_summary = cat_summary.sort_values("Ukupno (RSD)", ascending=False).reset_index()

    brand_summary = expenses_df.groupby(["Kategorija", "Brend"])["Isplata"].agg(["sum", "count"])
    brand_summary.columns = ["Ukupno (RSD)", "Br. transakcija"]
    brand_summary = brand_summary.sort_values("Ukupno (RSD)", ascending=False).reset_index()

    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='Sve transakcije', index=False)
        cat_summary.to_excel(writer, sheet_name='Po kategorijama', index=False)
        brand_summary.to_excel(writer, sheet_name='Po brendovima', index=False)

        for sheet_name in writer.sheets:
            worksheet = writer.sheets[sheet_name]
            worksheet.set_column(0, 10, 20)

    output.seek(0)
    return output.getvalue()


# ===== PAGE: POČETNA (Statistics) =====

def page_pocetna():
    """Home page with statistics in Intesa style."""
    saved_periods = get_saved_periods()

    # Stats header with logo (like before)
    stats_logo = """<svg width="60" height="60" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg"><circle cx="50" cy="50" r="45" fill="#1a1a2e" stroke="#667eea" stroke-width="3"/><rect x="20" y="55" width="12" height="25" fill="#667eea" rx="2"/><rect x="37" y="40" width="12" height="40" fill="#764ba2" rx="2"/><rect x="54" y="30" width="12" height="50" fill="#667eea" rx="2"/><rect x="71" y="20" width="12" height="60" fill="#764ba2" rx="2"/></svg>"""

    st.markdown(f"""
    <div style="display: flex; align-items: center; gap: 15px; margin-bottom: 24px; flex-wrap: wrap;">
        {stats_logo}
        <div>
            <h1 style="margin: 0; font-size: 28px; font-weight: 800; color: #1a1a2e;">Ukupna Statistika</h1>
            <p style="margin: 5px 0 0 0; font-size: 14px; color: #666;">Analiza svih učitanih izvoda</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if not saved_periods:
        st.info("📂 Nema učitanih izvoda. Idite na **Izvodi** da učitate prvi izvod.")
        return

    all_df = load_all_statements()
    if all_df.empty:
        st.info("Nema podataka za prikaz")
        return

    expenses_df = all_df[all_df["Isplata"] > 0].copy()
    income_df = all_df[all_df["Uplata"] > 0].copy()

    total_expenses = expenses_df["Isplata"].sum()
    total_income = income_df["Uplata"].sum()
    balance = total_income - total_expenses
    num_periods = len(saved_periods)

    # Category stats
    expenses_df = expenses_df[expenses_df["Kategorija"] != "❓ Ostalo"]
    expenses_df["Brend"] = expenses_df.apply(
        lambda row: normalize_merchant(row["Primalac/Platilac"], row["Opis"]), axis=1
    )

    monthly_cat = expenses_df.groupby(["Period", "Kategorija"])["Isplata"].sum().reset_index()
    cat_stats = monthly_cat[monthly_cat["Isplata"] > 0].groupby("Kategorija")["Isplata"].agg(["max", "mean", "sum"]).sort_values("max", ascending=False)

    # Find max months
    cat_max_months = {}
    for category in cat_stats.index:
        cat_monthly = monthly_cat[monthly_cat["Kategorija"] == category].set_index("Period")["Isplata"]
        if len(cat_monthly) > 0:
            max_period = cat_monthly.idxmax()
            cat_max_months[category] = period_to_name(max_period)
        else:
            cat_max_months[category] = "-"

    # Top category highlight
    if len(cat_stats) > 0:
        top_category = cat_stats.index[0]
        top_cat_max = cat_stats.loc[top_category, "max"]
        top_cat_avg = cat_stats.loc[top_category, "mean"]
        top_cat_max_month = cat_max_months[top_category]

        top_cat_df = expenses_df[expenses_df["Kategorija"] == top_category]
        brand_totals = top_cat_df.groupby("Brend")["Isplata"].sum().sort_values(ascending=False)
        top_brand = brand_totals.index[0] if len(brand_totals) > 0 else "-"

        st.markdown(f"""
        <div class="stat-card">
            <p class="stat-label">🎯 Gde najviše trošiš</p>
            <p class="stat-value">{top_category}</p>
            <p class="stat-subtitle">Max: {top_cat_max:,.0f} RSD ({top_cat_max_month}) | Prosek: {top_cat_avg:,.0f} RSD/mesec</p>
            <p class="stat-subtitle" style="margin-top: 8px;">Top trgovac: <strong>{top_brand}</strong></p>
        </div>
        """, unsafe_allow_html=True)

    # Category ranking
    st.markdown("### 📊 Rang lista kategorija")

    for i, category in enumerate(cat_stats.index, 1):
        cat_max = cat_stats.loc[category, "max"]
        cat_avg = cat_stats.loc[category, "mean"]
        cat_max_month = cat_max_months[category]

        cat_df = expenses_df[expenses_df["Kategorija"] == category]
        cat_brands = cat_df.groupby("Brend")["Isplata"].sum().sort_values(ascending=False)
        top_brand_in_cat = cat_brands.index[0] if len(cat_brands) > 0 else "-"

        with st.expander(f"**#{i} {category}** — {cat_max:,.0f} / {cat_avg:,.0f} RSD"):
            st.caption(f"Max mesec: {cat_max:,.0f} RSD ({cat_max_month}) | Prosek: {cat_avg:,.0f} RSD/mesec")

            # Top brand
            top_brand_monthly = expenses_df[(expenses_df["Kategorija"] == category) & (expenses_df["Brend"] == top_brand_in_cat)]
            top_brand_monthly_totals = top_brand_monthly.groupby("Period")["Isplata"].sum()
            top_brand_max = top_brand_monthly_totals.max() if len(top_brand_monthly_totals) > 0 else 0
            top_brand_avg = top_brand_monthly_totals.mean() if len(top_brand_monthly_totals) > 0 else 0
            top_brand_max_month = period_to_name(top_brand_monthly_totals.idxmax()) if len(top_brand_monthly_totals) > 0 else "-"
            st.markdown(f"🥇 **{top_brand_in_cat}** — Max: {top_brand_max:,.0f} ({top_brand_max_month}) | Prosek: {top_brand_avg:,.0f}")

            if len(cat_brands) > 1:
                st.caption("Ostali trgovci:")
                for j, (brand, brand_total) in enumerate(cat_brands.items()):
                    if j == 0:
                        continue
                    if j > 5:
                        break
                    brand_monthly = expenses_df[(expenses_df["Kategorija"] == category) & (expenses_df["Brend"] == brand)]
                    brand_monthly_totals = brand_monthly.groupby("Period")["Isplata"].sum()
                    brand_max = brand_monthly_totals.max()
                    brand_avg = brand_monthly_totals.mean()
                    brand_max_month = period_to_name(brand_monthly_totals.idxmax()) if len(brand_monthly_totals) > 0 else "-"
                    st.write(f"• **{brand}** — Max: {brand_max:,.0f} ({brand_max_month}) | Prosek: {brand_avg:,.0f}")

                if len(cat_brands) > 6:
                    remaining_count = len(cat_brands) - 6
                    with st.expander(f"📋 Prikaži još {remaining_count} trgovaca"):
                        for j, (brand, brand_total) in enumerate(cat_brands.items()):
                            if j <= 5:
                                continue
                            brand_monthly = expenses_df[(expenses_df["Kategorija"] == category) & (expenses_df["Brend"] == brand)]
                            brand_monthly_totals = brand_monthly.groupby("Period")["Isplata"].sum()
                            brand_max = brand_monthly_totals.max()
                            brand_avg = brand_monthly_totals.mean()
                            brand_max_month = period_to_name(brand_monthly_totals.idxmax()) if len(brand_monthly_totals) > 0 else "-"
                            st.write(f"• **{brand}** — Max: {brand_max:,.0f} ({brand_max_month}) | Prosek: {brand_avg:,.0f}")

    # Ukupna potrošnja card at the END
    st.markdown("<div style='margin-top: 24px;'></div>", unsafe_allow_html=True)
    st.markdown(f"""
    <div class="intesa-card">
        <div class="intesa-card-header">
            <div>
                <p class="intesa-card-title">Ukupna potrošnja</p>
                <p class="intesa-card-amount">{total_expenses:,.0f} RSD</p>
                <p class="intesa-card-subtitle">Ukupno potrošeno ({num_periods} meseci)</p>
            </div>
        </div>
        <div class="intesa-card-row">
            <span class="intesa-card-label">💵 Primanja</span>
            <span class="intesa-card-value">{total_income:,.0f} RSD</span>
        </div>
        <div class="intesa-card-row">
            <span class="intesa-card-label">💸 Potrošnja</span>
            <span class="intesa-card-value">{total_expenses:,.0f} RSD</span>
        </div>
        <div class="intesa-card-row">
            <span class="intesa-card-label">📊 Bilans</span>
            <span class="intesa-card-value" style="color: {'#10b981' if balance >= 0 else '#ef4444'}">{balance:+,.0f} RSD</span>
        </div>
        <div class="intesa-card-row">
            <span class="intesa-card-label">📝 Transakcija</span>
            <span class="intesa-card-value">{len(all_df)}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Excel download for all data
    st.markdown("")
    excel_data = create_excel_export(all_df, "Ukupna statistika")
    st.download_button(
        "📥 Preuzmi Excel (svi izvodi)",
        excel_data,
        "ukupna_statistika.xlsx",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )


# ===== PAGE: IZVODI =====

def page_izvodi():
    """Statement management page."""
    st.markdown("""
    <div class="page-header">
        <span style="font-size: 28px;">📂</span>
        <h1 class="page-title">Upravljanje izvodima</h1>
    </div>
    """, unsafe_allow_html=True)

    saved_periods = get_saved_periods()

    # Upload section
    st.markdown("### 📤 Učitaj novi izvod")

    if 'uploader_key' not in st.session_state:
        st.session_state['uploader_key'] = 0

    uploaded_file = st.file_uploader(
        "Izaberi PDF fajl (Banca Intesa izvod)",
        type="pdf",
        key=f"pdf_uploader_{st.session_state['uploader_key']}"
    )

    if st.session_state.get('upload_success'):
        st.success(f"✅ Uspešno učitan izvod: {st.session_state['upload_success']}")
        del st.session_state['upload_success']

    if uploaded_file is not None:
        pdf_bytes = uploaded_file.read()
        original_filename = uploaded_file.name

        with st.spinner("Učitavam i parsiram izvod..."):
            df_new = extract_transactions_from_pdf(BytesIO(pdf_bytes))

            if not df_new.empty:
                month, year = detect_statement_period(df_new)
                if month and year:
                    save_statement(df_new, month, year, pdf_bytes, original_filename)
                    st.session_state['upload_success'] = f"{get_month_name(month)} {year}"
                    st.session_state['uploader_key'] += 1
                    st.rerun()
                else:
                    st.error("Nije moguće detektovati period izvoda")
            else:
                st.error("Nije moguće parsirati transakcije iz PDF-a")

    st.divider()

    # Saved statements list
    st.markdown("### 📋 Sačuvani izvodi")

    if not saved_periods:
        st.info("Nema sačuvanih izvoda")
    else:
        # Initialize selected periods in session state
        if 'selected_periods' not in st.session_state:
            st.session_state['selected_periods'] = []

        # Group by year
        from collections import defaultdict
        periods_by_year = defaultdict(list)
        for period in saved_periods:
            year = period['key'].split('-')[0]
            periods_by_year[year].append(period)

        # List with checkboxes grouped by year in expanders
        selected = []
        for year in sorted(periods_by_year.keys(), reverse=True):
            year_periods = periods_by_year[year]
            with st.expander(f"📅 **{year}** ({len(year_periods)} izvoda)"):
                for period in year_periods:
                    month_name = period['name'].split()[0]
                    checked = st.checkbox(month_name, key=f"check_{period['key']}")
                    if checked:
                        selected.append(period['key'])

        # Update selected periods
        st.session_state['selected_periods'] = selected

        # Delete buttons row (below the list)
        st.markdown("")
        col_del1, col_del2 = st.columns([1, 1])
        with col_del1:
            if st.button("🗑️ Obriši odabrane", use_container_width=True, disabled=len(st.session_state.get('selected_periods', [])) == 0):
                for period_key in st.session_state.get('selected_periods', []):
                    delete_statement(period_key)
                st.session_state['selected_periods'] = []
                st.rerun()
        with col_del2:
            if st.button("🗑️ Obriši sve", use_container_width=True):
                for period in saved_periods:
                    delete_statement(period['key'])
                st.session_state['selected_periods'] = []
                st.rerun()

    # Tools section
    st.markdown("### 🔧 Alati")

    if st.session_state.get('recategorize_success'):
        st.success(st.session_state['recategorize_success'])
        del st.session_state['recategorize_success']

    if st.button("🔄 Rekategorizuj sve izvode", use_container_width=True):
        with st.spinner("Rekategorizujem..."):
            count = recategorize_all_statements()
        st.session_state['recategorize_success'] = f"✅ Uspešno rekategorizovano {count} izvoda!"
        st.rerun()


# ===== PAGE: MESEČNI PRIKAZ =====

def page_mesecni_prikaz():
    """Monthly view page with card navigation."""
    st.markdown("""
    <div class="page-header">
        <span style="font-size: 28px;">📅</span>
        <h1 class="page-title">Mesečni prikaz</h1>
    </div>
    """, unsafe_allow_html=True)

    saved_periods = get_saved_periods()

    if not saved_periods:
        st.info("📂 Nema učitanih izvoda. Idite na **Izvodi** da učitate prvi izvod.")
        return

    # Group by year
    from collections import defaultdict
    periods_by_year = defaultdict(list)
    for period in saved_periods:
        year = period['key'].split('-')[0]
        periods_by_year[year].append(period)

    # Initialize selected period in session state
    if 'selected_month_key' not in st.session_state:
        st.session_state['selected_month_key'] = saved_periods[0]['key']

    # Year selector
    years = sorted(periods_by_year.keys(), reverse=True)
    current_year = st.session_state['selected_month_key'].split('-')[0]
    if current_year not in years:
        current_year = years[0]

    selected_year = st.selectbox("Godina", years, index=years.index(current_year), label_visibility="collapsed")

    # Get periods for selected year
    year_periods = periods_by_year[selected_year]
    period_keys = [p['key'] for p in year_periods]

    # Find current selection index
    if st.session_state['selected_month_key'] in period_keys:
        current_idx = period_keys.index(st.session_state['selected_month_key'])
    else:
        current_idx = 0
        st.session_state['selected_month_key'] = period_keys[0]

    # Navigation with prev/current/next
    current_period = year_periods[current_idx]
    current_month = current_period['name'].split()[0]

    col1, col2, col3 = st.columns([1, 2, 1])

    with col1:
        if current_idx < len(year_periods) - 1:
            prev_period = year_periods[current_idx + 1]
            prev_month = prev_period['name'].split()[0]
            if st.button(f"◀ {prev_month}", key="prev_month", use_container_width=True):
                st.session_state['selected_month_key'] = prev_period['key']
                st.rerun()

    with col2:
        st.markdown(f"""
        <div style="text-align: center; padding: 16px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 12px; color: white;">
            <p style="margin: 0; font-size: 24px; font-weight: 700;">{current_month}</p>
            <p style="margin: 4px 0 0 0; opacity: 0.8;">{selected_year}</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        if current_idx > 0:
            next_period = year_periods[current_idx - 1]
            next_month = next_period['name'].split()[0]
            if st.button(f"{next_month} ▶", key="next_month", use_container_width=True):
                st.session_state['selected_month_key'] = next_period['key']
                st.rerun()

    st.markdown("")

    # Check if we need to refresh after mapping
    if st.session_state.get('mapping_done'):
        del st.session_state['mapping_done']
        st.rerun()

    selected_key = st.session_state['selected_month_key']
    selected_name = current_period['name']

    df, metadata = load_statement(selected_key)

    if df is None:
        st.error("Greška pri učitavanju izvoda")
        return

    expenses_df = df[df["Isplata"] > 0].copy()
    income_df = df[df["Uplata"] > 0].copy()

    total_expenses = expenses_df["Isplata"].sum()
    total_income = income_df["Uplata"].sum()
    balance = total_income - total_expenses

    # Categories breakdown
    st.markdown("### 📊 Potrošnja po kategorijama")

    category_totals = expenses_df.groupby("Kategorija")["Isplata"].agg(["sum", "count"])
    category_totals.columns = ["Ukupno (RSD)", "Br. transakcija"]
    category_totals = category_totals.sort_values("Ukupno (RSD)", ascending=False)

    for category in category_totals.index:
        total = category_totals.loc[category, "Ukupno (RSD)"]
        count = int(category_totals.loc[category, "Br. transakcija"])
        pct = (total / total_expenses * 100) if total_expenses > 0 else 0

        # Special handling for "Ostalo" category
        if category == "❓ Ostalo":
            with st.expander(f"{category} — **{total:,.0f} RSD** ({count}) ⚠️ Nemapirano", expanded=False):
                st.caption("Transakcije koje nisu svrstane ni u jednu kategoriju. Možete ih mapirati odavde.")

                cat_transactions = expenses_df[expenses_df["Kategorija"] == category].copy()
                cat_transactions["Brend"] = cat_transactions.apply(
                    lambda row: normalize_merchant(row["Primalac/Platilac"], row["Opis"]), axis=1
                )

                # Group by brand/merchant
                merchant_totals = cat_transactions.groupby("Brend")["Isplata"].agg(["sum", "count"])
                merchant_totals.columns = ["Ukupno (RSD)", "Br. kupovina"]
                merchant_totals = merchant_totals.sort_values("Ukupno (RSD)", ascending=False)

                # Load categories and brands for mapping
                categories_list = load_categories()
                brand_mapping = load_brand_mapping()

                for idx, brand in enumerate(merchant_totals.index):
                    brand_total = merchant_totals.loc[brand, "Ukupno (RSD)"]
                    brand_count = int(merchant_totals.loc[brand, "Br. kupovina"])

                    # Create stable key from brand name (only alphanumeric)
                    import re
                    brand_key = f"{selected_key}_{idx}"

                    with st.expander(f"**{brand}** — {brand_total:,.0f} RSD ({brand_count})", expanded=False):
                        # Show transactions
                        brand_transactions = cat_transactions[cat_transactions["Brend"] == brand][
                            ["Datum", "Opis", "Isplata", "Primalac/Platilac"]
                        ].copy()
                        brand_transactions = brand_transactions.sort_values("Datum")
                        brand_transactions.columns = ["Datum", "Opis", "Iznos (RSD)", "Detalji"]

                        st.dataframe(
                            brand_transactions.style.format({"Iznos (RSD)": "{:,.2f}"}),
                            use_container_width=True,
                            hide_index=True
                        )

                        # Mapping options
                        st.markdown("---")
                        st.markdown("##### 🏷️ Mapiraj ovog trgovca")

                        # Get original merchant name for mapping
                        original_merchant = cat_transactions[cat_transactions["Brend"] == brand]["Primalac/Platilac"].iloc[0]
                        default_keyword = str(original_merchant).upper().replace("\n", " ").strip()[:30]

                        # Use form for reliable submission
                        with st.form(key=f"map_form_{brand_key}"):
                            keyword_input = st.text_input(
                                "Ključna reč (po čemu da se prepoznaje):",
                                value=default_keyword,
                                help="Jednostavnija reč = bolje (npr. 'KAFANA' umesto 'KAFANACACAK 688')"
                            )

                            col1, col2 = st.columns(2)
                            with col1:
                                cat_options = ["— Izaberi —"] + list(categories_list.keys())
                                target_category = st.selectbox(
                                    "Dodaj u kategoriju:",
                                    cat_options
                                )
                            with col2:
                                brand_display = st.text_input(
                                    "Prikaži kao (brend):",
                                    value=brand if brand != "Nepoznato" else default_keyword.split()[0] if default_keyword else ""
                                )

                            submitted = st.form_submit_button("✅ Mapiraj", use_container_width=True, type="primary")

                            if submitted:
                                keyword_val = keyword_input.strip().upper() if keyword_input else ""
                                brand_val = brand_display.strip() if brand_display else ""
                                cat_val = target_category

                                if not keyword_val:
                                    st.error("Unesite ključnu reč!")
                                elif not brand_val:
                                    st.error("Unesite naziv brenda!")
                                elif cat_val == "— Izaberi —":
                                    st.error("Izaberite kategoriju!")
                                else:
                                    # Reload to get fresh data
                                    cats = load_categories()
                                    brands = load_brand_mapping()

                                    # Add keyword to category
                                    if keyword_val not in [k.upper() for k in cats.get(cat_val, [])]:
                                        if cat_val not in cats:
                                            cats[cat_val] = []
                                        cats[cat_val].append(keyword_val)
                                        save_categories(cats)
                                        st.info(f"DEBUG: Dodata ključna reč '{keyword_val}' u kategoriju '{cat_val}'")

                                    # Add brand mapping
                                    if brand_val not in brands:
                                        brands[brand_val] = []
                                    if keyword_val not in [a.upper() for a in brands[brand_val]]:
                                        brands[brand_val].append(keyword_val)
                                    save_brand_mapping(brands)
                                    st.info(f"DEBUG: Brend '{brand_val}' sačuvan sa varijantom '{keyword_val}'")

                                    # Auto recategorize
                                    count = recategorize_all_statements()
                                    st.info(f"DEBUG: Rekategorizovano {count} izvoda")

                                    st.success(f"✅ Mapirano! '{keyword_val}' → {cat_val}, brend '{brand_val}'")
                                    st.warning("⚠️ Kliknite bilo gde na stranici ili pritisnite F5 da osvežite prikaz")
        else:
            # Regular category expander
            with st.expander(f"{category} — **{total:,.0f} RSD** ({count})", expanded=False):
                cat_transactions = expenses_df[expenses_df["Kategorija"] == category].copy()
                cat_transactions["Brend"] = cat_transactions.apply(
                    lambda row: normalize_merchant(row["Primalac/Platilac"], row["Opis"]), axis=1
                )

                # Group by brand
                merchant_totals = cat_transactions.groupby("Brend")["Isplata"].agg(["sum", "count"])
                merchant_totals.columns = ["Ukupno (RSD)", "Br. kupovina"]
                merchant_totals = merchant_totals.sort_values("Ukupno (RSD)", ascending=False)

                # Nested expander for each brand
                for brand in merchant_totals.index:
                    brand_total = merchant_totals.loc[brand, "Ukupno (RSD)"]
                    brand_count = int(merchant_totals.loc[brand, "Br. kupovina"])

                    with st.expander(f"**{brand}** — {brand_total:,.0f} RSD ({brand_count})", expanded=False):
                        # Show transactions for this brand
                        brand_transactions = cat_transactions[cat_transactions["Brend"] == brand][
                            ["Datum", "Opis", "Isplata", "Primalac/Platilac"]
                        ].copy()
                        brand_transactions = brand_transactions.sort_values("Datum")
                        brand_transactions.columns = ["Datum", "Opis", "Iznos (RSD)", "Detalji"]

                        st.dataframe(
                            brand_transactions.style.format({"Iznos (RSD)": "{:,.2f}"}),
                            use_container_width=True,
                            hide_index=True
                        )

    # Stats card at the END
    st.markdown(f"""
    <div class="intesa-card">
        <div class="intesa-card-header">
            <div>
                <p class="intesa-card-title">{selected_name}</p>
                <p class="intesa-card-amount">{total_expenses:,.0f} RSD</p>
                <p class="intesa-card-subtitle">Ukupna potrošnja</p>
            </div>
        </div>
        <div class="intesa-card-row">
            <span class="intesa-card-label">💵 Primanja</span>
            <span class="intesa-card-value">{total_income:,.0f} RSD</span>
        </div>
        <div class="intesa-card-row">
            <span class="intesa-card-label">💸 Potrošnja</span>
            <span class="intesa-card-value">{total_expenses:,.0f} RSD</span>
        </div>
        <div class="intesa-card-row">
            <span class="intesa-card-label">📊 Bilans</span>
            <span class="intesa-card-value" style="color: {'#10b981' if balance >= 0 else '#ef4444'}">{balance:+,.0f} RSD</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Excel download
    st.markdown("")
    excel_data = create_excel_export(df, selected_name)
    st.download_button(
        "📥 Preuzmi Excel",
        excel_data,
        f"izvod_{selected_key}.xlsx",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )


# ===== PAGE: PODEŠAVANJA (Category Management) =====

def page_podesavanja():
    """Settings page for managing categories and brand mappings."""
    st.markdown("""
    <div class="page-header">
        <span style="font-size: 28px;">⚙️</span>
        <h1 class="page-title">Podešavanja kategorija</h1>
    </div>
    """, unsafe_allow_html=True)

    # Tabs for Categories and Brand Mapping
    tab1, tab2 = st.tabs(["📂 Kategorije", "🏷️ Mapiranje brendova"])

    # ===== TAB 1: CATEGORIES =====
    with tab1:
        categories = load_categories()

        # Success messages
        if st.session_state.get('cat_success'):
            st.success(st.session_state['cat_success'])
            del st.session_state['cat_success']

        # Add new category section
        st.markdown("### ➕ Dodaj novu kategoriju")
        new_cat_name = st.text_input("Naziv kategorije", key="new_cat_name", placeholder="npr. '🛍️ Šoping'")
        new_cat_keyword = st.text_input("Prva ključna reč (opciono)", key="new_cat_keyword", placeholder="npr. 'SHOPPING'")

        if st.button("➕ Dodaj kategoriju", key="add_cat_btn", use_container_width=True):
            if new_cat_name and new_cat_name.strip():
                if new_cat_name not in categories:
                    keywords = []
                    if new_cat_keyword and new_cat_keyword.strip():
                        keywords.append(new_cat_keyword.upper())
                    categories[new_cat_name] = keywords
                    save_categories(categories)
                    st.session_state['cat_success'] = f"✅ Kategorija '{new_cat_name}' je dodata!"
                    st.rerun()
                else:
                    st.error("Kategorija već postoji!")
            else:
                st.error("Unesite naziv kategorije!")

        st.divider()

        # List existing categories
        st.markdown("### 📋 Postojeće kategorije")

        for cat_name in list(categories.keys()):
            keywords = categories[cat_name]

            with st.expander(f"**{cat_name}** ({len(keywords)} ključnih reči)", expanded=False):
                # Initialize edit state for this category
                if f"edit_cat_{cat_name}" not in st.session_state:
                    st.session_state[f"edit_cat_{cat_name}"] = {
                        "name": cat_name,
                        "keywords": keywords.copy()
                    }

                edit_state = st.session_state[f"edit_cat_{cat_name}"]

                # Rename category
                st.markdown("##### ✏️ Naziv kategorije")
                edit_state["name"] = st.text_input("Naziv", value=edit_state["name"], key=f"rename_cat_{cat_name}", label_visibility="collapsed")

                st.markdown("##### 🔑 Ključne reči")
                st.caption("Transakcije koje sadrže ove reči će biti svrstane u ovu kategoriju")

                # Add new keyword
                col1, col2 = st.columns([3, 1])
                with col1:
                    new_keyword = st.text_input("Nova ključna reč", key=f"new_kw_{cat_name}", label_visibility="collapsed", placeholder="Dodaj novu ključnu reč...")
                with col2:
                    if st.button("Dodaj", key=f"add_kw_btn_{cat_name}", use_container_width=True):
                        if new_keyword and new_keyword.strip():
                            if new_keyword.upper() not in [k.upper() for k in edit_state["keywords"]]:
                                edit_state["keywords"].append(new_keyword.upper())
                                st.rerun()
                            else:
                                st.error("Ključna reč već postoji!")

                # List and edit keywords
                if edit_state["keywords"]:
                    keywords_to_remove = []
                    for i, kw in enumerate(edit_state["keywords"]):
                        col1, col2 = st.columns([4, 1])
                        with col1:
                            edit_state["keywords"][i] = st.text_input(f"kw_{i}", value=kw, key=f"edit_kw_{cat_name}_{i}", label_visibility="collapsed")
                        with col2:
                            if st.button("🗑️", key=f"del_kw_{cat_name}_{i}", help="Obriši"):
                                keywords_to_remove.append(i)

                    # Remove marked keywords
                    for i in reversed(keywords_to_remove):
                        edit_state["keywords"].pop(i)
                        st.rerun()
                else:
                    st.caption("Nema ključnih reči")

                # Save all changes button
                st.markdown("---")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("💾 Sačuvaj sve izmene", key=f"save_cat_{cat_name}", use_container_width=True, type="primary"):
                        new_name = edit_state["name"]
                        new_keywords = [k.upper() for k in edit_state["keywords"] if k.strip()]

                        # Check if name changed
                        if new_name != cat_name:
                            if new_name in categories and new_name != cat_name:
                                st.error("Kategorija sa tim imenom već postoji!")
                            else:
                                del categories[cat_name]
                                categories[new_name] = new_keywords
                                save_categories(categories)
                                recategorize_all_statements()  # Auto recategorize
                                del st.session_state[f"edit_cat_{cat_name}"]
                                st.session_state['cat_success'] = f"✅ Kategorija sačuvana kao '{new_name}'! Izvodi rekategorizovani."
                                st.rerun()
                        else:
                            categories[cat_name] = new_keywords
                            save_categories(categories)
                            recategorize_all_statements()  # Auto recategorize
                            st.session_state['cat_success'] = f"✅ Izmene sačuvane! Izvodi rekategorizovani."
                            st.rerun()

                with col2:
                    if st.button(f"🗑️ Obriši kategoriju", key=f"del_cat_{cat_name}", use_container_width=True):
                        del categories[cat_name]
                        save_categories(categories)
                        if f"edit_cat_{cat_name}" in st.session_state:
                            del st.session_state[f"edit_cat_{cat_name}"]
                        st.session_state['cat_success'] = f"✅ Kategorija '{cat_name}' obrisana!"
                        st.rerun()

    # ===== TAB 2: BRAND MAPPING =====
    with tab2:
        brand_mapping = load_brand_mapping()
        categories = load_categories()

        # Success messages
        if st.session_state.get('brand_success'):
            st.success(st.session_state['brand_success'])
            del st.session_state['brand_success']

        # Add new brand section
        st.markdown("### ➕ Dodaj novi brend")

        new_brand_name = st.text_input("Naziv brenda", key="new_brand_name", placeholder="npr. 'JKP VODOVOD'")
        new_brand_variant = st.text_input("Prva varijanta (ključna reč)", key="new_brand_variant", placeholder="npr. 'VODOVOD' - po čemu da se prepoznaje")

        # Category selection
        category_list = ["— Izaberi kategoriju —"] + list(categories.keys())
        selected_category = st.selectbox("Dodaj u kategoriju (opciono)", category_list, key="new_brand_category")

        if st.button("➕ Dodaj brend", key="add_brand_btn", use_container_width=True):
            if new_brand_name and new_brand_name.strip():
                if new_brand_name not in brand_mapping:
                    # Add brand with variant
                    variants = []
                    if new_brand_variant and new_brand_variant.strip():
                        variants.append(new_brand_variant.upper())
                    brand_mapping[new_brand_name] = variants
                    save_brand_mapping(brand_mapping)

                    # Optionally add to category
                    if selected_category != "— Izaberi kategoriju —" and new_brand_variant:
                        if new_brand_variant.upper() not in [k.upper() for k in categories[selected_category]]:
                            categories[selected_category].append(new_brand_variant.upper())
                            save_categories(categories)
                        recategorize_all_statements()  # Auto recategorize
                        st.session_state['brand_success'] = f"✅ Brend '{new_brand_name}' dodat i izvodi rekategorizovani!"
                    else:
                        st.session_state['brand_success'] = f"✅ Brend '{new_brand_name}' dodat!"
                    st.rerun()
                else:
                    st.error("Brend već postoji!")
            else:
                st.error("Unesite naziv brenda!")

        st.divider()

        # List existing brands
        st.markdown("### 📋 Postojeći brendovi")

        for brand_name in list(brand_mapping.keys()):
            aliases = brand_mapping[brand_name]

            with st.expander(f"**{brand_name}** ({len(aliases)} varijanti)", expanded=False):
                # Initialize edit state for this brand
                if f"edit_brand_{brand_name}" not in st.session_state:
                    st.session_state[f"edit_brand_{brand_name}"] = {
                        "name": brand_name,
                        "aliases": aliases.copy()
                    }

                edit_state = st.session_state[f"edit_brand_{brand_name}"]

                # Rename brand
                st.markdown("##### ✏️ Naziv brenda")
                edit_state["name"] = st.text_input("Naziv", value=edit_state["name"], key=f"rename_brand_{brand_name}", label_visibility="collapsed")

                st.markdown("##### 🔤 Varijante naziva")
                st.caption("Ključne reči po kojima se prepoznaje ovaj brend")

                # Add new alias
                col1, col2 = st.columns([3, 1])
                with col1:
                    new_alias = st.text_input("Nova varijanta", key=f"new_alias_{brand_name}", label_visibility="collapsed", placeholder="Dodaj novu varijantu...")
                with col2:
                    if st.button("Dodaj", key=f"add_alias_btn_{brand_name}", use_container_width=True):
                        if new_alias and new_alias.strip():
                            if new_alias.upper() not in [a.upper() for a in edit_state["aliases"]]:
                                edit_state["aliases"].append(new_alias.upper())
                                st.rerun()
                            else:
                                st.error("Varijanta već postoji!")

                # List and edit aliases
                if edit_state["aliases"]:
                    aliases_to_remove = []
                    for i, alias in enumerate(edit_state["aliases"]):
                        col1, col2 = st.columns([4, 1])
                        with col1:
                            edit_state["aliases"][i] = st.text_input(f"alias_{i}", value=alias, key=f"edit_alias_{brand_name}_{i}", label_visibility="collapsed")
                        with col2:
                            if st.button("🗑️", key=f"del_alias_{brand_name}_{i}", help="Obriši"):
                                aliases_to_remove.append(i)

                    # Remove marked aliases
                    for i in reversed(aliases_to_remove):
                        edit_state["aliases"].pop(i)
                        st.rerun()
                else:
                    st.caption("Nema varijanti")

                # Save all changes button
                st.markdown("---")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("💾 Sačuvaj sve izmene", key=f"save_brand_{brand_name}", use_container_width=True, type="primary"):
                        new_name = edit_state["name"]
                        new_aliases = [a.upper() for a in edit_state["aliases"] if a.strip()]

                        # Check if name changed
                        if new_name != brand_name:
                            if new_name in brand_mapping and new_name != brand_name:
                                st.error("Brend sa tim imenom već postoji!")
                            else:
                                del brand_mapping[brand_name]
                                brand_mapping[new_name] = new_aliases
                                save_brand_mapping(brand_mapping)
                                del st.session_state[f"edit_brand_{brand_name}"]
                                st.session_state['brand_success'] = f"✅ Brend sačuvan kao '{new_name}'!"
                                st.rerun()
                        else:
                            brand_mapping[brand_name] = new_aliases
                            save_brand_mapping(brand_mapping)
                            st.session_state['brand_success'] = f"✅ Izmene sačuvane!"
                            st.rerun()

                with col2:
                    if st.button(f"🗑️ Obriši brend", key=f"del_brand_{brand_name}", use_container_width=True):
                        del brand_mapping[brand_name]
                        save_brand_mapping(brand_mapping)
                        if f"edit_brand_{brand_name}" in st.session_state:
                            del st.session_state[f"edit_brand_{brand_name}"]
                        st.session_state['brand_success'] = f"✅ Brend '{brand_name}' obrisan!"
                        st.rerun()

    # ===== TAB 3: UNMAPPED MERCHANTS =====
    st.divider()
    st.markdown("### 🔍 Nemapirani trgovci")
    st.caption("Trgovci iz transakcija koji nemaju mapiranje na brend")

    # Load all transactions and find unmapped merchants
    all_df = load_all_statements()
    if not all_df.empty:
        expenses_df = all_df[all_df["Isplata"] > 0].copy()
        brand_mapping = load_brand_mapping()

        # Get all unique merchants
        unmapped_merchants = set()
        for _, row in expenses_df.iterrows():
            merchant = row["Primalac/Platilac"]
            description = row.get("Opis", "")
            normalized = normalize_merchant(merchant, description)

            # Check if it's truly unmapped (returned as-is or "Nepoznato")
            merchant_upper = str(merchant).upper()
            is_mapped = False
            for brand, aliases in brand_mapping.items():
                for alias in aliases:
                    if alias.upper() in f"{merchant_upper} {str(description).upper()}":
                        is_mapped = True
                        break
                if is_mapped:
                    break

            if not is_mapped and normalized not in ["Nepoznato", "ODRŽAVANJE RAČUNA"] and pd.notna(merchant) and str(merchant).strip():
                # Clean the merchant name for display
                clean_merchant = str(merchant).replace("\n", " ").strip()
                if clean_merchant and clean_merchant.upper() not in ["NAN", ""]:
                    unmapped_merchants.add(clean_merchant)

        if unmapped_merchants:
            st.info(f"Pronađeno **{len(unmapped_merchants)}** nemapirani trgovac/a")

            # Success message
            if st.session_state.get('unmapped_success'):
                st.success(st.session_state['unmapped_success'])
                del st.session_state['unmapped_success']

            for merchant in sorted(unmapped_merchants):
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    st.text(merchant[:50] + "..." if len(merchant) > 50 else merchant)
                with col2:
                    # Add as new brand
                    if st.button("➕ Novi brend", key=f"new_brand_{hash(merchant)}", help="Dodaj kao novi brend"):
                        brand_mapping = load_brand_mapping()
                        # Create a clean brand name
                        brand_name = merchant.upper().replace("\n", " ").strip()[:30]
                        if brand_name not in brand_mapping:
                            brand_mapping[brand_name] = [merchant.upper()]
                            save_brand_mapping(brand_mapping)
                            st.session_state['unmapped_success'] = f"✅ Brend '{brand_name}' dodat!"
                            st.rerun()
                with col3:
                    # Add to existing brand (dropdown)
                    if st.button("📎 Postojeći", key=f"existing_{hash(merchant)}", help="Dodaj kao varijantu postojećeg brenda"):
                        st.session_state[f'show_brands_for_{hash(merchant)}'] = True
                        st.rerun()

                # Show brand selector if requested
                if st.session_state.get(f'show_brands_for_{hash(merchant)}'):
                    brand_mapping = load_brand_mapping()
                    brand_list = list(brand_mapping.keys())
                    if brand_list:
                        selected_brand = st.selectbox(
                            "Izaberi brend:",
                            brand_list,
                            key=f"select_brand_{hash(merchant)}"
                        )
                        col_a, col_b = st.columns(2)
                        with col_a:
                            if st.button("✅ Dodaj", key=f"confirm_add_{hash(merchant)}"):
                                brand_mapping[selected_brand].append(merchant.upper())
                                save_brand_mapping(brand_mapping)
                                del st.session_state[f'show_brands_for_{hash(merchant)}']
                                st.session_state['unmapped_success'] = f"✅ '{merchant}' dodat kao varijanta brenda '{selected_brand}'!"
                                st.rerun()
                        with col_b:
                            if st.button("❌ Otkaži", key=f"cancel_add_{hash(merchant)}"):
                                del st.session_state[f'show_brands_for_{hash(merchant)}']
                                st.rerun()
                    else:
                        st.warning("Nema postojećih brendova. Prvo dodaj brend.")

        else:
            st.success("✅ Svi trgovci su mapirani!")
    else:
        st.info("Nema učitanih izvoda za analizu.")

    # Utility section
    st.divider()
    st.markdown("### 🔧 Alati")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Resetuj na podrazumevane vrednosti", use_container_width=True):
            save_categories(DEFAULT_CATEGORIES)
            save_brand_mapping(DEFAULT_BRAND_MAPPING)
            st.session_state['cat_success'] = "✅ Kategorije i brendovi resetovani na podrazumevane vrednosti!"
            st.rerun()

    with col2:
        if st.button("🔄 Rekategorizuj sve izvode", use_container_width=True):
            with st.spinner("Rekategorizujem..."):
                count = recategorize_all_statements()
            st.session_state['cat_success'] = f"✅ Uspešno rekategorizovano {count} izvoda!"
            st.rerun()

    st.caption("💡 Nakon izmena kategorija, kliknite 'Rekategorizuj sve izvode' da se promene primene na postojeće podatke.")


# ===== PAGE: POMOĆ =====

def page_pomoc():
    """Help page with usage instructions."""
    st.markdown("""
    <div class="page-header">
        <span style="font-size: 28px;">📖</span>
        <h1 class="page-title">Kako koristiti aplikaciju</h1>
    </div>
    """, unsafe_allow_html=True)

    # Quick start
    st.markdown("### 🚀 Brzi početak")
    st.markdown("""
    1. **Učitaj izvod** - Idi na 📂 Izvodi i upload-uj PDF iz Banca Intesa
    2. **Pregledaj mesec** - Idi na 📅 Mesečni prikaz da vidiš potrošnju po kategorijama
    3. **Mapiraj nepoznate** - Transakcije u "❓ Ostalo" možeš mapirati u odgovarajuće kategorije
    4. **Vidi statistiku** - Na 🏠 Početna vidiš ukupnu statistiku svih meseci
    """)

    st.divider()

    # How categorization works
    st.markdown("### 🏷️ Kako radi kategorizacija")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        **Kategorija** = gde spada transakcija
        - Određuje se po **ključnim rečima**
        - Npr. `LIDL` → 🛒 Marketi
        - Čuva se u CSV fajlu
        """)

    with col2:
        st.markdown("""
        **Brend** = kako se prikazuje naziv
        - Određuje se po **varijantama**
        - Npr. `LIDL CACAK 123` → `LIDL`
        - Računa se dinamički
        """)

    st.markdown("#### Primer toka")
    st.code("""
Transakcija: "LIDL CACAK 123"
        │
        ▼
┌─────────────────────────────────┐
│ 1. Traži ključnu reč            │
│    "LIDL" → 🛒 Marketi          │
└─────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────┐
│ 2. Traži varijantu brenda       │
│    "LIDL" → prikaži kao "LIDL"  │
└─────────────────────────────────┘
        │
        ▼
Rezultat: Marketi / LIDL
    """, language=None)

    st.divider()

    # How to map
    st.markdown("### 🔧 Kako mapirati novog trgovca")

    with st.expander("**Opcija 1: Iz mesečnog prikaza (preporučeno)**", expanded=True):
        st.markdown("""
        1. Idi na **📅 Mesečni prikaz**
        2. Otvori **❓ Ostalo** kategoriju
        3. Pronađi trgovca kojeg želiš da mapiraš
        4. Klikni na njega da se otvori
        5. Popuni:
           - **Ključna reč**: kratka reč za prepoznavanje (npr. `KAFANA`)
           - **Kategorija**: gde da se svrsta
           - **Brend**: kako da se prikazuje naziv
        6. Klikni **✅ Mapiraj**
        7. Pritisni **F5** da osveži stranicu
        """)

    with st.expander("**Opcija 2: Iz podešavanja**"):
        st.markdown("""
        1. Idi na **⚙️ Podešavanja**
        2. Za kategoriju:
           - Tab **📂 Kategorije**
           - Otvori željenu kategoriju
           - Dodaj ključnu reč
           - Sačuvaj
        3. Za brend:
           - Tab **🏷️ Mapiranje brendova**
           - Dodaj novi brend sa varijantom
        """)

    with st.expander("**Opcija 3: Nemapirani trgovci**"):
        st.markdown("""
        1. Idi na **⚙️ Podešavanja**
        2. Skroluj do **🔍 Nemapirani trgovci**
        3. Tu su svi trgovci koji nemaju brend mapiranje
        4. Klikni **➕ Novi brend** ili **📎 Postojeći**
        """)

    st.divider()

    # Tips
    st.markdown("### 💡 Saveti")

    st.success("""
    **Ključne reči treba da budu kratke i jedinstvene**

    ✅ Dobro: `KAFANA`, `LIDL`, `WOLT`

    ❌ Loše: `KAFANACACAK 688 BEOGRAD` (previše specifično, neće matchovati druge varijante)
    """)

    st.info("""
    **Brend je samo za prikaz**

    Ako trgovac ima ružan naziv kao `"VODOVOD"JKP CACAK 123`, možeš ga mapirati da se prikazuje kao `JKP Vodovod Čačak`.
    """)

    st.warning("""
    **Posle mapiranja iz "Ostalo", pritisni F5**

    Zbog načina kako Streamlit radi sa formama, stranica se ne osvežava automatski. Pritisni F5 da vidiš promene.
    """)

    st.divider()

    # FAQ
    st.markdown("### ❓ Česta pitanja")

    with st.expander("Zašto se transakcija ne pomera iz 'Ostalo'?"):
        st.markdown("""
        Mogući razlozi:
        1. **Ključna reč je previše specifična** - probaj kraću (npr. `KAFANA` umesto `KAFANACACAK 688`)
        2. **Nisi pritisnuo F5** - posle mapiranja osveži stranicu
        3. **Greška u kucanju** - proveri da li je ključna reč tačno uneta
        """)

    with st.expander("Kako da obrišem pogrešno mapiranje?"):
        st.markdown("""
        1. Idi na **⚙️ Podešavanja**
        2. Pronađi kategoriju ili brend
        3. Obriši pogrešnu ključnu reč ili varijantu
        4. Klikni **Sačuvaj**
        """)

    with st.expander("Kako da resetujem sve na početne vrednosti?"):
        st.markdown("""
        1. Idi na **⚙️ Podešavanja**
        2. Skroluj do **🔧 Alati**
        3. Klikni **🔄 Resetuj na podrazumevane vrednosti**
        """)

    with st.expander("Mogu li da dodam novu kategoriju?"):
        st.markdown("""
        Da!
        1. Idi na **⚙️ Podešavanja** → **📂 Kategorije**
        2. Unesi naziv nove kategorije (npr. `🎮 Gaming`)
        3. Dodaj prvu ključnu reč
        4. Klikni **Dodaj kategoriju**
        """)


# ===== MAIN APP =====

def main():
    # Sidebar navigation (Intesa style)
    with st.sidebar:
        # Logo
        st.markdown("""
        <div class="sidebar-logo">
            <svg width="55" height="55" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
                <defs>
                    <linearGradient id="logoGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                        <stop offset="0%" style="stop-color:#667eea"/>
                        <stop offset="100%" style="stop-color:#764ba2"/>
                    </linearGradient>
                </defs>
                <circle cx="50" cy="50" r="45" fill="#1a1a2e" stroke="url(#logoGrad)" stroke-width="4"/>
                <path d="M25 65 L40 45 L55 55 L75 30" stroke="url(#logoGrad)" stroke-width="5" fill="none" stroke-linecap="round"/>
                <circle cx="75" cy="30" r="6" fill="#764ba2"/>
                <text x="50" y="82" text-anchor="middle" fill="#667eea" font-size="14" font-weight="bold">RSD</text>
            </svg>
            <span class="sidebar-logo-text">Troškomer</span>
        </div>
        <p class="sidebar-subtitle">Analiza bankovnih izvoda</p>
        """, unsafe_allow_html=True)

        st.divider()

        # Navigation with styled buttons
        if 'current_page' not in st.session_state:
            st.session_state['current_page'] = "pocetna"

        # Navigation buttons
        if st.button("🏠  Početna", use_container_width=True,
                     type="primary" if st.session_state['current_page'] == "pocetna" else "secondary"):
            st.session_state['current_page'] = "pocetna"
            st.rerun()

        if st.button("📂  Izvodi", use_container_width=True,
                     type="primary" if st.session_state['current_page'] == "izvodi" else "secondary"):
            st.session_state['current_page'] = "izvodi"
            st.rerun()

        if st.button("📅  Mesečni prikaz", use_container_width=True,
                     type="primary" if st.session_state['current_page'] == "mesecni" else "secondary"):
            st.session_state['current_page'] = "mesecni"
            st.rerun()

        if st.button("⚙️  Podešavanja", use_container_width=True,
                     type="primary" if st.session_state['current_page'] == "podesavanja" else "secondary"):
            st.session_state['current_page'] = "podesavanja"
            st.rerun()

        if st.button("📖  Pomoć", use_container_width=True,
                     type="primary" if st.session_state['current_page'] == "pomoc" else "secondary"):
            st.session_state['current_page'] = "pomoc"
            st.rerun()

        st.divider()

        # Quick stats
        saved_periods = get_saved_periods()
        if saved_periods:
            st.caption(f"📊 {len(saved_periods)} učitanih izvoda")

    # Page routing
    if st.session_state.get('current_page') == "pocetna":
        page_pocetna()
    elif st.session_state.get('current_page') == "izvodi":
        page_izvodi()
    elif st.session_state.get('current_page') == "mesecni":
        page_mesecni_prikaz()
    elif st.session_state.get('current_page') == "podesavanja":
        page_podesavanja()
    elif st.session_state.get('current_page') == "pomoc":
        page_pomoc()


if __name__ == "__main__":
    main()
