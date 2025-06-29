import speech_recognition as sr
import pyttsx3
import json
import os
import threading
import time
from concurrent.futures import ThreadPoolExecutor

from speechrecognizers.WakeWordRecognizer import listen_with_wake_word, continuous_wake_word_mode
from voices import eleven_lab_voice
from aiagents import get_gpt4_response
from Agents import Neo4jGPTQuery
from loggers import prettyPrintJson
from jarvis_personality import jarvis_personality

# Initialize components
try:
    engine = pyttsx3.init('nsss')
    engine.setProperty('rate', 150)
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
    try:
        eleven_lab_voice(text)
    except Exception as e:
        print(f"TTS Error: {e}")
        if engine:
            engine.say(text)
            engine.runAndWait()

def startUpPrompt():
    """Startup greeting with time and Iron Man style"""
    greeting = jarvis_personality.get_time_based_greeting()
    startup_msg = "JARVIS systems are online and ready to assist. Simply say 'Jarvis' to activate."
    
    print(f"🤖 JARVIS: {greeting}")
    print(f"🤖 JARVIS: {startup_msg}")
    
    # Speak both messages
    speak_async(greeting)
    time.sleep(0.5)  # Small pause between messages
    speak_async(startup_msg)

def handle_special_commands(text):
    """Handle special system commands"""
    text_lower = text.lower().strip()
    
    if any(word in text_lower for word in ["exit", "quit", "goodbye", "shutdown", "stop"]):
        return "exit"
    elif any(word in text_lower for word in ["restart", "reload", "reset"]):
        return "restart"
    elif "sleep" in text_lower or "standby" in text_lower:
        return "sleep"
    
    return None

def main_jarvis():
    """Main Jarvis app with wake word detection"""
    print("\n" + "🤖" + "="*58 + "🤖")
    print("           JARVIS - AI Voice Assistant")
    print("🤖" + "="*58 + "🤖\n")
    
    # Startup
    startUpPrompt()
    time.sleep(2)  # Give time for greeting to play
    
    consecutive_errors = 0
    max_consecutive_errors = 2
    
    while True:
        try:
            print("\n" + "-"*40)
            print("👂 Waiting for wake word 'Jarvis'...")
            print("-"*40)
            
            # Listen for wake word and command with speak callback
            text = listen_with_wake_word(speak_async)
            
            # Handle different response types
            if text == "timeout":
                print("⏰ No command received. Listening again...")
                consecutive_errors += 1
                
                if consecutive_errors >= max_consecutive_errors:
                    print("💤 Going into quiet mode. Say 'Jarvis' when ready.")
                    consecutive_errors = 0
                continue
                
            elif text == "unclear":
                consecutive_errors += 1
                
                if consecutive_errors == 1:
                    response = "I'm sorry, I couldn't catch that. Could you repeat your command?"
                    print(f"🤖 Jarvis: {response}")
                    speak_async(response)
                else:
                    print("❓ Still having trouble hearing. Listening again...")
                
                if consecutive_errors >= max_consecutive_errors:
                    print("💤 Going into quiet mode. Say 'Jarvis' when ready.")
                    consecutive_errors = 0
                continue
                
            elif text.startswith("error:"):
                print(f"🚫 {text}")
                consecutive_errors += 1
                if consecutive_errors >= max_consecutive_errors:
                    print("💤 Technical difficulties. Going into quiet mode.")
                    consecutive_errors = 0
                continue
            
            # Valid command received
            consecutive_errors = 0
            print(f"👤 You: {text}")
            
            # Handle special commands
            special_command = handle_special_commands(text)
            if special_command == "exit":
                farewell = jarvis_personality.get_goodbye_response()
                print(f"🤖 JARVIS: {farewell}")
                speak_async(farewell)
                time.sleep(3)
                break
            elif special_command == "sleep":
                sleep_msg = "Entering sleep mode, Sir. Say 'Jarvis' when you need me."
                print(f"🤖 JARVIS: {sleep_msg}")
                speak_async(sleep_msg)
                continue
            elif special_command == "restart":
                restart_msg = "Restarting all systems, Sir. One moment please."
                print(f"🤖 JARVIS: {restart_msg}")
                speak_async(restart_msg)
                time.sleep(1)
                continue
            
            # Process AI response
            print("🧠 Processing your request...")
            
            try:
                response_future = executor.submit(process_response_async, text)
                response_text = response_future.result(timeout=15)
                
                print(f"🤖 JARVIS: {response_text}")
                
                # Speak response (non-blocking)
                speak_future = executor.submit(speak_async, response_text)
                
            except Exception as e:
                error_msg = jarvis_personality.get_error_response()
                print(f"❌ JARVIS: {error_msg}")
                speak_async(error_msg)
                
        except KeyboardInterrupt:
            print("\n👋 Jarvis interrupted by user. Shutting down...")
            break
        except Exception as e:
            print(f"❌ Unexpected system error: {e}")
            print("🔄 Restarting wake word detection...")
            time.sleep(1)
            continue

def main_continuous():
    """Continuous wake word mode without the main app loop"""
    print("Starting continuous wake word detection mode...")
    
    while True:
        try:
            # This will handle the continuous listening internally
            text = continuous_wake_word_mode()
            
            if text and not text.startswith(("timeout", "unclear", "error:")):
                print(f"📝 Command captured: {text}")
                
                # Process the command
                special_command = handle_special_commands(text)
                if special_command == "exit":
                    print("👋 Goodbye!")
                    break
                
                # Get AI response
                response = get_gpt4_response(text)
                print(f"🤖 Response: {response}")
                speak_async(response)
                
        except KeyboardInterrupt:
            print("\n👋 Continuous mode stopped. Goodbye!")
            break

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--continuous":
        main_continuous()
    else:
        main_jarvis()