# Quy tắc dự án ROS SLAM cho AI Agents
- Lĩnh vực: Robot di động tự hành vẽ bản đồ 2D/3D sử dụng ROS (Python, launch/YAML, TF, LiDAR/Odometry, SLAM).
- Quy tắc: Không sửa trực tiếp nhánh `main`, luôn nêu rõ tên file, topic/frame TF và giả định phần cứng nếu chưa có thông số.
- Vai trò:
  - Gemini: Thiết kế kiến trúc gói ROS, luồng topic/TF và kế hoạch triển khai.
  - Claude: Viết node Python, file launch và cấu hình SLAM chi tiết.
  - ChatGPT: Review lỗi TF, đồng bộ thời gian/trễ dữ liệu và tối ưu khi chạy thực tế.
