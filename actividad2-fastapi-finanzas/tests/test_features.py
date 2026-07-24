from __future__ import annotations

import pandas as pd
import pytest

from financial_api.features import create_features, create_targets, get_feature_columns, split_train_test


@pytest.fixture
def sample_df():
    dates = pd.date_range("2020-01-01", periods=100, freq="D")
    return pd.DataFrame({
        "Open": range(100, 200),
        "High": range(101, 201),
        "Low": range(99, 199),
        "Close": range(100, 200),
        "Volume": [1000] * 100
    }, index=dates)


def test_create_features(sample_df):
    result = create_features(sample_df)
    
    assert "MA_7" in result.columns
    assert "MA_30" in result.columns
    assert "Volatility_7" in result.columns
    assert "Return_1d" in result.columns
    assert "Lag_1" in result.columns


def test_create_targets(sample_df):
    result = create_features(sample_df)
    result = create_targets(result)
    
    assert "Target_Return_t1" in result.columns
    assert "Target_Direction_t1" in result.columns
    assert "Target_Volatility_t1" in result.columns


def test_get_feature_columns(sample_df):
    features = create_features(sample_df)
    features = create_targets(features)
    feature_cols = get_feature_columns(features)
    
    # Close, Open, High, Low deben estar excluidos
    assert "Close" not in feature_cols
    assert "Open" not in feature_cols
    assert "High" not in feature_cols
    assert "Low" not in feature_cols
    
    # Targets deben estar excluidos
    assert "Target_Return_t1" not in feature_cols
    assert "Target_Direction_t1" not in feature_cols
    assert "Target_Volatility_t1" not in feature_cols
    
    # Features válidas deben estar incluidas
    assert "Volume" in feature_cols
    assert "MA_7" in feature_cols
    assert "Volatility_7" in feature_cols


def test_split_train_test(sample_df):
    features = create_features(sample_df)
    train, test = split_train_test(features, test_size=0.2)
    
    assert len(train) + len(test) == len(features)
    assert len(test) >= int(len(features) * 0.2) - 1
    assert len(test) <= int(len(features) * 0.2) + 1
