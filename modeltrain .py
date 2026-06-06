import os
import numpy as np
import joblib
from sklearn.tree import DecisionTreeClassifier

# Tự động tạo thư mục chứa mô hình bộ não nếu chưa có
if not os.path.exists('models'):
    os.makedirs('models')

print("--- ĐANG HUẤN LUYỆN BỘ NÃO AI (DECISION TREE) ---")

# Tự động tạo dữ liệu mẫu (Diện tích, Độ tròn, Màu H, Màu S, Màu V)
np.random.seed(42)
plastic_sample = np.random.multivariate_normal([30, 150, 200, 6000, 0.85], [[2, 5, 5, 500, 0.01]]*5, 100)
paper_sample = np.random.multivariate_normal([15, 50, 180, 9000, 0.55], [[2, 5, 5, 800, 0.02]]*5, 100)
metal_sample = np.random.multivariate_normal([90, 20, 240, 3500, 0.90], [[2, 5, 5, 400, 0.01]]*5, 100)

X_train = np.vstack((plastic_sample, paper_sample, metal_sample))
y_train = np.array([0]*100 + [1]*100 + [2]*100)

# Khởi tạo và huấn luyện thuật toán Cây quyết định
model = DecisionTreeClassifier(max_depth=4, random_state=42)
model.fit(X_train, y_train)

# Xuất bộ não đã học xong ra file cứng
joblib.dump(model, 'models/decision_tree.pkl')
print("[AI] Thanh cong! Da luu file 'models/decision_tree.pkl'")