import speech_recognition as sr

import pyttsx3
import json

import os
from speechrecognizers import recognize_speech
from voices import eleven_lab_voice
from aiagents import get_gpt4_response

engine = pyttsx3.init()
engine.setProperty('rate', 125)
# Set the voice ID to a different voice
engine.setProperty('voice', 'com.apple.speech.synthesis.voice.Alex')

recognizer = sr.Recognizer()
microphone = sr.Microphone()


def startUpPrompt():
    engine.say("Hello sir, Good day, How can i help you")
    engine.runAndWait()


def prettyPrintJson(ugly_json):
    parsed_json = json.loads(ugly_json)
    pretty_json = json.dumps(parsed_json, indent=2)

    print(pretty_json)


def main():
    print("Say something!")
    while True:
        text = recognize_speech()
        print(f"You: {text}")
        if text.lower() == "exit":
            break
        response_text = get_gpt4_response(text)
        eleven_lab_voice(response_text)
        # print(f"ChatGPT: {response_text}")


if __name__ == "__main__":
    main()
