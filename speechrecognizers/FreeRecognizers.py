import speech_recognition as sr
import threading
import queue
import time


recognizer = sr.Recognizer()
microphone = sr.Microphone()

# Optimize recognizer settings for faster response
recognizer.energy_threshold = 4000  # Higher threshold for better noise filtering
recognizer.dynamic_energy_threshold = True
recognizer.dynamic_energy_adjustment_damping = 0.15
recognizer.dynamic_energy_ratio = 1.5
recognizer.pause_threshold = 0.8  # Shorter pause before considering speech ended
recognizer.operation_timeout = None
recognizer.phrase_threshold = 0.3  # Minimum seconds of speaking audio before processing
recognizer.non_speaking_duration = 0.8  # Seconds of non-speaking audio to keep on both sides

# Pre-adjust for ambient noise once at startup
print("Adjusting for ambient noise... Please be quiet for a moment.")
with microphone as source:
    recognizer.adjust_for_ambient_noise(source, duration=1)
print("Ready to listen!")


def recognize_speech_fast():
    """Optimized speech recognition with faster response times"""
    try:
        with microphone as source:
            print("Listening...")
            # Use shorter timeout and phrase detection
            audio = recognizer.listen(source, timeout=1, phrase_time_limit=5)
            print("Processing speech...")
            
        # Use Google's speech recognition (fastest free option)
        text = recognizer.recognize_google(audio)
        return text
        
    except sr.WaitTimeoutError:
        return "Listening timeout - please speak again."
    except sr.UnknownValueError:
        return "Sorry, I didn't understand that."
    except sr.RequestError as e:
        return f"Sorry, there was an error: {e}"


def recognize_speech_continuous():
    """Continuous listening with voice activity detection"""
    audio_queue = queue.Queue()
    
    def audio_callback(recognizer, audio):
        audio_queue.put(audio)
    
    # Start background listening
    stop_listening = recognizer.listen_in_background(microphone, audio_callback, phrase_time_limit=5)
    
    try:
        print("Continuous listening started. Say something...")
        while True:
            try:
                audio = audio_queue.get(timeout=1)
                try:
                    text = recognizer.recognize_google(audio)
                    if text.strip():  # Only return non-empty results
                        stop_listening()
                        return text
                except sr.UnknownValueError:
                    continue  # Keep listening
                except sr.RequestError as e:
                    stop_listening()
                    return f"Sorry, there was an error: {e}"
            except queue.Empty:
                continue
                
    except KeyboardInterrupt:
        stop_listening()
        return "Listening stopped."


def recognize_speech():
    """Main function with fallback options"""
    return recognize_speech_fast()    