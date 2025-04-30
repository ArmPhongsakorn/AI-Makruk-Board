#include <Wire.h>
#include <LiquidCrystal_I2C.h>

#define NUM_SENSORS 16
int sensorPins[NUM_SENSORS] = {15, 13, 2, 12, 0, 14, 4, 27, 16, 26, 17, 25, 5, 33, 18, 32};

LiquidCrystal_I2C lcd(0x27, 16, 2); // I2C LCD

void setup() {
  Serial.begin(115200);

  // Init sensors
  for (int i = 0; i < NUM_SENSORS; i++) {
    pinMode(sensorPins[i], INPUT);
  }

  // Init LCD
  lcd.init();
  lcd.backlight();
  lcd.print("ESP Ready!");
}

void loop() {
  if (Serial.available()) {
    String command = Serial.readStringUntil('\n');
    command.trim(); // remove \r\n if any

    if (command == "R") {
      // ??????????????????????????? Pi
      Serial.print("Sensors: ");
      for (int i = 0; i < NUM_SENSORS; i++) {
        Serial.print(digitalRead(sensorPins[i]));
        if (i < NUM_SENSORS - 1) Serial.print(",");
      }
      Serial.println();
    } else {
      // ????????????? LCD
      lcd.clear();
      lcd.setCursor(0, 0);
      lcd.print("Msg from Pi:");
      lcd.setCursor(0, 1);
      lcd.print(command); // ?????????????? Pi
      Serial.println("OK"); // ???? Pi ??? LCD ???????????????
    }
  }
}
