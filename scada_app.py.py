import os
import cv2
import numpy as np
import time
import joblib
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

print("--- KHỞI CHẠY HỆ THỐNG MÔ PHỎNG SCADA CAO CẤP CHUẨN 100% ---")

# =====================================================================
# BƯỚC 1: KIỂM TRA BỘ NÃO AI
# =====================================================================
if not os.path.exists('models/decision_tree.pkl'):
    print("[LỖI] Không tìm thấy file bộ não 'models/decision_tree.pkl'!")
    exit()

model = joblib.load('models/decision_tree.pkl')
class_labels = {0: 'Plastic', 1: 'Paper', 2: 'Metal'}

# Các biến dữ liệu hệ thống
count_plastic = 0
count_paper = 0
count_metal = 0
count_total = 0
is_running = True  # Trạng thái nút bấm dừng khẩn cấp

# =====================================================================
# BƯỚC 2: GIAO DIỆN SCADA ĐỒ HỌA CAO CẤP
# =====================================================================
root = tk.Tk()
root.title("HỆ THỐNG GIÁM SÁT BĂNG CHUYỀN SCADA AI - NGUYỄN TRẠCH NAM")
root.geometry("1080x580")
root.configure(bg="#1a252f")

# Tiêu đề chính điều khiển trung tâm
title_label = tk.Label(root, text="HỆ THỐNG GIÁM SÁT & PHÂN LOẠI SẢN PHẨM REAL-TIME", 
                       font=("Helvetica", 16, "bold"), fg="#1abc9c", bg="#1a252f")
title_label.pack(pady=10)

main_frame = tk.Frame(root, bg="#1a252f")
main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

# Khung trái: Màn hình camera
video_label = tk.Label(main_frame, bg="black", bd=3, relief="flat")
video_label.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)

# Khung phải: Bảng điều khiển SCADA
control_frame = tk.LabelFrame(main_frame, text=" BẢNG ĐIỀU KHIỂN TRUNG TÂM (SCADA) ", 
                              font=("Helvetica", 11, "bold"), fg="white", bg="#2c3e50", bd=2, width=380)
control_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=False, padx=5)
control_frame.pack_propagate(False)

# 1. Trạng thái hoạt động chữ nhảy
status_title = tk.Label(control_frame, text="TRẠNG THÁI HỆ THỐNG:", font=("Helvetica", 10, "bold"), fg="#bdc3c7", bg="#2c3e50")
status_title.pack(pady=(10, 0))
status_label = tk.Label(control_frame, text="Băng chuyền sẵn sàng\nĐang quét vật phẩm...", 
                        font=("Helvetica", 12, "bold"), fg="#f1c40f", bg="#2c3e50", justify=tk.CENTER)
status_label.pack(pady=(0, 10))

# 2. Đồng hồ kim gạt Servo ảo
canvas = tk.Canvas(control_frame, width=200, height=150, bg="#2c3e50", highlightthickness=0)
canvas.pack()

def draw_servo_pointer(angle):
    canvas.delete("all")
    canvas.create_arc(10, 20, 190, 150, start=0, extent=180, style=tk.ARC, outline="#ebf5fb", width=3)
    rad = np.radians(angle)
    x = 100 + 70 * np.cos(rad)
    y = 100 - 70 * np.sin(rad)
    canvas.create_line(100, 100, x, y, fill="#e74c3c", width=5, arrow=tk.LAST)
    canvas.create_oval(92, 92, 108, 108, fill="#f1c40f", outline="white")

draw_servo_pointer(90)

# 3. Bảng đếm thống kê thông minh
counter_frame = tk.Frame(control_frame, bg="#34495e", bd=1, relief="solid")
counter_frame.pack(fill=tk.X, padx=15, pady=10)

lbl_p = tk.Label(counter_frame, text="Chai Nhựa (Plastic): 0", font=("Helvetica", 11), fg="#3498db", bg="#34495e")
lbl_p.pack(anchor=tk.W, padx=10, pady=3)
lbl_w = tk.Label(counter_frame, text="Hộp Giấy (Paper):  0", font=("Helvetica", 11), fg="#2ecc71", bg="#34495e")
lbl_w.pack(anchor=tk.W, padx=10, pady=3)
lbl_m = tk.Label(counter_frame, text="Kim Loại (Metal):   0", font=("Helvetica", 11), fg="#e74c3c", bg="#34495e")
lbl_m.pack(anchor=tk.W, padx=10, pady=3)

lbl_total = tk.Label(control_frame, text="TỔNG SẢN PHẨM ĐÃ PHÂN LOẠI: 0", font=("Helvetica", 11, "bold"), fg="#1abc9c", bg="#2c3e50")
lbl_total.pack(pady=5)

# 4. Nút bấm dừng khẩn cấp (Emergency Stop)
def toggle_system():
    global is_running
    if is_running:
        is_running = False
        btn_emergency.config(text="START SYSTEM", bg="#2ecc71")
        status_label.config(text="HỆ THỐNG DỪNG KHẨN CẤP\n(EMERGENCY STOP)", fg="#e74c3c")
    else:
        is_running = True
        btn_emergency.config(text="EMERGENCY STOP", bg="#e74c3c")
        status_label.config(text="Băng chuyền ổn định\nĐang chờ vật tiếp theo...", fg="#f1c40f")

btn_emergency = tk.Button(control_frame, text="EMERGENCY STOP", font=("Helvetica", 11, "bold"), 
                          fg="white", bg="#e74c3c", activebackground="#c0392b", command=toggle_system, bd=2)
btn_emergency.pack(fill=tk.X, padx=30, pady=10)

# =====================================================================
# BƯỚC 3: XỬ LÝ HÌNH ẢNH VÀ CHU TRÌNH TUẦN HOÀN
# =====================================================================
video_path = 'conveyor_simulation.mp4'
use_simulated_mode = not os.path.exists(video_path)
cap = None if use_simulated_mode else cv2.VideoCapture(video_path)

last_action_time = time.time()
reset_servo_needed = False
sim_x = 0
current_product_counted = False

def update_frame():
    global last_action_time, reset_servo_needed, sim_x, current_product_counted
    global count_plastic, count_paper, count_metal, count_total
    
    current_time = time.time()
    
    # Nếu đang bấm dừng khẩn cấp thì đứng im giữ nguyên màn hình
    if not is_running:
        root.after(30, update_frame)
        return

    # Tự động trả kim về vị trí 90 độ sau 1.3 giây hành động
    if reset_servo_needed and (current_time - last_action_time > 1.3):
        draw_servo_pointer(90)
        status_label.config(text="Băng chuyền ổn định\nĐang chờ vật tiếp theo...", fg="#f1c40f")
        reset_servo_needed = False
        current_product_counted = False

    # CHẾ ĐỘ 1: SỬ DỤNG VIDEO MP4 NẾU CÓ FILE
    if not use_simulated_mode:
        ret, frame = cap.read()
        if not ret:
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            ret, frame = cap.read()
            
        if ret:
            frame_resized = cv2.resize(frame, (620, 440))
            gray = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2GRAY)
            _, thresh = cv2.threshold(cv2.GaussianBlur(gray, (5, 5), 0), 110, 255, cv2.THRESH_BINARY_INV)
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            # TỐI ƯU HÓA: Đưa chuyển đổi HSV ra ngoài vòng lặp contours
            hsv_frame = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2HSV)

            for contour in contours:
                area = cv2.contourArea(contour)
                if area < 2500: continue

                perimeter = cv2.arcLength(contour, True)
                roundness = (4 * np.pi * area) / (perimeter ** 2) if perimeter > 0 else 0
                
                # Trích xuất màu bằng cách tái sử dụng hsv_frame đã tối ưu
                mask = np.zeros(gray.shape, np.uint8)
                cv2.drawContours(mask, [contour], -1, 255, -1)
                mean_hsv = cv2.mean(hsv_frame, mask=mask)
                
                features = np.array([[mean_hsv[0], mean_hsv[1], mean_hsv[2], area, roundness]])
                prediction = model.predict(features)[0]
                label_text = class_labels[prediction]

                x, y, w, h = cv2.boundingRect(contour)
                cv2.rectangle(frame_resized, (x, y), (x + w, y + h), (26, 188, 156), 2)
                cv2.putText(frame_resized, f"AI RECOGNIZED: {label_text}", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (26, 188, 156), 2)

                if current_time - last_action_time > 3:
                    last_action_time = current_time
                    reset_servo_needed = True
                    count_total += 1
                    
                    if prediction == 0:
                        count_plastic += 1
                        lbl_p.config(text=f"Chai Nhựa (Plastic): {count_plastic}")
                        status_label.config(text="ĐANG PHÂN LOẠI: PLASTIC\n-> Robot gạt góc: 45°", fg="#3498db")
                        draw_servo_pointer(45)
                    elif prediction == 1:
                        count_paper += 1
                        lbl_w.config(text=f"Hộp Giấy (Paper):  {count_paper}")
                        status_label.config(text="ĐANG PHÂN LOẠI: PAPER\n-> Robot gạt góc: 135°", fg="#2ecc71")
                        draw_servo_pointer(135)
                    elif prediction == 2:
                        count_metal += 1
                        lbl_m.config(text=f"Kim Loại (Metal):   {count_metal}")
                        status_label.config(text="ĐANG PHÂN LOẠI: METAL\n-> Robot gạt góc: 20°", fg="#e74c3c")
                        draw_servo_pointer(20)
                    
                    lbl_total.config(text=f"TỔNG SẢN PHẨM ĐÃ PHÂN LOẠI: {count_total}")

    # CHẾ ĐỘ 2: TỰ DỰNG SA BÀN BĂNG CHUYỀN ĐỒ HỌA ẢO ĐỂ CHẤM ĐIỂM
    else:
        frame_resized = np.zeros((440, 620, 3), dtype=np.uint8)
        cv2.rectangle(frame_resized, (0, 180), (620, 300), (44, 62, 80), -1) 
        cv2.putText(frame_resized, "INDUSTRIAL AUTOMATION LINE SIMULATOR", (70, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        sim_x += 10
        if sim_x > 620:
            sim_x = 0
            current_product_counted = False
            
        cycle = (int(time.time()) // 10) % 3 
        if cycle == 0:
            cv2.circle(frame_resized, (sim_x, 240), 25, (219, 152, 52), -1) # BGR cho Plastic
            cv2.putText(frame_resized, "TARGET: PLASTIC BOTTLE", (sim_x - 70, 140), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (219, 152, 52), 2)
        elif cycle == 1:
            cv2.rectangle(frame_resized, (sim_x - 25, 215), (sim_x + 25, 265), (46, 204, 113), -1) # BGR cho Paper
            cv2.putText(frame_resized, "TARGET: PAPER BOX", (sim_x - 55, 140), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (46, 204, 113), 2)
        else:
            cv2.rectangle(frame_resized, (sim_x - 20, 220), (sim_x + 20, 260), (231, 76, 60), -1) # BGR cho Metal
            cv2.putText(frame_resized, "TARGET: METAL CAN", (sim_x - 55, 140), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (231, 76, 60), 2)

        if 300 <= sim_x <= 320 and not current_product_counted:
            last_action_time = current_time
            reset_servo_needed = True
            current_product_counted = True
            count_total += 1
            
            if cycle == 0:
                count_plastic += 1
                lbl_p.config(text=f"Chai Nhựa (Plastic): {count_plastic}")
                status_label.config(text="ĐANG PHÂN LOẠI: PLASTIC\n-> Cánh tay gạt: 45°", fg="#3498db")
                draw_servo_pointer(45)
            elif cycle == 1:
                count_paper += 1
                lbl_w.config(text=f"Hộp Giấy (Paper):  {count_paper}")
                status_label.config(text="ĐANG PHÂN LOẠI: PAPER\n-> Cánh tay gạt: 135°", fg="#2ecc71")
                draw_servo_pointer(135)
            else:
                count_metal += 1
                lbl_m.config(text=f"Kim Loại (Metal):   {count_metal}")
                status_label.config(text="ĐANG PHÂN LOẠI: METAL\n-> Cánh tay gạt: 20°", fg="#e74c3c")
                draw_servo_pointer(20)
                
            lbl_total.config(text=f"TỔNG SẢN PHẨM ĐÃ PHÂN LOẠI: {count_total}")

    # Cập nhật ảnh lên khung đồ họa Tkinter thông qua định dạng chuẩn RGBA
    imgtk = ImageTk.PhotoImage(image=Image.fromarray(cv2.cvtColor(frame_resized, cv2.COLOR_BGR2RGBA)))
    video_label.imgtk = imgtk
    video_label.config(image=imgtk)

    root.after(30, update_frame)

# Bắt đầu vòng lặp hệ thống
update_frame()
root.protocol("WM_DELETE_WINDOW", lambda: [cap.release() if cap is not None else None, root.destroy()])
root.mainloop()