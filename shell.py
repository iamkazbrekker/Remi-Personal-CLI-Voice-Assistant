import sys
import os
import shutil
import subprocess
import webbrowser
import psutil
from urllib.parse import quote_plus
import requests
import speech_recognition as sr

newsAPI = '50996d978fe94a2d8e06d5654c5f568e'

# do to: move, sleep, play, pause, volume, playlist, news, weather, download, ss, record

__commands__ = { 'open', 'close', 'exit', 'move', 'shutdown', 'restart', 'sleep', 'play', 'pause', 'volume', 'playlist', 'youtube', 'google', 'news', 'weather', 'wiki', 'download', 'screenshot', 'record', 'help', 'battery'}
__appMap__ = {
    "chrome": "chrome.exe",
    "vscode": "code.exe",
    "code": "code.exe",
    "notepad": "notepad.exe",
    "spotify": "spotify.exe",
    "brave": "brave.exe"
}
__commonPaths__ = [
    r"C:\Program Files",
    r"C:\Program Files (x86)",
    r"C:\Windows",
    r"C:\Windows\System32",
    r"C:\Users\{}\\AppData\Local\Programs\Microsoft VS Code".format(os.getlogin()),
    r"C:\Program Files\BraveSoftware\Brave-Browser\Application"
]

# -----------------------------------------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------------------------------------

def checkType(input: str):
    inputList = input.split(' ', 1)
    command = inputList[0]
    parameter = inputList[1] if len(inputList) > 1 else None

    if command not in __commands__:
        print(f'command {command} not found')
        return
    
    if command == 'exit':
        sys.exit()
    elif command == 'help':
        print('Available commands: ')
        for cmd in __commands__:
            print(cmd, end=" ")
        print()
        return
    elif command == 'battery':
        battery()
    elif command == 'shutdown' or command == 'restart':
        shutdownAndRestart(command)
    
    if parameter:
        if command == 'open':
            Fopen(parameter)
        elif command == 'close':
            Fclose(parameter)
        elif command == 'google':
            Fopen("https://www.google.com/search?q=" + quote_plus(parameter))
        elif command == 'youtube' or command == 'YouTube':
            openYT(parameter)
        elif command == 'wiki':
            Fopen("https://en.wikipedia.org/w/index.php?search=" + quote_plus(parameter))
        elif command == 'news':
            getNews(parameter)
        elif command == 'weather':
            getWeather(parameter)
        else:
            print(f'{command} available')

# -----------------------------------------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------------------------------------

def looksLikeURL(arg:str):
    arg = arg.lower()
    return arg.startswith('http://') or arg.startswith('https://')

def openYT(arg: str):
    brave = r'C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe'
    url = "https://www.youtube.com/results?search_query=" + quote_plus(arg)
    subprocess.Popen([brave, url])

def getNews(arg: str):
    if not newsAPI:
        print('API error')
        return
    
    if arg: 
        url = f"https://newsapi.org/v2/everything?q={arg}&sortBy=publishedAt&apiKey={newsAPI}"
    else:
        url = f"https://newsapi.org/v2/top-headlines?country=in&apiKey={newsAPI}"
    
    res = requests.get(url)
    data = res.json()
    if data.get("status") != "ok":
            print("news: API error:", data.get("message", "Unknown error"))
            return
        
    articles = data.get("articles", [])[:5]
    if not articles:
            print("news: no articles found.")
            return
        
    print("\nTop Headlines:\n")
    for i, a in enumerate(articles, 1):
        print(f"{i}. {a.get('title')}")
    print()

def getWeather(location):
    try:
        geo_url = "https://nominatim.openstreetmap.org/search"
        geo_params = {"q": location, "format": "json", "limit": 1}
        geo_res = requests.get(geo_url, params=geo_params, headers={
            "User-Agent": "MyWeatherCLI/1.0"
        }).json()

        if not geo_res:
            print("weather: location not found.")
            return

        lat = geo_res[0]["lat"]
        lon = geo_res[0]["lon"]

        weather_url = f"https://api.met.no/weatherapi/locationforecast/2.0/compact"
        weather_res = requests.get(
            weather_url,
            params={"lat": lat, "lon": lon},
            headers={"User-Agent": "MyWeatherCLI/1.0"}
        ).json()

        # Parse data
        timeseries = weather_res["properties"]["timeseries"]
        current = timeseries[0]["data"]

        temp = current["instant"]["details"]["air_temperature"]
        wind = current["instant"]["details"]["wind_speed"]
        
        print(f"\nWeather in {location.capitalize()}:")
        print(f"Temperature: {temp}°C")
        print(f"Windspeed: {wind} m/s")
        print()

    except Exception as e:
        print("weather: request failed:", e)

def runExecutable(name: str):
    if os.path.exists(name):
        return os.path.abspath(name)

    mapped = __appMap__.get(name.lower())
    if mapped:
        p = shutil.which(mapped)
        if p:
            return p
        
        for base in __commonPaths__:
            candidate = os.path.join(base, "Google", "Chrome", "Application", mapped)
            if os.path.exists(candidate):
                return candidate

            candidate = os.path.join(base, mapped)
            if os.path.exists(candidate):
                return candidate

    p = shutil.which(name)
    if p:
        return p

    return None

def shutdownAndRestart(arg: str):
    realityCheck = input(f'Are you sure you want to {arg}?(y/n) ').lower()
    if realityCheck == 'y':
        if arg == 'shutdown':
            os.system("shutdown /s /t 2")
        else:
            os.system("shutdown /r /t 2")
    return


def battery():
    battery = psutil.sensors_battery()
    if battery:
        percent = battery.percent
        power_plugged = battery.power_plugged
        
        status = "Plugged In" if power_plugged else "Not Plugged In"
        
        print(f"Battery Percentage: {percent}%")
        print(f"Power Status: {status}")
    else:
        print("Battery information not available.")

def Fopen(parameter):
    if not parameter:
        print('open: missing arguments')
    
    parameter = parameter.strip()

    if looksLikeURL(parameter):
        webbrowser.open(parameter)
        return
    
    if os.path.exists(parameter):
        os.startfile(os.path.abspath(parameter))
        return

    exe = runExecutable(parameter)
    if exe:
        try:
            subprocess.Popen([exe], creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)
        except Exception as e:
            print(f"Failed to open {parameter}: {e}")
        return

    print(f"open: could not find '{parameter}'. Add it to __appMap__ if needed.")




def Fclose(arg: str, confirm=True):
    if not arg:
        print("close: missing argument")
        return

    target = arg.strip()

    # ask once to avoid accidentally nuking wrong processes
    if confirm:
        ans = input(f"Close all processes named '{target}'? (y/n) ").lower()
        if ans != "y":
            print("Cancelled.")
            return

    # Ensure ".exe"
    if not target.lower().endswith(".exe"):
        target_exe = target + ".exe"
    else:
        target_exe = target

    # Run Windows taskkill
    try:
        subprocess.run(
            ["taskkill", "/IM", target_exe, "/F"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        print(f"Requested close for '{target_exe}'.")
    except Exception as e:
        print(f"close: error closing '{target_exe}': {e}")

# -----------------------------------------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------------------------------------

def __main__():
    while True:
        sys.stdout.write('$ ')
        voice_input = listen_for_voice()
        if voice_input:
            checkType(voice_input)

        # userInput = input().strip()

        # if not userInput:
        #     continue

        # checkType(userInput)

def listen_for_voice():
    recognizer = sr.Recognizer()
    mic = sr.Microphone()

    with mic as source:
        recognizer.adjust_for_ambient_noise(source)
        print("Listening...")

        audio = recognizer.listen(source)
    
    try:
        command = recognizer.recognize_google(audio) #type: ignore
        print(f"You said: {command}")
        return command.lower()
    except Exception:
        return ""


__main__()