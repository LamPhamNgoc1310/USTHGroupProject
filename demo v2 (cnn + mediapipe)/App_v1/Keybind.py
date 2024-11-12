from pyautogui import hotkey

shortcutDict = {
    'L' : ['ctrl', 'up']
    'W' : ['ctrl', 'down'],
    'F' : ['ctrl', 'left'],
    'B' : ['ctrl', 'right'],
    'A' : 'space',
    'Y' : ['ctrl', 'r'] 
}

# Function to activate shortcut
def activateShortcut(pred_output, count, activationTime):
    for key, value in shortcutDict.items():
        if key == pred_output:
            if isinstance(value, list):
                hotkey(*value)
            else:
                hotkey(value)
    # if pred_output == 'L': hotkey('ctrl', 'up')
    # if pred_output == 'W': hotkey('ctrl', 'down')
    # if pred_output == 'F' and count % (activationTime/2) == 0: hotkey('ctrl', 'left')
    # if pred_output == 'B' and count % (activationTime/2) == 0: hotkey('ctrl', 'right')
    # if count == activationTime:
    #     if pred_output == 'A': hotkey('space')
    #     if pred_output == 'Y': hotkey('ctrl', 'r')