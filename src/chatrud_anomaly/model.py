from sklearn.ensemble import IsolationForest


def detect_anomalies(data, scaled, n_estimators=500, contamination=0.10, random_state=42):
    """Fit Isolation Forest. Returns (scored_data, anomalies); label -1 marks an anomaly."""
    model = IsolationForest(
        n_estimators=n_estimators,
        contamination=contamination,
        random_state=random_state,
    )
    scored = data.copy()
    scored["anomaly_label"] = model.fit_predict(scaled)
    scored["score_value"] = model.decision_function(scaled)
    anomalies = scored[scored["anomaly_label"] == -1].copy()
    return scored, anomalies
