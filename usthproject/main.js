const { app, BrowserWindow } = require('electron')

const createWindow = () => {
    const win = new BrowserWindow({
        width: 800,
        height: 600
    })

    win.loadFile('index.html')
};

app.whenReady().then(()=> {
    // create a window whenever app is opened
    createWindow();
    // for macos, if the app is active and there's no window opening, create a window.
    app.on('activate', () => {
        if (BrowserWindow.getAllWindows().length === 0){
            createWindow;
        }
    })
});

// quit the app if all windows are closed
app.on('window-all-closed', () => {
    // check if platform is macos
    if (process.platform !== 'darwin'){
        app.quit()
    }
})