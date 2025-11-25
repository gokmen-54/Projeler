import numpy as np
from sklearn.ensemble import IsolationForest


class SimpleAnomalyDetector:
    def __init__(self) -> None:
        self.model = IsolationForest(contamination=0.05, random_state=42)
        self.is_fitted = False

    def fit(self, values: list[float]) -> None:
        data = np.array(values).reshape(-1, 1)
        self.model.fit(data)
        self.is_fitted = True

    def score(self, value: float) -> tuple[float, bool]:
        if not self.is_fitted:
            # Not enough data yet; treat as normal
            return 0.0, False
        prediction = self.model.decision_function([[value]])[0]
        is_anomaly = self.model.predict([[value]])[0] == -1
        return float(prediction), bool(is_anomaly)
