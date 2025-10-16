# 🎮 Roblox Idle Terminator

A lightweight Windows application that monitors Roblox gameplay and automatically terminates it after 20.5 minutes of inactivity to prevent battery drain and overheating.

## ✨ Features

### 🔥 Core Protection
- **Automatic Termination**: Kills Roblox after 20.5 minutes of inactivity (right when Roblox would kick you anyway)
- **Continuous Monitoring**: Keeps monitoring even after killing Roblox - no need to restart
- **Activity Detection**: Tracks keyboard and mouse input while Roblox is focused
- **Battery & Heat Protection**: Prevents your laptop from running at 80°C when you forget to close Roblox

### 🎯 Productivity Tools
- **Key Spammer**: Toggle spam any key (default: F) at 20 presses/second
- **Auto-Clicker**: Toggle automatic clicking at 10 clicks/second
- **Customizable Hotkeys**: Configure spam key and auto-click in the GUI

### 🖥️ User Interface
- **System Tray Support**: Minimize to hidden icons area to save taskbar space
- **Dark/Light Theme**: Toggle between themes with 🌙/☀️ button
- **Transparency Slider**: Adjust window opacity (0.2 to 1.0)
- **Real-time Monitoring**: View active window, Roblox status, focus state, and idle timer
- **Activity Log**: See last 2 activity events with timestamps

## 📋 Requirements

- Windows OS
- Python 3.7+
- Roblox installed

## 🚀 Installation

### Option 1: Virtual Environment (Recommended)

```powershell
# Clone or download the repository
cd UtilBlox

# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Run the application
python RobloxIdleTerminator.py
```

### Option 2: Global Installation

```powershell
pip install -r requirements.txt
python RobloxIdleTerminator.py
```

## 🎮 Usage

### Basic Operation
1. **Launch**: Run `RobloxIdleTerminator.py`
2. **Auto-Start**: Monitoring starts automatically
3. **Minimize**: Click minimize button to hide to system tray
4. **Close**: Click X to quit completely

### Key Spammer
1. Set your desired key in the "Spam:" field (default: F)
2. Click "Set" to apply
3. Click "Start" to begin spamming, "Stop" to end

### Auto-Clicker
1. Click "Start" under "Click:" to begin auto-clicking
2. Click "Stop" to end
3. Works at 10 clicks per second (100ms delay)

### System Tray
- **Minimize Button**: Hides window to system tray
- **Tray Icon**: Right-click for menu, left-click to show/hide
- **Close Button (X)**: Completely exits the application

## ⚙️ Configuration

### Idle Threshold
Edit `IDLE_THRESHOLD` in the script (default: 1230 seconds = 20.5 minutes)

```python
IDLE_THRESHOLD = 1230  # seconds
```

### Auto-Click Speed
Edit `autoclick_delay` in the script (default: 0.1 seconds = 10 clicks/second)

```python
autoclick_delay = 0.1  # seconds between clicks
```

### Key Spam Speed
Configured in `spam_key_loop()` (default: 0.05 seconds = 20 presses/second)

## 🛡️ Safety Features

- **Focus Detection**: Only tracks activity when Roblox window is focused
- **Continuous Operation**: Monitors across multiple Roblox sessions
- **Clean Termination**: Gracefully stops all threads on exit
- **System Tray Fallback**: Never lose access to the app

## 📝 Dependencies

- `psutil` - Process monitoring
- `pynput` - Keyboard and mouse control
- `pywin32` - Windows API access
- `pystray` - System tray icon
- `Pillow` - Image processing for tray icon
- `tkinter` - GUI (included with Python)

## 🔧 Troubleshooting

### Icon Not Found Error
If you see an icon error on startup, either:
1. Remove the icon line from the script, or
2. Create/provide an icon file at `D:\rb.ico`

### Monitoring Not Working
- Ensure Roblox process name is `RobloxPlayerBeta.exe`
- Check that Roblox window title is exactly "Roblox" when focused

### Virtual Environment Issues
```powershell
# If activation fails, enable scripts
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Then activate again
.\venv\Scripts\Activate.ps1
```

## 📄 License

Free to use and modify for personal use.

## ⚠️ Disclaimer

This tool is for educational and personal use. Use responsibly and in accordance with Roblox Terms of Service.

---

**Made to save laptops from becoming fire hazards! 🔥➡️❄️**
