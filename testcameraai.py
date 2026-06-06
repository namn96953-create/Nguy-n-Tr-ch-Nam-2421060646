import cv2
import numpy as np
import joblib
import os

print("--- KIỂM TRA MẮT NHÌN AI QUA VIDEO/CAM ---")

# Nạp bộ não AI
if not os.path.exists('models/decision_tree.pkl'):
    print("[LỖI] Vui long chay file '1_train_model.py' truoc de tao bo nao AI!")
    exit()

model = joblib.load('models/decision_tree.pkl')
class_labels = {0: 'Plastic', 1: 'Paper', 2: 'Metal'}

# Đọc video mẫu, nếu không có video sẽ tự mở Webcam (0)
video_path = 'conveyor_simulation.mp4'
cap = cv2.VideoCapture(video_path if os.path.exists(video_path) else 0)

while True:
    ret, frame = cap.read()
    if not ret:
        if os.path.exists(video_path): # Tự động lặp lại video nếu hết
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            continue
        break
        
    frame_resized = cv2.resize(frame, (600, 400))
    gray = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    _, thresh = cv2.threshold(blurred, 110, 255, cv2.THRESH_BINARY_INV)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for contour in contours:
        if cv2.contourArea(contour) < 2500:
            continue
        
        # Tính toán đặc trưng
        perimeter = cv2.arcLength(contour, True)
        roundness = (4 * np.pi * cv2.contourArea(contour)) / (perimeter ** 2) if perimeter > 0 else 0
        hsv = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2HSV)
        mask = np.zeros(gray.shape, np.uint8)
        cv2.drawContours(mask, [contour], -1, 255, -1)
        mean_hsv = cv2.mean(hsv, mask=mask)
        
        # Dự đoán nhãn bằng AI
        features = np.array([[mean_hsv[0], mean_hsv[1], mean_hsv[2], cv2.contourArea(contour), roundness]])
        prediction = model.predict(features)[0]
        
        # Vẽ khung lên màn hình xem thử
        x, y, w, h = cv2.boundingRect(contour)
        cv2.rectangle(frame_resized, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.putText(frame_resized, class_labels[prediction], (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

    cv2.imshow("Kiem tra nhan dien AI (An Q de thoat)", frame_resized)
    if cv2.waitKey(30) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()