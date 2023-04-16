import pyttsx3



def free_voice(text):
    engine = pyttsx3.init()
    engine.setProperty('rate', 125) 
    voices = engine.getProperty('voices')
    # For male voice use 0
    engine.setProperty('voice', voices[0].id) 
    engine.say(text)
    engine.runAndWait()