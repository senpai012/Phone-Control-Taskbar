import tkinter as tk
import subprocess
import psutil
import os
import platform

# Replace these with the actual device IDs of your phones
DEVICE_IDS = ["AUDUT20528007754", "MVSNW19A17002264", "R58M42XKVHH"]

# Store process objects to manage them later
processes = {}
current_index = 0  # Index to keep track of the current phone window


def start_scrcpy(device_id):
    # If the process already exists, bring it to the front
    if device_id in processes and processes[device_id].poll() is None:
        focus_window(device_id)
        return

    # Start a new scrcpy process for the specified device
    proc = subprocess.Popen(["scrcpy", "-s", device_id])
    processes[device_id] = proc


def stop_scrcpy(device_id):
    if device_id in processes and processes[device_id].poll() is None:
        processes[device_id].terminate()
        processes[device_id].wait()
        del processes[device_id]


def focus_window(device_id):
    print(f"Focusing window for device: {device_id}")
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        if proc.info['name'] == 'scrcpy' and device_id in proc.info['cmdline']:
            try:
                if platform.system() == 'Linux':
                    os.system(f"xdotool windowactivate $(xdotool search --pid {proc.info['pid']})")
                    print(f"Focused on {device_id} using xdotool.")
                elif platform.system() == 'Windows':
                    import ctypes
                    hwnd = ctypes.windll.user32.FindWindowW(None, f"scrcpy {device_id}")
                    ctypes.windll.user32.ShowWindow(hwnd, 5)  # SW_SHOW
                    ctypes.windll.user32.SetForegroundWindow(hwnd)
                    print(f"Focused on {device_id} using ctypes.")
            except Exception as e:
                print(f"Failed to focus window for {device_id}: {e}")
            return


def switch_to_next_phone():
    global current_index
    current_index = (current_index + 1) % len(DEVICE_IDS)
    print(f"Switching to next phone: {DEVICE_IDS[current_index]}")
    focus_window(DEVICE_IDS[current_index])


def switch_to_previous_phone():
    global current_index
    current_index = (current_index - 1) % len(DEVICE_IDS)
    print(f"Switching to previous phone: {DEVICE_IDS[current_index]}")
    focus_window(DEVICE_IDS[current_index])

def detect_devices():
    result = subprocess.run(["adb", "devices"], capture_output=True, text=True)
    devices = []
    for line in result.stdout.splitlines()[1:]:
        if '\tdevice' in line:
            devices.append(line.split('\t')[0])
    return devices

# Create the main Tkinter window
root = tk.Tk()
root.title("Phone Control Taskbar")

# Create buttons for each phone
for idx, device_id in enumerate(DEVICE_IDS):
    start_button = tk.Button(root, text=f"Start Phone {idx + 1}", command=lambda d=device_id: start_scrcpy(d))
    start_button.pack(side=tk.LEFT, padx=5, pady=5)

    stop_button = tk.Button(root, text=f"Stop Phone {idx + 1}", command=lambda d=device_id: stop_scrcpy(d))
    stop_button.pack(side=tk.LEFT, padx=5, pady=5)

# Bind the Page Up (Repag) and Page Down (Avpag) keys to switch between phone windows
root.bind('<Prior>', lambda e: switch_to_previous_phone())  # Page Up
root.bind('<Next>', lambda e: switch_to_next_phone())      # Page Down

# Start the Tkinter event loop
root.mainloop()
