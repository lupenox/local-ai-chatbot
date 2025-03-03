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

    // Load the React app correctly
    const startURL = `file://${path.join(__dirname, "build", "index.html")}`;
    console.log("Loading URL:", startURL);
    win.loadURL(startURL);

    win.webContents.openDevTools(); // Keep DevTools open for debugging
}

app.whenReady().then(createWindow);
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

    // Load the React app correctly
    const startURL = `file://${path.join(__dirname, "build", "index.html")}`;
    console.log("Loading URL:", startURL);
    win.loadURL(startURL);

    win.webContents.openDevTools(); // Keep DevTools open for debugging
}

app.whenReady().then(createWindow);
