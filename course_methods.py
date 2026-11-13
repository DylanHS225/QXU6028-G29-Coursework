#!/usr/bin/env python3
"""Reproduce the G29 QXU6028 blind L1, L2 and L3 submission.

Run from any directory with: python3 reproduce.py
Only the group data folder and this script are inputs. The three files written
to --output are the files to upload separately to QMplus.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

KB = 8.617333e-5  # eV/K, from the Methods Guide
NA = 3.816e15  # atoms/cm^2
QE = 1.602176634e-19  # C
EMAX = 2.5  # eV
GROUP = "G29"
SEED_L2 = 20260923
SEED_L3 = 20260924
SPEC = 0.030
HERE = Path(__file__).resolve().parent


def log(message, lines):
    print(message, flush=True)
    lines.append(message)


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def file_hash(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_inputs(folder):
    manifest = read_json(folder / "manifest.json")
    if manifest.get("group") != GROUP or manifest.get("dataset_set") != "blind":
        raise ValueError("This is not the G29 blind dataset")
    for item in manifest["files"]:
        path = folder / item["name"]
        if not path.is_file() or path.stat().st_size != item["bytes"] or file_hash(path) != item["sha256"]:
            raise ValueError(f"Input differs from the teacher's manifest: {path.name}")
    template = read_json(folder / "blind_results.json")
    if template.get("group") != GROUP or template.get("dataset_set") != "blind":
        raise ValueError("Wrong blind results template")
    return template


def fermi(energy, ef, temp):
    x = np.clip((energy - ef) / (KB * temp), -60, 60)
    return 1.0 / (np.exp(x) + 1.0)


def l1(folder):
    par = read_json(folder / "L1_params.json")
    df = pd.read_csv(folder / "L1_data.csv")
    if list(df) != par["columns"] or par["group"] != GROUP:
        raise ValueError("Invalid L1 input")
    c, temp, ef = float(par["c"]), float(par["T"]), float(par["EF_op_eV"])
    rho = float(par["rho_ohm_sq"])
    if min(c, temp, rho) <= 0 or not all(map(math.isfinite, (c, temp, ef, rho))):
        raise ValueError("Invalid L1 parameters")
    e_band = np.linspace(0.0, EMAX, 20001)
    e_fermi = np.linspace(ef, EMAX, 20001)
    n_band = NA * np.trapezoid(c * e_band * fermi(e_band, ef, temp), e_band)
    n_fermi = NA * np.trapezoid(c * e_fermi * fermi(e_fermi, ef, temp), e_fermi)
    n_closed = NA * c * KB * temp * (ef * np.log(2) + np.pi**2 * KB * temp / 12)
    if not np.isclose(n_fermi, n_closed, rtol=1e-5):
        raise AssertionError("L1 numerical and closed-form Fermi counts disagree")
    return {
        "correction_factor": float(n_band / n_fermi),
        "n_fermi_op_cm2": float(n_fermi),
        "mobility_corrected_cm2_Vs": float(1.0 / (QE * n_fermi * rho)),
    }


def l2_repeats(folder):
    meta = read_json(folder / "L2_meta.json")
    df = pd.read_csv(folder / "L2_data.csv")
    expected = ["measurement_index", "repeat", "R_H_raw", "R_xx_raw"]
    if list(df) != expected or meta["columns"] != expected or meta["group"] != GROUP:
        raise ValueError("Invalid L2 input schema")
    if df.empty or not np.isfinite(df.to_numpy(dtype=float)).all():
        raise ValueError("Non-finite L2 input")
    index = df.measurement_index.drop_duplicates().to_numpy(dtype=int)
    if not np.all(np.diff(index) > 0) or df.duplicated(["measurement_index", "repeat"]).any():
        raise ValueError("Invalid L2 acquisition indices")
    ids = sorted(df.repeat.unique().tolist())
    if len(ids) != 3:
        raise ValueError("Exactly three paired L2 repeats are required")
    rows = []
    for idx in index:
        block = df.loc[df.measurement_index == idx].set_index("repeat")
        if set(block.index) != set(ids) or len(block) != 3:
            raise ValueError(f"Incomplete L2 repeats at index {idx}")
        rows.append(block.loc[ids, ["R_H_raw", "R_xx_raw"]].to_numpy(dtype=float))
    reps = np.asarray(rows)
    if np.any(reps[..., 1] <= 0):
        raise ValueError("Non-positive sheet resistance")
    return index, reps, float(meta["T_K"])


def normalise(pairs):
    scales = np.array([np.max(np.abs(pairs[:, 0])), np.max(pairs[:, 1])])
    if np.any(scales <= 0):
        raise ValueError("Zero L2 normalisation scale")
    return pairs / scales


def model_library(temp):
    # Same masked full-grid trapezoids and independent channel scaling as
    # the G29 L2 checkpoint pipeline and the Methods Guide, pp. 7-8.
    energy = np.linspace(-EMAX, EMAX, 4000)
    ef_grid = np.linspace(-8 * KB * temp, 9 * KB * temp, 400)
    gaps = np.r_[0.0, np.arange(0.50, 8.001, 0.25)]
    f = fermi(energy[None, :], ef_grid[:, None], temp)
    electrons = np.where(energy[None, :] >= ef_grid[:, None], f, 0.0)
    holes = np.where(energy[None, :] <= ef_grid[:, None], 1.0 - f, 0.0)
    curves = []
    for gap in gaps:
        dos = np.maximum(np.abs(energy) - gap * KB * temp / 2, 0.0)
        n = NA * np.trapezoid(electrons * dos, energy, axis=1)
        p = NA * np.trapezoid(holes * dos, energy, axis=1)
        total = n + p
        raw = np.column_stack(((p - n) / total**2, 1.0 / total))
        curves.append(normalise(raw))
    return ef_grid, gaps, np.asarray(curves)


def fit_l2(pairs, ef_grid, gaps, curves):
    observed = normalise(pairs)
    distance2 = ((observed[None, :, None, :] - curves[:, None, :, :])**2).sum(axis=3)
    nearest = np.argmin(distance2, axis=2)
    minima = np.take_along_axis(distance2, nearest[..., None], axis=2)[..., 0]
    rms = np.sqrt(np.mean(minima, axis=1))
    best_gap = 1 + int(np.argmin(rms[1:]))
    selected = best_gap if rms[best_gap] < 0.85 * rms[0] and gaps[best_gap] >= 1.0 else 0
    return selected, best_gap, rms, ef_grid[nearest[selected]]


def l2(folder, lines):
    index, reps, temp = l2_repeats(folder)
    log(f"L2: {len(index)} indices, three paired repeats; building 4000 x 400 model library", lines)
    ef_grid, gaps, curves = model_library(temp)
    selected, best_gap, rms, trajectory = fit_l2(reps.mean(axis=1), ef_grid, gaps, curves)
    rng = np.random.default_rng(SEED_L2)
    selected_gaps = []
    for _ in range(200):
        picks = rng.integers(0, 3, size=len(index))
        fitted = fit_l2(reps[np.arange(len(index)), picks, :], ef_grid, gaps, curves)
        selected_gaps.append(gaps[fitted[0]])
    percentiles = np.percentile(selected_gaps, [16, 50, 84])
    model = "cone" if selected == 0 else "hard_gap"
    log(f"L2: {model}; Eg/kBT={gaps[selected]:.2f}; RMS cone={rms[0]:.7f}, best gap={rms[best_gap]:.7f}; hard-gap bootstrap fraction={np.mean(np.asarray(selected_gaps)>0):.3f}", lines)
    return {
        "model": model,
        "Eg_kT": float(gaps[selected]),
        "Eg_uncertainty_kT": float((percentiles[2] - percentiles[0]) / 2),
        "EF_trajectory_eV": trajectory.tolist(),
    }, len(index)


def gradient_matrix(side=10):
    rows = []
    for i in range(side):
        for j in range(side):
            k = i * side + j
            if j < side - 1:
                row = np.zeros(side * side); row[k] = -1; row[k + 1] = 1; rows.append(row)
            if i < side - 1:
                row = np.zeros(side * side); row[k] = -1; row[k + side] = 1; rows.append(row)
    return np.asarray(rows)


def l3(folder, lines):
    meta = read_json(folder / "L3_meta.json")
    A = np.load(folder / "L3_A.npy")
    scans = np.loadtxt(folder / "L3_d.csv", delimiter=",")
    if A.shape != (128, 100) or scans.shape != (3, 128) or meta["group"] != GROUP:
        raise ValueError("Invalid L3 input shape or group")
    if not np.isfinite(A).all() or not np.isfinite(scans).all():
        raise ValueError("Non-finite L3 input")
    row_sum = np.max(np.abs(A.sum(axis=1)))
    if row_sum >= 1e-11:
        raise AssertionError("L3 constant mode is not projected out")
    L = gradient_matrix()
    one = np.ones((100, 1)) / 10
    P = np.eye(100) - one @ one.T
    eta0 = 1e-2 * np.linalg.norm(A, 2)**2 / np.linalg.norm(L, 2)**2
    # The regular G29 checkpoint documented eta=0.01*eta0 because its residual
    # was closest to the independently measured repeat-noise norm. Freeze the
    # same factor for the blind set; it is not tuned against blind results.
    eta = 0.01 * eta0
    M = P @ (A.T @ A + eta * (L.T @ L)) @ P + 1e-9 * np.eye(100)
    transfer = np.linalg.solve(M, P @ A.T)

    def reconstruct(data):
        m = transfer @ data
        return m - m.mean(axis=0)

    m = reconstruct(scans.mean(axis=0))
    sigma = scans.std(axis=0, ddof=1)
    rng = np.random.default_rng(SEED_L3)
    noise = rng.normal(0.0, sigma, size=(500, 128))
    noise_maps = reconstruct(noise.T)
    detection = float(np.percentile(np.max(np.abs(noise_maps), axis=0), 95))
    centres = np.linspace(-2.7, 2.7, 10)

    def feature(k, sign):
        row, col = divmod(int(k), 10)
        return {"sign": sign, "row": row, "column": col,
                "x_probe_pitch": float(centres[col]),
                "y_probe_pitch": float(centres[::-1][row]),
                "amplitude_fraction": float(m[k])}

    # The same point-spread test and positive-lobe second moment used in the
    # regular checkpoint. The larger central/off-centre width is reported.
    xx, yy = np.meshgrid(centres, centres[::-1])
    widths = []
    for row, col in [(5, 5), (2, 2)]:
        q = np.zeros(100); q[row * 10 + col] = 1; q -= q.mean()
        response = reconstruct(A @ q).reshape(10, 10)
        weights = np.maximum(response, 0)
        r2 = (xx - centres[col])**2 + (yy - centres[::-1][row])**2
        sigma2 = float(np.sum(weights * r2) / (2 * np.sum(weights)))
        widths.append(2.355 * math.sqrt(sigma2))
    resolution = float(max(widths))
    maximum = float(np.max(np.abs(m)))
    passed = bool(maximum <= SPEC)
    if maximum + detection < SPEC:
        confidence = "clear pass: maximum + 95% noise detection limit < 0.030"
    elif maximum - detection > SPEC:
        confidence = "clear fail: maximum - 95% noise detection limit > 0.030"
    else:
        confidence = "borderline: threshold falls within the 95% noise detection band"
    log(f"L3: eta0={eta0:.8g}, eta={eta:.8g}; max|m|={maximum:.8f}; 95% noise limit={detection:.8g}; {confidence}", lines)
    return {
        "map": m.tolist(),
        "features": [feature(np.argmax(m), "positive"), feature(np.argmin(m), "negative")],
        "resolution_probe_pitch": resolution,
        "detection_limit_fraction": detection,
        "pass": passed,
        "confidence": confidence,
    }


def git_commit():
    try:
        commit = subprocess.check_output(["git", "-C", str(HERE), "rev-parse", "HEAD"], text=True, stderr=subprocess.PIPE).strip()
        dirty = subprocess.check_output(["git", "-C", str(HERE), "status", "--porcelain"], text=True).strip()
        if dirty or len(commit) != 40:
            raise ValueError("Pipeline source has uncommitted changes")
        return commit
    except (OSError, subprocess.CalledProcessError, ValueError) as exc:
        raise RuntimeError("A clean Git commit is required for pipeline_commit.txt") from exc


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=HERE / "data" / "blind_G29")
    parser.add_argument("--output", type=Path, default=HERE.parent)
    args = parser.parse_args()
    data = args.data.expanduser().resolve()
    out = args.output.expanduser().resolve()
    lines = []
    commit = git_commit()
    template = validate_inputs(data)
    log(f"G29 blind run; UTC {datetime.now(timezone.utc).isoformat()}", lines)
    log(f"Data: {data}; teacher manifest verified; pipeline commit: {commit}", lines)
    template["pipeline_commit"] = commit
    template["L1"] = l1(data)
    log(f"L1: correction={template['L1']['correction_factor']:.8f}; n_F={template['L1']['n_fermi_op_cm2']:.8e} cm^-2; mobility={template['L1']['mobility_corrected_cm2_Vs']:.8f} cm^2/Vs", lines)
    template["L2"], n_indices = l2(data, lines)
    template["L3"] = l3(data, lines)
    if len(template["L2"]["EF_trajectory_eV"]) != n_indices:
        raise AssertionError("Wrong L2 trajectory length")
    if len(template["L3"]["map"]) != 100 or not np.isfinite(template["L3"]["map"]).all():
        raise AssertionError("L3 map must contain exactly 100 finite numbers")
    if abs(sum(template["L3"]["map"])) > 1e-10:
        raise AssertionError("L3 map has a nonzero mean")
    payload = json.dumps(template, indent=2, ensure_ascii=False, allow_nan=False) + "\n"
    out.mkdir(parents=True, exist_ok=True)
    (out / "blind_results.json").write_text(payload, encoding="utf-8")
    (out / "pipeline_commit.txt").write_text(commit + "\n", encoding="utf-8")
    log("Validation passed: schema, index count, 100 finite zero-mean map values", lines)
    log(f"Created three submission files in {out}", lines)
    (out / "run_log.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise
