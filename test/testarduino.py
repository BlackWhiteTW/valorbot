import serial
import time
from serial.tools import list_ports
import pyautogui

def find_arduino():
    ports = list_ports.comports()
    print("Available COM ports:")
    for port in ports:
        print(f" - {port.device}")
    
    for port in ports:
        try:
            print(f"Trying to connect to {port.device}...")
            ser = serial.Serial(port.device, 9600)
            time.sleep(2)  # 等待串口連接
            ser.write(b'HELLO\n')  # 發送測試訊息
            response = ser.readline().decode().strip()
            print(f"Response from {port.device}: {response}")
            if response == 'HELLO':
                print(f"Connected to Arduino on port: {port.device}")
                return ser
            ser.close()
        except (OSError, serial.SerialException) as e:
            print(f"Error connecting to {port.device}: {e}")
        except PermissionError as e:
            print(f"Permission error on {port.device}: {e}")
    raise Exception("Arduino not found")

try:
    # 自動尋找 Arduino 串口
    ser = find_arduino()

    # 等待 Arduino 重置完成
    time.sleep(2)

    for i in range(5):
        # 獲取當前滑鼠位置
        current_position = pyautogui.position()
        target_position = (960, 540)  # 目標位置

        # 格式化座標為五位數字
        current_x_str = f"{current_position.x:05d}"
        current_y_str = f"{current_position.y:05d}"
        target_x_str = f"{target_position[0]:05d}"
        target_y_str = f"{target_position[1]:05d}"

        data = f"({current_x_str},{current_y_str}),({target_x_str},{target_y_str})\n"
        print(f"Sending data to Arduino: {data}")
        ser.write(data.encode())

        # 讀取 Arduino 回傳的訊息
        response = ser.readline().decode().strip()
        if response == data.strip():
            print(f"Arduino echoed the data: {response}")
        else:
            print(f"Unexpected response from Arduino: {response}")

        # 等待一段時間以確保每次移動都能被正確處理
        time.sleep(1)

finally:
    # 確保在程式結束時關閉串口
    if 'ser' in locals() and ser.is_open:
        ser.close()
        print("Serial port closed.")