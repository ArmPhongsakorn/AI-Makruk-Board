import serial
import time

# ???????????????????????? ???? /dev/ttyUSB0 ???? /dev/ttyACM0
PORT = "/dev/ttyUSB0"
BAUD = 115200

ser = serial.Serial(PORT, BAUD, timeout=1)
time.sleep(2)  # ?? ESP32 ??????

def send_message_to_lcd(msg):
    ser.write((msg + "\n").encode())
    print("[Sent to LCD] >", msg)
    response = ser.readline().decode().strip()
    if response == "OK":
        print("[ESP32] LCD updated")
    else:
        print("[ESP32] No ACK")

def request_sensor_values():
    ser.write(b"R\n")
    while True:
        line = ser.readline().decode().strip()
        if line.startswith("Sensors:"):
            print("[Sensor Values] >", line)
            break

if __name__ == "__main__":
    print("Testing serial communication...")

    # ???????????????
    send_message_to_lcd("g8e7")

    time.sleep(1)

    # ????????????? sensors
    request_sensor_values()