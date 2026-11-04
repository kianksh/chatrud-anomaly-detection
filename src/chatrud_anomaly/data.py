from pathlib import Path

import numpy as np
import pandas as pd

NON_DETECT_FACTOR = 0.75
METADATA_COLUMNS = 4
ID_COLUMNS = ["Name", "X", "Y"]
TARGET_ELEMENTS = [
    "Cr", "Ni", "Co", "Cu", "Zn", "Pb", "Au", "Ag",
    "As", "Sb", "Fe", "Mg", "Ti", "Al", "Mo",
]


def parse_concentration(value):
    """Convert a raw cell to float; values like '<0.5' become 0.75 * detection limit."""
    text = str(value).strip()
    try:
        if text.startswith("<"):
            return float(text[1:]) * NON_DETECT_FACTOR
        return float(text)
    except ValueError:
        return np.nan


def load_geochemical_data(path, sheet_name="Sheet2", elements=None):
    """Load the lab workbook: row 0 holds units, row 1 detection limits, data starts at row 2."""
    elements = list(elements or TARGET_ELEMENTS)
    raw = pd.read_excel(Path(path), sheet_name=sheet_name, header=0)
    detection_limits = raw.iloc[1].apply(pd.to_numeric, errors="coerce")
    data = raw.iloc[2:].copy()

    for column in data.columns[METADATA_COLUMNS:]:
        if pd.notna(detection_limits[column]):
            data[column] = data[column].apply(parse_concentration)

    clean = data[ID_COLUMNS + elements].reset_index(drop=True)
    clean[elements] = clean[elements].apply(pd.to_numeric)
    return clean
