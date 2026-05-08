from pathlib import Path

import numpy as np
import pandas as pd
import pydeck as pdk
import streamlit as st


DATA_PATH = Path(__file__).parent / "data" / "signal_samples.csv"
REQUIRED_COLUMNS = {
    "Latitude",
    "Longitude",
    "CellID",
    "Band",
    "RSRP_dBm",
    "SINR_dB",
    "TerminalType",
    "Download_Mbps",
}


def load_signal_data(path: Path = DATA_PATH) -> pd.DataFrame:
    """Load and normalize the 5G drive-test sample data."""
    df = pd.read_csv(path)
    missing = REQUIRED_COLUMNS.difference(df.columns)
    if missing:
        missing_columns = ", ".join(sorted(missing))
        raise ValueError(f"Missing required columns: {missing_columns}")

    numeric_columns = ["Latitude", "Longitude", "RSRP_dBm", "SINR_dB", "Download_Mbps"]
    df[numeric_columns] = df[numeric_columns].apply(pd.to_numeric, errors="coerce")
    df = df.dropna(subset=numeric_columns + ["Band", "TerminalType"]).copy()
    df["SignalQuality"] = pd.cut(
        df["RSRP_dBm"],
        bins=[-np.inf, -110, -90, np.inf],
        labels=["Weak", "Fair", "Strong"],
    )
    df["SignalColor"] = df["RSRP_dBm"].apply(signal_color)
    df["ColumnHeight"] = normalize_column_height(df["Download_Mbps"])
    return df


def signal_color(rsrp: float) -> list[int]:
    """Map RSRP to a traffic-light color used by the map layers."""
    if rsrp > -90:
        return [43, 180, 92, 190]
    if rsrp < -110:
        return [221, 64, 64, 190]
    return [244, 171, 54, 190]


def normalize_column_height(series: pd.Series) -> pd.Series:
    """Scale download speed into stable 3D column heights."""
    values = pd.to_numeric(series, errors="coerce").fillna(0)
    min_value = values.min()
    spread = values.max() - min_value
    if spread == 0:
        return pd.Series(np.full(len(values), 120), index=values.index)
    return 80 + (values - min_value) / spread * 520


def filter_signal_data(
    df: pd.DataFrame,
    bands: list[str],
    terminals: list[str],
    rsrp_range: tuple[float, float],
    sinr_range: tuple[float, float],
) -> pd.DataFrame:
    """Apply sidebar filters to the signal samples."""
    return df[
        df["Band"].isin(bands)
        & df["TerminalType"].isin(terminals)
        & df["RSRP_dBm"].between(rsrp_range[0], rsrp_range[1])
        & df["SINR_dB"].between(sinr_range[0], sinr_range[1])
    ].copy()


def metric_delta(current: float, baseline: float) -> str:
    diff = current - baseline
    return f"{diff:+.2f}"


def build_deck(df: pd.DataFrame, layer_mode: str) -> pdk.Deck:
    midpoint = {
        "latitude": float(df["Latitude"].mean()),
        "longitude": float(df["Longitude"].mean()),
    }
    view_state = pdk.ViewState(
        latitude=midpoint["latitude"],
        longitude=midpoint["longitude"],
        zoom=11.4,
        pitch=48 if layer_mode == "3D throughput columns" else 30,
        bearing=-18 if layer_mode == "3D throughput columns" else 0,
    )

    layers = [
        pdk.Layer(
            "ScatterplotLayer",
            df,
            get_position="[Longitude, Latitude]",
            get_fill_color="SignalColor",
            get_radius=80,
            radius_min_pixels=4,
            radius_max_pixels=16,
            pickable=True,
        )
    ]
    if layer_mode == "3D throughput columns":
        layers.append(
            pdk.Layer(
                "ColumnLayer",
                df,
                get_position="[Longitude, Latitude]",
                get_elevation="ColumnHeight",
                elevation_scale=2.2,
                radius=48,
                get_fill_color="SignalColor",
                pickable=True,
                extruded=True,
                auto_highlight=True,
            )
        )

    tooltip = {
        "html": """
            <b>Cell:</b> {CellID}<br/>
            <b>Band:</b> {Band}<br/>
            <b>RSRP:</b> {RSRP_dBm} dBm<br/>
            <b>SINR:</b> {SINR_dB} dB<br/>
            <b>Download:</b> {Download_Mbps} Mbps
        """,
        "style": {"backgroundColor": "#20242b", "color": "white"},
    }
    return pdk.Deck(
        layers=layers,
        initial_view_state=view_state,
        map_style=pdk.map_styles.CARTO_LIGHT,
        tooltip=tooltip,
    )


def render_sidebar(df: pd.DataFrame) -> tuple[list[str], list[str], tuple[float, float], tuple[float, float], str]:
    st.sidebar.header("Filters")
    bands = sorted(df["Band"].unique().tolist())
    terminals = sorted(df["TerminalType"].unique().tolist())

    selected_bands = st.sidebar.multiselect("Band", bands, default=bands)
    selected_terminals = st.sidebar.multiselect("Terminal type", terminals, default=terminals)
    rsrp_range = st.sidebar.slider(
        "RSRP range (dBm)",
        float(df["RSRP_dBm"].min()),
        float(df["RSRP_dBm"].max()),
        (float(df["RSRP_dBm"].min()), float(df["RSRP_dBm"].max())),
        step=1.0,
    )
    sinr_range = st.sidebar.slider(
        "SINR range (dB)",
        float(df["SINR_dB"].min()),
        float(df["SINR_dB"].max()),
        (float(df["SINR_dB"].min()), float(df["SINR_dB"].max())),
        step=1.0,
    )
    layer_mode = st.sidebar.radio("Map layer", ["Signal scatter", "3D throughput columns"], index=1)

    st.sidebar.divider()
    st.sidebar.caption("Color rule: green > -90 dBm, red < -110 dBm, amber otherwise.")
    return selected_bands, selected_terminals, rsrp_range, sinr_range, layer_mode


def render_metrics(filtered: pd.DataFrame, baseline: pd.DataFrame) -> None:
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Samples", f"{len(filtered):,}", delta=f"{len(filtered) - len(baseline):+,}")
    col2.metric(
        "Avg RSRP",
        f"{filtered['RSRP_dBm'].mean():.2f} dBm",
        delta=metric_delta(filtered["RSRP_dBm"].mean(), baseline["RSRP_dBm"].mean()),
    )
    col3.metric(
        "Avg SINR",
        f"{filtered['SINR_dB'].mean():.2f} dB",
        delta=metric_delta(filtered["SINR_dB"].mean(), baseline["SINR_dB"].mean()),
    )
    col4.metric(
        "Avg Download",
        f"{filtered['Download_Mbps'].mean():.2f} Mbps",
        delta=metric_delta(filtered["Download_Mbps"].mean(), baseline["Download_Mbps"].mean()),
    )


def render_charts(filtered: pd.DataFrame) -> None:
    band_counts = filtered.groupby("Band")["CellID"].nunique().sort_values(ascending=False)
    terminal_share = filtered["TerminalType"].value_counts().sort_index()
    quality_counts = filtered["SignalQuality"].value_counts().reindex(["Strong", "Fair", "Weak"]).fillna(0)

    chart_col1, chart_col2, chart_col3 = st.columns((1.1, 1, 1))
    with chart_col1:
        st.subheader("Base stations by band")
        st.bar_chart(band_counts, height=260)
    with chart_col2:
        st.subheader("Terminal mix")
        st.bar_chart(terminal_share, height=260)
    with chart_col3:
        st.subheader("Signal quality")
        st.bar_chart(quality_counts, height=260)


def main() -> None:
    st.set_page_config(page_title="5G Signal Operations Dashboard", layout="wide")
    st.title("5G Signal Operations Dashboard")
    st.caption("Interactive view of drive-test samples with live filters, RSRP color coding, and 3D throughput columns.")

    try:
        df = load_signal_data()
    except Exception as exc:
        st.error(f"Unable to load signal data: {exc}")
        st.stop()

    selected_bands, selected_terminals, rsrp_range, sinr_range, layer_mode = render_sidebar(df)
    filtered = filter_signal_data(df, selected_bands, selected_terminals, rsrp_range, sinr_range)

    if filtered.empty:
        st.warning("No samples match the current filters. Adjust the sidebar to restore map and chart data.")
        st.stop()

    render_metrics(filtered, df)
    st.pydeck_chart(build_deck(filtered, layer_mode), use_container_width=True, height=560)
    render_charts(filtered)

    with st.expander("Filtered data", expanded=False):
        st.dataframe(
            filtered[
                [
                    "Latitude",
                    "Longitude",
                    "CellID",
                    "Band",
                    "RSRP_dBm",
                    "SINR_dB",
                    "TerminalType",
                    "Download_Mbps",
                    "SignalQuality",
                ]
            ].sort_values("RSRP_dBm", ascending=False),
            use_container_width=True,
            hide_index=True,
        )


if __name__ == "__main__":
    main()
