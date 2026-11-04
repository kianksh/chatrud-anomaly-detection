import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.express as px
import seaborn as sns


def apply_style():
    sns.set_theme(style="whitegrid")
    plt.rcParams["figure.figsize"] = (10, 6)
    plt.rcParams["font.size"] = 12


def plot_correlation_heatmap(data, elements):
    corr = data[elements].corr(method="spearman")
    fig, ax = plt.subplots(figsize=(12, 10))
    sns.heatmap(
        corr, annot=True, fmt=".2f", cmap="RdBu_r", center=0, linewidths=0.5,
        cbar_kws={"label": "Spearman Correlation"}, annot_kws={"size": 10}, ax=ax,
    )
    ax.set_title("Spearman Correlation Matrix of Geochemical Elements", fontsize=16)
    fig.tight_layout()
    return fig


def plot_distribution_with_threshold(values, element, quantile=0.95):
    threshold = values.quantile(quantile)
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.histplot(values, bins=50, kde=True, color="teal", alpha=0.6, ax=ax)
    ax.axvline(
        threshold, color="red", linestyle="--", linewidth=2.5,
        label=f"{quantile:.0%} percentile: {threshold:.2f}",
    )
    ax.set_title(f"Distribution of {element} with {quantile:.0%} Threshold", fontsize=14)
    ax.set_xlabel(f"{element} concentration")
    ax.set_ylabel("Frequency")
    ax.legend()
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    return fig


def plot_raw_vs_log(raw, log_values, elements):
    fig, axes = plt.subplots(nrows=len(elements), ncols=2, figsize=(15, 3 * len(elements)))
    axes = np.atleast_2d(axes)
    for (left, right), element in zip(axes, elements):
        raw[element].hist(bins=30, ax=left, color="salmon", edgecolor="black")
        left.set_title(f"Raw: {element}")
        log_values[element].hist(bins=30, ax=right, color="orange", edgecolor="black")
        right.set_title(f"log1p: {element}")
    fig.tight_layout()
    return fig


def plot_score_distribution(scores):
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.hist(scores, bins=50, color="skyblue", edgecolor="black", alpha=0.7)
    ax.axvline(0, color="red", linestyle="--", label="Anomaly threshold (score = 0)")
    ax.set_title("Distribution of Isolation Forest Anomaly Scores")
    ax.set_xlabel("Decision function value")
    ax.set_ylabel("Frequency")
    ax.legend()
    fig.tight_layout()
    return fig


def plot_spatial_map(data, title, hover_columns, size_scale=1000):
    plot_data = data.copy()
    plot_data["marker_size"] = plot_data["score_value"].apply(
        lambda score: 5 if score >= 0 else abs(score) * size_scale
    )
    fig = px.scatter(
        plot_data, x="X", y="Y", color="score_value", size="marker_size",
        hover_data=hover_columns, title=title,
        color_continuous_scale="RdYlGn_r", labels={"score_value": "Anomaly Score"},
    )
    fig.update_layout(template="plotly_white")
    return fig


def plot_multi_model_map(targets_by_label, hover_columns, size_scale=100):
    frames = []
    for label, frame in targets_by_label.items():
        tagged = frame.copy()
        tagged["Type"] = label
        frames.append(tagged)
    combined = pd.concat(frames)
    combined["marker_size"] = combined["score_value"].abs() * size_scale
    fig = px.scatter(
        combined, x="X", y="Y", color="Type", size="marker_size",
        hover_data=hover_columns, template="plotly_white",
        title="Multi-Model Geochemical Prospectivity Map (Chatrud Area)",
        color_discrete_sequence=px.colors.qualitative.Alphabet,
    )
    fig.update_layout(
        xaxis_title="Easting (X)", yaxis_title="Northing (Y)", legend_title="Mineralization Type"
    )
    return fig


def plot_radar(scaled, index, elements, title="Geochemical Fingerprint (Normalized Radar Chart)"):
    subset = scaled.loc[index, elements]
    angles = np.linspace(0, 2 * np.pi, len(elements), endpoint=False).tolist()
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(9, 9), subplot_kw={"polar": True})
    for sample_index, row in subset.iterrows():
        values = row.tolist()
        values += values[:1]
        ax.plot(angles, values, linewidth=2, label=f"Target {sample_index}")
        ax.fill(angles, values, alpha=0.1)

    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(elements, fontsize=12, fontweight="bold")
    ax.set_title(title, size=16, y=1.1)
    if len(subset):
        ax.legend(loc="upper right", bbox_to_anchor=(1.3, 1.1), title="Target ID")
    ax.grid(True, linestyle="--", alpha=0.6)
    fig.tight_layout()
    return fig


def plot_target_validation(all_samples, if_anomalies, targets, x, y, label, annotate=False):
    fig, ax = plt.subplots(figsize=(10, 7))
    ax.scatter(all_samples[x], all_samples[y], color="lightgrey", alpha=0.5, s=20, label="All Samples")
    ax.scatter(if_anomalies[x], if_anomalies[y], color="blue", alpha=0.4, s=40, label="Isolation Forest Anomalies")
    ax.scatter(
        targets[x], targets[y], color="red", s=150, marker="*", edgecolor="black",
        label=f"Final {label} Targets",
    )
    if annotate:
        for index, row in targets.iterrows():
            ax.text(row[x], row[y], str(index), fontsize=10, fontweight="bold",
                    color="darkred", ha="right", va="bottom")
    ax.set_title(f"{label} Targets: {x} vs {y}", fontsize=16, fontweight="bold")
    ax.set_xlabel(f"{x} concentration", fontsize=12)
    ax.set_ylabel(f"{y} concentration", fontsize=12)
    ax.legend(loc="upper right")
    ax.grid(True, linestyle="--", alpha=0.5)
    fig.tight_layout()
    return fig


def enrichment_table(targets, background, elements):
    table = targets[elements].mean().to_frame(name="Anomaly")
    table["Background"] = background[elements].mean()
    table["Enrichment Factor"] = table["Anomaly"] / table["Background"]
    return table.sort_values("Enrichment Factor", ascending=False)


def plot_enrichment(table, title="Anomaly Signature vs Background"):
    fig, ax = plt.subplots(figsize=(14, 6))
    table[["Anomaly", "Background"]].plot(kind="bar", color=["salmon", "skyblue"], ax=ax)
    ax.set_title(title, fontsize=14)
    ax.set_ylabel("Mean concentration (log scale)")
    ax.set_yscale("log")
    ax.grid(axis="y", linestyle="--", alpha=0.7)
    fig.tight_layout()
    return fig


def plot_reduction_flow(counts):
    fig, ax = plt.subplots(figsize=(8, 5))
    colors = ["lightgrey", "orange", "red", "darkred", "purple", "brown"][: len(counts)]
    bars = ax.bar(list(counts.keys()), list(counts.values()), color=colors)
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2, height + 1, int(height),
                ha="center", va="bottom", fontweight="bold")
    ax.set_title("Sample Reduction Flow: From Raw Data to Targets")
    ax.set_ylabel("Number of Samples")
    fig.tight_layout()
    return fig
