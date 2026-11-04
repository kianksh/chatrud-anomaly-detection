from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from .filters import DEPOSIT_MODELS
from .plotting import (
    enrichment_table,
    plot_enrichment,
    plot_multi_model_map,
    plot_radar,
    plot_reduction_flow,
    plot_score_distribution,
    plot_spatial_map,
    plot_target_validation,
)

HOVER_COLUMNS = ["Name", "Cr", "Cu", "Au", "Mo", "Zn"]


def write_excel_report(result, path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with pd.ExcelWriter(path) as writer:
        for key, frame in result.deposit_targets.items():
            frame.to_excel(writer, sheet_name=key, index=False)
        result.general_targets.to_excel(writer, sheet_name="Final_Anomalies", index=False)
        result.anomalies.to_excel(writer, sheet_name="All_Anomalies", index=False)
    return path


def save_figures(result, directory, deposit_models=DEPOSIT_MODELS):
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)

    def save(fig, name):
        fig.savefig(directory / name, dpi=150, bbox_inches="tight")
        plt.close(fig)

    save(plot_score_distribution(result.scored["score_value"]), "score_distribution.png")

    table = enrichment_table(result.general_targets, result.scored, result.elements)
    table.to_csv(directory / "enrichment_factors.csv")
    save(plot_enrichment(table), "enrichment.png")

    counts = {
        "Raw Data": len(result.scored),
        "Isolation Forest": len(result.anomalies),
        "Percentile Filter": len(result.general_targets),
    }
    save(plot_reduction_flow(counts), "reduction_flow.png")

    hover = ["Name"] + result.elements
    plot_spatial_map(result.scored, "Spatial Distribution of Geochemical Anomalies", hover).write_html(
        directory / "map_all_samples.html"
    )
    plot_spatial_map(
        result.general_targets, "Spatial Distribution of Refined Geochemical Anomalies", hover
    ).write_html(directory / "map_refined_anomalies.html")

    targets_by_label = {}
    for model in deposit_models:
        targets = result.deposit_targets[model.key]
        targets_by_label[model.label] = targets
        if targets.empty:
            continue
        save(
            plot_radar(result.scaled, targets.index, list(model.pathfinders),
                       title=f"{model.label}: Geochemical Fingerprint"),
            f"radar_{model.key.lower()}.png",
        )
        for x, y in model.validation_pairs:
            save(
                plot_target_validation(result.scored, result.anomalies, targets, x, y,
                                       model.label, annotate=True),
                f"validation_{model.key.lower()}_{x}_{y}.png",
            )

    non_empty = {label: frame for label, frame in targets_by_label.items() if not frame.empty}
    if non_empty:
        plot_multi_model_map(non_empty, HOVER_COLUMNS).write_html(directory / "map_multi_model.html")
