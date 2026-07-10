# Zusammenhang zwischen Sci-Fi-Filmveröffentlichungen und globalen UFO-Sichtungsmeldungen

Interaktives Analyse-Dashboard. Projektarbeit im Modul Datenmanagement.

## Live-Version

Das Dashboard ist ohne Installation im Browser erreichbar:
https://ufo-movie-dashboard-projektarbeit.streamlit.app/

Hinweise zur Nutzung der Live-Version:

- Die App wird auf der kostenlosen Streamlit Community Cloud gehostet. Wurde sie
  längere Zeit nicht aufgerufen, erscheint zunächst die Meldung "Yes, get this
  app back up". Nach einem Klick darauf startet die App innerhalb von etwa
  30 Sekunden.
- Erscheint die Meldung "Oh no. Error running app", hat der Server seine
  Ressourcengrenze erreicht (dies kann bei sehr vielen Eingaben in schneller
  Folge passieren). In diesem Fall die Seite neu laden. Das Dashboard selbst
  enthält keinen Fehler.
- Einstellungen werden in der Seitenleiste gewählt und erst mit dem Button
  "Aktualisieren" übernommen. Nach dem Klick kurz warten, bis alle Diagramme
  neu geladen sind, bevor die nächste Änderung vorgenommen wird.

## Projektbeschreibung

Untersucht wird explorativ, ob zwischen der Anzahl veröffentlichter
Science-Fiction-Filme und der Anzahl gemeldeter UFO-Sichtungen ein
statistischer Zusammenhang besteht.

Datengrundlage:

- Filme: 11.844 Science-Fiction-Filme (2000 bis 2021) mit Titel,
  Veröffentlichungsdatum und Genres
- UFO-Sichtungen: 116.835 Meldungen (2000 bis 2021) mit Land, Stadt,
  Zeitpunkt und Koordinaten

Beide Datensätze werden monatlich aggregiert, über wählbare Zeitfenster
geglättet und mittels Korrelationsanalyse (Pearson und Spearman) verglichen.

## Funktionen

Das Dashboard umfasst vier Ansichten:

1. Zeitverlauf: Beide Zeitreihen im direkten Vergleich, Glättung über
   2, 5, 7, 9 oder 12 Monate, optionale z-Score-Normalisierung sowie ein
   Vergleich aller Zeitfenster gleichzeitig inklusive der Korrelation je
   Fenstergröße.
2. Korrelation: Streudiagramm mit Regressionsgerade, Pearson r und
   Spearman rho mit Signifikanzangabe sowie eine Lag-Analyse
   (Verschiebung um bis zu 12 Monate in beide Richtungen).
3. Monats-Cluster: Heatmaps (Jahr mal Monat) für beide Datensätze und
   gemittelte saisonale Monatsprofile im Vergleich.
4. Zeiträume vergleichen: Zwei frei wählbare Zeiträume nebeneinander
   mit Veränderung der Fallzahlen, der Korrelation und der Saisonmuster.

Alle Ansichten reagieren auf die Auswahl in der Seitenleiste (Jahre,
Zeitfenster, Länderfilter, Normalisierung).

## Lokale Ausführung

Voraussetzung: Python 3.9 oder neuer.

    git clone https://github.com/ChibiusaCho/ufo-dashboard.git
    cd ufo-dashboard
    pip install -r requirements.txt
    streamlit run app.py

Das Dashboard öffnet sich anschließend unter http://localhost:8501.

## Projektstruktur

    app.py                      Dashboard (Streamlit und Plotly)
    requirements.txt            Python-Abhängigkeiten
    Film_Datensatz_Final.csv    Sci-Fi-Filme
    Ufo_Datensatz_Final.csv     UFO-Sichtungen

## Hinweis zur Interpretation

Korrelation ist keine Kausalität. Beide Zeitreihen wachsen über den
Betrachtungszeitraum, was allein bereits eine positive Korrelation erzeugt.
Dass die Korrelation mit zunehmender Fenstergröße steigt (r = 0,24 bei
2 Monaten bis r = 0,35 bei 12 Monaten), deutet darauf hin, dass vor allem
der langfristige Trend beider Phänomene zusammenhängt und weniger die
kurzfristigen Schwankungen. Die Lag-Analyse und der Zeitraum-Vergleich im
Dashboard helfen, Trend-Artefakte von echten Mustern zu unterscheiden.
