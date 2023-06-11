import speech_recognition as sr

import pyttsx3
import json

import os
from speechrecognizers import recognize_speech
from voices import eleven_lab_voice
from aiagents import get_gpt4_response
from Agents import Neo4jGPTQuery
from loggers import prettyPrintJson

engine = pyttsx3.init()
engine.setProperty('rate', 125)

# Set the voice ID to a different voice
engine.setProperty('voice', 'com.apple.speech.synthesis.voice.Alex')

recognizer = sr.Recognizer()
microphone = sr.Microphone()


def startUpPrompt():
    engine.say("Hello sir, Good day, How can i help you")
    engine.runAndWait()



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
    activateNe04jAgent()
