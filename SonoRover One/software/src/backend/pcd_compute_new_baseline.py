"""
Script to create a baseline for multiple clusters from raw measurements.

All files live in a single folder. The cluster is identified by a tag that
appears somewhere in the middle of the filename, e.g.:
    something_elem_1_something.raw
    something_all_elems_something.raw

For each cluster this script:
1. Collects all raw files belonging to that cluster.
2. Reads the files.
3. Computes the average signal.
4. Writes the result to a new raw file.
5. Saves a PNG with all individual signals overlaid plus the average,
   so the result can be visually verified.
6. Saves a separate PNG with just the average signal.
"""

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from datetime import date

# ---------------- settings ----------------

input_folder = Path("data")     # folder containing all measurements (all clusters together)
dtype = np.float32                  # data type of the raw samples (e.g. np.float32, np.int16, np.float64)
output_folder = Path("baseline")   # folder where the resulting baselines (+ plots) are written

# Cluster tags -> must appear somewhere in the filename
clusters = ["all_elems_"] + [f"elem_{i}_" for i in range(1, 11)]

equipment_name = "IS_PCD15287_01002_IGT-32-ch_comb_1x10-ch"

run_date = date.today().strftime("%Y-%m-%d")  # current date, no time
# --------------------------------------------


def compute_baseline(cluster_tag: str):
    # 1. Collect files belonging to this cluster
    files = sorted(input_folder.glob(f"*{cluster_tag}*.raw"))
    if not files:
        print(f"  [SKIPPED] No files found for '{cluster_tag}'")
        return

    print(f"{cluster_tag}: {len(files)} files found for averaging:")
    for f in files:
        print(f"  - {f.name}")

    # 2. Read files
    signals = [np.fromfile(f, dtype=dtype) for f in files]

    # Check that all signals have the same length
    lengths = {len(s) for s in signals}
    if len(lengths) > 1:
        detail = ", ".join(f"{f.name}: {len(s)} samples" for f, s in zip(files, signals))
        raise ValueError(f"Not all signals in '{cluster_tag}' have the same length!\n{detail}")

    # 3. Compute average and spread
    baseline = np.mean(signals, axis=0).astype(dtype)
    std_signal = np.std(signals, axis=0)

    # 4. Write to raw file
    output_folder.mkdir(parents=True, exist_ok=True)
    base_name = f"{run_date}_{cluster_tag}of_{equipment_name}"
    output_file = output_folder / f"{base_name}_baseline.raw"
    baseline.tofile(output_file)
    print(f"  -> written to '{output_file}' ({len(baseline)} samples, dtype={dtype.__name__})")

    # Quantitative verification: how far does each signal deviate from the baseline?
    max_devs = [np.max(np.abs(s - baseline)) for s in signals]
    mean_devs = [np.mean(np.abs(s - baseline)) for s in signals]
    print(f"  Deviation from baseline (per file):")
    for f, max_d, mean_d in zip(files, max_devs, mean_devs):
        print(f"    - {f.name}: max={max_d:.4g}, mean={mean_d:.4g}")
    print(f"  Overall: worst max deviation = {max(max_devs):.4g}")

    # Shared y-limits for overlay and average plot (based on data range incl. std band)
    all_values = np.concatenate(signals + [baseline + std_signal, baseline - std_signal])
    margin = 0.05 * (all_values.max() - all_values.min())
    ylim = (all_values.min() - margin, all_values.max() + margin)

    # Summary std metrics to display on the plots
    mean_std = np.mean(std_signal)
    max_std = np.max(std_signal)

    # 5. Save overlay plot for visual verification
    plt.figure(figsize=(10, 5))
    for f, s in zip(files, signals):
        plt.plot(s, color="gray", alpha=0.4, linewidth=0.8, label=f.name)
    plt.fill_between(
        np.arange(len(baseline)), baseline - std_signal, baseline + std_signal,
        color="red", alpha=0.15, label="±1 std"
    )
    plt.plot(baseline, color="red", linewidth=2, label="average")
    plt.title(
        f"{equipment_name}\n'{cluster_tag}': individual signals + average\n"
        f"mean std = {mean_std:.4g}, max std = {max_std:.4g}"
    )
    plt.xlabel("Sample")
    plt.ylabel("Amplitude")
    plt.ylim(ylim)
    plt.tight_layout()
    overlay_file = output_folder / f"{base_name}_overlay.png"
    plt.savefig(overlay_file, dpi=150)
    plt.close()
    print(f"  -> overlay plot saved to '{overlay_file}'")

    # 6. Save a separate plot with just the average signal (same y-limits as overlay)
    plt.figure(figsize=(10, 5))
    plt.plot(baseline, color="red", linewidth=1.5)
    plt.title(
        f"{equipment_name}\n'{cluster_tag}': average signal\n"
        f"mean std = {mean_std:.4g}, max std = {max_std:.4g}"
    )
    plt.xlabel("Sample")
    plt.ylabel("Amplitude")
    plt.ylim(ylim)
    plt.tight_layout()
    average_file = output_folder / f"{base_name}_average.png"
    plt.savefig(average_file, dpi=150)
    plt.close()
    print(f"  -> average plot saved to '{average_file}'\n")


def main():
    for cluster_tag in clusters:
        compute_baseline(cluster_tag)


if __name__ == "__main__":
    main()