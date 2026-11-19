
## 7.1. Ưu điểm và hạn chế của hai thuật toán

| Thuật toán | Ưu điểm | Hạn chế |
|---|---|---|
| **K-Means** | Cách hoạt động dễ hiểu; đại diện mỗi cụm bằng một tâm; có thể gán mẫu mới vào tâm gần nhất. | Cần xác định K; kết quả phụ thuộc khởi tạo tâm và có thể hội tụ vào nghiệm tối ưu cục bộ. |
| **Hierarchical Ward** | Cung cấp cây phân cấp và Dendrogram để quan sát cấu trúc dữ liệu; có thể cắt cùng một cây ở nhiều số cụm; không cần khởi tạo tâm ngẫu nhiên. | Các phép gộp đã thực hiện không được đảo ngược trong quá trình xây cây; cần lựa chọn mức cắt để lấy các cụm cuối cùng; Ward yêu cầu khoảng cách Euclidean. |

Các đặc điểm trên giải thích sự khác nhau về cách hai thuật toán xây dựng cụm. K-Means có thể cập nhật tâm và gán lại mẫu qua các vòng lặp, trong khi Ward tạo một chuỗi các phép gộp. [Tài liệu phân cụm của scikit-learn](https://scikit-learn.org/stable/modules/clustering.html)

Về tài nguyên tính toán, triển khai Ward bằng `scipy.cluster.hierarchy.linkage` sử dụng bộ nhớ bậc hai theo số mẫu, nên cần cân nhắc khi tăng quy mô dữ liệu. Đây là đặc điểm của phương pháp triển khai; **nhóm chưa có phép đo thời gian và bộ nhớ trong cùng điều kiện để kết luận thuật toán nào nhanh hơn trong thí nghiệm này**. [Tài liệu SciPy](https://docs.scipy.org/doc/scipy/reference/generated/scipy.cluster.hierarchy.linkage.html)

## 7.2. Phân tích kết quả thực nghiệm

Hai thuật toán được so sánh trên cùng tập 3.000 mẫu, cùng thứ tự dòng và cùng 104 thành phần PCA. Số cụm được khảo sát từ K=2 đến K=10; cấu hình chính được chọn bằng Silhouette cao nhất.

**Tại K=2**, hai thuật toán có chất lượng nội bộ gần tương đương. K-Means đạt Silhouette bằng 0,415237, nhỉnh hơn Ward với 0,415037; đồng thời có Davies–Bouldin thấp hơn và Calinski–Harabasz cao hơn một chút. Những chênh lệch này nhỏ, chưa đủ để khẳng định K-Means vượt trội rõ rệt.

Ngược lại, Ward đạt ARI=0,332287 và NMI=0,556796, cao hơn K-Means với ARI=0,330108 và NMI=0,547843. Điều này cho thấy Ward có mức tương đồng với nhãn hoạt động tốt hơn theo hai chỉ số đánh giá ngoài tại K=2.

Bảng đối chiếu hoạt động cho thấy hai cụm Ward được diễn giải như sau:

- **Cụm 0:** 1.639 mẫu thuộc các tư thế ngồi, đứng và nằm.
- **Cụm 1:** 1.361 mẫu thuộc các hoạt động đi bộ, lên cầu thang và xuống cầu thang.

Không có mẫu nằm chéo giữa hai nhóm tĩnh–động này trên tập thực nghiệm. Tuy nhiên, mô hình chưa phân biệt riêng từng hoạt động bên trong mỗi nhóm. Vì vậy, kết quả không đồng nghĩa với việc nhận diện chính xác cả sáu hoạt động.

**Tại K=6**, K-Means đạt kết quả tốt hơn Ward trên cả năm chỉ số. Đặc biệt, ARI và NMI của K-Means tại K=6 cao hơn tại K=2, trong khi các chỉ số nội bộ kém hơn. Điều này minh họa rằng việc phân nhóm tương đồng hơn với nhãn hoạt động không nhất thiết tạo ra các cụm gọn và tách biệt hơn.

K=2 vẫn được giữ làm cấu hình chính của cả hai thuật toán theo tiêu chí lựa chọn đã thống nhất. K=6 được trình bày như một thực nghiệm bổ sung.

## 7.3. Hạn chế của thực nghiệm

1. **Kết quả dựa trên một tập mẫu cố định.**

   Việc dùng chung 3.000 mẫu giúp so sánh nhất quán, nhưng nhóm chưa kiểm tra độ ổn định của kết luận trên nhiều tập mẫu hoặc cấu hình tiền xử lý khác nhau.

2. **Phạm vi khảo sát còn giới hạn.**

   Thực nghiệm khảo sát K=2…10 và sử dụng Ward cho Hierarchical. Kết luận về K phù hợp chỉ áp dụng trong phạm vi và tiêu chí đã khảo sát; không đại diện cho mọi phương pháp phân cụm phân cấp.

3. **Nhãn hoạt động đã được dùng ở bước lấy mẫu phân tầng.**

   Nhãn không tham gia xây dựng mô hình hoặc lựa chọn K, nhưng có tham gia việc giữ tỷ lệ hoạt động trong tập mẫu. Vì vậy, không nên mô tả toàn bộ quy trình là hoàn toàn không sử dụng nhãn.

4. **Chưa đánh giá khả năng áp dụng cho dữ liệu mới.**

   StandardScaler và PCA được fit trên dữ liệu gộp train và test trước khi lấy mẫu. Kết quả hiện tại phản ánh cấu trúc của dữ liệu đã quan sát, chưa chứng minh khả năng phân nhóm tốt đối với người tham gia mới hoặc dữ liệu độc lập.

5. **Hình chiếu 2D chỉ hỗ trợ quan sát.**

   Biểu đồ PC1–PC2 không thể hiện toàn bộ thông tin trong 104 chiều. Việc đánh giá định lượng dựa trên không gian đầu vào đầy đủ, không chỉ dựa vào mức độ tách biệt nhìn thấy trên hình.

6. **Chưa có so sánh tài nguyên tính toán trong cùng điều kiện.**

   Nhóm chưa đo thời gian và bộ nhớ của hai thuật toán trên cùng máy, cùng môi trường và cùng quy trình đo.

## 7.4. Kết luận thực nghiệm

Trong điều kiện thực nghiệm của nhóm, K=2 là cấu hình có Silhouette cao nhất đối với cả K-Means và Hierarchical Ward. Kết quả Ward cho thấy cấu trúc nổi bật giữa nhóm tư thế tĩnh và nhóm hoạt động chuyển động, nhưng chưa phân biệt riêng sáu hoạt động.

Tại K=2, K-Means nhỉnh hơn về đánh giá nội bộ, còn Ward nhỉnh hơn về đánh giá ngoài. Tại K=6, K-Means đạt kết quả tốt hơn Ward trên cả năm chỉ số. Do đó, cần đánh giá thuật toán theo mục tiêu cụ thể thay vì khẳng định một phương pháp tốt hơn trong mọi trường hợp.

Hướng phát triển là kiểm tra độ ổn định trên nhiều tập mẫu, khảo sát thêm phương pháp liên kết và mức giảm chiều, đồng thời thiết kế đánh giá trên dữ liệu hoặc người tham gia độc lập nếu muốn nghiên cứu khả năng áp dụng cho dữ liệu mới.
