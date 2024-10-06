#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <Mouse.h>

LiquidCrystal_I2C lcd(0x27, 16, 2);  // 設定 LCD 地址和尺寸

unsigned long lastActivityTime = 0;  // 上次活動時間
const unsigned long idleTimeout = 5000;  // 待機超時時間 (毫秒)

void setup() {
  Serial.begin(9600);
  Mouse.begin();
  lcd.begin(16, 2);  // 提供列數和行數
  lcd.backlight();
  lcd.setCursor(0, 0);
  lcd.print("Waiting for data");
}

void loop() {
  if (Serial.available() > 0) {
    String data = Serial.readStringUntil('\n');
    
    if (data == "HELLO") {
      Serial.println("HELLO");  // 回應 HELLO
    } else {
      // 找出每個逗號和括號的索引
      int firstCommaIndex = data.indexOf(',');
      int secondCommaIndex = data.indexOf(',', firstCommaIndex + 1);
      int thirdCommaIndex = data.indexOf(',', secondCommaIndex + 1);
      int fourthCommaIndex = data.indexOf(',', thirdCommaIndex + 1);

      // 解析座標
      int currentX = data.substring(1, firstCommaIndex).toInt();
      int currentY = data.substring(firstCommaIndex + 1, secondCommaIndex).toInt();
      int targetX = data.substring(thirdCommaIndex + 2, fourthCommaIndex).toInt();
      int targetY = data.substring(fourthCommaIndex + 1, data.length() - 1).toInt();

      // 移動滑鼠到目標位置
      moveMouseTo(currentX, currentY, targetX, targetY);
      
      // 回傳相同的資料
      Serial.println(data);
      
      // 更新 LCD
      lcd.clear();
      lcd.setCursor(0, 0);
      lcd.print("X: ");
      lcd.print(targetX);
      lcd.setCursor(0, 1);
      lcd.print("Y: ");
      lcd.print(targetY);
      
      lastActivityTime = millis();  // 更新上次活動時間
    }
  }

  // 檢查是否超過待機超時時間
  if (millis() - lastActivityTime > idleTimeout) {
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("Idle");
    lcd.setCursor(0, 1);
    lcd.print("Waiting...");
    lastActivityTime = millis();  // 更新上次活動時間以避免重複清屏
  }
}

void moveMouseTo(int currentX, int currentY, int targetX, int targetY) {
  int stepX = (targetX - currentX) / 10;  // 將移動分成 10 步
  int stepY = (targetY - currentY) / 10;  // 將移動分成 10 步

  for (int i = 0; i < 10; i++) {
    Mouse.move(stepX, stepY);
    delay(50);  // 每步之間添加延遲
  }

  // 最後一步確保到達目標位置
  Mouse.move(targetX - currentX - stepX * 9, targetY - currentY - stepY * 9);
}
