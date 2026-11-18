"""Thực nghiệm K-Means của Thành trên tập PCA do Ly bàn giao.

Chạy từ thư mục gốc: python src/run_kmeans.py
Không lấy mẫu lại, chuẩn hóa lại hoặc fit PCA lại.
"""

from __future__ import annotations

import hashlib
import json
import platform
from pathlib import Path
from time import perf_counter

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import sklearn
from sklearn.cluster import KMeans
from sklearn.metrics import (
    adjusted_rand_score,
    calinski_harabasz_score,
    davies_bouldin_score,
    normalized_mutual_info_score,
    pairwise_distances,
    silhouette_samples,
    silhouette_score,
)
from threadpoolctl import threadpool_limits

ROOT = Path(__file__).resolve().parents[1]
MODEL_PARAMS = dict(
    init="k-means++", n_init=20, max_iter=300, tol=1e-4,
    random_state=42, algorithm="lloyd",
)


def load_inputs(root=ROOT):
    """Chỉ cho phép PC1..PC104; kiểm tra ghép dòng và nhãn tham chiếu."""
    root = Path(root)
    config = json.loads((root / "results/preprocessing_config.json").read_text())
    data_path = root / config["sample_files"]["sampled_pca_data"]
    indices_path = root / config["sample_files"]["indices_file"]
    data = pd.read_csv(data_path)
    indices = pd.read_csv(indices_path)
    columns = [f"PC{i}" for i in range(1, config["pca_components"] + 1)]
    if len(data) != config["sample_size"] or len(indices) != len(data):
        raise ValueError("Số mẫu không khớp cấu hình bàn giao.")
    if not set(columns).issubset(data.columns):
        raise ValueError("Thiếu cột PCA trong dữ liệu.")
    for col in ["Original_Index", "Subject", "Activity", "ActivityName"]:
        if not data[col].equals(indices[col]):
            raise ValueError(f"Sai thứ tự dòng hoặc thông tin tham chiếu: {col}")
    if not np.array_equal(indices["Sample_Index"], np.arange(len(data))):
        raise ValueError("Sample_Index phải liên tiếp từ 0 và giữ nguyên thứ tự.")
    if data["Original_Index"].duplicated().any():
        raise ValueError("Chỉ số dòng gốc bị lặp.")
    raw_dir = root / "data/raw/UCI HAR Dataset"
    y_all = np.concatenate([
        np.loadtxt(raw_dir / "train/y_train.txt", dtype=int),
        np.loadtxt(raw_dir / "test/y_test.txt", dtype=int),
    ])
    raw_indices = data["Original_Index"].to_numpy()
    if not np.issubdtype(raw_indices.dtype, np.integer):
        raise ValueError("Original_Index phải là số nguyên.")
    if ((raw_indices < 0) | (raw_indices >= len(y_all))).any():
        raise ValueError("Original_Index nằm ngoài dữ liệu gốc.")
    if not np.array_equal(y_all[raw_indices], data["Activity"].to_numpy()):
        raise ValueError("Nhãn tham chiếu không khớp nhãn UCI HAR gốc.")
    X = data.loc[:, columns].to_numpy(dtype=np.float64)
    if not np.isfinite(X).all():
        raise ValueError("Dữ liệu PCA chứa NaN hoặc vô cực.")
    return data, indices, X, config, data_path, indices_path


def select_k(results):
    """Chọn K bằng Silhouette cao nhất; nếu bằng nhau ưu tiên K nhỏ hơn."""
    return int(results.sort_values(["Silhouette", "K"], ascending=[False, True]).iloc[0]["K"])


def save_figure(fig, path):
    fig.tight_layout()
    fig.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(fig)


def run_experiment(root=ROOT):
    root = Path(root)
    data, indices, X, preprocessing, data_path, indices_path = load_inputs(root)
    output = root / "results/kmeans"
    output.mkdir(parents=True, exist_ok=True)
    models, rows, labels_by_k = {}, [], {}
    # Khoảng cách được tính trên đủ 104 chiều; không đánh giá trên hình chiếu 2D.
    with threadpool_limits(limits=1):
        distances = pairwise_distances(X, metric="euclidean")
        np.fill_diagonal(distances, 0.0)
        for k in range(2, 11):
            model = KMeans(n_clusters=k, **MODEL_PARAMS)
            start = perf_counter()
            labels = model.fit_predict(X)
            seconds = perf_counter() - start
            if len(np.unique(labels)) != k or model.n_iter_ >= MODEL_PARAMS["max_iter"]:
                raise RuntimeError(f"K={k}: thiếu cụm hoặc chạm giới hạn vòng lặp; cần kiểm tra hội tụ.")
            models[k] = model
            labels_by_k[k] = labels
            rows.append(dict(
                K=k, Inertia=float(model.inertia_),
                Silhouette=float(silhouette_score(distances, labels, metric="precomputed")),
                Davies_Bouldin=float(davies_bouldin_score(X, labels)),
                Calinski_Harabasz=float(calinski_harabasz_score(X, labels)),
                Fit_seconds=seconds, Iterations=int(model.n_iter_),
                Min_cluster_size=int(np.bincount(labels).min()),
                Max_cluster_size=int(np.bincount(labels).max()),
            ))
            print(f"K={k}: Silhouette={rows[-1]['Silhouette']:.6f}, inertia={model.inertia_:.2f}", flush=True)

        results = pd.DataFrame(rows)
        selected_k = select_k(results)
        # Chỉ sau khi chốt K mới sử dụng nhãn tham chiếu để đánh giá ngoài.
        y = data["Activity"].to_numpy()
        results["ARI"] = [adjusted_rand_score(y, labels_by_k[k]) for k in results["K"]]
        results["NMI"] = [normalized_mutual_info_score(y, labels_by_k[k], average_method="arithmetic") for k in results["K"]]
        labels = labels_by_k[selected_k]
        point_silhouettes = silhouette_samples(distances, labels, metric="precomputed")

    results.to_csv(output / "k_sweep.csv", index=False)
    selected = results.loc[results["K"] == selected_k].iloc[0]
    selected.to_frame("Value").rename_axis("Metric").to_csv(output / "final_metrics.csv")
    predictions = indices.copy()
    predictions["Cluster"] = labels
    predictions["Silhouette"] = point_silhouettes
    predictions.to_csv(output / "cluster_labels.csv", index=False)
    all_labels = indices[["Sample_Index", "Original_Index"]].copy()
    for k, cluster_labels in labels_by_k.items():
        all_labels[f"Cluster_K{k}"] = cluster_labels
    all_labels.to_csv(output / "labels_all_k.csv", index=False)
    pd.DataFrame(models[selected_k].cluster_centers_, columns=[f"PC{i+1}" for i in range(X.shape[1])]).rename_axis("Cluster").to_csv(output / "cluster_centers.csv")
    sizes = predictions.groupby("Cluster").size().rename("Samples").to_frame()
    sizes["Percent"] = sizes["Samples"] / len(data) * 100
    sizes.to_csv(output / "cluster_sizes.csv")
    for k in sorted({selected_k, 6}):
        table = pd.crosstab(pd.Series(labels_by_k[k], name="Cluster"), data["ActivityName"])
        table.to_csv(output / f"activity_crosstab_k{k}.csv")
        table.div(table.sum(axis=1), axis=0).mul(100).to_csv(output / f"activity_percent_k{k}.csv")

    # Gợi ý Elbow hình học minh bạch: độ lệch cực đại so với dây nối hai đầu.
    xs = (results["K"].to_numpy() - 2) / 8
    ys = (results["Inertia"].to_numpy() - results["Inertia"].iloc[-1]) / (results["Inertia"].iloc[0] - results["Inertia"].iloc[-1])
    elbow_k = int(results.iloc[int(np.argmax((1 - xs) - ys))]["K"])
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10})
    for metric, title, name in [
        ("Inertia", "Elbow trên tập cố định 3.000 mẫu × 104 PC", "fig_5_1_elbow.png"),
        ("Silhouette", "Silhouette theo số cụm K", "fig_5_2_silhouette.png"),
    ]:
        fig, ax = plt.subplots(figsize=(8, 4.5))
        ax.plot(results["K"], results[metric], "o-", color="#2563a6")
        ax.axvline(selected_k, color="#b34436", linestyle="--", label=f"K chọn theo Silhouette = {selected_k}")
        if metric == "Inertia":
            ax.axvline(elbow_k, color="#32804a", linestyle=":", label=f"Gợi ý Elbow hình học = {elbow_k}")
        ax.set(xlabel="Số cụm K", ylabel=metric, title=title, xticks=range(2, 11))
        ax.grid(alpha=.2)
        ax.legend()
        save_figure(fig, output / name)

    fig, axes = plt.subplots(1, 2, figsize=(12, 4.5), sharex=True, sharey=True)
    for cluster in range(selected_k):
        mask = labels == cluster
        axes[0].scatter(X[mask, 0], X[mask, 1], s=8, alpha=.5, label=f"Cụm {cluster}")
    for activity in sorted(data["ActivityName"].unique()):
        mask = data["ActivityName"].to_numpy() == activity
        axes[1].scatter(X[mask, 0], X[mask, 1], s=8, alpha=.5, label=activity)
    for ax, title in zip(axes, [f"K-Means K={selected_k}", "Nhãn hoạt động tham chiếu"]):
        ax.set(title=title, xlabel="PC1", ylabel="PC2")
        ax.legend(fontsize=7, loc="best")
        ax.grid(alpha=.15)
    fig.suptitle("Chỉ chiếu lên PC1–PC2 để vẽ; mô hình chạy trên đủ 104 PC")
    save_figure(fig, output / "fig_5_3_clusters_pca2d.png")

    table = pd.read_csv(output / f"activity_crosstab_k{selected_k}.csv", index_col=0)
    fig, ax = plt.subplots(figsize=(9, max(3.5, selected_k * .65 + 2)))
    ax.imshow(table.to_numpy(), cmap="Blues", aspect="auto")
    ax.set(xticks=range(len(table.columns)), xticklabels=table.columns, yticks=range(len(table)), yticklabels=[f"Cụm {i}" for i in table.index], title="Số mẫu từng hoạt động trong mỗi cụm")
    plt.setp(ax.get_xticklabels(), rotation=25, ha="right", fontsize=8)
    for i in range(len(table)):
        for j in range(len(table.columns)):
            v = int(table.iloc[i, j])
            ax.text(j, i, str(v), ha="center", va="center", color="white" if v > table.to_numpy().max() * .55 else "black")
    save_figure(fig, output / "activity_heatmap.png")

    fig, ax = plt.subplots(figsize=(7, 4))
    ax.bar(sizes.index.astype(str), sizes["Samples"], color="#2563a6")
    ax.set(xlabel="Cụm", ylabel="Số mẫu", title=f"Quy mô các cụm với K={selected_k}")
    save_figure(fig, output / "cluster_sizes.png")

    manifest = {
        "selected_k": selected_k, "elbow_geometric_candidate": elbow_k,
        "selection_rule": "maximum full-sample Euclidean Silhouette over K=2..10; tie -> smaller K; no reference labels",
        "elbow_rule": "maximum (1-x)-y after min-max scaling K and inertia; heuristic only",
        "model_parameters": MODEL_PARAMS, "input_shape": list(X.shape),
        "feature_columns": [f"PC{i+1}" for i in range(X.shape[1])],
        "excluded_columns": ["Activity", "ActivityName", "Subject", "Original_Index"],
        "inputs": {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest() for p in [data_path, indices_path, root / "results/preprocessing_config.json"]},
        "preprocessing": preprocessing,
        "versions": {"python": platform.python_version(), "numpy": np.__version__, "pandas": pd.__version__, "scikit-learn": sklearn.__version__, "matplotlib": matplotlib.__version__},
        "execution": {"threads": 1, "silhouette_samples": len(X), "distance": "euclidean", "fit_time_excludes_metrics_and_io": True},
        "negative_silhouette_percent": float(np.mean(point_silhouettes < 0) * 100),
        "reference_k6_role": "supplementary only; six known activities do not force six clusters",
    }
    (output / "experiment_config.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Chọn K={selected_k}; gợi ý Elbow={elbow_k}. K=6 chỉ là thực nghiệm bổ sung.")
    return results, predictions, manifest


if __name__ == "__main__":
    run_experiment()
