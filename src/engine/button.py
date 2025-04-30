import RPi.GPIO as GPIO
import time
import subprocess
import psutil
import os
print("[DEBUG] CWD:", os.getcwd())
print("[DEBUG] User:", os.getlogin())


# Define the GPIO pin number for the button
BUTTON_K2 = 27  # Yellow button K2

# Setup GPIO mode
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# Configure GPIO pin as input with pull-up resistor
GPIO.setup(BUTTON_K2, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Path to the program you want to run
program_to_run = "/home/admin/AI-Makruk-Board/src/engine/makruk_cli.py"

# Variable to track current process
current_process = None

print("System ready. Press K2 (yellow button) to run or restart the program")

# Function to kill a process and all its children
def kill_process_tree(process):
    try:
        parent = psutil.Process(process.pid)
        children = parent.children(recursive=True)
        
        # Kill children first
        for child in children:
            child.kill()
        
        # Kill parent
        parent.kill()
        parent.wait()
        
        print("Previous process terminated")
    except Exception as e:
        print(f"Error terminating process: {e}")

try:
    while True:
        # Check if button K2 is pressed (will be False when pressed because of pull-up)
        button_state = GPIO.input(BUTTON_K2)
        
        # When the button is pressed
        if button_state == False:
            print("Button K2 pressed!")
            
            # If a process is already running, kill it first
            if current_process is not None and current_process.poll() is None:
                print("Terminating existing program...")
                kill_process_tree(current_process)
                current_process = None
                time.sleep(0.5)  # Give some time for cleanup
            
            # Start a new process
            print("Starting program...")
            try:
                current_process = subprocess.Popen(["sudo", "python3", program_to_run])
                print("Program started successfully")
            except Exception as e:
                print(f"Error occurred: {e}")
                current_process = None
            
            # Wait for the button to be released before continuing
            while GPIO.input(BUTTON_K2) == False:
                time.sleep(0.1)
            print("Button released")
            
        time.sleep(0.1)  # Reduce CPU usage
        
except KeyboardInterrupt:
    print("Program stopped by user")
    # Clean up if a process is running
    if current_process is not None and current_process.poll() is None:
        kill_process_tree(current_process)
finally:
    GPIO.cleanup()  # Clean up GPIO