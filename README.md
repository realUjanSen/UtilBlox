# UtilBlox

UtilBlox is an open-source utility that builds upon the now-deprecated project, **RobloxIdleTerminator**. While RobloxIdleTerminator was already perfect in its functionality of monitoring Roblox for 20.5 minutes of inactivity and terminating it, UtilBlox introduces more power features for playing Roblox games that are time consuming.

## Key Features
- Monitors Roblox for inactivity (20.5 minutes) and automatically kills the Roblox process if idle
- Only works with Roblox (not other games)
- Simple, single-window GUI with dark mode and transparency slider
- Key spammer: Hold a trigger key (default: G) to rapidly spam a target key (default: F) in Roblox
- Spam key only activates after holding the trigger for 700ms (prevents accidental spam)
- Adjustable spam key and delay from the GUI
- Auto-clicker: Toggle with Tab key, adjustable delay, works only when Roblox is running and focused
- Shows the last 2 key/mouse events in the GUI for feedback
- System tray support: minimize to tray, restore, or quit from tray icon

## Why UtilBlox?
UtilBlox aims to add new features to extend its functionality. The core idea of RobloxIdleTerminator remains intact and unchanged.

## Getting Started
1. Clone the repository:
   ```
   git clone github.com/realUjanSen/UtilBlox
   ```
2. Navigate to the project directory:
   ```
   cd UtilBlox
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Run the application:
   ```
   python UtilBlox.py
   ```

## License
UtilBlox is licensed under the GNU General Public License v3.0 (GPLv3). This means it is free and open-source software, but any derivative works must also be distributed under the same license. For more details, see the [LICENSE](LICENSE) file.
