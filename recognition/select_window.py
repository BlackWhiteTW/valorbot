import pygetwindow as gw
from recognition.capture import capture_screen
import cv2
from capture import capture_screen

def list_windows():
    """列出所有當前打開的視窗標題"""
    windows = gw.getAllTitles()
    print("目前開啟的視窗標題:")
    for i, window in enumerate(windows):
        if window.strip():  # 檢查視窗標題是否為空或僅包含空格
            print(f"{i}: {window}")
    return windows

def select_window():
    """選擇視窗並擷取截圖"""
    windows = list_windows()
    try:
        index = int(input("請選擇一個視窗的序號："))
        if 0 <= index < len(windows):
            window_title = windows[index]
            print(f"你選擇的視窗是: {window_title}")

            # 使用指定的視窗標題擷取截圖
            image = capture_screen(window_title)

            if image is not None:
                # 保存截圖
                cv2.imwrite('recognition/img/captured_image.png', image)
                print("截圖已保存為 'recognition/img/captured_image.png'")
            else:
                print("無法擷取截圖。")
        else:
            print("選擇的序號無效。")
    except ValueError:
        print("無效的序號輸入。")

if __name__ == "__main__":
    list_windows()
