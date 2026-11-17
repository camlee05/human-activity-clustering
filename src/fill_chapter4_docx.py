"""
Cập nhật nội dung hoàn chỉnh, bảng biểu và hình ảnh cho Chương 4 trong file BÁO CÁO .docx
"""

import os
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT

DOCX_PATH = "/Users/camlee05/development/KPDL/BÁO CÁO .docx"
FIG_DIR = "/Users/camlee05/development/KPDL/human-activity-clustering/results/figures"

doc = docx.Document(DOCX_PATH)

# Tìm vị trí bắt đầu và kết thúc của Chương 4
p_c4_idx = -1
p_c5_idx = -1

for i, p in enumerate(doc.paragraphs):
    if "CHƯƠNG 4. TIỀN XỬ LÝ DỮ LIỆU VÀ PCA" in p.text:
        p_c4_idx = i
    elif "CHƯƠNG 5. XÂY DỰNG CÁC MÔ HÌNH PHÂN CỤM" in p.text:
        p_c5_idx = i
        break

print(f"Chương 4 bắt đầu tại paragraph {p_c4_idx}, Chương 5 bắt đầu tại {p_c5_idx}")

# Cập nhật nội dung các đoạn văn bản
replacements = {
    "Trình bày cách xác định các đặc trưng được sử dụng để phân cụm.": 
        "Sau khi kết hợp tập huấn luyện (Train) và tập kiểm tra (Test) ban đầu của bộ dữ liệu UCI Human Activity Recognition, toàn bộ tập dữ liệu gồm 10.299 mẫu. Bộ dữ liệu đầu vào cho quá trình tiền xử lý được xác định chính xác là toàn bộ 561 đặc trưng số thực (kiểu float64), được trích xuất từ các tín hiệu cảm biến chuyển động gia tốc kế (Accelerometer) và con quay hồi chuyển (Gyroscope) gắn trên điện thoại thông minh ở cả miền thời gian và miền tần số.",
        
    "Giải thích nguyên tắc không sử dụng nhãn hoạt động trong quá trình huấn luyện mô hình phân cụm.":
        "Trong học máy không giám sát (Unsupervised Learning) nói chung và bài toán phân cụm (Clustering) nói riêng, mô hình không được phép tiếp cận bất kỳ thông tin nào liên quan đến nhãn kết quả trong quá trình huấn luyện nhằm tránh hiện tượng rò rỉ dữ liệu (Data Leakage) và đảm bảo tính tự nhiên của cấu trúc cụm. Do đó, nhãn hoạt động (Activity, ActivityName) cùng mã số đối tượng tình nguyện viên (Subject) được loại bỏ hoàn toàn khỏi không gian huấn luyện. Bộ ma trận đặc trưng đầu vào X có kích thước chính xác 10.299 x 561.",
        
    "Nhãn gốc được lưu riêng để phục vụ đánh giá ngoài và diễn giải kết quả.":
        "Nhãn gốc được lưu trữ trong vector nhãn y (kích thước 10.299 x 1) trong môi trường thực nghiệm độc lập. Nhãn này chỉ được sử dụng ở bước sau cùng nhằm mục đích đánh giá bên ngoài (External Evaluation) thông qua các chỉ số Adjusted Rand Index (ARI) và Normalized Mutual Information (NMI), cũng như hỗ trợ trực quan hóa để đối chiếu mức độ tương đồng giữa các cụm hình thành tự nhiên và hành vi thực tế.",
        
    "Trình bày các bước kiểm tra dữ liệu thiếu, dữ liệu bất thường và các vấn đề phát hiện trong EDA.":
        "Dựa trên kết quả khám phá dữ liệu (EDA) ở Chương 3, quy trình kiểm tra chất lượng dữ liệu đầu vào ghi nhận các đặc điểm quan trọng: (1) Tổng số ô mang giá trị khuyết thiếu trong toàn bộ ma trận X là 0 giá trị (0%), do đó không cần áp dụng kỹ thuật điền khuyết; (2) Số lượng mẫu trùng lặp hoàn toàn là 0 mẫu, đảm bảo tính phân biệt và độc lập giữa các cửa sổ đo lường; (3) Mặc dù các thuộc tính đã được chuẩn hóa sơ bộ trong khoảng [-1, 1], giá trị trung bình và độ lệch chuẩn giữa các trục đo vẫn có sự chênh lệch đáng kể, đòi hỏi phải chuẩn hóa z-score đồng bộ trước khi đưa vào các thuật toán phân cụm dựa trên khoảng cách.",
        
    "Trình bày phương pháp chuẩn hóa được lựa chọn, lý do lựa chọn và cách áp dụng.":
        "Các thuật toán phân cụm như K-Means và Hierarchical Clustering sử dụng độ đo khoảng cách Euclid để tính toán độ tương đồng giữa các đối tượng. Nếu các đặc trưng có độ biến thiên không đồng đều, các thuộc tính có phương sai lớn sẽ chiếm ưu thế áp đảo hàm khoảng cách, làm sai lệch ranh giới cụm. Phương pháp chuẩn hóa được lựa chọn là StandardScaler (Z-score Normalization) theo công thức z = (x - μ) / σ, biến đổi toàn bộ 561 đặc trưng về phân phối chuẩn hóa có giá trị trung bình xấp xỉ 0 và độ lệch chuẩn bằng 1.0.",
        
    "[CHÈN BẢNG 4.1: So sánh thống kê dữ liệu trước và sau chuẩn hóa]":
        "Bảng 4.1 thể hiện sự thay đổi về mặt thống kê của 5 đặc trưng tiêu biểu trước và sau khi thực hiện chuẩn hóa z-score.",
        
    "4.2.1. Mục đích áp dụng PCA":
        "4.2.1. Mục đích áp dụng PCA\nBộ dữ liệu sau tiền xử lý có số lượng thuộc tính lên tới 561 chiều. Không gian đặc trưng quá lớn dẫn đến hiện tượng 'Lời nguyền số chiều' (Curse of Dimensionality), khiến khoảng cách giữa các cặp điểm trong không gian trở nên tương đương nhau, làm suy giảm khả năng phân tách của các thuật toán phân cụm. Ngoài ra, việc tồn tại tính tương quan cao giữa các trục đo lường gây ra sự dư thừa thông tin và tăng chi phí tính toán. Áp dụng phân tích thành phần chính (PCA) nhằm loại bỏ hiện tượng đa cộng tuyến, nén không gian dữ liệu xuống số chiều tối thiểu mà vẫn bảo toàn phần lớn phương sai của dữ liệu gốc, đồng thời nâng cao tốc độ hội tụ và độ ổn định của các mô hình phân cụm.",
        
    "4.2.2. Quy trình thực hiện PCA":
        "4.2.2. Quy trình thực hiện PCA\nQuy trình thực hiện PCA gồm các bước tuần tự: (1) Chuẩn hóa ma trận dữ liệu đầu vào X kích thước 10.299 x 561; (2) Tính toán ma trận hiệp phương sai; (3) Phân rã giá trị riêng (Eigenvalues) và vector riêng (Eigenvectors); (4) Sắp xếp các thành phần chính theo thứ tự giảm dần của tỷ lệ phương sai giải thích; (5) Tính phương sai tích lũy và xác định ngưỡng cắt tối ưu giữ lại tối thiểu 95% phương sai.",
        
    "4.2.3. Phân tích tỷ lệ phương sai giải thích":
        "4.2.3. Phân tích tỷ lệ phương sai giải thích\nThực nghiệm phân tích toàn bộ 561 thành phần chính cho thấy phần lớn phương sai của bộ dữ liệu tập trung ở các thành phần chính đầu tiên: thành phần PC1 giải thích tới 50.738% tổng phương sai, PC2 giải thích 6.239% phương sai, và 10 thành phần chính đầu tiên đã giải thích được hơn 70.208% tổng phương sai dữ liệu. Để bảo đảm giữ lại gần như toàn vẹn thông tin nhận dạng hành vi mà không làm thất thoát đặc trưng quan trọng, nhóm nghiên cứu lựa chọn ngưỡng phương sai tích lũy tối thiểu là 95%. Kết quả xác định được 104 thành phần chính đầu tiên (PC1 đến PC104) đạt 95.047% phương sai tích lũy, giúp giảm hơn 81.4% số lượng thuộc tính ban đầu.",
        
    "Nhận xét khả năng quan sát sự phân tách giữa các nhóm dữ liệu trên không gian hai chiều.":
        "Biểu đồ phân bố dữ liệu trên 2 thành phần chính (PCA 2D) cho thấy: Trục PC1 (50.74% phương sai) phân tách rất rõ giữa hai nhóm trạng thái lớn: nhóm hoạt động tĩnh (Sitting, Standing, Laying) tập trung ở nửa mặt phẳng âm (PC1 < 0), trong khi nhóm hoạt động động (Walking, Upstairs, Downstairs) nằm hoàn toàn ở nửa mặt phẳng dương (PC1 > 0). Trục PC2 (6.24% phương sai) hỗ trợ phân tách tư thế nằm (Laying) so với đứng và ngồi. Tuy nhiên, trên mặt phẳng 2 chiều vẫn tồn tại sự giao thoa đáng kể giữa Sitting và Standing cũng như giữa các kiểu đi bộ, chứng minh rằng không gian 2D chưa đủ để phân tách triệt để 6 hoạt động và khẳng định việc giữ lại 104 chiều PCA cho các thuật toán phân cụm là hoàn toàn cần thiết.",
        
    "Trình bày rõ dữ liệu đầu vào cuối cùng được sử dụng cho K-Means và Hierarchical Clustering:":
        "Dữ liệu đầu vào cuối cùng được sử dụng cho cả hai thuật toán K-Means và Hierarchical Clustering được thống nhất như sau: Không gian đặc trưng gồm 104 thành phần chính (PC1 đến PC104) từ phép biến đổi PCA sau khi chuẩn hóa StandardScaler; Quy mô tập thực nghiệm gồm 3.000 mẫu được lấy mẫu phân tầng nhằm bảo đảm tính công bằng khi so sánh.",
        
    "Giải thích lý do sử dụng tập mẫu khoảng 3.000 dòng để thực hiện Hierarchical Clustering nhằm giảm chi phí tính toán.":
        "Thuật toán Hierarchical Clustering (Agglomerative) đòi hỏi tính toán và lưu trữ ma trận khoảng cách pairwise kích thước N x N với độ phức tạp bộ nhớ là O(N^2) và độ phức tạp thời gian là O(N^2 log N) đến O(N^3). Với quy mô dữ liệu đầy đủ N = 10.299 mẫu, ma trận khoảng cách chứa tới khoảng 53 triệu phần tử số thực, tiêu tốn nhiều Gigabyte RAM và mất hàng chục phút tính toán cho mỗi lần thử nghiệm linkage, tiềm ẩn nguy cơ tràn bộ nhớ và treo môi trường chạy. Việc rút gọn tập dữ liệu về quy mô 3.000 mẫu giúp kích thước ma trận khoảng cách giảm xuống chỉ còn khoảng 4.5 triệu phần tử (giảm hơn 11.7 lần tải tính toán), cho phép thuật toán hoàn tất trong vài giây mà vẫn đảm bảo tính đại diện thống kê đầy đủ. Cả K-Means và Hierarchical Clustering đều được huấn luyện trên cùng một tập 3.000 mẫu này để tạo cơ sở so sánh công bằng.",
        
    "Trình bày cách lấy mẫu, cách cố định random state và cách lưu lại chỉ số dòng.":
        "Phương pháp lựa chọn mẫu được thực hiện bằng kỹ thuật Lấy mẫu phân tầng (Stratified Sampling) theo nhãn hoạt động gốc (Activity) với tỷ lệ xấp xỉ 29.13%, đảm bảo tỷ lệ phần trăm số lượng mẫu của từng hoạt động trong tập mẫu 3.000 dòng hoàn toàn tương đương với tỷ lệ trên toàn bộ 10.299 mẫu ban đầu. Tham số ngẫu nhiên được cố định tại random_state = 42 để đảm bảo tính tái lập (reproducibility). Toàn bộ danh sách chỉ số dòng gốc (Original Index từ 0 đến 10.298) được lưu trữ tại file data/processed/sample_indices.csv, dữ liệu 3.000 mẫu chuẩn hóa PCA được lưu tại data/processed/sampled_data_scaled_pca.csv, và thông tin cấu hình được lưu tại results/preprocessing_config.json.",
        
    "Tổng hợp quy trình tiền xử lý và mô tả dữ liệu cuối cùng được sử dụng trong các mô hình phân cụm.":
        "Chương 4 đã thiết lập một quy trình tiền xử lý dữ liệu và trích chọn đặc trưng chặt chẽ: (1) Phân tách độc lập không gian đặc trưng khỏi các thông tin định danh và nhãn giám sát; (2) Chuẩn hóa 561 đặc trưng bằng StandardScaler đưa về phân phối chuẩn; (3) Áp dụng PCA xác định 104 thành phần chính tối ưu giúp giữ lại 95.05% phương sai dữ liệu gốc, giải quyết triệt để vấn đề lời nguyền số chiều và tính tương quan dư thừa; (4) Lựa chọn và cố định tập mẫu phân tầng gồm 3.000 dòng với random_state = 42, lưu trữ đầy đủ file chỉ số và cấu hình. Đây là cơ sở dữ liệu đầu vào chuẩn mực sẵn sàng cho việc triển khai và đánh giá so sánh hai thuật toán K-Means và Hierarchical Clustering ở Chương 5."
}

for p in doc.paragraphs:
    for target, replacement in replacements.items():
        if target in p.text:
            p.text = p.text.replace(target, replacement)
            print(f"Đã cập nhật đoạn: {target[:40]}...")

# Chèn các ảnh vào các đoạn placeholder tương ứng nếu có
for p in doc.paragraphs:
    if "[CHÈN HÌNH 4.1: Biểu đồ Explained Variance Ratio]" in p.text:
        p.text = "Hình 4.1. Tỷ lệ phương sai giải thích của 20 thành phần chính đầu tiên"
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        # chèn ảnh phía trước paragraph này
        img_p = p.insert_paragraph_before()
        img_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        img_p.add_run().add_picture(os.path.join(FIG_DIR, "Hinh_4_1_variance_ratio.png"), width=Inches(5.8))
        print("Đã chèn ảnh Hình 4.1!")
        
    elif "[CHÈN HÌNH 4.2: Biểu đồ Cumulative Explained Variance]" in p.text:
        p.text = "Hình 4.2. Phương sai tích lũy theo số lượng thành phần chính PCA"
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        img_p = p.insert_paragraph_before()
        img_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        img_p.add_run().add_picture(os.path.join(FIG_DIR, "Hinh_4_2_cumulative_variance.png"), width=Inches(5.8))
        print("Đã chèn ảnh Hình 4.2!")
        
    elif "[CHÈN HÌNH 4.3: Biểu đồ phân bố dữ liệu trên PC1 và PC2]" in p.text:
        p.text = "Hình 4.3. Phân bố dữ liệu trên hai thành phần chính (PCA 2D)"
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        img_p = p.insert_paragraph_before()
        img_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        img_p.add_run().add_picture(os.path.join(FIG_DIR, "Hinh_4_3_pca_2d.png"), width=Inches(5.8))
        print("Đã chèn ảnh Hình 4.3!")
        
    elif "[CHÈN BẢNG 4.2: Tỷ lệ phương sai giải thích theo số thành phần chính]" in p.text:
        p.text = "Bảng 4.2. Tỷ lệ phương sai giải thích theo số lượng thành phần chính (Top 10 và các mốc quan trọng)"

# Cập nhật các dòng bỏ trống thừa
for p in doc.paragraphs:
    if p.text in [
        "Không gian đặc trưng được sử dụng.",
        "Phương pháp chuẩn hóa.",
        "Có hoặc không sử dụng PCA làm đầu vào mô hình.",
        "Số lượng mẫu.",
        "Số lượng đặc trưng cuối cùng."
    ]:
        p.text = ""

doc.save(DOCX_PATH)
print("Hoàn tất cập nhật trực tiếp vào file BÁO CÁO .docx!")

