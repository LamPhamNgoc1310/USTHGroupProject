const { app, BrowserWindow, Tray, Menu, ipcMain } = require('electron');
const { spawn } = require("child_process");
// const fs = require('fs');
const path = require('node:path');

let mainWindow;
let tray;
let flaskProcess; // To track the Flask server process
process.env['ELECTRON_DISABLE_SECURITY_WARNINGS'] = 'true';


// if (process.env.NODE_ENV === 'development') {
//   try {
//     require('electron-reload')(__dirname, {
//       electron: require(`${__dirname}/node_modules/electron`),
//     });
//   } catch (err) {
//     console.error('Failed to initialize electron-reload:', err);
//   }
// }

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
      webSecurity: false,  // Disable web security for external content
      allowRunningInsecureContent: true,  // Allow insecure content like local HTTP feeds
    },
    autoHideMenuBar: true,
  });
  
  // Remove CSP headers
  mainWindow.webContents.session.webRequest.onHeadersReceived((details, callback) => {
    if (details.responseHeaders['content-security-policy']) {
      delete details.responseHeaders['content-security-policy'];
    }
    callback({ cancel: false, responseHeaders: details.responseHeaders });
  });

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
  const iconPath = path.join(__dirname, 'dist', 'electron-icon.png'); // Path to neco.png

  try {
    tray = new Tray(iconPath); // We need an icon here :v
    const contextMenu = Menu.buildFromTemplate([
      {
        label: 'Open',
        click: () => {
          mainWindow.show();
        },
      },
      {
        label: 'Quit',
        click: () => {
          app.isQuitting = true;
          if (flaskProcess) {
            flaskProcess.kill(); // Stop Flask server when quitting
          }
          tray.destroy();
          app.quit();
        },
      },
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

// Handle Flask server start and stop via IPC
ipcMain.on('start-flask', (event) => {
  if (flaskProcess) {
    console.log('Flask server is already running.');
    event.reply('flask-started', { success: false, error: 'Server already running.' });
    return;
  }

  // Resolve relative path to main.py
  const flaskScriptPath = path.join(__dirname, '..', '..', 'demo v2 (cnn + mediapipe)', 'App_v1', 'main.py');
  console.log('Flask Script Path:', flaskScriptPath); 

  // Spawn the Flask process
  flaskProcess = spawn('python', [flaskScriptPath], {
    shell: true,  // For compatibility with Windows
    detached: true,
  });

  flaskProcess.stdout.on('data', (data) => {
    console.log(`Flask stdout: ${data}`);
  });

  flaskProcess.stderr.on('data', (data) => {
    console.error(`Flask stderr: ${data}`);
  });

  flaskProcess.on('close', (code) => {
    console.log(`Flask server exited with code ${code}`);
    flaskProcess = null;
  });

  flaskProcess.on('error', (err) => {
    console.error('Failed to start Flask process:', err);
    event.reply('flask-started', { success: false, error: 'Failed to start Flask process' });
  });  

  event.reply('flask-started', { success: true });
});

// Global Error Handling and Debugging
process.on('uncaughtException', (error) => {
  console.error('Uncaught Exception:', error);
});

process.on('unhandledRejection', (reason) => {
  console.error('Unhandled Promise Rejection:', reason);
});
