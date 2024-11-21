from pyautogui import hotkey
import time

def loadShortcut(filename):
    shortcut_dict = {}
    with open(filename, 'r') as file:
        for line in file:
            line = line.strip()
            if line:
                key, value = line.split(':')
                shortcut_dict[key] = value.split(',')

    return shortcut_dict
        
shortcutFile = 'shortcuts.txt'
shortcutDict =  loadShortcut(shortcutFile)

def printShortcut(shortcut_dict):
    print("Shortcut Dictionary:")
    for key, value in shortcutDict.items():
        print(f"{key}: {value}")

printShortcut(shortcutFile)

# Function to activate shortcut
def activateShortcut(pred_output, count, activationTime, shorcutDict):
    for key, value in shortcutDict.items():
        if key == pred_output:
            if pred_output == 'F' or pred_output == 'B':
                if count % (activationTime/2) == 0:
                    hotkey(*value)
            
            elif pred_output == 'A' or pred_output == 'Y':
                if count == activationTime:
                    hotkey(*value)
            else:
                hotkey(*value)


def addShortcut(filename):
    
    dataset = loadShortcut(shortcutFile)
    
    label = input('Enter a new label: ').strip()
    if label in dataset:
        print(f"The label '{label}' already exists with shortcut: {dataset[label]}")
        return
    
    shortcut = input("Enter a new shortcut (ex: 'ctrl,up'): ").strip().split(',')
    
    
    shortcut_str = ','.join(shortcut)
    
    with open(filename, 'a') as file:
        file.write(f'{label}:{shortcut_str}\n')


addShortcut(shortcutFile)