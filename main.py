import sys
import os
import subprocess

# 添加 'recognition' 資料夾到 sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'recognition')))

import cv2
from recognition.capture import capture_screen
from recognition.select_window import list_windows


def main():
    # 列出視窗並選擇一個
    windows = list_windows()
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

if __name__ == "__main__":
    main()