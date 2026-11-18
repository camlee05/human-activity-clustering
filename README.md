# Phân nhóm hoạt động con người từ dữ liệu cảm biến điện thoại

Dự án bài tập lớn môn **Khai phá dữ liệu**, sử dụng bộ dữ liệu **UCI Human Activity Recognition Using Smartphones (UCI HAR)** để khám phá và phân nhóm các hoạt động của con người thông qua đặc trưng cảm biến điện thoại.

## Giới thiệu

Điện thoại thông minh có thể ghi nhận chuyển động bằng gia tốc kế và con quay hồi chuyển. Các tín hiệu này được xử lý thành những đặc trưng số, phản ánh sự khác biệt giữa các trạng thái và hoạt động của người dùng.

Dự án áp dụng phương pháp học không giám sát để tìm các nhóm mẫu có đặc điểm tương đồng, sau đó đối chiếu với hoạt động thực tế nhằm đánh giá và diễn giải kết quả.

## Mục tiêu

- Tìm hiểu cấu trúc và đặc điểm của bộ dữ liệu UCI HAR.
- Khám phá dữ liệu bằng thống kê và biểu đồ.
- Chuẩn hóa dữ liệu và giảm chiều bằng PCA.
- Xây dựng, đánh giá mô hình phân cụm K-Means.
- Hướng tới so sánh K-Means với Hierarchical Clustering trên cùng tập dữ liệu.
- Phân tích mối quan hệ giữa các cụm và hoạt động thực tế.

## Bộ dữ liệu

Bộ dữ liệu UCI HAR được thu thập từ **30 người tham gia**, sử dụng điện thoại Samsung Galaxy S II đặt tại thắt lưng.

| Đặc điểm | Giá trị |
| --- | --- |
| Tổng số mẫu | 10.299 |
| Số đặc trưng cảm biến | 561 |
| Số người tham gia | 30 |
| Số hoạt động | 6 |

Sáu hoạt động trong bộ dữ liệu gồm:

| Hoạt động | Ý nghĩa |
| --- | --- |
| WALKING | Đi bộ |
| WALKING_UPSTAIRS | Đi lên cầu thang |
| WALKING_DOWNSTAIRS | Đi xuống cầu thang |
| SITTING | Ngồi |
| STANDING | Đứng |
| LAYING | Nằm |

## Phương pháp thực hiện

### Khám phá dữ liệu

Kiểm tra kích thước, kiểu dữ liệu, giá trị thiếu, dòng trùng lặp, phân bố hoạt động và mức độ tương quan giữa các đặc trưng.

### Tiền xử lý và giảm chiều

Dữ liệu được chuẩn hóa bằng **StandardScaler**, sau đó áp dụng **PCA** để giảm từ 561 đặc trưng xuống **104 thành phần chính**, giữ lại khoảng **95,05% phương sai**.

Tập thực nghiệm gồm **3.000 mẫu cố định**, được lấy mẫu phân tầng theo hoạt động với `random_state = 42`, nhằm tạo đầu vào thống nhất cho việc so sánh các thuật toán.

### Phân cụm K-Means

Khảo sát số cụm **K từ 2 đến 10**, sử dụng Elbow và Silhouette để phân tích và lựa chọn số cụm phù hợp.

Mô hình chỉ sử dụng các thành phần PCA làm đầu vào. Nhãn hoạt động và thông tin định danh được giữ riêng, không tham gia huấn luyện hoặc lựa chọn K.

### Đánh giá kết quả

Các chỉ số đánh giá nội bộ:

- Silhouette Score.
- Davies–Bouldin Index.
- Calinski–Harabasz Index.

Các chỉ số đối chiếu với nhãn hoạt động sau phân cụm:

- Adjusted Rand Index (ARI).
- Normalized Mutual Information (NMI).

Kết quả được trình bày bằng bảng số liệu, biểu đồ phân cụm trên PC1–PC2 và bảng phân bố hoạt động trong từng cụm.

## Kết quả K-Means

Trong dải giá trị khảo sát, **K=2 có Silhouette cao nhất** và được chọn làm mô hình chính. Hai cụm chủ yếu phản ánh sự khác biệt giữa nhóm hoạt động chuyển động và nhóm tư thế tĩnh.

Kết quả này chưa tương ứng với việc nhận diện riêng biệt cả sáu hoạt động. Thực nghiệm K=6 được giữ lại để phân tích bổ sung và làm rõ sự khác biệt giữa cấu trúc phân cụm với các nhãn hoạt động gốc.

## Công nghệ sử dụng

- Python.
- Jupyter Notebook.
- NumPy và pandas.
- Matplotlib và Seaborn.
- Scikit-learn.
- SciPy.

## Thành viên thực hiện

| Thành viên | Phần việc chính |
| --- | --- |
| Cao Thanh Thảo | Tìm hiểu đề tài và khám phá dữ liệu |
| Lê Thị Cẩm Ly | Tiền xử lý, chuẩn hóa và PCA |
| Nguyễn Văn Thành | Xây dựng và đánh giá K-Means |
| Lê Quang Huy | Hierarchical Clustering và so sánh thuật toán |

## Ý nghĩa của dự án

Dự án giúp vận dụng quy trình khai phá dữ liệu từ khám phá, tiền xử lý đến xây dựng và đánh giá mô hình. Qua dữ liệu cảm biến điện thoại, nhóm tìm hiểu khả năng phát hiện cấu trúc hoạt động bằng phân cụm và những hạn chế khi diễn giải các cụm thành hoạt động thực tế.
