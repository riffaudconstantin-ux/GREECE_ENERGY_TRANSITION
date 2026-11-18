import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import html

# =====================================================
# PAGE CONFIGURATION
# =====================================================

st.set_page_config(
    page_title="Greece Energy Transition",
    page_icon="🇬🇷",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =====================================================
# GLOBAL DESIGN
# =====================================================

st.markdown("""
<style>
:root {
    color-scheme: dark;
}

.stApp,
[data-testid="stAppViewContainer"],
[data-testid="stMain"] {
    background-color: #0b0e14 !important;
    color: #F5F7FA !important;
}

.stApp p,
.stApp li,
.stApp label {
    color: #E6EAF0 !important;
}

h1, h2, h3, h4, h5 {
    color: #FFFFFF !important;
}

[data-testid="stCaption"] {
    color: #B8C4D3 !important;
}

[data-testid="stSidebar"] {
    background-color: #171E29 !important;
}

[data-testid="stSidebar"] * {
    color: #F5F7FA !important;
}

[data-testid="stMetric"] {
    background-color: #171E29 !important;
    border: 1px solid #354256 !important;
    padding: 18px !important;
    border-radius: 8px !important;
}

[data-testid="stMetricLabel"] {
    color: #C5CFDD !important;
}

[data-testid="stMetricValue"] {
    color: #FFAD5C !important;
}

[data-testid="stMetricDelta"] {
    background-color: transparent !important;
    color: #8FE0B5 !important;
}

[data-testid="stMetricDelta"] span {
    color: #8FE0B5 !important;
    background-color: transparent !important;
}

[data-baseweb="select"] > div {
    background-color: #202A38 !important;
    border-color: #526176 !important;
    color: #FFFFFF !important;
}

[data-baseweb="select"] * {
    color: #FFFFFF !important;
}

[data-baseweb="popover"],
[data-baseweb="menu"] {
    background-color: #202A38 !important;
}

[data-baseweb="popover"] *,
[data-baseweb="menu"] * {
    color: #FFFFFF !important;
}

[data-baseweb="tag"] {
    background-color: #34445B !important;
    color: #FFFFFF !important;
}

[data-baseweb="tag"] span {
    color: #FFFFFF !important;
}

.stTextInput input,
.stNumberInput input,
.stDateInput input {
    background-color: #202A38 !important;
    color: #FFFFFF !important;
    border-color: #526176 !important;
}

.stButton button {
    background-color: #26364B !important;
    color: #FFFFFF !important;
    border: 1px solid #526176 !important;
}

[data-testid="stAlert"] {
    background-color: #1B3047 !important;
    border: 1px solid #42688F !important;
    border-radius: 9px !important;
}

[data-testid="stAlert"] * {
    color: #FFFFFF !important;
}

[data-testid="stExpander"] {
    background-color: #171E29 !important;
    border: 1px solid #354256 !important;
}

[data-testid="stExpander"] summary,
[data-testid="stExpander"] summary * {
    color: #FFFFFF !important;
}

[data-testid="stTabs"] button {
    color: #DCE3ED !important;
}

[data-testid="stTabs"] button[aria-selected="true"] {
    color: #FFAD5C !important;
}

[data-testid="stDataFrame"] {
    border: 1px solid #354256 !important;
}

hr {
    border-color: #354256 !important;
}

a {
    color: #78BDF5 !important;
}

div[data-testid="stMarkdownContainer"] a {
    color: #78BDF5 !important;
}

</style>
""", unsafe_allow_html=True)


# =====================================================
# CUSTOM NOTICE
# =====================================================

def show_notice(message, kind="info"):

    styles = {
        "info": ("#1B3047", "#42688F"),
        "success": ("#173528", "#347A55"),
        "warning": ("#40351D", "#A17A32"),
        "error": ("#401F26", "#963F4D")
    }

    background, border = styles.get(
        kind, styles["info"]
    )

    safe_message = html.escape(str(message))

    st.markdown(
        f"""
        <div style="
            background-color: {background};
            border: 1px solid {border};
            border-radius: 9px;
            padding: 18px 22px;
            margin: 12px 0;
            color: #FFFFFF !important;
            font-size: 16px;
            line-height: 1.6;
        ">
            <span style="color:#FFFFFF !important;">
                {safe_message}
            </span>
        </div>
        """,
        unsafe_allow_html=True
    )


# =====================================================
# CHART DESIGN
# =====================================================

def apply_chart_design(fig):

    fig.update_layout(
        paper_bgcolor="#0b0e14",
        plot_bgcolor="#0b0e14",

        font=dict(
            family="Arial",
            color="#FFFFFF",
            size=14
        ),

        title=dict(
            font=dict(color="#FFFFFF", size=21)
        ),

        legend=dict(
            title_font=dict(color="#FFFFFF", size=15),
            font=dict(color="#FFFFFF", size=14),
            bgcolor="#202A38",
            bordercolor="#526176",
            borderwidth=1
        ),

        xaxis=dict(
            title_font=dict(color="#FFFFFF"),
            tickfont=dict(color="#FFFFFF"),
            gridcolor="#354256"
        ),

        yaxis=dict(
            title_font=dict(color="#FFFFFF"),
            tickfont=dict(color="#FFFFFF"),
            gridcolor="#354256"
        ),

        hoverlabel=dict(
            bgcolor="#202A38",
            bordercolor="#526176",
            font=dict(color="#FFFFFF", size=13)
        )
    )

    return fig


# =====================================================
# LOAD ELECTRICITY GENERATION DATA
# =====================================================

DATA_PATH = Path("data/greece_energy.csv")

if not DATA_PATH.exists():
    show_notice("Electricity dataset not found.", "error")
    st.stop()

df = pd.read_csv(DATA_PATH)

required_columns = [
    "date", "fuel_code", "fuel",
    "value", "unit", "source"
]

if not all(column in df.columns for column in required_columns):
    show_notice("Electricity dataset has missing columns.", "error")
    st.stop()

df["value"] = pd.to_numeric(df["value"], errors="coerce")

df["date"] = pd.to_datetime(
    df["date"],
    format="%Y-%m",
    errors="coerce"
)

df = df.dropna(
    subset=["value", "date", "fuel_code"]
)

df["year"] = df["date"].dt.year


# =====================================================
# LOAD ENERGY SECURITY DATA
# =====================================================

SECURITY_PATH = Path("data/security_data.csv")

security = None

if SECURITY_PATH.exists():

    security = pd.read_csv(SECURITY_PATH)

    security["value"] = pd.to_numeric(
        security["value"], errors="coerce"
    )

    security["year"] = pd.to_numeric(
        security["date"], errors="coerce"
    )

    security = security.dropna(
        subset=["value", "year"]
    )

    security["year"] = security["year"].astype(int)


# =====================================================
# LOAD REGIONAL DATA
# =====================================================

REGIONAL_PATH = Path("data/regional_data.csv")

regional = None

if REGIONAL_PATH.exists():

    regional = pd.read_csv(REGIONAL_PATH)

    regional["value"] = pd.to_numeric(
        regional["value"], errors="coerce"
    )

    regional["year"] = pd.to_numeric(
        regional["year"], errors="coerce"
    )

    regional = regional.dropna(
        subset=["value", "year"]
    )

    regional["year"] = regional["year"].astype(int)


# =====================================================
# LOAD LIGNITE EMPLOYMENT DATA
# =====================================================

LIGNITE_EMPLOYMENT_PATH = Path("data/lignite_employment.csv")
lignite_employment = None

if LIGNITE_EMPLOYMENT_PATH.exists():
    try:
        lignite_employment = pd.read_csv(LIGNITE_EMPLOYMENT_PATH)

        required_lignite_columns = [
            "year", "value", "region", "scope"
        ]

        if not all(
            column in lignite_employment.columns
            for column in required_lignite_columns
        ):
            lignite_employment = None

        else:

            lignite_employment["year"] = pd.to_numeric(
                lignite_employment["year"], errors="coerce"
            )

            lignite_employment["value"] = pd.to_numeric(
                lignite_employment["value"], errors="coerce"
            )

            lignite_employment = lignite_employment.dropna(
                subset=["year", "value"]
            ).sort_values("year")

            lignite_employment["year"] = (
                lignite_employment["year"].astype(int)
            )

            if lignite_employment.empty:
                lignite_employment = None

    except Exception:
        lignite_employment = None


# =====================================================
# SIDEBAR
# =====================================================

st.sidebar.title("🇬🇷 GREECE ENERGY")

st.sidebar.caption("ENERGY TRANSITION INTELLIGENCE")

st.sidebar.divider()

page = st.sidebar.radio(
    "NAVIGATION",
    [
        "Executive Overview",
        "Electricity Generation",
        "Annual Energy Mix",
        "Energy Security",
        "Regional Development",
        "International Comparison",
        "Financing Simulator"
    ]
)

st.sidebar.divider()

st.sidebar.caption("DATA SOURCE: EUROSTAT")
st.sidebar.caption("GENERATION DATA: 2008–2026")

if security is not None:
    st.sidebar.caption("SECURITY DATA: 1990–2025")

if regional is not None:
    st.sidebar.caption("REGIONAL DATA: 1999–2025")

st.sidebar.divider()

st.sidebar.markdown("### DATA PROVENANCE")

st.sidebar.markdown(
    "[Eurostat – Electricity Generation](https://ec.europa.eu/eurostat/databrowser/view/nrg_cb_pem/default/table)"
)

st.sidebar.markdown(
    "[Eurostat – Energy Security](https://ec.europa.eu/eurostat/databrowser/view/nrg_ind_id/default/table)"
)

st.sidebar.markdown(
    "[Eurostat – Regional GDP](https://ec.europa.eu/eurostat/databrowser/view/nama_10r_2gdp/default/table)"
)


# =====================================================
# EXECUTIVE OVERVIEW
# =====================================================

if page == "Executive Overview":

    st.title("GREECE ENERGY TRANSITION")

    st.caption(
        "NATIONAL ENERGY TRANSITION | STRATEGIC ANALYSIS"
    )

    st.divider()

    st.subheader("Electricity System Overview")

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "OBSERVATIONS",
        f"{len(df):,}"
    )

    col2.metric(
        "FIRST PERIOD",
        df["date"].min().strftime("%b %Y")
    )

    col3.metric(
        "LATEST PERIOD",
        df["date"].max().strftime("%b %Y")
    )

    st.divider()

    st.subheader("Strategic Assessment")

    col1, col2 = st.columns(2)

    with col1:

        st.markdown("### Climate Transition")

        st.write(
            "Assessment of electricity generation trends, "
            "renewable energy deployment and fossil fuel reduction."
        )

        st.markdown("### Energy Security")

        st.write(
            "Analysis of natural gas exposure, electricity imports "
            "and system flexibility."
        )

    with col2:

        st.markdown("### Regional Development")

        st.write(
            "Assessment of employment impacts, regional investment "
            "and economic diversification."
        )

        st.markdown("### Transition Financing")

        st.write(
            "Assessment of European funding, public investment "
            "and private capital."
        )

    st.divider()

    show_notice(
        "Historical electricity generation data retrieved from Eurostat.",
        "info"
    )


# =====================================================
# ELECTRICITY GENERATION
# =====================================================

elif page == "Electricity Generation":

    st.title("ELECTRICITY GENERATION")

    st.caption("GREECE | MONTHLY NET ELECTRICITY GENERATION")

    st.divider()

    fuels = sorted(df["fuel"].dropna().unique())

    default_fuels = [
        fuel for fuel in [
            "Natural gas",
            "Wind",
            "Solar",
            "Hydro",
            "Coal and manufactured gases"
        ]
        if fuel in fuels
    ]

    selected_fuels = st.multiselect(
        "Select energy sources",
        fuels,
        default=default_fuels
    )

    if selected_fuels:

        chart_data = df[
            df["fuel"].isin(selected_fuels)
        ].copy()

        fig = px.line(
            chart_data,
            x="date",
            y="value",
            color="fuel",
            title="Monthly Electricity Generation by Energy Source"
        )

        fig.update_layout(
            xaxis_title="Date",
            yaxis_title="Electricity Generation (GWh)",
            legend_title="ENERGY SOURCE",
            hovermode="x unified"
        )

        fig = apply_chart_design(fig)

        st.plotly_chart(
            fig,
            use_container_width=True,
            theme=None
        )

    else:

        show_notice(
            "Select at least one energy source.",
            "warning"
        )

    st.divider()

    st.subheader("Historical Dataset")

    st.dataframe(
        df[
            ["date", "fuel_code", "fuel", "value", "unit", "source"]
        ],
        use_container_width=True,
        hide_index=True
    )

    st.caption(
        "Source: Eurostat | Dataset: nrg_cb_pem. "
        "Coal and manufactured gases is an aggregated category "
        "and must not be interpreted as lignite alone."
    )


# =====================================================
# ANNUAL ENERGY MIX
# =====================================================

elif page == "Annual Energy Mix":

    st.title("ANNUAL ELECTRICITY MIX")

    st.caption("GREECE | ANNUAL GENERATION SHARES")

    st.divider()

    selected_codes = [
        "C0000", "G3000", "O4000XBIO",
        "N9000", "RA100", "RA200",
        "RA300", "RA400", "RA500_5160", "X9900"
    ]

    fuel_data = df[
        df["fuel_code"].isin(selected_codes)
    ].copy()

    annual_fuel = (
        fuel_data.groupby(
            ["year", "fuel_code", "fuel"],
            as_index=False
        )["value"].sum()
    )

    total_data = df[
        df["fuel_code"] == "TOTAL"
    ].copy()

    annual_total = (
        total_data.groupby("year", as_index=False)["value"]
        .sum()
        .rename(columns={"value": "total_generation"})
    )

    annual_mix = annual_fuel.merge(
        annual_total,
        on="year",
        how="inner"
    )

    annual_mix["share"] = (
        annual_mix["value"]
        / annual_mix["total_generation"]
        * 100
    )

    available_years = sorted(
        annual_mix["year"].unique()
    )

    preferred_years = [2008, 2015, 2020, 2025]

    selected_years = [
        year for year in preferred_years
        if year in available_years
    ]

    annual_mix = annual_mix[
        annual_mix["year"].isin(selected_years)
    ]

    if not annual_mix.empty:

        fig = px.bar(
            annual_mix,
            x="year",
            y="share",
            color="fuel",
            barmode="stack",
            title="Electricity Generation Mix",
            hover_data={
                "value": ":,.1f",
                "total_generation": ":,.1f",
                "share": ":.2f"
            }
        )

        fig.update_layout(
            xaxis_title="Year",
            yaxis_title="Share of Total Generation (%)",
            legend_title="ENERGY SOURCE"
        )

        fig = apply_chart_design(fig)

        st.plotly_chart(
            fig,
            use_container_width=True,
            theme=None
        )

        st.divider()

        st.subheader("Annual Generation Data")

        st.dataframe(
            annual_mix[
                ["year", "fuel", "value", "total_generation", "share"]
            ].rename(
                columns={
                    "year": "Year",
                    "fuel": "Energy Source",
                    "value": "Generation (GWh)",
                    "total_generation": "Total Generation (GWh)",
                    "share": "Share (%)"
                }
            ),
            use_container_width=True,
            hide_index=True
        )

    else:

        show_notice(
            "Annual generation data unavailable.",
            "warning"
        )
        # =====================================================
# ENERGY SECURITY
# =====================================================

elif page == "Energy Security":

    st.title("ENERGY SECURITY")

    st.caption(
        "GREECE | IMPORT DEPENDENCY AND ELECTRICITY TRADE"
    )

    st.divider()

    if security is None or security.empty:

        show_notice(
            "Energy security dataset not found. "
            "Please run fetch_security_data.py first.",
            "error"
        )

        st.stop()

    imports = security[
        security["indicator"] == "Electricity imports"
    ].copy()

    exports = security[
        security["indicator"] == "Electricity exports"
    ].copy()

    total_dependency = security[
        security["indicator"] == "Total energy import dependency"
    ].copy()

    gas_dependency = security[
        security["indicator"] == "Natural gas import dependency"
    ].copy()

    dependency_years = (
        set(total_dependency["year"])
        & set(gas_dependency["year"])
    )

    latest_dependency_year = (
        max(dependency_years)
        if dependency_years else None
    )

    latest_import_year = (
        imports["year"].max()
        if not imports.empty else None
    )

    latest_export_year = (
        exports["year"].max()
        if not exports.empty else None
    )

    st.subheader("Key Security Indicators")

    col1, col2, col3, col4 = st.columns(4)

    if latest_import_year is not None:

        latest_import = imports[
            imports["year"] == latest_import_year
        ]["value"].iloc[-1]

        col1.metric(
            f"ELECTRICITY IMPORTS ({int(latest_import_year)})",
            f"{latest_import:,.0f} GWh"
        )

    if latest_export_year is not None:

        latest_export = exports[
            exports["year"] == latest_export_year
        ]["value"].iloc[-1]

        col2.metric(
            f"ELECTRICITY EXPORTS ({int(latest_export_year)})",
            f"{latest_export:,.0f} GWh"
        )

    if latest_dependency_year is not None:

        total_value = total_dependency[
            total_dependency["year"] == latest_dependency_year
        ]["value"].iloc[-1]

        gas_value = gas_dependency[
            gas_dependency["year"] == latest_dependency_year
        ]["value"].iloc[-1]

        col3.metric(
            f"TOTAL ENERGY DEPENDENCY ({latest_dependency_year})",
            f"{total_value:.1f}%"
        )

        col4.metric(
            f"NATURAL GAS DEPENDENCY ({latest_dependency_year})",
            f"{gas_value:.1f}%"
        )

    st.divider()

    st.subheader("Electricity Imports and Exports")

    st.write(
        "Annual electricity trade flows between Greece and neighbouring markets."
    )

    trade_data = pd.concat(
        [
            imports.assign(Trade="Imports"),
            exports.assign(Trade="Exports")
        ],
        ignore_index=True
    )

    if not trade_data.empty:

        fig = px.line(
            trade_data,
            x="year",
            y="value",
            color="Trade",
            markers=True,
            title="Annual Electricity Trade"
        )

        fig.update_layout(
            xaxis_title="Year",
            yaxis_title="Electricity Trade (GWh)",
            legend_title="TRADE FLOW"
        )

        fig = apply_chart_design(fig)

        st.plotly_chart(
            fig,
            use_container_width=True,
            theme=None
        )

    st.divider()

    st.subheader("Energy Import Dependency")

    st.write(
        "Comparison between Greece's total energy import dependency "
        "and its natural gas import dependency."
    )

    dependency_data = pd.concat(
        [
            total_dependency.assign(
                Indicator="Total energy dependency"
            ),
            gas_dependency.assign(
                Indicator="Natural gas dependency"
            )
        ],
        ignore_index=True
    )

    if not dependency_data.empty:

        fig = px.line(
            dependency_data,
            x="year",
            y="value",
            color="Indicator",
            markers=True,
            title="Energy Import Dependency Over Time"
        )

        fig.update_layout(
            xaxis_title="Year",
            yaxis_title="Import Dependency (%)",
            legend_title="INDICATOR"
        )

        fig = apply_chart_design(fig)

        st.plotly_chart(
            fig,
            use_container_width=True,
            theme=None
        )

    st.divider()

    st.subheader("Historical Security Dataset")

    st.dataframe(
        security[
            ["year", "indicator", "value", "unit", "source", "dataset"]
        ].sort_values(
            ["indicator", "year"]
        ),
        use_container_width=True,
        hide_index=True
    )

    show_notice(
        "Electricity trade data: Eurostat nrg_cb_e. "
        "Energy import dependency: Eurostat nrg_ind_id. "
        "Dependency figures are available through 2024; "
        "electricity trade data may extend through 2025.",
        "info"
    )


# =====================================================
# REGIONAL DEVELOPMENT
# =====================================================

elif page == "Regional Development":

    st.title("REGIONAL DEVELOPMENT")

    st.caption(
        "WESTERN MACEDONIA VS PELOPONNESE | REGIONAL ECONOMIC TRANSITION"
    )

    st.divider()

    if regional is None or regional.empty:

        show_notice(
            "Regional dataset not found. "
            "Please run fetch_regional_data.py first.",
            "error"
        )

        st.stop()

    gdp = regional[
        regional["indicator"] == "GDP per capita"
    ].copy()

    employment = regional[
        regional["indicator"] == "Employment rate"
    ].copy()

    region_colors = {
        "Western Macedonia": "#FF9F43",
        "Peloponnese": "#58B8E8"
    }

    st.subheader("Regional Overview")

    st.write(
        "Comparison of economic performance and employment "
        "in two Greek regions affected by the lignite transition."
    )

    col1, col2 = st.columns(2)

    with col1:

        st.markdown("### Western Macedonia")
        st.caption("Eurostat regional code: EL53")

    with col2:

        st.markdown("### Peloponnese")
        st.caption("Eurostat regional code: EL65")

    st.divider()

    # GDP PER CAPITA

    st.subheader("GDP per Capita")

    st.write(
        "Regional GDP per inhabitant, measured in euros."
    )

    if not gdp.empty:

        latest_gdp = (
            gdp.sort_values("year")
            .groupby("region", as_index=False)
            .tail(1)
        )

        col1, col2 = st.columns(2)

        for column, region_name in [
            (col1, "Western Macedonia"),
            (col2, "Peloponnese")
        ]:

            region_latest = latest_gdp[
                latest_gdp["region"] == region_name
            ]

            if not region_latest.empty:

                value = region_latest["value"].iloc[0]
                year = region_latest["year"].iloc[0]

                column.metric(
                    f"{region_name.upper()} GDP PER CAPITA",
                    f"€{value:,.0f}"
                )

                column.caption(
                    f"Latest available year: {int(year)}"
                )

        fig = px.line(
            gdp,
            x="year",
            y="value",
            color="region",
            markers=True,
            color_discrete_map=region_colors,
            title="GDP per Capita — Regional Comparison"
        )

        fig.update_layout(
            xaxis_title="Year",
            yaxis_title="GDP per Capita (EUR)",
            legend_title="REGION",
            hovermode="x unified"
        )

        fig = apply_chart_design(fig)

        st.plotly_chart(
            fig,
            use_container_width=True,
            theme=None
        )

    else:

        show_notice(
            "GDP per capita observations are unavailable.",
            "warning"
        )

    st.divider()

    # EMPLOYMENT RATE

    st.subheader("Regional Employment Rate")

    st.write(
        "Employment rate among the population aged 15–64."
    )

    if not employment.empty:

        latest_employment = (
            employment.sort_values("year")
            .groupby("region", as_index=False)
            .tail(1)
        )

        col1, col2 = st.columns(2)

        for column, region_name in [
            (col1, "Western Macedonia"),
            (col2, "Peloponnese")
        ]:

            region_latest = latest_employment[
                latest_employment["region"] == region_name
            ]

            if not region_latest.empty:

                value = region_latest["value"].iloc[0]
                year = region_latest["year"].iloc[0]

                column.metric(
                    f"{region_name.upper()} EMPLOYMENT RATE",
                    f"{value:.1f}%"
                )

                column.caption(
                    f"Latest available year: {int(year)}"
                )

        fig = px.line(
            employment,
            x="year",
            y="value",
            color="region",
            markers=True,
            color_discrete_map=region_colors,
            title="Employment Rate — Regional Comparison"
        )

        fig.update_layout(
            xaxis_title="Year",
            yaxis_title="Employment Rate (%)",
            legend_title="REGION",
            hovermode="x unified"
        )

        fig = apply_chart_design(fig)

        st.plotly_chart(
            fig,
            use_container_width=True,
            theme=None
        )

    else:

        show_notice(
            "Employment observations are unavailable.",
            "warning"
        )

    st.divider()

    # LIGNITE-RELATED WORKFORCE

    st.subheader("Lignite-Related Workforce")

    st.write(
        "Historical workforce figures associated with PPC activities "
        "in Western Macedonia and the company operating the Meliti plant."
    )

    if lignite_employment is not None and not lignite_employment.empty:

        first_row = lignite_employment.iloc[0]
        last_row = lignite_employment.iloc[-1]

        initial_workforce = int(first_row["value"])
        latest_workforce = int(last_row["value"])

        absolute_change = latest_workforce - initial_workforce

        percentage_change = (
            absolute_change / initial_workforce * 100
            if initial_workforce else 0
        )

        first_year = int(first_row["year"])
        latest_year = int(last_row["year"])

        st.caption(
            "Indicator: PPC and Meliti workforce | "
            f"Observed years: {first_year}–{latest_year}"
        )

        k1, k2, k3 = st.columns(3)

        k1.metric(
            f"WORKFORCE ({first_year})",
            f"{initial_workforce:,} employees"
        )

        k2.metric(
            f"WORKFORCE ({latest_year})",
            f"{latest_workforce:,} employees"
        )

        k3.metric(
            "CHANGE OVER PERIOD",
            f"{percentage_change:.1f}%",
            delta=f"{absolute_change:+,} employees",
            delta_color="inverse"
        )

        workforce_chart = px.line(
            lignite_employment,
            x="year",
            y="value",
            markers=True,
            text="value",
            title="PPC and Meliti Workforce — Western Macedonia",
            labels={
                "year": "Year",
                "value": "Employees"
            }
        )

        workforce_chart.update_traces(
            line=dict(color="#FF9F43", width=3),
            marker=dict(size=10, color="#FF9F43"),
            texttemplate="%{text:,.0f}",
            textposition="top center",
            textfont=dict(color="#FFFFFF", size=12)
        )

        workforce_chart.update_layout(
            yaxis_title="Number of employees",
            xaxis_title="Year",
            showlegend=False,
            margin=dict(t=70, b=40)
        )

        workforce_chart = apply_chart_design(workforce_chart)

        st.plotly_chart(
            workforce_chart,
            use_container_width=True,
            theme=None
        )

        show_notice(
            "These figures represent the PPC and Meliti corporate workforce "
            "scope described in the source dataset. They are not a count "
            "of miners only and must not be interpreted as total direct "
            "and indirect regional employment losses.",
            "warning"
        )

        if "source_url" in lignite_employment.columns:

            source_urls = (
                lignite_employment["source_url"]
                .dropna()
                .astype(str)
                .unique()
            )

            for source_url in source_urls:

                if source_url.startswith("https://"):

                    st.markdown(
                        f"[Open recorded source]({source_url})"
                    )

        st.subheader("Lignite-Related Workforce Dataset")

        display_columns = [
            column for column in [
                "year", "date", "indicator", "value", "unit",
                "region", "scope", "data_status", "source",
                "reference_study"
            ]
            if column in lignite_employment.columns
        ]

        st.dataframe(
            lignite_employment[display_columns],
            use_container_width=True,
            hide_index=True
        )

    else:

        show_notice(
            "Lignite employment dataset not found or incomplete. "
            "Run build_lignite_employment_data.py.",
            "warning"
        )

    st.divider()

    # HISTORICAL REGIONAL DATA

    st.subheader("Historical Regional Dataset")

    selected_indicator = st.selectbox(
        "Select indicator",
        [
            "GDP per capita",
            "Employment rate"
        ]
    )

    selected_region = st.selectbox(
        "Select region",
        [
            "All regions",
            "Western Macedonia",
            "Peloponnese"
        ]
    )

    table_data = regional[
        regional["indicator"] == selected_indicator
    ].copy()

    if selected_region != "All regions":

        table_data = table_data[
            table_data["region"] == selected_region
        ]

    table_data = table_data.sort_values(
        ["region", "year"]
    )

    display_columns = [
        column for column in [
            "year", "region", "region_code",
            "indicator", "value", "unit",
            "source", "dataset"
        ]
        if column in table_data.columns
    ]

    st.dataframe(
        table_data[display_columns],
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    st.subheader("Methodology and Limitations")

    show_notice(
        "Eurostat GDP and employment-rate indicators describe broad "
        "regional trends; they do not isolate the effects of lignite "
        "closures. The separate PPC and Meliti workforce series above "
        "has a narrower corporate scope and must not be interpreted as "
        "total mining employment or total direct and indirect regional "
        "job losses.",
        "warning"
    )

    st.caption(
        "Source: Eurostat. GDP per capita: nama_10r_2gdp. "
        "Employment rate: lfst_r_lfe2emprt. "
        "Regional codes: EL53 and EL65."
    )
    # =====================================================
# INTERNATIONAL COMPARISON
# =====================================================

elif page == "International Comparison":

    st.title("INTERNATIONAL COMPARISON")

    st.caption(
        "EUROPEAN COAL REGIONS | TRANSITION STRATEGIES AND POLICY LESSONS"
    )

    st.divider()

    st.markdown("""
    This module benchmarks Greece's lignite transition against selected
    European coal regions. The objective is to identify transferable
    policies rather than assume that regions have identical economic,
    industrial or energy-system characteristics.
    """)

    show_notice(
        "The comparison below is a qualitative policy benchmark based on "
        "documented European Commission and EU institutional sources. "
        "It is not a statistical ranking of regional performance.",
        "info"
    )

    # -------------------------------------------------
    # CASE STUDIES
    # -------------------------------------------------

    case_studies = {

        "Silesia — Poland": {

            "country": "Poland",

            "region": "Upper Silesia",

            "transition_context": (
                "A major European hard-coal mining and industrial region. "
                "The transition involves mining, energy-intensive industry, "
                "employment and the redevelopment of former industrial land."
            ),

            "policy_approach": (
                "A Territorial Just Transition Plan supported by the "
                "European Just Transition Fund. The regional approach "
                "includes economic diversification, SME investment, "
                "post-mining land rehabilitation and stakeholder coordination."
            ),

            "economic_diversification": (
                "Support for SMEs, renewable energy, clean mobility, "
                "industrial redevelopment and new economic activities."
            ),

            "employment_policy": (
                "Reskilling, worker adaptation, stakeholder consultation "
                "and regional monitoring of transition impacts."
            ),

            "key_lesson": (
                "Create a strong project pipeline and a regional governance "
                "structure before allocating large amounts of funding. "
                "Funding alone does not automatically create new jobs."
            ),

            "transferability": (
                "Highly relevant to Western Macedonia because both regions "
                "must manage industrial restructuring, workforce adaptation "
                "and post-mining land."
            ),

            "sources": [
                (
                    "European Commission — Silesia Regional Observatory",
                    "https://just-transition-experts.ec.europa.eu/find-knowledge/regional-observatory-transition-process-silesia-ropt-case-study_en"
                ),
                (
                    "European Commission — Support to Just Transition in Poland",
                    "https://reforms-investments.ec.europa.eu/technical-support-instrument-0/green-transition/support-implementation-just-transition-poland_en"
                )
            ]
        },

        "Asturias — Spain": {

            "country": "Spain",

            "region": "Asturias",

            "transition_context": (
                "A historic coal-mining and industrial region facing "
                "the economic and social consequences of coal restructuring."
            ),

            "policy_approach": (
                "A combination of regional restructuring, public support "
                "for affected territories, environmental rehabilitation "
                "and investment in alternative economic activities."
            ),

            "economic_diversification": (
                "Industrial redevelopment, environmental restoration, "
                "new business activities and clean-energy opportunities."
            ),

            "employment_policy": (
                "Support for affected workers and local communities, "
                "including training and adaptation to new economic activities."
            ),

            "key_lesson": (
                "A coal-region transition requires a long-term regional "
                "economic strategy. New industries must be developed "
                "alongside the closure of existing activities."
            ),

            "transferability": (
                "Relevant to Western Macedonia for the management of "
                "industrial decline and the need to create alternative "
                "employment opportunities."
            ),

            "sources": [
                (
                    "European Court of Auditors — EU support to coal regions",
                    "https://op.europa.eu/webpub/eca/special-reports/support-coal-regions-22-2022/en/"
                )
            ]
        },

        "Lusatia — Germany": {

            "country": "Germany",

            "region": "Brandenburg / Lusatia",

            "transition_context": (
                "A lignite-dependent region undergoing a major structural "
                "transformation away from coal-based electricity generation."
            ),

            "policy_approach": (
                "Long-term structural support, regional investment planning "
                "and the development of alternative economic activities."
            ),

            "economic_diversification": (
                "Industrial transformation, infrastructure, research, "
                "innovation and the development of new economic sectors."
            ),

            "employment_policy": (
                "A focus on managing structural change and supporting "
                "workers and communities affected by the decline of lignite."
            ),

            "key_lesson": (
                "The timing and sequencing of investment matter. "
                "Alternative economic activity must develop before "
                "the regional economy becomes excessively dependent "
                "on replacement subsidies."
            ),

            "transferability": (
                "Particularly relevant to Greece because both regions "
                "have a historical dependence on lignite and power generation."
            ),

            "sources": [
                (
                    "European Court of Auditors — EU support to coal regions",
                    "https://op.europa.eu/webpub/eca/special-reports/support-coal-regions-22-2022/en/"
                )
            ]
        }
    }

    selected_case = st.selectbox(
        "Select a European coal-region case study",
        list(case_studies.keys())
    )

    case = case_studies[selected_case]

    st.divider()

    # CASE STUDY HEADER

    st.subheader(selected_case.upper())

    col1, col2 = st.columns(2)

    col1.metric(
        "COUNTRY",
        case["country"]
    )

    col2.metric(
        "REGION",
        case["region"]
    )

    st.divider()

    # CASE STUDY DETAILS

    st.markdown("### Transition Context")

    st.write(case["transition_context"])

    st.markdown("### Policy Approach")

    st.write(case["policy_approach"])

    col1, col2 = st.columns(2)

    with col1:

        st.markdown("### Economic Diversification")

        st.write(case["economic_diversification"])

    with col2:

        st.markdown("### Employment Policy")

        st.write(case["employment_policy"])

    st.divider()

    st.markdown("### Main Policy Lesson")

    show_notice(
        case["key_lesson"],
        "success"
    )

    st.markdown("### Relevance for Greece")

    st.write(case["transferability"])

    st.markdown("### Institutional Sources")

    for source_name, source_url in case["sources"]:

        st.markdown(
            f"- [{source_name}]({source_url})"
        )

    st.divider()

    # -------------------------------------------------
    # COMPARATIVE FRAMEWORK
    # -------------------------------------------------

    st.subheader("Comparative Policy Framework")

    comparison_data = pd.DataFrame([

        {
            "Region": "Western Macedonia",
            "Main Energy Legacy": "Lignite",
            "Main Challenge": "Regional economic diversification",
            "Priority": "Alternative employment and investment"
        },

        {
            "Region": "Silesia",
            "Main Energy Legacy": "Hard coal",
            "Main Challenge": "Industrial and mining restructuring",
            "Priority": "SMEs, land rehabilitation and skills"
        },

        {
            "Region": "Asturias",
            "Main Energy Legacy": "Coal mining and industry",
            "Main Challenge": "Industrial restructuring",
            "Priority": "Economic diversification"
        },

        {
            "Region": "Lusatia",
            "Main Energy Legacy": "Lignite",
            "Main Challenge": "Structural economic transformation",
            "Priority": "Long-term investment and new industries"
        }

    ])

    st.dataframe(
        comparison_data,
        use_container_width=True,
        hide_index=True
    )

    st.caption(
        "This is a qualitative comparison of documented policy priorities. "
        "It does not imply that the regions have identical economic structures "
        "or transition outcomes."
    )

    st.divider()

    # -------------------------------------------------
    # POLICY LESSONS FOR GREECE
    # -------------------------------------------------

    st.subheader("Policy Lessons for Western Macedonia")

    lessons = [

        (
            "1. Economic diversification",
            "Develop alternative sectors before the full economic impact "
            "of lignite closures materialises."
        ),

        (
            "2. Workforce transition",
            "Connect training programmes to actual labour-market demand "
            "and identifiable employers."
        ),

        (
            "3. Industrial land redevelopment",
            "Prepare former mining and power-generation sites for new "
            "productive uses."
        ),

        (
            "4. Investment pipeline",
            "Build a pipeline of technically and financially mature projects "
            "rather than relying only on broad funding announcements."
        ),

        (
            "5. Regional governance",
            "Coordinate central government, regional authorities, companies, "
            "workers, universities and local communities."
        ),

        (
            "6. Energy-system reliability",
            "Coordinate renewable generation with grids, storage, flexibility "
            "and interconnections."
        )
    ]

    for title, description in lessons:

        with st.expander(title):

            st.write(description)

    st.divider()

    # -------------------------------------------------
    # LIMITATIONS
    # -------------------------------------------------

    st.subheader("Methodological Limitations")

    show_notice(
        "The selected regions differ in industrial structure, population, "
        "coal type, electricity-market conditions and national policy context. "
        "The comparison therefore identifies policy approaches and lessons; "
        "it does not establish a causal ranking of transition success.",
        "warning"
    )

    st.caption(
        "Main sources: European Commission, European Court of Auditors "
        "and the EU Just Transition Platform."
    )
    # =====================================================
# FINANCING SIMULATOR
# =====================================================

elif page == "Financing Simulator":

    st.title("ENERGY TRANSITION FINANCING SIMULATOR")

    st.caption(
        "WESTERN MACEDONIA | INVESTMENT STRUCTURE AND FUNDING GAP ANALYSIS"
    )

    st.divider()

    st.markdown("""
    This simulator allows users to construct an illustrative financing
    package for the Greek energy transition.

    It combines potential grants, public financing, debt and private
    investment to assess how a transition investment programme could
    be financed.
    """)

    show_notice(
        "All amounts and financing percentages entered below are scenario "
        "assumptions. They are not confirmed funding allocations, approved "
        "project budgets or financing commitments.",
        "warning"
    )

    # -------------------------------------------------
    # PROJECT ASSUMPTIONS
    # -------------------------------------------------

    st.subheader("1. Project Investment Assumptions")

    col1, col2 = st.columns(2)

    with col1:

        total_capex = st.number_input(
            "Total investment programme (€ million)",
            min_value=1.0,
            max_value=50000.0,
            value=1500.0,
            step=50.0
        )

        project_duration = st.slider(
            "Investment programme duration (years)",
            min_value=3,
            max_value=20,
            value=10
        )

    with col2:

        contingency_percentage = st.slider(
            "Contingency reserve (%)",
            min_value=0,
            max_value=25,
            value=10
        )

        financing_currency = "EUR"

    contingency_amount = (
        total_capex * contingency_percentage / 100
    )

    total_project_cost = (
        total_capex + contingency_amount
    )

    st.metric(
        "TOTAL PROJECT COST INCLUDING CONTINGENCY",
        f"€{total_project_cost:,.1f} million"
    )

    st.caption(
        "The contingency reserve is an editable planning assumption."
    )

    st.divider()

    # -------------------------------------------------
    # FUNDING MIX
    # -------------------------------------------------

    st.subheader("2. Financing Structure")

    st.write(
        "Define the share of the total project cost covered by each "
        "financing source."
    )

    col1, col2 = st.columns(2)

    with col1:

        jtf_share = st.slider(
            "EU Just Transition Fund — assumed contribution (%)",
            min_value=0,
            max_value=85,
            value=25
        )

        public_grant_share = st.slider(
            "Other public grants — assumed contribution (%)",
            min_value=0,
            max_value=50,
            value=10
        )

        eib_share = st.slider(
            "Public / EIB loans — assumed contribution (%)",
            min_value=0,
            max_value=70,
            value=25
        )

    with col2:

        private_share = st.slider(
            "Private investment — assumed contribution (%)",
            min_value=0,
            max_value=100,
            value=25
        )

        national_share = st.slider(
            "National public contribution (%)",
            min_value=0,
            max_value=50,
            value=15
        )

    total_financing_share = (
        jtf_share
        + public_grant_share
        + eib_share
        + private_share
        + national_share
    )

    st.divider()

    # -------------------------------------------------
    # FINANCING CALCULATIONS
    # -------------------------------------------------

    jtf_amount = (
        total_project_cost * jtf_share / 100
    )

    public_grant_amount = (
        total_project_cost * public_grant_share / 100
    )

    eib_amount = (
        total_project_cost * eib_share / 100
    )

    private_amount = (
        total_project_cost * private_share / 100
    )

    national_amount = (
        total_project_cost * national_share / 100
    )

    total_committed_scenario = (
        jtf_amount
        + public_grant_amount
        + eib_amount
        + private_amount
        + national_amount
    )

    funding_gap = (
        total_project_cost - total_committed_scenario
    )

    # -------------------------------------------------
    # FUNDING GAP
    # -------------------------------------------------

    st.subheader("3. Funding Gap Analysis")

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "TOTAL PROJECT COST",
        f"€{total_project_cost:,.1f}m"
    )

    col2.metric(
        "SCENARIO FINANCING",
        f"€{total_committed_scenario:,.1f}m"
    )

    col3.metric(
        "FUNDING GAP",
        f"€{funding_gap:,.1f}m",
        delta=(
            f"{funding_gap / total_project_cost * 100:.1f}% of project cost"
        ),
        delta_color="inverse"
    )

    if abs(total_financing_share - 100) < 0.01:

        show_notice(
            "The financing structure covers 100% of the project cost.",
            "success"
        )

    elif total_financing_share < 100:

        show_notice(
            f"The financing structure covers {total_financing_share:.1f}% "
            f"of project costs. An additional "
            f"{100 - total_financing_share:.1f}% must be financed.",
            "warning"
        )

    else:

        show_notice(
            f"The financing structure exceeds project costs by "
            f"{total_financing_share - 100:.1f}%. "
            "Review the financing assumptions to avoid double counting.",
            "error"
        )

    st.divider()

    # -------------------------------------------------
    # FINANCING MIX CHART
    # -------------------------------------------------

    st.subheader("4. Financing Mix")

    financing_data = pd.DataFrame({

        "Financing Source": [
            "Just Transition Fund",
            "Other Public Grants",
            "Public / EIB Loans",
            "Private Investment",
            "National Public Contribution"
        ],

        "Amount (€ million)": [
            jtf_amount,
            public_grant_amount,
            eib_amount,
            private_amount,
            national_amount
        ]

    })

    financing_data = financing_data[
        financing_data["Amount (€ million)"] > 0
    ]

    if not financing_data.empty:

        fig = px.pie(
            financing_data,
            names="Financing Source",
            values="Amount (€ million)",
            hole=0.55,
            title="Illustrative Project Financing Structure"
        )

        fig.update_traces(
            textposition="inside",
            textinfo="percent+label"
        )

        fig = apply_chart_design(fig)

        st.plotly_chart(
            fig,
            use_container_width=True,
            theme=None
        )

    st.dataframe(
        financing_data,
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    # -------------------------------------------------
    # DEBT SERVICE
    # -------------------------------------------------

    st.subheader("5. Loan Repayment Analysis")

    st.write(
        "Estimate annual debt service for the assumed public / EIB loan."
    )

    col1, col2 = st.columns(2)

    with col1:

        interest_rate = st.number_input(
            "Annual loan interest rate (%)",
            min_value=0.0,
            max_value=20.0,
            value=3.5,
            step=0.25
        )

    with col2:

        loan_tenor = st.slider(
            "Loan maturity (years)",
            min_value=3,
            max_value=30,
            value=20
        )

    principal = eib_amount

    rate = interest_rate / 100

    if principal > 0:

        if rate > 0:

            annual_debt_service = (
                principal
                * rate
                / (1 - (1 + rate) ** (-loan_tenor))
            )

        else:

            annual_debt_service = (
                principal / loan_tenor
            )

        total_debt_repayment = (
            annual_debt_service * loan_tenor
        )

        total_interest = (
            total_debt_repayment - principal
        )

    else:

        annual_debt_service = 0
        total_debt_repayment = 0
        total_interest = 0

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "LOAN PRINCIPAL",
        f"€{principal:,.1f}m"
    )

    col2.metric(
        "ANNUAL DEBT SERVICE",
        f"€{annual_debt_service:,.1f}m"
    )

    col3.metric(
        "TOTAL INTEREST",
        f"€{total_interest:,.1f}m"
    )

    st.caption(
        "Debt service is calculated using a standard constant annual "
        "payment formula. It excludes fees, grace periods, variable-rate "
        "changes, refinancing and other contractual features."
    )

    st.divider()

    # -------------------------------------------------
    # DEBT AMORTISATION PROFILE
    # -------------------------------------------------

    st.subheader("6. Indicative Debt Repayment Profile")

    if principal > 0:

        remaining_balance = principal
        amortisation_rows = []

        for year in range(1, loan_tenor + 1):

            interest_payment = (
                remaining_balance * rate
            )

            principal_repayment = (
                annual_debt_service - interest_payment
            )

            if year == loan_tenor:
                principal_repayment = remaining_balance

            remaining_balance = max(
                0,
                remaining_balance - principal_repayment
            )

            amortisation_rows.append({

                "Year": year,

                "Interest Payment (€m)": interest_payment,

                "Principal Repayment (€m)": principal_repayment,

                "Annual Debt Service (€m)": (
                    interest_payment + principal_repayment
                ),

                "Remaining Balance (€m)": remaining_balance

            })

        amortisation = pd.DataFrame(
            amortisation_rows
        )

        fig = px.bar(
            amortisation,
            x="Year",
            y=[
                "Interest Payment (€m)",
                "Principal Repayment (€m)"
            ],
            title="Annual Debt Service Composition",
            barmode="stack"
        )

        fig.update_layout(
            xaxis_title="Year",
            yaxis_title="Annual Payment (€ million)",
            legend_title="PAYMENT COMPONENT"
        )

        fig = apply_chart_design(fig)

        st.plotly_chart(
            fig,
            use_container_width=True,
            theme=None
        )

        with st.expander("View full amortisation schedule"):

            st.dataframe(
                amortisation,
                use_container_width=True,
                hide_index=True
            )

    else:

        show_notice(
            "No public / EIB loan has been included in the financing structure.",
            "info"
        )

    st.divider()

    # -------------------------------------------------
    # FUNDING INSTRUMENTS
    # -------------------------------------------------

    st.subheader("7. Potential European Financing Instruments")

    st.markdown("### Just Transition Fund (JTF)")

    st.write(
        "The JTF supports territories facing major socio-economic "
        "challenges arising from the transition to climate neutrality. "
        "It can support economic diversification, SME development, "
        "worker adaptation and environmental rehabilitation, subject "
        "to the approved Territorial Just Transition Plan and programme rules."
    )

    st.markdown(
        "[European Commission — Just Transition Mechanism](https://commission.europa.eu/topics/regional-and-urban-policy/just-transition-mechanism_en)"
    )

    st.markdown("### InvestEU — Just Transition Scheme")

    st.write(
        "InvestEU can help mobilise private investment in projects "
        "that contribute to the objectives of the relevant Territorial "
        "Just Transition Plans. It is particularly relevant for "
        "commercially viable investments that require risk-sharing "
        "or financial guarantees."
    )

    st.markdown(
        "[European Commission — InvestEU](https://investeu.europa.eu/investeu-programme/questions-and-answers_en)"
    )

    st.markdown("### Public Sector Loan Facility")

    st.write(
        "The Public Sector Loan Facility combines EU grants with "
        "European Investment Bank lending to support public-sector "
        "projects addressing the economic, social and environmental "
        "challenges of the transition."
    )

    st.markdown(
        "[CINEA — Public Sector Loan Facility](https://cinea.ec.europa.eu/just-transition-mechanism/about-public-sector-loan-facility-just-transition-mechanism_en)"
    )

    st.markdown("### Modernisation Fund")

    st.write(
        "Greece is among the beneficiary Member States. The Modernisation "
        "Fund can support eligible investments in renewable energy, "
        "energy efficiency, storage, electricity networks and just "
        "transition in carbon-dependent regions."
    )

    st.markdown(
        "[European Commission — Modernisation Fund](https://climate.ec.europa.eu/areas-action/eu-funding-climate-action/modernisation-fund_en)"
    )

    st.divider()

    # -------------------------------------------------
    # FINANCING RECOMMENDATION
    # -------------------------------------------------

    st.subheader("8. Financing Strategy Assessment")

    if total_financing_share < 100:

        st.markdown("### Funding Gap")

        st.write(
            "The scenario still contains an unfunded portion. "
            "Additional grants, public contributions, private capital "
            "or debt financing would be required."
        )

    elif total_financing_share > 100:

        st.markdown("### Overfunding Risk")

        st.write(
            "The assumed financing sources exceed the project cost. "
            "The financing package should be adjusted to avoid "
            "double counting or unnecessary financing."
        )

    else:

        st.markdown("### Fully Financed Scenario")

        st.write(
            "The scenario is fully financed under the selected assumptions. "
            "The next step would be to test the eligibility, bankability, "
            "timing and contractual conditions of each financing source."
        )

    show_notice(
        "Important: the simulator is a simplified financial planning tool. "
        "Actual JTF, InvestEU, EIB and Modernisation Fund support depends "
        "on eligibility, approved programmes, project appraisal, state-aid "
        "rules, co-financing requirements and the availability of funding.",
        "warning"
    )

    st.caption(
        "Framework sources: European Commission, CINEA and InvestEU. "
        "All scenario inputs are user-defined assumptions."
    )