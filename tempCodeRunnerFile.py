import time
import threading
import psutil
import tkinter as tk
from tkinter import ttk
from pynput import keyboard, mouse
from pynput.keyboard import Key, Controller as KeyboardController
from pynput.mouse import Button, Controller as MouseController
import win32gui
import pystray
from PIL import Image, ImageDraw

# --- CONFIG ---
IDLE_THRESHOLD = 1230  # 20.5 minutes
UPDATE_INTERVAL = 1000  # ms
LOG_WINDOW_SIZE = 3     # Show last 3 log lines

# --- GLOBALS ----
last_activity_time = time.time()
running = False
keyboard_listener = None
mouse_listener = None
is_dark_mode = True  # Start in dark mode
tray_icon = None
window_visible = True

# Key spammer and auto-clicker globals
kb_controller = KeyboardController()
mouse_controller = MouseController()
spam_key = 'f'  # Default spam key
spam_key_active = False
spam_key_held_start = None  # Track when key was first pressed
spam_thread = None
autoclick_hotkey = Key.tab  # Default auto-click toggle key (Tab)
autoclick_active = False
autoclick_thread = None
autoclick_delay = 0.1  # Click every 100ms (10 clicks per second)
SPAM_ACTIVATION_DELAY = 0.7  # 700ms like AHK script

# --- COLOR SCHEMES ---
DARK = {
    "bg": "#181818",
    "fg": "#ffffff",
    "btn_bg": "#222222",
    "btn_fg": "#ffffff",
    "entry_bg": "#222222",
    "entry_fg": "#ffffff",
    "scroll_bg": "#181818",
    "scroll_fg": "#ffffff"
}
LIGHT = {
    "bg": "#f0f0f0",
    "fg": "#181818",
    "btn_bg": "#e0e0e0",
    "btn_fg": "#181818",
    "entry_bg": "#ffffff",
    "entry_fg": "#181818",
    "scroll_bg": "#f0f0f0",
    "scroll_fg": "#181818"
}

def get_theme():
    return DARK if is_dark_mode else LIGHT

def apply_theme():
    theme = get_theme()
    root.configure(bg=theme["bg"])
    main_frame.configure(style="Main.TFrame")
    log_frame.configure(style="Main.TFrame")
    control_frame.configure(style="Main.TFrame")
    spam_frame.configure(style="Main.TFrame")
    output_box.configure(bg=theme["bg"], fg=theme["fg"], insertbackground=theme["fg"])
    transparency_slider.configure(
        bg=theme["bg"], fg=theme["fg"], troughcolor=theme["btn_bg"], highlightbackground=theme["bg"]
    )
    for l in labels:
        l.configure(background=theme["bg"], foreground=theme["fg"])
    process_label.configure(background=theme["bg"], foreground=theme["fg"])
    status_label.configure(background=theme["bg"], foreground=theme["fg"])
    focus_label.configure(background=theme["bg"], foreground=theme["fg"])
    timer_label.configure(background=theme["bg"], foreground=theme["fg"])
    spam_label.configure(background=theme["bg"], foreground=theme["fg"])
    spam_status_label.configure(background=theme["bg"], foreground=theme["fg"])
    autoclick_label.configure(background=theme["bg"], foreground=theme["fg"])
    spam_key_entry.configure(bg=theme["entry_bg"], fg=theme["entry_fg"])
    style.configure("TButton", background=theme["btn_bg"], foreground=theme["btn_fg"])
    style.configure("Main.TFrame", background=theme["bg"])
    dark_mode_btn.config(text="🌙" if is_dark_mode else "☀️")

def toggle_dark_mode():
    global is_dark_mode
    is_dark_mode = not is_dark_mode
    apply_theme()

# --- KEY SPAMMER AND AUTO-CLICKER FUNCTIONS ---
def spam_key_loop():
    """Continuously press the configured spam key while active"""
    global spam_key_active
    while spam_key_active:
        try:
            kb_controller.press(spam_key)
            kb_controller.release(spam_key)
            time.sleep(0.03)  # 30ms like AHK script
        except Exception as e:
            print(f"Key spam error: {e}")
            break

def check_spam_key_held():
    """Check if spam key has been held for 700ms, then start spamming"""
    global spam_key_active, spam_key_held_start, spam_thread
    
    if spam_key_held_start is not None:
        held_duration = time.time() - spam_key_held_start
        if held_duration >= SPAM_ACTIVATION_DELAY and not spam_key_active:
            # Key has been held for 700ms, start spamming
            spam_key_active = True
            spam_thread = threading.Thread(target=spam_key_loop, daemon=True)
            spam_thread.start()
            log(f"Key spam activated: {spam_key.upper()}")

def stop_spam_key():
    """Stop the key spammer"""
    global spam_key_active, spam_key_held_start
    if spam_key_active:
        spam_key_active = False
        log(f"Key spam stopped")
    spam_key_held_start = None

def autoclick_loop():
    """Continuously click at the configured rate while active"""
    global autoclick_active
    while autoclick_active:
        try:
            mouse_controller.click(Button.left, 1)
            time.sleep(autoclick_delay)
        except Exception as e:
            print(f"Auto-click error: {e}")
            break

def toggle_autoclick():
    """Toggle auto-clicker on/off"""
    global autoclick_active, autoclick_thread
    if autoclick_active:
        autoclick_active = False
        log("Auto-click stopped")
    else:
        autoclick_active = True
        autoclick_thread = threading.Thread(target=autoclick_loop, daemon=True)
        autoclick_thread.start()
        log("Auto-click started")

def update_spam_key(new_key):
    """Update the spam key from GUI input"""
    global spam_key
    if new_key and len(new_key) == 1:
        spam_key = new_key.lower()
        log(f"Spam key set to: {spam_key.upper()}")
    else:
        log("Invalid spam key (use single character)")

def truncate_text(text, max_length=17):  # Now 17 characters
    return text if len(text) <= max_length else text[:max_length-3] + "..."

# --- SYSTEM TRAY FUNCTIONS ---
def create_tray_image():
    """Create a simple icon for the system tray"""
    width = 64
    height = 64
    image = Image.new('RGB', (width, height), color='#1e90ff')
    dc = ImageDraw.Draw(image)
    # Draw a simple "R" for Roblox
    dc.text((16, 16), "R", fill='white')
    return image

def show_window():
    """Show the window from system tray"""
    global window_visible
    root.deiconify()
    root.lift()
    root.focus_force()
    window_visible = True

def hide_window():
    """Hide the window to system tray"""
    global window_visible
    root.withdraw()
    window_visible = False

def quit_app(icon=None, item=None):
    """Quit the application completely"""
    global running, tray_icon
    running = False
    if tray_icon:
        tray_icon.stop()
    root.quit()

def on_window_close():
    """Handle window close button - quit the app completely"""
    quit_app()

def on_window_minimize(event):
    """Handle window minimize - hide to system tray"""
    if root.state() == 'iconic':  # Window was minimized
        hide_window()
        return "break"

def toggle_window():
    """Toggle window visibility from tray icon"""
    if window_visible:
        hide_window()
    else:
        show_window()

def setup_tray_icon():
    """Setup the system tray icon"""
    global tray_icon
    icon_image = create_tray_image()
    menu = pystray.Menu(
        pystray.MenuItem("Show/Hide", toggle_window, default=True),
        pystray.MenuItem("Quit", quit_app)
    )
    tray_icon = pystray.Icon("RobloxMonitor", icon_image, "Roblox Idle Monitor", menu)
    threading.Thread(target=tray_icon.run, daemon=True).start()


# --- TKINTER GUI ---
root = tk.Tk()
root.title("Roblox Idle Monitor")
root.geometry("233x165")  # Increased height to show all controls
root.resizable(True, True)
root.attributes("-alpha", 0.7)  # Default alpha is now 0.7
root.protocol("WM_DELETE_WINDOW", on_window_close)  # Close button quits app
root.bind("<Unmap>", on_window_minimize)  # Minimize button hides to tray

# Set custom icon
try:
    root.iconbitmap(r"D:\rb.ico")
except Exception as e:
    print("Could not set icon:", e)

style = ttk.Style()
style.theme_use('clam')
style.configure("TButton", background=DARK["btn_bg"], foreground=DARK["btn_fg"])
style.configure("Main.TFrame", background=DARK["bg"])

main_frame = ttk.Frame(root, style="Main.TFrame")
main_frame.pack(expand=True, fill='both', padx=2, pady=2)

labels = []
for i, lbl in enumerate(["ActiveWindow", "Status", "Focus", "SinceIdle"]):
    l = ttk.Label(main_frame, text=lbl, font=('Arial', 8, 'bold'), background=DARK["bg"], foreground=DARK["fg"])
    l.grid(row=0, column=i, sticky="nsew", padx=1, pady=1)
    labels.append(l)

process_label = ttk.Label(main_frame, font=('Arial', 8), width=11, anchor="w", wraplength=120, background=DARK["bg"], foreground=DARK["fg"])
process_label.grid(row=1, column=0, sticky="nsew", padx=1, pady=1)

status_label = ttk.Label(main_frame, font=('Arial', 8), width=7, anchor="center", background=DARK["bg"], foreground=DARK["fg"])
status_label.grid(row=1, column=1, sticky="nsew", padx=1, pady=1)

focus_label = ttk.Label(main_frame, font=('Arial', 8), width=6, anchor="center", background=DARK["bg"], foreground=DARK["fg"])
focus_label.grid(row=1, column=2, sticky="nsew", padx=1, pady=1)

timer_label = ttk.Label(main_frame, font=('Arial', 8), width=8, anchor="center", background=DARK["bg"], foreground=DARK["fg"])
timer_label.grid(row=1, column=3, sticky="nsew", padx=1, pady=1)

log_frame = ttk.Frame(root, style="Main.TFrame")
log_frame.pack(fill='both', expand=True, padx=2, pady=1)

# Use tk.Text instead of ScrolledText, set height=3 for 3 lines, no scrollbar
output_box = tk.Text(
    log_frame, height=3, font=('Arial', 7),
    bg=DARK["bg"], fg=DARK["fg"], insertbackground=DARK["fg"], borderwidth=1, relief="solid"
)
output_box.pack(expand=True, fill='both')

def log(msg):
    output_box.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] {msg}\n")
    lines = output_box.get('1.0', tk.END).splitlines()
    if len(lines) > LOG_WINDOW_SIZE:
        output_box.delete('1.0', f"{len(lines) - LOG_WINDOW_SIZE + 1}.0")
    output_box.see(tk.END)

def format_time(seconds):
    hours, rem = divmod(seconds, 3600)
    minutes, seconds = divmod(rem, 60)
    return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"

def get_foreground_window_title():
    try:
        return win32gui.GetWindowText(win32gui.GetForegroundWindow())
    except Exception:
        return "(Unknown)"

def is_roblox_running():
    for proc in psutil.process_iter(['name']):
        if proc.info['name'] and proc.info['name'].lower() == "robloxplayerbeta.exe":
            return proc
    return None

def is_roblox_focused():
    roblox_proc = is_roblox_running()
    if not roblox_proc:
        return False
    return get_foreground_window_title().strip() == "Roblox"

def get_readable_key(key):
    if hasattr(key, 'char') and key.char is not None:
        return key.char
    return str(key).split('.')[-1].capitalize()

def get_readable_button(button):
    mapping = {
        mouse.Button.left: "Left Mouse Button",
        mouse.Button.right: "Right Mouse Button",
        mouse.Button.middle: "Middle Mouse Button"
    }
    return mapping.get(button, str(button))

def on_key_press(key):
    global last_activity_time, spam_key_held_start, spam_key
    
    # Update spam_key from entry field dynamically
    try:
        current_spam_key = spam_key_entry.get().lower().strip()
        if current_spam_key and len(current_spam_key) == 1:
            spam_key = current_spam_key
    except:
        pass
    
    # Get the character representation of the key
    key_char = None
    if hasattr(key, 'char') and key.char is not None:
        key_char = key.char.lower()
    
    # Check for spam key press (first press is normal, then start tracking)
    if key_char == spam_key and spam_key_held_start is None:
        # First press - this is a normal keypress (could be chatting)
        spam_key_held_start = time.time()
        # Schedule check after 700ms
        threading.Timer(SPAM_ACTIVATION_DELAY, check_spam_key_held).start()
    
    # Check for auto-click toggle hotkey (Tab key)
    if key == autoclick_hotkey:
        toggle_autoclick()
    
    # Original activity tracking for Roblox
    if is_roblox_running():
        if is_roblox_focused():
            readable = get_readable_key(key)
            log(f"Key: {readable}")
            last_activity_time = time.time()

def on_key_release(key):
    """Handle key release events"""
    global spam_key_active, spam_key_held_start
    
    # Stop spam when spam key is released
    key_char = None
    if hasattr(key, 'char') and key.char is not None:
        key_char = key.char.lower()
    
    if key_char == spam_key:
        stop_spam_key()

def on_click(x, y, button, pressed):
    global last_activity_time
    if pressed:
        if is_roblox_running():
            if is_roblox_focused():
                readable = get_readable_button(button)
                log(f"Click: {readable}")
                last_activity_time = time.time()

def monitor_loop():
    global running, last_activity_time
    while running:
        time.sleep(1)
        roblox_proc = is_roblox_running()
        now = time.time()
        if roblox_proc:
            idle_duration = now - last_activity_time
            if idle_duration >= IDLE_THRESHOLD:
                log("Idle limit! Killing.")
                try:
                    roblox_proc.kill()
                    log("Roblox killed. Monitoring continues...")
                except Exception as e:
                    log(f"Kill fail: {e}")
                # Reset timer and continue monitoring (don't stop or break)
                last_activity_time = time.time()
        else:
            last_activity_time = now

def start_monitoring():
    global running, keyboard_listener, mouse_listener
    if not running:
        running = True
        threading.Thread(target=monitor_loop, daemon=True).start()
        keyboard_listener = keyboard.Listener(on_press=on_key_press, on_release=on_key_release)
        mouse_listener = mouse.Listener(on_click=on_click)
        keyboard_listener.start()
        mouse_listener.start()
        log("Started monitoring Roblox inactivity.")

def stop_monitoring():
    global running, keyboard_listener, mouse_listener
    running = False
    if keyboard_listener:
        keyboard_listener.stop()
        keyboard_listener = None
    if mouse_listener:
        mouse_listener.stop()
        mouse_listener = None
    log("Stopped monitoring Roblox inactivity.")

def update_gui():
    roblox_proc = is_roblox_running()
    roblox_focused = is_roblox_focused()
    title = get_foreground_window_title()
    process_label.config(text=truncate_text(title))
    status_label.config(text="Running" if roblox_proc else "Stopped")
    focus_label.config(text="Yes" if roblox_focused else "No")
    if roblox_proc:
        idle_time = time.time() - last_activity_time
    else:
        idle_time = 0
    timer_label.config(text=format_time(idle_time))
    root.after(UPDATE_INTERVAL, update_gui)

# --- Control Buttons, Dark Mode Button, and Transparency Slider ---
control_frame = ttk.Frame(root, style="Main.TFrame")
control_frame.pack(pady=1)

ttk.Button(control_frame, text="Start", command=start_monitoring, width=5).pack(side='left', padx=2)
ttk.Button(control_frame, text="Stop", command=stop_monitoring, width=5).pack(side='left', padx=2)

def set_transparency(val):
    root.attributes("-alpha", float(val))

transparency_slider = tk.Scale(
    control_frame, from_=0.2, to=1.0, orient='horizontal', resolution=0.01,
    showvalue=False, tickinterval=0, length=80, command=set_transparency,
    bg=DARK["bg"], fg=DARK["fg"], troughcolor=DARK["btn_bg"], highlightbackground=DARK["bg"]
)
transparency_slider.set(0.7)  # Default slider value matches window alpha
transparency_slider.pack(side='left', padx=6)

# Dark mode toggle button with sun/moon icon
dark_mode_btn = ttk.Button(
    control_frame, text="🌙", width=2, command=toggle_dark_mode
)
dark_mode_btn.pack(side='left', padx=2)

# --- Key Spammer and Auto-Clicker Controls ---
spam_frame = ttk.Frame(root, style="Main.TFrame")
spam_frame.pack(pady=2, fill='x', padx=2)

# Key Spammer controls (no Set button - always listening)
spam_label = ttk.Label(spam_frame, text="Spam Key:", font=('Arial', 7), background=DARK["bg"], foreground=DARK["fg"])
spam_label.pack(side='left', padx=2)

spam_key_entry = tk.Entry(spam_frame, width=2, font=('Arial', 8), bg=DARK["entry_bg"], fg=DARK["entry_fg"], justify='center')
spam_key_entry.insert(0, spam_key.upper())
spam_key_entry.pack(side='left', padx=2)

spam_status_label = ttk.Label(spam_frame, text="(Listening)", font=('Arial', 7), background=DARK["bg"], foreground=DARK["fg"])
spam_status_label.pack(side='left', padx=2)

# Auto-clicker info (no button - use Tab to toggle)
autoclick_label = ttk.Label(spam_frame, text="AutoClick: Tab", font=('Arial', 7), background=DARK["bg"], foreground=DARK["fg"])
autoclick_label.pack(side='left', padx=(10, 2))

apply_theme()  # Set initial theme

# Setup system tray icon
setup_tray_icon()

# Start Roblox monitoring by default (spam/autoclick remain OFF by default)
start_monitoring()
update_gui()
root.mainloop()
