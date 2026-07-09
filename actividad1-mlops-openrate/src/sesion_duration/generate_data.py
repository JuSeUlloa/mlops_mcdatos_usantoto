import argparse
from pathlib import Path

import numpy as np
import pandas as pd
import yaml


def generate_session_data(n_samples: int, random_state: int, noise_std: float) -> pd.DataFrame:
    rng = np.random.default_rng(random_state)

    segments = ["new", "casual", "regular", "power_user"]
    device_os_list = ["Android", "iOS"]
    sites = ["web", "mobile_app", "tablet_app"]
    entry_points = ["push_notification", "organic", "deep_link", "search"]

    data = {
        "historical_avg_session_minutes": rng.uniform(5, 120, n_samples),
        "historical_sessions_last_7d": rng.integers(0, 30, n_samples),
        "days_since_last_session": rng.integers(0, 90, n_samples),
        "hour_of_day": rng.integers(0, 24, n_samples),
        "day_of_week": rng.choice(
            ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
            n_samples,
        ),
        "push_received_last_24h": rng.integers(0, 10, n_samples),
        "segment": rng.choice(segments, n_samples),
        "device_os": rng.choice(device_os_list, n_samples),
        "site": rng.choice(sites, n_samples),
        "entry_point": rng.choice(entry_points, n_samples),
    }

    df = pd.DataFrame(data)

    base = (
        0.4 * df["historical_avg_session_minutes"]
        + 1.5 * df["historical_sessions_last_7d"]
        - 0.3 * df["days_since_last_session"]
        + 0.2 * df["push_received_last_24h"]
    )
    segment_effect = df["segment"].map(
        {"new": -5, "casual": 0, "regular": 5, "power_user": 15}
    )
    df["session_minutes"] = (base + segment_effect + rng.normal(0, noise_std, n_samples)).clip(1)

    return df


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--params", default="params.yaml")
    args = parser.parse_args()

    with open(args.params, "r", encoding="utf-8") as f:
        params = yaml.safe_load(f)

    n_samples = params["data"]["n_samples"]
    random_state = params["data"]["random_state"]
    noise_std = params["data"].get("noise_std", 5.0)
    test_size = params["split"]["test_size"]

    df = generate_session_data(n_samples, random_state, noise_std)

    split_idx = int(n_samples * (1 - test_size))
    train_df = df.iloc[:split_idx]
    test_df = df.iloc[split_idx:]

    train_path = Path(params["data"]["processed_train_path"])
    test_path = Path(params["data"]["processed_test_path"])
    train_path.parent.mkdir(parents=True, exist_ok=True)
    test_path.parent.mkdir(parents=True, exist_ok=True)

    train_df.to_csv(train_path, index=False)
    test_df.to_csv(test_path, index=False)
    print(f"Train: {len(train_df)} rows -> {train_path}")
    print(f"Test:  {len(test_df)} rows -> {test_path}")


if __name__ == "__main__":
    main()
