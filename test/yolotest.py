import cv2
import torch
import os
import pyautogui
import numpy as np
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
import time
from ultralytics import YOLO

def perform_detection(model, image, output_dir):
    # 記錄開始時間
    start_time = time.time()

    # 將圖像轉換為 (batch, channel, height, width)
    image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    image_resized = cv2.resize(image, (640, 640))  # 確保圖像大小一致
    image_tensor = torch.from_numpy(image_resized).permute(2, 0, 1).unsqueeze(0).float() / 255.0  # 歸一化到 0.0 到 1.0

    # 將圖像轉移到 GPU（如果可用）
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    image_tensor = image_tensor.to(device)

    # 執行檢測
    results = model(image_tensor)

    # 獲取帶有邊界框的圖像
    annotated_image = image.copy()
    person_detected = False

    # 檢查是否有檢測到物體
    if len(results) > 0:
        for result in results:  # 迭代每個檢測到的物體
            if result.boxes.xyxy.shape[0] > 0:  # 檢查是否有檢測到的框
                x1, y1, x2, y2, conf, cls = result.boxes.xyxy[0].tolist() + result.boxes.conf[0].tolist() + result.boxes.cls[0].tolist()
                x1, y1, x2, y2 = map(int, [x1, y1, x2, y2])
                cv2.rectangle(annotated_image, (x1, y1), (x2, y2), (0, 255, 0), 2)  # 畫出邊界框

                # 確保類別索引存在於 model.names 中
                if int(cls) in model.names:
                    label = f'{model.names[int(cls)]}: {conf:.2f}'
                    if model.names[int(cls)] == 'person':
                        person_detected = True
                else:
                    label = f'Class {int(cls)}: {conf:.2f}'

                cv2.putText(annotated_image, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    # 計算處理時間
    end_time = time.time()
    processing_time = end_time - start_time
    print(f"處理時間: {processing_time:.4f} 秒")

    # 如果檢測到人物，保存結果
    if person_detected:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = os.path.join(output_dir, f'screenshot_{timestamp}.png')
        cv2.imwrite(output_file, annotated_image)
        print(f"檢測結果已保存到 '{output_file}'")

    return annotated_image

def load_model():
    # 定義和初始化 YOLOv8 模型
    model_path = r'..\yolov8\runs\detect\train\weights\best.pt'  # 使用原始字符串來避免轉義字符問題
    model = YOLO(model_path)  # 使用 YOLOv8n 模型，你可以根據需要選擇其他版本
    return model

def main():
    # 確認輸出資料夾存在
    output_dir = os.path.join('recognition', 'img')
    os.makedirs(output_dir, exist_ok=True)

    # 加載模型
    model = load_model()

    # 使用多執行緒進行檢測
    with ThreadPoolExecutor(max_workers=4) as executor:
        while True:
            start_time = time.time()

            # 截圖螢幕
            screenshot = pyautogui.screenshot()

            # 提交檢測任務
            future = executor.submit(perform_detection, model, screenshot, output_dir)
            annotated_image = future.result()

            # 計算並顯示 FPS
            end_time = time.time()
            fps = 1 / (end_time - start_time)
            print(f"FPS: {fps:.2f}")

            # 確保至少 1000 FPS
            time.sleep(max(0, 1/1000 - (end_time - start_time)))

if __name__ == "__main__":
    main()