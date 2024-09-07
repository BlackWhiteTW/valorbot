import cv2
import mediapipe as mp
import os
import time
import numpy as np
import ctypes
from PIL import ImageGrab
import serial
import serial.tools.list_ports

mp_pose = mp.solutions.pose
pose = mp_pose.Pose()
mp_drawing = mp.solutions.drawing_utils

# 初始化成功辨識次數計數器
success_count = 0

def detect_arduino_port():
    """自動偵測 Arduino 所連接的串口"""
    ports = list(serial.tools.list_ports.comports())
    for port in ports:
        try:
            ser = serial.Serial(port.device, 9600, timeout=1)
            ser.write(b'Hello Arduino\n')
            time.sleep(2)  # 等待 Arduino 重置
            if ser.in_waiting > 0:
                response = ser.readline().decode('utf-8').strip()
                if response == 'Hello Python':
                    ser.close()
                    return port.device
            ser.close()
        except (OSError, serial.SerialException):
            pass
    return None

# 初始化串口通信
arduino_port = detect_arduino_port()
if arduino_port:
    ser = serial.Serial(arduino_port, 9600)
    print(f"Arduino 已連接到 {arduino_port}")
else:
    raise Exception("未能找到 Arduino")

def detect_pose(image):
    """檢測圖像中的人體架構，並返回頭部的關鍵點座標"""
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = pose.process(image_rgb)
    landmarks = results.pose_landmarks

    head_points = {}
    if landmarks:
        image_height, image_width, _ = image.shape
        # 提取頭部的關鍵點座標，並轉換為像素座標
        head_points['nose'] = (int(landmarks.landmark[mp_pose.PoseLandmark.NOSE].x * image_width),
                               int(landmarks.landmark[mp_pose.PoseLandmark.NOSE].y * image_height))
        head_points['left_eye'] = (int(landmarks.landmark[mp_pose.PoseLandmark.LEFT_EYE].x * image_width),
                                   int(landmarks.landmark[mp_pose.PoseLandmark.LEFT_EYE].y * image_height))
        head_points['right_eye'] = (int(landmarks.landmark[mp_pose.PoseLandmark.RIGHT_EYE].x * image_width),
                                    int(landmarks.landmark[mp_pose.PoseLandmark.RIGHT_EYE].y * image_height))
        head_points['left_ear'] = (int(landmarks.landmark[mp_pose.PoseLandmark.LEFT_EAR].x * image_width),
                                   int(landmarks.landmark[mp_pose.PoseLandmark.LEFT_EAR].y * image_height))
        head_points['right_ear'] = (int(landmarks.landmark[mp_pose.PoseLandmark.RIGHT_EAR].x * image_width),
                                    int(landmarks.landmark[mp_pose.PoseLandmark.RIGHT_EAR].y * image_height))
    
    return landmarks, head_points

def draw_pose(image, landmarks, head_points, is_target):
    """在圖像上繪製人體架構並標出頭部中心點和綠色框"""
    # 計算頭部中心點
    center_x, center_y = None, None
    if head_points:
        x_coords = [coord[0] for coord in head_points.values()]
        y_coords = [coord[1] for coord in head_points.values()]
        center_x = int(sum(x_coords) / len(x_coords))
        center_y = int(sum(y_coords) / len(y_coords))
        
        # 在圖像上繪製頭部紅色點
        cv2.circle(image, (center_x, center_y), 5, (0, 0, 255), -1)
    
    # 繪製綠色的框框住整個身體
    if landmarks:
        x_coords = [int(landmark.x * image.shape[1]) for landmark in landmarks.landmark]
        y_coords = [int(landmark.y * image.shape[0]) for landmark in landmarks.landmark]
        min_x, max_x = min(x_coords), max(x_coords)
        min_y, max_y = min(y_coords), max(y_coords)
        cv2.rectangle(image, (min_x, min_y), (max_x, max_y), (0, 255, 0), 2)
        
        # 如果是目標人像，繪製部分紅框
        if is_target:
            cv2.rectangle(image, (min_x, min_y), (max_x, max_y), (0, 0, 255), 2)
    
    return image, (center_x, center_y) if is_target else None

def convert_to_screen_coordinates(head_points, screen_width, screen_height, image_width, image_height):
    """將頭部關鍵點座標轉換為螢幕上的像素座標"""
    screen_points = {}
    for point, (x, y) in head_points.items():
        screen_x = int(x * screen_width / image_width)
        screen_y = int(y * screen_height / image_height)
        screen_points[point] = (screen_x, screen_y)
    return screen_points

def capture_screenshot():
    """捕捉螢幕畫面並轉換為OpenCV格式"""
    screenshot = ImageGrab.grab()
    screenshot = np.array(screenshot)
    screenshot = cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR)
    return screenshot

def is_target_person(image, landmarks):
    """判斷是否為目標人像"""
    if not landmarks:
        return False

    # 將圖像轉換為 HSV 色彩空間
    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # 定義紅色的 HSV 範圍
    lower_red = np.array([0, 120, 70])
    upper_red = np.array([10, 255, 255])
    mask1 = cv2.inRange(hsv_image, lower_red, upper_red)

    lower_red = np.array([170, 120, 70])
    upper_red = np.array([180, 255, 255])
    mask2 = cv2.inRange(hsv_image, lower_red, upper_red)

    # 合併兩個紅色範圍的掩碼
    red_mask = mask1 + mask2

    # 找到紅色區域的輪廓
    contours, _ = cv2.findContours(red_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # 獲取人體框的邊界
    x_coords = [int(landmark.x * image.shape[1]) for landmark in landmarks.landmark]
    y_coords = [int(landmark.y * image.shape[0]) for landmark in landmarks.landmark]
    min_x, max_x = min(x_coords), max(x_coords)
    min_y, max_y = min(y_coords), max(y_coords)

    # 檢查紅色區域是否在人體框內
    for contour in contours:
        for point in contour:
            x, y = point[0]
            if min_x <= x <= max_x and min_y <= y <= max_y:
                return True

    return False

def send_position_to_arduino(x, y):
    """通過串口將位置發送給 Arduino"""
    position_str = f"{x},{y}\n"
    ser.write(position_str.encode())

def main():
    global success_count
    while True:
        # 捕捉螢幕畫面
        image = capture_screenshot()
        
        # 檢測人體姿態
        landmarks, head_points = detect_pose(image)
        is_target = is_target_person(landmarks) if landmarks else False
        output_image, target_position = draw_pose(image, landmarks, head_points, is_target)
        
        # 儲存結果圖像
        output_path = "testtest_pose.png"
        cv2.imwrite(output_path, output_image)
        print(f"人體架構檢測結果已保存為 '{output_path}'")
        
        # 獲取螢幕解析度
        screen_width = ctypes.windll.user32.GetSystemMetrics(0)
        screen_height = ctypes.windll.user32.GetSystemMetrics(1)
        image_height, image_width, _ = image.shape
        screen_points = convert_to_screen_coordinates(head_points, screen_width, screen_height, image_width, image_height)
        
        print("頭部關鍵點座標（螢幕像素）：")
        for point, coords in screen_points.items():
            print(f"{point}: {coords}")
        
        # 如果找到目標人像，移動鼠標到頭部中心點
        if target_position:
            # 更新成功辨識次數
            success_count += 1
            
            # 確保 test 資料夾存在
            if not os.path.exists("test"):
                os.makedirs("test")
            
            # 儲存結果圖像
            output_path = f"test/test{success_count}.png"
            cv2.imwrite(output_path, output_image)
            print(f"人體架構檢測結果已保存為 '{output_path}'")
            
            screen_x = int(target_position[0] * screen_width / image_width)
            screen_y = int(target_position[1] * screen_height / image_height)
            print(f"移動鼠標到螢幕座標: ({screen_x}, {screen_y})")
            send_position_to_arduino(screen_x, screen_y)  # 發送位置給 Arduino
            print(f"位置已發送給 Arduino: ({screen_x}, {screen_y})")
        
        # 等待一段時間後再次捕捉
        time.sleep(0.1)  # 每隔0.1秒捕捉一次

if __name__ == "__main__":
    main()