import keyboard
import pyautogui
import tkinter as tk
from tkinter import filedialog

def choose_image():
    file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg;*.png;*.gif")])
    if file_path:
        # Process the chosen image here
        print("Selected image:", file_path)

# Create the main window
window = tk.Tk()
window.title("Image Uploader")

# Create a button to trigger the image selection
button = tk.Button(window, text="Choose Image", command=choose_image)
button.pack()

# Start the event loop
window.mainloop()

def keybind(key):
    ## Currently there is an error when you bind to arrow keys
    if key.name == '1':
        print('Play/Pause')
        pyautogui.hotkey('space')
        
    elif key.name == '2':
        print('Next Track')
        pyautogui.hotkey('ctrl', 'right')
        
    elif key.name == '3':
        print('Previous Track')
        pyautogui.hotkey('ctrl', 'left')
        
    elif key.name == '4':
        print('Volume Up')
        pyautogui.hotkey('ctrl', 'up')
        
    elif key.name == '5':
        print('Volume Down')
        pyautogui.hotkey('ctrl', 'down')
        
    elif key.name == '6':
        print('Shuffle Track')
        pyautogui.hotkey('ctrl', 's')
        
    elif key.name == '7':
        print('Repeat Track')
        pyautogui.hotkey('ctrl', 'r')
    
    elif key.name == 'm':
        print('Mute/Unmute')
        pyautogui.hotkey('ctrl', 'shift', 'down')  # This shortcut didn't work for some reasons...


if __name__ == '__main__':
    choose_image()
    keyboard.on_press(keybind)
    keyboard.wait()
