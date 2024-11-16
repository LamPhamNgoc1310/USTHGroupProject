const { app, BrowserWindow, Tray, Menu } = require('electron');
const path = require('node:path');

// require('electron-reload')(__dirname, { electron: require(`${__dirname}/node_modules/electron`) });

let mainWindow;
let tray;

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

const createWindow = () => {
  mainWindow = new BrowserWindow({
    width: 800,
    height: 600,
    webPreferences: {
      preload: MAIN_WINDOW_PRELOAD_WEBPACK_ENTRY,
    },
    autoHideMenuBar: true,
  });

  mainWindow.loadURL(MAIN_WINDOW_WEBPACK_ENTRY);

  mainWindow.webContents.openDevTools();

  // Minimize to tray when closing
  mainWindow.on('close', (event) => {
    if (process.platform !== 'darwin') {
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
    {
      label: 'Open',
      click: () => {
        mainWindow.show();
      }
    },
    {
      label: 'Quit',
      click: () => {
        app.quit();
      }
    }
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

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

console.log(path.join(__dirname, 'src', 'neco.png'));
// mainWindow.loadURL(MAIN_WINDOW_WEBPACK_ENTRY).catch((error) => {
//   console.error('Failed to load URL:', error);
// });
