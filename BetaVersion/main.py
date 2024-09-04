import keyboard
import pyautogui
from model import load_model
import tkinter as tk
from tkinter import filedialog

def choose_image():
    file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg;*.png;*.gif")])
    if file_path:
        # Process the chosen image here
        print("Selected image:", file_path)
        
    return file_path


# Create the main window
window = tk.Tk()
window.title("Image Uploader")

# Create a button to trigger the image selection
button = tk.Button(window, text="Choose Image", command=choose_image)
button.pack()

# # Start the event loop
# window.mainloop()

def keybind(label):
    print('Keybind')
    pyautogui.sleep(3)
    ## Currently there is an error when you bind to arrow keys
    if label == 'okay':
        print('Play/Pause')
        pyautogui.hotkey('space')
        
    elif label == 'paper':
        print('Next Track')
        pyautogui.hotkey('ctrl', 'right')
        
    elif label == 'rock':
        print('Previous Track')
        pyautogui.hotkey('ctrl', 'left')
        
    elif label == 'scissor':
        print('Volume Up')
        pyautogui.hotkey('ctrl', 'up')
        
    elif label == 'thumbs':
        print('Volume Down')
        pyautogui.hotkey('ctrl', 'down')
        
    # elif label.name == '6':
    #     print('Shuffle Track')
    #     pyautogui.hotkey('ctrl', 's')
        
    elif label == 'up':
        print('Repeat Track')
        pyautogui.hotkey('ctrl', 'r')
    
    # elif key.name == 'm':
    #     print('Mute/Unmute')
    #     pyautogui.hotkey('ctrl', 'shift', 'down')  # This shortcut didn't work for some reasons...
    else: 
        print("Invalid label")

if __name__ == '__main__':
    file_path = choose_image()
    label = load_model(file_path)
    keybind(label)
    keyboard.wait()
