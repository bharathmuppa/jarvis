import speech_recognition as sr
import requests
import pyttsx3
import json
import openai
import os

engine = pyttsx3.init()
engine.setProperty('rate', 125) 
voices = engine.getProperty('voices')
# For male voice use 0
engine.setProperty('voice', voices[0].id) 

recognizer = sr.Recognizer()
microphone = sr.Microphone()


openai.api_key = os.getenv("OPENAI_API_KEY") 

def recognize_speech():
    with microphone as source:
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
        try:
            text = recognizer.recognize_google(audio)
            return text
        except sr.UnknownValueError:
            return "Sorry, I didn't understand that."
        except sr.RequestError as e:
            return f"Sorry, there was an error: {e}"

def startUpPrompt():
    engine.say("Hello sir, Good day, How can i help you")
    engine.runAndWait()

def prettyPrintJson(ugly_json):
    parsed_json = json.loads(ugly_json)
    pretty_json = json.dumps(parsed_json, indent=2)

    print(pretty_json)


def get_response(text):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": text}
        ],
        temparature= 0.8,
        max_tokens=7,
        n=1
    )
    return response.choices[0].message.content


def speak(text):
    engine.say(text)
    engine.runAndWait()


def main():
    print("Say something!")
    while True:
        text = recognize_speech()
        print(f"You: {text}")
        if text.lower() == "exit":
            break
        response_text = get_response(text)
        speak(response_text)
        print(f"ChatGPT: {response_text}")


if __name__ == "__main__":
    main()
