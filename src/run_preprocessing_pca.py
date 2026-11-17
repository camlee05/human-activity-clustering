"""
Module tiền xử lý dữ liệu, khảo sát PCA, và lấy mẫu phân tầng 3.000 dòng
cho đề tài phân nhóm hoạt động con người (UCI HAR).
"""

import os
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.model_selection import train_test_split

# Thiết lập đường dẫn
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_RAW = os.path.join(BASE_DIR, "data", "raw", "UCI HAR Dataset")
DATA_PROCESSED = os.path.join(BASE_DIR, "data", "processed")
RESULTS_DIR = os.path.join(BASE_DIR, "results")
FIGURES_DIR = os.path.join(RESULTS_DIR, "figures")

os.makedirs(DATA_PROCESSED, exist_ok=True)
os.makedirs(FIGURES_DIR, exist_ok=True)

# 1. Đọc dữ liệu
print("1. Đang nạp dữ liệu từ UCI HAR Dataset...")
features_df = pd.read_csv(
    os.path.join(DATA_RAW, "features.txt"),
    sep=r"\s+",
    header=None,
    names=["Index", "Feature"]
)
feature_names = features_df["Feature"].tolist()

activity_labels_df = pd.read_csv(
    os.path.join(DATA_RAW, "activity_labels.txt"),
    sep=r"\s+",
    header=None,
    names=["Activity", "ActivityName"]
)
activity_dict = dict(zip(activity_labels_df["Activity"], activity_labels_df["ActivityName"]))

# Train data
X_train = pd.read_csv(os.path.join(DATA_RAW, "train", "X_train.txt"), sep=r"\s+", header=None)
X_train.columns = feature_names
y_train = pd.read_csv(os.path.join(DATA_RAW, "train", "y_train.txt"), header=None, names=["Activity"])
subject_train = pd.read_csv(os.path.join(DATA_RAW, "train", "subject_train.txt"), header=None, names=["Subject"])
train_data = pd.concat([subject_train, y_train, X_train], axis=1)

# Test data
X_test = pd.read_csv(os.path.join(DATA_RAW, "test", "X_test.txt"), sep=r"\s+", header=None)
X_test.columns = feature_names
y_test = pd.read_csv(os.path.join(DATA_RAW, "test", "y_test.txt"), header=None, names=["Activity"])
subject_test = pd.read_csv(os.path.join(DATA_RAW, "test", "subject_test.txt"), header=None, names=["Subject"])
test_data = pd.concat([subject_test, y_test, X_test], axis=1)

# Ghép toàn bộ
all_data = pd.concat([train_data, test_data], ignore_index=True)
all_data["ActivityName"] = all_data["Activity"].map(activity_dict)
print(f"Tổng số mẫu toàn bộ: {len(all_data)} (Train: {len(train_data)}, Test: {len(test_data)})")

# 2. Phân tách đặc trưng X và nhãn y
print("\n2. Tách bộ đặc trưng X và nhãn y...")
# Lưu ý: features.txt có một số tên bị trùng lặp (ví dụ các bandsEnergy), vì vậy dùng drop columns để giữ đúng 561 cột gốc
X = all_data.drop(columns=["Subject", "Activity", "ActivityName"]).copy()
y = all_data["Activity"].copy()
y_name = all_data["ActivityName"].copy()
subjects = all_data["Subject"].copy()
print(f"Shape của X: {X.shape}, Shape của y: {y.shape}")

# Kiểm tra thiếu và bất thường
nan_count = X.isnull().sum().sum()
dup_count = X.duplicated().sum()
print(f"Giá trị thiếu trong X: {nan_count}, Dòng trùng lặp trong X: {dup_count}")

# 3. Chuẩn hóa dữ liệu với StandardScaler
print("\n3. Chuẩn hóa dữ liệu bằng StandardScaler...")
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X.values)

# So sánh trước và sau chuẩn hóa trên 5 đặc trưng tiêu biểu cho Bảng 4.1
sample_features = [
    "tBodyAcc-mean()-X",
    "tBodyAcc-mean()-Y",
    "tBodyAcc-mean()-Z",
    "tBodyAcc-std()-X",
    "tBodyAcc-std()-Y"
]
compare_rows = []
for feat in sample_features:
    idx = feature_names.index(feat)
    raw_col = X[feat].values
    scaled_col = X_scaled[:, idx]
    compare_rows.append({
        "Đặc trưng": feat,
        "Mean (Gốc)": round(float(np.mean(raw_col)), 4),
        "Std (Gốc)": round(float(np.std(raw_col)), 4),
        "Min (Gốc)": round(float(np.min(raw_col)), 4),
        "Max (Gốc)": round(float(np.max(raw_col)), 4),
        "Mean (Chuẩn hóa)": round(float(np.mean(scaled_col)), 4),
        "Std (Chuẩn hóa)": round(float(np.std(scaled_col)), 4),
        "Min (Chuẩn hóa)": round(float(np.min(scaled_col)), 4),
        "Max (Chuẩn hóa)": round(float(np.max(scaled_col)), 4),
    })
compare_df = pd.DataFrame(compare_rows)
compare_df.to_csv(os.path.join(RESULTS_DIR, "table_4_1_scaling_comparison.csv"), index=False)
print("Đã lưu Bảng 4.1 so sánh trước và sau chuẩn hóa.")

# 4. Thực hiện PCA toàn diện
print("\n4. Phân tích thành phần chính PCA...")
pca_full = PCA(random_state=42)
pca_full.fit(X_scaled)

explained_variance = pca_full.explained_variance_ratio_
cumulative_variance = np.cumsum(explained_variance)

# Tìm các mốc phương sai chính
milestones = [0.50, 0.60, 0.70, 0.80, 0.90, 0.95, 0.99]
milestone_rows = []
for m in milestones:
    n_comp = int(np.argmax(cumulative_variance >= m) + 1)
    milestone_rows.append({
        "Mức phương sai mục tiêu (%)": int(m * 100),
        "Số thành phần chính (PCs)": n_comp,
        "Phương sai tích lũy thực tế (%)": round(float(cumulative_variance[n_comp - 1]) * 100, 2)
    })
milestone_df = pd.DataFrame(milestone_rows)
milestone_df.to_csv(os.path.join(RESULTS_DIR, "explained_variance_milestones.csv"), index=False)
print("Bảng mốc phương sai tích lũy:")
print(milestone_df.to_string(index=False))

# Số PC tối ưu để đạt >= 95%
n_components_95 = int(np.argmax(cumulative_variance >= 0.95) + 1)
print(f"\nSố thành phần chính cần thiết để giữ >= 95% phương sai: {n_components_95}")

# Xuất bảng tổng hợp phương sai giải thích explained_variance_summary.csv
summary_rows = []
milestone_pcs = {
    1: "Mốc đạt >= 50% phương sai",
    4: "Mốc đạt >= 60% phương sai",
    10: "Mốc đạt >= 70% phương sai",
    27: "Mốc đạt >= 80% phương sai",
    65: "Mốc đạt >= 90% phương sai",
    n_components_95: "NGƯỠNG LỰA CHỌN TỐI ƯU (>= 95% phương sai)",
    int(np.argmax(cumulative_variance >= 0.99) + 1): "Mốc đạt >= 99% phương sai"
}

# Top 20 PC đầu tiên và các PC mốc
key_pcs = sorted(list(set(list(range(1, 21)) + list(milestone_pcs.keys()))))
for pc_num in key_pcs:
    idx = pc_num - 1
    summary_rows.append({
        "Thành phần chính": f"PC{pc_num}",
        "Phương sai giải thích (%)": round(float(explained_variance[idx]) * 100, 3),
        "Phương sai tích lũy (%)": round(float(cumulative_variance[idx]) * 100, 3),
        "Ghi chú / Mốc quan trọng": milestone_pcs.get(pc_num, "")
    })

summary_df = pd.DataFrame(summary_rows)
summary_df.to_csv(os.path.join(RESULTS_DIR, "explained_variance_summary.csv"), index=False)
summary_df.to_csv(os.path.join(RESULTS_DIR, "table_4_2_top20_pca_variance.csv"), index=False)
print("Đã lưu bảng explained_variance_summary.csv.")

# Số PC tối ưu để đạt >= 95%
n_components_95 = int(np.argmax(cumulative_variance >= 0.95) + 1)
print(f"\nSố thành phần chính cần thiết để giữ >= 95% phương sai: {n_components_95}")

# 5. Vẽ đồ thị PCA
print("\n5. Vẽ các biểu đồ phục vụ Báo cáo...")
# Hình 4.1: Biểu đồ Explained Variance Ratio của 20 PC đầu
plt.figure(figsize=(10, 5))
bars = plt.bar(range(1, 21), explained_variance[:20] * 100, color="steelblue", edgecolor="black", alpha=0.85)
plt.xlabel("Thành phần chính (Principal Component)")
plt.ylabel("Tỷ lệ phương sai giải thích (%)")
plt.title("Hình 4.1: Tỷ lệ phương sai giải thích của 20 thành phần chính đầu tiên")
plt.xticks(range(1, 21))
plt.grid(axis="y", linestyle="--", alpha=0.7)
plt.tight_layout()
plt.savefig(os.path.join(FIGURES_DIR, "fig_4_1_variance_ratio.png"), dpi=300)
plt.savefig(os.path.join(FIGURES_DIR, "Hinh_4_1_variance_ratio.png"), dpi=300)
plt.close()

# Hình 4.2: Biểu đồ Cumulative Explained Variance
plt.figure(figsize=(10, 5))
plt.plot(range(1, len(cumulative_variance) + 1), cumulative_variance * 100, color="darkorange", linewidth=2)
plt.axhline(y=95, color="red", linestyle="--", label="Ngưỡng 95% phương sai")
plt.axvline(x=n_components_95, color="green", linestyle="--", label=f"PC {n_components_95} (95.05%)")
plt.scatter([n_components_95], [cumulative_variance[n_components_95 - 1] * 100], color="red", s=50, zorder=5)
plt.xlabel("Số lượng thành phần chính")
plt.ylabel("Phương sai tích lũy giải thích (%)")
plt.title("Hình 4.2: Phương sai tích lũy theo số lượng thành phần chính PCA")
plt.legend(loc="lower right")
plt.grid(True, linestyle="--", alpha=0.7)
plt.tight_layout()
plt.savefig(os.path.join(FIGURES_DIR, "fig_4_2_cumulative_variance.png"), dpi=300)
plt.savefig(os.path.join(FIGURES_DIR, "Hinh_4_2_cumulative_variance.png"), dpi=300)
plt.close()

# Hình 4.3: Trực quan hóa PCA 2D
pca_2d = PCA(n_components=2, random_state=42)
X_pca_2d = pca_2d.fit_transform(X_scaled)

plt.figure(figsize=(10, 7))
colors = ["#e41a1c", "#377eb8", "#4daf4a", "#984ea3", "#ff7f00", "#ffff33"]
for act_idx, act_name in enumerate(activity_labels_df["ActivityName"]):
    mask = (all_data["ActivityName"] == act_name)
    plt.scatter(
        X_pca_2d[mask, 0],
        X_pca_2d[mask, 1],
        label=act_name,
        alpha=0.6,
        s=15,
        edgecolors="none"
    )
plt.xlabel(f"PC1 ({pca_2d.explained_variance_ratio_[0]*100:.2f}% phương sai)")
plt.ylabel(f"PC2 ({pca_2d.explained_variance_ratio_[1]*100:.2f}% phương sai)")
plt.title("Hình 4.3: Phân bố dữ liệu trên 2 thành phần chính (PCA 2D)")
plt.legend(title="Hoạt động", bbox_to_anchor=(1.02, 1), loc="upper left")
plt.grid(True, linestyle="--", alpha=0.5)
plt.tight_layout()
plt.savefig(os.path.join(FIGURES_DIR, "fig_4_3_pca_2d.png"), dpi=300)
plt.savefig(os.path.join(FIGURES_DIR, "Hinh_4_3_pca_2d.png"), dpi=300)
plt.close()

# Hình 3.3 chuẩn hóa: Phân bố 6 hoạt động trên toàn bộ 10.299 mẫu
activity_counts = all_data["ActivityName"].value_counts()[activity_labels_df["ActivityName"]]
plt.figure(figsize=(9, 5))
bars = plt.bar(activity_counts.index, activity_counts.values, color="cornflowerblue", edgecolor="black")
for bar in bars:
    yval = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2.0, yval + 20, f"{int(yval)}", ha="center", va="bottom", fontsize=9)
plt.title("Hình 3.3: Phân phối số lượng mẫu của 6 hoạt động (Tổng số: 10.299 mẫu)")
plt.xlabel("Hoạt động")
plt.ylabel("Số lượng mẫu")
plt.xticks(rotation=25, ha="right")
plt.ylim(0, max(activity_counts.values) + 200)
plt.grid(axis="y", linestyle="--", alpha=0.7)
plt.tight_layout()
plt.savefig(os.path.join(FIGURES_DIR, "fig_3_3_activity_distribution_all.png"), dpi=300)
plt.close()

# 6. Chọn và cố định tập dữ liệu mẫu 3.000 dòng bằng Stratified Sampling
print("\n6. Thực hiện lấy mẫu phân tầng 3.000 dòng (Stratified Sampling, random_state=42)...")
SAMPLE_SIZE = 3000
RANDOM_STATE = 42

indices = np.arange(len(all_data))
sample_indices, _ = train_test_split(
    indices,
    train_size=SAMPLE_SIZE,
    stratify=y,
    random_state=RANDOM_STATE
)
sample_indices = np.sort(sample_indices)

sampled_data = all_data.iloc[sample_indices].copy()
sampled_data["Original_Index"] = sample_indices

# Thống kê phân bố trong tập mẫu 3.000 dòng
sample_act_counts = sampled_data["ActivityName"].value_counts()
dist_comparison = pd.DataFrame({
    "Hoạt động": activity_labels_df["ActivityName"],
    "Số mẫu gốc (N=10.299)": [all_data[all_data["ActivityName"] == name].shape[0] for name in activity_labels_df["ActivityName"]],
    "Tỷ lệ gốc (%)": [round(all_data[all_data["ActivityName"] == name].shape[0] / len(all_data) * 100, 2) for name in activity_labels_df["ActivityName"]],
    "Số mẫu tập mẫu (N=3.000)": [sampled_data[sampled_data["ActivityName"] == name].shape[0] for name in activity_labels_df["ActivityName"]],
    "Tỷ lệ tập mẫu (%)": [round(sampled_data[sampled_data["ActivityName"] == name].shape[0] / SAMPLE_SIZE * 100, 2) for name in activity_labels_df["ActivityName"]]
})
dist_comparison.to_csv(os.path.join(RESULTS_DIR, "table_4_3_sample_distribution.csv"), index=False)
print("Bảng so sánh phân bố hoạt động tập gốc vs tập mẫu 3.000 dòng:")
print(dist_comparison.to_string(index=False))

# 7. Xuất các file dữ liệu đã xử lý
print("\n7. Xuất file chỉ số dòng và dữ liệu mẫu...")
# File chỉ số mẫu
sample_indices_df = pd.DataFrame({
    "Sample_Index": np.arange(SAMPLE_SIZE),
    "Original_Index": sample_indices,
    "Subject": sampled_data["Subject"].values,
    "Activity": sampled_data["Activity"].values,
    "ActivityName": sampled_data["ActivityName"].values
})
sample_indices_df.to_csv(os.path.join(DATA_PROCESSED, "sample_indices.csv"), index=False)

# File dữ liệu 3.000 mẫu sau chuẩn hóa và PCA 104 components
pca_final = PCA(n_components=n_components_95, random_state=RANDOM_STATE)
X_scaled_pca_all = pca_final.fit_transform(X_scaled)
X_sampled_pca = X_scaled_pca_all[sample_indices]

pca_cols = [f"PC{i+1}" for i in range(n_components_95)]
sampled_pca_df = pd.DataFrame(X_sampled_pca, columns=pca_cols)
sampled_pca_df["Activity"] = sampled_data["Activity"].values
sampled_pca_df["ActivityName"] = sampled_data["ActivityName"].values
sampled_pca_df["Subject"] = sampled_data["Subject"].values
sampled_pca_df["Original_Index"] = sample_indices

sampled_pca_df.to_csv(os.path.join(DATA_PROCESSED, "sampled_data_scaled_pca.csv"), index=False)

# Lưu cấu hình tiền xử lý JSON
config = {
    "random_state": RANDOM_STATE,
    "original_samples": int(len(all_data)),
    "train_samples": int(len(train_data)),
    "test_samples": int(len(test_data)),
    "original_features": int(len(feature_names)),
    "sample_size": SAMPLE_SIZE,
    "sampling_strategy": "stratified_by_activity",
    "scaler": "StandardScaler",
    "scaler_mean_preserved": True,
    "pca_components": n_components_95,
    "pca_cumulative_variance": round(float(cumulative_variance[n_components_95 - 1]) * 100, 2),
    "sample_files": {
        "indices_file": "data/processed/sample_indices.csv",
        "sampled_pca_data": "data/processed/sampled_data_scaled_pca.csv"
    }
}
with open(os.path.join(RESULTS_DIR, "preprocessing_config.json"), "w", encoding="utf-8") as f:
    json.dump(config, f, indent=4, ensure_ascii=False)

print(f"\nHoàn tất! Đã lưu thành công:")
print(f" - {os.path.join(DATA_PROCESSED, 'sample_indices.csv')}")
print(f" - {os.path.join(DATA_PROCESSED, 'sampled_data_scaled_pca.csv')}")
print(f" - {os.path.join(RESULTS_DIR, 'preprocessing_config.json')}")
print(f" - {os.path.join(RESULTS_DIR, 'table_4_1_scaling_comparison.csv')}")
print(f" - {os.path.join(RESULTS_DIR, 'table_4_2_top20_pca_variance.csv')}")
print(f" - {os.path.join(RESULTS_DIR, 'table_4_3_sample_distribution.csv')}")
print(f" - {os.path.join(RESULTS_DIR, 'explained_variance_milestones.csv')}")
print(f" - Các biểu đồ trong {FIGURES_DIR}")
