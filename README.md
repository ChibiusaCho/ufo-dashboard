# UFO & Sci-Fi Dashboard
Ein Streamlit-Dashboard das UFO-Sichtungen und Scinece-Fiction-Filmrealeases monatlich gegenüberstellt und auf Zusammenhänge untersucht.

#Live-Demo
Hier klicken, um das Dashboard direkt im Browser zu öffnen, keine Installation nötig:

> https://DEINE-APP.streamlit.app (Link nach dem Deploy hier eintragen)

Hinweis: Wurde die App länger nicht genutzt, erscheint zuerst ein Button
„Yes, get this app back up" —> einmal klicken und ca. 30 Sekunden warten.

Funktionen
- Zeitverlauf — beide Zeitreihen im direkten Vergleich, wählbares Glättungsfenster (2 / 5 / 7 Monate), optional z-Score-normalisiert
- Korrelation — Scatterplot mit Regressionslinie, Pearson & Spearman, Lag-Analyse (±12 Monate): Laufen Filme den Sichtungen voraus?
- Monats-Cluster — Heatmaps (Jahr × Monat) und gemittelte saisonale Monatsprofile
- Zeitraum-Vergleich — zwei frei wählbare Zeiträume mit Kennzahlen und Monatsprofilen nebeneinander
Alle Filter (Jahre, Zeitfenster, Länder, Normalisierung) in der Sidebar.

Lokal starten
# 1. Repository klonen oder als ZIP herunterladen
git clone https://github.com/ChibiusaCho/ufo-dashboard.git
cd ufo-dashboard

# 2. Pakete installieren
pip install -r requirements.txt

# 3. Dashboard starten
streamlit run app.py
--
 Hinweis zur Interpretation
Korrelation ≠ Kausalität:
Beide Zeitreihen wachsen über den Betrachtungszeitraum, was allein bereits Korrelation erzeugt. Die Lag-Analyse und der Zeitraum-Vergleich im Dashboard helfen, Trend-Artefakte von echten Mustern zu unterscheiden.
