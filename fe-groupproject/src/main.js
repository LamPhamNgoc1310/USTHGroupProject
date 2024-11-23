const { app, BrowserWindow, Tray, Menu, ipcMain, dialog } = require('electron');
const fs = require("fs");
const path = require('node:path');
const WebSocket = require('ws');  // We use the ws library for WebSocket communication
const { Buffer } = require('buffer');

let mainWindow;
let tray;

// WebSocket connection setup for receiving frames
const ws = new WebSocket('ws://localhost:8765'); // Connect to the Python WebSocket server

ws.on('open', () => {
  console.log("Connected to WebSocket server");
});

ws.on('message', (message) => {
  console.log("Received frame:", message);  // Debugging the frame

  // Each message will be a base64-encoded frame
  if (mainWindow && mainWindow.webContents) {
    mainWindow.webContents.send('frame', message);  // Send the frame to the renderer process
  }
});

ws.on('close', () => {
  console.log("WebSocket connection closed");
});

ws.on('error', (error) => {
  console.error("WebSocket error:", error);
});

// Handle saving the video file
ipcMain.on("save-video", async (event, buffer) => {
  try {
    const { canceled, filePath } = await dialog.showSaveDialog({
      title: "Save Video",
      defaultPath: path.join(app.getPath("downloads"), "recorded-video.webm"),
      filters: [{ name: "WebM Video", extensions: ["webm"] }],
    });

    if (canceled || !filePath) {
      console.log("User canceled save dialog.");
      return;
    }

    fs.writeFile(filePath, buffer, (err) => {
      if (err) {
        console.error("Failed to save video file:", err);
        dialog.showErrorBox('Save Video Failed', `Error: ${err.message}`);
        event.reply("save-video-reply", { success: false, error: err.message });
      } else {
        console.log("Video saved successfully to:", filePath);
        event.reply("save-video-reply", { success: true });
      }
    });
  } catch (error) {
    console.error("Error during save dialog:", error);
    dialog.showErrorBox('Save Video Failed', `Error: ${error.message}`);
    event.reply("save-video-reply", { success: false, error: error.message });
  }
});

if (process.env.NODE_ENV === 'development') {
  try {
    require('electron-reload')(__dirname, {
      electron: require(`${__dirname}/node_modules/electron`)
    });
  } catch (err) {
    console.error('Failed to initialize electron-reload:', err);
  }
}

if (require('electron-squirrel-startup')) {
  app.quit();
}

// Create main window
const createWindow = () => {
  console.log('Creating window...');
  mainWindow = new BrowserWindow({
    width: 800,
    height: 600,
    webPreferences: {
      preload: path.join(__dirname, 'dist', "preload.js"),
      nodeIntegration: true,
      contextIsolation: false,
    },
    autoHideMenuBar: true,
  });

  console.log(MAIN_WINDOW_WEBPACK_ENTRY);
  mainWindow.loadURL(MAIN_WINDOW_WEBPACK_ENTRY)
    .then(() => console.log('Main window loaded'))
    .catch((error) => console.error('Error loading window:', error));

  mainWindow.webContents.openDevTools();

  // Minimize to tray when closing
  mainWindow.on('close', (event) => {
    if (!app.isQuitting && mainWindow) {
      event.preventDefault();
      mainWindow.hide();
    }
  });
};

const createTray = () => {
  const iconPath = path.join(__dirname, 'dist', 'neco.png'); // Path to neco.png

  try {
    tray = new Tray(iconPath); // We need an icon here :v
  const contextMenu = Menu.buildFromTemplate([
    { label: 'Open',
      click: () => {
        mainWindow.show();
      }},
    { label: 'Quit',
      click: () => {
        app.isQuitting = true;
        tray.destroy();
        app.quit();
      }}
  ]);

  tray.setContextMenu(contextMenu);
  tray.setToolTip('HGFMP');
  } catch (error) {
    console.error('Failed to load tray icon:', error);
  }
};

app.whenReady().then(() => {
  createWindow();
  createTray();
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow();
  }
});

// Global Error Handling and Debugging
process.on('uncaughtException', (error) => {
  console.error('Uncaught Exception:', error);
});

process.on('unhandledRejection', (reason) => {
  console.error('Unhandled Promise Rejection:', reason);
});

// console.log(path.join(__dirname, 'src', 'neco.png'));
// mainWindow.loadURL(MAIN_WINDOW_WEBPACK_ENTRY).catch((error) => {
//   console.error('Failed to load URL:', error);
// });
