# -*- coding: utf-8 -*-
"""
Sci-Fi-Filme & UFO-Sichtungen — Interaktives Dashboard
Zeitfenster-Analyse (2/5/7/9/12 Monate) · Monats-Cluster · Korrelation
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from scipy import stats

# Seiten-Setup & Styling
st.set_page_config(
    page_title="UFOs & Sci-Fi Dashboard",
        layout="wide",
)

st.markdown("""
<style>
    .main .block-container { padding-top: 2rem; }

    /* Titel mit Farbverlauf */
    h1 { background: linear-gradient(90deg, #7b2ff7, #00d4ff);
         -webkit-background-clip: text; -webkit-text-fill-color: transparent;
         font-size: 2.1rem !important; line-height: 1.25 !important; }

    /* Kennzahlen-Kacheln */
    [data-testid="stMetricValue"] { color: #7b2ff7; }
    div[data-testid="stMetric"] {
        background: rgba(123, 47, 247, 0.06);
        border: 1px solid rgba(123, 47, 247, 0.25);
        border-radius: 12px; padding: 12px 16px;
    }

    /* ── Sidebar ───────────────────────────── */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg,
            rgba(123, 47, 247, 0.14) 0%,
            rgba(0, 212, 255, 0.05) 55%,
            rgba(14, 17, 23, 0) 100%);
        border-right: 1px solid rgba(123, 47, 247, 0.30);
    }
    [data-testid="stSidebar"] h1 {
        font-size: 1.35rem !important;
        text-align: center;
        padding-bottom: 0.3rem;
        border-bottom: 1px solid rgba(0, 212, 255, 0.35);
    }
    /* Beschriftungen der Sidebar-Elemente */
    [data-testid="stSidebar"] label p {
        font-weight: 600;
        letter-spacing: 0.02em;
        color: #c9b8ff;
    }
    /* Radio-Buttons als Pillen */
    [data-testid="stSidebar"] div[role="radiogroup"] label {
        background: rgba(123, 47, 247, 0.12);
        border: 1px solid rgba(123, 47, 247, 0.35);
        border-radius: 999px;
        padding: 2px 14px;
        margin-right: 4px;
    }
    /* Slider-Akzent */
    [data-testid="stSidebar"] [data-baseweb="slider"] div[role="slider"] {
        background: #00d4ff;
    }
</style>
""", unsafe_allow_html=True)

FARBE_UFO  = "#00d4ff"  
FARBE_FILM = "#7b2ff7"  

MONATSNAMEN = ["Jan", "Feb", "Mär", "Apr", "Mai", "Jun",
               "Jul", "Aug", "Sep", "Okt", "Nov", "Dez"]

# Daten laden
@st.cache_data
def lade_daten():
    # Nur benötigte Spalten laden
    filme = pd.read_csv("Film_Datensatz_Final.csv",
                        usecols=["release_date"], parse_dates=["release_date"])
    ufos  = pd.read_csv("Ufo_Datensatz_Final.csv",
                        usecols=["country", "date_time",
                                 "city_latitude", "city_longitude"],
                        parse_dates=["date_time"])
    ufos["country"] = ufos["country"].astype("category")
    filme["jahr"]  = filme["release_date"].dt.year
    filme["monat"] = filme["release_date"].dt.month
    ufos["jahr"]   = ufos["date_time"].dt.year
    ufos["monat"]  = ufos["date_time"].dt.month
    return filme, ufos

filme, ufos = lade_daten()

# Sidebar — Steuerung
st.sidebar.title("Analyse-Steuerung")
st.sidebar.caption("Einstellungen wählen, dann unten auf **Aktualisieren** klicken.")

# Formular: das Dashboard rechnet erst beim Klick auf "Aktualisieren" neu
# nicht bei jeder Bewegung am Regler. Das schont den (kostenlosen) Server.
with st.sidebar.form("steuerung", border=False):
    st.markdown("##### Zeitraum & Fenster")
    jahr_von, jahr_bis = st.slider(
        "Zeitraum (Jahre)", 2000, 2021, (2000, 2021)
    )

    fenster = st.radio(
        "Zeitfenster / Glättung (Monate)",
        [2, 5, 7, 9, 12],
        index=1,
        horizontal=True,
        help="Gleitender Durchschnitt über die monatlichen Werte — "
             "größeres Fenster = glattere Kurven, Trends besser sichtbar."
    )

    st.markdown("##### Daten-Filter")
    laender = st.multiselect(
        "UFO-Sichtungen: Länder",
        options=sorted(ufos["country"].dropna().unique()),
        default=[],
        help="Leer = alle Länder"
    )

    st.markdown("##### Darstellung")
    alle_fenster = st.checkbox(
        "Alle Zeitfenster vergleichen", value=False,
        help="Zeigt im Tab 'Zeitverlauf' zusätzlich alle Fenster (2-12 Monate) "
             "übereinander sowie die Korrelation je Fenstergröße."
    )

    normalisieren = st.checkbox(
        "Kurven normalisieren (z-Score)", value=True,
        help="Bringt beide Reihen auf dieselbe Skala — nur so sind sie fair vergleichbar."
    )

    st.form_submit_button("Aktualisieren", type="primary", width="stretch")

st.sidebar.markdown("---")
st.sidebar.caption(
    f"{len(filme):,} Sci-Fi-Filme · {len(ufos):,} Sichtungen".replace(",", ".")
)

# Filter + monatliche Aggregation (gecacht: gleiche Auswahl = keine Neuberechnung)
@st.cache_data
def aggregiere(jahr_von, jahr_bis, laender_tuple):
    f = filme[(filme["jahr"] >= jahr_von) & (filme["jahr"] <= jahr_bis)]
    u = ufos[(ufos["jahr"] >= jahr_von) & (ufos["jahr"] <= jahr_bis)]
    if laender_tuple:
        u = u[u["country"].isin(list(laender_tuple))]
    film_m = f.set_index("release_date").resample("MS").size().rename("Filme")
    ufo_m  = u.set_index("date_time").resample("MS").size().rename("UFOs")
    df = pd.concat([film_m, ufo_m], axis=1).fillna(0)
    return f, u, df

f, u, df = aggregiere(jahr_von, jahr_bis, tuple(laender))

# Gleitender Durchschnitt (Zeitfenster)
df["Filme_glatt"] = df["Filme"].rolling(fenster, center=True, min_periods=1).mean()
df["UFOs_glatt"]  = df["UFOs"].rolling(fenster, center=True, min_periods=1).mean()

def z(s):
    return (s - s.mean()) / s.std() if s.std() > 0 else s * 0

# Kopfbereich
st.title("Zusammenhang zwischen Sci-Fi-Filmveröffentlichungen und globalen UFO-Sichtungsmeldungen")
st.markdown(
    f"Eine explorative Analyse · **Zeitraum {jahr_von}–{jahr_bis}** · "
    f"Zeitfenster: **{fenster} Monate** · "
    f"{'Länder: ' + ', '.join(laender) if laender else 'alle Länder'}"
)

st.caption(
    "Hinweis: Diese App läuft auf einem kostenlosen Server mit begrenzten Ressourcen. "
    "Nach einem Klick auf 'Aktualisieren' bitte kurz warten, bis die Diagramme neu geladen "
    "sind, bevor die nächste Änderung folgt. Sehr viele Änderungen in schneller Folge können "
    "die App vorübergehend zum Absturz bringen — in dem Fall einfach die Seite neu laden."
)

pearson_r, pearson_p = stats.pearsonr(df["Filme_glatt"], df["UFOs_glatt"])
spearman_r, spearman_p = stats.spearmanr(df["Filme_glatt"], df["UFOs_glatt"])

c1, c2, c3, c4 = st.columns(4)
c1.metric("Filme im Zeitraum", f"{len(f):,}".replace(",", "."))
c2.metric("Sichtungen", f"{len(u):,}".replace(",", "."))
c3.metric("Pearson r", f"{pearson_r:+.3f}",
          help="Linearer Zusammenhang der geglätteten Monatswerte (−1 bis +1)")
c4.metric("Spearman ρ", f"{spearman_r:+.3f}",
          help="Rang-Korrelation — robust gegen Ausreißer")

# Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs(
    ["Zeitverlauf", "Korrelation", "Monats-Cluster", "Zeiträume vergleichen", "Heatmap"]
)

with tab1:
    st.subheader("Monatlicher Verlauf im direkten Vergleich")

    if normalisieren:
        y_film, y_ufo = z(df["Filme_glatt"]), z(df["UFOs_glatt"])
        y_titel = "z-Score (normalisiert)"
    else:
        y_film, y_ufo = df["Filme_glatt"], df["UFOs_glatt"]
        y_titel = "Anzahl pro Monat (geglättet)"

    fig = go.Figure()
    # Rohdaten dezent im Hintergrund
    fig.add_trace(go.Scatter(
        x=df.index, y=z(df["UFOs"]) if normalisieren else df["UFOs"],
        name="UFOs (roh)", line=dict(color=FARBE_UFO, width=1), opacity=0.18,
        showlegend=False, hoverinfo="skip"))
    fig.add_trace(go.Scatter(
        x=df.index, y=z(df["Filme"]) if normalisieren else df["Filme"],
        name="Filme (roh)", line=dict(color=FARBE_FILM, width=1), opacity=0.18,
        showlegend=False, hoverinfo="skip"))
    # Geglättete Kurven
    fig.add_trace(go.Scatter(x=df.index, y=y_ufo, name="UFO-Sichtungen",
                             line=dict(color=FARBE_UFO, width=3)))
    fig.add_trace(go.Scatter(x=df.index, y=y_film, name="Sci-Fi-Releases",
                             line=dict(color=FARBE_FILM, width=3)))
    fig.update_layout(
        height=480, template="plotly_dark",
        yaxis_title=y_titel, hovermode="x unified",
        legend=dict(orientation="h", y=1.08),
        margin=dict(t=30, b=10),
    )
    st.plotly_chart(fig, width="stretch")
    st.caption(f"Dünne Linien = Rohdaten, dicke Linien = gleitender {fenster}-Monats-Durchschnitt.")

    if alle_fenster:
        st.markdown("---")
        st.subheader("Vergleich aller Zeitfenster (2, 5, 7, 9, 12 Monate)")
        FENSTER_ALLE = [2, 5, 7, 9, 12]

        col_l, col_r = st.columns([2, 1])
        with col_l:
            fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                                subplot_titles=("UFO-Sichtungen", "Sci-Fi-Releases"),
                                vertical_spacing=0.10)
            farben_blau = px.colors.sample_colorscale("Teal", [0.35, 0.5, 0.65, 0.8, 0.95])
            farben_lila = px.colors.sample_colorscale("Purpor", [0.35, 0.5, 0.65, 0.8, 0.95])
            for i, w in enumerate(FENSTER_ALLE):
                ug = z(df["UFOs"].rolling(w, center=True, min_periods=1).mean())
                fg = z(df["Filme"].rolling(w, center=True, min_periods=1).mean())
                fig.add_trace(go.Scatter(x=df.index, y=ug, name=f"{w} Monate",
                                         legendgroup=f"{w}", line=dict(color=farben_blau[i], width=1.5 + i * 0.5)),
                              row=1, col=1)
                fig.add_trace(go.Scatter(x=df.index, y=fg, name=f"{w} Monate", showlegend=False,
                                         legendgroup=f"{w}", line=dict(color=farben_lila[i], width=1.5 + i * 0.5)),
                              row=2, col=1)
            fig.update_layout(height=560, template="plotly_dark",
                              legend=dict(orientation="h", y=1.10),
                              margin=dict(t=60, b=10))
            fig.update_yaxes(title_text="z-Score", row=1, col=1)
            fig.update_yaxes(title_text="z-Score", row=2, col=1)
            st.plotly_chart(fig, width="stretch")

        with col_r:
            r_werte = []
            for w in FENSTER_ALLE:
                fg = df["Filme"].rolling(w, center=True, min_periods=1).mean()
                ug = df["UFOs"].rolling(w, center=True, min_periods=1).mean()
                r_werte.append(fg.corr(ug))
            fig = go.Figure(go.Bar(
                x=[f"{w} M." for w in FENSTER_ALLE], y=r_werte,
                marker_color=FARBE_FILM,
                text=[f"{r:+.3f}" for r in r_werte], textposition="outside"))
            fig.update_layout(height=560, template="plotly_dark",
                              yaxis_title="Pearson r",
                              title="Korrelation je Fenstergröße",
                              yaxis_range=[0, max(r_werte) * 1.25],
                              margin=dict(t=60, b=10))
            st.plotly_chart(fig, width="stretch")

        st.caption("Je größer das Fenster, desto stärker wird kurzfristiges Rauschen "
                   "herausgefiltert. Steigt die Korrelation mit der Fenstergröße, deutet das "
                   "darauf hin, dass vor allem der langfristige Trend beider Reihen "
                   "zusammenhängt und weniger die kurzfristigen Schwankungen.")

with tab2:
    st.subheader("Wie stark hängen die Reihen zusammen?")
    col_a, col_b = st.columns([1, 1])

    with col_a:
        fig = px.scatter(
            df, x="Filme_glatt", y="UFOs_glatt",
            color=df.index.year.astype(str),
            labels={"Filme_glatt": "Filme / Monat (geglättet)",
                    "UFOs_glatt": "UFO-Sichtungen / Monat (geglättet)",
                    "color": "Jahr"},
            trendline="ols",
            color_discrete_sequence=px.colors.sequential.Plasma_r,
        )
        fig.update_layout(height=460, template="plotly_dark",
                          margin=dict(t=30, b=10))
        st.plotly_chart(fig, width="stretch")
        signifikanz = "signifikant"if pearson_p < 0.05 else "nicht signifikant"
        st.caption(f"Pearson r = {pearson_r:+.3f} (p = {pearson_p:.2g}, {signifikanz}) · "
                   f"Spearman ρ = {spearman_r:+.3f}")

    with col_b:
        st.markdown("**Zeitversetzte Korrelation (Lag-Analyse)**")
        st.caption("Verschiebt die Film-Reihe um n Monate: Folgen UFO-Sichtungen "
                   "den Kino-Releases — oder umgekehrt?")
        max_lag = 12
        lags = range(-max_lag, max_lag + 1)
        lag_r = [df["UFOs_glatt"].corr(df["Filme_glatt"].shift(l)) for l in lags]
        farben = [FARBE_FILM if r == max(lag_r) else "rgba(150,150,170,0.45)"for r in lag_r]
        fig = go.Figure(go.Bar(x=list(lags), y=lag_r, marker_color=farben))
        fig.add_hline(y=0, line_color="white", line_width=1)
        fig.update_layout(
            height=380, template="plotly_dark",
            xaxis_title="Verschiebung in Monaten (+ = Filme früher)",
            yaxis_title="Korrelation r", margin=dict(t=30, b=10),
        )
        st.plotly_chart(fig, width="stretch")
        best_lag = list(lags)[int(np.argmax(lag_r))]
        if best_lag > 0:
            deutung = f"Filme laufen den Sichtungen ~{best_lag} Monate **voraus**."
        elif best_lag < 0:
            deutung = f"Sichtungen laufen den Filmen ~{-best_lag} Monate voraus."
        else:
            deutung = "Stärkster Zusammenhang ohne Zeitversatz."
        st.info(f"Höchste Korrelation bei Lag = {best_lag}: {deutung}")

    st.warning("**Korrelation ≠ Kausalität** — beide Reihen wachsen über die Jahre, "
               "was allein schon Korrelation erzeugt. Die Lag-Analyse und der "
               "Zeitraum-Vergleich helfen, echte Muster von Trend-Artefakten zu trennen.")

with tab3:
    st.subheader("Saisonale Muster — Clusterung nach Monaten")

    col_a, col_b = st.columns(2)
    ufo_heat = u.groupby(["jahr", "monat"]).size().unstack(fill_value=0)
    film_heat = f.groupby(["jahr", "monat"]).size().unstack(fill_value=0)

    for col, heat, name, scale in [
        (col_a, ufo_heat, "UFO-Sichtungen", "Teal"),
        (col_b, film_heat, "Sci-Fi-Releases", "Purpor"),
    ]:
        with col:
            fig = px.imshow(
                heat,
                labels=dict(x="Monat", y="Jahr", color="Anzahl"),
                x=MONATSNAMEN[:heat.shape[1]],
                aspect="auto", color_continuous_scale=scale,
            )
            fig.update_layout(height=440, template="plotly_dark",
                              title=name, margin=dict(t=50, b=10))
            st.plotly_chart(fig, width="stretch")

    st.markdown("**Durchschnittliches Monatsprofil (alle Jahre gemittelt, normalisiert)**")
    ufo_profil = z(u.groupby("monat").size())
    film_profil = z(f.groupby("monat").size())
    fig = go.Figure()
    fig.add_trace(go.Bar(x=MONATSNAMEN, y=ufo_profil, name="UFOs",
                         marker_color=FARBE_UFO, opacity=0.85))
    fig.add_trace(go.Bar(x=MONATSNAMEN, y=film_profil, name="Filme",
                         marker_color=FARBE_FILM, opacity=0.85))
    fig.update_layout(height=380, template="plotly_dark", barmode="group",
                      yaxis_title="z-Score", legend=dict(orientation="h", y=1.1),
                      margin=dict(t=30, b=10))
    st.plotly_chart(fig, width="stretch")
    saison_r = float(np.corrcoef(ufo_profil, film_profil)[0, 1])
    st.caption(f"Korrelation der Monatsprofile: r = {saison_r:+.3f} — "
               "zeigt, ob beide Phänomene denselben Jahresrhythmus haben "
               "(UFOs typischerweise im Sommer, Releases oft vor Sommer/Weihnachten).")

with tab4:
    st.subheader("Zwei Zeiträume direkt gegenüberstellen")
    col_a, col_b = st.columns(2)
    with col_a:
        z1 = st.slider("Zeitraum A", 2000, 2021, (2000, 2010), key="za")
    with col_b:
        z2 = st.slider("Zeitraum B", 2000, 2021, (2011, 2021), key="zb")

    def zeitraum_stats(von, bis):
        ff = filme[(filme["jahr"] >= von) & (filme["jahr"] <= bis)]
        uu = ufos[(ufos["jahr"] >= von) & (ufos["jahr"] <= bis)]
        if laender:
            uu = uu[uu["country"].isin(laender)]
        fm = ff.set_index("release_date").resample("MS").size()
        um = uu.set_index("date_time").resample("MS").size()
        m = pd.concat([fm.rename("Filme"), um.rename("UFOs")], axis=1).fillna(0)
        m = m.rolling(fenster, center=True, min_periods=1).mean()
        r = m["Filme"].corr(m["UFOs"]) if len(m) > 2 else np.nan
        return ff, uu, r

    fA, uA, rA = zeitraum_stats(*z1)
    fB, uB, rB = zeitraum_stats(*z2)

    m1, m2, m3 = st.columns(3)
    m1.metric("Filme A  B", f"{len(fA):,}  {len(fB):,}".replace(",", "."),
              delta=f"{(len(fB)-len(fA))/max(len(fA),1)*100:+.0f} %")
    m2.metric("Sichtungen A  B", f"{len(uA):,}  {len(uB):,}".replace(",", "."),
              delta=f"{(len(uB)-len(uA))/max(len(uA),1)*100:+.0f} %")
    m3.metric("Korrelation A  B", f"{rA:+.2f}  {rB:+.2f}")

    # Monatsprofile beider Zeiträume nebeneinander
    fig = make_subplots(rows=1, cols=2, subplot_titles=(
        f"Zeitraum A · {z1[0]}–{z1[1]}", f"Zeitraum B · {z2[0]}–{z2[1]}"))
    for i, (ff, uu) in enumerate([(fA, uA), (fB, uB)], start=1):
        fig.add_trace(go.Bar(x=MONATSNAMEN, y=z(uu.groupby("monat").size()),
                             name="UFOs", marker_color=FARBE_UFO,
                             showlegend=(i == 1)), row=1, col=i)
        fig.add_trace(go.Bar(x=MONATSNAMEN, y=z(ff.groupby("monat").size()),
                             name="Filme", marker_color=FARBE_FILM,
                             showlegend=(i == 1)), row=1, col=i)
    fig.update_layout(height=400, template="plotly_dark", barmode="group",
                      legend=dict(orientation="h", y=1.15),
                      margin=dict(t=60, b=10))
    st.plotly_chart(fig, width="stretch")
    st.caption("Normalisierte Monatsprofile (z-Score) — so siehst du sofort, "
               "ob sich das saisonale Muster zwischen den Zeiträumen verschoben hat.")

WOCHENTAGE = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]

with tab5:
    st.subheader("Anpassbare Heatmap")
    ansicht = st.radio(
        "Ansicht", ["Weltkarte (Sichtungsdichte)", "Kalender (Zeitmuster)"],
        horizontal=True, key="hm_ansicht"
    )

    if ansicht.startswith("Weltkarte"):
        st.caption("Dichte der UFO-Sichtungen im gewählten Zeitraum. "
                   "Koordinaten liegen für rund 83 % der Meldungen vor.")

        radius = st.slider("Glühradius der Heatmap", 5, 30, 12,
                           help="Größerer Radius = weichere, großflächigere Darstellung.")

        @st.cache_data
        def geo_aggregation(jahr_von, jahr_bis, laender_tuple):
            g = ufos[(ufos["jahr"] >= jahr_von) & (ufos["jahr"] <= jahr_bis)]
            if laender_tuple:
                g = g[g["country"].isin(list(laender_tuple))]
            g = g.dropna(subset=["city_latitude", "city_longitude"])
            g = g.assign(lat=g["city_latitude"].round(1),
                         lon=g["city_longitude"].round(1))
            return g.groupby(["lat", "lon"]).size().reset_index(name="Sichtungen")

        geo = geo_aggregation(jahr_von, jahr_bis, tuple(laender))
        fig = px.density_map(
            geo, lat="lat", lon="lon", z="Sichtungen",
            radius=radius, zoom=1.2, center=dict(lat=30, lon=-40),
            map_style="carto-darkmatter",
            color_continuous_scale=["#0b0f1a", FARBE_UFO, "#ffffff"],
        )
        fig.update_layout(height=560, margin=dict(t=10, b=10, l=0, r=0))
        st.plotly_chart(fig, width="stretch")
        st.caption(f"{int(geo['Sichtungen'].sum()):,} Sichtungen mit Koordinaten "
                   f"im gewählten Zeitraum.".replace(",", "."))

    else:
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            quelle = st.radio("Datensatz", ["UFO-Sichtungen", "Sci-Fi-Filme"],
                              key="hm_quelle")
        daten = u if quelle == "UFO-Sichtungen" else f
        zeitspalte = "date_time" if quelle == "UFO-Sichtungen" else "release_date"

        dims = ["Jahr × Monat", "Monat × Wochentag"]
        if quelle == "UFO-Sichtungen":
            dims.append("Wochentag × Uhrzeit")
        with col_b:
            dimension = st.selectbox("Dimensionen", dims, key="hm_dim")
        with col_c:
            farbskala = st.selectbox(
                "Farbskala", ["Teal", "Purpor", "Viridis", "Plasma", "Magma"],
                index=0 if quelle == "UFO-Sichtungen" else 1, key="hm_farbe")

        d = daten.copy()
        d["wochentag"] = d[zeitspalte].dt.dayofweek
        d["stunde"] = d[zeitspalte].dt.hour

        if dimension == "Jahr × Monat":
            heat = d.groupby(["jahr", "monat"]).size().unstack(fill_value=0)
            x_labels, x_titel, y_titel = MONATSNAMEN[:heat.shape[1]], "Monat", "Jahr"
        elif dimension == "Monat × Wochentag":
            heat = d.groupby(["monat", "wochentag"]).size().unstack(fill_value=0)
            heat.index = [MONATSNAMEN[m - 1] for m in heat.index]
            x_labels, x_titel, y_titel = [WOCHENTAGE[i] for i in heat.columns], "Wochentag", "Monat"
        else:  # Wochentag × Uhrzeit
            heat = d.groupby(["wochentag", "stunde"]).size().unstack(fill_value=0)
            heat.index = [WOCHENTAGE[i] for i in heat.index]
            x_labels, x_titel, y_titel = list(heat.columns), "Uhrzeit (Stunde)", "Wochentag"

        fig = px.imshow(
            heat, x=x_labels, aspect="auto",
            labels=dict(x=x_titel, y=y_titel, color="Anzahl"),
            color_continuous_scale=farbskala,
        )
        fig.update_layout(height=520, template="plotly_dark",
                          title=f"{quelle}: {dimension}",
                          margin=dict(t=50, b=10))
        st.plotly_chart(fig, width="stretch")

        if dimension == "Wochentag × Uhrzeit":
            st.caption("Typisches Muster: Die meisten Sichtungen werden abends "
                       "zwischen 20 und 23 Uhr gemeldet, mit leichtem Übergewicht "
                       "am Wochenende.")
        st.caption("Die Heatmap nutzt die Auswahl aus der Seitenleiste "
                   "(Zeitraum und Länderfilter).")
