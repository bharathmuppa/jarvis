import speech_recognition as sr
import pyttsx3
import json
import os
import threading
import time
from concurrent.futures import ThreadPoolExecutor

from speechrecognizers.FastRecognizers import recognize_speech_ultrafast
from voices import eleven_lab_voice
from aiagents import get_gpt4_response
from Agents import Neo4jGPTQuery
from loggers import prettyPrintJson

# Initialize components
try:
    engine = pyttsx3.init('nsss')
    engine.setProperty('rate', 150)  # Slightly faster speech
    engine.setProperty('voice', 'com.apple.speech.synthesis.voice.Alex')
except:
    try:
        engine = pyttsx3.init('espeak')
        engine.setProperty('rate', 150)
    except:
        engine = None
        print("Warning: Text-to-speech engine could not be initialized")

# Thread pool for parallel processing
executor = ThreadPoolExecutor(max_workers=3)

def process_response_async(text):
    """Process AI response in background thread"""
    return get_gpt4_response(text)

def speak_async(text):
    """Speak text in background thread"""
    if engine:
        engine.say(text)
        engine.runAndWait()
    else:
        eleven_lab_voice(text)

def startUpPrompt():
    if engine:
        engine.say("Hello sir, Good day, How can I help you today?")
        engine.runAndWait()
    else:
        print("Hello sir, Good day, How can I help you today?")

def main_fast():
    """Optimized main loop with concurrent processing"""
    print("🚀 Fast Jarvis is ready! Starting up...")
    startUpPrompt()
    
    print("\n" + "="*50)
    print("🎤 Say something! (or 'exit' to quit)")
    print("💡 Tips:")
    print("   - Speak clearly and wait for the listening prompt")
    print("   - Keep phrases under 8 seconds for best response")
    print("   - Say 'exit' to quit")
    print("="*50 + "\n")
    
    while True:
        try:
            # Get speech input (optimized)
            text = recognize_speech_ultrafast()
            print(f"👤 You: {text}")
            
            # Check for exit command
            if text.lower().strip() in ["exit", "quit", "goodbye", "stop"]:
                print("👋 Goodbye!")
                break
            
            # Skip processing if no valid input
            if text.startswith(("Sorry", "Could not", "Listening timeout", "No speech")):
                continue
            
            # Process AI response and speaking concurrently
            print("🤖 Thinking...")
            response_future = executor.submit(process_response_async, text)
            
            # Get response (with timeout)
            try:
                response_text = response_future.result(timeout=10)
                print(f"🤖 Jarvis: {response_text}")
                
                # Speak response
                speak_future = executor.submit(speak_async, response_text)
                # Don't wait for speaking to complete - allows for interruption
                
            except Exception as e:
                error_msg = f"Sorry, I encountered an error: {str(e)}"
                print(f"❌ Error: {error_msg}")
                speak_async(error_msg)
                
        except KeyboardInterrupt:
            print("\n👋 Interrupted by user. Goodbye!")
            break
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            continue

def main_continuous():
    """Continuous listening mode"""
    from speechrecognizers.FastRecognizers import start_continuous_listening
    
    print("🔄 Starting continuous listening mode...")
    print("💡 Speak naturally - I'm always listening!")
    print("Press Ctrl+C to stop\n")
    
    stop_listening = start_continuous_listening()
    
    try:
        while True:
            time.sleep(0.1)  # Keep main thread alive
    except KeyboardInterrupt:
        print("\n🛑 Stopping continuous listening...")
        stop_listening()
        print("👋 Goodbye!")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--continuous":
        main_continuous()
    else:
        main_fast()