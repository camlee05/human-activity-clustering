"""Kiểm tra các lỗi bàn giao dễ làm sai kết quả thực nghiệm."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from run_kmeans import load_inputs, select_k


class HandoffTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "results").mkdir()
        (self.root / "data/processed").mkdir(parents=True)
        raw = self.root / "data/raw/UCI HAR Dataset"
        for split, labels in [("train", [1, 1, 2]), ("test", [2, 1, 2])]:
            (raw / split).mkdir(parents=True)
            np.savetxt(raw / split / f"y_{split}.txt", labels, fmt="%d")
        config = {"pca_components": 2, "sample_size": 4, "sample_files": {
            "sampled_pca_data": "data/processed/sample.csv",
            "indices_file": "data/processed/indices.csv",
        }}
        (self.root / "results/preprocessing_config.json").write_text(json.dumps(config))
        self.data = pd.DataFrame({"PC1": [1., 2., 3., 4.], "PC2": [4., 3., 2., 1.],
                                  "Original_Index": [0, 2, 3, 5], "Subject": [1, 1, 2, 2],
                                  "Activity": [1, 2, 2, 2], "ActivityName": ["A", "B", "B", "B"]})
        self.indices = self.data[["Original_Index", "Subject", "Activity", "ActivityName"]].copy()
        self.indices.insert(0, "Sample_Index", np.arange(4))
        self.write_data()

    def write_data(self):
        self.data.to_csv(self.root / "data/processed/sample.csv", index=False)
        self.indices.to_csv(self.root / "data/processed/indices.csv", index=False)

    def test_metadata_never_enters_features(self):
        _, _, X, *_ = load_inputs(self.root)
        np.testing.assert_array_equal(X, self.data[["PC1", "PC2"]].to_numpy())

    def test_reordered_handoff_rejected(self):
        self.indices = self.indices.iloc[::-1].reset_index(drop=True)
        self.write_data()
        with self.assertRaisesRegex(ValueError, "thứ tự dòng"):
            load_inputs(self.root)

    def test_wrong_reference_labels_rejected(self):
        self.data.loc[0, "Activity"] = 2
        self.indices.loc[0, "Activity"] = 2
        self.write_data()
        with self.assertRaisesRegex(ValueError, "UCI HAR"):
            load_inputs(self.root)

    def test_nonfinite_features_rejected(self):
        self.data.loc[0, "PC1"] = np.inf
        self.write_data()
        with self.assertRaisesRegex(ValueError, "NaN hoặc vô cực"):
            load_inputs(self.root)

    def test_k_selection_ignores_external_scores(self):
        values = pd.DataFrame({"K": [6, 2, 3], "Silhouette": [.2, .4, .4], "ARI": [1., 0., .9]})
        self.assertEqual(select_k(values), 2)


if __name__ == "__main__":
    unittest.main()
