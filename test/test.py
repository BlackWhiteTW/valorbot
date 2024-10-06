import cv2
import torch
import os
import numpy as np
import time
from ultralytics import YOLO
import win32gui
import win32ui
import win32con
import win32api

def get_window_rect(window_name):
    hwnd = win32gui.FindWindow(None, window_name)
    if hwnd:
        rect = win32gui.GetWindowRect(hwnd)
        return rect
    else:
        raise Exception(f"Window with name '{window_name}' not found")

def capture_window(window_name):
    rect = get_window_rect(window_name)
    x1, y1, x2, y2 = rect
    width = x2 - x1
    height = y2 - y1

    hwnd = win32gui.FindWindow(None, window_name)
    wDC = win32gui.GetWindowDC(hwnd)
    dcObj = win32ui.CreateDCFromHandle(wDC)
    cDC = dcObj.CreateCompatibleDC()
    dataBitMap = win32ui.CreateBitmap()
    dataBitMap.CreateCompatibleBitmap(dcObj, width, height)
    cDC.SelectObject(dataBitMap)
    cDC.BitBlt((0, 0), (width, height), dcObj, (0, 0), win32con.SRCCOPY)

    signedIntsArray = dataBitMap.GetBitmapBits(True)
    img = np.frombuffer(signedIntsArray, dtype='uint8')
    img.shape = (height, width, 4)

    dcObj.DeleteDC()
    cDC.DeleteDC()
    win32gui.ReleaseDC(hwnd, wDC)
    win32gui.DeleteObject(dataBitMap.GetHandle())

    img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
    return img

def list_windows():
    def enum_handler(hwnd, result):
        if win32gui.IsWindowVisible(hwnd):
            window_text = win32gui.GetWindowText(hwnd)
            if window_text:
                result.append(window_text)
    windows = []
    win32gui.EnumWindows(enum_handler, windows)
    return windows

def perform_detection(model, image):
    # 將圖像轉換為 (batch, channel, height, width)
    image_resized = cv2.resize(image, (640, 640))  # 確保圖像大小一致
    image_tensor = torch.from_numpy(image_resized).permute(2, 0, 1).unsqueeze(0).float() / 255.0  # 歸一化到 0.0 到 1.0

    # 將圖像轉移到 GPU（如果可用）
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    image_tensor = image_tensor.to(device)

    # 執行檢測
    results = model(image_tensor)

    # 獲取帶有邊界框的圖像
    annotated_image = image.copy()

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
                else:
                    label = f'Class {int(cls)}: {conf:.2f}'

                cv2.putText(annotated_image, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    return annotated_image

def load_model():
    # 定義和初始化 YOLOv8 模型
    model_path = r'\..\yolov8\runs\detect\train\weights\best.pt'  # 更新為你的模型權重文件的正確路徑
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"{model_path} does not exist")
    model = YOLO(model_path)  # 使用 YOLOv8n 模型，你可以根據需要選擇其他版本
    return model

def main():
    # 加載模型
    try:
        model = load_model()
    except FileNotFoundError as e:
        print(e)
        return

    # 列出所有可選擇的應用程式窗口
    windows = list_windows()
    print("可選擇的應用程式窗口:")
    for i, window in enumerate(windows):
        print(f"{i + 1}. {window}")

    # 輸入應用程式名稱
    window_index = int(input("請輸入應用程式編號: ")) - 1
    window_name = windows[window_index]

    while True:
        start_time = time.time()

        # 截圖應用程式窗口
        screenshot = capture_window(window_name)

        # 執行檢測
        annotated_image = perform_detection(model, screenshot)

        # 顯示結果
        cv2.imshow('YOLOv8 Detection', annotated_image)

        # 計算並顯示 FPS
        end_time = time.time()
        fps = 1 / (end_time - start_time)
        print(f"FPS: {fps:.2f}")

        # 按 'q' 鍵退出
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()