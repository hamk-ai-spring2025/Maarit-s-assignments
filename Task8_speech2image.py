import speech_recognition as sr
import pyttsx3
import os
import openai
import requests
import msvcrt  # For detecting key presses in Windows

# Retrieve OpenAI API key from environment variables
openai.api_key = os.getenv("OPENAI_API_KEY")

# Initialize the recognizer and TTS engine
recognizer = sr.Recognizer()
engine = pyttsx3.init()

# Function to capture speech and convert to text
def listen_for_input():
    with sr.Microphone() as source:
        print("Listening for voice command...")
        audio = recognizer.listen(source)
    try:
        command = recognizer.recognize_google(audio)
        print(f"Recognized command: {command}")
        return command
    except sr.UnknownValueError:
        print("Sorry, I did not understand the command.")
        return None
    except sr.RequestError:
        print("Could not request results.")
        return None

# Function to generate image using OpenAI's DALL·E or another AI image generator
def generate_image(command):
    try:
        # Use OpenAI's DALL·E 2 or latest image generation model
        response = openai.Image.create(
            prompt=command,
            n=1,
            size="1024x1024",  # You can choose larger sizes if needed, like 2048x2048
            model="dall-e-2"  # Specifying DALL·E 2 as the model
        )
        image_url = response['data'][0]['url']
        print(f"Generated Image URL: {image_url}")
        return image_url
    except Exception as e:
        print(f"Failed to generate image: {e}")
        return None
    


# Function to speak a message
def speak(message):
    engine.say(message)
    engine.runAndWait()

# Function to check if the Enter key has been pressed
def wait_for_enter():
    print("Press Enter to start speaking.")
    while True:
        if msvcrt.kbhit():
            if msvcrt.getch() == b'\r':  # Enter key pressed
                break

def main():
    while True:
        wait_for_enter()  # Wait for the user to press Enter to start

        command = listen_for_input()
        if command:
            speak(f"Generating an image based on: {command}")
            image_url = generate_image(command)
            if image_url:
                speak(f"Here is your generated image: {command}")
            else:
                speak("I couldn't generate the image. Please try again.")
        else:
            speak("Please repeat your command.")
        
        print("Press Enter again to end.")
        while True:
            if msvcrt.kbhit():
                if msvcrt.getch() == b'\r':  # Enter key pressed
                    print("Command input ended.")
                    break

if __name__ == "__main__":
    main()

