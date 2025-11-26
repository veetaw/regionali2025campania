# Heatmap Candidati - Elezioni Regionali Campania 2025

Visualizzazione interattiva dei risultati elettorali per la provincia di Salerno.

## Come usare

1. Apri `heatmap_candidati.html` nel browser
2. Passa il mouse sui comuni per vedere i candidati più votati
3. Usa il menu a tendina per filtrare per candidato specifico

## File necessari

- `heatmap_candidati.html` - Mappa interattiva
- `salerno_candidati.geojson` - Dati geografici ed elettorali

## Deploy su GitHub Pages

1. Crea un repository su GitHub
2. Carica entrambi i file (HTML e GeoJSON) nella root del repository
3. Vai su Settings > Pages
4. Seleziona la branch `main` come source
5. La tua mappa sarà disponibile su `https://[tuo-username].github.io/[nome-repo]/heatmap_candidati.html`

## Tecnologie

- Leaflet.js per la mappa
- OpenStreetMap come base layer
- Dati: Elezioni Regionali Campania 23/11/2025
