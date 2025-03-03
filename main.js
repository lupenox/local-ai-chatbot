const { app, BrowserWindow } = require("electron");
const path = require("path");

function createWindow() {
    let win = new BrowserWindow({
        width: 800,
        height: 600,
        webPreferences: {
            nodeIntegration: true,
        }
    });

    // Ensure Electron correctly loads the React build
    const startURL = `file://${path.join(__dirname, "build", "index.html")}`;
    console.log("Loading URL:", startURL); // Debugging line
    win.loadURL(startURL);

    // Open DevTools for debugging
    win.webContents.openDevTools();
}

app.whenReady().then(createWindow);
