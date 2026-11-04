from dataclasses import dataclass, field

import pandas as pd

from .data import TARGET_ELEMENTS
from .filters import DEPOSIT_MODELS, GENERAL_MODEL, apply_filter
from .model import detect_anomalies
from .preprocessing import log_scale


@dataclass
class PipelineResult:
    elements: list
    scored: pd.DataFrame
    log_values: pd.DataFrame
    scaled: pd.DataFrame
    anomalies: pd.DataFrame
    general_targets: pd.DataFrame
    deposit_targets: dict = field(default_factory=dict)

    def summary(self):
        rows = {
            "Raw samples": len(self.scored),
            "Isolation Forest anomalies": len(self.anomalies),
            "General percentile filter": len(self.general_targets),
        }
        rows.update({f"{key} targets": len(frame) for key, frame in self.deposit_targets.items()})
        return pd.Series(rows, name="count")


def run_pipeline(
    data,
    elements=None,
    contamination=0.10,
    n_estimators=500,
    random_state=42,
    deposit_models=DEPOSIT_MODELS,
):
    elements = list(elements or TARGET_ELEMENTS)
    log_values, scaled = log_scale(data, elements)
    scored, anomalies = detect_anomalies(
        data, scaled, n_estimators, contamination, random_state
    )
    general_targets = apply_filter(anomalies, scored, GENERAL_MODEL)
    deposit_targets = {
        model.key: apply_filter(anomalies, scored, model) for model in deposit_models
    }
    return PipelineResult(
        elements=elements,
        scored=scored,
        log_values=log_values,
        scaled=scaled,
        anomalies=anomalies,
        general_targets=general_targets,
        deposit_targets=deposit_targets,
    )
