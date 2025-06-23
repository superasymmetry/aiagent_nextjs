import subprocess
import os
import pyautogui
import pygetwindow as gw
import time

ps_script = r"C:\Users\2025130\Documents\aiagent_nextjs\vm\initialize.ps1"

windows = gw.getWindowsWithTitle("Windows10VM")
if windows:
    vm_window = windows[0]
    vm_window.activate()
    time.sleep(1)
    # center_x = vm_window.left + vm_window.width // 2
    # center_y = vm_window.top + vm_window.height // 2
    # pyautogui.moveTo(center_x, center_y, duration=0.5)
    # pyautogui.click()
    # pyautogui.press('enter')
    pyautogui.write('Ab200708', interval=0.1)
    pyautogui.press('enter')
    time.sleep(2)
    # print(f"Clicking at center: ({center_x}, {center_y})")
    pyautogui.click(600, 2000)
    time.sleep(1)
    pyautogui.write('word', interval=0.1)
    time.sleep(1)
    pyautogui.press('enter')
    time.sleep(1)
    pyautogui.click(800, 800)
    time.sleep(1)
    pyautogui.write("Hello!", interval=0.1)
else:
    subprocess.run([
        "powershell",
        "-Command",
        f'Start-Process powershell -ArgumentList \'-ExecutionPolicy Bypass -File "{ps_script}"\' -Verb RunAs'
    ])
    time.sleep(15)

