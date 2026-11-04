import numpy as np
import pandas as pd
from sklearn.preprocessing import RobustScaler


def log_scale(data, elements):
    """Apply log1p, then RobustScaler. Returns (log_values, scaled) as DataFrames."""
    log_values = np.log1p(data[elements])
    scaled = pd.DataFrame(
        RobustScaler().fit_transform(log_values),
        columns=elements,
        index=data.index,
    )
    return log_values, scaled
