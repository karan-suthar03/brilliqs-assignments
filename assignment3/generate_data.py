"""Generate fake IoT sensor readings and write them to a CSV."""

import csv
import random
from datetime import datetime, timedelta

DEVICES = ["sensor-01", "sensor-02", "sensor-03", "sensor-04", "sensor-05"]
READINGS_PER_DEVICE = 2000
START_TIME = datetime(2026, 7, 1, 0, 0, 0)
INTERVAL = timedelta(minutes=5)
OUTPUT_FILE = "sensor_data.csv"

SPIKE_CHANCE = 0.01
LATE_CHANCE = 0.02
DRIFT_CHANCE = 0.01


def main():
    random.seed(42)
    rows = []
    spikes = 0
    late_arrivals = 0
    drifted_clocks = 0

    for device in DEVICES:
        baseline = random.uniform(20, 30)
        event_time = START_TIME

        for _ in range(READINGS_PER_DEVICE):
            event_time = event_time + INTERVAL
            reading = round(random.gauss(baseline, 1.5), 2)

            reported_time = event_time
            received_at = event_time + timedelta(seconds=random.randint(1, 20))

            if random.random() < SPIKE_CHANCE:
                reading = round(reading * random.uniform(3, 6), 2)
                spikes += 1

            # device lost connection and sent its buffered readings later
            if random.random() < LATE_CHANCE:
                received_at = event_time + timedelta(minutes=random.randint(30, 240))
                late_arrivals += 1

            # device clock is running behind, so it reports an older timestamp
            if random.random() < DRIFT_CHANCE:
                reported_time = event_time - timedelta(minutes=random.randint(10, 90))
                drifted_clocks += 1

            rows.append([device, reported_time, received_at, reading])

    # the pipeline sees rows in the order they arrived, not the order they happened
    rows.sort(key=lambda row: row[2])

    with open(OUTPUT_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["device_id", "event_time", "received_at", "reading"])
        for device, event_time, received_at, reading in rows:
            writer.writerow([device, event_time.isoformat(), received_at.isoformat(), reading])

    print(f"wrote {OUTPUT_FILE} with {len(rows)} rows")
    print(f"  {len(DEVICES)} devices, {READINGS_PER_DEVICE} readings each")
    print(f"  {spikes} spikes")
    print(f"  {late_arrivals} late arrivals")
    print(f"  {drifted_clocks} backdated by clock drift")

    print()
    print(f"{'device':<12}{'event_time':<22}{'received_at':<22}{'reading':>8}")
    for device, reported_time, received_at, reading in rows[:10]:
        print(f"{device:<12}{reported_time.isoformat():<22}"
              f"{received_at.isoformat():<22}{reading:>8.2f}")


if __name__ == "__main__":
    main()
