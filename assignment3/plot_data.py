"""Walk through the sensor data one chart at a time.

Close each window to move on to the next step.
"""

import matplotlib
matplotlib.use("TkAgg")

import matplotlib.pyplot as plt

from detect_anomalies import LATE_AFTER_MINUTES, Z_THRESHOLD, load_data

DEVICE_TO_PLOT = "sensor-01"


def step_1_raw_data(df):
    print("STEP 1 - the raw data")
    print(df[["device_id", "event_time", "received_at", "reading"]].head(10).to_string(index=False))
    print()

    device = DEVICE_TO_PLOT
    data = df[df["device_id"] == device].sort_values("event_time")

    plt.figure(figsize=(14, 5))
    plt.plot(data["event_time"], data["reading"], linewidth=0.7)
    plt.title(f"Step 1: {device} readings over time (close to continue)")
    plt.xlabel("event time")
    plt.ylabel("reading")
    plt.tight_layout()
    plt.show()


def step_2_all_devices(df):
    print("STEP 2 - every device has its own baseline")
    print(df.groupby("device_id")["reading"].agg(["mean", "std"]).round(2).to_string())
    print()

    plt.figure(figsize=(14, 5))
    for device, data in df.groupby("device_id"):
        data = data.sort_values("event_time")
        plt.plot(data["event_time"], data["reading"], linewidth=0.5, label=device)

    plt.title("Step 2: all devices - this is why the z-score is per device")
    plt.xlabel("event time")
    plt.ylabel("reading")
    plt.legend()
    plt.tight_layout()
    plt.show()


def step_3_z_scores(df):
    outliers = df[df["z_score"].abs() > Z_THRESHOLD]

    print(f"STEP 3 - z-score flags {len(outliers)} readings above the threshold of {Z_THRESHOLD}")
    print(outliers.nlargest(5, "z_score")[["device_id", "event_time", "reading", "z_score"]].to_string(index=False))
    print()

    normal = df[df["z_score"].abs() <= Z_THRESHOLD]

    plt.figure(figsize=(14, 5))
    plt.scatter(normal["event_time"], normal["z_score"], s=3, alpha=0.3, label="normal")
    plt.scatter(outliers["event_time"], outliers["z_score"], s=20, color="red", label="outlier")
    plt.axhline(Z_THRESHOLD, color="black", linestyle="--", linewidth=1)
    plt.axhline(-Z_THRESHOLD, color="black", linestyle="--", linewidth=1)

    plt.title(f"Step 3: z-score of every reading, threshold {Z_THRESHOLD}")
    plt.xlabel("event time")
    plt.ylabel("z-score")
    plt.legend()
    plt.tight_layout()
    plt.show()


def step_4_outliers_marked(df):
    device = DEVICE_TO_PLOT
    data = df[df["device_id"] == device].sort_values("event_time")
    outliers = data[data["z_score"].abs() > Z_THRESHOLD]

    print(f"STEP 4 - the same {device} chart, with the {len(outliers)} outliers marked")
    print()

    plt.figure(figsize=(14, 5))
    plt.plot(data["event_time"], data["reading"], linewidth=0.7, label="reading")
    plt.scatter(outliers["event_time"], outliers["reading"],
                color="red", s=40, zorder=3, label="outlier")
    plt.title(f"Step 4: {device} with outliers marked")
    plt.xlabel("event time")
    plt.ylabel("reading")
    plt.legend()
    plt.tight_layout()
    plt.show()


def step_5_delays(df):
    late = df[df["delay_minutes"] > LATE_AFTER_MINUTES]

    print(f"STEP 5 - {len(late)} readings arrived more than {LATE_AFTER_MINUTES} minutes after they were taken")
    print(late.nlargest(5, "delay_minutes")[["device_id", "event_time", "received_at", "delay_minutes"]].to_string(index=False))
    print()

    plt.figure(figsize=(12, 5))
    plt.hist(late["delay_minutes"], bins=40, color="orange", edgecolor="black")
    plt.title("Step 5: how late the delayed readings were")
    plt.xlabel("minutes between the reading and its arrival")
    plt.ylabel("count")
    plt.tight_layout()
    plt.show()


def main():
    df = load_data()

    step_1_raw_data(df)
    step_2_all_devices(df)
    step_3_z_scores(df)
    step_4_outliers_marked(df)
    step_5_delays(df)

    print("done")


if __name__ == "__main__":
    main()
