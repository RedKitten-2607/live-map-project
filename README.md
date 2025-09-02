# Live Map Project

An internal tool to visualize dark store locations on an interactive Google Map.

## Structure
- `data_pipeline/` → Python scripts to fetch data from Postgres and export JSON + config.
- `frontend/` → Static UI (HTML, CSS, JS) served via GitHub Pages.

## Usage
1. Set your API key in `data_pipeline/config.py`.
2. Run the pipeline:
   ```bash
   cd data_pipeline
   python export_json.py
