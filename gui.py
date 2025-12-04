import tkinter as tk
from tkinter import scrolledtext, messagebox
import keyboard
import threading
import speech_recognition as sr
import subprocess
import webbrowser
import os
import shutil
import psutil
from urllib.parse import quote_plus
import pystray
from PIL import Image, ImageDraw

# ----------------------- COMMAND SYSTEM -----------------------

__commands__ = { 'open', 'close', 'exit', 'shutdown', 'restart', 'google', 'youtube', 'wiki', 'help', 'battery'}
__appMap__ = {
    "chrome": "chrome.exe",
    "vscode": "code.exe",
    "notepad": "notepad.exe",
    "spotify": "spotify.exe",
    "brave": "brave.exe"
}
__commonPaths__ = [
    r"C:\Program Files",
    r"C:\Program Files (x86)",
    r"C:\Windows",
    r"C:\Windows\System32"
]

def looksLikeURL(arg:str):
    return arg.lower().startswith(("http://","https://"))

def openYT(arg: str):
    url = "https://www.youtube.com/results?search_query=" + quote_plus(arg)
    subprocess.Popen(["brave.exe", url], shell=True)

def runExecutable(name: str):
    mapped = __appMap__.get(name.lower())
    if mapped:
        # Try direct system PATH first
        p = shutil.which(mapped)
        if p:
            return p
        
        # Try common install locations
        for base in __commonPaths__:
            for folder in ["", "Google\\Chrome\\Application", "BraveSoftware\\Brave-Browser\\Application"]:
                candidate = os.path.join(base, folder, mapped)
                if os.path.exists(candidate):
                    return candidate

    # Last resort scan PATH
    return shutil.which(name)


def shutdownAndRestart(arg: str):
    check = input(f"Are you sure to {arg}? (y/n) ").lower()
    if check == "y":
        os.system("shutdown /s /t 2" if arg == "shutdown" else "shutdown /r /t 2")

def batteryInfo():
    battery = psutil.sensors_battery()
    if not battery:
        return "Battery info unavailable."
    return f"Battery: {battery.percent}%, Plugged: {battery.power_plugged}"

def executeCommand(text, log_callback):
    parts = text.lower().split(" ", 1)
    command = parts[0]
    param = parts[1] if len(parts) > 1 else None

    if command not in __commands__:
        log_callback(f"Unknown command: {command}")
        return

    if command == "help":
        log_callback("Commands: " + ", ".join(__commands__))
        return

    if command == "battery":
        log_callback(batteryInfo())
        return

    if param:
        if command == "open":
            if looksLikeURL(param):
                webbrowser.open(param)
                log_callback("Opening URL...")
            else:
                exe = runExecutable(param)
                if exe:
                    subprocess.Popen([exe])
                    log_callback(f"Opening {param}")
                else:
                    log_callback(f"Cannot open '{param}'")
        elif command == "google":
            webbrowser.open("https://www.google.com/search?q=" + quote_plus(param))
            log_callback("Searching Google...")
        elif command == "wiki":
            webbrowser.open("https://en.wikipedia.org/wiki/" + quote_plus(param))
            log_callback("Searching Wikipedia...")
        elif command == "youtube":
            openYT(param)
            log_callback("Searching YouTube...")
        elif command == "close":
            subprocess.run(["taskkill", "/IM", param + ".exe", "/F"])
            log_callback(f"Closed {param}")

# ----------------------- GUI + VOICE + TRAY SYSTEM -----------------------

class VoiceApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PersonalCLI")
        self.root.geometry("260x160")
        self.root.resizable(False, False)
        self.root.configure(bg="#1a1a1a")

        self.is_listening = False
        self.recognizer = sr.Recognizer()
        self.mic = sr.Microphone()

        self.listen_btn = tk.Button(root, text="Start Listening",
                                    command=self.toggle_listening,
                                    font=("Segoe UI", 11, "bold"),
                                    bg="#00b894", fg="white")
        self.listen_btn.pack(fill="x", padx=10, pady=(10, 5))

        self.status_label = tk.Label(root, text="Idle", fg="#dfe6e9", bg="#1a1a1a")
        self.status_label.pack(fill="x")

        self.output_box = scrolledtext.ScrolledText(root, wrap=tk.WORD, height=5,
                                                    bg="#2d3436", fg="white", font=("Consolas", 10))
        self.output_box.pack(fill="both", expand=True, padx=10, pady=5)

        keyboard.add_hotkey("ctrl+space", self.toggle_listening)
        self.create_tray_icon()

    # ------------------ TRAY ICON ------------------

    def create_tray_icon(self):
        img = Image.new("RGB", (64, 64), "black")
        draw = ImageDraw.Draw(img)
        draw.rectangle((12, 12, 52, 52), fill="cyan")

        self.tray_icon = pystray.Icon("PersonalCLI", img, "PersonalCLI", menu=pystray.Menu(
            pystray.MenuItem("Start Listening", lambda: self.start_listening()),
            pystray.MenuItem("Stop Listening", lambda: self.stop_listening()),
            pystray.MenuItem("Show Window", lambda: self.root.after(0, self.root.deiconify)),
            pystray.MenuItem("Exit", lambda: self.force_exit())
        ))

        threading.Thread(target=self.tray_icon.run, daemon=True).start()
        self.root.protocol("WM_DELETE_WINDOW", self.hide_window)

    def hide_window(self):
        self.root.withdraw()

    def force_exit(self):
        self.tray_icon.stop()
        os._exit(0)

    # ------------------ LISTENING ------------------

    def toggle_listening(self):
        if self.is_listening:
            self.stop_listening()
        else:
            self.start_listening()

    def start_listening(self):
        self.is_listening = True
        self.listen_btn.config(text="Stop Listening", bg="#d63031")
        self.status_label.config(text="Listening...")
        threading.Thread(target=self.listen_microphone, daemon=True).start()

    def stop_listening(self):
        self.is_listening = False
        self.listen_btn.config(text="Start Listening", bg="#00b894")
        self.status_label.config(text="Idle")

    def listen_microphone(self):
        while self.is_listening:
            try:
                with self.mic as source:
                    self.recognizer.adjust_for_ambient_noise(source)
                    audio = self.recognizer.listen(source, timeout=3, phrase_time_limit=4)

                text = self.recognizer.recognize_google(audio) #type: ignore
                self.log(f"You said: {text}")
                executeCommand(text, self.log)

            except sr.WaitTimeoutError:
                self.log("...")
            except sr.UnknownValueError:
                self.log("[Could not understand]")
            except Exception as e:
                self.log(f"Error: {e}")
                self.stop_listening()

    def log(self, message):
        self.output_box.insert(tk.END, message + "\n")
        self.output_box.yview(tk.END)


if __name__ == "__main__":
    root = tk.Tk()
    app = VoiceApp(root)
    root.mainloop()
