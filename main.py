import speech_recognition as sr
from gtts import gTTS
from playsound import playsound
import webbrowser
import time
import os
import sys
import musicLibrary
import google.generativeai as genai
from dotenv import load_dotenv

# === Gemini Setup ===
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel(model_name="models/gemini-1.5-flash")

def ask_gemini(prompt):
    try:
        convo = model.start_chat(history=[])
        response = convo.send_message(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"[ERROR] Gemini API failed: {e}")
        return "Sorry, I couldn't get a response from Gemini."

# === Speak with gTTS ===
def speak(text):
    print(f"Jarvis says: {text}")
    try:
        tts = gTTS(text=text, lang='en')
        filename = "temp_audio.mp3"
        tts.save(filename)
        playsound(filename)
        os.remove(filename)
        time.sleep(0.2)
    except Exception as e:
        print(f"[ERROR] Speaking failed: {e}")

# === Command Processing ===
def processCommand(command):
    command = command.lower()
    music = musicLibrary.music

    if "open google" in command:
        speak("Opening Google.")
        webbrowser.open("https://google.com")

    elif "open youtube" in command:
        speak("Opening YouTube.")
        webbrowser.open("https://youtube.com")

    elif "open linkedin" in command:
        speak("Opening LinkedIn.")
        webbrowser.open("https://linkedin.com")

    elif "open instagram" in command:
        speak("Opening Instagram.")
        webbrowser.open("https://instagram.com")

    elif "open spotify" in command:
        speak("Opening Spotify.")
        webbrowser.open("https://open.spotify.com/")

    elif "play" in command:
        found = False
        for song in music:
            if song in command:
                speak(f"Playing {song}")
                webbrowser.open(music[song])
                found = True
                break
        if not found:
            speak("Sorry, I couldn't find that song in your playlist.")
            speak("Opening Spotify.")
            webbrowser.open("https://open.spotify.com/")

    elif "playlist" in command or "show playlist" in command:
        if not music:
            speak("Your playlist is empty.")
        else:
            speak(f"You have {len(music)} songs in your playlist.")
            print("\n🎵 Playlist:")
            for song, link in music.items():
                print(f"{song.title()} → {link}")
            song_names = ', '.join(music.keys())
            speak(f"The songs are: {song_names}")

    elif "exit" in command or "stop" in command:
        speak("Goodbye!")
        sys.exit()

    else:
        response = ask_gemini(command)
        print("Gemini:", response)
        speak(response)

# === Main ===
if __name__ == "__main__":
    recognizer = sr.Recognizer()
    speak("Initializing Jarvis...")

    while True:
        try:
            with sr.Microphone() as source:
                print("🎤 Listening for wake word 'Jarvis'...")
                recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=3)
                wake_word = recognizer.recognize_google(audio)
                print(f"Heard: {wake_word}")

            if "jarvis" in wake_word.lower():
                speak("Jarvis activated. Listening for your command.")

                with sr.Microphone() as source:
                    recognizer.adjust_for_ambient_noise(source, duration=0.5)
                    audio = recognizer.listen(source, timeout=5, phrase_time_limit=6)
                    command = recognizer.recognize_google(audio)
                    print(f"Command received: {command}")
                    processCommand(command)

        except sr.UnknownValueError:
            print("Could not understand the audio.")
        except sr.RequestError as e:
            print(f"Speech recognition request failed: {e}")
        except sr.WaitTimeoutError:
            print("Listening timed out.")
        except KeyboardInterrupt:
            speak("Shutting down. Goodbye!")
            break

