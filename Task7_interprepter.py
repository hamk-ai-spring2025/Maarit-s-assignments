import os
import sys
import time
from pathlib import Path
import io
import threading
import speech_recognition as sr
from gtts import gTTS
import openai
import pygame  

# === Setup ===
openai.api_key = os.environ.get("OPENAI_API_KEY")
recognizer = sr.Recognizer()
mic = sr.Microphone()
client = openai

print("VOICE INTERPRETER PROGRAM")
print("=========================")

# === Choose target language ===
languages = {
    "1": ("English", "en"),
    "2": ("Finnish", "fi"),
    "3": ("Swedish", "sv"),
}

print("Available target languages:")
for key, (name, _) in languages.items():
    print(f"{key}. {name}")

language_choice = input("Choose target language number (1–3): ").strip()
if language_choice not in languages:
    print("Invalid choice. Exiting.")
    sys.exit()

target_language, language_code = languages[language_choice]
print(f"\nTarget language selected: {target_language}")

# === Record voice ===
print("\n🎤 Press Enter to start recording.")
input()
print("Recording... Press Enter again to stop.")

frames = []
stop_recording = [False]

def record_audio():
    with mic as source:
        recognizer.adjust_for_ambient_noise(source)
        while not stop_recording[0]:
            try:
                frame = source.stream.read(source.CHUNK)
                frames.append(frame)
            except Exception:
                break

record_thread = threading.Thread(target=record_audio)
record_thread.start()
input()  # Wait for second Enter
stop_recording[0] = True
record_thread.join()

# === Process recorded audio ===
raw_audio = b"".join(frames)
audio_data = sr.AudioData(raw_audio, mic.SAMPLE_RATE, 2)
audio_file = io.BytesIO(audio_data.get_wav_data())
audio_file.name = "recorded.wav"

print("\n📝 Transcribing...")
transcription = client.Audio.transcribe("whisper-1", audio_file)["text"]
print(f"\nOriginal Text:\n{transcription}")

# Save transcription
with open("original_text.txt", "w", encoding="utf-8") as f:
    f.write(transcription)

# === Translate ===
print("\n🌍 Translating...")
response = client.ChatCompletion.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": f"You are a translator. Translate everything to {target_language}. Only return the translated text."},
        {"role": "user", "content": transcription}
    ]
)
translation = response.choices[0].message.content.strip()
print(f"\nTranslated Text:\n{translation}")

# Save translation
with open("translated_text.txt", "w", encoding="utf-8") as f:
    f.write(translation)

# === Text to Speech ===
print("\n🔊 Generating speech...")
tts = gTTS(text=translation, lang=language_code)
speech_path = Path("translated_speech.mp3")
tts.save(speech_path)

# === Play audio ===
pygame.mixer.init()
pygame.mixer.music.load(str(speech_path))
pygame.mixer.music.play()
while pygame.mixer.music.get_busy():
    time.sleep(0.5)

print("✅ Done.")
