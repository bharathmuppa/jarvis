import speech_recognition as sr

import pyttsx3
import json

import os
from speechrecognizers.FreeRecognizers import recognize_speech
from voices import eleven_lab_voice
from aiagents import get_gpt4_response
from Agents import Neo4jGPTQuery
from loggers import prettyPrintJson

try:
    engine = pyttsx3.init('nsss')
    engine.setProperty('rate', 125)
    # Set the voice ID to a different voice
    engine.setProperty('voice', 'com.apple.speech.synthesis.voice.Alex')
except:
    try:
        engine = pyttsx3.init('espeak')
        engine.setProperty('rate', 125)
    except:
        engine = None
        print("Warning: Text-to-speech engine could not be initialized")

recognizer = sr.Recognizer()
microphone = sr.Microphone()


def startUpPrompt():
    if engine:
        engine.say("Hello sir, Good day, How can i help you")
        engine.runAndWait()
    else:
        print("Hello sir, Good day, How can i help you")



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

def activateNe04jAgent():
    gds_db = Neo4jGPTQuery(
    url="bolt://44.199.213.212:7687",
    user="neo4j",
    password="coders-modification-dose"
    )

    print(gds_db.run("""Which User Retweets the most?"""))

if __name__ == "__main__":
    main()
