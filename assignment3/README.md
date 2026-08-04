# Assignment 3 - IoT Data & Anomaly Detection

Generates synthetic sensor readings, including ones that arrive late or
backdated, then finds the outliers.

## Files

```
generate_data.py     writes sensor_data.csv
detect_anomalies.py  finds outliers and late arrivals
plot_data.py         the same thing as charts, one step at a time
```

## Running

```
uv run generate_data.py
uv run detect_anomalies.py
uv run plot_data.py
```

`plot_data.py` opens one chart at a time - close each window to move on.

## The data

Five devices, 2000 readings each at 5 minute intervals, every device with its
own baseline. Three things are mixed in on purpose:

- **spikes** - readings 3 to 6 times the normal value
- **late arrivals** - a device loses connection and sends its buffered
  readings up to four hours later
- **clock drift** - a device whose clock is behind, so it reports an older
  timestamp than the reading actually has

Rows are written in the order they *arrived*, not the order they happened,
so the file is out of order the way a real feed is. Each row carries both
`event_time` and `received_at`, which is what makes the delay measurable.

The seed is fixed, so the same file comes out every run.

## Detection

Outliers are found with a z-score - how many standard deviations a reading
is from the mean - computed **per device**, not across the whole file. The
devices sit at different baselines, so a global mean would drown the quiet
sensors' anomalies inside the noisy ones' normal range.

Late arrivals and clock drift are counted together rather than separately.
With only an event time and an arrival time you cannot tell them apart -
both simply mean the reading is older than its arrival - and reporting them
as two findings made one problem look like two.

## Checking it works

The generator prints how many anomalies it injected and the detector prints
how many it found, so the two scripts check each other. 98 spikes in, 98
outliers out.
