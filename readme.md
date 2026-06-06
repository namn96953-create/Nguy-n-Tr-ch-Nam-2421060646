```markdown
# 🏭 Hệ Thống Giám Sát & Phân Loại Sản Phẩm Băng Chuyền Real-time (SCADA AI)

An industrial-grade SCADA simulation and product sorting system utilizing Machine Learning (Decision Tree) and Computer Vision (OpenCV) to classify and sort recyclable items on a conveyor belt.

---

## 📝 1. Tổng Quan Dự Án
Dự án tập trung giải quyết bài toán phân loại tự động 03 nhóm vật phẩm tái chế phổ biến trong công nghiệp bao gồm: **Chai Nhựa (Plastic)**, **Hộp Giấy (Paper)**, và **Vỏ lon Kim loại (Metal)** khi chúng di chuyển trên băng tải phẳng thực tế hoặc môi trường sa bàn giả lập.

---

## 🛠️ 2. Tính Năng Cốt Lõi
- **Thị giác máy thời gian thực (Computer Vision):** Thu thập dữ liệu hình ảnh trực tiếp từ Camera, lọc nhiễu Gaussian, phân ngưỡng nhị phân biên vật thể (`Contours`), tự động khoanh vùng `Bounding Box` và đổi màu sắc khung hiển thị linh hoạt theo từng lớp vật phẩm nhận diện.
- **Trích xuất 5 chiều đặc trưng công nghệ:** `[Màu H, Màu S, Màu V, Diện tích (Area), Độ tròn (Roundness)]`.
- **Giao diện quản lý trung tâm SCADA trực quan:**
  - **Màn hình luồng Camera:** Hiển thị trực tiếp luồng hình ảnh từ Webcam hoặc Camera công nghiệp thời gian thực phục vụ trích xuất đặc trưng vùng biên.
  - **Đồng hồ Servo vật lý ảo (Servo Canvas):** Phản hồi trực quan góc quay cơ cấu chấp hành theo đúng nhãn AI ($45^\circ$ cho Plastic, $135^\circ$ cho Paper, $20^\circ$ cho Metal) và tự động reset về trạng thái cân bằng $90^\circ$ sau 1.3 giây hành động.
  - **Bảng đếm sản phẩm thông minh:** Thống kê cập nhật thời gian thực tổng lượng sản phẩm đã phân loại và chi tiết sản lượng từng nhóm.
  - **Cơ chế an toàn dừng khẩn cấp (Emergency Stop):** Nút bấm công nghiệp cho phép đóng băng toàn bộ hệ thống ngay lập tức khi xảy ra sự cố cơ khí trên băng chuyền.

---

## 📂 3. Kiến Trúc Thư Mục Dự Án
```text
project-sorting-conveyor/
├── models/
│   └── decision_tree.pkl    # Bộ não AI sau khi học xong (được đóng gói bằng Joblib)
├── 1_train_model.py         # Script Python sinh dữ liệu mẫu và huấn luyện mô hình
├── 2_scada_app.py           # Ứng dụng SCADA điều khiển trung tâm và xử lý ảnh từ Camera
└── README.md                # Tài liệu hướng dẫn hệ thống (File này)