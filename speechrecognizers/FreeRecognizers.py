import speech_recognition as sr


recognizer = sr.Recognizer()
microphone = sr.Microphone()


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