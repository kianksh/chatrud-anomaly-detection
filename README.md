# Chatrud Geochemical Anomaly Detection

Anomaly detection for stream sediment geochemistry in an ophiolitic terrain. The pipeline combines:

1. Detection-limit handling (`<LOD` values replaced with `LOD x 0.75`)
2. `log1p` transform and `RobustScaler`
3. Isolation Forest to flag statistically unusual samples
4. Percentile-based extreme-value filters to keep only enriched samples
5. Deposit-specific pathfinder rules for chromite, VMS, epithermal and porphyry targets

The percentile filters are a simple extreme-value screen, not a fitted Generalized Pareto Distribution.

## Repository layout

```
.
├── notebooks/chatrud_anomaly_analysis.ipynb   step-by-step analysis
├── scripts/run_pipeline.py                    command-line entry point
├── src/chatrud_anomaly/
│   ├── data.py            workbook loading and detection-limit cleaning
│   ├── preprocessing.py   log1p + RobustScaler
│   ├── model.py           Isolation Forest
│   ├── filters.py         deposit models and percentile filter
│   ├── pipeline.py        end-to-end run
│   ├── plotting.py        all figures and maps
│   └── reporting.py       Excel report and figure export
└── pyproject.toml
```

## Installation

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -e .
pip install -e ".[notebook]"     # only if you want to run the notebook
```

## Input format

An Excel workbook (default sheet `Sheet2`) where:

- row 1 is the header,
- the first data row holds measurement units,
- the second data row holds detection limits,
- samples start from the third data row,
- the first four columns are metadata and include `Name`, `X` and `Y`, followed by one column per element.

Place the file in `data/` (ignored by git). Sampling coordinates and assay data are often confidential, so they are not tracked.

## Usage

```bash
python scripts/run_pipeline.py --input data/Chatrud_Final_data.xlsx --output-dir outputs
```

| Option | Default | Description |
| --- | --- | --- |
| `--input` | required | Path to the Excel workbook |
| `--sheet` | `Sheet2` | Worksheet name |
| `--output-dir` | `outputs` | Where results are written |
| `--contamination` | `0.10` | Share of samples Isolation Forest flags |
| `--n-estimators` | `500` | Number of trees |
| `--seed` | `42` | Random seed |
| `--no-plots` | off | Skip figure and map export |

Outputs:

- `anomalies_report.xlsx` with sheets `Chromite`, `VMS`, `Epithermal`, `Porphyry`, `Final_Anomalies`, `All_Anomalies`
- `figures/` with PNG charts, an enrichment table and interactive HTML maps

## Deposit models

Defined in `src/chatrud_anomaly/filters.py`. A candidate must reach the given percentile (computed on the whole dataset) in at least `min_elements` pathfinders.

| Model | Pathfinders | Percentile | Min. elements |
| --- | --- | --- | --- |
| General | Cr, Ni, Cu, Au, As, Sb, Mo | 95 | 1 |
| Chromite | Cr, Ni | 95 | 1 |
| VMS | Cu, Co, Zn, Fe | 95 | 1 |
| Epithermal | Cu, Au, Ag, As, Sb | 90 | 3 |
| Porphyry | Cu, Mo, Au, Ag, Fe | 80 | 3 |

## Using the package

```python
from chatrud_anomaly import load_geochemical_data, run_pipeline

data = load_geochemical_data("data/Chatrud_Final_data.xlsx")
result = run_pipeline(data, contamination=0.10)
print(result.summary())
```

## Limitations

- Isolation Forest detects outlyingness in any direction, so low-value outliers are also flagged; the percentile filters are what enforce enrichment.
- Thresholds are computed on the full dataset, so results depend on the sample population and are not absolute.
- Deposit-model thresholds were tuned for this survey area and should be revisited for other datasets.
