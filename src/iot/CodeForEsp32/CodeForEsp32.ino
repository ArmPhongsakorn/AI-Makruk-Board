//
//#include <Wire.h>
//#include <LiquidCrystal_I2C.h>
//
//#define NUM_SENSORS 16
//int sensorPins[NUM_SENSORS] = {15, 13, 2, 12, 0, 14, 4, 27, 16 , 26, 17, 25, 5, 33, 18, 32};
//
//LiquidCrystal_I2C lcd(0x27, 16, 2); // I2C LCD
//
//String receivedMessage = "";
//boolean messageComplete = false;
//
//void setup() {
//  Serial.begin(115200);
//  for (int i = 0; i < NUM_SENSORS; i++) {
//    pinMode(sensorPins[i], INPUT);
//  }
//
//  // Init LCD
//  lcd.init();
//  lcd.backlight();
//  lcd.print("ESP Ready!");
//  lcd.setCursor(0, 1);
//  lcd.print("Waiting for msg...");
//}
//
//void loop() {
//  // ????????????? Raspberry Pi
//  while (Serial.available() > 0) {
//    char inChar = Serial.read();
//    
//    // ?????? 'R' ???????????????????????? (????????????)
//    if (inChar == 'R') {
//      Serial.print("Sensor values: ");
//      for (int i = 0; i < NUM_SENSORS; i++) {
//        int value = digitalRead(sensorPins[i]);
//        Serial.print(value);
//        Serial.print(" ");
//      }
//      Serial.println();
//      continue; // ????????????????
//    }
//    
//    // ??????????????????????? ?????????????????????
//    if (inChar == '\n') {
//      messageComplete = true;
//      break;
//    }
//    
//    // ????????????????????????????
//    receivedMessage += inChar;
//  }
//  
//  // ???????????????? ????????? LCD
//  if (messageComplete) {
//    // ????????????? LCD
//    lcd.clear();
//    
//    // ?????????????????? 16 ???????? ??????????????????
//    if (receivedMessage.length() <= 16) {
//      lcd.setCursor(0, 0);
//      lcd.print(receivedMessage);
//    } else {
//      // ????????????????? 16 ???????? ???????? 2 ??????
//      lcd.setCursor(0, 0);
//      lcd.print(receivedMessage.substring(0, 16));
//      lcd.setCursor(0, 1);
//      
//      // ????????????????????????????? 16 ????????
//      int endPos = receivedMessage.length();
//      if (endPos > 32) endPos = 32;
//      lcd.print(receivedMessage.substring(16, endPos));
//    }
//    
//    // ????????????????????? Raspberry Pi
//    Serial.print("Message received: ");
//    Serial.println(receivedMessage);
//    
//    // ?????????????
//    receivedMessage = "";
//    messageComplete = false;
//  }
//}

//#include <Wire.h>
//#include <LiquidCrystal_I2C.h>
//
//#define NUM_SENSORS 16
//#define POT_PIN 34  // ??????? GPIO34 ?????? potentiometer
//
//int sensorPins[NUM_SENSORS] = {15, 13, 2, 12, 0, 14, 4, 27, 16, 26, 17, 25, 5, 33, 18, 32};
//int potValue = 0;  // ????????????? potentiometer
//
//LiquidCrystal_I2C lcd(0x27, 16, 2); // I2C LCD
//String receivedMessage = "";
//boolean messageComplete = false;
//
//void setup() {
//  Serial.begin(115200);
//  
//  // ????????? input
//  for (int i = 0; i < NUM_SENSORS; i++) {
//    pinMode(sensorPins[i], INPUT);
//  }
//  pinMode(POT_PIN, INPUT);  // ????????? potentiometer ???? input
//  
//  // Init LCD
//  lcd.init();
//  lcd.backlight();
//  lcd.print("ESP Ready!");
//  lcd.setCursor(0, 1);
//  lcd.print("Waiting for msg...");
//}
//
//void loop() {
//  // ??????? potentiometer
//  potValue = analogRead(POT_PIN);
//  // ?????????? 0-4095 ???? 0-20 (?????? ESP32 ADC ?? resolution 12 bit ??? 0-4095)
//  int engineLevel = map(potValue, 0, 4095, 0, 20);
//  
//  // ???????????? Raspberry Pi
//  while (Serial.available() > 0) {
//    char inChar = Serial.read();
//    
//    // ????????????? 'R' ????????????????????
//    if (inChar == 'R') {
//      Serial.print("Sensor values: ");
//      for (int i = 0; i < NUM_SENSORS; i++) {
//        int value = digitalRead(sensorPins[i]);
//        Serial.print(value);
//        Serial.print(" ");
//      }
//      Serial.println();
//      continue;
//    }
//    
//    // ????????????? 'L' ??????????? potentiometer ??????
//    if (inChar == 'L') {
//      Serial.print("Engine's level: ");
//      Serial.println(engineLevel);
//      continue;
//    }
//    
//    // ???????????????????
//    if (inChar == '\n') {
//      messageComplete = true;
//      break;
//    }
//    
//    // ??????????????????????????
//    receivedMessage += inChar;
//  }
//  
//  // ??????? potentiometer ?? LCD
//  lcd.setCursor(0, 1);
//  lcd.print("Engine lvl: ");
//  lcd.print(engineLevel);
//  lcd.print("   ");  // ??????????????????????????????????
//  
//  // ??????????????????? ?????? LCD
//  if (messageComplete) {
//    // ???????????????? LCD
//    lcd.setCursor(0, 0);
//    lcd.print("                ");  // 16 ????????
//    lcd.setCursor(0, 0);
//    
//    // ?????????????????? 16 ???????? ???????????
//    if (receivedMessage.length() <= 16) {
//      lcd.print(receivedMessage);
//    } else {
//      // ????????????????? 16 ???????? ??????????????? 16 ??????
//      lcd.print(receivedMessage.substring(0, 16));
//    }
//    
//    // ????????????????????? Raspberry Pi
//    Serial.print("Message received: ");
//    Serial.println(receivedMessage);
//    
//    // ?????????????
//    receivedMessage = "";
//    messageComplete = false;
//  }
//  
//  delay(100);  // ????????????????????????????????
//}

#include <Wire.h>
#include <LiquidCrystal_I2C.h>

#define NUM_SENSORS 16
#define POT_PIN 34 // Define GPIO34 for potentiometer

int sensorPins[NUM_SENSORS] = {15, 13, 2, 12, 0, 14, 4, 27, 16, 26, 17, 25, 5, 33, 18, 32};
int potValue = 0; // Variable to store potentiometer value
int engineLevel = 0; // Current engine level
bool inSelectionMode = false; // Flag to track if we're in engine level selection mode

LiquidCrystal_I2C lcd(0x27, 16, 2); // I2C LCD
String receivedMessage = "";
boolean messageComplete = false;

void setup() {
  Serial.begin(115200);

  // Set sensor pins as input
  for (int i = 0; i < NUM_SENSORS; i++) {
    pinMode(sensorPins[i], INPUT);
  }
  pinMode(POT_PIN, INPUT); // Set potentiometer pin as input

  // Initialize LCD
  lcd.init();
  lcd.backlight();
  lcd.print("ESP Ready!");
  lcd.setCursor(0, 1);
  lcd.print("Waiting for msg...");
}

void loop() {
  // Read potentiometer value
  potValue = analogRead(POT_PIN);
  // Map value from 0-4095 to 0-20 (ESP32 ADC resolution is 12-bit)
  engineLevel = map(potValue, 0, 4095, 0, 20);

  // If in selection mode, continuously update the display
  if (inSelectionMode) {
    displayEngineLevel(engineLevel);
  }

  // Receive data from Raspberry Pi
  while (Serial.available() > 0) {
    char inChar = Serial.read();

    // Check for command 'R' to send sensor values
    if (inChar == 'R') {
      Serial.print("Sensor values: ");
      for (int i = 0; i < NUM_SENSORS; i++) {
        int value = digitalRead(sensorPins[i]);
        Serial.print(value);
        Serial.print(" ");
      }
      Serial.println();
      continue;
    }

    // Check for command 'S' to enter engine level selection mode
    if (inChar == 'S') {
      inSelectionMode = true;
      Serial.println("Entered selection mode");
      displayEngineLevel(engineLevel);
      continue;
    }

    // Check for command 'L' to confirm the level and exit selection mode
    if (inChar == 'L') {
      if (inSelectionMode) {
        inSelectionMode = false;
        Serial.print("Engine level confirmed: ");
        Serial.println(engineLevel);
        
        // Display confirmation on LCD
        lcd.clear();
        lcd.setCursor(0, 0);
        lcd.print("Level confirmed:");
        lcd.setCursor(0, 1);
        lcd.print("Engine lvl: ");
        lcd.print(engineLevel);
        
        delay(2000); // Show confirmation for 2 seconds
        
      } else {
        // If not in selection mode, just send the current level
        Serial.print("Engine's level: ");
        Serial.println(engineLevel);
      }
      continue;
    }

    // Check for end of message
    if (inChar == '\n') {
      messageComplete = true;
      break;
    }

    // Append character to message buffer
    receivedMessage += inChar;
  }

  // If message is complete and not in selection mode, display on LCD
  if (messageComplete && !inSelectionMode) {
    lcd.clear();
    // Display the text on the first line (characters 1-16)
    lcd.setCursor(0, 0);
    if (receivedMessage.length() <= 16) {
      // If the message is less than or equal to 16 characters, display all on the first line.
      lcd.print(receivedMessage);
    } else {
      // If the message is longer than 16 characters, display the first 16 characters on the first line.
      lcd.print(receivedMessage.substring(0, 16));
      
      // Displays the remaining characters on the second line (characters 17-32).
      lcd.setCursor(0, 1);
      // Check if the message exceeds 32 characters.
      int remainingLength = receivedMessage.length() - 16;
      if (remainingLength > 16) {
        remainingLength = 16; // Limit to 16 characters on the second line.
      }
      lcd.print(receivedMessage.substring(16, 16 + remainingLength));
    }

    // Send acknowledgment back to Raspberry Pi
    Serial.print("Message received: ");
    Serial.println(receivedMessage);

    // Reset message buffer
    receivedMessage = "";
    messageComplete = false;
  } else if (messageComplete && inSelectionMode) {
    lcd.clear();
    // If in selection mode, just acknowledge the message but don't change the display
    Serial.print("Message received (in selection mode): ");
    Serial.println(receivedMessage);
    receivedMessage = "";
    messageComplete = false;
  }

  delay(100); // Small delay for stability
}

// Function to display engine level on LCD (both lines)
void displayEngineLevel(int level) {
  lcd.setCursor(0, 0); // Set cursor to the first row (row 0)
  lcd.print("Choose level    ");
  lcd.setCursor(0, 1); // Set cursor to the second row (row 1)
  lcd.print("Engine lvl: ");
  lcd.print(level);
  lcd.print("   "); // Add spaces to clear old characters
}
