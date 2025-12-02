import tkinter as tk
from tkinter import scrolledtext
import keyboard
import threading
import speech_recognition as sr

class VoiceApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PersonalCLI")
        self.root.geometry("260x160")
        self.root.resizable(False, False)

        self.is_listening = False
        self.recognizer = sr.Recognizer()
        self.mic = sr.Microphone()

        # UI STYLE
        self.root.configure(bg="#1a1a1a")

        self.listen_btn = tk.Button(
            root, text="Start Listening",
            command=self.toggle_listening,
            font=("Segoe UI", 11, "bold"),
            bg="#00b894", fg="white", activebackground="#098c6e",
            relief="flat", padx=10, pady=5
        )
        self.listen_btn.pack(fill="x", padx=10, pady=(10, 5))

        self.status_label = tk.Label(
            root, text="Idle",
            font=("Segoe UI", 10),
            fg="#dfe6e9", bg="#1a1a1a"
        )
        self.status_label.pack(fill="x")

        self.output_box = scrolledtext.ScrolledText(
            root, wrap=tk.WORD, height=5,
            bg="#2d3436", fg="white",
            font=("Consolas", 10),
            borderwidth=0
        )
        self.output_box.pack(fill="both", expand=True, padx=10, pady=5)

        keyboard.add_hotkey("ctrl+space", self.toggle_listening)

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

                text = self.recognizer.recognize_google(audio)
                self.log(f"You said: {text}")

            except sr.WaitTimeoutError:
                self.log("...")
            except sr.UnknownValueError:
                self.log("[Could not understand audio]")
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
