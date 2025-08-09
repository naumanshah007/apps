# Cervical Screening Decision Support (NZ/MMH)

## Local setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.local .env
python scripts/phase1_extract_rules.py  # creates empty rules workbook and OCRs any images in ./images
streamlit run app.py
```

Place the 11 input images in `./images` named exactly:
`1.jpg`..`10.jpg` and `table.jpg`.

## Docker

```bash
docker build -t screening-app .
docker run -p 8501:8501 -v $(pwd):/app screening-app
```

or

```bash
docker compose up --build
```

## Files
- `data/screening_rules_master_integrated.xlsx` is the rules source (sheet `Rules`).
- Admin page provides integrity checks and a rules viewer.
- PDF exports are saved to `./local_data/reports/`.