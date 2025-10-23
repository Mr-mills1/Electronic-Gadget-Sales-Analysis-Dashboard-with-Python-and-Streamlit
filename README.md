# Electronics Sales Streamlit Dashboard

This small Streamlit app reproduces the analysis in `report.ipynb` and provides interactive filtering and visualizations for the sales CSVs included in this workspace.

Files created:
- `app.py` — the Streamlit application
- `requirements.txt` — Python dependencies

How to run (Windows PowerShell):

```powershell
python -m pip install -r requirements.txt
streamlit run app.py
```

Notes:
- The app expects the CSV files from the original notebook to be present in the same folder.
- If you use a virtual environment, activate it before installing dependencies.
