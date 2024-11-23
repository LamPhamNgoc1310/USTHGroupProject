const { app, BrowserWindow, Tray, Menu, ipcMain, dialog } = require('electron');
const fs = require("fs");
const path = require('path');
const { spawn } = require("child_process");
const zmq = require('zeromq');

// Global variables
let mainWindow;
let tray;
let pythonProcess;

// Initialize ZeroMQ socket to send frames to Camera
const socket = new zmq.Subscriber(); // Creating a subscriber socket
socket.connect('tcp://localhost:5555'); // Connect to the ZeroMQ server
socket.subscribe(''); // Subscribe to all messages

// ZeroMQ message listener using async iteration
const listenForFrames = async () => {
  for await (const [msg] of socket) {
    // Send the message (frame) to the renderer process
    if (mainWindow) {
      mainWindow.webContents.send('frame-data', msg.toString('utf-8'));
    }
  }
};

// Start listening for frames
listenForFrames().catch((err) => {
  console.error("Error listening for frames:", err);
});


// Handle saving the video file
ipcMain.on("save-video", async (event, buffer) => {
  try {
    // Send the save-video command with base64-encoded buffer to Python
    pythonProcess.stdin.write(JSON.stringify({ type: "save-video", data: buffer }) + "\n");

    // Simulating a response from Python
    pythonProcess.stdout.once("data", (response) => {
      const responseData = JSON.parse(response);
      event.reply("save-video-reply", responseData);  // Return success/failure to renderer
    });

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
        dialog.showErrorBox('Save Video Failed', `Error: ${err.message}`);  // Error dialog for the user
        event.reply("save-video-reply", { success: false, error: err.message });
      } else {
        console.log("Video saved successfully to:", filePath);
        event.reply("save-video-reply", { success: true });
      }
    });
  } catch (error) {
    console.error("Error during save dialog:", error);
    dialog.showErrorBox('Save Video Failed', `Error: ${error.message}`);  // Error dialog for the user
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

// Create Main Window
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

// Create Tray Icon
const createTray = () => {
  const iconPath = path.join(__dirname, 'dist', 'neco.png'); // Path to neco.png

  try {
    tray = new Tray(iconPath); // We need an icon here :v
    const contextMenu = Menu.buildFromTemplate([
      { label: 'Open', click: () => { mainWindow.show(); }},
      { label: 'Quit', click: () => { app.isQuitting = true; tray.destroy(); app.quit(); }}
    ]);

    tray.setContextMenu(contextMenu);
    tray.setToolTip('HGFMP');
  } catch (error) {
    console.error('Failed to load tray icon:', error);
  }
};

// Start the Python process
const startPythonProcess = () => {
  const pythonScriptPath = process.env.PYTHON_SCRIPT_PATH;

  console.log('Python Script Path from Environment:', pythonScriptPath);

  // Ensure the Python script is called correctly
  const pythonProcess = spawn('python', [pythonScriptPath]);

  // Capture the output from the Python script
  pythonProcess.stdout.on('data', (data) => {
    console.log(`Python script output: ${data.toString()}`);
  });

  // Capture any errors from the Python script
  pythonProcess.stderr.on('data', (data) => {
    console.error(`Python script error: ${data.toString()}`);
  });

  // Handle process completion
  pythonProcess.on('close', (code) => {
    console.log(`Python script finished with code ${code}`);
  }); 
};

app.whenReady().then(() => {
  startPythonProcess();
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
