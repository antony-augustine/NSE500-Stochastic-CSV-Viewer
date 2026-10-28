import streamlit as st
import pandas as pd
from io import BytesIO

# ==========================================================
# PAGE CONFIGURATION
# ==========================================================

st.set_page_config(
    page_title="NSE 500 Stochastic Scanner",
    page_icon="📊",
    layout="wide"
)

st.title("📊 NSE 500 Stochastic Scanner")
st.caption("Display selected CSV fields, filter stocks, and export results.")

# ==========================================================
# UPLOAD CSV FILE
# ==========================================================

uploaded_file = st.file_uploader(
    "Upload NSE 500 Stochastic CSV file",
    type=["csv"]
)

if uploaded_file is None:
    st.info("Please upload NSE500_Stochastic_1433_All.csv to continue.")
    st.stop()

try:
    df = pd.read_csv(uploaded_file)
except Exception as e:
    st.error(f"Unable to read CSV file: {e}")
    st.stop()

if df.empty:
    st.warning("The uploaded CSV file contains no records.")
    st.stop()

# Remove completely empty columns
df = df.dropna(axis=1, how="all")

# ==========================================================
# DEFAULT SELECTED FIELDS
# ==========================================================

preferred_fields = [
    "Ticker",
    "Date",
    "Close",
    #"Stoch_%K",
    #"Stoch_%D",
    "Zone",
    "Signal",
    #"Last_Crossover_Date",
    #"Last_Crossover_Type",
    #"Crossover_Close",
    #"Pct_Change_Since_Crossover",
    #"Trading_Days_Since_Crossover",
    "Last_Signal_Date",
    "Last_Signal",
    "Pct_Change_Since_Last_Signal",
    "TDays_Since_Last_Signal",
    "Chart"
]

default_fields = [
    col for col in preferred_fields
    if col in df.columns
]

if not default_fields:
    default_fields = df.columns.tolist()[:8]

# ==========================================================
# SIDEBAR: FIELD SELECTION
# ==========================================================

st.sidebar.header("Display Settings")

selected_fields = st.sidebar.multiselect(
    "Select CSV fields to display",
    options=df.columns.tolist(),
    default=default_fields
)

if not selected_fields:
    st.warning("Please select at least one field.")
    st.stop()

# ==========================================================
# SEARCH AND FILTERS
# ==========================================================

st.sidebar.header("Filters")

filtered_df = df.copy()

# Search by ticker
if "Ticker" in df.columns:
    ticker_search = st.sidebar.text_input(
        "Search stock symbol"
    )

    if ticker_search.strip():
        filtered_df = filtered_df[
            filtered_df["Ticker"]
            .astype(str)
            .str.contains(
                ticker_search.strip(),
                case=False,
                na=False
            )
        ]

# Filter by current crossover signal
if "Signal" in df.columns:
    signal_values = sorted(
        df["Signal"].dropna().astype(str).unique().tolist()
    )

    selected_signals = st.sidebar.multiselect(
        "Current crossover signal",
        options=signal_values,
        default=signal_values
    )

    if selected_signals:
        filtered_df = filtered_df[
            filtered_df["Signal"]
            .astype(str)
            .isin(selected_signals)
        ]
    else:
        filtered_df = filtered_df.iloc[0:0]

# Filter by last crossover type
if "Last_Crossover_Type" in df.columns:
    crossover_values = sorted(
        df["Last_Crossover_Type"]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

    selected_crossovers = st.sidebar.multiselect(
        "Last crossover type",
        options=crossover_values,
        default=crossover_values
    )

    if selected_crossovers:
        filtered_df = filtered_df[
            filtered_df["Last_Crossover_Type"]
            .astype(str)
            .isin(selected_crossovers)
        ]
    else:
        filtered_df = filtered_df.iloc[0:0]

# Filter by Stochastic zone
if "Zone" in df.columns:
    zone_values = sorted(
        df["Zone"].dropna().astype(str).unique().tolist()
    )

    selected_zones = st.sidebar.multiselect(
        "Stochastic zone",
        options=zone_values,
        default=zone_values
    )

    if selected_zones:
        filtered_df = filtered_df[
            filtered_df["Zone"].astype(str).isin(selected_zones)
        ]
    else:
        filtered_df = filtered_df.iloc[0:0]

# ==========================================================
# SUMMARY METRICS
# ==========================================================

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Total CSV Records",
    f"{len(df):,}"
)

col2.metric(
    "Filtered Stocks",
    f"{len(filtered_df):,}"
)

if "Last_Crossover_Type" in filtered_df.columns:
    bullish_count = (
        filtered_df["Last_Crossover_Type"]
        .astype(str)
        .str.lower()
        .eq("bullish")
        .sum()
    )
else:
    bullish_count = 0

if "Last_Crossover_Type" in filtered_df.columns:
    bearish_count = (
        filtered_df["Last_Crossover_Type"]
        .astype(str)
        .str.lower()
        .eq("bearish")
        .sum()
    )
else:
    bearish_count = 0

col3.metric("Last Bullish Crossover", f"{bullish_count:,}")
col4.metric("Last Bearish Crossover", f"{bearish_count:,}")

# ==========================================================
# DISPLAY TABLE
# ==========================================================

st.subheader("Stock Results")

# Show only the selected columns
display_df = filtered_df[selected_fields].copy()

# Format date columns where possible
for col in display_df.columns:
    if "Date" in col:
        display_df[col] = display_df[col].astype("string")

# Display TradingView charts as clickable links
column_config = {}

if "Chart" in display_df.columns:
    column_config["Chart"] = st.column_config.LinkColumn(
        "TradingView Chart",
        display_text="Open Chart"
    )

if "Yahoo Finance" in display_df.columns:
    column_config["Yahoo Finance"] = st.column_config.LinkColumn(
        "Yahoo Finance",
        display_text="Open Yahoo"
    )

if "News" in display_df.columns:
    column_config["News"] = st.column_config.LinkColumn(
        "Stock News",
        display_text="Open News"
    )

st.dataframe(
    display_df,
    column_config=column_config,
    use_container_width=True,
    hide_index=True,
    height=600
)

# ==========================================================
# DOWNLOAD FILTERED RESULTS
# ==========================================================

st.subheader("Export Results")

csv_data = filtered_df[selected_fields].to_csv(
    index=False
).encode("utf-8-sig")

st.download_button(
    label="📥 Download Selected Fields as CSV",
    data=csv_data,
    file_name="NSE500_Stochastic_Selected_Fields.csv",
    mime="text/csv"
)

# ==========================================================
# FOOTER
# ==========================================================

st.caption(
    f"Displaying {len(display_df):,} records "
    f"and {len(selected_fields)} selected fields."
)