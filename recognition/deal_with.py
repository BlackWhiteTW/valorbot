import cv2
import numpy as np

def detect_and_save_person(image):
    """檢測圖像中的人形，並將結果儲存到新檔案"""
    # 讀取預訓練的人形檢測模型
    hog = cv2.HOGDescriptor()
    hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

    # 使用 HOG 模型檢測圖像中的人形
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    boxes, weights = hog.detectMultiScale(gray_image, winStride=(8, 8), padding=(2, 2), scale=1.05)

    # 如果檢測到人形，將其框起來並儲存結果
    if len(boxes) > 0:
        for (x, y, w, h) in boxes:
            cv2.rectangle(image, (x, y), (x+w, y+h), (0, 255, 0), 2)
        # 儲存帶有檢測結果的圖像
        output_file = 'recognition/img/deal.png'
        cv2.imwrite(output_file, image)
        print(f"檢測結果已保存為 '{output_file}'")
    else:
        print("未檢測到人形")

if __name__ == "__main__":
    # 讀取截圖圖像
    input_image_path = 'recognition/img/image.png'
    image = cv2.imread(input_image_path)

    if image is not None:
        # 保存截圖
        captured_image_path = 'recognition/img/captured_image.png'
        cv2.imwrite(captured_image_path, image)
        print(f"截圖已保存為 '{captured_image_path}'")
    
        # 顯示原始圖像
        cv2.imshow('Original Image', image)
        cv2.waitKey(0)  # 等待按鍵事件
        cv2.destroyAllWindows()

        # 檢測並保存人像
        detect_and_save_person(image)

        # 讀取處理後的圖像
        processed_image_path = 'recognition/img/deal.png'
        processed_image = cv2.imread(processed_image_path)

        if processed_image is not None:
            # 顯示處理後的圖像
            cv2.imshow('Processed Image', processed_image)
            cv2.waitKey(0)  # 等待按鍵事件
            cv2.destroyAllWindows()
        else:
            print("無法讀取處理後的圖像")
    else:
        print("無法擷取截圖。")
