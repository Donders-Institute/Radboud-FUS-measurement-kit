"""
Script to check drift relative to a baseline over time.

For each cluster:
1. Load the baseline (created by baseline_average.py).
2. Find all raw measurement files for that cluster.
3. Extract the measurement date from the filename (format: YYYYMMDD).
4. Compute the std of the residual (measurement - baseline) per file.
   -> This tells you how much that measurement deviates from the baseline.
5. Plot this deviation over time, so you can see whether it is
   increasing, decreasing, or fluctuating.

Note: if multiple files share the same date, their deviation values are
averaged for that date.
"""

import re
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from datetime import datetime

# ---------------- settings ----------------

input_folder = Path("data")       # folder containing all measurements (all clusters, all dates)
baseline_folder = Path("baselines\Imasonic_15287_1002_R75")   # folder containing the baseline files from baseline_average.py
dtype = np.float32                    # data type of the raw samples
output_folder = Path("drift_check")   # folder where the drift plots are written

# Cluster tags -> must appear somewhere in the filename (trailing "_" avoids elem_1 matching elem_10)
clusters = ["all_elems_"] + [f"elem_{i}_" for i in range(1, 11)]

equipment_name = "IS_PCD15287_01002_IGT-32-ch_comb_1x10-ch"

run_date = datetime.now().date().strftime("%Y-%m-%d")  # current date, no time

date_pattern = re.compile(r"(\d{4}-\d{2}-\d{2})_\d{2}-\d{2}-\d{2}")  # matches e.g. 2026-03-04_11-44-58
date_format = "%Y-%m-%d"


# --------------------------------------------


def extract_date(filename: str):
    match = date_pattern.search(filename)
    if not match:
        return None
    try:
        return datetime.strptime(match.group(1), date_format)
    except ValueError:
        return None


def check_drift(cluster_tag: str):
    # Baseline files use the same naming convention as the raw data, just in their own folder
    baseline_candidates = sorted(baseline_folder.glob(f"*{cluster_tag}*.raw"))
    if not baseline_candidates:
        print(f"  [SKIPPED] No baseline found for '{cluster_tag}' in '{baseline_folder}'")
        return
    if len(baseline_candidates) > 1:
        print(f"  [WARNING] Multiple baseline files found for '{cluster_tag}', using '{baseline_candidates[0].name}'")
    baseline_file = baseline_candidates[0]
    baseline = np.fromfile(baseline_file, dtype=dtype)

    files = sorted(input_folder.glob(f"*{cluster_tag}*.raw"))
    if not files:
        print(f"  [SKIPPED] No measurement files found for '{cluster_tag}'")
        return

    dates, devs = [], []
    for f in files:
        date = extract_date(f.name)
        if date is None:
            print(f"  [WARNING] Could not find a date in '{f.name}', skipping")
            continue

        signal = np.fromfile(f, dtype=dtype)
        if len(signal) != len(baseline):
            print(f"  [WARNING] '{f.name}' has a different length than the baseline, skipping")
            continue

        residual_std = np.std(signal - baseline)
        dates.append(date)
        devs.append(residual_std)

    if not dates:
        print(f"  [SKIPPED] No usable dated measurements for '{cluster_tag}'")
        return

    # Average deviation per date, in case of multiple files per date
    unique_dates = sorted(set(dates))
    avg_devs = [np.mean([d for dt, d in zip(dates, devs) if dt == u]) for u in unique_dates]

    print(f"{cluster_tag}: {len(unique_dates)} dates found")
    for u, d in zip(unique_dates, avg_devs):
        print(f"  - {u.date()}: std vs baseline = {d:.4g}")

    # Simple linear trend to describe the overall direction
    x = np.array([(u - unique_dates[0]).days for u in unique_dates])
    if len(x) >= 2:
        slope, intercept = np.polyfit(x, avg_devs, 1)
        rel_change = (slope * x[-1]) / avg_devs[0] if avg_devs[0] != 0 else 0
        if abs(rel_change) < 0.1:
            trend_label = "roughly stable / fluctuating"
        elif slope > 0:
            trend_label = "increasing (drifting away from baseline)"
        else:
            trend_label = "decreasing (converging towards baseline)"
    else:
        slope, trend_label = 0, "not enough dates to determine a trend"

    print(f"  -> trend: {trend_label}\n")

    # Plot
    output_folder.mkdir(parents=True, exist_ok=True)
    plt.figure(figsize=(10, 5))
    plt.plot(unique_dates, avg_devs, marker="o", color="red", label="std vs baseline")
    if len(x) >= 2:
        plt.plot(unique_dates, slope * x + intercept, linestyle="--", color="gray", label="linear trend")
    plt.title(f"{equipment_name}\nCluster '{cluster_tag}': deviation from baseline over time\nTrend: {trend_label}")
    plt.xlabel("Date")
    plt.ylabel("Std of (measurement - baseline)")
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    plot_file = output_folder / f"{run_date}_{cluster_tag}of_{equipment_name}_drift.png"
    plt.savefig(plot_file, dpi=150)
    plt.close()
    print(f"  -> drift plot saved to '{plot_file}'\n")


def main():
    for cluster_tag in clusters:
        check_drift(cluster_tag)


if __name__ == "__main__":
    main()