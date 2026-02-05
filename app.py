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
    layout="wide"
)

# Custom CSS and Logo
LOGO_SVG = """
<svg width="50" height="50" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
  <circle cx="50" cy="50" r="45" fill="#1a1a2e" stroke="#667eea" stroke-width="3"/>
  <path d="M25 65 L40 45 L55 55 L75 30" stroke="#667eea" stroke-width="4" fill="none" stroke-linecap="round"/>
  <circle cx="75" cy="30" r="5" fill="#764ba2"/>
  <text x="50" y="82" text-anchor="middle" fill="#667eea" font-size="14" font-weight="bold">RSD</text>
</svg>
"""

st.markdown(f"""
<style>
    .troskomer-header {{
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 10px;
    }}
    .troskomer-logo {{
        font-size: 38px !important;
        font-weight: 800 !important;
        color: #000000 !important;
        margin: 0 !important;
        letter-spacing: -1px;
    }}
    .troskomer-subtitle {{
        font-size: 14px !important;
        color: #666 !important;
        margin-top: -5px !important;
    }}
</style>
""", unsafe_allow_html=True)

# Data storage folder
DATA_DIR = Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)
STATEMENTS_DIR = DATA_DIR / "statements"
STATEMENTS_DIR.mkdir(exist_ok=True)

# Categories configuration
CATEGORIES = {
    "🏥 Apoteke": [
        "LILLY", "APOTEKA", "VIDAKOVI", "VUCKOVIC", "KRSENKOVIC", "BENU"
    ],
    "🩺 Zdravstveni pregledi i analize": [
        "MEDILAB", "DRPISCEVIC", "DR PISCEVIC", "MEDILEK", "MEDILEKCACAK", "NATASA RANDJELOVIC", "RANDJELOVICPR"
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
        "STRADIVARIUS", "MASSIMO", "LC WAIKIKI", "NEW YORKER", "C&A",
        "DEICHMANN", "OFFICE SHOES", "BUZZ", "SPORT VISION", "PLANETBIKE", "TOMTAILOR", "TOM TAILOR",
        "TAKKO", "TAKKOFASHION", "KIDSBEBA", "PLANETASPORT", "PLANETA SPORT"
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
        "VELVET", "GALIJA", "CASTELLO", "GALLERY", "MORAVSKIALASI", "PEKARA", "PONS"
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


# Brand normalization
BRAND_MAPPING = {
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

    for category, keywords in CATEGORIES.items():
        for keyword in keywords:
            if keyword.upper() in text:
                return category

    return "❓ Ostalo"


def normalize_merchant(merchant, description=""):
    """Normalize merchant name to a common brand."""
    merchant_upper = str(merchant).upper()
    desc_upper = str(description).upper()

    # Combine merchant and description for matching
    text = f"{merchant_upper} {desc_upper}"

    for brand, keywords in BRAND_MAPPING.items():
        for keyword in keywords:
            if keyword.upper() in text:
                return brand

    # Handle empty/nan merchant
    if merchant_upper in ["NAN", "", "NONE"] or pd.isna(merchant):
        if any(kw in desc_upper for kw in ["NAKNADA", "ODRZAVANJE", "MESECNO"]):
            return "ODRŽAVANJE RAČUNA"
        return "Nepoznato"

    cleaned = str(merchant).replace("\n", " ").strip()
    if len(cleaned) > 30:
        cleaned = cleaned[:30] + "..."
    return cleaned


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


def get_month_name(month):
    """Get Serbian month name."""
    months = {
        1: "Januar", 2: "Februar", 3: "Mart", 4: "April",
        5: "Maj", 6: "Jun", 7: "Jul", 8: "Avgust",
        9: "Septembar", 10: "Oktobar", 11: "Novembar", 12: "Decembar"
    }
    return months.get(month, str(month))


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

    csv_path = period_dir / "transactions.csv"
    df.to_csv(csv_path, index=False)

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
                # Re-categorize each transaction
                df["Kategorija"] = df.apply(
                    lambda row: categorize_transaction(row["Opis"], row["Primalac/Platilac"]),
                    axis=1
                )
                # Save updated CSV
                df.to_csv(csv_path, index=False)

                # Update metadata
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


def display_global_stats(df):
    """Display statistics across all periods."""
    expenses_df = df[df["Isplata"] > 0].copy()

    # Exclude "Ostalo" category from statistics
    expenses_df = expenses_df[expenses_df["Kategorija"] != "❓ Ostalo"]

    if expenses_df.empty:
        st.info("Nema podataka za prikaz")
        return

    expenses_df["Brend"] = expenses_df.apply(
        lambda row: normalize_merchant(row["Primalac/Platilac"], row["Opis"]), axis=1
    )

    # Monthly totals per category
    monthly_cat = expenses_df.groupby(["Period", "Kategorija"])["Isplata"].sum().reset_index()
    cat_stats = monthly_cat.groupby("Kategorija")["Isplata"].agg(["max", "mean", "sum"]).sort_values("sum", ascending=False)

    top_category = cat_stats.index[0]
    top_cat_max = cat_stats.loc[top_category, "max"]
    top_cat_avg = cat_stats.loc[top_category, "mean"]

    # Get top brand in top category
    top_cat_df = expenses_df[expenses_df["Kategorija"] == top_category]
    brand_totals = top_cat_df.groupby("Brend")["Isplata"].sum().sort_values(ascending=False)
    top_brand = brand_totals.index[0]

    # Display insights
    st.subheader("🎯 Gde najviše trošiš?")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Kategorija #1:**")
        st.markdown(f"### {top_category}")
        st.caption(f"Max mesec: {top_cat_max:,.0f} RSD | Prosek/mesec: {top_cat_avg:,.0f} RSD")

    with col2:
        st.markdown("**Najviše u toj kategoriji:**")
        st.markdown(f"### {top_brand}")

    st.divider()

    # Full ranking
    st.subheader("📊 Rang lista kategorija")

    for i, category in enumerate(cat_stats.index, 1):
        cat_max = cat_stats.loc[category, "max"]
        cat_avg = cat_stats.loc[category, "mean"]

        # Get top brand for this category
        cat_df = expenses_df[expenses_df["Kategorija"] == category]
        cat_brands = cat_df.groupby("Brend")["Isplata"].sum().sort_values(ascending=False)
        top_brand_in_cat = cat_brands.index[0] if len(cat_brands) > 0 else "-"

        with st.expander(f"**#{i} {category}** — Max mesec: {cat_max:,.0f} RSD | Prosek/mesec: {cat_avg:,.0f} RSD"):
            # Monthly stats for top brand
            top_brand_monthly = expenses_df[(expenses_df["Kategorija"] == category) & (expenses_df["Brend"] == top_brand_in_cat)]
            top_brand_monthly_totals = top_brand_monthly.groupby("Period")["Isplata"].sum()
            top_brand_max = top_brand_monthly_totals.max() if len(top_brand_monthly_totals) > 0 else 0
            top_brand_avg = top_brand_monthly_totals.mean() if len(top_brand_monthly_totals) > 0 else 0
            st.markdown(f"🥇 **Najviše trošiš na:** {top_brand_in_cat} — Max mesec: {top_brand_max:,.0f} | Prosek/mesec: {top_brand_avg:,.0f} RSD")

            if len(cat_brands) > 1:
                st.caption("Ostali:")
                for j, (brand, _) in enumerate(cat_brands.items()):
                    if j == 0:
                        continue
                    if j > 5:
                        st.caption(f"... i još {len(cat_brands) - 5} trgovaca")
                        break
                    # Monthly stats per brand
                    brand_monthly = expenses_df[(expenses_df["Kategorija"] == category) & (expenses_df["Brend"] == brand)]
                    brand_monthly_totals = brand_monthly.groupby("Period")["Isplata"].sum()
                    brand_max = brand_monthly_totals.max()
                    brand_avg = brand_monthly_totals.mean()
                    st.write(f"• {brand} — Max mesec: {brand_max:,.0f} | Prosek/mesec: {brand_avg:,.0f} RSD")


def create_export_data(df):
    """Create summary export data with categories and brands."""
    expenses_df = df[df["Isplata"] > 0].copy()
    expenses_df["Brend"] = expenses_df.apply(
        lambda row: normalize_merchant(row["Primalac/Platilac"], row["Opis"]), axis=1
    )

    # Summary by category
    cat_summary = expenses_df.groupby("Kategorija")["Isplata"].agg(["sum", "count"])
    cat_summary.columns = ["Ukupno (RSD)", "Br. transakcija"]
    cat_summary = cat_summary.sort_values("Ukupno (RSD)", ascending=False).reset_index()

    # Summary by brand
    brand_summary = expenses_df.groupby(["Kategorija", "Brend"])["Isplata"].agg(["sum", "count"])
    brand_summary.columns = ["Ukupno (RSD)", "Br. transakcija"]
    brand_summary = brand_summary.sort_values("Ukupno (RSD)", ascending=False).reset_index()

    return cat_summary, brand_summary, expenses_df


def create_excel_export(df, period_name=""):
    """Create Excel file with multiple sheets."""
    cat_summary, brand_summary, expenses_df = create_export_data(df)

    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        # Sheet 1: All transactions
        df.to_excel(writer, sheet_name='Sve transakcije', index=False)

        # Sheet 2: By category
        cat_summary.to_excel(writer, sheet_name='Po kategorijama', index=False)

        # Sheet 3: By brand
        brand_summary.to_excel(writer, sheet_name='Po brendovima', index=False)

        # Auto-fit columns
        for sheet_name in writer.sheets:
            worksheet = writer.sheets[sheet_name]
            worksheet.set_column(0, 10, 20)

    output.seek(0)
    return output.getvalue()


def display_statement(df, period_name=None):
    """Display the statement analysis."""

    # Summary metrics
    expenses_df = df[df["Isplata"] > 0].copy()
    income_df = df[df["Uplata"] > 0].copy()

    total_expenses = expenses_df["Isplata"].sum()
    total_income = income_df["Uplata"].sum()
    balance = total_income - total_expenses

    # Metrics row
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("💵 Primanja", f"{total_income:,.0f} RSD")
    with col2:
        st.metric("💸 Potrošnja", f"{total_expenses:,.0f} RSD")
    with col3:
        st.metric("📊 Bilans", f"{balance:,.0f} RSD", delta=f"{balance:,.0f}")
    with col4:
        st.metric("📝 Transakcija", len(df))

    st.divider()

    st.subheader("💸 Potrošnja po kategorijama")

    category_totals = expenses_df.groupby("Kategorija")["Isplata"].agg(["sum", "count"])
    category_totals.columns = ["Ukupno (RSD)", "Br. transakcija"]
    category_totals = category_totals.sort_values("Ukupno (RSD)", ascending=False)

    for category in category_totals.index:
        total = category_totals.loc[category, "Ukupno (RSD)"]
        count = int(category_totals.loc[category, "Br. transakcija"])

        with st.expander(f"{category} — **{total:,.2f} RSD** ({count} transakcija)"):
            cat_transactions = expenses_df[expenses_df["Kategorija"] == category].copy()
            cat_transactions["Brend"] = cat_transactions.apply(
                lambda row: normalize_merchant(row["Primalac/Platilac"], row["Opis"]), axis=1
            )

            merchant_totals = cat_transactions.groupby("Brend")["Isplata"].agg(["sum", "count"])
            merchant_totals.columns = ["Ukupno (RSD)", "Br. kupovina"]
            merchant_totals = merchant_totals.sort_values("Ukupno (RSD)", ascending=False)

            # Show each brand with nested expander for transactions
            for brand in merchant_totals.index:
                brand_total = merchant_totals.loc[brand, "Ukupno (RSD)"]
                brand_count = int(merchant_totals.loc[brand, "Br. kupovina"])

                with st.expander(f"**{brand}** — {brand_total:,.2f} RSD ({brand_count} kupovina)"):
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


def main():
    # Get saved periods
    saved_periods = get_saved_periods()

    # ===== SIDEBAR =====
    with st.sidebar:
        st.markdown(f'<div class="troskomer-header">{LOGO_SVG}<h1 class="troskomer-logo">Troškomer</h1></div>', unsafe_allow_html=True)
        st.markdown('<p class="troskomer-subtitle">Analiza bankovnih izvoda</p>', unsafe_allow_html=True)
        st.divider()

        # Upload section
        st.subheader("📤 Učitaj izvod")

        # Initialize uploader key counter
        if 'uploader_key' not in st.session_state:
            st.session_state['uploader_key'] = 0

        uploaded_file = st.file_uploader(
            "PDF fajl",
            type="pdf",
            help="Banca Intesa mesečni izvod",
            label_visibility="collapsed",
            key=f"pdf_uploader_{st.session_state['uploader_key']}"
        )

        # Show success message if just uploaded
        if st.session_state.get('upload_success'):
            st.success(f"✅ Uspešno učitan izvod: {st.session_state['upload_success']}")
            del st.session_state['upload_success']

        if uploaded_file is not None:
            pdf_bytes = uploaded_file.read()
            original_filename = uploaded_file.name

            with st.spinner("Učitavam..."):
                df_new = extract_transactions_from_pdf(BytesIO(pdf_bytes))

                if not df_new.empty:
                    month, year = detect_statement_period(df_new)
                    if month and year:
                        save_statement(df_new, month, year, pdf_bytes, original_filename)
                        st.session_state['upload_success'] = f"{get_month_name(month)} {year}"
                        st.session_state['uploader_key'] += 1  # Reset uploader
                        st.rerun()

        st.divider()

        # Saved statements list
        st.subheader("📂 Sačuvani izvodi")

        if not saved_periods:
            st.info("Nema izvoda")
        else:
            # View mode selector
            view_mode = st.radio(
                "Prikaz:",
                options=["pojedinacni", "statistika"],
                format_func=lambda x: "📅 Pojedinačni mesec" if x == "pojedinacni" else "📊 Ukupna statistika",
                horizontal=True
            )

            selected_key = None
            if view_mode == "pojedinacni":
                # Period selector
                selected_key = st.radio(
                    "Odaberi period:",
                    options=[p["key"] for p in saved_periods],
                    format_func=lambda k: next(p["name"] for p in saved_periods if p["key"] == k),
                    label_visibility="collapsed"
                )

            if view_mode == "pojedinacni" and selected_key:
                # Delete button
                if st.button("🗑️ Obriši odabrani", use_container_width=True):
                    if delete_statement(selected_key):
                        st.rerun()

                st.divider()

                # Export button
                st.subheader("📥 Preuzmi")
                if st.button("📊 Generiši Excel", use_container_width=True):
                    df_export, _ = load_statement(selected_key)
                    if df_export is not None:
                        selected_name = next(p["name"] for p in saved_periods if p["key"] == selected_key)
                        st.session_state['excel_data'] = create_excel_export(df_export, selected_name)
                        st.session_state['excel_filename'] = f"izvod_{selected_key}.xlsx"

                if 'excel_data' in st.session_state:
                    st.download_button(
                        "⬇️ Preuzmi Excel",
                        st.session_state['excel_data'],
                        st.session_state['excel_filename'],
                        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True
                    )

            # Recategorize button (always visible when there are periods)
            st.divider()
            st.subheader("🔄 Alati")

            # Show success message if just recategorized
            if st.session_state.get('recategorize_success'):
                st.success(st.session_state['recategorize_success'])
                del st.session_state['recategorize_success']

            if st.button("🔄 Rekategorizuj sve", use_container_width=True, help="Ponovo primeni pravila kategorisanja na sve izvode"):
                with st.spinner("Rekategorizujem izvode..."):
                    count = recategorize_all_statements()
                st.session_state['recategorize_success'] = f"✅ Uspešno rekategorizovano {count} izvoda!"
                st.rerun()


    # ===== MAIN CONTENT =====
    if not saved_periods:
        st.markdown('<h1 class="troskomer-logo">Troškomer</h1>', unsafe_allow_html=True)
        st.info("👈 Učitaj prvi izvod preko sidebar-a")
    elif view_mode == "statistika":
        # Big statistics header
        stats_logo = """<svg width="80" height="80" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg"><circle cx="50" cy="50" r="45" fill="#1a1a2e" stroke="#667eea" stroke-width="3"/><rect x="20" y="55" width="12" height="25" fill="#667eea" rx="2"/><rect x="37" y="40" width="12" height="40" fill="#764ba2" rx="2"/><rect x="54" y="30" width="12" height="50" fill="#667eea" rx="2"/><rect x="71" y="20" width="12" height="60" fill="#764ba2" rx="2"/></svg>"""

        st.markdown(f'<div style="display: flex; align-items: center; gap: 20px; margin-bottom: 20px;">{stats_logo}<div><h1 style="margin: 0; font-size: 36px; font-weight: 800;">Ukupna Statistika</h1><p style="margin: 5px 0 0 0; font-size: 18px; color: #666;">Analiza svih učitanih izvoda</p></div></div>', unsafe_allow_html=True)
        st.divider()
        all_df = load_all_statements()
        if not all_df.empty:
            display_global_stats(all_df)
        else:
            st.info("Nema podataka")
    elif selected_key is None:
        st.markdown('<h1 class="troskomer-logo">Troškomer</h1>', unsafe_allow_html=True)
        st.info("👈 Odaberi izvod iz liste")
    else:
        # Load and display selected statement
        df, metadata = load_statement(selected_key)
        if df is not None:
            selected_name = next(p["name"] for p in saved_periods if p["key"] == selected_key)
            st.title(f"📅 {selected_name}")
            display_statement(df, selected_name)


if __name__ == "__main__":
    main()
