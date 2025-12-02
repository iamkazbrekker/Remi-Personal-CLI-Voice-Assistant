

## **Remi — Personal CLI Voice Assistant (Windows)**

### **Overview**

PersonalCLI is a voice-controlled command-line assistant for Windows.
It listens continuously for voice commands and performs system actions like opening apps, searching YouTube, checking weather, reading news headlines, controlling power actions, and more.
The project aims to evolve into a floating GUI microphone widget that launches at system startup and stays always-listening.

---

### **Current Features**

#### **System / OS Commands**

| Command                | Description                                                                    |
| ---------------------- | ------------------------------------------------------------------------------ |
| `open <app>`           | Opens an installed application (Chrome, Brave, VSCode, Notepad, Spotify, etc.) |
| `close <app>`          | Force closes a running process                                                 |
| `shutdown` / `restart` | System shutdown or restart with confirmation                                   |
| `battery`              | Displays battery percentage & power status                                     |
| `exit`                 | Terminates the assistant                                                       |

#### **Internet & Media Commands**

| Command              | Description                                 |
| -------------------- | ------------------------------------------- |
| `google <query>`     | Google search in default browser            |
| `youtube <keywords>` | YouTube search in Brave browser             |
| `news <topic>`       | Fetches top 5 news headlines                |
| `weather <city>`     | Current temperature & wind using met.no API |
| `wiki <keywords>`    | Wikipedia search                            |

---

### **Dependencies**

Install the required libraries:

```bash
pip install speechrecognition requests psutil pyaudio
```

Windows users might need:

```bash
pip install pipwin
pipwin install pyaudio
```

---

### **App & Path Configuration**

Apps are resolved using `__appMap__` and common install folders:

```python
__appMap__ = {
    "chrome": "chrome.exe",
    "vscode": "code.exe",
    "notepad": "notepad.exe",
    "spotify": "spotify.exe",
    "brave": "brave.exe"
}
```

Add custom apps by inserting new entries.

---

### **Voice Recognition Loop**

The assistant continuously prints:

```
Listening...
You said: <command>
```

Then performs the requested operation.

---

### **Future Goals**

Planned upcoming features:

* Floating circular GUI widget (Tkinter or PyQt)
* Continuous background microphone listener
* Hotword activation (e.g., “Hey Remi”)
* Local offline speech recognition
* Media controls (play, pause, volume, next)
* Screenshot & screen recording
* File operations and automation
* Multi-step command pipeline


---

### **Known Issues**

* Google Speech API requires Internet
* Might misinterpret sentences with more than 2–3 words
* News API key may require rotating services later

---

### **Contribution**

PRs and Ideas are welcome.
Future goal: Make it a modular desktop assistant framework.

---



