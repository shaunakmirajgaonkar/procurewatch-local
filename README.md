# 🏛️ ProcureWatch Local
Local-first public procurement anomaly screening dashboard.

Features: explainable 0–100 screening, pricing and bid-gap signals, competition analysis, supplier concentration, repeat-win signals, human conflict-review signal, CSV analysis, SQLite, Plotly, tests, and synthetic data.

A screening score is not proof of fraud, corruption, collusion, bid-rigging, or conflict of interest.

## Run
```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
python3 self_test.py
python3 -m streamlit run app.py --server.port 8510
```
