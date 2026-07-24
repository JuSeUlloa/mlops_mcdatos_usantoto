from __future__ import annotations

import argparse
import json
from pathlib import Path

import joblib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import mlflow
import mlflow.sklearn
import pandas as pd
import yaml
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    mean_absolute_error,
    r2_score,
    root_mean_squared_error,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from .data import load_processed_data
from .features import create_targets, get_feature_columns, split_train_test
from .predict import save_model_metadata


def load_params(params_path: str) -> dict:
    with open(params_path, "r") as f:
        return yaml.safe_load(f)


def build_model(model_params: dict, model_task: str) -> Pipeline:
    """
    Construye pipeline de RandomForest.
    
    Args:
        model_params: Parámetros del modelo (n_estimators, max_depth, random_state)
        model_task: "classification", "regression_return", "regression_volatility"
    """
    numeric_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )
    
    n_estimators = int(model_params.get("n_estimators", 100))
    max_depth = int(model_params.get("max_depth", 10)) if model_params.get("max_depth") else None
    random_state = int(model_params.get("random_state", 42))
    
    if model_task == "classification":
        model = RandomForestClassifier(
            n_estimators=n_estimators,
            max_depth=max_depth,
            random_state=random_state,
            n_jobs=-1,
        )
        return Pipeline(steps=[("preprocessor", numeric_pipeline), ("classifier", model)])
    else:
        model = RandomForestRegressor(
            n_estimators=n_estimators,
            max_depth=max_depth,
            random_state=random_state,
            n_jobs=-1,
        )
        return Pipeline(steps=[("preprocessor", numeric_pipeline), ("regressor", model)])


def evaluate_classification(y_true: pd.Series, predictions: np.ndarray, probabilities: np.ndarray) -> dict[str, float]:
    return {
        "accuracy": float(accuracy_score(y_true, predictions)),
        "f1_score": float(f1_score(y_true, predictions, average="binary")),
    }


def evaluate_regression(y_true: pd.Series, predictions: np.ndarray) -> dict[str, float]:
    return {
        "mae": float(mean_absolute_error(y_true, predictions)),
        "rmse": float(root_mean_squared_error(y_true, predictions)),
        "r2": float(r2_score(y_true, predictions)),
    }


def save_prediction_plot(y_true: pd.Series, predictions: np.ndarray, output_path: str) -> None:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    
    plt.figure(figsize=(7, 5))
    plt.scatter(y_true, predictions, alpha=0.65)
    min_value = min(y_true.min(), predictions.min())
    max_value = max(y_true.max(), predictions.max())
    plt.plot([min_value, max_value], [min_value, max_value], color="black", linestyle="--")
    plt.xlabel("Valor real")
    plt.ylabel("Predicción")
    plt.title("Predicción vs. valor real")
    plt.tight_layout()
    plt.savefig(path, dpi=140)
    plt.close()


def _train_and_log_model(
    symbol: str,
    X_train: pd.DataFrame,
    X_test: pd.DataFrame,
    y_train: pd.Series,
    y_test: pd.Series,
    model_task: str,
    params: dict,
    artifacts_dir: Path,
    reports_dir: Path
) -> dict:
    """
    Función genérica para entrenar y loguear un modelo en MLflow.
    
    Args:
        symbol: Símbolo del ticker
        X_train, X_test: Features de train y test
        y_train, y_test: Targets de train y test
        model_task: Tipo de tarea ("classification", "regression_return", "regression_volatility")
        params: Parámetros del modelo
        artifacts_dir: Directorio para guardar modelos
        reports_dir: Directorio para guardar reportes
    
    Returns:
        dict con métricas del modelo
    """
    pipeline = build_model(params["model"], model_task)
    
    with mlflow.start_run(run_name=f"{symbol}_{model_task}"):
        pipeline.fit(X_train, y_train)
        predictions = pipeline.predict(X_test)
        
        if model_task == "classification":
            probabilities = pipeline.predict_proba(X_test)[:, 1]
            metrics = evaluate_classification(y_test, predictions, probabilities)
            model_name = type(pipeline.named_steps["classifier"]).__name__
        else:
            metrics = evaluate_regression(y_test, predictions)
            model_name = type(pipeline.named_steps["regressor"]).__name__
        
        model_path = artifacts_dir / f"{symbol}_{model_task}.joblib"
        joblib.dump(pipeline, model_path)
        
        metrics_path = reports_dir / f"{symbol}_metrics_{model_task}.json"
        metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
        
        if model_task != "classification":
            plot_path = reports_dir / f"{symbol}_predicted_vs_actual_{model_task.replace('regression_', '')}.png"
            save_prediction_plot(y_test, predictions, str(plot_path))
        
        save_model_metadata(f"{symbol}_{model_task}", metrics, model_path, model_name)
        
        mlflow.log_params({
            "ticker": symbol,
            "model_type": "random_forest",
            "task": model_task,
            "n_estimators": params["model"].get("n_estimators"),
            "max_depth": params["model"].get("max_depth"),
        })
        mlflow.log_metrics(metrics)
        mlflow.log_artifact(str(metrics_path))
        
        if model_task != "classification":
            mlflow.log_artifact(str(plot_path))
        
        mlflow.sklearn.log_model(
            pipeline,
            name="model",
            serialization_format=mlflow.sklearn.SERIALIZATION_FORMAT_PICKLE,
        )
    
    return metrics


def run(ticker: str, params_path: str) -> None:
    params = load_params(params_path)
    symbol = ticker.strip().upper()
    
    data_path = Path(params["data"]["processed_dir"]) / f"{symbol}.csv"
    
    if not data_path.exists():
        raise FileNotFoundError(
            f"No se encontraron datos procesados para {symbol} en {data_path}. "
            f"Ejecuta GET /market-data/{symbol}/5y primero."
        )
    
    df = pd.read_csv(data_path, index_col=0, parse_dates=True)
    df = create_targets(df)
    df = df.dropna()
    
    feature_cols = get_feature_columns(df)
    X = df[feature_cols]
    test_size = params["split"]["test_size"]
    
    mlflow_config = params.get("mlflow", {})
    tracking_uri = mlflow_config.get("tracking_uri", "sqlite:///mlruns/mlflow.db")
    experiment_name = mlflow_config.get("experiment_name", "stock_price_prediction")
    
    mlflow.set_tracking_uri(tracking_uri)
    mlflow.set_experiment(experiment_name)
    
    artifacts_dir = Path("artifacts")
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    reports_dir = Path("reports")
    reports_dir.mkdir(parents=True, exist_ok=True)
    
    tasks = [
        ("classification", "CLASIFICACIÓN (Tendencia)", df["Target_Direction_t1"]),
        ("regression_return", "REGRESIÓN (Retorno)", df["Target_Return_t1"]),
        ("regression_volatility", "REGRESIÓN (Volatilidad)", df["Target_Volatility_t1"]),
    ]
    
    for model_task, task_name, y_target in tasks:
        print("\n" + "="*60)
        print(f"ENTRENANDO MODELO DE {task_name}")
        print("="*60)
        
        X_train, X_test = split_train_test(X, test_size)
        y_train, y_test = split_train_test(y_target, test_size)
        
        metrics = _train_and_log_model(
            symbol=symbol,
            X_train=X_train,
            X_test=X_test,
            y_train=y_train,
            y_test=y_test,
            model_task=model_task,
            params=params,
            artifacts_dir=artifacts_dir,
            reports_dir=reports_dir
        )
        
        if model_task == "classification":
            print(f"✓ Modelo de clasificación entrenado")
            print(f"  Accuracy: {metrics['accuracy']:.4f}")
            print(f"  F1 Score: {metrics['f1_score']:.4f}")
        else:
            print(f"✓ Modelo de regresión ({task_name.split('(')[1].rstrip(')')}) entrenado")
            print(f"  MAE: {metrics['mae']:.6f}")
            print(f"  RMSE: {metrics['rmse']:.6f}")
            print(f"  R2: {metrics['r2']:.4f}")
        
        print(f"  Modelo guardado en: artifacts/{symbol}_{model_task}.joblib")
    
    print("\n" + "="*60)
    print("TODOS LOS MODELOS ENTRENADOS EXITOSAMENTE")
    print("="*60)


def main():
    parser = argparse.ArgumentParser(description="Entrenar modelo de regresión para predicción de precios")
    parser.add_argument("--ticker", required=True, help="Símbolo del ticker (ej: AAPL, MSFT, GOOGL)")
    parser.add_argument("--params", default="params.yaml", help="Ruta al archivo de parámetros (default: params.yaml)")
    
    args = parser.parse_args()
    
    run(args.ticker, args.params)


if __name__ == "__main__":
    main()
