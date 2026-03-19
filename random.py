import pyautogui
import time
import subprocess

# --- CONFIGURATION ---

# 1. The X-coordinate where your second monitor starts. 
# (e.g., If your main monitor is 1920x1080 and the second is on the right, this is 1920)
MONITOR_2_START_X = 1920 

# 2. How many seconds of inactivity before turning off?
TIMEOUT_SECONDS = 5 # 5 minutes

# 3. Paste your Monitor Device Name from ControlMyMonitor here
MONITOR_ID = r"DISPLAY\YOUR_MONITOR_ID_HERE"

# Commands to send to ControlMyMonitor
# VCP Code 214 (D6) controls power. 4 is standby/off, 1 is on.
CMD_OFF = f'ControlMyMonitor.exe /SetValue "{MONITOR_ID}" 214 4'
CMD_ON  = f'ControlMyMonitor.exe /SetValue "{MONITOR_ID}" 214 1'

# --- SCRIPT LOGIC ---

timer = 0
is_monitor_off = False

print("Monitor script running. Press Ctrl+C in this window to stop.")

try:
    while True:
        # Get current mouse coordinates
        x, y = pyautogui.position()

        # Check if the mouse is currently on the second monitor
        if x >= MONITOR_2_START_X:
            # If the monitor is off, turn it back on
            if is_monitor_off:
                print("Activity detected! Waking up Monitor 2...")
                subprocess.run(CMD_ON, shell=True)
                is_monitor_off = False
            
            # Reset the idle timer because we are active on Monitor 2
            timer = 0 
            
        else:
            # The mouse is on Monitor 1
            if not is_monitor_off:
                timer += 1
                
                # If the timer hits our limit, turn off the monitor
                if timer >= TIMEOUT_SECONDS:
                    print("Idle limit reached. Putting Monitor 2 to sleep...")
                    subprocess.run(CMD_OFF, shell=True)
                    is_monitor_off = True

        # Wait 1 second before checking again
        time.sleep(1)

except KeyboardInterrupt:
    print("\nScript stopped by user.")