import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, r2_score, root_mean_squared_error
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from sesion_duration.config import ensure_parent, load_params


TARGET_COLUMN = "session_minutes"
NUMERIC_FEATURES = [
    "historical_avg_session_minutes",
    "historical_sessions_last_7d",
    "days_since_last_session",
    "hour_of_day",
    "push_received_last_24h",
]
CATEGORICAL_FEATURES = ["segment", "device_os", "site", "entry_point", "day_of_week"]


def build_model(model_params: dict) -> Pipeline:
    """Build a regression pipeline from params.yaml."""
    numeric_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )
    categorical_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("encoder", OneHotEncoder(handle_unknown="ignore")),
        ]
    )
    preprocessor = ColumnTransformer(
        transformers=[
            ("numeric", numeric_pipeline, NUMERIC_FEATURES),
            ("categorical", categorical_pipeline, CATEGORICAL_FEATURES),
        ]
    )

    model_type = model_params["type"]
    if model_type == "linear_regression":
        regressor = LinearRegression()
    elif model_type == "random_forest":
        regressor = RandomForestRegressor(
            n_estimators=int(model_params["n_estimators"]),
            max_depth=int(model_params["max_depth"]),
            random_state=int(model_params["random_state"]),
            n_jobs=-1,
        )
    else:
        raise ValueError(f"Modelo no soportado: {model_type}")

    return Pipeline(steps=[("preprocessor", preprocessor), ("regressor", regressor)])


def evaluate(y_true: pd.Series, predictions: np.ndarray) -> dict[str, float]:
    """Compute standard regression metrics."""
    return {
        "mae": float(mean_absolute_error(y_true, predictions)),
        "rmse": float(root_mean_squared_error(y_true, predictions)),
        "r2": float(r2_score(y_true, predictions)),
    }


def save_prediction_plot(y_true: pd.Series, predictions: np.ndarray, output_path: str) -> None:
    """Save a predicted vs actual scatter plot."""
    import matplotlib.pyplot as plt

    path = ensure_parent(output_path)
    plt.figure(figsize=(7, 5))
    plt.scatter(y_true, predictions, alpha=0.65)
    min_value = min(y_true.min(), predictions.min())
    max_value = max(y_true.max(), predictions.max())
    plt.plot([min_value, max_value], [min_value, max_value], color="black", linestyle="--")
    plt.xlabel("Valor real")
    plt.ylabel("Prediccion")
    plt.title("Prediccion vs. valor real")
    plt.tight_layout()
    plt.savefig(path, dpi=140)
    plt.close()


def run() -> None:
    import joblib
    import mlflow
    import mlflow.sklearn

    parser = argparse.ArgumentParser()
    parser.add_argument("--params", default="params.yaml")
    args = parser.parse_args()

    params = load_params(args.params)
    train_data = pd.read_csv(params["data"]["processed_train_path"])
    test_data = pd.read_csv(params["data"]["processed_test_path"])

    X_train = train_data[NUMERIC_FEATURES + CATEGORICAL_FEATURES]
    y_train = train_data[TARGET_COLUMN]
    X_test = test_data[NUMERIC_FEATURES + CATEGORICAL_FEATURES]
    y_test = test_data[TARGET_COLUMN]

    pipeline = build_model(params["model"])
    mlflow.set_tracking_uri(params["mlflow"]["tracking_uri"])
    mlflow.set_experiment(params["mlflow"]["experiment_name"])

    with mlflow.start_run(run_name=params["model"]["type"]):
        pipeline.fit(X_train, y_train)
        predictions = pipeline.predict(X_test)
        metrics = evaluate(y_test, predictions)

        model_path = ensure_parent("models/regression_model.joblib")
        metrics_path = ensure_parent("reports/metrics.json")
        predictions_path = ensure_parent("reports/predictions.csv")
        plot_path = Path("reports/predicted_vs_actual.png")

        joblib.dump(pipeline, model_path)
        metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
        pd.DataFrame({"actual": y_test, "prediction": predictions}).to_csv(
            predictions_path, index=False
        )
        save_prediction_plot(y_test, predictions, str(plot_path))

        mlflow.log_params(
            {
                "model_type": params["model"]["type"],
                "n_estimators": params["model"].get("n_estimators"),
                "max_depth": params["model"].get("max_depth"),
                "model_random_state": params["model"].get("random_state"),
                "data_random_state": params["data"]["random_state"],
                "n_samples": params["data"]["n_samples"],
                "test_size": params["split"]["test_size"],
            }
        )
        mlflow.log_metrics(metrics)
        mlflow.log_artifact(str(metrics_path))
        mlflow.log_artifact(str(predictions_path))
        mlflow.log_artifact(str(plot_path))
        mlflow.sklearn.log_model(
            pipeline,
            name="model",
            serialization_format=mlflow.sklearn.SERIALIZATION_FORMAT_PICKLE,
        )

    print(f"Metricas guardadas en {metrics_path}: {metrics}")


if __name__ == "__main__":
    main()