import win32gui
import win32con
import pyautogui
import numpy as np
import cv2
import time
import os

def bring_window_to_foreground(hwnd):
    """將視窗恢復並置於前景"""
    try:
        if win32gui.IsIconic(hwnd):
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)

        win32gui.ShowWindow(hwnd, win32con.SW_SHOW)
        win32gui.BringWindowToTop(hwnd)  # 使用 BringWindowToTop
        win32gui.SetForegroundWindow(hwnd)
    except Exception as e:
        print(f"將視窗置於前景時發生錯誤：{e}")

def capture_window(window_title):
    try:
        hwnd = win32gui.FindWindow(None, window_title)
        if not hwnd:
            print(f"找不到視窗 '{window_title}'")
            return None

        bring_window_to_foreground(hwnd)

        left, top, right, bottom = win32gui.GetWindowRect(hwnd)
        width = right - left
        height = bottom - top

        print(f"窗口位置: {left}, {top}, {right}, {bottom}")
        print(f"窗口大小: {width} x {height}")

        # 使用 pyautogui 擷取整個屏幕
        screenshot = pyautogui.screenshot()
        screenshot_np = np.array(screenshot)

        # 裁剪指定區域
        image = screenshot_np[top:top+height, left:left+width]

        if image.size == 0 or np.all(image == 0):
            print("截圖結果為全黑圖像")
            return None

        return cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    except Exception as e:
        print(f"擷取視窗內容時發生錯誤：{e}")
        return None

def save_screenshot(image, directory='recognition/img'):
    """保存截圖到指定目錄"""
    try:
        if image is not None:
            if not os.path.exists(directory):
                os.makedirs(directory)
            filename = os.path.join(directory, 'image.png')
            cv2.imwrite(filename, image)
            print(f"截圖已保存到: {filename}")
        else:
            print("沒有可保存的截圖。")
    except Exception as e:
        print(f"保存截圖時發生錯誤：{e}")

def capture_screen(window_title):
    """根據視窗標題截圖"""
    image = capture_window(window_title)
    if image is None:
        print("無法擷取視窗截圖，請檢查視窗內容或位置。")
    else:
        save_screenshot(image)
    return image

if __name__ == "__main__":
    window_title = input("輸入要截圖的視窗標題: ")
    capture_screen(window_title)
