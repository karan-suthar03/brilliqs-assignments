"""Read the sensor data and report outliers and late-arriving events."""

import pandas as pd

INPUT_FILE = "sensor_data.csv"
Z_THRESHOLD = 3
LATE_AFTER_MINUTES = 5


def load_data():
    df = pd.read_csv(INPUT_FILE, parse_dates=["event_time", "received_at"])

    df["delay_minutes"] = (df["received_at"] - df["event_time"]).dt.total_seconds() / 60

    # each sensor sits at its own baseline, so the z-score has to be per device
    grouped = df.groupby("device_id")["reading"]
    df["z_score"] = (df["reading"] - grouped.transform("mean")) / grouped.transform("std")
    return df


def main():
    df = load_data()

    outliers = df[df["z_score"].abs() > Z_THRESHOLD]

    # a slow network and a slow device clock look identical from here: both just
    # mean the reading is older than its arrival. They are counted together.
    late = df[df["delay_minutes"] > LATE_AFTER_MINUTES]

    print(f"rows read: {len(df)}")
    print(f"outliers (|z| > {Z_THRESHOLD}): {len(outliers)}")
    print(f"late or backdated (delay > {LATE_AFTER_MINUTES} min): {len(late)}")

    print()
    print("per device:")
    for device, group in df.groupby("device_id"):
        outlier_count = (group["z_score"].abs() > Z_THRESHOLD).sum()
        late_count = (group["delay_minutes"] > LATE_AFTER_MINUTES).sum()
        print(f"  {device}  mean {group['reading'].mean():.2f}"
              f"  std {group['reading'].std():.2f}"
              f"  outliers {outlier_count}"
              f"  late {late_count}")

    print()
    print("worst 10 outliers:")
    worst = outliers.reindex(outliers["z_score"].abs().sort_values(ascending=False).index)
    for _, row in worst.head(10).iterrows():
        print(f"  {row['device_id']}  {row['event_time']}  "
              f"reading {row['reading']:.2f}  z {row['z_score']:.2f}")

    print()
    print("worst 5 delays:")
    for _, row in late.nlargest(5, "delay_minutes").iterrows():
        print(f"  {row['device_id']}  {row['event_time']}  "
              f"{row['delay_minutes']:.0f} min late")

    outliers.to_csv("outliers.csv", index=False)
    print()
    print(f"wrote outliers.csv with {len(outliers)} rows")


if __name__ == "__main__":
    main()
