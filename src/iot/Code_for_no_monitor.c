//#include <WiFi.h>
//
//void setup() {
//  Serial.begin(115200);
//  Serial.println();
//  Serial.print("ESP32 Mac Address: ");
//  Serial.println(WiFi.macAddress());
//}
//void loop() {
//  
//}
#include <WiFi.h>
#define NUM_SENSORS 16
int sensorPins[NUM_SENSORS] = {15, 35, 19, 34, 0, 14, 21, 27, 16 , 26, 17, 25, 5, 33, 18, 32};


void setup() {
  delay(500);
  Serial.print("MAC:");
  Serial.println(WiFi.macAddress());
  Serial.begin(115200);
  delay(500);
  Serial.flush();
  while(Serial.available()) {
    Serial.read();
  }
  Serial.println("ESP32 restarted and ready");
  
  // start sensors
  delay(1000);
  for (int i = 0; i < NUM_SENSORS; i++) {
    pinMode(sensorPins[i], INPUT);
  }
}

void loop() {
  // ?????????????????????? Pi ???????
  if (Serial.available() > 0) {
    char command = Serial.read();
    if (command == 'R') { // Raspberry Pi ??? 'R' ???????????????
      Serial.print("Sensor values: ");
      for (int i = 0; i < NUM_SENSORS; i++) {
        int value = digitalRead(sensorPins[i]);
        Serial.print(value);
        Serial.print(" ");
      }
      Serial.println();
    }
  }
}