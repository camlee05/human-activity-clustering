# NỘI DUNG HOÀN CHỈNH CHO CHƯƠNG 4 TRONG BÁO CÁO CUỐI KỲ

---

## CHƯƠNG 4. TIỀN XỬ LÝ DỮ LIỆU VÀ PCA

### 4.1. Quy trình tiền xử lý dữ liệu

#### 4.1.1. Xác định dữ liệu đầu vào
Sau khi tiến hành hợp nhất dữ liệu từ hai tập huấn luyện (Train) và tập kiểm tra (Test) ban đầu của bộ dữ liệu UCI Human Activity Recognition, toàn bộ tập dữ liệu gồm $10.299$ dòng và $563$ cột (bao gồm mã đối tượng `Subject`, nhãn số `Activity`, nhãn phân loại `ActivityName` và $561$ cột thuộc tính cảm biến).

Bộ dữ liệu đầu vào cho quá trình tiền xử lý được xác định chính xác là toàn bộ $561$ đặc trưng số thực (thuộc kiểu `float64`), trích xuất từ các tín hiệu cảm biến chuyển động gia tốc kế (Accelerometer) và con quay hồi chuyển (Gyroscope) gắn trên điện thoại thông minh ở miền thời gian và miền tần số.

#### 4.1.2. Tách nhãn hoạt động khỏi dữ liệu đầu vào
Trong học máy không giám sát (Unsupervised Learning) nói chung và bài toán phân cụm (Clustering) nói riêng, mô hình không được phép tiếp cận bất kỳ thông tin nào liên quan đến nhãn kết quả trong quá trình huấn luyện nhằm tránh hiện tượng rò rỉ dữ liệu (Data Leakage) và đảm bảo tính tự nhiên của cấu trúc phân cụm:
- Thuộc tính `Activity` (nhãn số từ 1 đến 6) và `ActivityName` (tên 6 hoạt động: WALKING, WALKING_UPSTAIRS, WALKING_DOWNSTAIRS, SITTING, STANDING, LAYING) cùng mã số tình nguyện viên `Subject` được loại bỏ hoàn toàn khỏi không gian huấn luyện.
- Ma trận đặc trưng phục vụ phân cụm được ký hiệu là $X$ có kích thước $10.299 \times 561$.
- Vector nhãn $y$ kích thước $10.299 \times 1$ được lưu trữ độc lập trong môi trường thực nghiệm, chỉ được sử dụng ở bước sau cùng nhằm mục đích đánh giá bên ngoài (External Evaluation) thông qua các chỉ số Adjusted Rand Index (ARI) và Normalized Mutual Information (NMI), cũng như hỗ trợ trực quan hóa để đối chiếu mức độ tương đồng giữa cụm phát hiện được và hành vi thực tế.

#### 4.1.3. Kiểm tra và xử lý dữ liệu
Dựa trên kết quả khám phá dữ liệu (EDA) ở Chương 3, quy trình kiểm tra chất lượng dữ liệu đầu vào ghi nhận các đặc điểm sau:
- **Giá trị thiếu (Missing Values)**: Tổng số ô mang giá trị khuyết thiếu (`NaN`/`Null`) trong toàn bộ ma trận $X$ là $0$ giá trị (tỷ lệ $0\%$). Do đó, không cần áp dụng các kỹ thuật điền khuyết như Mean/Median Imputation hay K-Nearest Neighbors Imputation.
- **Dữ liệu trùng lặp (Duplicate Records)**: Số lượng dòng dữ liệu trùng lặp hoàn toàn là $0$ dòng, đảm bảo tính phân biệt và độc lập giữa các cửa sổ đo lường.
- **Giá trị ngoại lai và khoảng giá trị**: Mặc dù dữ liệu gốc đã được chuẩn hóa sơ bộ trong khoảng $[-1, 1]$ từ khâu trích xuất tín hiệu, tuy nhiên độ lệch chuẩn và giá trị trung bình giữa các biến chưa thực sự đồng nhất (ví dụ: các biến gia tốc có giá trị trung bình khác $0$, trong khi độ lớn dao động của tín hiệu miền tần số khác biệt đáng kể so với miền thời gian). Do đó, bước chuẩn hóa nâng cao là điều kiện bắt buộc trước khi đưa vào các thuật toán phân cụm dựa trên khoảng cách.

#### 4.1.4. Chuẩn hóa dữ liệu
Các thuật toán phân cụm như K-Means và Hierarchical Clustering sử dụng độ đo khoảng cách Euclid để tính toán độ tương đồng giữa các đối tượng. Nếu các đặc trưng có thang đo và độ biến thiên không đồng đều, những thuộc tính có phương sai lớn sẽ chiếm ưu thế áp đảo hàm khoảng cách, làm sai lệch ranh giới cụm.

Phương pháp chuẩn hóa được lựa chọn là **StandardScaler (Z-score Normalization)** theo công thức:
$$z = \frac{x - \mu}{\sigma}$$
Trong đó $\mu$ là giá trị trung bình và $\sigma$ là độ lệch chuẩn của từng đặc trưng. Quá trình này biến đổi toàn bộ 561 đặc trưng về phân phối chuẩn hóa có giá trị trung bình $\mu \approx 0$ và độ lệch chuẩn $\sigma = 1.0$.

**Bảng 4.1. So sánh thống kê dữ liệu trước và sau chuẩn hóa**

| Đặc trưng | Mean (Gốc) | Std (Gốc) | Min (Gốc) | Max (Gốc) | Mean (Chuẩn hóa) | Std (Chuẩn hóa) | Min (Chuẩn hóa) | Max (Chuẩn hóa) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `tBodyAcc-mean()-X` | 0.2743 | 0.0676 | -1.0000 | 1.0000 | 0.0000 | 1.0000 | -18.8445 | 10.7306 |
| `tBodyAcc-mean()-Y` | -0.0177 | 0.0371 | -1.0000 | 1.0000 | 0.0000 | 1.0000 | -26.4571 | 27.4130 |
| `tBodyAcc-mean()-Z` | -0.1089 | 0.0530 | -1.0000 | 1.0000 | 0.0000 | 1.0000 | -16.8031 | 20.9111 |
| `tBodyAcc-std()-X` | -0.6078 | 0.4387 | -1.0000 | 1.0000 | 0.0000 | 1.0000 | -0.8941 | 3.6651 |
| `tBodyAcc-std()-Y` | -0.5102 | 0.5002 | -1.0000 | 1.0000 | 0.0000 | 1.0000 | -0.9792 | 3.0191 |

---

### 4.2. Giảm chiều dữ liệu bằng PCA

#### 4.2.1. Mục đích áp dụng PCA
Bộ dữ liệu sau tiền xử lý có số lượng thuộc tính lên tới $561$ chiều. Không gian đặc trưng quá lớn dẫn đến hiện tượng "Lời nguyền số chiều" (Curse of Dimensionality), khiến khoảng cách giữa các cặp điểm trong không gian trở nên tương đương nhau, làm suy giảm nghiêm trọng khả năng phân tách của các thuật toán phân cụm. Ngoài ra, việc tồn tại tính tương quan cao giữa các trục đo lường (như đã phát hiện tại ma trận tương quan ở EDA) gây ra sự dư thừa thông tin và tăng chi phí tính toán.

Áp dụng phân tích thành phần chính (PCA) nhằm các mục đích:
1. Loại bỏ hiện tượng đa cộng tuyến giữa các đặc trưng cảm biến.
2. Nén không gian dữ liệu từ 561 chiều xuống số chiều tối thiểu mà vẫn bảo toàn phần lớn phương sai (thông tin) của dữ liệu gốc.
3. Nâng cao tốc độ hội tụ và độ ổn định của các thuật toán phân cụm K-Means và Hierarchical Clustering.
4. Chiếu dữ liệu xuống không gian 2D phục vụ trực quan hóa và quan sát trực quan cấu trúc cụm.

#### 4.2.2. Quy trình thực hiện PCA
Quy trình thực hiện PCA gồm các bước tuần tự:
1. Khởi tạo ma trận dữ liệu đã chuẩn hóa $X_{scaled} \in \mathbb{R}^{10299 \times 561}$.
2. Tính toán ma trận hiệp phương sai (Covariance Matrix) $\Sigma = \frac{1}{N} X_{scaled}^T X_{scaled}$.
3. Phân rã giá trị riêng (Eigenvalues $\lambda_i$) và vector riêng (Eigenvectors $v_i$).
4. Sắp xếp các thành phần chính theo thứ tự giảm dần của tỷ lệ phương sai giải thích:
   $$\text{Ratio}_i = \frac{\lambda_i}{\sum_{j=1}^{561} \lambda_j}$$
5. Tính phương sai tích lũy (Cumulative Explained Variance) và xác định ngưỡng cắt tối ưu $\ge 95\%$.

#### 4.2.3. Phân tích tỷ lệ phương sai giải thích
Thực nghiệm phân tích toàn bộ 561 thành phần chính cho thấy phần lớn phương sai của bộ dữ liệu tập trung ở các thành phần chính đầu tiên:
- Thành phần chính thứ nhất (**PC1**) giải thích tới **$50.738\%$** tổng phương sai của toàn bộ dữ liệu.
- Thành phần chính thứ hai (**PC2**) giải thích **$6.239\%$** phương sai.
- 10 thành phần chính đầu tiên đã giải thích được hơn **$70.208\%$** tổng phương sai dữ liệu.

*(Chèn Hình 4.1: `Hinh_4_1_variance_ratio.png`)*
**Hình 4.1. Tỷ lệ phương sai giải thích của 20 thành phần chính đầu tiên**

*(Chèn Hình 4.2: `Hinh_4_2_cumulative_variance.png`)*
**Hình 4.2. Phương sai tích lũy theo số lượng thành phần chính PCA**

Để bảo đảm giữ lại gần như toàn vẹn thông tin nhận dạng hành vi mà không làm thất thoát đặc trưng quan trọng, nhóm nghiên cứu lựa chọn ngưỡng phương sai tích lũy tối thiểu là **$95\%$**. Kết quả tính toán cho thấy tại **$104$ thành phần chính đầu tiên**, phương sai tích lũy đạt **$95.047\%$**.

**Bảng 4.2. Tỷ lệ phương sai giải thích theo số lượng thành phần chính (Top 10 và các mốc quan trọng)**

| Thành phần chính | Tỷ lệ phương sai giải thích (%) | Phương sai tích lũy (%) | Ghi chú / Mốc quan trọng |
| :---: | :---: | :---: | :--- |
| **PC1** | 50.738% | 50.738% | Mốc đạt $\ge 50\%$ phương sai |
| **PC2** | 6.239% | 56.977% | |
| **PC3** | 2.693% | 59.670% | |
| **PC4** | 2.453% | 62.123% | Mốc đạt $\ge 60\%$ phương sai |
| **PC5** | 1.889% | 64.012% | |
| **PC6** | 1.631% | 65.643% | |
| **PC7** | 1.415% | 67.058% | |
| **PC8** | 1.216% | 68.274% | |
| **PC9** | 0.985% | 69.259% | |
| **PC10** | 0.949% | 70.208% | Mốc đạt $\ge 70\%$ phương sai |
| **PC27** | 0.417% | 80.104% | Mốc đạt $\ge 80\%$ phương sai |
| **PC65** | 0.174% | 90.048% | Mốc đạt $\ge 90\%$ phương sai |
| **PC104** | 0.092% | **95.047%** | **NGƯỠNG LỰA CHỌN TỐI ƯU ($\ge 95\%$)** |
| **PC182** | 0.021% | 99.020% | Mốc đạt $\ge 99\%$ phương sai |

#### 4.2.4. Trực quan hóa dữ liệu bằng PCA 2D
Để có cái nhìn trực quan ban đầu về cấu trúc phân bố không gian của các hành vi vận động, ma trận dữ liệu được chiếu xuống không gian hai chiều tạo bởi hai thành phần chính đầu tiên (PC1 và PC2), giải thích tổng cộng $56.98\%$ phương sai.

*(Chèn Hình 4.3: `Hinh_4_3_pca_2d.png`)*
**Hình 4.3. Phân bố dữ liệu trên hai thành phần chính (PCA 2D)**

**Nhận xét khả năng phân tách trên không gian 2D**:
1. **Phân tách rõ rệt giữa hai nhóm trạng thái lớn**:
   - Trục PC1 thể hiện rõ năng lượng vận động của cơ thể. Phía bên trái ($PC1 < 0$) là vùng tập trung hoàn toàn của **nhóm hoạt động tĩnh** (`SITTING`, `STANDING`, `LAYING`).
   - Phía bên phải ($PC1 > 0$) là vùng tập trung của **nhóm hoạt động động** (`WALKING`, `WALKING_UPSTAIRS`, `WALKING_DOWNSTAIRS`).
2. **Khả năng phân biệt nội nhóm**:
   - Trong nhóm tĩnh, hoạt động nằm (`LAYING`) tách biệt tương đối rõ ràng so với đứng và ngồi nhờ trục PC2. Tuy nhiên, giữa `SITTING` và `STANDING` có độ giao thoa lớn trên mặt phẳng 2D.
   - Trong nhóm động, 3 hoạt động đi bộ, lên cầu thang và xuống cầu thang có sự xen kẽ đáng kể do các chuyển động bước chân có tần số và hình dạng sóng tương đồng nhau.
   - Nhận xét này chứng minh việc chỉ sử dụng 2 chiều PCA là chưa đủ để phân tách trọn vẹn 6 hoạt động, khẳng định tính đúng đắn khi lựa chọn không gian **104 chiều PCA** cho các mô hình phân cụm chính thức.

#### 4.2.5. Lựa chọn dữ liệu sử dụng cho mô hình
Trên cơ sở các kết quả phân tích ở trên, cấu hình dữ liệu đầu vào cuối cùng được chốt lại như sau:
- **Không gian đặc trưng**: Không gian nén 104 thành phần chính (PCs) thu được từ phép biến đổi PCA.
- **Phương pháp chuẩn hóa**: StandardScaler (Z-score) áp dụng trước khi phân rã PCA.
- **Quy mô tập dữ liệu thực nghiệm**: Tập mẫu thống nhất gồm **3.000 dòng** (được mô tả chi tiết tại Mục 4.3).
- **Số lượng thuộc tính đầu vào mô hình**: **104 đặc trưng** ($PC1$ đến $PC104$).

---

### 4.3. Lựa chọn tập dữ liệu mẫu

#### 4.3.1. Lý do lựa chọn tập mẫu
Trong đồ án này, bên cạnh K-Means, nhóm nghiên cứu triển khai thuật toán **Hierarchical Clustering (Agglomerative)**:
- Thuật toán phân cụm phân cấp đòi hỏi tính toán và lưu trữ ma trận khoảng cách pairwise kích thước $N \times N$, với độ phức tạp không gian bộ nhớ là $O(N^2)$ và độ phức tạp thời gian là $O(N^2 \log N)$ đến $O(N^3)$.
- Với quy mô dữ liệu đầy đủ $N = 10.299$ mẫu, ma trận khoảng cách chứa tới $\frac{10299 \times 10298}{2} \approx 53$ triệu phần tử số thực float64, tiêu tốn nhiều Gigabyte RAM và mất hàng chục phút tính toán cho mỗi lần thử nghiệm linkage, tiềm ẩn nguy cơ tràn bộ nhớ và treo môi trường chạy.
- Việc rút gọn tập dữ liệu về quy mô **3.000 mẫu** giúp kích thước ma trận khoảng cách giảm xuống chỉ còn $\approx 4.5$ triệu phần tử (giảm hơn **11.7 lần** tải tính toán và bộ nhớ), cho phép thuật toán hoàn tất trong vài giây mà vẫn đảm bảo tính đại diện thống kê đầy đủ.
- Đồng thời, cả K-Means và Hierarchical Clustering sẽ được huấn luyện trên **cùng một tập 3.000 mẫu này**, tạo cơ sở so sánh công bằng, khách quan về các chỉ số nội bộ (Silhouette, Davies-Bouldin, Calinski-Harabasz) và chỉ số bên ngoài (ARI, NMI).

#### 4.3.2. Phương pháp lựa chọn mẫu
- **Kỹ thuật lấy mẫu**: Áp dụng phương pháp **Lấy mẫu phân tầng (Stratified Sampling)** theo nhãn hoạt động gốc `Activity`. Kỹ thuật này bảo đảm tỷ lệ phần trăm số lượng mẫu của từng hoạt động trong tập mẫu 3.000 dòng hoàn toàn tương đương với tỷ lệ trên toàn bộ 10.299 mẫu ban đầu.
- **Tính tái lập (Reproducibility)**: Cố định tham số ngẫu nhiên `random_state = 42`.
- **Lưu trữ vết dữ liệu**:
  - Toàn bộ chỉ số dòng gốc (Original Index từ 0 đến 10.298) của 3.000 mẫu được xuất ra tệp `data/processed/sample_indices.csv`.
  - Bộ dữ liệu mẫu 104 chiều sau PCA được lưu trữ tại `data/processed/sampled_data_scaled_pca.csv`.
  - Toàn bộ tham số cấu hình tiền xử lý được lưu trữ dưới định dạng JSON tại `results/preprocessing_config.json`.

#### 4.3.3. Đặc điểm tập dữ liệu mẫu

**Bảng 4.3. Đặc điểm và phân bố tập dữ liệu mẫu so với tập dữ liệu gốc**

| Tiêu chí | Dữ liệu gốc (Toàn bộ) | Tập dữ liệu mẫu thực nghiệm |
| :--- | :---: | :---: |
| **Tổng số mẫu ($N$)** | 10.299 mẫu | **3.000 mẫu** |
| **Số đặc trưng ban đầu** | 561 đặc trưng | 561 đặc trưng |
| **Số chiều sau PCA ($\ge 95\%$)** | 104 thành phần | **104 thành phần** |
| **Phương pháp chuẩn hóa** | StandardScaler | StandardScaler |
| **Phương pháp lấy mẫu** | - | **Stratified Sampling (theo nhãn)** |
| **Random State** | - | **42** |
| *WALKING* | 1.722 mẫu (16.72%) | **502 mẫu (16.73%)** |
| *WALKING_UPSTAIRS* | 1.544 mẫu (14.99%) | **450 mẫu (15.00%)** |
| *WALKING_DOWNSTAIRS* | 1.406 mẫu (13.65%) | **409 mẫu (13.63%)** |
| *SITTING* | 1.777 mẫu (17.25%) | **518 mẫu (17.27%)** |
| *STANDING* | 1.906 mẫu (18.51%) | **555 mẫu (18.50%)** |
| *LAYING* | 1.944 mẫu (18.88%) | **566 mẫu (18.87%)** |

---

### 4.4. Kết luận chương
Chương 4 đã thiết lập một quy trình tiền xử lý dữ liệu và trích chọn đặc trưng chặt chẽ, khoa học:
1. Đã phân tách dữ liệu đặc trưng khỏi các thông tin định danh và nhãn giám sát, ngăn chặn triệt để hiện tượng rò rỉ thông tin trong học máy không giám sát.
2. Đã kiểm tra tính toàn vẹn của dữ liệu và thực hiện chuẩn hóa dữ liệu bằng StandardScaler, đưa 561 thuộc tính về cùng một thang đo chuẩn.
3. Đã áp dụng phân tích thành phần chính (PCA), xác định được **104 thành phần chính** là số lượng tối ưu giúp giữ lại tới **$95.05\%$** phương sai dữ liệu gốc, giải quyết triệt để vấn đề lời nguyền số chiều và tính đa cộng tuyến.
4. Đã lựa chọn và cố định tập mẫu phân tầng gồm **3.000 dòng** với `random_state = 42`, lưu trữ đầy đủ file chỉ số và file cấu hình. Đây là đầu vào chuẩn hóa thống nhất sẵn sàng để triển khai và so sánh hai thuật toán K-Means và Hierarchical Clustering ở Chương 5.

